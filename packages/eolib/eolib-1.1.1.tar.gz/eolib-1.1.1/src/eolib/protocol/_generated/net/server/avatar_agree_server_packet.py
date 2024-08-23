# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .avatar_change import AvatarChange
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AvatarAgreeServerPacket(Packet):
    """
    Nearby player changed appearance
    """
    _byte_size: int = 0
    _change: AvatarChange = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def change(self) -> AvatarChange:
        return self._change

    @change.setter
    def change(self, change: AvatarChange) -> None:
        self._change = change

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Avatar

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
        AvatarAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AvatarAgreeServerPacket") -> None:
        """
        Serializes an instance of `AvatarAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AvatarAgreeServerPacket): The data to serialize.
        """
        if data._change is None:
            raise SerializationError("change must be provided.")
        AvatarChange.serialize(writer, data._change)

    @staticmethod
    def deserialize(reader: EoReader) -> "AvatarAgreeServerPacket":
        """
        Deserializes an instance of `AvatarAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AvatarAgreeServerPacket: The data to serialize.
        """
        data: AvatarAgreeServerPacket = AvatarAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._change = AvatarChange.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AvatarAgreeServerPacket(byte_size={repr(self._byte_size)}, change={repr(self._change)})"
