# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .map_effect import MapEffect
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectUseServerPacket(Packet):
    """
    Map effect
    """
    _byte_size: int = 0
    _effect: MapEffect = None # type: ignore [assignment]
    _effect_data: 'EffectUseServerPacket.EffectData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def effect(self) -> MapEffect:
        return self._effect

    @effect.setter
    def effect(self, effect: MapEffect) -> None:
        self._effect = effect

    @property
    def effect_data(self) -> 'EffectUseServerPacket.EffectData':
        """
        EffectUseServerPacket.EffectData: Gets or sets the data associated with the `effect` field.
        """
        return self._effect_data

    @effect_data.setter
    def effect_data(self, effect_data: 'EffectUseServerPacket.EffectData') -> None:
        self._effect_data = effect_data

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
        return PacketAction.Use

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        EffectUseServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectUseServerPacket") -> None:
        """
        Serializes an instance of `EffectUseServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectUseServerPacket): The data to serialize.
        """
        if data._effect is None:
            raise SerializationError("effect must be provided.")
        writer.add_char(int(data._effect))
        if data._effect == MapEffect.Quake:
            if not isinstance(data._effect_data, EffectUseServerPacket.EffectDataQuake):
                raise SerializationError("Expected effect_data to be type EffectUseServerPacket.EffectDataQuake for effect " + MapEffect(data._effect).name + ".")
            EffectUseServerPacket.EffectDataQuake.serialize(writer, data._effect_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectUseServerPacket":
        """
        Deserializes an instance of `EffectUseServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectUseServerPacket: The data to serialize.
        """
        data: EffectUseServerPacket = EffectUseServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._effect = MapEffect(reader.get_char())
            if data._effect == MapEffect.Quake:
                data._effect_data = EffectUseServerPacket.EffectDataQuake.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectUseServerPacket(byte_size={repr(self._byte_size)}, effect={repr(self._effect)}, effect_data={repr(self._effect_data)})"

    EffectData = Union['EffectUseServerPacket.EffectDataQuake', None]
    EffectData.__doc__ = \
        """
        Data associated with different values of the `effect` field.
        """

    class EffectDataQuake:
        """
        Data associated with effect value MapEffect.Quake
        """
        _byte_size: int = 0
        _quake_strength: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def quake_strength(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._quake_strength

        @quake_strength.setter
        def quake_strength(self, quake_strength: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._quake_strength = quake_strength

        @staticmethod
        def serialize(writer: EoWriter, data: "EffectUseServerPacket.EffectDataQuake") -> None:
            """
            Serializes an instance of `EffectUseServerPacket.EffectDataQuake` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (EffectUseServerPacket.EffectDataQuake): The data to serialize.
            """
            if data._quake_strength is None:
                raise SerializationError("quake_strength must be provided.")
            writer.add_char(data._quake_strength)

        @staticmethod
        def deserialize(reader: EoReader) -> "EffectUseServerPacket.EffectDataQuake":
            """
            Deserializes an instance of `EffectUseServerPacket.EffectDataQuake` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                EffectUseServerPacket.EffectDataQuake: The data to serialize.
            """
            data: EffectUseServerPacket.EffectDataQuake = EffectUseServerPacket.EffectDataQuake()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._quake_strength = reader.get_char()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"EffectUseServerPacket.EffectDataQuake(byte_size={repr(self._byte_size)}, quake_strength={repr(self._quake_strength)})"
