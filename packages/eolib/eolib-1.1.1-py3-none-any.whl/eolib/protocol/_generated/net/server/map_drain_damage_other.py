# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MapDrainDamageOther:
    """
    Another player taking damage from a map HP drain
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _hp_percentage: int = None # type: ignore [assignment]
    _damage: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._player_id

    @player_id.setter
    def player_id(self, player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._player_id = player_id

    @property
    def hp_percentage(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hp_percentage

    @hp_percentage.setter
    def hp_percentage(self, hp_percentage: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hp_percentage = hp_percentage

    @property
    def damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._damage

    @damage.setter
    def damage(self, damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._damage = damage

    @staticmethod
    def serialize(writer: EoWriter, data: "MapDrainDamageOther") -> None:
        """
        Serializes an instance of `MapDrainDamageOther` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapDrainDamageOther): The data to serialize.
        """
        if data._player_id is None:
            raise SerializationError("player_id must be provided.")
        writer.add_short(data._player_id)
        if data._hp_percentage is None:
            raise SerializationError("hp_percentage must be provided.")
        writer.add_char(data._hp_percentage)
        if data._damage is None:
            raise SerializationError("damage must be provided.")
        writer.add_short(data._damage)

    @staticmethod
    def deserialize(reader: EoReader) -> "MapDrainDamageOther":
        """
        Deserializes an instance of `MapDrainDamageOther` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapDrainDamageOther: The data to serialize.
        """
        data: MapDrainDamageOther = MapDrainDamageOther()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._hp_percentage = reader.get_char()
            data._damage = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapDrainDamageOther(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, hp_percentage={repr(self._hp_percentage)}, damage={repr(self._damage)})"
