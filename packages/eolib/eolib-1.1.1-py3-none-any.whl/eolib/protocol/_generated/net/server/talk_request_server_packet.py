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

class TalkRequestServerPacket(Packet):
    """
    Guild chat message
    """
    _byte_size: int = 0
    _player_name: str = None # type: ignore [assignment]
    _message: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_name(self) -> str:
        return self._player_name

    @player_name.setter
    def player_name(self, player_name: str) -> None:
        self._player_name = player_name

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = message

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Talk

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TalkRequestServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkRequestServerPacket") -> None:
        """
        Serializes an instance of `TalkRequestServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkRequestServerPacket): The data to serialize.
        """
        if data._player_name is None:
            raise SerializationError("player_name must be provided.")
        writer.add_string(data._player_name)
        writer.add_byte(0xFF)
        if data._message is None:
            raise SerializationError("message must be provided.")
        writer.add_string(data._message)

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkRequestServerPacket":
        """
        Deserializes an instance of `TalkRequestServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkRequestServerPacket: The data to serialize.
        """
        data: TalkRequestServerPacket = TalkRequestServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._player_name = reader.get_string()
            reader.next_chunk()
            data._message = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkRequestServerPacket(byte_size={repr(self._byte_size)}, player_name={repr(self._player_name)}, message={repr(self._message)})"
