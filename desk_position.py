import struct
import math


class DeskPosition:
    @classmethod
    def from_bytes(cls, data):
        return cls(struct.unpack('<H', data[0:2])[0])

    @classmethod
    def raw_from_cm(cls, cm):
        return math.ceil(cm * 100.0)

    @classmethod
    def bytes_from_raw(cls, raw):
        return struct.pack('<H', raw)

    @classmethod
    def from_cm(cls, cm):
        return cls(cls.raw_from_cm(cm))

    def __init__(self, raw):
        self._raw = raw

    @property
    def raw(self):
        return self._raw

    @property
    def cm(self):
        return math.ceil(self.raw / 100.0)

    @property
    def human_cm(self):
        return "%d cm" % self.cm
