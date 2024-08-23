# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AttackErrorServerPacket(Packet):
    """
    Show flood protection message (vestigial)
    """
    _byte_size: int = 0

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Attack

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Error

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AttackErrorServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AttackErrorServerPacket") -> None:
        """
        Serializes an instance of `AttackErrorServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AttackErrorServerPacket): The data to serialize.
        """
        old_writer_length: int = len(writer)
        if len(writer) == old_writer_length:
            writer.add_byte(255)

    @staticmethod
    def deserialize(reader: EoReader) -> "AttackErrorServerPacket":
        """
        Deserializes an instance of `AttackErrorServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AttackErrorServerPacket: The data to serialize.
        """
        data: AttackErrorServerPacket = AttackErrorServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            if reader.position == reader_start_position:
                reader.get_byte()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AttackErrorServerPacket(byte_size={repr(self._byte_size)})"
