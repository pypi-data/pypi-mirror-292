# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .marriage_reply import MarriageReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MarriageReplyServerPacket(Packet):
    """
    Reply to client Marriage-family packets
    """
    _byte_size: int = 0
    _reply_code: MarriageReply = None # type: ignore [assignment]
    _reply_code_data: 'MarriageReplyServerPacket.ReplyCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> MarriageReply:
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: MarriageReply) -> None:
        self._reply_code = reply_code

    @property
    def reply_code_data(self) -> 'MarriageReplyServerPacket.ReplyCodeData':
        """
        MarriageReplyServerPacket.ReplyCodeData: Gets or sets the data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @reply_code_data.setter
    def reply_code_data(self, reply_code_data: 'MarriageReplyServerPacket.ReplyCodeData') -> None:
        self._reply_code_data = reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Marriage

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
        MarriageReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "MarriageReplyServerPacket") -> None:
        """
        Serializes an instance of `MarriageReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MarriageReplyServerPacket): The data to serialize.
        """
        if data._reply_code is None:
            raise SerializationError("reply_code must be provided.")
        writer.add_short(int(data._reply_code))
        if data._reply_code == MarriageReply.Success:
            if not isinstance(data._reply_code_data, MarriageReplyServerPacket.ReplyCodeDataSuccess):
                raise SerializationError("Expected reply_code_data to be type MarriageReplyServerPacket.ReplyCodeDataSuccess for reply_code " + MarriageReply(data._reply_code).name + ".")
            MarriageReplyServerPacket.ReplyCodeDataSuccess.serialize(writer, data._reply_code_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "MarriageReplyServerPacket":
        """
        Deserializes an instance of `MarriageReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MarriageReplyServerPacket: The data to serialize.
        """
        data: MarriageReplyServerPacket = MarriageReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = MarriageReply(reader.get_short())
            if data._reply_code == MarriageReply.Success:
                data._reply_code_data = MarriageReplyServerPacket.ReplyCodeDataSuccess.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MarriageReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['MarriageReplyServerPacket.ReplyCodeDataSuccess', None]
    ReplyCodeData.__doc__ = \
        """
        Data associated with different values of the `reply_code` field.
        """

    class ReplyCodeDataSuccess:
        """
        Data associated with reply_code value MarriageReply.Success
        """
        _byte_size: int = 0
        _gold_amount: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def gold_amount(self) -> int:
            """
            Note:
              - Value range is 0-4097152080.
            """
            return self._gold_amount

        @gold_amount.setter
        def gold_amount(self, gold_amount: int) -> None:
            """
            Note:
              - Value range is 0-4097152080.
            """
            self._gold_amount = gold_amount

        @staticmethod
        def serialize(writer: EoWriter, data: "MarriageReplyServerPacket.ReplyCodeDataSuccess") -> None:
            """
            Serializes an instance of `MarriageReplyServerPacket.ReplyCodeDataSuccess` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (MarriageReplyServerPacket.ReplyCodeDataSuccess): The data to serialize.
            """
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)

        @staticmethod
        def deserialize(reader: EoReader) -> "MarriageReplyServerPacket.ReplyCodeDataSuccess":
            """
            Deserializes an instance of `MarriageReplyServerPacket.ReplyCodeDataSuccess` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                MarriageReplyServerPacket.ReplyCodeDataSuccess: The data to serialize.
            """
            data: MarriageReplyServerPacket.ReplyCodeDataSuccess = MarriageReplyServerPacket.ReplyCodeDataSuccess()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._gold_amount = reader.get_int()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"MarriageReplyServerPacket.ReplyCodeDataSuccess(byte_size={repr(self._byte_size)}, gold_amount={repr(self._gold_amount)})"
