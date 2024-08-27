# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List, Union

from fameio.source.metadata import Metadata
from fameio.source.scenario.exception import log_and_raise
from fameio.source.tools import keys_to_lower


class StringSet(Metadata):
    """Hosts a StringSet in the given format"""

    ValueType = Union[List[str], Dict[str, Dict]]
    StringSetType = Dict[str, Union[Dict, ValueType]]

    _ERR_NO_STRING_SET_VALUES = "Missing mandatory key '{}' in StringSet definition {}."

    _KEY_VALUES = "Values".lower()

    def __init__(self):
        super().__init__()
        self._values = {}

    @classmethod
    def from_dict(cls, definition: StringSetType) -> "StringSet":
        """Returns StringSet initialised from `definition`"""
        string_set = cls()
        string_set._extract_metadata(definition)
        definition = keys_to_lower(definition)
        if cls._KEY_VALUES in definition:
            string_set._values = string_set._read_values(definition)
        else:
            log_and_raise(cls._ERR_NO_STRING_SET_VALUES.format(cls._KEY_VALUES, definition))
        return string_set

    def _read_values(self, definition: ValueType) -> Dict[str, Dict]:
        """Ensures values are returned as dictionary representation by converting `definitions` of type 'List[str]'"""
        values = definition[self._KEY_VALUES]
        if isinstance(values, list):
            return {name: {} for name in values}
        return values

    def to_dict(self) -> Dict:
        """Serializes the StringSet to a dict"""
        result = {self._KEY_VALUES: self._values}
        return self._enrich_with_metadata(result)

    def is_in_set(self, key: str) -> bool:
        """Returns True if `key` is a valid name in this StringSet"""
        return key in self._values
