"""Emulator-free controller specs: the walking demo runs headlessly
and buttons are injected per frame through the $4016 controller model.
"""

from unittest import TestCase

from neslib import PAD_LEFT, PAD_RIGHT
from pynes.tests.nes_runner import NESRunner
from pynes.tests.mixins.demos import get_demo_filename

BLOCK = 1  # first declared tile
BALL = 2  # second declared tile


class WalkingSpecTest(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(get_demo_filename('walking.py')) as f:
            cls.runner = NESRunner(f.read())
        cls.runner.run_reset()

    def test_01_ball_on_screen_and_camera_at_rest(self):
        self.runner.run_frames(10)  # no buttons held
        self.assertEqual(self.runner.ppu.scroll, (0, 0))
        # sprite 0 after DMA: y, tile, attr, x
        self.assertEqual(self.runner.ppu.oam[0], 199)
        self.assertEqual(self.runner.ppu.oam[1], BALL)
        self.assertEqual(self.runner.ppu.oam[3], 120)

    def test_02_holding_right_walks(self):
        self.runner.press(PAD_RIGHT)
        self.runner.run_frames(10)
        self.assertEqual(self.runner.ppu.scroll, (20, 0))

    def test_03_releasing_stops(self):
        self.runner.release()
        self.runner.run_frames(30)
        self.assertEqual(self.runner.ppu.scroll, (20, 0))

    def test_04_other_buttons_do_nothing(self):
        self.runner.press(PAD_LEFT)
        self.runner.run_frames(10)
        self.assertEqual(self.runner.ppu.scroll, (20, 0))

    def test_05_walking_streams_columns(self):
        # walk to camera 40: source column 68 replaced the start
        # platform at physical column 4
        self.runner.press(PAD_RIGHT)
        self.runner.run_frames(10)
        vram = self.runner.ppu.vram
        self.assertEqual(self.runner.ppu.scroll, (40, 0))
        self.assertEqual(vram[0x2000 + 20 * 32 + 4], 0)
        self.assertEqual(vram[0x2000 + 26 * 32 + 4], BLOCK)

    def test_06_walk_to_the_end_of_the_level(self):
        # camera 768 needs 364 more frames; walk longer to prove the
        # camera parks at the level end while Right is still held
        self.runner.run_frames(400)
        vram = self.runner.ppu.vram
        self.assertEqual(self.runner.ppu.scroll, (0, 0))
        self.assertEqual(self.runner.ppu.ctrl & 0x03, 1)
        # nametable B shows the digit '4' and the end platform
        self.assertEqual(vram[0x2400 + 16 * 32 + 13], BLOCK)
        self.assertEqual(vram[0x2400 + 20 * 32 + 27], BLOCK)
