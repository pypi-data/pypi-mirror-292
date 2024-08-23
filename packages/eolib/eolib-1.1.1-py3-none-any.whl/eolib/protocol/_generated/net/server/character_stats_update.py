# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats import CharacterSecondaryStats
from .character_base_stats import CharacterBaseStats
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsUpdate:
    """
    Character stats data.
    Sent when stats are updated.
    """
    _byte_size: int = 0
    _base_stats: CharacterBaseStats = None # type: ignore [assignment]
    _max_hp: int = None # type: ignore [assignment]
    _max_tp: int = None # type: ignore [assignment]
    _max_sp: int = None # type: ignore [assignment]
    _max_weight: int = None # type: ignore [assignment]
    _secondary_stats: CharacterSecondaryStats = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def base_stats(self) -> CharacterBaseStats:
        return self._base_stats

    @base_stats.setter
    def base_stats(self, base_stats: CharacterBaseStats) -> None:
        self._base_stats = base_stats

    @property
    def max_hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_hp

    @max_hp.setter
    def max_hp(self, max_hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_hp = max_hp

    @property
    def max_tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_tp

    @max_tp.setter
    def max_tp(self, max_tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_tp = max_tp

    @property
    def max_sp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_sp

    @max_sp.setter
    def max_sp(self, max_sp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_sp = max_sp

    @property
    def max_weight(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_weight

    @max_weight.setter
    def max_weight(self, max_weight: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_weight = max_weight

    @property
    def secondary_stats(self) -> CharacterSecondaryStats:
        return self._secondary_stats

    @secondary_stats.setter
    def secondary_stats(self, secondary_stats: CharacterSecondaryStats) -> None:
        self._secondary_stats = secondary_stats

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsUpdate") -> None:
        """
        Serializes an instance of `CharacterStatsUpdate` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsUpdate): The data to serialize.
        """
        if data._base_stats is None:
            raise SerializationError("base_stats must be provided.")
        CharacterBaseStats.serialize(writer, data._base_stats)
        if data._max_hp is None:
            raise SerializationError("max_hp must be provided.")
        writer.add_short(data._max_hp)
        if data._max_tp is None:
            raise SerializationError("max_tp must be provided.")
        writer.add_short(data._max_tp)
        if data._max_sp is None:
            raise SerializationError("max_sp must be provided.")
        writer.add_short(data._max_sp)
        if data._max_weight is None:
            raise SerializationError("max_weight must be provided.")
        writer.add_short(data._max_weight)
        if data._secondary_stats is None:
            raise SerializationError("secondary_stats must be provided.")
        CharacterSecondaryStats.serialize(writer, data._secondary_stats)

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsUpdate":
        """
        Deserializes an instance of `CharacterStatsUpdate` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsUpdate: The data to serialize.
        """
        data: CharacterStatsUpdate = CharacterStatsUpdate()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._base_stats = CharacterBaseStats.deserialize(reader)
            data._max_hp = reader.get_short()
            data._max_tp = reader.get_short()
            data._max_sp = reader.get_short()
            data._max_weight = reader.get_short()
            data._secondary_stats = CharacterSecondaryStats.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsUpdate(byte_size={repr(self._byte_size)}, base_stats={repr(self._base_stats)}, max_hp={repr(self._max_hp)}, max_tp={repr(self._max_tp)}, max_sp={repr(self._max_sp)}, max_weight={repr(self._max_weight)}, secondary_stats={repr(self._secondary_stats)})"
