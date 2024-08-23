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

class PaperdollRemoveClientPacket(Packet):
    """
    Unequipping an item
    """
    _byte_size: int = 0
    _item_id: int = None # type: ignore [assignment]
    _sub_loc: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._item_id

    @item_id.setter
    def item_id(self, item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._item_id = item_id

    @property
    def sub_loc(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._sub_loc

    @sub_loc.setter
    def sub_loc(self, sub_loc: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._sub_loc = sub_loc

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
        return PacketAction.Remove

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PaperdollRemoveClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PaperdollRemoveClientPacket") -> None:
        """
        Serializes an instance of `PaperdollRemoveClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PaperdollRemoveClientPacket): The data to serialize.
        """
        if data._item_id is None:
            raise SerializationError("item_id must be provided.")
        writer.add_short(data._item_id)
        if data._sub_loc is None:
            raise SerializationError("sub_loc must be provided.")
        writer.add_char(data._sub_loc)

    @staticmethod
    def deserialize(reader: EoReader) -> "PaperdollRemoveClientPacket":
        """
        Deserializes an instance of `PaperdollRemoveClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PaperdollRemoveClientPacket: The data to serialize.
        """
        data: PaperdollRemoveClientPacket = PaperdollRemoveClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._item_id = reader.get_short()
            data._sub_loc = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PaperdollRemoveClientPacket(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, sub_loc={repr(self._sub_loc)})"
