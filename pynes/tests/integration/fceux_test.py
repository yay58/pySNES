"""Emulator-in-the-loop integration tests.

Runs built ROMs inside FCEUX with a Lua script that samples the
framebuffer, then asserts the exact number of lit pixels computed
from the bundled font glyphs. Skipped when FCEUX is not available.
"""

import os
import shutil
import subprocess  # nosec B404
import tempfile
import unittest
from unittest import TestCase

from neslib.font import GLYPHS
from pynes.tests.integration.rom_test import build_demo_rom

HERE = os.path.dirname(os.path.abspath(__file__))
LUA_SCRIPT = os.path.join(HERE, 'screen_check.lua')


def expected_lit_pixels(text):
    return sum(row.count('#') for c in text for row in GLYPHS[c])


def text_region(tile_x, tile_y, text):
    """Screen region (in pixels) of text drawn at a nametable tile."""
    x, y = tile_x * 8, tile_y * 8
    return (x, y, x + len(text) * 8 - 1, y + 7)


def char_cell(tile_x, tile_y, index):
    """Screen region of a single character cell."""
    x, y = (tile_x + index) * 8, tile_y * 8
    return (x, y, x + 7, y + 7)


def fceux_available():
    return shutil.which('fceux') is not None and (
        os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
    )


def run_screen_check(rom_bytes, regions, wait_frames=120):
    """Run a ROM in FCEUX, returning lit-pixel counts per region."""
    with tempfile.TemporaryDirectory() as tmp:
        rom_path = os.path.join(tmp, 'test.nes')
        result_path = os.path.join(tmp, 'result.txt')
        with open(rom_path, 'wb') as f:
            f.write(rom_bytes)
        env = dict(
            os.environ,
            RESULT_FILE=result_path,
            REGIONS=';'.join(
                ','.join(str(c) for c in region) for region in regions
            ),
            WAIT_FRAMES=str(wait_frames),
        )
        subprocess.run(  # nosec B603
            [shutil.which('fceux'), '--loadlua', LUA_SCRIPT, rom_path],
            env=env,
            timeout=60,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        results = {}
        with open(result_path) as f:
            for line in f:
                key, value = line.strip().split('=')
                results[key] = value
        return [int(count) for count in results['lit'].split(';')], results


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class HelloScreenTest(TestCase):
    def test_hello_world_is_rendered(self):
        rom = build_demo_rom('hello.py')
        regions = [text_region(10, 14, 'HELLO WORLD!'), (8, 8, 15, 15)]
        counts, results = run_screen_check(rom, regions)

        self.assertEqual(counts[0], expected_lit_pixels('HELLO WORLD!'))
        self.assertEqual(counts[1], 0)  # background is clean
        red, green, blue = (int(c) for c in results['bg'].split(','))
        self.assertLess(red + green + blue, 192)

    def test_hello_1_with_ntadr_a_matches(self):
        rom = build_demo_rom('hello_1.py')
        counts, _ = run_screen_check(
            rom, [text_region(10, 14, 'HELLO WORLD!')]
        )

        self.assertEqual(counts[0], expected_lit_pixels('HELLO WORLD!'))

    def test_hello_2_with_put_str_matches(self):
        rom = build_demo_rom('hello_2.py')
        counts, _ = run_screen_check(
            rom, [text_region(10, 14, 'HELLO WORLD!')]
        )

        self.assertEqual(counts[0], expected_lit_pixels('HELLO WORLD!'))


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class FactorialScreenTest(TestCase):
    def _check(self, demo):
        rom = build_demo_rom(demo)
        text = '5! = 120'
        regions = [
            text_region(12, 14, text),
            char_cell(12, 14, 5),  # '1'
            char_cell(12, 14, 6),  # '2'
            char_cell(12, 14, 7),  # '0'
        ]
        counts, _ = run_screen_check(rom, regions)

        self.assertEqual(counts[0], expected_lit_pixels(text))
        self.assertEqual(counts[1], expected_lit_pixels('1'))
        self.assertEqual(counts[2], expected_lit_pixels('2'))
        self.assertEqual(counts[3], expected_lit_pixels('0'))

    def test_factorial_result_is_rendered(self):
        self._check('factorial.py')

    def test_factorial_1_with_put_str_matches(self):
        self._check('factorial_1.py')

    def test_factorial_2_with_put_num_matches(self):
        self._check('factorial_2.py')

    def test_factorial_3_uint16_renders_40320(self):
        rom = build_demo_rom('factorial_3.py')
        text = '8! = 40320'
        regions = [text_region(11, 14, text)]
        regions += [char_cell(11, 14, 5 + i) for i in range(5)]
        counts, _ = run_screen_check(rom, regions)

        self.assertEqual(counts[0], expected_lit_pixels(text))
        for i, digit in enumerate('40320'):
            self.assertEqual(
                counts[1 + i],
                expected_lit_pixels(digit),
                f'digit {i} should be {digit!r}',
            )


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class SorterScreenTest(TestCase):
    def _check(self, demo):
        rom = build_demo_rom(demo)
        regions = [text_region(13, 12, '31425')]
        # each cell of the sorted row must contain the right digit
        regions += [char_cell(13, 16, i) for i in range(5)]
        counts, _ = run_screen_check(rom, regions)

        self.assertEqual(counts[0], expected_lit_pixels('31425'))
        for i, digit in enumerate('12345'):
            self.assertEqual(
                counts[1 + i],
                expected_lit_pixels(digit),
                f'cell {i} should show {digit!r}',
            )

    def test_bubble_sorted_row_is_rendered_in_order(self):
        self._check('sorter_bubble.py')

    def test_bubble_1_pythonic_matches(self):
        self._check('sorter_bubble_1.py')

    def test_bubble_2_tuple_swap_matches(self):
        self._check('sorter_bubble_2.py')

    def test_quicksort_matches(self):
        self._check('sorter_quicksort.py')

    def test_insertion_matches(self):
        self._check('sorter_insertion.py')

    def test_animated_bubble_settles_sorted(self):
        # one sort step per vblank: after 120 frames the working row
        # must have settled on the sorted result
        self._check('sorter_bubble_animated.py')


BALL_ART = [
    '..####..',
    '.######.',
    '########',
    '########',
    '########',
    '########',
    '.######.',
    '..####..',
]


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class SpriteScreenTest(TestCase):
    def test_sprite_is_rendered(self):
        rom = build_demo_rom('sprite.py')
        # OAM y is delayed by one scanline: sprite at y=120 shows at 121
        regions = [(100, 121, 107, 128), (8, 8, 15, 15)]
        counts, _ = run_screen_check(rom, regions)

        expected = sum(row.count('#') for row in BALL_ART)
        self.assertEqual(counts[0], expected)
        self.assertEqual(counts[1], 0)  # background is clean


BLOCK_PIXELS = 28  # outline block: 8+8 full rows + 6 rows of 2 pixels


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class StageScreenTest(TestCase):
    def test_stage_is_rendered(self):
        rom = build_demo_rom('stage.py')
        regions = [
            char_cell(0, 26, 0),  # ground, first tile
            char_cell(31, 27, 0),  # ground, last tile
            char_cell(12, 20, 0),  # platform, first tile
            char_cell(19, 20, 0),  # platform, last tile
            char_cell(12, 19, 0),  # above the platform: empty
            char_cell(20, 20, 0),  # right of the platform: empty
        ]
        counts, _ = run_screen_check(rom, regions)

        self.assertEqual(counts[0], BLOCK_PIXELS)
        self.assertEqual(counts[1], BLOCK_PIXELS)
        self.assertEqual(counts[2], BLOCK_PIXELS)
        self.assertEqual(counts[3], BLOCK_PIXELS)
        self.assertEqual(counts[4], 0)
        self.assertEqual(counts[5], 0)


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class ScrollingScreenTest(TestCase):
    def test_camera_rests_scrolled(self):
        rom = build_demo_rom('scrolling.py')
        # the camera scrolls one pixel per frame and rests at x=100,
        # so screen column p shows source column p+100
        regions = [
            # platform (source px 96-159) now shows at screen px -4..59:
            # cell x=2 spans two adjacent blocks, still 28 lit pixels
            char_cell(2, 20, 0),
            # where the platform was drawn: source px 196-203 is empty
            char_cell(12, 20, 0),
            # ground is a full row: still solid after the shift
            char_cell(0, 26, 0),
            # above the platform: still empty
            char_cell(2, 19, 0),
        ]
        counts, _ = run_screen_check(rom, regions)

        self.assertEqual(counts[0], BLOCK_PIXELS)
        self.assertEqual(counts[1], 0)
        self.assertEqual(counts[2], BLOCK_PIXELS)
        self.assertEqual(counts[3], 0)


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class ScrollingLevelScreenTest(TestCase):
    def test_camera_stops_at_the_end_of_the_level(self):
        rom = build_demo_rom('scrolling_level.py')
        # the camera advances 2 px/frame across 4 nametables and rests
        # at 768: the screen then shows source columns 96..127, where
        # the end platform sits at columns 116-123 (screen cells 20-27)
        regions = [
            char_cell(20, 20, 0),  # end platform, first block
            char_cell(27, 20, 0),  # end platform, last block
            char_cell(19, 20, 0),  # left of the platform: empty
            char_cell(20, 19, 0),  # above the platform: empty
            char_cell(0, 26, 0),  # ground, left edge
            char_cell(31, 27, 0),  # ground, right edge
            # the big '4' digit centered on the last nametable
            # (block cells 13-17, rows 12-18)
            char_cell(16, 12, 0),  # '...#.' top row: block
            char_cell(13, 12, 0),  # '...#.' top row: empty
            char_cell(13, 16, 0),  # '#####' middle bar: block
            char_cell(17, 16, 0),  # '#####' middle bar: block
        ]
        counts, _ = run_screen_check(rom, regions, wait_frames=450)

        self.assertEqual(counts[0], BLOCK_PIXELS)
        self.assertEqual(counts[1], BLOCK_PIXELS)
        self.assertEqual(counts[2], 0)
        self.assertEqual(counts[3], 0)
        self.assertEqual(counts[4], BLOCK_PIXELS)
        self.assertEqual(counts[5], BLOCK_PIXELS)
        self.assertEqual(counts[6], BLOCK_PIXELS)
        self.assertEqual(counts[7], 0)
        self.assertEqual(counts[8], BLOCK_PIXELS)
        self.assertEqual(counts[9], BLOCK_PIXELS)
