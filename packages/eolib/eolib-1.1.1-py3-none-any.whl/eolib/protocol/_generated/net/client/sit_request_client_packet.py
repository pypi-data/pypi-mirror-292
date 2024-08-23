# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .sit_action import SitAction
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SitRequestClientPacket(Packet):
    """
    Sit/stand request
    """
    _byte_size: int = 0
    _sit_action: SitAction = None # type: ignore [assignment]
    _sit_action_data: 'SitRequestClientPacket.SitActionData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def sit_action(self) -> SitAction:
        return self._sit_action

    @sit_action.setter
    def sit_action(self, sit_action: SitAction) -> None:
        self._sit_action = sit_action

    @property
    def sit_action_data(self) -> 'SitRequestClientPacket.SitActionData':
        """
        SitRequestClientPacket.SitActionData: Gets or sets the data associated with the `sit_action` field.
        """
        return self._sit_action_data

    @sit_action_data.setter
    def sit_action_data(self, sit_action_data: 'SitRequestClientPacket.SitActionData') -> None:
        self._sit_action_data = sit_action_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Sit

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        SitRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SitRequestClientPacket") -> None:
        """
        Serializes an instance of `SitRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SitRequestClientPacket): The data to serialize.
        """
        if data._sit_action is None:
            raise SerializationError("sit_action must be provided.")
        writer.add_char(int(data._sit_action))
        if data._sit_action == SitAction.Sit:
            if not isinstance(data._sit_action_data, SitRequestClientPacket.SitActionDataSit):
                raise SerializationError("Expected sit_action_data to be type SitRequestClientPacket.SitActionDataSit for sit_action " + SitAction(data._sit_action).name + ".")
            SitRequestClientPacket.SitActionDataSit.serialize(writer, data._sit_action_data)

    @staticmethod
    def deserialize(reader: EoReader) -> "SitRequestClientPacket":
        """
        Deserializes an instance of `SitRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SitRequestClientPacket: The data to serialize.
        """
        data: SitRequestClientPacket = SitRequestClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._sit_action = SitAction(reader.get_char())
            if data._sit_action == SitAction.Sit:
                data._sit_action_data = SitRequestClientPacket.SitActionDataSit.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SitRequestClientPacket(byte_size={repr(self._byte_size)}, sit_action={repr(self._sit_action)}, sit_action_data={repr(self._sit_action_data)})"

    SitActionData = Union['SitRequestClientPacket.SitActionDataSit', None]
    SitActionData.__doc__ = \
        """
        Data associated with different values of the `sit_action` field.
        """

    class SitActionDataSit:
        """
        Data associated with sit_action value SitAction.Sit
        """
        _byte_size: int = 0
        _cursor_coords: Coords = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def cursor_coords(self) -> Coords:
            """
            The coordinates of the map cursor
            """
            return self._cursor_coords

        @cursor_coords.setter
        def cursor_coords(self, cursor_coords: Coords) -> None:
            """
            The coordinates of the map cursor
            """
            self._cursor_coords = cursor_coords

        @staticmethod
        def serialize(writer: EoWriter, data: "SitRequestClientPacket.SitActionDataSit") -> None:
            """
            Serializes an instance of `SitRequestClientPacket.SitActionDataSit` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (SitRequestClientPacket.SitActionDataSit): The data to serialize.
            """
            if data._cursor_coords is None:
                raise SerializationError("cursor_coords must be provided.")
            Coords.serialize(writer, data._cursor_coords)

        @staticmethod
        def deserialize(reader: EoReader) -> "SitRequestClientPacket.SitActionDataSit":
            """
            Deserializes an instance of `SitRequestClientPacket.SitActionDataSit` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                SitRequestClientPacket.SitActionDataSit: The data to serialize.
            """
            data: SitRequestClientPacket.SitActionDataSit = SitRequestClientPacket.SitActionDataSit()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._cursor_coords = Coords.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"SitRequestClientPacket.SitActionDataSit(byte_size={repr(self._byte_size)}, cursor_coords={repr(self._cursor_coords)})"
