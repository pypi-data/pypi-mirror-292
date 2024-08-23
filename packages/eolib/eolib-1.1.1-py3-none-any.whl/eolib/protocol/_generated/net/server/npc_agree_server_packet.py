# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .npc_map_info import NpcMapInfo
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcAgreeServerPacket(Packet):
    """
    Reply to request for information about nearby NPCs
    """
    _byte_size: int = 0
    _npcs_count: int = None # type: ignore [assignment]
    _npcs: list[NpcMapInfo] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npcs(self) -> list[NpcMapInfo]:
        """
        Note:
          - Length must be 64008 or less.
        """
        return self._npcs

    @npcs.setter
    def npcs(self, npcs: list[NpcMapInfo]) -> None:
        """
        Note:
          - Length must be 64008 or less.
        """
        self._npcs = npcs
        self._npcs_count = len(self._npcs)

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
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcAgreeServerPacket") -> None:
        """
        Serializes an instance of `NpcAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcAgreeServerPacket): The data to serialize.
        """
        if data._npcs_count is None:
            raise SerializationError("npcs_count must be provided.")
        writer.add_short(data._npcs_count)
        if data._npcs is None:
            raise SerializationError("npcs must be provided.")
        if len(data._npcs) > 64008:
            raise SerializationError(f"Expected length of npcs to be 64008 or less, got {len(data._npcs)}.")
        for i in range(data._npcs_count):
            NpcMapInfo.serialize(writer, data._npcs[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcAgreeServerPacket":
        """
        Deserializes an instance of `NpcAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcAgreeServerPacket: The data to serialize.
        """
        data: NpcAgreeServerPacket = NpcAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._npcs_count = reader.get_short()
            data._npcs = []
            for i in range(data._npcs_count):
                data._npcs.append(NpcMapInfo.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcAgreeServerPacket(byte_size={repr(self._byte_size)}, npcs={repr(self._npcs)})"
