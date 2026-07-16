"""Pure-Python implementation of the neslib API.

This lets game code and specs run unmodified in CPython against the PPU
mock, while `neslib.library` provides the compile-time definitions used
by the pyNES compiler to generate real 6502 code.
"""

from neslib.ppu import PPU, MASK_ON_ALL, CTRL_NMI
from neslib.pad import Pad

ppu = PPU()
pad = Pad()

# controller buttons, in shift-out order (A first)
PAD_A = 0x80
PAD_B = 0x40
PAD_SELECT = 0x20
PAD_START = 0x10
PAD_UP = 0x08
PAD_DOWN = 0x04
PAD_LEFT = 0x02
PAD_RIGHT = 0x01


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


_tasks = {}


def step(task):
    """Resume a generator task: run it until its next yield. Returns
    1 while the task is alive, 0 once it has finished. On the NES the
    task compiles to a state machine; here it is a real generator."""
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
    """Read the first controller: one byte with A in bit 7 down to
    Right in bit 0."""
    return pad.state & 0xFF


def scroll_x(x, nt):
    """Set the horizontal camera: fine x scroll plus the nametable
    select bit (camera = nt*256 + x)."""
    ppu.scroll = (x, 0)
    ppu.ctrl = (ppu.ctrl & ~0x03) | (nt & 1)


def stage_column(level, col):
    """Upload one 30-tile stage column to its nametable position.
    Columns wrap over the two physical nametables."""
    rows = level['rows']
    pad = 30 - len(rows)
    pcol = col & 63
    base = 0x2000 if pcol < 32 else 0x2400
    x = pcol & 31
    for row in range(30):
        char = rows[row - pad][col] if row >= pad else '.'
        ppu.vram[base + row * 32 + x] = 0 if char == '.' else 1


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
