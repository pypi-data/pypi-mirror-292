# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import Dict, Any

from fameio.source.tools import keys_to_lower


class Metadata(ABC):
    """Hosts Metadata"""

    _KEY_METADATA = "MetaData".lower()

    def __init__(self):
        self._metadata = {}

    @property
    def metadata(self) -> dict:
        """Returns list of metadata or an empty list if no metadata are defined"""
        return self._metadata

    def _extract_metadata(self, definitions: Dict[str, Any]) -> None:
        """If metadata is found in definitions, it is extracted and set"""
        definitions = keys_to_lower(definitions)
        if self._KEY_METADATA in definitions:
            self._metadata = definitions[self._KEY_METADATA]

    def _enrich_with_metadata(self, data: Dict) -> Dict:
        """Returns data enriched with metadata field"""
        data[self._KEY_METADATA] = self._metadata
        return data
