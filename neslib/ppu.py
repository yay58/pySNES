MASK_BG = 0b00001000
MASK_SPR = 0b00010000
MASK_BG_LEFT = 0b00000010
MASK_SPR_LEFT = 0b00000100
MASK_ON_ALL = MASK_BG | MASK_SPR | MASK_BG_LEFT | MASK_SPR_LEFT
CTRL_NMI = 0b10000000


class PPU:
    """Minimal PPU state mock used by the pure-Python neslib
    implementation, so game specs can run and be asserted in CPython."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.vram = bytearray(0x4000)
        self.addr = 0
        self.mask = 0
        self.ctrl = 0
        self.scroll = (0, 0)
        # shadow OAM: 64 sprites x 4 bytes (y, tile, attr, x)
        self.oam = bytearray(b'\xff' * 256)
        # tile objects per sprite id (mock keeps them abstract; the
        # compiler substitutes tile names with CHR indexes)
        self.oam_tiles = {}

    @property
    def rendering_enabled(self):
        return (self.mask & MASK_ON_ALL) == MASK_ON_ALL

    @property
    def nmi_enabled(self):
        return bool(self.ctrl & CTRL_NMI)
