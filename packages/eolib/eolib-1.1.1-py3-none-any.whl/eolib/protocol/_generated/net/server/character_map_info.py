# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from .warp_effect import WarpEffect
from .sit_state import SitState
from .equipment_map_info import EquipmentMapInfo
from .big_coords import BigCoords
from ...gender import Gender
from ...direction import Direction
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterMapInfo:
    """
    Information about a nearby character.
    The official client skips these if they&#x27;re under 42 bytes in length.
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _player_id: int = None # type: ignore [assignment]
    _map_id: int = None # type: ignore [assignment]
    _coords: BigCoords = None # type: ignore [assignment]
    _direction: Direction = None # type: ignore [assignment]
    _class_id: int = None # type: ignore [assignment]
    _guild_tag: str = None # type: ignore [assignment]
    _level: int = None # type: ignore [assignment]
    _gender: Gender = None # type: ignore [assignment]
    _hair_style: int = None # type: ignore [assignment]
    _hair_color: int = None # type: ignore [assignment]
    _skin: int = None # type: ignore [assignment]
    _max_hp: int = None # type: ignore [assignment]
    _hp: int = None # type: ignore [assignment]
    _max_tp: int = None # type: ignore [assignment]
    _tp: int = None # type: ignore [assignment]
    _equipment: EquipmentMapInfo = None # type: ignore [assignment]
    _sit_state: SitState = None # type: ignore [assignment]
    _invisible: bool = None # type: ignore [assignment]
    _warp_effect: Optional[WarpEffect] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

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
    def coords(self) -> BigCoords:
        return self._coords

    @coords.setter
    def coords(self, coords: BigCoords) -> None:
        self._coords = coords

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

    @property
    def class_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._class_id

    @class_id.setter
    def class_id(self, class_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._class_id = class_id

    @property
    def guild_tag(self) -> str:
        """
        Note:
          - Length must be `3`.
        """
        return self._guild_tag

    @guild_tag.setter
    def guild_tag(self, guild_tag: str) -> None:
        """
        Note:
          - Length must be `3`.
        """
        self._guild_tag = guild_tag

    @property
    def level(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._level = level

    @property
    def gender(self) -> Gender:
        return self._gender

    @gender.setter
    def gender(self, gender: Gender) -> None:
        self._gender = gender

    @property
    def hair_style(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hair_style

    @hair_style.setter
    def hair_style(self, hair_style: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hair_style = hair_style

    @property
    def hair_color(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hair_color

    @hair_color.setter
    def hair_color(self, hair_color: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hair_color = hair_color

    @property
    def skin(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._skin

    @skin.setter
    def skin(self, skin: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._skin = skin

    @property
    def max_hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_hp

    @max_hp.setter
    def max_hp(self, max_hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_hp = max_hp

    @property
    def hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hp = hp

    @property
    def max_tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_tp

    @max_tp.setter
    def max_tp(self, max_tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_tp = max_tp

    @property
    def tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._tp

    @tp.setter
    def tp(self, tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._tp = tp

    @property
    def equipment(self) -> EquipmentMapInfo:
        return self._equipment

    @equipment.setter
    def equipment(self, equipment: EquipmentMapInfo) -> None:
        self._equipment = equipment

    @property
    def sit_state(self) -> SitState:
        return self._sit_state

    @sit_state.setter
    def sit_state(self, sit_state: SitState) -> None:
        self._sit_state = sit_state

    @property
    def invisible(self) -> bool:
        return self._invisible

    @invisible.setter
    def invisible(self, invisible: bool) -> None:
        self._invisible = invisible

    @property
    def warp_effect(self) -> Optional[WarpEffect]:
        return self._warp_effect

    @warp_effect.setter
    def warp_effect(self, warp_effect: Optional[WarpEffect]) -> None:
        self._warp_effect = warp_effect

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterMapInfo") -> None:
        """
        Serializes an instance of `CharacterMapInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterMapInfo): The data to serialize.
        """
        if data._name is None:
            raise SerializationError("name must be provided.")
        writer.add_string(data._name)
        writer.add_byte(0xFF)
        if data._player_id is None:
            raise SerializationError("player_id must be provided.")
        writer.add_short(data._player_id)
        if data._map_id is None:
            raise SerializationError("map_id must be provided.")
        writer.add_short(data._map_id)
        if data._coords is None:
            raise SerializationError("coords must be provided.")
        BigCoords.serialize(writer, data._coords)
        if data._direction is None:
            raise SerializationError("direction must be provided.")
        writer.add_char(int(data._direction))
        if data._class_id is None:
            raise SerializationError("class_id must be provided.")
        writer.add_char(data._class_id)
        if data._guild_tag is None:
            raise SerializationError("guild_tag must be provided.")
        if len(data._guild_tag) != 3:
            raise SerializationError(f"Expected length of guild_tag to be exactly 3, got {len(data._guild_tag)}.")
        writer.add_fixed_string(data._guild_tag, 3, False)
        if data._level is None:
            raise SerializationError("level must be provided.")
        writer.add_char(data._level)
        if data._gender is None:
            raise SerializationError("gender must be provided.")
        writer.add_char(int(data._gender))
        if data._hair_style is None:
            raise SerializationError("hair_style must be provided.")
        writer.add_char(data._hair_style)
        if data._hair_color is None:
            raise SerializationError("hair_color must be provided.")
        writer.add_char(data._hair_color)
        if data._skin is None:
            raise SerializationError("skin must be provided.")
        writer.add_char(data._skin)
        if data._max_hp is None:
            raise SerializationError("max_hp must be provided.")
        writer.add_short(data._max_hp)
        if data._hp is None:
            raise SerializationError("hp must be provided.")
        writer.add_short(data._hp)
        if data._max_tp is None:
            raise SerializationError("max_tp must be provided.")
        writer.add_short(data._max_tp)
        if data._tp is None:
            raise SerializationError("tp must be provided.")
        writer.add_short(data._tp)
        if data._equipment is None:
            raise SerializationError("equipment must be provided.")
        EquipmentMapInfo.serialize(writer, data._equipment)
        if data._sit_state is None:
            raise SerializationError("sit_state must be provided.")
        writer.add_char(int(data._sit_state))
        if data._invisible is None:
            raise SerializationError("invisible must be provided.")
        writer.add_char(1 if data._invisible else 0)
        reached_missing_optional = data._warp_effect is None
        if not reached_missing_optional:
            writer.add_char(int(cast(WarpEffect, data._warp_effect)))

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterMapInfo":
        """
        Deserializes an instance of `CharacterMapInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterMapInfo: The data to serialize.
        """
        data: CharacterMapInfo = CharacterMapInfo()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._player_id = reader.get_short()
            data._map_id = reader.get_short()
            data._coords = BigCoords.deserialize(reader)
            data._direction = Direction(reader.get_char())
            data._class_id = reader.get_char()
            data._guild_tag = reader.get_fixed_string(3, False)
            data._level = reader.get_char()
            data._gender = Gender(reader.get_char())
            data._hair_style = reader.get_char()
            data._hair_color = reader.get_char()
            data._skin = reader.get_char()
            data._max_hp = reader.get_short()
            data._hp = reader.get_short()
            data._max_tp = reader.get_short()
            data._tp = reader.get_short()
            data._equipment = EquipmentMapInfo.deserialize(reader)
            data._sit_state = SitState(reader.get_char())
            data._invisible = reader.get_char() != 0
            if reader.remaining > 0:
                data._warp_effect = WarpEffect(reader.get_char())
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterMapInfo(byte_size={repr(self._byte_size)}, name={repr(self._name)}, player_id={repr(self._player_id)}, map_id={repr(self._map_id)}, coords={repr(self._coords)}, direction={repr(self._direction)}, class_id={repr(self._class_id)}, guild_tag={repr(self._guild_tag)}, level={repr(self._level)}, gender={repr(self._gender)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, skin={repr(self._skin)}, max_hp={repr(self._max_hp)}, hp={repr(self._hp)}, max_tp={repr(self._max_tp)}, tp={repr(self._tp)}, equipment={repr(self._equipment)}, sit_state={repr(self._sit_state)}, invisible={repr(self._invisible)}, warp_effect={repr(self._warp_effect)})"
