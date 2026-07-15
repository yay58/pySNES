from neslib import reset, pal_col, ppu_on_all, vram_adr, vram_put, NTADR_A
from pynes.types import tile

block = tile([
    '########',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '########',
])


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # blocks: white

    # ground: two full rows at the bottom of the screen
    vram_adr(NTADR_A(0, 26))
    for var_i in range(64):
        vram_put(block)

    # a floating platform
    vram_adr(NTADR_A(12, 20))
    for var_i in range(8):
        vram_put(block)

    ppu_on_all()

    while True:
        pass
