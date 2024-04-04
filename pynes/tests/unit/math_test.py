from unittest import TestCase
from pynes.tests.math_spec import MathSpec
from pynes.tests.base import MetaNESTest


class PythonMathTest(MathSpec, TestCase):
    pass


class PyNESMathTest(PythonMathTest, metaclass=MetaNESTest):
    pass
