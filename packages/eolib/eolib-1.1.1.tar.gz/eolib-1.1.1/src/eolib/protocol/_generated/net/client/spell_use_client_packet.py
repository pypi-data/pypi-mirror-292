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

class SpellUseClientPacket(Packet):
    """
    Raise arm to cast a spell (vestigial)
    """
    _byte_size: int = 0
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
        return PacketFamily.Spell

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
        SpellUseClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SpellUseClientPacket") -> None:
        """
        Serializes an instance of `SpellUseClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SpellUseClientPacket): The data to serialize.
        """
        if data._direction is None:
            raise SerializationError("direction must be provided.")
        writer.add_char(int(data._direction))

    @staticmethod
    def deserialize(reader: EoReader) -> "SpellUseClientPacket":
        """
        Deserializes an instance of `SpellUseClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SpellUseClientPacket: The data to serialize.
        """
        data: SpellUseClientPacket = SpellUseClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._direction = Direction(reader.get_char())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SpellUseClientPacket(byte_size={repr(self._byte_size)}, direction={repr(self._direction)})"
