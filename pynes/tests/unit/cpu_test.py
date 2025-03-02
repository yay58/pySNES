from unittest import TestCase
from pynes.tests.cpu_spec import CPUSpec
from pynes.tests.base import MetaNESTest


class PythonCPUTest(CPUSpec, TestCase):
    pass


class PyNESCPUTest(PythonCPUTest, metaclass=MetaNESTest):
    pass
