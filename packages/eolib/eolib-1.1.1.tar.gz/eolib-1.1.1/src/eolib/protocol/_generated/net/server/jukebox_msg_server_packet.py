# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class JukeboxMsgServerPacket(Packet):
    """
    Someone playing a note with the bard skill nearby
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _direction: Direction = None # type: ignore [assignment]
    _instrument_id: int = None # type: ignore [assignment]
    _note_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._player_id

    @player_id.setter
    def player_id(self, player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._player_id = player_id

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

    @property
    def instrument_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._instrument_id

    @instrument_id.setter
    def instrument_id(self, instrument_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._instrument_id = instrument_id

    @property
    def note_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._note_id

    @note_id.setter
    def note_id(self, note_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._note_id = note_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Jukebox

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Msg

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        JukeboxMsgServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "JukeboxMsgServerPacket") -> None:
        """
        Serializes an instance of `JukeboxMsgServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (JukeboxMsgServerPacket): The data to serialize.
        """
        if data._player_id is None:
            raise SerializationError("player_id must be provided.")
        writer.add_short(data._player_id)
        if data._direction is None:
            raise SerializationError("direction must be provided.")
        writer.add_char(int(data._direction))
        if data._instrument_id is None:
            raise SerializationError("instrument_id must be provided.")
        writer.add_char(data._instrument_id)
        if data._note_id is None:
            raise SerializationError("note_id must be provided.")
        writer.add_char(data._note_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "JukeboxMsgServerPacket":
        """
        Deserializes an instance of `JukeboxMsgServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            JukeboxMsgServerPacket: The data to serialize.
        """
        data: JukeboxMsgServerPacket = JukeboxMsgServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._direction = Direction(reader.get_char())
            data._instrument_id = reader.get_char()
            data._note_id = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"JukeboxMsgServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, direction={repr(self._direction)}, instrument_id={repr(self._instrument_id)}, note_id={repr(self._note_id)})"
