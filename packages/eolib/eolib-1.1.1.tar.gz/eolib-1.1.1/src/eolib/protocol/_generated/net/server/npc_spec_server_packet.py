# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from .npc_killed_data import NpcKilledData
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcSpecServerPacket(Packet):
    """
    Nearby NPC killed by player
    """
    _byte_size: int = 0
    _npc_killed_data: NpcKilledData = None # type: ignore [assignment]
    _experience: Optional[int] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_killed_data(self) -> NpcKilledData:
        return self._npc_killed_data

    @npc_killed_data.setter
    def npc_killed_data(self, npc_killed_data: NpcKilledData) -> None:
        self._npc_killed_data = npc_killed_data

    @property
    def experience(self) -> Optional[int]:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._experience

    @experience.setter
    def experience(self, experience: Optional[int]) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._experience = experience

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
        return PacketAction.Spec

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcSpecServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcSpecServerPacket") -> None:
        """
        Serializes an instance of `NpcSpecServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcSpecServerPacket): The data to serialize.
        """
        if data._npc_killed_data is None:
            raise SerializationError("npc_killed_data must be provided.")
        NpcKilledData.serialize(writer, data._npc_killed_data)
        reached_missing_optional = data._experience is None
        if not reached_missing_optional:
            writer.add_int(cast(int, data._experience))

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcSpecServerPacket":
        """
        Deserializes an instance of `NpcSpecServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcSpecServerPacket: The data to serialize.
        """
        data: NpcSpecServerPacket = NpcSpecServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._npc_killed_data = NpcKilledData.deserialize(reader)
            if reader.remaining > 0:
                data._experience = reader.get_int()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcSpecServerPacket(byte_size={repr(self._byte_size)}, npc_killed_data={repr(self._npc_killed_data)}, experience={repr(self._experience)})"
