from unittest import TestCase

import neslib
from neslib.ppu import PPU


class NeslibPythonTest(TestCase):
    """Pure-Python behaviour of neslib against the PPU mock."""

    def setUp(self):
        neslib.ppu.reset()

    def test_ntadr_a(self):
        self.assertEqual(neslib.NTADR_A(0, 0), 0x2000)
        self.assertEqual(neslib.NTADR_A(2, 2), 0x2042)
        self.assertEqual(neslib.NTADR_A(31, 29), 0x23BF)

    def test_vram_adr(self):
        neslib.vram_adr(0x2042)
        self.assertEqual(neslib.ppu.addr, 0x2042)

    def test_vram_put_autoincrement(self):
        neslib.vram_adr(0x2042)
        neslib.vram_put(0x28)
        neslib.vram_put(0x29)
        self.assertEqual(neslib.ppu.vram[0x2042], 0x28)
        self.assertEqual(neslib.ppu.vram[0x2043], 0x29)
        self.assertEqual(neslib.ppu.addr, 0x2044)

    def test_pal_col(self):
        neslib.pal_col(1, 0x30)
        self.assertEqual(neslib.ppu.vram[0x3F01], 0x30)

    def test_pal_col_wraps_index(self):
        neslib.pal_col(33, 0x15)
        self.assertEqual(neslib.ppu.vram[0x3F01], 0x15)

    def test_ppu_on_all(self):
        neslib.ppu_on_all()
        self.assertTrue(neslib.ppu.rendering_enabled)

    def test_hello_world_nametable(self):
        text = 'HELLO, WORLD!'
        neslib.vram_adr(neslib.NTADR_A(2, 2))
        for char in text:
            neslib.vram_put(ord(char) - 0x20)

        base = neslib.NTADR_A(2, 2)
        for i, char in enumerate(text):
            self.assertEqual(neslib.ppu.vram[base + i], ord(char) - 0x20)

    def test_ppu_mock_is_isolated(self):
        other = PPU()
        neslib.vram_adr(0x2000)
        neslib.vram_put(1)
        self.assertEqual(other.vram[0x2000], 0)


class NeslibPutStrTest(TestCase):
    def setUp(self):
        neslib.ppu.reset()

    def test_put_str_writes_to_nametable(self):
        addr = neslib.NTADR_A(10, 14)
        neslib.put_str(addr, 'HI!')

        self.assertEqual(neslib.ppu.vram[addr], ord('H'))
        self.assertEqual(neslib.ppu.vram[addr + 1], ord('I'))
        self.assertEqual(neslib.ppu.vram[addr + 2], ord('!'))


class NeslibNmiTest(TestCase):
    def setUp(self):
        neslib.ppu.reset()

    def test_nmi_on_sets_ctrl_bit(self):
        self.assertFalse(neslib.ppu.nmi_enabled)
        neslib.nmi_on()
        self.assertTrue(neslib.ppu.nmi_enabled)

    def test_scroll_updates_position(self):
        neslib.scroll(0, 0)
        self.assertEqual(neslib.ppu.scroll, (0, 0))


class NeslibOamTest(TestCase):
    def setUp(self):
        neslib.ppu.reset()

    def test_oam_clear_hides_all_sprites(self):
        neslib.oam_clear()
        self.assertEqual(neslib.ppu.oam, bytearray(b'\xff' * 256))

    def test_oam_spr_sets_sprite_entry(self):
        neslib.oam_clear()
        neslib.oam_spr(100, 120, 1, 0, 0)

        self.assertEqual(neslib.ppu.oam[0], 120)  # y
        self.assertEqual(neslib.ppu.oam[1], 1)  # tile
        self.assertEqual(neslib.ppu.oam[2], 0)  # attributes
        self.assertEqual(neslib.ppu.oam[3], 100)  # x

    def test_oam_spr_second_sprite(self):
        neslib.oam_clear()
        neslib.oam_spr(10, 20, 2, 1, 1)

        self.assertEqual(neslib.ppu.oam[4], 20)
        self.assertEqual(neslib.ppu.oam[5], 2)
        self.assertEqual(neslib.ppu.oam[6], 1)
        self.assertEqual(neslib.ppu.oam[7], 10)

    def test_oam_spr_accepts_tile_art(self):
        # in CPython, tile() names hold the art; the mock keeps them
        neslib.oam_clear()
        art = ['#' * 8] * 8
        neslib.oam_spr(50, 60, art, 0, 3)
        self.assertEqual(neslib.ppu.oam_tiles[3], art)


class NeslibPutNumTest(TestCase):
    def setUp(self):
        neslib.ppu.reset()

    def test_put_num_writes_three_decimal_digits(self):
        addr = neslib.NTADR_A(5, 5)
        neslib.vram_adr(addr)
        neslib.put_num(120)

        self.assertEqual(neslib.ppu.vram[addr], ord('1'))
        self.assertEqual(neslib.ppu.vram[addr + 1], ord('2'))
        self.assertEqual(neslib.ppu.vram[addr + 2], ord('0'))

    def test_put_num16_writes_five_decimal_digits(self):
        addr = neslib.NTADR_A(5, 5)
        neslib.vram_adr(addr)
        neslib.put_num16(40320)

        self.assertEqual(neslib.ppu.vram[addr], ord('4'))
        self.assertEqual(neslib.ppu.vram[addr + 1], ord('0'))
        self.assertEqual(neslib.ppu.vram[addr + 2], ord('3'))
        self.assertEqual(neslib.ppu.vram[addr + 3], ord('2'))
        self.assertEqual(neslib.ppu.vram[addr + 4], ord('0'))

    def test_put_num_pads_with_leading_zeros(self):
        addr = neslib.NTADR_A(5, 5)
        neslib.vram_adr(addr)
        neslib.put_num(7)

        self.assertEqual(neslib.ppu.vram[addr], ord('0'))
        self.assertEqual(neslib.ppu.vram[addr + 1], ord('0'))
        self.assertEqual(neslib.ppu.vram[addr + 2], ord('7'))


class NeslibExternTest(TestCase):
    """Compile-time behaviour: neslib registers externs for the compiler."""

    def _translate(self, code):
        from pynes.translator import PythonTo6502
        from neslib.library import lib

        translator = PythonTo6502(libraries=[lib])
        return translator.translate(code)

    def test_vram_adr_constant(self):
        asm = self._translate('vram_adr(0x2042)')
        self.assertIn('LDX #32', asm)  # high byte 0x20
        self.assertIn('LDA #66', asm)  # low byte 0x42
        self.assertIn('JSR vram_adr', asm)

    def test_vram_put_constant(self):
        asm = self._translate('vram_put(65)')
        self.assertIn('LDA #65', asm)
        self.assertIn('JSR vram_put', asm)

    def test_vram_put_variable(self):
        asm = self._translate('var_a = 65\nvram_put(var_a)')
        self.assertIn('LDA var_a', asm)
        self.assertIn('JSR vram_put', asm)

    def test_pal_col(self):
        asm = self._translate('pal_col(1, 0x30)')
        self.assertIn('LDX #1', asm)
        self.assertIn('LDA #48', asm)
        self.assertIn('JSR pal_col', asm)

    def test_ppu_on_all(self):
        asm = self._translate('ppu_on_all()')
        self.assertIn('JSR ppu_on_all', asm)

    def test_runtime_defines_routines(self):
        from neslib.library import lib

        runtime = '\n'.join(lib.runtime_asm)
        for routine in ('vram_adr:', 'vram_put:', 'pal_col:', 'ppu_on_all:'):
            self.assertIn(routine, runtime)
        self.assertIn('RTS', runtime)
