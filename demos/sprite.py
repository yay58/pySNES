from neslib import (
    reset,
    pal_col,
    ppu_on_all,
    oam_clear,
    oam_spr,
    oam_dma,
)
from pynes.types import tile

ball = tile(
    [
        '..####..',
        '.######.',
        '########',
        '########',
        '########',
        '########',
        '.######.',
        '..####..',
    ]
)


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(17, 0x30)  # sprite: white

    oam_clear()
    oam_spr(100, 120, ball, 0, 0)
    oam_dma()

    ppu_on_all()

    while True:
        pass
