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

class WelcomeRequestClientPacket(Packet):
    """
    Selected a character
    """
    _byte_size: int = 0
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
        return PacketFamily.Welcome

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
        WelcomeRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WelcomeRequestClientPacket") -> None:
        """
        Serializes an instance of `WelcomeRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WelcomeRequestClientPacket): The data to serialize.
        """
        if data._character_id is None:
            raise SerializationError("character_id must be provided.")
        writer.add_int(data._character_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "WelcomeRequestClientPacket":
        """
        Deserializes an instance of `WelcomeRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WelcomeRequestClientPacket: The data to serialize.
        """
        data: WelcomeRequestClientPacket = WelcomeRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._character_id = reader.get_int()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WelcomeRequestClientPacket(byte_size={repr(self._byte_size)}, character_id={repr(self._character_id)})"
