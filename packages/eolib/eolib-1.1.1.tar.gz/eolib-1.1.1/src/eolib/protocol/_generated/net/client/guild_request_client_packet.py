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

class GuildRequestClientPacket(Packet):
    """
    Requested to create a guild
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _guild_tag: str = None # type: ignore [assignment]
    _guild_name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._session_id = session_id

    @property
    def guild_tag(self) -> str:
        return self._guild_tag

    @guild_tag.setter
    def guild_tag(self, guild_tag: str) -> None:
        self._guild_tag = guild_tag

    @property
    def guild_name(self) -> str:
        return self._guild_name

    @guild_name.setter
    def guild_name(self, guild_name: str) -> None:
        self._guild_name = guild_name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

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
        GuildRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildRequestClientPacket") -> None:
        """
        Serializes an instance of `GuildRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildRequestClientPacket): The data to serialize.
        """
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_int(data._session_id)
        writer.add_byte(0xFF)
        if data._guild_tag is None:
            raise SerializationError("guild_tag must be provided.")
        writer.add_string(data._guild_tag)
        writer.add_byte(0xFF)
        if data._guild_name is None:
            raise SerializationError("guild_name must be provided.")
        writer.add_string(data._guild_name)
        writer.add_byte(0xFF)

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildRequestClientPacket":
        """
        Deserializes an instance of `GuildRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildRequestClientPacket: The data to serialize.
        """
        data: GuildRequestClientPacket = GuildRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._session_id = reader.get_int()
            reader.next_chunk()
            data._guild_tag = reader.get_string()
            reader.next_chunk()
            data._guild_name = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildRequestClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, guild_tag={repr(self._guild_tag)}, guild_name={repr(self._guild_name)})"
