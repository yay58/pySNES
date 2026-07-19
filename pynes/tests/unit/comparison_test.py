from unittest import TestCase
from pynes.tests.comparison_spec import ComparisonSpec
from pynes.tests.base import MetaNESTest


class PythonComparisonTest(ComparisonSpec, TestCase):
    pass


class PyNESComparisonTest(PythonComparisonTest, metaclass=MetaNESTest):
    pass
