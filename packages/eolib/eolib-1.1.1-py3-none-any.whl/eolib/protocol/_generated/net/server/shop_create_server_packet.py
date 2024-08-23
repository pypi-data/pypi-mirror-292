# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..weight import Weight
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopCreateServerPacket(Packet):
    """
    Response to crafting an item from a shop
    """
    _byte_size: int = 0
    _craft_item_id: int = None # type: ignore [assignment]
    _weight: Weight = None # type: ignore [assignment]
    _ingredients: list[Item] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def craft_item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._craft_item_id

    @craft_item_id.setter
    def craft_item_id(self, craft_item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._craft_item_id = craft_item_id

    @property
    def weight(self) -> Weight:
        return self._weight

    @weight.setter
    def weight(self, weight: Weight) -> None:
        self._weight = weight

    @property
    def ingredients(self) -> list[Item]:
        """
        Note:
          - Length must be `4`.
        """
        return self._ingredients

    @ingredients.setter
    def ingredients(self, ingredients: list[Item]) -> None:
        """
        Note:
          - Length must be `4`.
        """
        self._ingredients = ingredients

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Shop

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ShopCreateServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopCreateServerPacket") -> None:
        """
        Serializes an instance of `ShopCreateServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopCreateServerPacket): The data to serialize.
        """
        if data._craft_item_id is None:
            raise SerializationError("craft_item_id must be provided.")
        writer.add_short(data._craft_item_id)
        if data._weight is None:
            raise SerializationError("weight must be provided.")
        Weight.serialize(writer, data._weight)
        if data._ingredients is None:
            raise SerializationError("ingredients must be provided.")
        if len(data._ingredients) != 4:
            raise SerializationError(f"Expected length of ingredients to be exactly 4, got {len(data._ingredients)}.")
        for i in range(4):
            Item.serialize(writer, data._ingredients[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopCreateServerPacket":
        """
        Deserializes an instance of `ShopCreateServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopCreateServerPacket: The data to serialize.
        """
        data: ShopCreateServerPacket = ShopCreateServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._craft_item_id = reader.get_short()
            data._weight = Weight.deserialize(reader)
            data._ingredients = []
            for i in range(4):
                data._ingredients.append(Item.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopCreateServerPacket(byte_size={repr(self._byte_size)}, craft_item_id={repr(self._craft_item_id)}, weight={repr(self._weight)}, ingredients={repr(self._ingredients)})"
