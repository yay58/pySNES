from unittest import TestCase
from pynes.tests.uint16_spec import Uint16Spec
from pynes.tests.base import MetaNESTest


class PythonUint16Test(Uint16Spec, TestCase):
    pass


class PyNESUint16Test(PythonUint16Test, metaclass=MetaNESTest):
    pass
