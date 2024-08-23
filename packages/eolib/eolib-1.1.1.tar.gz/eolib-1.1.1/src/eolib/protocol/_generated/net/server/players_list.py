# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .online_player import OnlinePlayer
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PlayersList:
    """
    Information about online players
    """
    _byte_size: int = 0
    _players_count: int = None # type: ignore [assignment]
    _players: list[OnlinePlayer] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def players(self) -> list[OnlinePlayer]:
        """
        Note:
          - Length must be 64008 or less.
        """
        return self._players

    @players.setter
    def players(self, players: list[OnlinePlayer]) -> None:
        """
        Note:
          - Length must be 64008 or less.
        """
        self._players = players
        self._players_count = len(self._players)

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayersList") -> None:
        """
        Serializes an instance of `PlayersList` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayersList): The data to serialize.
        """
        if data._players_count is None:
            raise SerializationError("players_count must be provided.")
        writer.add_short(data._players_count)
        writer.add_byte(0xFF)
        if data._players is None:
            raise SerializationError("players must be provided.")
        if len(data._players) > 64008:
            raise SerializationError(f"Expected length of players to be 64008 or less, got {len(data._players)}.")
        for i in range(data._players_count):
            if i > 0:
                writer.add_byte(0xFF)
            OnlinePlayer.serialize(writer, data._players[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayersList":
        """
        Deserializes an instance of `PlayersList` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayersList: The data to serialize.
        """
        data: PlayersList = PlayersList()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._players_count = reader.get_short()
            reader.next_chunk()
            data._players = []
            for i in range(data._players_count):
                data._players.append(OnlinePlayer.deserialize(reader))
                if i + 1 < data._players_count:
                    reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayersList(byte_size={repr(self._byte_size)}, players={repr(self._players)})"
