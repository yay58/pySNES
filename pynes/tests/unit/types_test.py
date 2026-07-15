from unittest import TestCase

from pynes.types import uint8, uint16, string, rom


class TypesTest(TestCase):
    """Types must behave sensibly in pure Python so game code runs
    unmodified in CPython."""

    def test_uint8_default(self):
        self.assertEqual(uint8(), 0)

    def test_uint8_value(self):
        self.assertEqual(uint8(42), 42)

    def test_uint8_wraps(self):
        self.assertEqual(uint8(256), 0)
        self.assertEqual(uint8(300), 44)

    def test_uint16_default(self):
        self.assertEqual(uint16(), 0)

    def test_uint16_wraps(self):
        self.assertEqual(uint16(0x10001), 1)

    def test_string(self):
        self.assertEqual(string('HELLO'), 'HELLO')

    def test_rom(self):
        self.assertEqual(rom([1, 2, 3]), [1, 2, 3])
