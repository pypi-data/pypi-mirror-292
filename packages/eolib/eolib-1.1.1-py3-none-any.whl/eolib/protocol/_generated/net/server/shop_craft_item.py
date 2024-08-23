# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..char_item import CharItem
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopCraftItem:
    """
    An item that a shop can craft
    """
    _byte_size: int = 0
    _item_id: int = None # type: ignore [assignment]
    _ingredients: list[CharItem] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._item_id

    @item_id.setter
    def item_id(self, item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._item_id = item_id

    @property
    def ingredients(self) -> list[CharItem]:
        """
        Note:
          - Length must be `4`.
        """
        return self._ingredients

    @ingredients.setter
    def ingredients(self, ingredients: list[CharItem]) -> None:
        """
        Note:
          - Length must be `4`.
        """
        self._ingredients = ingredients

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopCraftItem") -> None:
        """
        Serializes an instance of `ShopCraftItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopCraftItem): The data to serialize.
        """
        if data._item_id is None:
            raise SerializationError("item_id must be provided.")
        writer.add_short(data._item_id)
        if data._ingredients is None:
            raise SerializationError("ingredients must be provided.")
        if len(data._ingredients) != 4:
            raise SerializationError(f"Expected length of ingredients to be exactly 4, got {len(data._ingredients)}.")
        for i in range(4):
            CharItem.serialize(writer, data._ingredients[i])

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopCraftItem":
        """
        Deserializes an instance of `ShopCraftItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopCraftItem: The data to serialize.
        """
        data: ShopCraftItem = ShopCraftItem()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._item_id = reader.get_short()
            data._ingredients = []
            for i in range(4):
                data._ingredients.append(CharItem.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopCraftItem(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, ingredients={repr(self._ingredients)})"
