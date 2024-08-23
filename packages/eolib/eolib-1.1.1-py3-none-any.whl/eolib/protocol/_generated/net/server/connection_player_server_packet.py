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

class ConnectionPlayerServerPacket(Packet):
    """
    Ping request
    """
    _byte_size: int = 0
    _seq1: int = None # type: ignore [assignment]
    _seq2: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def seq1(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._seq1

    @seq1.setter
    def seq1(self, seq1: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._seq1 = seq1

    @property
    def seq2(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._seq2

    @seq2.setter
    def seq2(self, seq2: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._seq2 = seq2

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Connection

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Player

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ConnectionPlayerServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ConnectionPlayerServerPacket") -> None:
        """
        Serializes an instance of `ConnectionPlayerServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ConnectionPlayerServerPacket): The data to serialize.
        """
        if data._seq1 is None:
            raise SerializationError("seq1 must be provided.")
        writer.add_short(data._seq1)
        if data._seq2 is None:
            raise SerializationError("seq2 must be provided.")
        writer.add_char(data._seq2)

    @staticmethod
    def deserialize(reader: EoReader) -> "ConnectionPlayerServerPacket":
        """
        Deserializes an instance of `ConnectionPlayerServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ConnectionPlayerServerPacket: The data to serialize.
        """
        data: ConnectionPlayerServerPacket = ConnectionPlayerServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._seq1 = reader.get_short()
            data._seq2 = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ConnectionPlayerServerPacket(byte_size={repr(self._byte_size)}, seq1={repr(self._seq1)}, seq2={repr(self._seq2)})"
