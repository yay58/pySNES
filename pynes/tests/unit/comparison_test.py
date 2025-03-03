import unittest
from pynes.tests.base import MetaNESTest


class PyNESComparisonTest(unittest.TestCase, metaclass=MetaNESTest):
    def test_equal_comparison(self):
        var_q = 1
        var_w = 1
        var_e = 0
        if var_q == var_w:
            var_e = 1

        self.assertEqual(var_q, 1)
        self.assertEqual(var_w, 1)
        self.assertEqual(var_e, 1)

    def test_not_equal_comparison(self):
        var_q = 1
        var_w = 2
        var_e = 0
        if var_q != var_w:
            var_e = 1

        self.assertEqual(var_q, 1)
        self.assertEqual(var_w, 2)
        self.assertEqual(var_e, 1)

    def test_less_than_comparison(self):
        var_q = 1
        var_w = 2
        var_e = 0
        if var_q < var_w:
            var_e = 1

        self.assertEqual(var_q, 1)
        self.assertEqual(var_w, 2)
        self.assertEqual(var_e, 1)

    def test_greater_than_comparison(self):
        var_q = 2
        var_w = 1
        var_e = 0
        if var_q > var_w:
            var_e = 1

        self.assertEqual(var_q, 2)
        self.assertEqual(var_w, 1)
        self.assertEqual(var_e, 1)

    def test_less_than_equal_comparison(self):
        var_q = 1
        var_w = 1
        var_e = 0
        if var_q <= var_w:
            var_e = 1

        self.assertEqual(var_q, 1)
        self.assertEqual(var_w, 1)
        self.assertEqual(var_e, 1)

    def test_greater_than_equal_comparison(self):
        var_q = 1
        var_w = 1
        var_e = 0
        if var_q >= var_w:
            var_e = 1

        self.assertEqual(var_q, 1)
        self.assertEqual(var_w, 1)
        self.assertEqual(var_e, 1)
