# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .walk_action import WalkAction
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WalkPlayerClientPacket(Packet):
    """
    Walking
    """
    _byte_size: int = 0
    _walk_action: WalkAction = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def walk_action(self) -> WalkAction:
        return self._walk_action

    @walk_action.setter
    def walk_action(self, walk_action: WalkAction) -> None:
        self._walk_action = walk_action

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Walk

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Player

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WalkPlayerClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WalkPlayerClientPacket") -> None:
        """
        Serializes an instance of `WalkPlayerClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WalkPlayerClientPacket): The data to serialize.
        """
        if data._walk_action is None:
            raise SerializationError("walk_action must be provided.")
        WalkAction.serialize(writer, data._walk_action)

    @staticmethod
    def deserialize(reader: EoReader) -> "WalkPlayerClientPacket":
        """
        Deserializes an instance of `WalkPlayerClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WalkPlayerClientPacket: The data to serialize.
        """
        data: WalkPlayerClientPacket = WalkPlayerClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._walk_action = WalkAction.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WalkPlayerClientPacket(byte_size={repr(self._byte_size)}, walk_action={repr(self._walk_action)})"
