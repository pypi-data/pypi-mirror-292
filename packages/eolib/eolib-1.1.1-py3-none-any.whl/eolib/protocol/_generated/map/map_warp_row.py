# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .map_warp_row_tile import MapWarpRowTile
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapWarpRow:
    """
    A row of warp entities
    """
    _byte_size: int = 0
    _y: int = None # type: ignore [assignment]
    _tiles_count: int = None # type: ignore [assignment]
    _tiles: list[MapWarpRowTile] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def y(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._y

    @y.setter
    def y(self, y: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._y = y

    @property
    def tiles(self) -> list[MapWarpRowTile]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._tiles

    @tiles.setter
    def tiles(self, tiles: list[MapWarpRowTile]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._tiles = tiles
        self._tiles_count = len(self._tiles)

    @staticmethod
    def serialize(writer: EoWriter, data: "MapWarpRow") -> None:
        """
        Serializes an instance of `MapWarpRow` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapWarpRow): The data to serialize.
        """
        if data._y is None:
            raise SerializationError("y must be provided.")
        writer.add_char(data._y)
        if data._tiles_count is None:
            raise SerializationError("tiles_count must be provided.")
        writer.add_char(data._tiles_count)
        if data._tiles is None:
            raise SerializationError("tiles must be provided.")
        if len(data._tiles) > 252:
            raise SerializationError(f"Expected length of tiles to be 252 or less, got {len(data._tiles)}.")
        for i in range(data._tiles_count):
            MapWarpRowTile.serialize(writer, data._tiles[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "MapWarpRow":
        """
        Deserializes an instance of `MapWarpRow` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapWarpRow: The data to serialize.
        """
        data: MapWarpRow = MapWarpRow()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._y = reader.get_char()
            data._tiles_count = reader.get_char()
            data._tiles = []
            for i in range(data._tiles_count):
                data._tiles.append(MapWarpRowTile.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapWarpRow(byte_size={repr(self._byte_size)}, y={repr(self._y)}, tiles={repr(self._tiles)})"
