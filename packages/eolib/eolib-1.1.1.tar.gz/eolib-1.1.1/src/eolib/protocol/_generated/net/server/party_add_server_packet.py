# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .party_member import PartyMember
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyAddServerPacket(Packet):
    """
    New player joined the party
    """
    _byte_size: int = 0
    _member: PartyMember = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def member(self) -> PartyMember:
        return self._member

    @member.setter
    def member(self, member: PartyMember) -> None:
        self._member = member

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
        return PacketAction.Add

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PartyAddServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyAddServerPacket") -> None:
        """
        Serializes an instance of `PartyAddServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyAddServerPacket): The data to serialize.
        """
        if data._member is None:
            raise SerializationError("member must be provided.")
        PartyMember.serialize(writer, data._member)

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyAddServerPacket":
        """
        Deserializes an instance of `PartyAddServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyAddServerPacket: The data to serialize.
        """
        data: PartyAddServerPacket = PartyAddServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._member = PartyMember.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyAddServerPacket(byte_size={repr(self._byte_size)}, member={repr(self._member)})"
