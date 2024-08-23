# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .party_reply_code import PartyReplyCode
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyReplyServerPacket(Packet):
    """
    Failed party invite / join request
    """
    _byte_size: int = 0
    _reply_code: PartyReplyCode = None # type: ignore [assignment]
    _reply_code_data: 'PartyReplyServerPacket.ReplyCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> PartyReplyCode:
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: PartyReplyCode) -> None:
        self._reply_code = reply_code

    @property
    def reply_code_data(self) -> 'PartyReplyServerPacket.ReplyCodeData':
        """
        PartyReplyServerPacket.ReplyCodeData: Gets or sets the data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @reply_code_data.setter
    def reply_code_data(self, reply_code_data: 'PartyReplyServerPacket.ReplyCodeData') -> None:
        self._reply_code_data = reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Party

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
        PartyReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyReplyServerPacket") -> None:
        """
        Serializes an instance of `PartyReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyReplyServerPacket): The data to serialize.
        """
        if data._reply_code is None:
            raise SerializationError("reply_code must be provided.")
        writer.add_char(int(data._reply_code))
        if data._reply_code == PartyReplyCode.AlreadyInAnotherParty:
            if not isinstance(data._reply_code_data, PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty):
                raise SerializationError("Expected reply_code_data to be type PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty for reply_code " + PartyReplyCode(data._reply_code).name + ".")
            PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty.serialize(writer, data._reply_code_data)
        elif data._reply_code == PartyReplyCode.AlreadyInYourParty:
            if not isinstance(data._reply_code_data, PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty):
                raise SerializationError("Expected reply_code_data to be type PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty for reply_code " + PartyReplyCode(data._reply_code).name + ".")
            PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty.serialize(writer, data._reply_code_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyReplyServerPacket":
        """
        Deserializes an instance of `PartyReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyReplyServerPacket: The data to serialize.
        """
        data: PartyReplyServerPacket = PartyReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = PartyReplyCode(reader.get_char())
            if data._reply_code == PartyReplyCode.AlreadyInAnotherParty:
                data._reply_code_data = PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty.deserialize(reader)
            elif data._reply_code == PartyReplyCode.AlreadyInYourParty:
                data._reply_code_data = PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty', 'PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty', None]
    ReplyCodeData.__doc__ = \
        """
        Data associated with different values of the `reply_code` field.
        """

    class ReplyCodeDataAlreadyInAnotherParty:
        """
        Data associated with reply_code value PartyReplyCode.AlreadyInAnotherParty
        """
        _byte_size: int = 0
        _player_name: str = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def player_name(self) -> str:
            return self._player_name

        @player_name.setter
        def player_name(self, player_name: str) -> None:
            self._player_name = player_name

        @staticmethod
        def serialize(writer: EoWriter, data: "PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty") -> None:
            """
            Serializes an instance of `PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty): The data to serialize.
            """
            if data._player_name is None:
                raise SerializationError("player_name must be provided.")
            writer.add_string(data._player_name)

        @staticmethod
        def deserialize(reader: EoReader) -> "PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty":
            """
            Deserializes an instance of `PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty: The data to serialize.
            """
            data: PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty = PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._player_name = reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"PartyReplyServerPacket.ReplyCodeDataAlreadyInAnotherParty(byte_size={repr(self._byte_size)}, player_name={repr(self._player_name)})"

    class ReplyCodeDataAlreadyInYourParty:
        """
        Data associated with reply_code value PartyReplyCode.AlreadyInYourParty
        """
        _byte_size: int = 0
        _player_name: str = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def player_name(self) -> str:
            return self._player_name

        @player_name.setter
        def player_name(self, player_name: str) -> None:
            self._player_name = player_name

        @staticmethod
        def serialize(writer: EoWriter, data: "PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty") -> None:
            """
            Serializes an instance of `PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty): The data to serialize.
            """
            if data._player_name is None:
                raise SerializationError("player_name must be provided.")
            writer.add_string(data._player_name)

        @staticmethod
        def deserialize(reader: EoReader) -> "PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty":
            """
            Deserializes an instance of `PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty: The data to serialize.
            """
            data: PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty = PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._player_name = reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"PartyReplyServerPacket.ReplyCodeDataAlreadyInYourParty(byte_size={repr(self._byte_size)}, player_name={repr(self._player_name)})"
