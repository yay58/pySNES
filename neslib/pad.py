class Pad:
    """Controller model: button state plus the $4016 strobe/shift
    register protocol, so compiled code polling the hardware sees the
    same buttons as the pure-Python twin."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 0
        self.strobe = False
        self.index = 0

    def write(self, value):
        """$4016 write: strobe high reloads the shift register;
        strobe low starts shifting buttons out."""
        if value & 1:
            self.strobe = True
        else:
            self.strobe = False
            self.index = 0

    def read(self):
        """$4016 read: one button per read, A first (bit 7 of state).
        After all 8 buttons, official controllers return 1."""
        if self.strobe:
            return (self.state >> 7) & 1
        if self.index >= 8:
            return 1
        bit = (self.state >> (7 - self.index)) & 1
        self.index += 1
        return bit
