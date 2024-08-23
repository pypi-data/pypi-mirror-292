# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .party_member import PartyMember
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyListServerPacket(Packet):
    """
    Party member list update
    """
    _byte_size: int = 0
    _members: list[PartyMember] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def members(self) -> list[PartyMember]:
        return self._members

    @members.setter
    def members(self, members: list[PartyMember]) -> None:
        self._members = members

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
        return PacketAction.List

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PartyListServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyListServerPacket") -> None:
        """
        Serializes an instance of `PartyListServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyListServerPacket): The data to serialize.
        """
        if data._members is None:
            raise SerializationError("members must be provided.")
        for i in range(len(data._members)):
            if i > 0:
                writer.add_byte(0xFF)
            PartyMember.serialize(writer, data._members[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyListServerPacket":
        """
        Deserializes an instance of `PartyListServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyListServerPacket: The data to serialize.
        """
        data: PartyListServerPacket = PartyListServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._members = []
            while reader.remaining > 0:
                data._members.append(PartyMember.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyListServerPacket(byte_size={repr(self._byte_size)}, members={repr(self._members)})"
