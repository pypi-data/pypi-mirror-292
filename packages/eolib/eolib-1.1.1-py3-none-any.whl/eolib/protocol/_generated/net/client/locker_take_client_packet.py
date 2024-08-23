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

class LockerTakeClientPacket(Packet):
    """
    Taking an item from a bank locker
    """
    _byte_size: int = 0
    _locker_coords: Coords = None # type: ignore [assignment]
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
    def locker_coords(self) -> Coords:
        return self._locker_coords

    @locker_coords.setter
    def locker_coords(self, locker_coords: Coords) -> None:
        self._locker_coords = locker_coords

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
        return PacketFamily.Locker

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
        LockerTakeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LockerTakeClientPacket") -> None:
        """
        Serializes an instance of `LockerTakeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LockerTakeClientPacket): The data to serialize.
        """
        if data._locker_coords is None:
            raise SerializationError("locker_coords must be provided.")
        Coords.serialize(writer, data._locker_coords)
        if data._take_item_id is None:
            raise SerializationError("take_item_id must be provided.")
        writer.add_short(data._take_item_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "LockerTakeClientPacket":
        """
        Deserializes an instance of `LockerTakeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LockerTakeClientPacket: The data to serialize.
        """
        data: LockerTakeClientPacket = LockerTakeClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._locker_coords = Coords.deserialize(reader)
            data._take_item_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LockerTakeClientPacket(byte_size={repr(self._byte_size)}, locker_coords={repr(self._locker_coords)}, take_item_id={repr(self._take_item_id)})"
