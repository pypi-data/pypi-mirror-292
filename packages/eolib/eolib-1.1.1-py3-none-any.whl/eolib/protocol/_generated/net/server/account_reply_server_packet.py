# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .account_reply import AccountReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AccountReplyServerPacket(Packet):
    """
    Reply to client Account-family packets
    """
    _byte_size: int = 0
    _reply_code: AccountReply = None # type: ignore [assignment]
    _reply_code_data: 'AccountReplyServerPacket.ReplyCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> AccountReply:
        """
        Sometimes an AccountReply code, sometimes a session ID for account creation
        """
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: AccountReply) -> None:
        """
        Sometimes an AccountReply code, sometimes a session ID for account creation
        """
        self._reply_code = reply_code

    @property
    def reply_code_data(self) -> 'AccountReplyServerPacket.ReplyCodeData':
        """
        AccountReplyServerPacket.ReplyCodeData: Gets or sets the data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @reply_code_data.setter
    def reply_code_data(self, reply_code_data: 'AccountReplyServerPacket.ReplyCodeData') -> None:
        self._reply_code_data = reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Account

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
        AccountReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AccountReplyServerPacket") -> None:
        """
        Serializes an instance of `AccountReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AccountReplyServerPacket): The data to serialize.
        """
        if data._reply_code is None:
            raise SerializationError("reply_code must be provided.")
        writer.add_short(int(data._reply_code))
        if data._reply_code == 0:
            if data._reply_code_data is not None:
                raise SerializationError("Expected reply_code_data to be None for reply_code " + AccountReply(data._reply_code).name + ".")
        elif data._reply_code == AccountReply.Exists:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataExists):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataExists for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataExists.serialize(writer, data._reply_code_data)
        elif data._reply_code == AccountReply.NotApproved:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataNotApproved):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataNotApproved for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataNotApproved.serialize(writer, data._reply_code_data)
        elif data._reply_code == AccountReply.Created:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataCreated):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataCreated for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataCreated.serialize(writer, data._reply_code_data)
        elif data._reply_code == 4:
            if data._reply_code_data is not None:
                raise SerializationError("Expected reply_code_data to be None for reply_code " + AccountReply(data._reply_code).name + ".")
        elif data._reply_code == AccountReply.ChangeFailed:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataChangeFailed):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataChangeFailed for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataChangeFailed.serialize(writer, data._reply_code_data)
        elif data._reply_code == AccountReply.Changed:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataChanged):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataChanged for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataChanged.serialize(writer, data._reply_code_data)
        elif data._reply_code == AccountReply.RequestDenied:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataRequestDenied):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataRequestDenied for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataRequestDenied.serialize(writer, data._reply_code_data)
        elif data._reply_code == 8:
            if data._reply_code_data is not None:
                raise SerializationError("Expected reply_code_data to be None for reply_code " + AccountReply(data._reply_code).name + ".")
        elif data._reply_code == 9:
            if data._reply_code_data is not None:
                raise SerializationError("Expected reply_code_data to be None for reply_code " + AccountReply(data._reply_code).name + ".")
        else:
            if not isinstance(data._reply_code_data, AccountReplyServerPacket.ReplyCodeDataDefault):
                raise SerializationError("Expected reply_code_data to be type AccountReplyServerPacket.ReplyCodeDataDefault for reply_code " + AccountReply(data._reply_code).name + ".")
            AccountReplyServerPacket.ReplyCodeDataDefault.serialize(writer, data._reply_code_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "AccountReplyServerPacket":
        """
        Deserializes an instance of `AccountReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AccountReplyServerPacket: The data to serialize.
        """
        data: AccountReplyServerPacket = AccountReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = AccountReply(reader.get_short())
            if data._reply_code == 0:
                data._reply_code_data = None
            elif data._reply_code == AccountReply.Exists:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataExists.deserialize(reader)
            elif data._reply_code == AccountReply.NotApproved:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataNotApproved.deserialize(reader)
            elif data._reply_code == AccountReply.Created:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataCreated.deserialize(reader)
            elif data._reply_code == 4:
                data._reply_code_data = None
            elif data._reply_code == AccountReply.ChangeFailed:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataChangeFailed.deserialize(reader)
            elif data._reply_code == AccountReply.Changed:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataChanged.deserialize(reader)
            elif data._reply_code == AccountReply.RequestDenied:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataRequestDenied.deserialize(reader)
            elif data._reply_code == 8:
                data._reply_code_data = None
            elif data._reply_code == 9:
                data._reply_code_data = None
            else:
                data._reply_code_data = AccountReplyServerPacket.ReplyCodeDataDefault.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AccountReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['AccountReplyServerPacket.ReplyCodeDataExists', 'AccountReplyServerPacket.ReplyCodeDataNotApproved', 'AccountReplyServerPacket.ReplyCodeDataCreated', 'AccountReplyServerPacket.ReplyCodeDataChangeFailed', 'AccountReplyServerPacket.ReplyCodeDataChanged', 'AccountReplyServerPacket.ReplyCodeDataRequestDenied', 'AccountReplyServerPacket.ReplyCodeDataDefault', None]
    ReplyCodeData.__doc__ = \
        """
        Data associated with different values of the `reply_code` field.
        """

    class ReplyCodeDataExists:
        """
        Data associated with reply_code value AccountReply.Exists
        """
        _byte_size: int = 0

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataExists") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataExists` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataExists): The data to serialize.
            """
            writer.add_string("NO")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataExists":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataExists` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataExists: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataExists = AccountReplyServerPacket.ReplyCodeDataExists()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataExists(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataNotApproved:
        """
        Data associated with reply_code value AccountReply.NotApproved
        """
        _byte_size: int = 0

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataNotApproved") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataNotApproved` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataNotApproved): The data to serialize.
            """
            writer.add_string("NO")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataNotApproved":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataNotApproved` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataNotApproved: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataNotApproved = AccountReplyServerPacket.ReplyCodeDataNotApproved()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataNotApproved(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataCreated:
        """
        Data associated with reply_code value AccountReply.Created
        """
        _byte_size: int = 0

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataCreated") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataCreated` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataCreated): The data to serialize.
            """
            writer.add_string("GO")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataCreated":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataCreated` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataCreated: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataCreated = AccountReplyServerPacket.ReplyCodeDataCreated()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataCreated(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataChangeFailed:
        """
        Data associated with reply_code value AccountReply.ChangeFailed
        """
        _byte_size: int = 0

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataChangeFailed") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataChangeFailed` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataChangeFailed): The data to serialize.
            """
            writer.add_string("NO")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataChangeFailed":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataChangeFailed` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataChangeFailed: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataChangeFailed = AccountReplyServerPacket.ReplyCodeDataChangeFailed()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataChangeFailed(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataChanged:
        """
        Data associated with reply_code value AccountReply.Changed
        """
        _byte_size: int = 0

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataChanged") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataChanged` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataChanged): The data to serialize.
            """
            writer.add_string("NO")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataChanged":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataChanged` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataChanged: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataChanged = AccountReplyServerPacket.ReplyCodeDataChanged()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataChanged(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataRequestDenied:
        """
        Data associated with reply_code value AccountReply.RequestDenied
        """
        _byte_size: int = 0

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size


        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataRequestDenied") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataRequestDenied` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataRequestDenied): The data to serialize.
            """
            writer.add_string("NO")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataRequestDenied":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataRequestDenied` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataRequestDenied: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataRequestDenied = AccountReplyServerPacket.ReplyCodeDataRequestDenied()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataRequestDenied(byte_size={repr(self._byte_size)})"

    class ReplyCodeDataDefault:
        """
        Default data associated with reply_code

        In this case (reply_code &gt; 9), reply_code is a session ID for account creation
        """
        _byte_size: int = 0
        _sequence_start: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def sequence_start(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._sequence_start

        @sequence_start.setter
        def sequence_start(self, sequence_start: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._sequence_start = sequence_start

        @staticmethod
        def serialize(writer: EoWriter, data: "AccountReplyServerPacket.ReplyCodeDataDefault") -> None:
            """
            Serializes an instance of `AccountReplyServerPacket.ReplyCodeDataDefault` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AccountReplyServerPacket.ReplyCodeDataDefault): The data to serialize.
            """
            if data._sequence_start is None:
                raise SerializationError("sequence_start must be provided.")
            writer.add_char(data._sequence_start)
            writer.add_string("OK")

        @staticmethod
        def deserialize(reader: EoReader) -> "AccountReplyServerPacket.ReplyCodeDataDefault":
            """
            Deserializes an instance of `AccountReplyServerPacket.ReplyCodeDataDefault` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AccountReplyServerPacket.ReplyCodeDataDefault: The data to serialize.
            """
            data: AccountReplyServerPacket.ReplyCodeDataDefault = AccountReplyServerPacket.ReplyCodeDataDefault()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._sequence_start = reader.get_char()
                reader.get_string()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AccountReplyServerPacket.ReplyCodeDataDefault(byte_size={repr(self._byte_size)}, sequence_start={repr(self._sequence_start)})"
