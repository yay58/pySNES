from unittest import TestCase
from pynes.tests.sort_spec import SortSpec
from pynes.tests.base import MetaNESTest


class PythonSortTest(SortSpec, TestCase):
    pass


class PyNESSortTest(PythonSortTest, metaclass=MetaNESTest):
    pass
