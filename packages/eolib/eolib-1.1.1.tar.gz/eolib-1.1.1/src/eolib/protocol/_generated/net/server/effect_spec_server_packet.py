# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .map_damage_type import MapDamageType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectSpecServerPacket(Packet):
    """
    Taking spike or tp drain damage
    """
    _byte_size: int = 0
    _map_damage_type: MapDamageType = None # type: ignore [assignment]
    _map_damage_type_data: 'EffectSpecServerPacket.MapDamageTypeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def map_damage_type(self) -> MapDamageType:
        return self._map_damage_type

    @map_damage_type.setter
    def map_damage_type(self, map_damage_type: MapDamageType) -> None:
        self._map_damage_type = map_damage_type

    @property
    def map_damage_type_data(self) -> 'EffectSpecServerPacket.MapDamageTypeData':
        """
        EffectSpecServerPacket.MapDamageTypeData: Gets or sets the data associated with the `map_damage_type` field.
        """
        return self._map_damage_type_data

    @map_damage_type_data.setter
    def map_damage_type_data(self, map_damage_type_data: 'EffectSpecServerPacket.MapDamageTypeData') -> None:
        self._map_damage_type_data = map_damage_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Effect

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
        EffectSpecServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectSpecServerPacket") -> None:
        """
        Serializes an instance of `EffectSpecServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectSpecServerPacket): The data to serialize.
        """
        if data._map_damage_type is None:
            raise SerializationError("map_damage_type must be provided.")
        writer.add_char(int(data._map_damage_type))
        if data._map_damage_type == MapDamageType.TpDrain:
            if not isinstance(data._map_damage_type_data, EffectSpecServerPacket.MapDamageTypeDataTpDrain):
                raise SerializationError("Expected map_damage_type_data to be type EffectSpecServerPacket.MapDamageTypeDataTpDrain for map_damage_type " + MapDamageType(data._map_damage_type).name + ".")
            EffectSpecServerPacket.MapDamageTypeDataTpDrain.serialize(writer, data._map_damage_type_data)
        elif data._map_damage_type == MapDamageType.Spikes:
            if not isinstance(data._map_damage_type_data, EffectSpecServerPacket.MapDamageTypeDataSpikes):
                raise SerializationError("Expected map_damage_type_data to be type EffectSpecServerPacket.MapDamageTypeDataSpikes for map_damage_type " + MapDamageType(data._map_damage_type).name + ".")
            EffectSpecServerPacket.MapDamageTypeDataSpikes.serialize(writer, data._map_damage_type_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectSpecServerPacket":
        """
        Deserializes an instance of `EffectSpecServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectSpecServerPacket: The data to serialize.
        """
        data: EffectSpecServerPacket = EffectSpecServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._map_damage_type = MapDamageType(reader.get_char())
            if data._map_damage_type == MapDamageType.TpDrain:
                data._map_damage_type_data = EffectSpecServerPacket.MapDamageTypeDataTpDrain.deserialize(reader)
            elif data._map_damage_type == MapDamageType.Spikes:
                data._map_damage_type_data = EffectSpecServerPacket.MapDamageTypeDataSpikes.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectSpecServerPacket(byte_size={repr(self._byte_size)}, map_damage_type={repr(self._map_damage_type)}, map_damage_type_data={repr(self._map_damage_type_data)})"

    MapDamageTypeData = Union['EffectSpecServerPacket.MapDamageTypeDataTpDrain', 'EffectSpecServerPacket.MapDamageTypeDataSpikes', None]
    MapDamageTypeData.__doc__ = \
        """
        Data associated with different values of the `map_damage_type` field.
        """

    class MapDamageTypeDataTpDrain:
        """
        Data associated with map_damage_type value MapDamageType.TpDrain
        """
        _byte_size: int = 0
        _tp_damage: int = None # type: ignore [assignment]
        _tp: int = None # type: ignore [assignment]
        _max_tp: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def tp_damage(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._tp_damage

        @tp_damage.setter
        def tp_damage(self, tp_damage: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._tp_damage = tp_damage

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

        @staticmethod
        def serialize(writer: EoWriter, data: "EffectSpecServerPacket.MapDamageTypeDataTpDrain") -> None:
            """
            Serializes an instance of `EffectSpecServerPacket.MapDamageTypeDataTpDrain` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (EffectSpecServerPacket.MapDamageTypeDataTpDrain): The data to serialize.
            """
            if data._tp_damage is None:
                raise SerializationError("tp_damage must be provided.")
            writer.add_short(data._tp_damage)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)

        @staticmethod
        def deserialize(reader: EoReader) -> "EffectSpecServerPacket.MapDamageTypeDataTpDrain":
            """
            Deserializes an instance of `EffectSpecServerPacket.MapDamageTypeDataTpDrain` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                EffectSpecServerPacket.MapDamageTypeDataTpDrain: The data to serialize.
            """
            data: EffectSpecServerPacket.MapDamageTypeDataTpDrain = EffectSpecServerPacket.MapDamageTypeDataTpDrain()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._tp_damage = reader.get_short()
                data._tp = reader.get_short()
                data._max_tp = reader.get_short()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"EffectSpecServerPacket.MapDamageTypeDataTpDrain(byte_size={repr(self._byte_size)}, tp_damage={repr(self._tp_damage)}, tp={repr(self._tp)}, max_tp={repr(self._max_tp)})"

    class MapDamageTypeDataSpikes:
        """
        Data associated with map_damage_type value MapDamageType.Spikes
        """
        _byte_size: int = 0
        _hp_damage: int = None # type: ignore [assignment]
        _hp: int = None # type: ignore [assignment]
        _max_hp: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def hp_damage(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._hp_damage

        @hp_damage.setter
        def hp_damage(self, hp_damage: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._hp_damage = hp_damage

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

        @staticmethod
        def serialize(writer: EoWriter, data: "EffectSpecServerPacket.MapDamageTypeDataSpikes") -> None:
            """
            Serializes an instance of `EffectSpecServerPacket.MapDamageTypeDataSpikes` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (EffectSpecServerPacket.MapDamageTypeDataSpikes): The data to serialize.
            """
            if data._hp_damage is None:
                raise SerializationError("hp_damage must be provided.")
            writer.add_short(data._hp_damage)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)

        @staticmethod
        def deserialize(reader: EoReader) -> "EffectSpecServerPacket.MapDamageTypeDataSpikes":
            """
            Deserializes an instance of `EffectSpecServerPacket.MapDamageTypeDataSpikes` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                EffectSpecServerPacket.MapDamageTypeDataSpikes: The data to serialize.
            """
            data: EffectSpecServerPacket.MapDamageTypeDataSpikes = EffectSpecServerPacket.MapDamageTypeDataSpikes()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._hp_damage = reader.get_short()
                data._hp = reader.get_short()
                data._max_hp = reader.get_short()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"EffectSpecServerPacket.MapDamageTypeDataSpikes(byte_size={repr(self._byte_size)}, hp_damage={repr(self._hp_damage)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)})"
