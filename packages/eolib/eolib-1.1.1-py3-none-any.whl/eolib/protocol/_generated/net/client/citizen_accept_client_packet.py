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

class CitizenAcceptClientPacket(Packet):
    """
    Confirm sleeping at an inn
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _behavior_id: int = None # type: ignore [assignment]

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
    def behavior_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, behavior_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._behavior_id = behavior_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Citizen

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CitizenAcceptClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenAcceptClientPacket") -> None:
        """
        Serializes an instance of `CitizenAcceptClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenAcceptClientPacket): The data to serialize.
        """
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_short(data._session_id)
        if data._behavior_id is None:
            raise SerializationError("behavior_id must be provided.")
        writer.add_short(data._behavior_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenAcceptClientPacket":
        """
        Deserializes an instance of `CitizenAcceptClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenAcceptClientPacket: The data to serialize.
        """
        data: CitizenAcceptClientPacket = CitizenAcceptClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._session_id = reader.get_short()
            data._behavior_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenAcceptClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, behavior_id={repr(self._behavior_id)})"
