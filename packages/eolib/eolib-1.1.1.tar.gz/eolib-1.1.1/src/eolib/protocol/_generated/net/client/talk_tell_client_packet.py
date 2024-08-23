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

class TalkTellClientPacket(Packet):
    """
    Private chat message
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _message: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = message

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Talk

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Tell

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TalkTellClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkTellClientPacket") -> None:
        """
        Serializes an instance of `TalkTellClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkTellClientPacket): The data to serialize.
        """
        if data._name is None:
            raise SerializationError("name must be provided.")
        writer.add_string(data._name)
        writer.add_byte(0xFF)
        if data._message is None:
            raise SerializationError("message must be provided.")
        writer.add_string(data._message)

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkTellClientPacket":
        """
        Deserializes an instance of `TalkTellClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkTellClientPacket: The data to serialize.
        """
        data: TalkTellClientPacket = TalkTellClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._message = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkTellClientPacket(byte_size={repr(self._byte_size)}, name={repr(self._name)}, message={repr(self._message)})"
