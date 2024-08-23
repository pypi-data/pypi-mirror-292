# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AttackUseClientPacket(Packet):
    """
    Attacking
    """
    _byte_size: int = 0
    _direction: Direction = None # type: ignore [assignment]
    _timestamp: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

    @property
    def timestamp(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._timestamp = timestamp

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Attack

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Use

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AttackUseClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AttackUseClientPacket") -> None:
        """
        Serializes an instance of `AttackUseClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AttackUseClientPacket): The data to serialize.
        """
        if data._direction is None:
            raise SerializationError("direction must be provided.")
        writer.add_char(int(data._direction))
        if data._timestamp is None:
            raise SerializationError("timestamp must be provided.")
        writer.add_three(data._timestamp)

    @staticmethod
    def deserialize(reader: EoReader) -> "AttackUseClientPacket":
        """
        Deserializes an instance of `AttackUseClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AttackUseClientPacket: The data to serialize.
        """
        data: AttackUseClientPacket = AttackUseClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._direction = Direction(reader.get_char())
            data._timestamp = reader.get_three()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AttackUseClientPacket(byte_size={repr(self._byte_size)}, direction={repr(self._direction)}, timestamp={repr(self._timestamp)})"
