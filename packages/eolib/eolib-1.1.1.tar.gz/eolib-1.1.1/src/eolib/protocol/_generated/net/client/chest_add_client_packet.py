# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestAddClientPacket(Packet):
    """
    Placing an item in to a chest
    """
    _byte_size: int = 0
    _coords: Coords = None # type: ignore [assignment]
    _add_item: ThreeItem = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def coords(self) -> Coords:
        return self._coords

    @coords.setter
    def coords(self, coords: Coords) -> None:
        self._coords = coords

    @property
    def add_item(self) -> ThreeItem:
        return self._add_item

    @add_item.setter
    def add_item(self, add_item: ThreeItem) -> None:
        self._add_item = add_item

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
        return PacketAction.Add

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ChestAddClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestAddClientPacket") -> None:
        """
        Serializes an instance of `ChestAddClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestAddClientPacket): The data to serialize.
        """
        if data._coords is None:
            raise SerializationError("coords must be provided.")
        Coords.serialize(writer, data._coords)
        if data._add_item is None:
            raise SerializationError("add_item must be provided.")
        ThreeItem.serialize(writer, data._add_item)

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestAddClientPacket":
        """
        Deserializes an instance of `ChestAddClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestAddClientPacket: The data to serialize.
        """
        data: ChestAddClientPacket = ChestAddClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._coords = Coords.deserialize(reader)
            data._add_item = ThreeItem.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestAddClientPacket(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, add_item={repr(self._add_item)})"
