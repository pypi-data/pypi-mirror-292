# SPDX-FileCopyrightText: 2023 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Dict, List, Any

from fameio.source.logs import log_error_and_raise, log
from fameio.source.schema.exception import SchemaException
from fameio.source.schema.attribute import AttributeSpecs
from fameio.source.tools import keys_to_lower


class AgentType:
    """Schema definitions for an Agent type"""

    _ERR_NAME_INVALID = "'{}' is not a valid name for AgentTypes"
    _ERR_PRODUCTS_NO_STRING = "Product definition of AgentType '{}' contains item(s) / key(s) other than string: '{}'"
    _ERR_PRODUCTS_UNKNOWN_STRUCTURE = "Product definition of AgentType '{}' is neither list nor dictionary: '{}'"

    _NO_ATTRIBUTES = "Agent '{}' has no specified 'Attributes'."
    _NO_PRODUCTS = "Agent '{}' has no specified 'Products'."
    _NO_OUTPUTS = "Agent '{}' has no specified 'Outputs'."
    _NO_METADATA = "Agent '{}' has no specified 'Metadata'."

    _KEY_ATTRIBUTES = "Attributes".lower()
    _KEY_PRODUCTS = "Products".lower()
    _KEY_OUTPUTS = "Outputs".lower()
    _KEY_METADATA = "MetaData".lower()

    def __init__(self, name: str):
        """
        Initialise a new AgentType

        Args:
            name: name of the AgenType - must not be None or empty
        """
        if not name or name.isspace():
            log_error_and_raise(SchemaException(AgentType._ERR_NAME_INVALID.format(name)))
        self._name = name
        self._attributes = {}
        self._products = {}
        self._outputs = {}
        self._metadata = {}

    @classmethod
    def from_dict(cls, name: str, definitions: dict) -> AgentType:
        """
        Creates AgentType with given `name` from specified dictionary

        Args:
            name: of the agent type
            definitions: of the agent type specifying, e.g., its attributes and products

        Returns:
            a new instance of AgentType
        """
        agent_type = cls(name)

        definition = keys_to_lower(definitions)
        if AgentType._KEY_ATTRIBUTES in definition:
            for attribute_name, attribute_details in definition[AgentType._KEY_ATTRIBUTES].items():
                full_name = name + "." + attribute_name
                agent_type._attributes[attribute_name] = AttributeSpecs(full_name, attribute_details)
        else:
            log().info(AgentType._NO_ATTRIBUTES.format(name))

        if AgentType._KEY_PRODUCTS in definition and definition[AgentType._KEY_PRODUCTS]:
            agent_type._products.update(AgentType._read_products(definition[AgentType._KEY_PRODUCTS], name))
        else:
            log().info(AgentType._NO_PRODUCTS.format(name))

        if AgentType._KEY_OUTPUTS in definition:
            outputs_to_add = definition[AgentType._KEY_OUTPUTS]
            if outputs_to_add:
                agent_type._outputs.update(outputs_to_add)
        else:
            log().debug(AgentType._NO_OUTPUTS.format(name))

        if AgentType._KEY_METADATA in definition:
            metadata_to_add = definition[AgentType._KEY_METADATA]
            if metadata_to_add:
                agent_type._metadata.update(metadata_to_add)
        else:
            log().debug(AgentType._NO_METADATA.format(name))

        return agent_type

    @staticmethod
    def _read_products(products: Any, agent_type: str) -> Dict[str, Any]:
        """Returns a dict obtained from given `products` defined for `agent_type`"""
        product_names = None
        if isinstance(products, dict):
            product_names = products
        elif isinstance(products, list):
            product_names = {key: None for key in products}
        else:
            log_error_and_raise(SchemaException(AgentType._ERR_PRODUCTS_UNKNOWN_STRUCTURE.format(agent_type, products)))

        if all([isinstance(item, str) for item in product_names.keys()]):
            return product_names
        else:
            log_error_and_raise(SchemaException(AgentType._ERR_PRODUCTS_NO_STRING.format(agent_type, product_names)))

    @property
    def name(self) -> str:
        """Returns the agent type name"""
        return self._name

    @property
    def products(self) -> dict:
        """Returns dict of products or an empty dict if no products are defined"""
        return self._products

    def get_product_names(self) -> List[str]:
        """Returns list of product names or an empty list if no products are defined"""
        return list(self._products.keys())

    @property
    def attributes(self) -> Dict[str, AttributeSpecs]:
        """Returns list of Attributes of this agent or an empty list if no attributes are defined"""
        return self._attributes

    @property
    def outputs(self) -> dict:
        """Returns list of outputs or an empty list if no outputs are defined"""
        return self._outputs

    @property
    def metadata(self) -> dict:
        """Returns list of metadata or an empty list if no metadata are defined"""
        return self._metadata
