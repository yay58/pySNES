from neslib import (
    reset,
    nmi,
    nmi_on,
    pal_col,
    ppu_on_all,
    stage_column,
    scroll_x,
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

# a level 4 nametables wide (128 columns): a big digit centered on
# each nametable (so the scroll progress 1..4 is visible), a platform
# at the start, another at the very end, and ground all the way
level = stage(
    [
        '.' * 13 + '..#..' + '.' * 27 + '.###.' + '.' * 27
        + '.###.' + '.' * 27 + '...#.' + '.' * 14,
        '.' * 13 + '.##..' + '.' * 27 + '#...#' + '.' * 27
        + '#...#' + '.' * 27 + '..##.' + '.' * 14,
        '.' * 13 + '..#..' + '.' * 27 + '....#' + '.' * 27
        + '....#' + '.' * 27 + '.#.#.' + '.' * 14,
        '.' * 13 + '..#..' + '.' * 27 + '..##.' + '.' * 27
        + '..##.' + '.' * 27 + '#..#.' + '.' * 14,
        '.' * 13 + '..#..' + '.' * 27 + '.#...' + '.' * 27
        + '....#' + '.' * 27 + '#####' + '.' * 14,
        '.' * 13 + '..#..' + '.' * 27 + '#....' + '.' * 27
        + '#...#' + '.' * 27 + '...#.' + '.' * 14,
        '.' * 13 + '.###.' + '.' * 27 + '#####' + '.' * 27
        + '.###.' + '.' * 27 + '...#.' + '.' * 14,
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

    # draw the two visible nametables (columns 0..63)
    var_col = 0
    while var_col < 64:
        stage_column(level, var_col)
        var_col += 1

    var_x = 0  # fine scroll within the current nametable
    var_nt = 0  # current nametable (0..3): camera = nt*256 + x
    var_sub = 0  # pixels scrolled since the last column fetch

    ppu_on_all()
    nmi_on()

    while True:
        pass


@nmi
def frame():
    # 2 px per frame; fetch one column ahead every 8 px; the camera
    # stops when it reaches the end of the level (nt=3, x=0)
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
