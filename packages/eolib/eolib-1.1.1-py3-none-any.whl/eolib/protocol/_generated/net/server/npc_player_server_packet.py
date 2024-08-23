# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import cast
from typing import Optional
from .npc_update_position import NpcUpdatePosition
from .npc_update_chat import NpcUpdateChat
from .npc_update_attack import NpcUpdateAttack
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcPlayerServerPacket(Packet):
    """
    Main NPC update message
    """
    _byte_size: int = 0
    _positions: list[NpcUpdatePosition] = None # type: ignore [assignment]
    _attacks: list[NpcUpdateAttack] = None # type: ignore [assignment]
    _chats: list[NpcUpdateChat] = None # type: ignore [assignment]
    _hp: Optional[int] = None # type: ignore [assignment]
    _tp: Optional[int] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def positions(self) -> list[NpcUpdatePosition]:
        return self._positions

    @positions.setter
    def positions(self, positions: list[NpcUpdatePosition]) -> None:
        self._positions = positions

    @property
    def attacks(self) -> list[NpcUpdateAttack]:
        return self._attacks

    @attacks.setter
    def attacks(self, attacks: list[NpcUpdateAttack]) -> None:
        self._attacks = attacks

    @property
    def chats(self) -> list[NpcUpdateChat]:
        return self._chats

    @chats.setter
    def chats(self, chats: list[NpcUpdateChat]) -> None:
        self._chats = chats

    @property
    def hp(self) -> Optional[int]:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: Optional[int]) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hp = hp

    @property
    def tp(self) -> Optional[int]:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._tp

    @tp.setter
    def tp(self, tp: Optional[int]) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._tp = tp

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
        return PacketAction.Player

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcPlayerServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcPlayerServerPacket") -> None:
        """
        Serializes an instance of `NpcPlayerServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcPlayerServerPacket): The data to serialize.
        """
        if data._positions is None:
            raise SerializationError("positions must be provided.")
        for i in range(len(data._positions)):
            NpcUpdatePosition.serialize(writer, data._positions[i])
        writer.add_byte(0xFF)
        if data._attacks is None:
            raise SerializationError("attacks must be provided.")
        for i in range(len(data._attacks)):
            NpcUpdateAttack.serialize(writer, data._attacks[i])
        writer.add_byte(0xFF)
        if data._chats is None:
            raise SerializationError("chats must be provided.")
        for i in range(len(data._chats)):
            NpcUpdateChat.serialize(writer, data._chats[i])
        writer.add_byte(0xFF)
        reached_missing_optional = data._hp is None
        if not reached_missing_optional:
            writer.add_short(cast(int, data._hp))
        reached_missing_optional = reached_missing_optional or data._tp is None
        if not reached_missing_optional:
            writer.add_short(cast(int, data._tp))

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcPlayerServerPacket":
        """
        Deserializes an instance of `NpcPlayerServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcPlayerServerPacket: The data to serialize.
        """
        data: NpcPlayerServerPacket = NpcPlayerServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            positions_length = int(reader.remaining / 4)
            data._positions = []
            for i in range(positions_length):
                data._positions.append(NpcUpdatePosition.deserialize(reader))
            reader.next_chunk()
            attacks_length = int(reader.remaining / 9)
            data._attacks = []
            for i in range(attacks_length):
                data._attacks.append(NpcUpdateAttack.deserialize(reader))
            reader.next_chunk()
            data._chats = []
            while reader.remaining > 0:
                data._chats.append(NpcUpdateChat.deserialize(reader))
            reader.next_chunk()
            if reader.remaining > 0:
                data._hp = reader.get_short()
            if reader.remaining > 0:
                data._tp = reader.get_short()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcPlayerServerPacket(byte_size={repr(self._byte_size)}, positions={repr(self._positions)}, attacks={repr(self._attacks)}, chats={repr(self._chats)}, hp={repr(self._hp)}, tp={repr(self._tp)})"
