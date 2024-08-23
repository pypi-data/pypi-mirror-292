# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .character_icon import CharacterIcon
from .character_details import CharacterDetails
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class BookReplyServerPacket(Packet):
    """
    Reply to requesting a book
    """
    _byte_size: int = 0
    _details: CharacterDetails = None # type: ignore [assignment]
    _icon: CharacterIcon = None # type: ignore [assignment]
    _quest_names: list[str] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def details(self) -> CharacterDetails:
        return self._details

    @details.setter
    def details(self, details: CharacterDetails) -> None:
        self._details = details

    @property
    def icon(self) -> CharacterIcon:
        return self._icon

    @icon.setter
    def icon(self, icon: CharacterIcon) -> None:
        self._icon = icon

    @property
    def quest_names(self) -> list[str]:
        return self._quest_names

    @quest_names.setter
    def quest_names(self, quest_names: list[str]) -> None:
        self._quest_names = quest_names

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Book

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
        BookReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BookReplyServerPacket") -> None:
        """
        Serializes an instance of `BookReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BookReplyServerPacket): The data to serialize.
        """
        if data._details is None:
            raise SerializationError("details must be provided.")
        CharacterDetails.serialize(writer, data._details)
        if data._icon is None:
            raise SerializationError("icon must be provided.")
        writer.add_char(int(data._icon))
        writer.add_byte(0xFF)
        if data._quest_names is None:
            raise SerializationError("quest_names must be provided.")
        for i in range(len(data._quest_names)):
            if i > 0:
                writer.add_byte(0xFF)
            writer.add_string(data._quest_names[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "BookReplyServerPacket":
        """
        Deserializes an instance of `BookReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BookReplyServerPacket: The data to serialize.
        """
        data: BookReplyServerPacket = BookReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._details = CharacterDetails.deserialize(reader)
            data._icon = CharacterIcon(reader.get_char())
            reader.next_chunk()
            data._quest_names = []
            while reader.remaining > 0:
                data._quest_names.append(reader.get_string())
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BookReplyServerPacket(byte_size={repr(self._byte_size)}, details={repr(self._details)}, icon={repr(self._icon)}, quest_names={repr(self._quest_names)})"
