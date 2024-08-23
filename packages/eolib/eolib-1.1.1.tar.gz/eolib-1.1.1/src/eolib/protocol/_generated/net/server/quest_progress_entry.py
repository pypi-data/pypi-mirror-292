# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .quest_requirement_icon import QuestRequirementIcon
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestProgressEntry:
    """
    An entry in the Quest Progress window
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _description: str = None # type: ignore [assignment]
    _icon: QuestRequirementIcon = None # type: ignore [assignment]
    _progress: int = None # type: ignore [assignment]
    _target: int = None # type: ignore [assignment]

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
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        self._description = description

    @property
    def icon(self) -> QuestRequirementIcon:
        return self._icon

    @icon.setter
    def icon(self, icon: QuestRequirementIcon) -> None:
        self._icon = icon

    @property
    def progress(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._progress

    @progress.setter
    def progress(self, progress: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._progress = progress

    @property
    def target(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._target

    @target.setter
    def target(self, target: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._target = target

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestProgressEntry") -> None:
        """
        Serializes an instance of `QuestProgressEntry` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestProgressEntry): The data to serialize.
        """
        if data._name is None:
            raise SerializationError("name must be provided.")
        writer.add_string(data._name)
        writer.add_byte(0xFF)
        if data._description is None:
            raise SerializationError("description must be provided.")
        writer.add_string(data._description)
        writer.add_byte(0xFF)
        if data._icon is None:
            raise SerializationError("icon must be provided.")
        writer.add_short(int(data._icon))
        if data._progress is None:
            raise SerializationError("progress must be provided.")
        writer.add_short(data._progress)
        if data._target is None:
            raise SerializationError("target must be provided.")
        writer.add_short(data._target)

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestProgressEntry":
        """
        Deserializes an instance of `QuestProgressEntry` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestProgressEntry: The data to serialize.
        """
        data: QuestProgressEntry = QuestProgressEntry()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._description = reader.get_string()
            reader.next_chunk()
            data._icon = QuestRequirementIcon(reader.get_short())
            data._progress = reader.get_short()
            data._target = reader.get_short()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestProgressEntry(byte_size={repr(self._byte_size)}, name={repr(self._name)}, description={repr(self._description)}, icon={repr(self._icon)}, progress={repr(self._progress)}, target={repr(self._target)})"
