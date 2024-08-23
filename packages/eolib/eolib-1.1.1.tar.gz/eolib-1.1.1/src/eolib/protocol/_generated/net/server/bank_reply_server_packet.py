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

class BankReplyServerPacket(Packet):
    """
    Update gold counts after deposit/withdraw
    """
    _byte_size: int = 0
    _gold_inventory: int = None # type: ignore [assignment]
    _gold_bank: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def gold_inventory(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._gold_inventory

    @gold_inventory.setter
    def gold_inventory(self, gold_inventory: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._gold_inventory = gold_inventory

    @property
    def gold_bank(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._gold_bank

    @gold_bank.setter
    def gold_bank(self, gold_bank: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._gold_bank = gold_bank

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Bank

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BankReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BankReplyServerPacket") -> None:
        """
        Serializes an instance of `BankReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BankReplyServerPacket): The data to serialize.
        """
        if data._gold_inventory is None:
            raise SerializationError("gold_inventory must be provided.")
        writer.add_int(data._gold_inventory)
        if data._gold_bank is None:
            raise SerializationError("gold_bank must be provided.")
        writer.add_int(data._gold_bank)

    @staticmethod
    def deserialize(reader: EoReader) -> "BankReplyServerPacket":
        """
        Deserializes an instance of `BankReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BankReplyServerPacket: The data to serialize.
        """
        data: BankReplyServerPacket = BankReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._gold_inventory = reader.get_int()
            data._gold_bank = reader.get_int()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BankReplyServerPacket(byte_size={repr(self._byte_size)}, gold_inventory={repr(self._gold_inventory)}, gold_bank={repr(self._gold_bank)})"
