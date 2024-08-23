# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .marriage_request_type import MarriageRequestType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MarriageRequestClientPacket(Packet):
    """
    Requesting marriage approval
    """
    _byte_size: int = 0
    _request_type: MarriageRequestType = None # type: ignore [assignment]
    _session_id: int = None # type: ignore [assignment]
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
    def request_type(self) -> MarriageRequestType:
        return self._request_type

    @request_type.setter
    def request_type(self, request_type: MarriageRequestType) -> None:
        self._request_type = request_type

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._session_id = session_id

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
        return PacketFamily.Marriage

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
        MarriageRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "MarriageRequestClientPacket") -> None:
        """
        Serializes an instance of `MarriageRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MarriageRequestClientPacket): The data to serialize.
        """
        if data._request_type is None:
            raise SerializationError("request_type must be provided.")
        writer.add_char(int(data._request_type))
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_int(data._session_id)
        writer.add_byte(0xFF)
        if data._name is None:
            raise SerializationError("name must be provided.")
        writer.add_string(data._name)

    @staticmethod
    def deserialize(reader: EoReader) -> "MarriageRequestClientPacket":
        """
        Deserializes an instance of `MarriageRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MarriageRequestClientPacket: The data to serialize.
        """
        data: MarriageRequestClientPacket = MarriageRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._request_type = MarriageRequestType(reader.get_char())
            data._session_id = reader.get_int()
            reader.next_chunk()
            data._name = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MarriageRequestClientPacket(byte_size={repr(self._byte_size)}, request_type={repr(self._request_type)}, session_id={repr(self._session_id)}, name={repr(self._name)})"
