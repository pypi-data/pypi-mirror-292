# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .guild_reply import GuildReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildReplyServerPacket(Packet):
    """
    Generic guild reply messages
    """
    _byte_size: int = 0
    _reply_code: GuildReply = None # type: ignore [assignment]
    _reply_code_data: 'GuildReplyServerPacket.ReplyCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> GuildReply:
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: GuildReply) -> None:
        self._reply_code = reply_code

    @property
    def reply_code_data(self) -> 'GuildReplyServerPacket.ReplyCodeData':
        """
        GuildReplyServerPacket.ReplyCodeData: Gets or sets the data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @reply_code_data.setter
    def reply_code_data(self, reply_code_data: 'GuildReplyServerPacket.ReplyCodeData') -> None:
        self._reply_code_data = reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

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
        GuildReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildReplyServerPacket") -> None:
        """
        Serializes an instance of `GuildReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildReplyServerPacket): The data to serialize.
        """
        if data._reply_code is None:
            raise SerializationError("reply_code must be provided.")
        writer.add_short(int(data._reply_code))
        if data._reply_code == GuildReply.CreateAdd:
            if not isinstance(data._reply_code_data, GuildReplyServerPacket.ReplyCodeDataCreateAdd):
                raise SerializationError("Expected reply_code_data to be type GuildReplyServerPacket.ReplyCodeDataCreateAdd for reply_code " + GuildReply(data._reply_code).name + ".")
            GuildReplyServerPacket.ReplyCodeDataCreateAdd.serialize(writer, data._reply_code_data)
        elif data._reply_code == GuildReply.CreateAddConfirm:
            if not isinstance(data._reply_code_data, GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm):
                raise SerializationError("Expected reply_code_data to be type GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm for reply_code " + GuildReply(data._reply_code).name + ".")
            GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm.serialize(writer, data._reply_code_data)
        elif data._reply_code == GuildReply.JoinRequest:
            if not isinstance(data._reply_code_data, GuildReplyServerPacket.ReplyCodeDataJoinRequest):
                raise SerializationError("Expected reply_code_data to be type GuildReplyServerPacket.ReplyCodeDataJoinRequest for reply_code " + GuildReply(data._reply_code).name + ".")
            GuildReplyServerPacket.ReplyCodeDataJoinRequest.serialize(writer, data._reply_code_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildReplyServerPacket":
        """
        Deserializes an instance of `GuildReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildReplyServerPacket: The data to serialize.
        """
        data: GuildReplyServerPacket = GuildReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = GuildReply(reader.get_short())
            if data._reply_code == GuildReply.CreateAdd:
                data._reply_code_data = GuildReplyServerPacket.ReplyCodeDataCreateAdd.deserialize(reader)
            elif data._reply_code == GuildReply.CreateAddConfirm:
                data._reply_code_data = GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm.deserialize(reader)
            elif data._reply_code == GuildReply.JoinRequest:
                data._reply_code_data = GuildReplyServerPacket.ReplyCodeDataJoinRequest.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['GuildReplyServerPacket.ReplyCodeDataCreateAdd', 'GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm', 'GuildReplyServerPacket.ReplyCodeDataJoinRequest', None]
    ReplyCodeData.__doc__ = \
        """
        Data associated with different values of the `reply_code` field.
        """

    class ReplyCodeDataCreateAdd:
        """
        Data associated with reply_code value GuildReply.CreateAdd
        """
        _byte_size: int = 0
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
        def name(self) -> str:
            return self._name

        @name.setter
        def name(self, name: str) -> None:
            self._name = name

        @staticmethod
        def serialize(writer: EoWriter, data: "GuildReplyServerPacket.ReplyCodeDataCreateAdd") -> None:
            """
            Serializes an instance of `GuildReplyServerPacket.ReplyCodeDataCreateAdd` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (GuildReplyServerPacket.ReplyCodeDataCreateAdd): The data to serialize.
            """
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)

        @staticmethod
        def deserialize(reader: EoReader) -> "GuildReplyServerPacket.ReplyCodeDataCreateAdd":
            """
            Deserializes an instance of `GuildReplyServerPacket.ReplyCodeDataCreateAdd` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                GuildReplyServerPacket.ReplyCodeDataCreateAdd: The data to serialize.
            """
            data: GuildReplyServerPacket.ReplyCodeDataCreateAdd = GuildReplyServerPacket.ReplyCodeDataCreateAdd()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._name = reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"GuildReplyServerPacket.ReplyCodeDataCreateAdd(byte_size={repr(self._byte_size)}, name={repr(self._name)})"

    class ReplyCodeDataCreateAddConfirm:
        """
        Data associated with reply_code value GuildReply.CreateAddConfirm
        """
        _byte_size: int = 0
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
        def name(self) -> str:
            return self._name

        @name.setter
        def name(self, name: str) -> None:
            self._name = name

        @staticmethod
        def serialize(writer: EoWriter, data: "GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm") -> None:
            """
            Serializes an instance of `GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm): The data to serialize.
            """
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)

        @staticmethod
        def deserialize(reader: EoReader) -> "GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm":
            """
            Deserializes an instance of `GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm: The data to serialize.
            """
            data: GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm = GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._name = reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"GuildReplyServerPacket.ReplyCodeDataCreateAddConfirm(byte_size={repr(self._byte_size)}, name={repr(self._name)})"

    class ReplyCodeDataJoinRequest:
        """
        Data associated with reply_code value GuildReply.JoinRequest
        """
        _byte_size: int = 0
        _player_id: int = None # type: ignore [assignment]
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
        def name(self) -> str:
            return self._name

        @name.setter
        def name(self, name: str) -> None:
            self._name = name

        @staticmethod
        def serialize(writer: EoWriter, data: "GuildReplyServerPacket.ReplyCodeDataJoinRequest") -> None:
            """
            Serializes an instance of `GuildReplyServerPacket.ReplyCodeDataJoinRequest` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (GuildReplyServerPacket.ReplyCodeDataJoinRequest): The data to serialize.
            """
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)

        @staticmethod
        def deserialize(reader: EoReader) -> "GuildReplyServerPacket.ReplyCodeDataJoinRequest":
            """
            Deserializes an instance of `GuildReplyServerPacket.ReplyCodeDataJoinRequest` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                GuildReplyServerPacket.ReplyCodeDataJoinRequest: The data to serialize.
            """
            data: GuildReplyServerPacket.ReplyCodeDataJoinRequest = GuildReplyServerPacket.ReplyCodeDataJoinRequest()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._player_id = reader.get_short()
                data._name = reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"GuildReplyServerPacket.ReplyCodeDataJoinRequest(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, name={repr(self._name)})"
