# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TradeAgreeServerPacket(Packet):
    """
    Partner agree state updated
    """
    _byte_size: int = 0
    _partner_player_id: int = None # type: ignore [assignment]
    _agree: bool = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def partner_player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._partner_player_id

    @partner_player_id.setter
    def partner_player_id(self, partner_player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._partner_player_id = partner_player_id

    @property
    def agree(self) -> bool:
        return self._agree

    @agree.setter
    def agree(self, agree: bool) -> None:
        self._agree = agree

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Trade

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TradeAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeAgreeServerPacket") -> None:
        """
        Serializes an instance of `TradeAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeAgreeServerPacket): The data to serialize.
        """
        if data._partner_player_id is None:
            raise SerializationError("partner_player_id must be provided.")
        writer.add_short(data._partner_player_id)
        if data._agree is None:
            raise SerializationError("agree must be provided.")
        writer.add_char(1 if data._agree else 0)

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeAgreeServerPacket":
        """
        Deserializes an instance of `TradeAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeAgreeServerPacket: The data to serialize.
        """
        data: TradeAgreeServerPacket = TradeAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._partner_player_id = reader.get_short()
            data._agree = reader.get_char() != 0
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeAgreeServerPacket(byte_size={repr(self._byte_size)}, partner_player_id={repr(self._partner_player_id)}, agree={repr(self._agree)})"
