# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .global_backfill_message import GlobalBackfillMessage
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TalkListServerPacket(Packet):
    """
    Global chat backfill.
    Sent by the official game server when a player opens the global chat tab.
    """
    _byte_size: int = 0
    _messages: list[GlobalBackfillMessage] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def messages(self) -> list[GlobalBackfillMessage]:
        return self._messages

    @messages.setter
    def messages(self, messages: list[GlobalBackfillMessage]) -> None:
        self._messages = messages

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
        return PacketAction.List

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TalkListServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkListServerPacket") -> None:
        """
        Serializes an instance of `TalkListServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkListServerPacket): The data to serialize.
        """
        if data._messages is None:
            raise SerializationError("messages must be provided.")
        for i in range(len(data._messages)):
            if i > 0:
                writer.add_byte(0xFF)
            GlobalBackfillMessage.serialize(writer, data._messages[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkListServerPacket":
        """
        Deserializes an instance of `TalkListServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkListServerPacket: The data to serialize.
        """
        data: TalkListServerPacket = TalkListServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._messages = []
            while reader.remaining > 0:
                data._messages.append(GlobalBackfillMessage.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkListServerPacket(byte_size={repr(self._byte_size)}, messages={repr(self._messages)})"
