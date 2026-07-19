"""Emulator-free scrolling specs.

The actual demo sources run headlessly (py65 + the neslib PPU model),
so scroll positions, nametable switches and column streaming are
asserted at exact frame counts -- something the FCEUX screen checks
cannot do deterministically.
"""

from unittest import TestCase

from pynes.tests.nes_runner import NESRunner
from pynes.tests.mixins.demos import get_demo_filename

BLOCK = 1  # first declared tile


def demo_source(filename):
    with open(get_demo_filename(filename)) as f:
        return f.read()


def cell(base, x, y):
    return base + y * 32 + x


class ScrollingSpecTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = NESRunner(demo_source('scrolling.py'))
        cls.runner.run_reset()

    def test_01_stage_drawn_before_scrolling(self):
        vram = self.runner.ppu.vram
        self.assertEqual(vram[cell(0x2000, 0, 26)], BLOCK)  # ground
        self.assertEqual(vram[cell(0x2000, 12, 20)], BLOCK)  # platform
        self.assertEqual(vram[cell(0x2000, 11, 20)], 0)
        self.assertEqual(self.runner.ppu.scroll, (0, 0))

    def test_02_camera_moves_one_pixel_per_frame(self):
        self.runner.run_frames(10)
        self.assertEqual(self.runner.ppu.scroll, (10, 0))

    def test_03_camera_rests_at_100(self):
        self.runner.run_frames(200)
        self.assertEqual(self.runner.ppu.scroll, (100, 0))


class ScrollingLevelSpecTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = NESRunner(demo_source('scrolling_level.py'))
        cls.runner.run_reset()

    def test_01_reset_draws_the_first_two_nametables(self):
        vram = self.runner.ppu.vram
        # digit '1' bottom row ('.###.') centered on nametable A
        self.assertEqual(vram[cell(0x2000, 14, 18)], BLOCK)
        self.assertEqual(vram[cell(0x2000, 13, 18)], 0)
        # digit '2' bottom row ('#####') centered on nametable B
        self.assertEqual(vram[cell(0x2400, 13, 18)], BLOCK)
        self.assertEqual(vram[cell(0x2400, 17, 18)], BLOCK)
        # start platform and ground
        self.assertEqual(vram[cell(0x2000, 4, 20)], BLOCK)
        self.assertEqual(vram[cell(0x2000, 0, 26)], BLOCK)
        self.assertEqual(self.runner.ppu.scroll, (0, 0))
        self.assertEqual(self.runner.ppu.ctrl & 0x03, 0)

    def test_02_columns_stream_in_behind_the_camera(self):
        # 20 frames at 2 px/frame = camera 40: source columns 64..68
        # have been streamed over physical columns 0..4, replacing the
        # start platform (source column 68 is empty at row 20)
        self.runner.run_frames(20)
        vram = self.runner.ppu.vram
        self.assertEqual(self.runner.ppu.scroll, (40, 0))
        self.assertEqual(vram[cell(0x2000, 4, 20)], 0)
        self.assertEqual(vram[cell(0x2000, 4, 26)], BLOCK)  # ground

    def test_03_camera_crosses_into_the_next_nametable(self):
        # up to frame 130: camera 260 -> nametable 1, fine x 4
        self.runner.run_frames(110)
        self.assertEqual(self.runner.ppu.scroll, (4, 0))
        self.assertEqual(self.runner.ppu.ctrl & 0x03, 1)

    def test_04_camera_stops_at_the_end_of_the_level(self):
        # 384 frames in total reach camera 768 (nt=3, x=0)
        self.runner.run_frames(300)
        vram = self.runner.ppu.vram
        self.assertEqual(self.runner.ppu.scroll, (0, 0))
        self.assertEqual(self.runner.ppu.ctrl & 0x03, 1)
        # the view is nametable B: digit '4' middle bar at row 16
        self.assertEqual(vram[cell(0x2400, 13, 16)], BLOCK)
        self.assertEqual(vram[cell(0x2400, 17, 16)], BLOCK)
        self.assertEqual(vram[cell(0x2400, 13, 12)], 0)
        # the end platform (source columns 116-123 -> B columns 20-27)
        self.assertEqual(vram[cell(0x2400, 20, 20)], BLOCK)
        self.assertEqual(vram[cell(0x2400, 27, 20)], BLOCK)

    def test_05_camera_stays_parked(self):
        self.runner.run_frames(50)
        self.assertEqual(self.runner.ppu.scroll, (0, 0))
        self.assertEqual(self.runner.ppu.ctrl & 0x03, 1)
