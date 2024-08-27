# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import ast
from typing import List, Dict, Any, Optional, Tuple

from fameprotobuf.DataStorage_pb2 import DataStorage
from fameprotobuf.Field_pb2 import NestedField
from fameprotobuf.InputFile_pb2 import InputData

from fameio.source.logs import log
from fameio.source.scenario import GeneralProperties, Agent, Contract, Scenario
from fameio.source.schema import Schema, AttributeSpecs, AttributeType
from fameio.source.series import TimeSeriesManager


class InputConversionException(Exception):
    """An Exception indication an error during reconstruction of input from its protobuf representation"""

    pass


class InputDao:
    """Data access object for inputs saved in protobuf"""

    _ERR_NO_INPUTS = "No input data found on file."
    _ERR_MULTIPLE_INPUTS = "File corrupt. More than one input section found on file."

    _FIELD_NAME_MAP: Dict = {
        AttributeType.STRING: "stringValue",
        AttributeType.ENUM: "stringValue",
        AttributeType.INTEGER: "intValue",
        AttributeType.DOUBLE: "doubleValue",
        AttributeType.LONG: "longValue",
        AttributeType.TIME_SERIES: "seriesId",
        AttributeType.BLOCK: "field",
    }

    def __init__(self) -> None:
        self._inputs: List[InputData] = []
        self._timeseries_manager: TimeSeriesManager = TimeSeriesManager()
        self._schema: Optional[Schema] = None

    def store_inputs(self, data_storages: List[DataStorage]) -> None:
        """
        Extracts and stores Inputs in given DataStorages - if such are present

        Args:
            data_storages: to be scanned for InputData
        """
        self._inputs.extend([data_storage.input for data_storage in data_storages if data_storage.HasField("input")])

    def recover_inputs(self) -> Tuple[TimeSeriesManager, Scenario]:
        """
        Recovers inputs to GeneralProperties, Schema, Agents, Contracts, Timeseries

        Return:
            recovered timeseries and scenario

        Raises:
            InputConversionException: if inputs could not be recovered
        """
        input_data = self._get_input_data()
        self._schema = self._get_schema(input_data)
        scenario = Scenario(self._schema, self._get_general_properties(input_data))
        for contract in self._get_contracts(input_data):
            scenario.add_contract(contract)

        self._init_timeseries(input_data)
        for agent in self._get_agents(input_data):
            scenario.add_agent(agent)

        return self._timeseries_manager, scenario

    def _get_input_data(self) -> InputData:
        """
        Check that exactly one previously extracted input data exist, otherwise raises an exception

        Raises:
            InputConversionException: if no or more than one input is present
        """
        if not self._inputs:
            log().error(self._ERR_NO_INPUTS)
            raise InputConversionException(self._ERR_NO_INPUTS)
        if len(self._inputs) > 1:
            log().error(self._ERR_MULTIPLE_INPUTS)
            raise InputConversionException(self._ERR_MULTIPLE_INPUTS)
        return self._inputs[0]

    @staticmethod
    def _get_schema(input_data: InputData) -> Schema:
        """Read and return Schema from given `input_data`"""
        return Schema.from_string(input_data.schema)

    @staticmethod
    def _get_general_properties(input_data: InputData) -> GeneralProperties:
        """Read and return GeneralProperties from given `input_data`"""
        return GeneralProperties(
            run_id=input_data.runId,
            simulation_start_time=input_data.simulation.startTime,
            simulation_stop_time=input_data.simulation.stopTime,
            simulation_random_seed=input_data.simulation.randomSeed,
            output_process=input_data.output.process,
            output_interval=input_data.output.interval,
        )

    @staticmethod
    def _get_contracts(input_data: InputData) -> List[Contract]:
        """Read and return Contracts from given `input_data`"""
        return [
            Contract(
                sender_id=contract.senderId,
                receiver_id=contract.receiverId,
                product_name=contract.productName,
                delivery_interval=contract.deliveryIntervalInSteps,
                first_delivery_time=contract.firstDeliveryTime,
                expiration_time=contract.expirationTime,
                meta_data=ast.literal_eval(contract.metadata),
            )
            for contract in input_data.contract
        ]

    def _init_timeseries(self, input_data: InputData) -> None:
        """Read timeseries from given `input_data` and initialise TimeSeriesManager"""
        self._timeseries_manager.reconstruct_time_series(list(input_data.timeSeries))

    def _get_agents(self, input_data: InputData) -> List[Agent]:
        """Read and return Agents from given `input_data`"""
        agents = []
        for agent_dao in input_data.agent:
            agent = Agent(
                agent_id=agent_dao.id, type_name=agent_dao.className, meta_data=ast.literal_eval(agent_dao.metadata)
            )
            attribute_dict = self._get_attributes(
                list(agent_dao.field), self._schema.agent_types[agent_dao.className].attributes
            )
            agent.init_attributes_from_dict(attribute_dict)
            agents.append(agent)
        return agents

    def _get_attributes(self, fields: List[NestedField], schematics: Dict[str, AttributeSpecs]) -> Dict[str, Any]:
        """Read and return Attributes as Dictionary from given list of fields"""
        attributes: Dict[str, Any] = {}
        for field in fields:
            attributes[field.fieldName] = self._get_field_value(field, schematics[field.fieldName])
        return attributes

    def _get_field_value(self, field: NestedField, schematic: AttributeSpecs) -> Any:
        """Extracts and returns value(s) of given `field`"""
        attribute_type: AttributeType = schematic.attr_type
        value = field.__getattribute__(self._FIELD_NAME_MAP[attribute_type])
        if attribute_type is AttributeType.TIME_SERIES:
            return self._timeseries_manager.get_reconstructed_series_by_id(field.seriesId)
        elif attribute_type is AttributeType.BLOCK:
            if schematic.is_list:
                return [self._get_attributes(list(entry.field), schematic.nested_attributes) for entry in field.field]
            else:
                return self._get_attributes(list(field.field), schematic.nested_attributes)
        else:
            if schematic.is_list:
                return list(value)
            else:
                return list(value)[0]
