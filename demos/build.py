"""Build all demos into .nes ROMs: python demos/build.py"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neslib.font import font_chr  # noqa: E402
from neslib.library import lib as neslib  # noqa: E402
from pynes.cart import Cart  # noqa: E402

DEMOS_DIR = os.path.dirname(os.path.abspath(__file__))
DEMOS = [
    'hello.py',
    'hello_1.py',
    'hello_2.py',
    'factorial.py',
    'factorial_1.py',
    'factorial_2.py',
    'factorial_3.py',
    'factorial_4.py',
    'factorial_6.py',
    'factorial_7.py',
    'factorial_8.py',
    'sorter_bubble.py',
    'sorter_bubble_1.py',
    'sorter_bubble_2.py',
    'sorter_bubble_3.py',
    'sorter_quicksort.py',
    'sorter_insertion.py',
    'sorter_bubble_animated.py',
    'sorter_generator.py',
    'sorter_generator_1.py',
    'sprite.py',
    'stage.py',
    'scrolling.py',
    'scrolling_level.py',
    'walking.py',
]


def build(filename):
    with open(os.path.join(DEMOS_DIR, filename)) as f:
        source = f.read()
    cart = Cart(libraries=[neslib], chr_banks=1, chr_data=font_chr())
    rom = cart.to_nes(source)
    rom_path = os.path.join(DEMOS_DIR, filename.replace('.py', '.nes'))
    with open(rom_path, 'wb') as f:
        f.write(rom)
    print(f'{filename} -> {rom_path} ({len(rom)} bytes)')


if __name__ == '__main__':
    for demo in DEMOS:
        build(demo)
