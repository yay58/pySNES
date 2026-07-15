from unittest import TestCase

from pynes.chr import TILE_SIZE, encode_stage, encode_tile


class EncodeStageTest(TestCase):
    def test_column_major_layout(self):
        rows = ['#..', '.#.']
        data = encode_stage(rows, {'#': 5})

        self.assertEqual(len(data), 3 * 30)
        # column 0: 28 empty rows, then '#' (row 28) and '.' (row 29)
        self.assertEqual(data[28], 5)
        self.assertEqual(data[29], 0)
        # column 1: '.' at row 28, '#' at row 29
        self.assertEqual(data[30 + 28], 0)
        self.assertEqual(data[30 + 29], 5)
        # column 2 is empty
        self.assertEqual(data[60:90], bytes(30))

    def test_rows_anchor_to_the_bottom(self):
        data = encode_stage(['#'], {'#': 1})
        self.assertEqual(data[:29], bytes(29))
        self.assertEqual(data[29], 1)

    def test_uneven_rows_rejected(self):
        with self.assertRaises(ValueError):
            encode_stage(['##', '#'], {'#': 1})

    def test_too_many_rows_rejected(self):
        with self.assertRaises(ValueError):
            encode_stage(['#'] * 31, {'#': 1})


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
