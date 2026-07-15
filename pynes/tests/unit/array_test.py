from unittest import TestCase
from pynes.tests.array_spec import ArraySpec
from pynes.tests.base import MetaNESTest


class PythonArrayTest(ArraySpec, TestCase):
    pass


class PyNESArrayTest(PythonArrayTest, metaclass=MetaNESTest):
    pass
