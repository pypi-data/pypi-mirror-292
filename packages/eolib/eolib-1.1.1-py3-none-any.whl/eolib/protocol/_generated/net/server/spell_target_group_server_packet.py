# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .group_heal_target_player import GroupHealTargetPlayer
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SpellTargetGroupServerPacket(Packet):
    """
    Nearby player(s) hit by a group heal spell from a player
    """
    _byte_size: int = 0
    _spell_id: int = None # type: ignore [assignment]
    _caster_id: int = None # type: ignore [assignment]
    _caster_tp: int = None # type: ignore [assignment]
    _spell_heal_hp: int = None # type: ignore [assignment]
    _players: list[GroupHealTargetPlayer] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def spell_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._spell_id

    @spell_id.setter
    def spell_id(self, spell_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._spell_id = spell_id

    @property
    def caster_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._caster_id

    @caster_id.setter
    def caster_id(self, caster_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._caster_id = caster_id

    @property
    def caster_tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._caster_tp

    @caster_tp.setter
    def caster_tp(self, caster_tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._caster_tp = caster_tp

    @property
    def spell_heal_hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._spell_heal_hp

    @spell_heal_hp.setter
    def spell_heal_hp(self, spell_heal_hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._spell_heal_hp = spell_heal_hp

    @property
    def players(self) -> list[GroupHealTargetPlayer]:
        return self._players

    @players.setter
    def players(self, players: list[GroupHealTargetPlayer]) -> None:
        self._players = players

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Spell

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.TargetGroup

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        SpellTargetGroupServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SpellTargetGroupServerPacket") -> None:
        """
        Serializes an instance of `SpellTargetGroupServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SpellTargetGroupServerPacket): The data to serialize.
        """
        if data._spell_id is None:
            raise SerializationError("spell_id must be provided.")
        writer.add_short(data._spell_id)
        if data._caster_id is None:
            raise SerializationError("caster_id must be provided.")
        writer.add_short(data._caster_id)
        if data._caster_tp is None:
            raise SerializationError("caster_tp must be provided.")
        writer.add_short(data._caster_tp)
        if data._spell_heal_hp is None:
            raise SerializationError("spell_heal_hp must be provided.")
        writer.add_short(data._spell_heal_hp)
        if data._players is None:
            raise SerializationError("players must be provided.")
        for i in range(len(data._players)):
            GroupHealTargetPlayer.serialize(writer, data._players[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "SpellTargetGroupServerPacket":
        """
        Deserializes an instance of `SpellTargetGroupServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SpellTargetGroupServerPacket: The data to serialize.
        """
        data: SpellTargetGroupServerPacket = SpellTargetGroupServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._spell_id = reader.get_short()
            data._caster_id = reader.get_short()
            data._caster_tp = reader.get_short()
            data._spell_heal_hp = reader.get_short()
            players_length = int(reader.remaining / 5)
            data._players = []
            for i in range(players_length):
                data._players.append(GroupHealTargetPlayer.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SpellTargetGroupServerPacket(byte_size={repr(self._byte_size)}, spell_id={repr(self._spell_id)}, caster_id={repr(self._caster_id)}, caster_tp={repr(self._caster_tp)}, spell_heal_hp={repr(self._spell_heal_hp)}, players={repr(self._players)})"
