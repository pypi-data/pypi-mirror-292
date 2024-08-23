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

class AccountRequestClientPacket(Packet):
    """
    Request creating an account
    """
    _byte_size: int = 0
    _username: str = None # type: ignore [assignment]

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
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AccountRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AccountRequestClientPacket") -> None:
        """
        Serializes an instance of `AccountRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AccountRequestClientPacket): The data to serialize.
        """
        if data._username is None:
            raise SerializationError("username must be provided.")
        writer.add_string(data._username)

    @staticmethod
    def deserialize(reader: EoReader) -> "AccountRequestClientPacket":
        """
        Deserializes an instance of `AccountRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AccountRequestClientPacket: The data to serialize.
        """
        data: AccountRequestClientPacket = AccountRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._username = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AccountRequestClientPacket(byte_size={repr(self._byte_size)}, username={repr(self._username)})"
