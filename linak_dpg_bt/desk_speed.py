import struct


class DeskSpeed:
    @classmethod
    def from_bytes(cls, data):
        return cls(struct.unpack('H', data[2:4])[0] & 0xFFF)

    def __init__(self, raw):
        self._raw = raw

    @property
    def raw(self):
        return self._raw

    @property
    def parsed(self):
        return (self.raw * 0.09765625) / 10.0
