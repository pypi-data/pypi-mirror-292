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

class GuildAcceptServerPacket(Packet):
    """
    Update guild rank
    """
    _byte_size: int = 0
    _rank: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rank(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._rank = rank

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildAcceptServerPacket") -> None:
        """
        Serializes an instance of `GuildAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildAcceptServerPacket): The data to serialize.
        """
        if data._rank is None:
            raise SerializationError("rank must be provided.")
        writer.add_char(data._rank)

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildAcceptServerPacket":
        """
        Deserializes an instance of `GuildAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildAcceptServerPacket: The data to serialize.
        """
        data: GuildAcceptServerPacket = GuildAcceptServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._rank = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildAcceptServerPacket(byte_size={repr(self._byte_size)}, rank={repr(self._rank)})"
