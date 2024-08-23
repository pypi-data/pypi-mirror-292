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

class GuildRankClientPacket(Packet):
    """
    Update a member&#x27;s rank
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _rank: int = None # type: ignore [assignment]
    _member_name: str = None # type: ignore [assignment]

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
    def rank(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._rank = rank

    @property
    def member_name(self) -> str:
        return self._member_name

    @member_name.setter
    def member_name(self, member_name: str) -> None:
        self._member_name = member_name

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
        return PacketAction.Rank

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildRankClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildRankClientPacket") -> None:
        """
        Serializes an instance of `GuildRankClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildRankClientPacket): The data to serialize.
        """
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_int(data._session_id)
        if data._rank is None:
            raise SerializationError("rank must be provided.")
        writer.add_char(data._rank)
        if data._member_name is None:
            raise SerializationError("member_name must be provided.")
        writer.add_string(data._member_name)

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildRankClientPacket":
        """
        Deserializes an instance of `GuildRankClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildRankClientPacket: The data to serialize.
        """
        data: GuildRankClientPacket = GuildRankClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._session_id = reader.get_int()
            data._rank = reader.get_char()
            data._member_name = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildRankClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, rank={repr(self._rank)}, member_name={repr(self._member_name)})"
