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

class GuildCreateServerPacket(Packet):
    """
    Guild created
    """
    _byte_size: int = 0
    _leader_player_id: int = None # type: ignore [assignment]
    _guild_tag: str = None # type: ignore [assignment]
    _guild_name: str = None # type: ignore [assignment]
    _rank_name: str = None # type: ignore [assignment]
    _gold_amount: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def leader_player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._leader_player_id

    @leader_player_id.setter
    def leader_player_id(self, leader_player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._leader_player_id = leader_player_id

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

    @property
    def rank_name(self) -> str:
        return self._rank_name

    @rank_name.setter
    def rank_name(self, rank_name: str) -> None:
        self._rank_name = rank_name

    @property
    def gold_amount(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._gold_amount

    @gold_amount.setter
    def gold_amount(self, gold_amount: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._gold_amount = gold_amount

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
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildCreateServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildCreateServerPacket") -> None:
        """
        Serializes an instance of `GuildCreateServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildCreateServerPacket): The data to serialize.
        """
        if data._leader_player_id is None:
            raise SerializationError("leader_player_id must be provided.")
        writer.add_short(data._leader_player_id)
        writer.add_byte(0xFF)
        if data._guild_tag is None:
            raise SerializationError("guild_tag must be provided.")
        writer.add_string(data._guild_tag)
        writer.add_byte(0xFF)
        if data._guild_name is None:
            raise SerializationError("guild_name must be provided.")
        writer.add_string(data._guild_name)
        writer.add_byte(0xFF)
        if data._rank_name is None:
            raise SerializationError("rank_name must be provided.")
        writer.add_string(data._rank_name)
        writer.add_byte(0xFF)
        if data._gold_amount is None:
            raise SerializationError("gold_amount must be provided.")
        writer.add_int(data._gold_amount)

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildCreateServerPacket":
        """
        Deserializes an instance of `GuildCreateServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildCreateServerPacket: The data to serialize.
        """
        data: GuildCreateServerPacket = GuildCreateServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._leader_player_id = reader.get_short()
            reader.next_chunk()
            data._guild_tag = reader.get_string()
            reader.next_chunk()
            data._guild_name = reader.get_string()
            reader.next_chunk()
            data._rank_name = reader.get_string()
            reader.next_chunk()
            data._gold_amount = reader.get_int()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildCreateServerPacket(byte_size={repr(self._byte_size)}, leader_player_id={repr(self._leader_player_id)}, guild_tag={repr(self._guild_tag)}, guild_name={repr(self._guild_name)}, rank_name={repr(self._rank_name)}, gold_amount={repr(self._gold_amount)})"
