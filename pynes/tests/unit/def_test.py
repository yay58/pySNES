from unittest import TestCase
from pynes.tests.def_spec import DefSpec
from pynes.tests.base import MetaNESTest


class PythonDefTest(DefSpec, TestCase):
    pass


class PyNESDefTest(PythonDefTest, metaclass=MetaNESTest):
    pass
