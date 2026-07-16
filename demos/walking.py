from neslib import (
    reset,
    nmi,
    nmi_on,
    pal_col,
    ppu_on_all,
    pad_poll,
    stage_column,
    scroll_x,
    oam_clear,
    oam_spr,
    oam_dma,
    PAD_RIGHT,
)
from pynes.types import tile, stage

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

# the same 4-nametable level as scrolling_level, with the digits
# 1-4 marking each screen -- but here the player walks through it
level = stage(
    [
        '.' * 13
        + '..#..'
        + '.' * 27
        + '.###.'
        + '.' * 27
        + '.###.'
        + '.' * 27
        + '...#.'
        + '.' * 14,
        '.' * 13
        + '.##..'
        + '.' * 27
        + '#...#'
        + '.' * 27
        + '#...#'
        + '.' * 27
        + '..##.'
        + '.' * 14,
        '.' * 13
        + '..#..'
        + '.' * 27
        + '....#'
        + '.' * 27
        + '....#'
        + '.' * 27
        + '.#.#.'
        + '.' * 14,
        '.' * 13
        + '..#..'
        + '.' * 27
        + '..##.'
        + '.' * 27
        + '..##.'
        + '.' * 27
        + '#..#.'
        + '.' * 14,
        '.' * 13
        + '..#..'
        + '.' * 27
        + '.#...'
        + '.' * 27
        + '....#'
        + '.' * 27
        + '#####'
        + '.' * 14,
        '.' * 13
        + '..#..'
        + '.' * 27
        + '#....'
        + '.' * 27
        + '#...#'
        + '.' * 27
        + '...#.'
        + '.' * 14,
        '.' * 13
        + '.###.'
        + '.' * 27
        + '#####'
        + '.' * 27
        + '.###.'
        + '.' * 27
        + '...#.'
        + '.' * 14,
        '.' * 128,
        '....########' + '.' * 104 + '########....',
        '.' * 128,
        '.' * 128,
        '.' * 128,
        '.' * 128,
        '.' * 128,
        '#' * 128,
        '#' * 128,
        '.' * 128,
        '.' * 128,
    ],
    {'#': block},
)


@reset
def main():

    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # blocks: white
    pal_col(17, 0x28)  # ball: yellow

    # draw the two visible nametables (columns 0..63)
    var_col = 0
    while var_col < 64:
        stage_column(level, var_col)
        var_col += 1

    # the ball stands on the ground, mid-screen
    oam_clear()
    oam_spr(120, 199, ball, 0, 0)

    var_x = 0  # fine scroll within the current nametable
    var_nt = 0  # current nametable (0..3): camera = nt*256 + x
    var_sub = 0  # pixels walked since the last column fetch
    var_pad = 0

    ppu_on_all()
    nmi_on()

    while True:
        pass


@nmi
def frame():

    oam_dma()
    var_pad = pad_poll()
    # holding Right walks the ball through the level (the camera
    # follows, 2 px per frame) until the end of the last nametable
    if var_pad & PAD_RIGHT:
        if var_nt < 3:
            var_x += 2
            if var_x == 0:
                var_nt += 1
            var_sub += 2
            if var_sub == 8:
                var_sub = 0
                if var_col < 128:
                    stage_column(level, var_col)
                    var_col += 1
    scroll_x(var_x, var_nt)
