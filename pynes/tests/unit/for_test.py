from unittest import TestCase
from pynes.tests.for_spec import ForSpec
from pynes.tests.base import MetaNESTest


class PythonForTest(ForSpec, TestCase):
    pass


class PyNESForTest(PythonForTest, metaclass=MetaNESTest):
    pass
