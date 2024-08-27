# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import List, Dict

from fameio.source.logs import log_error_and_raise
from fameio.source.schema import SchemaException
from fameio.source.tools import keys_to_lower


class JavaPackages:
    """Schema definitions for Java package names in which model classes reside"""

    _ERR_MISSING_AGENTS = "JavaPackages requires non-empty list for `Agents`. Key was missing or list was empty."
    _ERR_MISSING_DATA_ITEMS = "JavaPackages requires non-empty list for `DataItems`. Key was missing or list was empty."
    _ERR_MISSING_PORTABLES = "JavaPackages require non-empty list for `Portables`. Key was missing or list was empty."

    _KEY_AGENT = "Agents".lower()
    _KEY_DATA_ITEM = "DataItems".lower()
    _KEY_PORTABLE = "Portables".lower()

    def __init__(self):
        self._agents: List[str] = []
        self._data_items: List[str] = []
        self._portables: List[str] = []

    @classmethod
    def from_dict(cls, definitions: Dict[str, List[str]]) -> JavaPackages:
        """
        Creates JavaPackages from a dictionary representation

        Args:
            definitions: dictionary representation of JavaPackages

        Returns:
            new instance of JavaPackages
        """
        java_packages = cls()
        definitions = keys_to_lower(definitions)

        java_packages._agents = definitions.get(JavaPackages._KEY_AGENT, [])
        java_packages._data_items = definitions.get(JavaPackages._KEY_DATA_ITEM, [])
        java_packages._portables = definitions.get(JavaPackages._KEY_PORTABLE, [])

        if not java_packages._agents:
            log_error_and_raise(SchemaException(JavaPackages._ERR_MISSING_AGENTS))
        if not java_packages._data_items:
            log_error_and_raise(SchemaException(JavaPackages._ERR_MISSING_DATA_ITEMS))
        if not java_packages._portables:
            log_error_and_raise(SchemaException(JavaPackages._ERR_MISSING_PORTABLES))

        return java_packages

    @property
    def agents(self) -> List[str]:
        """Return list of java package names that contain the model's Agents"""
        return self._agents

    @property
    def data_items(self) -> List[str]:
        """Return list of java package names that contain the model's DataItems"""
        return self._data_items

    @property
    def portables(self) -> List[str]:
        """Return list of java package names that contain the model's Portables"""
        return self._portables
