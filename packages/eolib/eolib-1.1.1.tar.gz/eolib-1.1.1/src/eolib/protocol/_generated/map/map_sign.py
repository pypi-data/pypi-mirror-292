# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapSign:
    """
    Sign EMF entity
    """
    _byte_size: int = 0
    _coords: Coords = None # type: ignore [assignment]
    _string_data_length: int = None # type: ignore [assignment]
    _string_data: str = None # type: ignore [assignment]
    _title_length: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def coords(self) -> Coords:
        return self._coords

    @coords.setter
    def coords(self, coords: Coords) -> None:
        self._coords = coords

    @property
    def string_data(self) -> str:
        """
        Note:
          - Length must be 64007 or less.
        """
        return self._string_data

    @string_data.setter
    def string_data(self, string_data: str) -> None:
        """
        Note:
          - Length must be 64007 or less.
        """
        self._string_data = string_data
        self._string_data_length = len(self._string_data)

    @property
    def title_length(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._title_length

    @title_length.setter
    def title_length(self, title_length: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._title_length = title_length

    @staticmethod
    def serialize(writer: EoWriter, data: "MapSign") -> None:
        """
        Serializes an instance of `MapSign` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapSign): The data to serialize.
        """
        if data._coords is None:
            raise SerializationError("coords must be provided.")
        Coords.serialize(writer, data._coords)
        if data._string_data_length is None:
            raise SerializationError("string_data_length must be provided.")
        writer.add_short(data._string_data_length + 1)
        if data._string_data is None:
            raise SerializationError("string_data must be provided.")
        if len(data._string_data) > 64007:
            raise SerializationError(f"Expected length of string_data to be 64007 or less, got {len(data._string_data)}.")
        writer.add_fixed_encoded_string(data._string_data, data._string_data_length, False)
        if data._title_length is None:
            raise SerializationError("title_length must be provided.")
        writer.add_char(data._title_length)

    @staticmethod
    def deserialize(reader: EoReader) -> "MapSign":
        """
        Deserializes an instance of `MapSign` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapSign: The data to serialize.
        """
        data: MapSign = MapSign()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._coords = Coords.deserialize(reader)
            data._string_data_length = reader.get_short() - 1
            data._string_data = reader.get_fixed_encoded_string(data._string_data_length, False)
            data._title_length = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapSign(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, string_data={repr(self._string_data)}, title_length={repr(self._title_length)})"
