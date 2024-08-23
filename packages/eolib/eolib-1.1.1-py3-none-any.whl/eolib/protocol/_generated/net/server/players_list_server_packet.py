# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .players_list import PlayersList
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PlayersListServerPacket(Packet):
    """
    Equivalent to INIT_INIT with InitReply.PlayersList
    """
    _byte_size: int = 0
    _players_list: PlayersList = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def players_list(self) -> PlayersList:
        return self._players_list

    @players_list.setter
    def players_list(self, players_list: PlayersList) -> None:
        self._players_list = players_list

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
        return PacketAction.List

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PlayersListServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayersListServerPacket") -> None:
        """
        Serializes an instance of `PlayersListServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayersListServerPacket): The data to serialize.
        """
        if data._players_list is None:
            raise SerializationError("players_list must be provided.")
        PlayersList.serialize(writer, data._players_list)

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayersListServerPacket":
        """
        Deserializes an instance of `PlayersListServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayersListServerPacket: The data to serialize.
        """
        data: PlayersListServerPacket = PlayersListServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._players_list = PlayersList.deserialize(reader)
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayersListServerPacket(byte_size={repr(self._byte_size)}, players_list={repr(self._players_list)})"
