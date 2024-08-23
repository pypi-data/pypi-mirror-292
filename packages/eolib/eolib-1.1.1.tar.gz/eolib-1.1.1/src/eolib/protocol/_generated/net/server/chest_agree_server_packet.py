# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestAgreeServerPacket(Packet):
    """
    Chest contents updating
    """
    _byte_size: int = 0
    _items: list[ThreeItem] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def items(self) -> list[ThreeItem]:
        return self._items

    @items.setter
    def items(self, items: list[ThreeItem]) -> None:
        self._items = items

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Chest

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
        ChestAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestAgreeServerPacket") -> None:
        """
        Serializes an instance of `ChestAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestAgreeServerPacket): The data to serialize.
        """
        if data._items is None:
            raise SerializationError("items must be provided.")
        for i in range(len(data._items)):
            ThreeItem.serialize(writer, data._items[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestAgreeServerPacket":
        """
        Deserializes an instance of `ChestAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestAgreeServerPacket: The data to serialize.
        """
        data: ChestAgreeServerPacket = ChestAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            items_length = int(reader.remaining / 5)
            data._items = []
            for i in range(items_length):
                data._items.append(ThreeItem.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestAgreeServerPacket(byte_size={repr(self._byte_size)}, items={repr(self._items)})"
