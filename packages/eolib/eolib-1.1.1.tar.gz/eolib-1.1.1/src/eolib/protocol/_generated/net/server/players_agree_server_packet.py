# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .nearby_info import NearbyInfo
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PlayersAgreeServerPacket(Packet):
    """
    Player has appeared in nearby view
    """
    _byte_size: int = 0
    _nearby: NearbyInfo = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def nearby(self) -> NearbyInfo:
        return self._nearby

    @nearby.setter
    def nearby(self, nearby: NearbyInfo) -> None:
        self._nearby = nearby

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Players

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
        PlayersAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayersAgreeServerPacket") -> None:
        """
        Serializes an instance of `PlayersAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayersAgreeServerPacket): The data to serialize.
        """
        if data._nearby is None:
            raise SerializationError("nearby must be provided.")
        NearbyInfo.serialize(writer, data._nearby)

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayersAgreeServerPacket":
        """
        Deserializes an instance of `PlayersAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayersAgreeServerPacket: The data to serialize.
        """
        data: PlayersAgreeServerPacket = PlayersAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._nearby = NearbyInfo.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayersAgreeServerPacket(byte_size={repr(self._byte_size)}, nearby={repr(self._nearby)})"
