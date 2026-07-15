MASK_BG = 0b00001000
MASK_SPR = 0b00010000
MASK_BG_LEFT = 0b00000010
MASK_SPR_LEFT = 0b00000100
MASK_ON_ALL = MASK_BG | MASK_SPR | MASK_BG_LEFT | MASK_SPR_LEFT
CTRL_NMI = 0b10000000
CTRL_INC32 = 0b00000100
STATUS_VBLANK = 0b10000000


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
        # register-level state (shared $2005/$2006 write toggle)
        self.oam_addr = 0
        self.latch = None

    @property
    def rendering_enabled(self):
        return (self.mask & MASK_ON_ALL) == MASK_ON_ALL

    @property
    def nmi_enabled(self):
        return bool(self.ctrl & CTRL_NMI)

    def write_register(self, address, value):
        """Hardware-register write ($2000-$2007), as performed by
        compiled 6502 code running against this model."""
        register = 0x2000 + (address & 7)
        value &= 0xFF
        if register == 0x2000:
            self.ctrl = value
        elif register == 0x2001:
            self.mask = value
        elif register == 0x2003:
            self.oam_addr = value
        elif register == 0x2004:
            self.oam[self.oam_addr] = value
            self.oam_addr = (self.oam_addr + 1) & 0xFF
        elif register == 0x2005:
            if self.latch is None:
                self.latch = value
            else:
                self.scroll = (self.latch, value)
                self.latch = None
        elif register == 0x2006:
            if self.latch is None:
                self.latch = value
            else:
                self.addr = ((self.latch << 8) | value) & 0x3FFF
                self.latch = None
        elif register == 0x2007:
            self.vram[self.addr] = value
            step = 32 if self.ctrl & CTRL_INC32 else 1
            self.addr = (self.addr + step) & 0x3FFF

    def read_register(self, address):
        """Hardware-register read. $2002 reports vblank (the model is
        always in vblank, so wait loops finish) and clears the write
        toggle."""
        register = 0x2000 + (address & 7)
        if register == 0x2002:
            self.latch = None
            return STATUS_VBLANK
        return 0
