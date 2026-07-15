from unittest import TestCase

from pynes.chr import TILE_SIZE, encode_tile

BALL = [
    '..####..',
    '.######.',
    '########',
    '########',
    '########',
    '########',
    '.######.',
    '..####..',
]


class EncodeTileTest(TestCase):
    def test_tile_is_16_bytes(self):
        self.assertEqual(len(encode_tile(BALL)), TILE_SIZE)

    def test_plane0_matches_art(self):
        data = encode_tile(BALL)
        self.assertEqual(data[0], 0b00111100)
        self.assertEqual(data[1], 0b01111110)
        self.assertEqual(data[2], 0b11111111)
        self.assertEqual(data[7], 0b00111100)

    def test_plane1_is_empty(self):
        data = encode_tile(BALL)
        self.assertEqual(data[8:], bytes(8))

    def test_empty_art_encodes_blank(self):
        data = encode_tile(['........'] * 8)
        self.assertEqual(data, bytes(16))
