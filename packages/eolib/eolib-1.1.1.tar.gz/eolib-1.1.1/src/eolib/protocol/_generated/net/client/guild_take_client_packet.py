# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .guild_info_type import GuildInfoType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildTakeClientPacket(Packet):
    """
    Request guild description, rank list, or bank balance
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _info_type: GuildInfoType = None # type: ignore [assignment]

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
    def info_type(self) -> GuildInfoType:
        return self._info_type

    @info_type.setter
    def info_type(self, info_type: GuildInfoType) -> None:
        self._info_type = info_type

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
        return PacketAction.Take

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildTakeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildTakeClientPacket") -> None:
        """
        Serializes an instance of `GuildTakeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildTakeClientPacket): The data to serialize.
        """
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_int(data._session_id)
        if data._info_type is None:
            raise SerializationError("info_type must be provided.")
        writer.add_short(int(data._info_type))

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildTakeClientPacket":
        """
        Deserializes an instance of `GuildTakeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildTakeClientPacket: The data to serialize.
        """
        data: GuildTakeClientPacket = GuildTakeClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._session_id = reader.get_int()
            data._info_type = GuildInfoType(reader.get_short())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildTakeClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, info_type={repr(self._info_type)})"
