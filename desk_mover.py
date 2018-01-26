import logging
from time import sleep

import constants
from threading import Timer

from desk_position import DeskPosition
from height_speed import HeightSpeed

MOVE_TO_HANDLE = 0x003a
REFERENCE_OUTPUT_NOTIFY_HANDLE = 0x001e  # Used for desk offset / speed notifications

_LOGGER = logging.getLogger(__name__)


class DeskMover:
    def __init__(self, conn, target):
        self._conn = conn
        self._target = target
        self._running = False
        self._stopTimer = Timer(30, self._stop_move)

    def start(self):
        _LOGGER.debug("Start move to: %d", self._target)

        self._running = True
        self._stopTimer.start()

        with self._conn as conn:
            conn.subscribe_to_notification(REFERENCE_OUTPUT_NOTIFY_HANDLE, constants.REFERENCE_OUTPUT_HANDLE,
                                           self._handle_notification)

            for _ in range(150):
                if self._running:
                    self._send_move_to()
                    sleep(0.2)

    def _handle_notification(self, data):
        hs = HeightSpeed.from_bytes(data)

        _LOGGER.debug("Current relative height: %s, speed: %f", hs.height.human_cm, hs.speed.parsed)

        if hs.speed.parsed < 0.001:
            self._stop_move()

    def _send_move_to(self):
        _LOGGER.debug("Sending move to: %d", self._target)
        self._conn.make_request(MOVE_TO_HANDLE, DeskPosition.bytes_from_raw(self._target))

    def _stop_move(self):
        _LOGGER.debug("Move stopped")
        # send stop move
        self._running = False
        self._stopTimer.cancel()
