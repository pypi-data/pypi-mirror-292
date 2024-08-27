# SPDX-FileCopyrightText: 2023 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import struct
import typing
from abc import ABC, abstractmethod
from typing import IO, List

from fameprotobuf.DataStorage_pb2 import DataStorage
from google.protobuf.message import DecodeError

from fameio.source.logs import log


class Reader(ABC):
    """Abstract base class for protobuf file readers"""

    _WARN_NO_HEADER = "No header recognised in file. File might be deprecated or corrupted."  # noqa
    _ERR_FILE_CORRUPT_NEGATIVE_LENGTH = "Corrupt file, message length must be positive."
    _ERR_FILE_CORRUPT_MISSING_DATA = "Trying to read corrupt file caused by inconsistent message length."
    _ERR_UNSUPPORTED_MODE = "Ignoring memory saving mode: not supported for files created with `fame-core<1.4`."
    _ERR_PARSING_FAILED = "File Corrupt. Could not parse file content."
    _DEBUG_FILE_END_REACHED = "Reached expected end of file."

    _HEADER_LENGTH = 30
    HEADER_ENCODING = "utf-8"
    BYTES_DEFINING_MESSAGE_LENGTH = 4
    _READER_HEADERS = {
        "famecoreprotobufstreamfilev001": lambda file, mode: ReaderV1(file, mode),  # noqa
    }

    def __init__(self, file: IO, read_single) -> None:
        self._file = file
        self._read_single = read_single

    @abstractmethod
    def read(self) -> List[DataStorage]:
        """Reads associated filestream and returns one or multiple DataStorage(s) or empty list"""

    @staticmethod
    def get_reader(file: IO, read_single: bool = False) -> Reader:
        """
        Returns reader matching the given file header

        Args:
            file: to be read by the returned Reader
            read_single: if True, the returned Reader's `read()` method gets one messages at a time

        Returns:
            Reader that can read the specified file
        """
        log().debug("Reading file headers...")
        try:
            header = file.read(Reader._HEADER_LENGTH).decode(Reader.HEADER_ENCODING)
            return Reader._READER_HEADERS[header](file, read_single)
        except (KeyError, UnicodeDecodeError):
            log().warning(Reader._WARN_NO_HEADER)
            file.seek(0)
            if read_single:
                log().error(Reader._ERR_UNSUPPORTED_MODE)
            return ReaderV0(file, False)

    @typing.final
    def _read_message_length(self) -> int:
        """Returns length of next DataStorage message in file"""
        message_length_byte = self._file.read(self.BYTES_DEFINING_MESSAGE_LENGTH)
        if not message_length_byte:
            log().debug(self._DEBUG_FILE_END_REACHED)
            message_length_int = 0
        else:
            message_length_int = struct.unpack(">i", message_length_byte)[0]
        return message_length_int

    @typing.final
    def _read_data_storage_message(self, message_length: int = None) -> DataStorage:
        """
        Returns given `data_storage` read from current file position and following `message_length` bytes.
        If `message_length` is omitted, the rest of the file is read. If no message is found, None is returned.
        """
        if message_length is None:
            message = self._file.read()
        elif message_length > 0:
            message = self._file.read(message_length)
        else:
            raise IOError(self._ERR_FILE_CORRUPT_NEGATIVE_LENGTH)
        if message_length and len(message) != message_length:
            log().error(self._ERR_FILE_CORRUPT_MISSING_DATA)
        return self._parse_to_data_storage(message) if message else None

    @staticmethod
    @typing.final
    def _parse_to_data_storage(message: bytes) -> DataStorage:
        data_storage = DataStorage()
        try:
            data_storage.ParseFromString(message)
        except DecodeError:
            raise IOError(Reader._ERR_PARSING_FAILED)
        return data_storage


class ReaderV0(Reader):
    """Reader class for deprecated `fame-core<1.4` output without any header"""

    _WARN_DEPRECATED = "DeprecationWarning: Please consider updating to `FAME-Core>=1.4` and `fameio>=1.6`"

    def __init__(self, file: IO, read_single):
        super().__init__(file, read_single)
        log().warning(self._WARN_DEPRECATED)

    def read(self) -> List[DataStorage]:
        result = self._read_data_storage_message()
        return [result] if result else []


class ReaderV1(Reader):
    """Reader class for `fame-core>=1.4` output with header of version v001"""

    def read(self) -> List[DataStorage]:
        messages = []
        while True:
            message_length = self._read_message_length()
            if message_length == 0:
                break
            messages.append(self._read_data_storage_message(message_length))
            if self._read_single:
                break
        log().debug(f"Read {len(messages)} messages from file.")
        return messages
