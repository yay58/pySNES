from unittest import TestCase
from pynes.tests.assign_spec import AssignSpec
from pynes.tests.base import MetaNESTest


class PythonAssignTest(AssignSpec, TestCase):
    pass


class PyNESAssignTest(PythonAssignTest, metaclass=MetaNESTest):
    pass
