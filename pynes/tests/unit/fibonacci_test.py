from unittest import TestCase
from pynes.tests.fibonacci_spec import FibonacciSpec
from pynes.tests.base import MetaNESTest


class PythonFibonacciTest(FibonacciSpec, TestCase):
    pass


class PyNESFibonacciTest(PythonFibonacciTest, metaclass=MetaNESTest):
    pass
