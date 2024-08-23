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

class LoginRequestClientPacket(Packet):
    """
    Login request
    """
    _byte_size: int = 0
    _username: str = None # type: ignore [assignment]
    _password: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str) -> None:
        self._password = password

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Login

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
        LoginRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LoginRequestClientPacket") -> None:
        """
        Serializes an instance of `LoginRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LoginRequestClientPacket): The data to serialize.
        """
        if data._username is None:
            raise SerializationError("username must be provided.")
        writer.add_string(data._username)
        writer.add_byte(0xFF)
        if data._password is None:
            raise SerializationError("password must be provided.")
        writer.add_string(data._password)
        writer.add_byte(0xFF)

    @staticmethod
    def deserialize(reader: EoReader) -> "LoginRequestClientPacket":
        """
        Deserializes an instance of `LoginRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LoginRequestClientPacket: The data to serialize.
        """
        data: LoginRequestClientPacket = LoginRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._username = reader.get_string()
            reader.next_chunk()
            data._password = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LoginRequestClientPacket(byte_size={repr(self._byte_size)}, username={repr(self._username)}, password={repr(self._password)})"
