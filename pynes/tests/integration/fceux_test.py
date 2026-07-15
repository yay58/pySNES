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
    def test_factorial_result_is_rendered(self):
        rom = build_demo_rom('factorial.py')
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


@unittest.skipUnless(fceux_available(), 'fceux or display not available')
class SorterScreenTest(TestCase):
    def test_sorted_row_is_rendered_in_order(self):
        rom = build_demo_rom('sorter.py')
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
