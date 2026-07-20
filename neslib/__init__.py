"""Pure-Python implementation of the neslib API.

This lets game code and specs run unmodified in CPython against the PPU
mock, while `neslib.library` provides the compile-time definitions used
by the pyNES compiler to generate real 6502 code.
"""

from sneslib.ppu import PPU, MASK_ON_ALL, CTRL_NMI
from sneslib.pad import Pad

ppu = PPU()
pad = Pad()

# SNES Controller Buttons in hardware shift-out order (16-bit masks)
# Left-shifted into a 16-bit variable as they arrive from $4016
PAD_B      = 0x8000  # 1st bit out
PAD_Y      = 0x4000  # 2nd bit out
PAD_SELECT = 0x2000  # 3rd bit out
PAD_START  = 0x1000  # 4th bit out
PAD_UP     = 0x800  # 5th bit out
PAD_DOWN   = 0x400  # 6th bit out
PAD_LEFT   = 0x200  # 7th bit out
PAD_RIGHT  = 0x100  # 8th bit out
PAD_A      = 0x80  # 9th bit out
PAD_X      = 0x40  # 10th bit out  <-- Your missing value
PAD_L      = 0x20  # 11th bit out
PAD_R      = 0x10  # 12th bit out


def BG_ADR(x, y, bg_base_addr):
    """Calculates the VRAM word address for a tile coordinate (x, y) on SNES.
    Assumes a standard 32x32 tile map layout."""
    return bg_base_addr + ((y & 0x1F) << 5) + (x & 0x1F)


def vram_adr(addr):
    # SNES VRAM expands up to 0xFFFF (16-bit word addressing)
    ppu.addr = addr & 0xFFFF


def vram_put(value):
    # SNES VRAM stores 16-bit words (Tile ID + Attributes)
    ppu.vram[ppu.addr] = value & 0xFFFF
    ppu.addr = (ppu.addr + 1) & 0xFFFF


def pal_col(palette_index, color_index, color_15bit):
    """SNES CGRAM (Palette RAM) holds 256 colors, each 15-bit BGR (0-32767)."""
    cgram_addr = (palette_index << 4) + (color_index & 0x0F)
    ppu.cgram[cgram_addr] = color_15bit & 0x7FFF


def ppu_on_all():
    # SNES uses Screen Screen Designator registers ($212C/$212D) to enable layers
    ppu.main_screen |= MainScreen_BG1 | MainScreen_OBJ


def nmi_on():
    """Enable NMI (vblank) via SNES register $4200."""
    ppu.nmitimen |= 0x80


def scroll(bg_id, x, y):
    """Set the background scroll position for a specific SNES BG layer (1 to 4).
    SNES scroll registers require two writes (low byte, then high byte)."""
    ppu.bg_scroll[bg_id] = (x & 0x3FF, y & 0x3FF)


_tasks = {}


def step(task):
    """Resume a generator task: run it until its next yield."""
    if task not in _tasks:
        _tasks[task] = task()
    gen = _tasks[task]
    if gen is None:
        return 0
    try:
        next(gen)
        return 1
    except StopIteration:
        _tasks[task] = None
        return 0


def reset_task(task):
    """Rewind a generator task to its beginning."""
    _tasks.pop(task, None)


def pad_poll():
    """Read the first controller: returns a 16-bit integer for SNES."""
    return pad.state & 0xFFFF


def stage_column(level, col, bg_base_addr):
    """Upload one 32-tile stage column to the SNES tilemap.
    SNES standard vertical screen fits 28 or 32 tiles depending on mode."""
    rows = level['rows']
    pcol = col & 63
    # Standard SNES 64x32 map stepping
    base = bg_base_addr if pcol < 32 else bg_base_addr + 0x0400
    x = pcol & 31
    for row in range(32):
        if row < len(rows):
            char = rows[row][col]
            # In SNES, VRAM values contain tile index AND attributes (palette, priority)
            ppu.vram[base + row * 32 + x] = 0x0000 if char == '.' else 0x0001


def oam_clear():
    """Hide all 128 SNES sprites by moving them off-screen."""
    # SNES OAM is split into 512 bytes (main data) + 32 bytes (high table for sizes/X bits)
    ppu.oam = bytearray(b'\xe0' * 512)  # Y=224 moves sprites below standard 224p screen
    ppu.oam_high = bytearray(b'\x00' * 32)


def oam_spr(x, y, tile, attr, sprite_id):
    """Set one sprite entry in the SNES OAM (Main Table)."""
    base = (sprite_id & 0x7F) * 4
    ppu.oam[base] = x & 0xFF
    ppu.oam[base + 1] = y & 0xFF
    ppu.oam[base + 2] = tile & 0xFF
    ppu.oam[base + 3] = attr & 0xFF  # Flipping, Palette, Priority, and Name Table bits


def put_str(addr, text):
    """Write a string to SNES VRAM (each character tile uses 16 bits)."""
    vram_adr(addr)
    for char in text:
        vram_put(ord(char))  # Missing attributes defaults to palette 0, priority 0


def reset(func):
    return func


def nmi(func):
    return func


def irq(func):
    """Entry point decorator: marks the IRQ handler."""
    func.__pynes_entry__ = 'irq'
    return func
