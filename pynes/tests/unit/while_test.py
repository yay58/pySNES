from unittest import TestCase
from pynes.tests.while_spec import WhileSpec
from pynes.tests.base import MetaNESTest


class PythonWhileTest(WhileSpec, TestCase):
    pass


class PyNESWhileTest(PythonWhileTest, metaclass=MetaNESTest):
    pass
