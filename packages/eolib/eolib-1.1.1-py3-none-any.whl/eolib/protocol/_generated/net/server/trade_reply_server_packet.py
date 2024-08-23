# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .trade_item_data import TradeItemData
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TradeReplyServerPacket(Packet):
    """
    Trade updated (items changed)
    """
    _byte_size: int = 0
    _trade_data: TradeItemData = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def trade_data(self) -> TradeItemData:
        return self._trade_data

    @trade_data.setter
    def trade_data(self, trade_data: TradeItemData) -> None:
        self._trade_data = trade_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Trade

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TradeReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeReplyServerPacket") -> None:
        """
        Serializes an instance of `TradeReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeReplyServerPacket): The data to serialize.
        """
        if data._trade_data is None:
            raise SerializationError("trade_data must be provided.")
        TradeItemData.serialize(writer, data._trade_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeReplyServerPacket":
        """
        Deserializes an instance of `TradeReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeReplyServerPacket: The data to serialize.
        """
        data: TradeReplyServerPacket = TradeReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._trade_data = TradeItemData.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeReplyServerPacket(byte_size={repr(self._byte_size)}, trade_data={repr(self._trade_data)})"
