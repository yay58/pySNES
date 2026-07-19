from unittest import TestCase

from neslib.font import CHR_BANK_SIZE, GLYPHS, TILE_SIZE, font_chr, glyph_tile
from neslib.library import lib as neslib
from pynes.cart import Cart
from pynes.tests.mixins.demos import get_demo_filename

PRG_SIZE = 16384
HEADER_SIZE = 16


def build_demo_rom(filename):
    with open(get_demo_filename(filename)) as f:
        source = f.read()
    cart = Cart(libraries=[neslib], chr_banks=1, chr_data=font_chr())
    return cart.to_nes(source)


def build_hello_rom():
    return build_demo_rom('hello.py')


class HelloRomTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = build_hello_rom()

    def test_ines_header(self):
        self.assertEqual(self.rom[:4], b'NES\x1a')
        self.assertEqual(self.rom[4], 1)  # 1x 16KB PRG
        self.assertEqual(self.rom[5], 1)  # 1x 8KB CHR

    def test_rom_size(self):
        self.assertEqual(len(self.rom), HEADER_SIZE + PRG_SIZE + CHR_BANK_SIZE)

    def test_reset_vector_points_into_prg(self):
        # vectors live at the end of PRG ($FFFA-$FFFF)
        vectors = self.rom[HEADER_SIZE + PRG_SIZE - 6 : HEADER_SIZE + PRG_SIZE]
        reset_addr = vectors[2] | (vectors[3] << 8)
        self.assertGreaterEqual(reset_addr, 0xC000)
        self.assertLess(reset_addr, 0xFFFA)

    def test_font_in_chr_bank(self):
        chr_bank = self.rom[HEADER_SIZE + PRG_SIZE :]
        offset = ord('H') * TILE_SIZE
        self.assertEqual(
            chr_bank[offset : offset + TILE_SIZE], glyph_tile(GLYPHS['H'])
        )
