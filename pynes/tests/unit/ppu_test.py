from unittest import TestCase

from neslib.ppu import PPU, STATUS_VBLANK


class PPURegisterTest(TestCase):
    def setUp(self):
        self.ppu = PPU()

    def test_ctrl_and_mask(self):
        self.ppu.write_register(0x2000, 0x80)
        self.ppu.write_register(0x2001, 0x1E)
        self.assertTrue(self.ppu.nmi_enabled)
        self.assertTrue(self.ppu.rendering_enabled)

    def test_addr_latch_and_vram_write(self):
        self.ppu.write_register(0x2006, 0x21)
        self.ppu.write_register(0x2006, 0x08)
        self.ppu.write_register(0x2007, 0x41)
        self.ppu.write_register(0x2007, 0x42)

        self.assertEqual(self.ppu.vram[0x2108], 0x41)
        self.assertEqual(self.ppu.vram[0x2109], 0x42)

    def test_vertical_increment_mode(self):
        self.ppu.write_register(0x2000, 0x04)
        self.ppu.write_register(0x2006, 0x20)
        self.ppu.write_register(0x2006, 0x00)
        self.ppu.write_register(0x2007, 1)
        self.ppu.write_register(0x2007, 2)

        self.assertEqual(self.ppu.vram[0x2000], 1)
        self.assertEqual(self.ppu.vram[0x2020], 2)

    def test_scroll_latch(self):
        self.ppu.write_register(0x2005, 100)
        self.ppu.write_register(0x2005, 0)
        self.assertEqual(self.ppu.scroll, (100, 0))

    def test_status_read_reports_vblank_and_clears_latch(self):
        self.ppu.write_register(0x2006, 0x21)  # half-written latch
        status = self.ppu.read_register(0x2002)

        self.assertEqual(status, STATUS_VBLANK)
        self.ppu.write_register(0x2005, 5)
        self.ppu.write_register(0x2005, 0)
        self.assertEqual(self.ppu.scroll, (5, 0))

    def test_oam_writes(self):
        self.ppu.write_register(0x2003, 0)
        self.ppu.write_register(0x2004, 120)
        self.ppu.write_register(0x2004, 1)
        self.assertEqual(self.ppu.oam[0], 120)
        self.assertEqual(self.ppu.oam[1], 1)


class PadTest(TestCase):
    def setUp(self):
        from neslib.pad import Pad

        self.pad = Pad()

    def _poll(self):
        """The pad_poll protocol: strobe, then 8 reads, A first."""
        self.pad.write(1)
        self.pad.write(0)
        state = 0
        for _ in range(8):
            state = ((state << 1) | self.pad.read()) & 0xFF
        return state

    def test_buttons_shift_out_a_first(self):
        from neslib import PAD_A, PAD_RIGHT

        self.pad.state = PAD_A | PAD_RIGHT
        self.assertEqual(self._poll(), PAD_A | PAD_RIGHT)

    def test_strobe_high_repeats_a(self):
        from neslib import PAD_A

        self.pad.state = PAD_A
        self.pad.write(1)
        self.assertEqual(self.pad.read(), 1)
        self.assertEqual(self.pad.read(), 1)

    def test_reads_past_eight_return_one(self):
        self.pad.state = 0
        self.assertEqual(self._poll(), 0)
        self.assertEqual(self.pad.read(), 1)
