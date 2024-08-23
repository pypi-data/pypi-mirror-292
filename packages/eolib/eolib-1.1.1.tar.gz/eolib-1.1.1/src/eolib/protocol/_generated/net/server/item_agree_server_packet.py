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

class ItemAgreeServerPacket(Packet):
    """
    Reply to using an item that you don&#x27;t have
    """
    _byte_size: int = 0
    _item_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._item_id

    @item_id.setter
    def item_id(self, item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._item_id = item_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Item

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemAgreeServerPacket") -> None:
        """
        Serializes an instance of `ItemAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemAgreeServerPacket): The data to serialize.
        """
        if data._item_id is None:
            raise SerializationError("item_id must be provided.")
        writer.add_short(data._item_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemAgreeServerPacket":
        """
        Deserializes an instance of `ItemAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemAgreeServerPacket: The data to serialize.
        """
        data: ItemAgreeServerPacket = ItemAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._item_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemAgreeServerPacket(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)})"
