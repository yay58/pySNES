from neslib import (
    reset,
    nmi,
    nmi_on,
    scroll,
    pal_col,
    ppu_on_all,
    vram_adr,
    vram_put,
    NTADR_A,
)
from pynes.types import tile

block = tile(
    [
        '########',
        '#......#',
        '#......#',
        '#......#',
        '#......#',
        '#......#',
        '#......#',
        '########',
    ]
)


@reset
def main():
    global var_x

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

    var_x = 0

    ppu_on_all()
    nmi_on()

    while True:
        pass


@nmi
def frame():
    global var_x

    # one pixel per frame until the camera rests at x=100
    if var_x < 100:
        var_x += 1
        scroll(var_x, 0)
