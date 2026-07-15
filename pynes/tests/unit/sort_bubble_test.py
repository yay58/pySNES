from unittest import TestCase
from pynes.tests.sort_bubble_spec import SortBubbleSpec
from pynes.tests.base import MetaNESTest


class PythonSortBubbleTest(SortBubbleSpec, TestCase):
    pass


class PyNESSortBubbleTest(PythonSortBubbleTest, metaclass=MetaNESTest):
    pass
