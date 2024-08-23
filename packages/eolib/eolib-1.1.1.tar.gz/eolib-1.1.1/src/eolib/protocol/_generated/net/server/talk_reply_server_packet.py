# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .talk_reply import TalkReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TalkReplyServerPacket(Packet):
    """
    Reply to trying to send a private message
    """
    _byte_size: int = 0
    _reply_code: TalkReply = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> TalkReply:
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: TalkReply) -> None:
        self._reply_code = reply_code

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

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
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TalkReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkReplyServerPacket") -> None:
        """
        Serializes an instance of `TalkReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkReplyServerPacket): The data to serialize.
        """
        if data._reply_code is None:
            raise SerializationError("reply_code must be provided.")
        writer.add_short(int(data._reply_code))
        if data._name is None:
            raise SerializationError("name must be provided.")
        writer.add_string(data._name)

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkReplyServerPacket":
        """
        Deserializes an instance of `TalkReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkReplyServerPacket: The data to serialize.
        """
        data: TalkReplyServerPacket = TalkReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = TalkReply(reader.get_short())
            data._name = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, name={repr(self._name)})"
