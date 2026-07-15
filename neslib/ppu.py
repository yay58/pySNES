MASK_BG = 0b00001000
MASK_SPR = 0b00010000
MASK_BG_LEFT = 0b00000010
MASK_SPR_LEFT = 0b00000100
MASK_ON_ALL = MASK_BG | MASK_SPR | MASK_BG_LEFT | MASK_SPR_LEFT


class PPU:
    """Minimal PPU state mock used by the pure-Python neslib
    implementation, so game specs can run and be asserted in CPython."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.vram = bytearray(0x4000)
        self.addr = 0
        self.mask = 0

    @property
    def rendering_enabled(self):
        return (self.mask & MASK_ON_ALL) == MASK_ON_ALL
