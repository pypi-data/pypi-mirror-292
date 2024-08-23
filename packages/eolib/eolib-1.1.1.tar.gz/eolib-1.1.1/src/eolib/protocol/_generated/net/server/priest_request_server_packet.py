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

class PriestRequestServerPacket(Packet):
    """
    Wedding request
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _partner_name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._session_id = session_id

    @property
    def partner_name(self) -> str:
        return self._partner_name

    @partner_name.setter
    def partner_name(self, partner_name: str) -> None:
        self._partner_name = partner_name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Priest

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
        PriestRequestServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PriestRequestServerPacket") -> None:
        """
        Serializes an instance of `PriestRequestServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PriestRequestServerPacket): The data to serialize.
        """
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_short(data._session_id)
        if data._partner_name is None:
            raise SerializationError("partner_name must be provided.")
        writer.add_string(data._partner_name)

    @staticmethod
    def deserialize(reader: EoReader) -> "PriestRequestServerPacket":
        """
        Deserializes an instance of `PriestRequestServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PriestRequestServerPacket: The data to serialize.
        """
        data: PriestRequestServerPacket = PriestRequestServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._session_id = reader.get_short()
            data._partner_name = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PriestRequestServerPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, partner_name={repr(self._partner_name)})"
