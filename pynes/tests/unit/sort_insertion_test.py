from unittest import TestCase
from pynes.tests.sort_insertion_spec import SortInsertionSpec
from pynes.tests.base import MetaNESTest


class PythonSortInsertionTest(SortInsertionSpec, TestCase):
    pass


class PyNESSortInsertionTest(PythonSortInsertionTest, metaclass=MetaNESTest):
    pass
