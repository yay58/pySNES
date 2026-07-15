from unittest import TestCase
from pynes.tests.sort_quicksort_spec import SortQuicksortSpec
from pynes.tests.base import MetaNESTest


class PythonSortQuicksortTest(SortQuicksortSpec, TestCase):
    pass


class PyNESSortQuicksortTest(PythonSortQuicksortTest, metaclass=MetaNESTest):
    pass
