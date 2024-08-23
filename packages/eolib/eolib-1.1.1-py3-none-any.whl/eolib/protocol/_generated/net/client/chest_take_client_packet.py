# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestTakeClientPacket(Packet):
    """
    Taking an item from a chest
    """
    _byte_size: int = 0
    _coords: Coords = None # type: ignore [assignment]
    _take_item_id: int = None # type: ignore [assignment]

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
    def take_item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._take_item_id

    @take_item_id.setter
    def take_item_id(self, take_item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._take_item_id = take_item_id

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
        return PacketAction.Take

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ChestTakeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestTakeClientPacket") -> None:
        """
        Serializes an instance of `ChestTakeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestTakeClientPacket): The data to serialize.
        """
        if data._coords is None:
            raise SerializationError("coords must be provided.")
        Coords.serialize(writer, data._coords)
        if data._take_item_id is None:
            raise SerializationError("take_item_id must be provided.")
        writer.add_short(data._take_item_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestTakeClientPacket":
        """
        Deserializes an instance of `ChestTakeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestTakeClientPacket: The data to serialize.
        """
        data: ChestTakeClientPacket = ChestTakeClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._coords = Coords.deserialize(reader)
            data._take_item_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestTakeClientPacket(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, take_item_id={repr(self._take_item_id)})"
