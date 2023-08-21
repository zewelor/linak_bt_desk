import logging
from time import sleep

import linak_dpg_bt.constants as constants
from .connection import BTLEConnection
from .desk_mover import DeskMover
from .desk_position import DeskPosition
from .dpg_command import DPGCommand, DeskOffsetCommand, MemorySetting1Command, MemorySetting2Command
from .height_speed import HeightSpeed

_LOGGER = logging.getLogger(__name__)

DPG_COMMAND_NOTIFY_HANDLE = 0x0015  # Used for DPG Commands anwsers

NAME_HANDLE = 0x0003

PROP_GET_CAPABILITIES = 0x80
PROP_DESK_OFFSET = 0x81
PROP_USER_ID = 0x86
PROP_MEMORY_POSITION_1 = 0x89
PROP_MEMORY_POSITION_2 = 0x8a


class DPGCommandReadError(Exception):
    pass


class WrongFavoriteNumber(Exception):
    pass


class LinakDesk:
    def __init__(self, bdaddr):
        self._bdaddr = bdaddr
        self._conn = BTLEConnection(bdaddr)

        self._name = None
        self._desk_offset = None
        self._fav_position_1 = None
        self._fav_position_2 = None
        self._height_speed = None

    @property
    def name(self):
        return self._wait_for_variable('_name')

    @property
    def desk_offset(self):
        return self._wait_for_variable('_desk_offset')

    @property
    def favorite_position_1(self):
        return self._wait_for_variable('_fav_position_1')

    @property
    def favorite_position_2(self):
        return self._wait_for_variable('_fav_position_2')

    @property
    def current_height(self):
        return self.height_speed.height

    @property
    def current_height_with_offset(self):
        return self._with_desk_offset(self.height_speed.height)

    @property
    def height_speed(self):
        return self._wait_for_variable('_height_speed')

    def read_dpg_data(self):
        _LOGGER.debug("Querying the device..")

        with self._conn as conn:
            """ We need to query for name before doing anything, without it device doesnt respond """
            self._name = conn.read_characteristic(NAME_HANDLE)

            conn.subscribe_to_notification(DPG_COMMAND_NOTIFY_HANDLE, constants.DPG_COMMAND_HANDLE,
                                           self._handle_dpg_notification)

            # conn.dpg_command(PROP_USER_ID)
            # conn.dpg_command(PROP_GET_CAPABILITIES)
            conn.dpg_command(PROP_DESK_OFFSET)
            conn.dpg_command(PROP_MEMORY_POSITION_1)
            conn.dpg_command(PROP_MEMORY_POSITION_2)
            self._height_speed = HeightSpeed.from_bytes(conn.read_characteristic(constants.REFERENCE_OUTPUT_HANDLE))

    def __str__(self):
        return "[%s] Desk offset: %s, name: %s\nFav position1: %s, Fav position 2: %s Height with offset: %s" % (
            self._bdaddr,
            self.desk_offset.human_cm,
            self.name,
            self._with_desk_offset(self.favorite_position_1).human_cm,
            self._with_desk_offset(self.favorite_position_2).human_cm,
            self._with_desk_offset(self.height_speed.height).human_cm,
        )

    def move_to_cm(self, cm):
        calculated_raw = DeskPosition.raw_from_cm(cm - self._desk_offset.cm)
        self._move_to_raw(calculated_raw)

    def move_to_fav(self, fav):
        if fav == 1:
            raw = self.favorite_position_1.raw
        elif fav == 2:
            raw = self.favorite_position_2.raw
        else:
            raise DPGCommandReadError('Favorite with position: %d does not exists' % fav)

        self._move_to_raw(raw)

    def _wait_for_variable(self, var_name):
        value = getattr(self, var_name)
        if value is not None:
            return value

        for _ in range(0, 100):
            value = getattr(self, var_name)

            if value is not None:
                return value

            sleep(0.2)

        raise DPGCommandReadError('Cannot fetch value for %s' % var_name)

    def _with_desk_offset(self, value):
        return DeskPosition(value.raw + self.desk_offset.raw)

    def _handle_dpg_notification(self, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        _LOGGER.debug("Received notification from the device..")

        if data[0] != 0x1:
            raise DPGCommandReadError('DPG_Control packets needs to have 0x01 in first byte')

        command = DPGCommand.build_command(data)
        _LOGGER.debug("Received %s (%s)", command.__class__.__name__, command.decoded_value)

        if command.__class__ == DeskOffsetCommand:
            self._desk_offset = command.offset
        elif command.__class__ == MemorySetting1Command:
            self._fav_position_1 = command.offset
        elif command.__class__ == MemorySetting2Command:
            self._fav_position_2 = command.offset

    def _move_to_raw(self, raw_value):
        with self._conn as conn:
            current_raw_height = self.current_height.raw
            move_not_possible = (abs(raw_value - current_raw_height) < 10)

            if move_not_possible:
                _LOGGER.debug("Move not possible, current raw height: %d", current_raw_height)
                return

            DeskMover(conn, raw_value).start()
