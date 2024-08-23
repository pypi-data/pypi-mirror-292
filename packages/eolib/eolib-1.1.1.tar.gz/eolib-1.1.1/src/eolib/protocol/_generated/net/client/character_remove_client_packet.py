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

class CharacterRemoveClientPacket(Packet):
    """
    Confirm deleting character from an account
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _character_id: int = None # type: ignore [assignment]

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
          - Value range is 0-64008.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._session_id = session_id

    @property
    def character_id(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._character_id

    @character_id.setter
    def character_id(self, character_id: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._character_id = character_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Character

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Remove

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CharacterRemoveClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterRemoveClientPacket") -> None:
        """
        Serializes an instance of `CharacterRemoveClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterRemoveClientPacket): The data to serialize.
        """
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_short(data._session_id)
        if data._character_id is None:
            raise SerializationError("character_id must be provided.")
        writer.add_int(data._character_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterRemoveClientPacket":
        """
        Deserializes an instance of `CharacterRemoveClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterRemoveClientPacket: The data to serialize.
        """
        data: CharacterRemoveClientPacket = CharacterRemoveClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._session_id = reader.get_short()
            data._character_id = reader.get_int()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterRemoveClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, character_id={repr(self._character_id)})"
