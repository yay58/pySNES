from unittest import TestCase

from pynes.tests.mixins.demos import (
    AbstractFactorialFCEUXOneLine,
)

class FactorialDemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial.py'


class Factorial1DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_1.py'


class Factorial2DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_2.py'


class Factorial4DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_4.py'


class Factorial5DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_5.py'
