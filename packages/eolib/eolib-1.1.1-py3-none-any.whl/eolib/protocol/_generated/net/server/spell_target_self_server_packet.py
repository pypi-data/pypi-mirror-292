# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SpellTargetSelfServerPacket(Packet):
    """
    Nearby player self-casted a spell
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _spell_id: int = None # type: ignore [assignment]
    _spell_heal_hp: int = None # type: ignore [assignment]
    _hp_percentage: int = None # type: ignore [assignment]
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
    def player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._player_id

    @player_id.setter
    def player_id(self, player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._player_id = player_id

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
    def spell_heal_hp(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._spell_heal_hp

    @spell_heal_hp.setter
    def spell_heal_hp(self, spell_heal_hp: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._spell_heal_hp = spell_heal_hp

    @property
    def hp_percentage(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hp_percentage

    @hp_percentage.setter
    def hp_percentage(self, hp_percentage: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hp_percentage = hp_percentage

    @property
    def hp(self) -> Optional[int]:
        """
        The official client reads this if the packet is larger than 12 bytes

        Note:
          - Value range is 0-64008.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: Optional[int]) -> None:
        """
        The official client reads this if the packet is larger than 12 bytes

        Note:
          - Value range is 0-64008.
        """
        self._hp = hp

    @property
    def tp(self) -> Optional[int]:
        """
        The official client reads this if the packet is larger than 12 bytes

        Note:
          - Value range is 0-64008.
        """
        return self._tp

    @tp.setter
    def tp(self, tp: Optional[int]) -> None:
        """
        The official client reads this if the packet is larger than 12 bytes

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
        return PacketFamily.Spell

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.TargetSelf

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        SpellTargetSelfServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SpellTargetSelfServerPacket") -> None:
        """
        Serializes an instance of `SpellTargetSelfServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SpellTargetSelfServerPacket): The data to serialize.
        """
        if data._player_id is None:
            raise SerializationError("player_id must be provided.")
        writer.add_short(data._player_id)
        if data._spell_id is None:
            raise SerializationError("spell_id must be provided.")
        writer.add_short(data._spell_id)
        if data._spell_heal_hp is None:
            raise SerializationError("spell_heal_hp must be provided.")
        writer.add_int(data._spell_heal_hp)
        if data._hp_percentage is None:
            raise SerializationError("hp_percentage must be provided.")
        writer.add_char(data._hp_percentage)
        reached_missing_optional = data._hp is None
        if not reached_missing_optional:
            writer.add_short(cast(int, data._hp))
        reached_missing_optional = reached_missing_optional or data._tp is None
        if not reached_missing_optional:
            writer.add_short(cast(int, data._tp))

    @staticmethod
    def deserialize(reader: EoReader) -> "SpellTargetSelfServerPacket":
        """
        Deserializes an instance of `SpellTargetSelfServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SpellTargetSelfServerPacket: The data to serialize.
        """
        data: SpellTargetSelfServerPacket = SpellTargetSelfServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._spell_id = reader.get_short()
            data._spell_heal_hp = reader.get_int()
            data._hp_percentage = reader.get_char()
            if reader.remaining > 0:
                data._hp = reader.get_short()
            if reader.remaining > 0:
                data._tp = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SpellTargetSelfServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, spell_id={repr(self._spell_id)}, spell_heal_hp={repr(self._spell_heal_hp)}, hp_percentage={repr(self._hp_percentage)}, hp={repr(self._hp)}, tp={repr(self._tp)})"
