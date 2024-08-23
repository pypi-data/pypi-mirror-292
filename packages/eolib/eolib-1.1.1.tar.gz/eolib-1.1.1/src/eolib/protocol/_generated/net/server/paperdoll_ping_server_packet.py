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

class PaperdollPingServerPacket(Packet):
    """
    Failed to equip an item due to being the incorrect class
    """
    _byte_size: int = 0
    _class_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def class_id(self) -> int:
        """
        The player&#x27;s current class ID (not the item&#x27;s required class ID)

        Note:
          - Value range is 0-252.
        """
        return self._class_id

    @class_id.setter
    def class_id(self, class_id: int) -> None:
        """
        The player&#x27;s current class ID (not the item&#x27;s required class ID)

        Note:
          - Value range is 0-252.
        """
        self._class_id = class_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Paperdoll

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Ping

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PaperdollPingServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PaperdollPingServerPacket") -> None:
        """
        Serializes an instance of `PaperdollPingServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PaperdollPingServerPacket): The data to serialize.
        """
        if data._class_id is None:
            raise SerializationError("class_id must be provided.")
        writer.add_char(data._class_id)

    @staticmethod
    def deserialize(reader: EoReader) -> "PaperdollPingServerPacket":
        """
        Deserializes an instance of `PaperdollPingServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PaperdollPingServerPacket: The data to serialize.
        """
        data: PaperdollPingServerPacket = PaperdollPingServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._class_id = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PaperdollPingServerPacket(byte_size={repr(self._byte_size)}, class_id={repr(self._class_id)})"
