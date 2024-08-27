# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ast
from typing import Dict, Optional

from fameio.source.logs import log_error_and_raise, log
from fameio.source.schema.agenttype import AgentType
from fameio.source.schema.exception import SchemaException
from fameio.source.schema.java_packages import JavaPackages
from fameio.source.tools import keys_to_lower


class Schema:
    """Definition of a schema"""

    _ERR_AGENT_TYPES_MISSING = "Required keyword `AgentTypes` missing in Schema."
    _ERR_AGENT_TYPES_EMPTY = "`AgentTypes` must not be empty - at least one type of agent is required."
    _WARN_MISSING_PACKAGES = "No `JavaPackages` defined Schema. Future versions of fameio will require it."

    _KEY_AGENT_TYPE = "AgentTypes".lower()
    _KEY_PACKAGES = "JavaPackages".lower()

    def __init__(self, definitions: dict):
        self._original_input_dict = definitions
        self._agent_types = {}
        self._packages: Optional[JavaPackages] = None

    @classmethod
    def from_dict(cls, definitions: dict) -> Schema:
        """Load given dictionary `definitions` into a new Schema"""
        definitions = keys_to_lower(definitions)
        if Schema._KEY_AGENT_TYPE not in definitions:
            log_error_and_raise(SchemaException(Schema._ERR_AGENT_TYPES_MISSING))
        schema = cls(definitions)
        agent_types = definitions[Schema._KEY_AGENT_TYPE]
        if len(agent_types) == 0:
            log_error_and_raise(SchemaException(Schema._ERR_AGENT_TYPES_EMPTY))

        for agent_type_name, agent_definition in agent_types.items():
            agent_type = AgentType.from_dict(agent_type_name, agent_definition)
            schema._agent_types[agent_type_name] = agent_type

        if Schema._KEY_PACKAGES in definitions:
            schema._packages = JavaPackages.from_dict(definitions[Schema._KEY_PACKAGES])
        else:
            log().warning(Schema._WARN_MISSING_PACKAGES)
            schema._packages = JavaPackages()
        return schema

    @classmethod
    def from_string(cls, definitions: str) -> Schema:
        """Load given string `definitions` into a new Schema"""
        return cls.from_dict(ast.literal_eval(definitions))

    def to_dict(self) -> dict:
        """Serializes the schema content to a dict"""
        return self._original_input_dict

    def to_string(self) -> str:
        """Returns a string representation of the Schema of which the class can be rebuilt"""
        return repr(self.to_dict())

    @property
    def agent_types(self) -> Dict[str, AgentType]:
        """Returns all the agent types by their name"""
        return self._agent_types

    @property
    def packages(self) -> JavaPackages:
        """Returns JavaPackages, i.e. names where model classes are defined in"""
        return self._packages
