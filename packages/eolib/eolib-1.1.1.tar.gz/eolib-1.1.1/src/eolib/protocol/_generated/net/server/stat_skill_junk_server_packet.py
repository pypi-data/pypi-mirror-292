# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_stats_reset import CharacterStatsReset
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillJunkServerPacket(Packet):
    """
    Response to resetting stats and skills at a skill master
    """
    _byte_size: int = 0
    _stats: CharacterStatsReset = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def stats(self) -> CharacterStatsReset:
        return self._stats

    @stats.setter
    def stats(self, stats: CharacterStatsReset) -> None:
        self._stats = stats

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.StatSkill

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Junk

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillJunkServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillJunkServerPacket") -> None:
        """
        Serializes an instance of `StatSkillJunkServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillJunkServerPacket): The data to serialize.
        """
        if data._stats is None:
            raise SerializationError("stats must be provided.")
        CharacterStatsReset.serialize(writer, data._stats)

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillJunkServerPacket":
        """
        Deserializes an instance of `StatSkillJunkServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillJunkServerPacket: The data to serialize.
        """
        data: StatSkillJunkServerPacket = StatSkillJunkServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._stats = CharacterStatsReset.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillJunkServerPacket(byte_size={repr(self._byte_size)}, stats={repr(self._stats)})"
