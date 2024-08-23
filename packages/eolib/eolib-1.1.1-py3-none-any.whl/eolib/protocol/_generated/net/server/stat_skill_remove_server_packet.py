# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillRemoveServerPacket(Packet):
    """
    Response to forgetting a skill at a skill master
    """
    _byte_size: int = 0
    _spell_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def spell_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._spell_id

    @spell_id.setter
    def spell_id(self, spell_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._spell_id = spell_id

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
        return PacketAction.Remove

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillRemoveServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillRemoveServerPacket") -> None:
        """
        Serializes an instance of `StatSkillRemoveServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillRemoveServerPacket): The data to serialize.
        """
        if data._spell_id is None:
            raise SerializationError("spell_id must be provided.")
        writer.add_short(data._spell_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillRemoveServerPacket":
        """
        Deserializes an instance of `StatSkillRemoveServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillRemoveServerPacket: The data to serialize.
        """
        data: StatSkillRemoveServerPacket = StatSkillRemoveServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._spell_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillRemoveServerPacket(byte_size={repr(self._byte_size)}, spell_id={repr(self._spell_id)})"
