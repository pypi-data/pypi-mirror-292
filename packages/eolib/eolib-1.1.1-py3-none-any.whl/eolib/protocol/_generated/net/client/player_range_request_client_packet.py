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

class PlayerRangeRequestClientPacket(Packet):
    """
    Requesting info about nearby players
    """
    _byte_size: int = 0
    _player_ids: list[int] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_ids(self) -> list[int]:
        """
        Note:
          - Element value range is 0-64008.
        """
        return self._player_ids

    @player_ids.setter
    def player_ids(self, player_ids: list[int]) -> None:
        """
        Note:
          - Element value range is 0-64008.
        """
        self._player_ids = player_ids

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.PlayerRange

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
        PlayerRangeRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayerRangeRequestClientPacket") -> None:
        """
        Serializes an instance of `PlayerRangeRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayerRangeRequestClientPacket): The data to serialize.
        """
        if data._player_ids is None:
            raise SerializationError("player_ids must be provided.")
        for i in range(len(data._player_ids)):
            writer.add_short(data._player_ids[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayerRangeRequestClientPacket":
        """
        Deserializes an instance of `PlayerRangeRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayerRangeRequestClientPacket: The data to serialize.
        """
        data: PlayerRangeRequestClientPacket = PlayerRangeRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_ids_length = int(reader.remaining / 2)
            data._player_ids = []
            for i in range(player_ids_length):
                data._player_ids.append(reader.get_short())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayerRangeRequestClientPacket(byte_size={repr(self._byte_size)}, player_ids={repr(self._player_ids)})"
