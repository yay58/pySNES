from unittest import TestCase
from pynes.tests.sort_selection_spec import SortSelectionSpec
from pynes.tests.base import MetaNESTest


class PythonSortSelectionTest(SortSelectionSpec, TestCase):
    pass


class PyNESSortSelectionTest(PythonSortSelectionTest, metaclass=MetaNESTest):
    pass
