"""Factorial demo specs: expressions as extern arguments
(put_num(factorial(5))) and runtime 16-bit arguments
(vram_adr(NTADR_A(12, line)) with a variable line).

Results are 8-bit: factorials beyond 5! wrap modulo 256, on the NES
and in the CPython twins alike.
"""

from unittest import TestCase

from pynes.tests.mixins.demos import (
    AbstractFactorialMultiline,
    AbstractFactorialOneLine,
    load_runner,
    text,
)


class FactorialDemoTest(AbstractFactorialOneLine, TestCase):
    demo_filename = 'factorial.py'


class Factorial1DemoTest(AbstractFactorialOneLine, TestCase):
    demo_filename = 'factorial_1.py'


class Factorial2DemoTest(AbstractFactorialOneLine, TestCase):
    demo_filename = 'factorial_2.py'


class Factorial4DemoTest(AbstractFactorialOneLine, TestCase):
    demo_filename = 'factorial_4.py'


# class Factorial5DemoTest(AbstractFactorialOneLine, TestCase):
#     demo_filename = 'factorial_5.py'

#     def get_factorial_factor(self):
#         return 8


class Factorial6DemoTest(AbstractFactorialMultiline, TestCase):
    demo_filename = 'factorial_6.py'


class Factorial7DemoTest(AbstractFactorialMultiline, TestCase):
    demo_filename = 'factorial_7.py'


class Factorial8DemoTest(AbstractFactorialMultiline, TestCase):
    demo_filename = 'factorial_8.py'
