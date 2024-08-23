# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SitReplyServerPacket(Packet):
    """
    Your character sitting down
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _coords: Coords = None # type: ignore [assignment]
    _direction: Direction = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._player_id

    @player_id.setter
    def player_id(self, player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._player_id = player_id

    @property
    def coords(self) -> Coords:
        return self._coords

    @coords.setter
    def coords(self, coords: Coords) -> None:
        self._coords = coords

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Sit

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
        SitReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SitReplyServerPacket") -> None:
        """
        Serializes an instance of `SitReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SitReplyServerPacket): The data to serialize.
        """
        if data._player_id is None:
            raise SerializationError("player_id must be provided.")
        writer.add_short(data._player_id)
        if data._coords is None:
            raise SerializationError("coords must be provided.")
        Coords.serialize(writer, data._coords)
        if data._direction is None:
            raise SerializationError("direction must be provided.")
        writer.add_char(int(data._direction))
        writer.add_char(0)

    @staticmethod
    def deserialize(reader: EoReader) -> "SitReplyServerPacket":
        """
        Deserializes an instance of `SitReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SitReplyServerPacket: The data to serialize.
        """
        data: SitReplyServerPacket = SitReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._coords = Coords.deserialize(reader)
            data._direction = Direction(reader.get_char())
            reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SitReplyServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, coords={repr(self._coords)}, direction={repr(self._direction)})"
