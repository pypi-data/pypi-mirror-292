# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopBuyClientPacket(Packet):
    """
    Purchasing an item from a shop
    """
    _byte_size: int = 0
    _buy_item: Item = None # type: ignore [assignment]
    _session_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def buy_item(self) -> Item:
        return self._buy_item

    @buy_item.setter
    def buy_item(self, buy_item: Item) -> None:
        self._buy_item = buy_item

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._session_id = session_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Shop

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Buy

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ShopBuyClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopBuyClientPacket") -> None:
        """
        Serializes an instance of `ShopBuyClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopBuyClientPacket): The data to serialize.
        """
        if data._buy_item is None:
            raise SerializationError("buy_item must be provided.")
        Item.serialize(writer, data._buy_item)
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_int(data._session_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopBuyClientPacket":
        """
        Deserializes an instance of `ShopBuyClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopBuyClientPacket: The data to serialize.
        """
        data: ShopBuyClientPacket = ShopBuyClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._buy_item = Item.deserialize(reader)
            data._session_id = reader.get_int()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopBuyClientPacket(byte_size={repr(self._byte_size)}, buy_item={repr(self._buy_item)}, session_id={repr(self._session_id)})"
