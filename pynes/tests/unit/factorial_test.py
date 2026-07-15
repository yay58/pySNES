from unittest import TestCase
from pynes.tests.factorial_spec import FactorialSpec
from pynes.tests.base import MetaNESTest


class PythonFactorialTest(FactorialSpec, TestCase):
    pass


class PyNESFactorialTest(PythonFactorialTest, metaclass=MetaNESTest):
    pass
