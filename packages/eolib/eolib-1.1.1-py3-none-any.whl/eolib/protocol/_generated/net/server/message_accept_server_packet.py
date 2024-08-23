# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MessageAcceptServerPacket(Packet):
    """
    Large message box
    """
    _byte_size: int = 0
    _messages: list[str] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def messages(self) -> list[str]:
        """
        Note:
          - Length must be `4`.
        """
        return self._messages

    @messages.setter
    def messages(self, messages: list[str]) -> None:
        """
        Note:
          - Length must be `4`.
        """
        self._messages = messages

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Message

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        MessageAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "MessageAcceptServerPacket") -> None:
        """
        Serializes an instance of `MessageAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MessageAcceptServerPacket): The data to serialize.
        """
        if data._messages is None:
            raise SerializationError("messages must be provided.")
        if len(data._messages) != 4:
            raise SerializationError(f"Expected length of messages to be exactly 4, got {len(data._messages)}.")
        for i in range(4):
            if i > 0:
                writer.add_byte(0xFF)
            writer.add_string(data._messages[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "MessageAcceptServerPacket":
        """
        Deserializes an instance of `MessageAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MessageAcceptServerPacket: The data to serialize.
        """
        data: MessageAcceptServerPacket = MessageAcceptServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._messages = []
            for i in range(4):
                data._messages.append(reader.get_string())
                if i + 1 < 4:
                    reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MessageAcceptServerPacket(byte_size={repr(self._byte_size)}, messages={repr(self._messages)})"
