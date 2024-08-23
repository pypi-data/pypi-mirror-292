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

class NpcDialogServerPacket(Packet):
    """
    NPC chat message
    """
    _byte_size: int = 0
    _npc_index: int = None # type: ignore [assignment]
    _message: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_index(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._npc_index

    @npc_index.setter
    def npc_index(self, npc_index: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._npc_index = npc_index

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = message

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Npc

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Dialog

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcDialogServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcDialogServerPacket") -> None:
        """
        Serializes an instance of `NpcDialogServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcDialogServerPacket): The data to serialize.
        """
        if data._npc_index is None:
            raise SerializationError("npc_index must be provided.")
        writer.add_short(data._npc_index)
        if data._message is None:
            raise SerializationError("message must be provided.")
        writer.add_string(data._message)

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcDialogServerPacket":
        """
        Deserializes an instance of `NpcDialogServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcDialogServerPacket: The data to serialize.
        """
        data: NpcDialogServerPacket = NpcDialogServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._npc_index = reader.get_short()
            data._message = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcDialogServerPacket(byte_size={repr(self._byte_size)}, npc_index={repr(self._npc_index)}, message={repr(self._message)})"
