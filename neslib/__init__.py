"""Pure-Python implementation of the neslib API.

This lets game code and specs run unmodified in CPython against the PPU
mock, while `neslib.library` provides the compile-time definitions used
by the pyNES compiler to generate real 6502 code.
"""

from neslib.ppu import PPU, MASK_ON_ALL

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


def put_str(addr, text):
    """Write a zero-terminated string at a nametable address."""
    vram_adr(addr)
    for char in text:
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
