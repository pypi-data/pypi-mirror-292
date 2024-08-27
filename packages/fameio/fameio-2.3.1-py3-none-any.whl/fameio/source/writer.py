# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import sys
import importlib.metadata as metadata
from pathlib import Path
from typing import Any, Dict, List, Union

from fameprotobuf.Contract_pb2 import ProtoContract
from fameprotobuf.DataStorage_pb2 import DataStorage
from fameprotobuf.ExecutionData_pb2 import ExecutionData
from fameprotobuf.Field_pb2 import NestedField
from fameprotobuf.InputFile_pb2 import InputData
from fameprotobuf.Model_pb2 import ModelData

from fameio.source.logs import log_error_and_raise, log
from fameio.source.results.reader import Reader
from fameio.source.scenario import (
    Agent,
    Attribute,
    Contract,
    GeneralProperties,
    Scenario,
)
from fameio.source.schema import Schema
from fameio.source.schema.attribute import AttributeSpecs, AttributeType
from fameio.source.schema.java_packages import JavaPackages
from fameio.source.series import TimeSeriesManager
from fameio.source.time import FameTime
from fameio.source.tools import ensure_is_list


class ProtoWriterException(Exception):
    """Indicates an error during writing of protobuf file"""

    pass


class ProtoWriter:
    """Writes a given scenario to protobuf file"""

    _FAME_PROTOBUF_STREAM_HEADER = "famecoreprotobufstreamfilev001"  # noqa

    _TYPE_NOT_IMPLEMENTED = "AttributeType '{}' not implemented."
    _CONTRACT_UNSUPPORTED = (
        "Unsupported value for Contract Attribute '{}'; "
        "Only support `int`, `float`, `enum` or `dict` types are supported here."
    )
    _USING_DEFAULT = "Using provided Default for Attribute: '{}'."
    _NO_FILE_SPECIFIED = "Could not write to '{}'. Please specify a valid output file."

    _INFO_WRITING = "Writing scenario to protobuf file `{}`"
    _INFO_WRITING_COMPLETED = "Saved protobuf file `{}` to disk"

    def __init__(self, file_path: Path, time_series_manager: TimeSeriesManager) -> None:
        self.file_path: Path = file_path
        self._time_series_manager: TimeSeriesManager = time_series_manager

    def write_validated_scenario(self, scenario: Scenario) -> None:
        """Writes given validated Scenario to file"""
        pb_data_storage = self._create_protobuf_from_scenario(scenario)
        self._write_protobuf_to_disk(pb_data_storage)

    def _create_protobuf_from_scenario(self, scenario: Scenario) -> DataStorage:
        """Returns given `scenario` written to new DataStorage protobuf"""
        log().info("Converting scenario to protobuf.")
        pb_data_storage = DataStorage()
        pb_input = pb_data_storage.input

        self._set_general_properties(pb_input, scenario.general_properties)
        self._add_agents(pb_input, scenario.agents, scenario.schema)
        self._add_contracts(pb_input, scenario.contracts)
        self._set_time_series(pb_input)
        self._set_schema(pb_input, scenario.schema)

        self._set_java_package_names(pb_data_storage.model, scenario.schema.packages)
        self._set_execution_versions(pb_data_storage.execution.versions)
        return pb_data_storage

    @staticmethod
    def _set_general_properties(pb_input: InputData, general_properties: GeneralProperties) -> None:
        """Saves a scenario's general properties to specified protobuf `pb_input` container"""
        log().info("Adding General Properties")
        pb_input.runId = general_properties.run_id
        pb_input.simulation.startTime = general_properties.simulation_start_time
        pb_input.simulation.stopTime = general_properties.simulation_stop_time
        pb_input.simulation.randomSeed = general_properties.simulation_random_seed
        pb_input.output.interval = general_properties.output_interval
        pb_input.output.process = general_properties.output_process

    def _add_agents(self, pb_input: InputData, agents: List[Agent], schema: Schema) -> None:
        """Triggers setting of `agents` to `pb_input`"""
        log().info("Adding Agents")
        for agent in agents:
            pb_agent = self._set_agent(pb_input.agent.add(), agent)
            attribute_specs = schema.agent_types[agent.type_name].attributes
            self._set_attributes(pb_agent, agent.attributes, attribute_specs)
            pb_agent.metadata = repr(agent.meta_data)

    @staticmethod
    def _set_agent(pb_agent: InputData.AgentDao, agent: Agent) -> InputData.AgentDao:
        """Saves type and id of given `agent` to protobuf `pb_agent` container. Returns given `pb_agent`"""
        pb_agent.className = agent.type_name
        pb_agent.id = agent.id
        return pb_agent

    def _set_attributes(
        self,
        pb_parent: Union[InputData.AgentDao, NestedField],
        attributes: Dict[str, Attribute],
        specs: Dict[str, AttributeSpecs],
    ) -> None:
        """Assigns `attributes` to protobuf fields of given `pb_parent` - cascades for nested Attributes"""
        values_not_set = [key for key in specs.keys()]
        for name, attribute in attributes.items():
            pb_field = self._add_field(pb_parent, name)
            attribute_specs = specs[name]
            values_not_set.remove(name)
            attribute_type = attribute_specs.attr_type
            if attribute_type is AttributeType.BLOCK:
                if attribute_specs.is_list:
                    for index, entry in enumerate(attribute.nested_list):
                        pb_inner = self._add_field(pb_field, str(index))
                        self._set_attributes(pb_inner, entry, attribute_specs.nested_attributes)
                else:
                    self._set_attributes(pb_field, attribute.nested, attribute_specs.nested_attributes)
            else:
                self._set_attribute(pb_field, attribute.value, attribute_type)
        for name in values_not_set:
            attribute_specs = specs[name]
            if attribute_specs.is_mandatory:
                pb_field = self._add_field(pb_parent, name)
                self._set_attribute(pb_field, attribute_specs.default_value, attribute_specs.attr_type)
                log().info(self._USING_DEFAULT.format(name))

    @staticmethod
    def _add_field(pb_parent: Union[InputData.AgentDao, NestedField], name: str) -> NestedField:
        """Returns new field with given `name` that is added to given `pb_parent`"""
        pb_field = pb_parent.field.add()
        pb_field.fieldName = name
        return pb_field

    def _set_attribute(self, pb_field: NestedField, value: Any, attribute_type: AttributeType) -> None:
        """Sets given `value` to given protobuf `pb_field` depending on specified `attribute_type`"""
        if attribute_type is AttributeType.INTEGER:
            pb_field.intValue.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.DOUBLE:
            pb_field.doubleValue.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.LONG:
            pb_field.longValue.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.TIME_STAMP:
            pb_field.longValue.extend(ensure_is_list(FameTime.convert_string_if_is_datetime(value)))
        elif attribute_type in (AttributeType.ENUM, AttributeType.STRING, AttributeType.STRING_SET):
            pb_field.stringValue.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.TIME_SERIES:
            pb_field.seriesId = self._time_series_manager.get_series_id_by_identifier(value)
        else:
            log_error_and_raise(ProtoWriterException(self._TYPE_NOT_IMPLEMENTED.format(attribute_type)))

    @staticmethod
    def _add_contracts(pb_input: InputData, contracts: List[Contract]) -> None:
        """Triggers setting of `contracts` to `pb_input`"""
        log().info("Adding Contracts")
        for contract in contracts:
            pb_contract = ProtoWriter._set_contract(pb_input.contract.add(), contract)
            ProtoWriter._set_contract_attributes(pb_contract, contract.attributes)
            pb_contract.metadata = repr(contract.meta_data)

    @staticmethod
    def _set_contract(pb_contract: ProtoContract, contract: Contract) -> ProtoContract:
        """Saves given `contract` details to protobuf container `pb_contract`. Returns given `pb_contract`"""
        pb_contract.senderId = contract.sender_id
        pb_contract.receiverId = contract.receiver_id
        pb_contract.productName = contract.product_name
        pb_contract.firstDeliveryTime = contract.first_delivery_time
        pb_contract.deliveryIntervalInSteps = contract.delivery_interval
        if contract.expiration_time:
            pb_contract.expirationTime = contract.expiration_time
        return pb_contract

    @staticmethod
    def _set_contract_attributes(
        pb_parent: Union[ProtoContract, NestedField], attributes: Dict[str, Attribute]
    ) -> None:
        """Assign (nested) Attributes to given protobuf container `pb_parent`"""
        for name, attribute in attributes.items():
            log().debug("Assigning contract attribute `{}`.".format(name))
            pb_field = ProtoWriter._add_field(pb_parent, name)

            if attribute.has_value:
                value = attribute.value
                if isinstance(value, int):
                    pb_field.intValue.extend([value])
                elif isinstance(value, float):
                    pb_field.doubleValue.extend([value])
                elif isinstance(value, str):
                    pb_field.stringValue.extend([value])
                else:
                    log_error_and_raise(ProtoWriterException(ProtoWriter._CONTRACT_UNSUPPORTED.format(str(attribute))))
            elif attribute.has_nested:
                ProtoWriter._set_contract_attributes(pb_field, attribute.nested)

    def _set_time_series(self, pb_input: InputData) -> None:
        """Adds all time series from TimeSeriesManager to given `pb_input`"""
        log().info("Adding TimeSeries")
        for unique_id, identifier, data in self._time_series_manager.get_all_series():
            pb_series = pb_input.timeSeries.add()
            pb_series.seriesId = unique_id
            pb_series.seriesName = identifier
            ProtoWriter._add_rows_to_series(pb_series, data)

    @staticmethod
    def _add_rows_to_series(series: InputData.TimeSeriesDao, data_frame) -> None:
        for key, value in data_frame.itertuples(index=False):
            row = series.row.add()
            row.timeStep = int(key)
            row.value = value

    @staticmethod
    def _set_schema(pb_input: InputData, schema: Schema) -> None:
        """Sets the given `schema` `pb_input`"""
        log().info("Adding Schema")
        pb_input.schema = schema.to_string()

    @staticmethod
    def _set_java_package_names(pb_model: ModelData, java_packages: JavaPackages) -> None:
        """Adds given JavaPackages names to given ModelData section"""
        pb_packages = pb_model.packages
        pb_packages.agent.extend(java_packages.agents)
        pb_packages.dataItem.extend(java_packages.data_items)
        pb_packages.portable.extend(java_packages.portables)

    def _write_protobuf_to_disk(self, pb_data_storage: DataStorage) -> None:
        """Writes given `protobuf_input_data` to disk"""
        log().info(self._INFO_WRITING.format(self.file_path))
        try:
            with open(self.file_path, "wb") as file:
                serialised_data_storage = pb_data_storage.SerializeToString()
                file.write(self._FAME_PROTOBUF_STREAM_HEADER.encode(Reader.HEADER_ENCODING))
                file.write(len(serialised_data_storage).to_bytes(Reader.BYTES_DEFINING_MESSAGE_LENGTH, byteorder="big"))
                file.write(serialised_data_storage)
        except OSError as e:
            log_error_and_raise(ProtoWriterException(ProtoWriter._NO_FILE_SPECIFIED.format(self.file_path), e))
        log().info(self._INFO_WRITING_COMPLETED.format(self.file_path))

    @staticmethod
    def _set_execution_versions(pb_versions: ExecutionData.Versions) -> None:
        """Adds version strings for fameio, fameprotobuf, and python to the given Versions message"""
        pb_versions.fameProtobuf = metadata.version("fameprotobuf")
        pb_versions.fameIo = metadata.version("fameio")
        pb_versions.python = sys.version
