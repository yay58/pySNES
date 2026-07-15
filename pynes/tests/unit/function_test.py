from unittest import TestCase
from pynes.tests.function_spec import FunctionSpec
from pynes.tests.base import MetaNESTest


class PythonFunctionTest(FunctionSpec, TestCase):
    pass


class PyNESFunctionTest(PythonFunctionTest, metaclass=MetaNESTest):
    pass
