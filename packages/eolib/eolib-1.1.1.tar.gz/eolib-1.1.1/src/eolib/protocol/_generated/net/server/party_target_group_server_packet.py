# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .party_exp_share import PartyExpShare
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyTargetGroupServerPacket(Packet):
    """
    Updated experience and level-ups from party experience
    """
    _byte_size: int = 0
    _gains: list[PartyExpShare] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def gains(self) -> list[PartyExpShare]:
        return self._gains

    @gains.setter
    def gains(self, gains: list[PartyExpShare]) -> None:
        self._gains = gains

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Party

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
        PartyTargetGroupServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyTargetGroupServerPacket") -> None:
        """
        Serializes an instance of `PartyTargetGroupServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyTargetGroupServerPacket): The data to serialize.
        """
        if data._gains is None:
            raise SerializationError("gains must be provided.")
        for i in range(len(data._gains)):
            PartyExpShare.serialize(writer, data._gains[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyTargetGroupServerPacket":
        """
        Deserializes an instance of `PartyTargetGroupServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyTargetGroupServerPacket: The data to serialize.
        """
        data: PartyTargetGroupServerPacket = PartyTargetGroupServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            gains_length = int(reader.remaining / 7)
            data._gains = []
            for i in range(gains_length):
                data._gains.append(PartyExpShare.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyTargetGroupServerPacket(byte_size={repr(self._byte_size)}, gains={repr(self._gains)})"
