"""Pure-Python implementation of the neslib API.

This lets game code and specs run unmodified in CPython against the PPU
mock, while `neslib.library` provides the compile-time definitions used
by the pyNES compiler to generate real 6502 code.
"""

from neslib.ppu import PPU, MASK_ON_ALL, CTRL_NMI

ppu = PPU()


def NTADR_A(x, y):
    """Nametable A address for tile coordinate (x, y)."""
    return 0x2000 | ((y & 0x1F) << 5) | (x & 0x1F)


def vram_adr(addr):
    ppu.addr = addr & 0x3FFF


def vram_put(value):
    ppu.vram[ppu.addr] = value & 0xFF
    ppu.addr = (ppu.addr + 1) & 0x3FFF


def pal_col(index, color):
    ppu.vram[0x3F00 + (index & 0x1F)] = color & 0xFF


def ppu_on_all():
    ppu.mask |= MASK_ON_ALL


def nmi_on():
    """Enable the NMI (vblank) interrupt."""
    ppu.ctrl |= CTRL_NMI


def scroll(x, y):
    """Set the background scroll position (also resets the internal
    latch clobbered by VRAM writes during NMI)."""
    ppu.scroll = (x, y)


def oam_clear():
    """Hide all sprites (move them below the visible screen)."""
    ppu.oam = bytearray(b'\xff' * 256)
    ppu.oam_tiles = {}


def oam_spr(x, y, tile, attr, sprite_id):
    """Set one sprite entry in the shadow OAM."""
    base = (sprite_id & 0x3F) * 4
    ppu.oam[base] = y & 0xFF
    ppu.oam[base + 1] = tile & 0xFF if isinstance(tile, int) else 0
    ppu.oam[base + 2] = attr & 0xFF
    ppu.oam[base + 3] = x & 0xFF
    ppu.oam_tiles[sprite_id] = tile


def oam_dma():
    """Copy the shadow OAM to the PPU (a no-op in the mock, where the
    shadow is the live OAM)."""


def put_str(addr, text):
    """Write a zero-terminated string at a nametable address."""
    vram_adr(addr)
    for char in text:
        vram_put(ord(char))


def put_num(value):
    """Write a number as three decimal digits (zero padded) at the
    current VRAM address."""
    for char in f'{value:03d}':
        vram_put(ord(char))


def put_num16(value):
    """Write a 16-bit number as five decimal digits (zero padded) at
    the current VRAM address."""
    for char in f'{value:05d}':
        vram_put(ord(char))


def reset(func):
    """Entry point decorator: marks the RESET handler."""
    func.__pynes_entry__ = 'reset'
    return func


def nmi(func):
    """Entry point decorator: marks the NMI (vblank) handler."""
    func.__pynes_entry__ = 'nmi'
    return func


def irq(func):
    """Entry point decorator: marks the IRQ handler."""
    func.__pynes_entry__ = 'irq'
    return func
