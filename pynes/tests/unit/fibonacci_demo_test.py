"""Fibonacci demo specs: the same feature ladder as the factorial
demos (inline loop, function call as argument, generator task,
enumerate), checked against the CPython twin of each demo."""

from unittest import TestCase

from pynes.tests.mixins.demos import load_runner, text


class FibonacciOneLineSpec:

    def expected(self):
        def fibonacci(n):
            a, b = 0, 1
            while n > 0:
                a, b = b, a + b
                n -= 1
            return a

        return fibonacci(10)

    def setUpRunner(self, demo):
        self.runner = load_runner(demo)

    def test_label_drawn(self):
        self.setUpRunner(self.demo_filename)
        self.assertEqual(text(self.runner, 10, 14, 9), b'FIB 10 = ')

    def test_result_printed_after_the_label(self):
        self.setUpRunner(self.demo_filename)
        self.assertEqual(
            text(self.runner, 19, 14, 3), b'%03d' % self.expected()
        )


class FibonacciMultilineSpec:

    def expected(self):
        def fibonacci(n):
            a, b = 0, 1
            while n > 0:
                a, b = b, a + b
                yield a
                n -= 1

        return list(fibonacci(8))

    def test_each_line_shows_its_fibonacci(self):
        runner = load_runner(self.demo_filename)
        for i, value in enumerate(self.expected()):
            line = 10 + i
            self.assertEqual(
                text(runner, 12, line, 3),
                b'%03d' % value,
                f'{self.demo_filename} line {line} (fib({i + 1}))',
            )


class FibonacciDemoTest(FibonacciOneLineSpec, TestCase):
    demo_filename = 'fibonacci.py'


class Fibonacci1DemoTest(FibonacciOneLineSpec, TestCase):
    demo_filename = 'fibonacci_1.py'


class Fibonacci2DemoTest(FibonacciMultilineSpec, TestCase):
    demo_filename = 'fibonacci_2.py'


class Fibonacci3DemoTest(FibonacciMultilineSpec, TestCase):
    demo_filename = 'fibonacci_3.py'
