from unittest import TestCase
from pynes.tests.bitwise_spec import BitwiseSpec
from pynes.tests.base import MetaNESTest


class PythonBitwiseTest(BitwiseSpec, TestCase):
    pass


class PyNESBitwiseTest(PythonBitwiseTest, metaclass=MetaNESTest):
    pass
