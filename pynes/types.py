import numpy as np


class char(type):
    pass


class uint8(type):
    def __init__(self, value=0):
        return np.uint8(value)


class uint16(type):  # two bytes
    pass


class uint32(type):
    # four bytes
    pass


class string(type):
    pass
