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

class WarpTakeClientPacket(Packet):
    """
    Request to download a copy of the map
    """
    _byte_size: int = 0
    _map_id: int = None # type: ignore [assignment]
    _session_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def map_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._map_id

    @map_id.setter
    def map_id(self, map_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._map_id = map_id

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

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Warp

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Take

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WarpTakeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WarpTakeClientPacket") -> None:
        """
        Serializes an instance of `WarpTakeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WarpTakeClientPacket): The data to serialize.
        """
        if data._map_id is None:
            raise SerializationError("map_id must be provided.")
        writer.add_short(data._map_id)
        if data._session_id is None:
            raise SerializationError("session_id must be provided.")
        writer.add_short(data._session_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "WarpTakeClientPacket":
        """
        Deserializes an instance of `WarpTakeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WarpTakeClientPacket: The data to serialize.
        """
        data: WarpTakeClientPacket = WarpTakeClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._map_id = reader.get_short()
            data._session_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WarpTakeClientPacket(byte_size={repr(self._byte_size)}, map_id={repr(self._map_id)}, session_id={repr(self._session_id)})"
