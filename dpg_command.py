import codecs
import struct

from desk_position import DeskPosition


class DPGCommand:
    @classmethod
    def wrap_read_command(cls, value):
        return struct.pack('BBB', 0x7F, value, 0x0)

    @classmethod
    def build_command(cls, data):
        command_type = data[1]
        command_data = data[2:]

        return COMMAND_TYPES.get(command_type, cls)(command_data)

    def __init__(self, data):
        self._data = data

    @property
    def raw_value(self):
        return codecs.encode(self._data, 'hex')

    @property
    def decoded_value(self):
        return self.raw_value


class UserIDCommand(DPGCommand):
    pass


class CapabilitiesCommand(DPGCommand):
    pass


class ReminderSettingsCommand(DPGCommand):
    pass


class DeskOffsetCommand(DPGCommand):
    @property
    def decoded_value(self):
        if self._data[0] != 0x01:
            return -1

        return self.offset

    @property
    def offset(self):
        return DeskPosition.from_bytes(self._data[1:3])


class MemorySettingCommand(DeskOffsetCommand):
    pass


class MemorySetting1Command(MemorySettingCommand):
    pass


class MemorySetting2Command(MemorySettingCommand):
    pass


COMMAND_TYPES = {
    0x02: CapabilitiesCommand,
    0x03: DeskOffsetCommand,
    0x07: MemorySetting2Command,
    0x0b: ReminderSettingsCommand,
    0x0d: MemorySetting1Command,
    0x11: UserIDCommand,
}


