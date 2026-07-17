"""Factorial demo specs: expressions as extern arguments
(put_num(factorial(5))) and runtime 16-bit arguments
(vram_adr(NTADR_A(12, line)) with a variable line).

Results are 8-bit: factorials beyond 5! wrap modulo 256, on the NES
and in the CPython twins alike.
"""

import os
import importlib
from unittest import TestCase

from pynes.tests.nes_runner import NESRunner

DEMOS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'demos'
)

def get_demo_filename(demo):
    return os.path.join(DEMOS_DIR, demo)

def load_runner(demo):
    with open(get_demo_filename(demo)) as f:
        runner = NESRunner(f.read())
    runner.run_reset()
    return runner

def text(runner, x, y, length):
    base = 0x2000 + y * 32 + x
    return bytes(runner.ppu.vram[base : base + length])


class FactorialOneLineSpec:

    def get_factorial_factor(self):
        raise NotImplementedError()

    def get_factorial_result(self):
        raise NotImplementedError()

    def when_factorial_demos_runs(self):
        raise NotImplementedError()
    
    def assert_text(self, x, y, expected):
        raise NotImplementedError()
    
    def assert_factorial_result(self, x, y):
        raise NotImplementedError()

    def test_label_draw(self):

        self.when_factorial_demos_runs()

        self.assert_text(12, 14, b'%d! = ' % self.get_factorial_factor())

    def test_result_printed_after_the_label(self):
        self.when_factorial_demos_runs()

        self.assert_factorial_result(17, 14)


class FactorialDemoTest(FactorialOneLineSpec, TestCase):
    demo_filename = 'factorial.py'

    def get_demo_filename(self):
        return self.demo_filename

    def get_factorial_factor(self):
        return 5

    def get_factorial_function(self):
        module_path = 'demos.' + self.get_demo_filename().replace('.py', '')
        function_name = 'factorial'
        try:
            module = importlib.import_module(module_path)
            func = getattr(module, function_name)
            return func
        except ModuleNotFoundError:
            print(f"Error: The module '{module_path}' could not be found.")
            raise
        except AttributeError:
            print(f"Error: The function '{function_name}' does not exist in '{module_path}'.")
            raise

    def get_factorial_result(self):
        func = self.get_factorial_function()
        return func(self.get_factorial_factor())

    def when_factorial_demos_runs(self):
        self.runner = load_runner(self.get_demo_filename())

    def assert_text(self, x, y, expected):
        self.assertEqual(text(self.runner, x, y, len(expected)), expected)

    def assert_factorial_result(self, x, y):
        self.assertEqual(text(self.runner, x, y, len(str(self.get_factorial_result()))), str(self.get_factorial_result()).encode())


class Factorial1DemoTest(FactorialDemoTest):
    demo_filename = 'factorial_1.py'


class Factorial2DemoTest(FactorialDemoTest):
    demo_filename = 'factorial_2.py'

class Factorial4DemoTest(FactorialDemoTest):
    demo_filename = 'factorial_4.py'

# class Factorial5DemoTest(FactorialDemoTest):
#     demo_filename = 'factorial_5.py'

#     def get_factorial_factor(self):
#         return 8


class CallArgumentSpecTest(TestCase):
    """factorial_4: the result of a user function call feeds put_num
    directly, without an intermediate variable."""

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner('factorial_4.py')

    def test_label_drawn(self):
        self.assertEqual(text(self.runner, 12, 14, 5), b'5! = ')

    def test_result_printed_after_the_label(self):
        self.assertEqual(text(self.runner, 17, 14, 3), b'120')


class RuntimeVramAdrSpecTest(TestCase):
    """factorial_6: every loop iteration computes a nametable address
    from a variable line before printing."""

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner('factorial_6.py')

    def expected(self):
        # the CPython twin of the demo's factorial, 8-bit wrapped
        def factorial(n):
            result = 1
            while n > 1:
                result = (result * n) & 0xFF
                n -= 1
            return result

        return [factorial(value) for value in range(5)]

    def test_every_line_shows_its_factorial(self):
        for value, result in enumerate(self.expected()):
            line = 10 + value
            self.assertEqual(
                text(self.runner, 12, line, 3),
                b'%03d' % result,
                f'line {line} (factorial({value}))',
            )


class GeneratorArgumentSpecTest(TestCase):
    """factorial_7 and factorial_8: a for loop consumes a generator
    taking a scalar argument, printing each yielded value on its own
    computed line."""

    def expected(self):
        # the CPython twin of the demos' generator, 8-bit wrapped
        # def factorial(n):
        #     result = 1
        #     while n > 1:
        #         result = (result * n) & 0xFF
        #         yield result
        #         n -= 1

        from demos.factorial_8 import factorial
        return list(factorial(5))

    def check(self, demo):
        runner = load_runner(demo)
        for i, result in enumerate(self.expected()):
            line = 10 + i
            self.assertEqual(
                text(runner, 12, line, 3),
                b'%03d' % result,
                f'{demo} line {line}',
            )

    def test_factorial_7_yields_after_the_decrement(self):
        self.check('factorial_7.py')

    def test_factorial_8_yields_before_the_decrement(self):
        self.check('factorial_8.py')
