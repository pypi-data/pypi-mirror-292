# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MusicPlayerServerPacket(Packet):
    """
    Sound effect
    """
    _byte_size: int = 0
    _sound_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def sound_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._sound_id

    @sound_id.setter
    def sound_id(self, sound_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._sound_id = sound_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Music

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
        MusicPlayerServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "MusicPlayerServerPacket") -> None:
        """
        Serializes an instance of `MusicPlayerServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MusicPlayerServerPacket): The data to serialize.
        """
        if data._sound_id is None:
            raise SerializationError("sound_id must be provided.")
        writer.add_char(data._sound_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "MusicPlayerServerPacket":
        """
        Deserializes an instance of `MusicPlayerServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MusicPlayerServerPacket: The data to serialize.
        """
        data: MusicPlayerServerPacket = MusicPlayerServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._sound_id = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MusicPlayerServerPacket(byte_size={repr(self._byte_size)}, sound_id={repr(self._sound_id)})"
