# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class LockerOpenServerPacket(Packet):
    """
    Opening a bank locker
    """
    _byte_size: int = 0
    _locker_coords: Coords = None # type: ignore [assignment]
    _locker_items: list[ThreeItem] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def locker_coords(self) -> Coords:
        return self._locker_coords

    @locker_coords.setter
    def locker_coords(self, locker_coords: Coords) -> None:
        self._locker_coords = locker_coords

    @property
    def locker_items(self) -> list[ThreeItem]:
        return self._locker_items

    @locker_items.setter
    def locker_items(self, locker_items: list[ThreeItem]) -> None:
        self._locker_items = locker_items

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Locker

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        LockerOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LockerOpenServerPacket") -> None:
        """
        Serializes an instance of `LockerOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LockerOpenServerPacket): The data to serialize.
        """
        if data._locker_coords is None:
            raise SerializationError("locker_coords must be provided.")
        Coords.serialize(writer, data._locker_coords)
        if data._locker_items is None:
            raise SerializationError("locker_items must be provided.")
        for i in range(len(data._locker_items)):
            ThreeItem.serialize(writer, data._locker_items[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "LockerOpenServerPacket":
        """
        Deserializes an instance of `LockerOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LockerOpenServerPacket: The data to serialize.
        """
        data: LockerOpenServerPacket = LockerOpenServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._locker_coords = Coords.deserialize(reader)
            locker_items_length = int(reader.remaining / 5)
            data._locker_items = []
            for i in range(locker_items_length):
                data._locker_items.append(ThreeItem.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LockerOpenServerPacket(byte_size={repr(self._byte_size)}, locker_coords={repr(self._locker_coords)}, locker_items={repr(self._locker_items)})"
