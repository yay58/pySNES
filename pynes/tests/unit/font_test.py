from unittest import TestCase

from neslib.font import (
    CHR_BANK_SIZE,
    GLYPHS,
    TILE_SIZE,
    font_chr,
    glyph_tile,
)


class FontTest(TestCase):
    def test_chr_bank_size(self):
        self.assertEqual(len(font_chr()), CHR_BANK_SIZE)

    def test_tiles_at_ascii_codes(self):
        bank = font_chr()
        offset = ord('A') * TILE_SIZE
        self.assertEqual(
            bank[offset : offset + TILE_SIZE], glyph_tile(GLYPHS['A'])
        )

    def test_glyph_shape(self):
        # every glyph must be 7 rows of 5 columns
        for char, art in GLYPHS.items():
            self.assertEqual(len(art), 7, f'glyph {char!r}')
            for line in art:
                self.assertEqual(len(line), 5, f'glyph {char!r}')

    def test_tile_encoding_roundtrip(self):
        # decode plane 0 of 'H' back into ASCII art
        tile = glyph_tile(GLYPHS['H'])
        art = []
        for byte in tile[:7]:
            line = ''
            for i in range(5):
                bit = 0x80 >> (i + 1)
                line += '#' if byte & bit else '.'
            art.append(line)
        self.assertEqual(art, GLYPHS['H'])

    def test_second_plane_is_empty(self):
        # monochrome font: color index 1 only
        tile = glyph_tile(GLYPHS['A'])
        self.assertEqual(tile[8:], bytes(8))

    def test_space_tile_is_blank(self):
        self.assertEqual(glyph_tile(GLYPHS[' ']), bytes(16))

    def test_demo_glyphs_available(self):
        for char in 'HELLO WORLD! FACTORIAL SORT 0123456789':
            self.assertIn(char, GLYPHS)
