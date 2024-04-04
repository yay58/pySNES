from unittest import TestCase
from pynes.tests.if_spec import IfSpec
from pynes.tests.base import MetaNESTest


class PythonIfTest(IfSpec, TestCase):
    pass


class PyNESAssignTest(PythonIfTest, metaclass=MetaNESTest):
    pass
