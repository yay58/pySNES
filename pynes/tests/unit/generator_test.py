"""Generator task specs: the same yield-based code runs as a real
generator in CPython (via the neslib step() twin) and as a compiled
6502 state machine in the headless runner.
"""

from unittest import TestCase

import neslib
from pynes.tests.mixins.demos import load_runner


class StepTwinTest(TestCase):
    """The pure-Python step()/reset_task() behavior."""

    def setUp(self):
        self.trace = []

        def task():
            self.trace.append('a')
            yield
            self.trace.append('b')
            yield
            self.trace.append('c')

        self.task = task
        neslib.reset_task(task)

    def test_step_resumes_one_yield_at_a_time(self):
        self.assertEqual(neslib.step(self.task), 1)
        self.assertEqual(self.trace, ['a'])
        self.assertEqual(neslib.step(self.task), 1)
        self.assertEqual(self.trace, ['a', 'b'])

    def test_step_reports_finished(self):
        neslib.step(self.task)
        neslib.step(self.task)
        self.assertEqual(neslib.step(self.task), 0)
        self.assertEqual(self.trace, ['a', 'b', 'c'])
        # finished tasks stay finished
        self.assertEqual(neslib.step(self.task), 0)

    def test_reset_task_rewinds(self):
        neslib.step(self.task)
        neslib.reset_task(self.task)
        self.assertEqual(neslib.step(self.task), 1)
        self.assertEqual(self.trace, ['a', 'a'])


class GeneratorSpecTest(TestCase):
    """The compiled state machine, one frame per step."""

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner('sorter_generator.py')
        cls.runner.run_reset()

    def _row(self, y):
        base = 0x2000 + y * 32 + 13
        return bytes(v - 48 for v in self.runner.ppu.vram[base : base + 5])

    def test_01_unsorted_array_drawn(self):
        self.assertEqual(self._row(12), bytes([3, 1, 4, 2, 5]))

    def test_02_first_step_swaps_one_pair(self):
        self.runner.run_frames(1)
        self.assertEqual(self._row(16), bytes([1, 3, 4, 2, 5]))

    def test_03_second_step_compares_without_swapping(self):
        self.runner.run_frames(1)
        self.assertEqual(self._row(16), bytes([1, 3, 4, 2, 5]))

    def test_04_task_finishes_sorted(self):
        # 4x4 comparisons = 16 yields in total
        self.runner.run_frames(20)
        self.assertEqual(self._row(16), bytes([1, 2, 3, 4, 5]))
        # the original row is untouched
        self.assertEqual(self._row(12), bytes([3, 1, 4, 2, 5]))

    def test_05_finished_task_stays_stable(self):
        self.runner.run_frames(10)
        self.assertEqual(self._row(16), bytes([1, 2, 3, 4, 5]))


class ArrayParamSpecTest(TestCase):
    """sorter_bubble_3: the sort is a function receiving the array."""

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner('sorter_bubble_3.py')
        cls.runner.run_reset()

    def _row(self, y):
        base = 0x2000 + y * 32 + 13
        return bytes(v - 48 for v in self.runner.ppu.vram[base : base + 5])

    def test_unsorted_and_sorted_rows(self):
        self.assertEqual(self._row(12), bytes([3, 1, 4, 2, 5]))
        self.assertEqual(self._row(16), bytes([1, 2, 3, 4, 5]))


class ForOverGeneratorSpecTest(TestCase):
    """sorter_generator_1: a for loop consumes the generator, the
    loop variable receiving each yielded value."""

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner('sorter_generator_1.py')
        cls.runner.run_reset()

    def _text(self, x, y, length):
        base = 0x2000 + y * 32 + x
        return bytes(self.runner.ppu.vram[base : base + length])

    def test_array_is_sorted_through_the_parameter(self):
        self.assertEqual(self._text(13, 12, 5), b'31425')
        self.assertEqual(self._text(13, 16, 5), b'12345')

    def test_loop_counts_the_yields(self):
        # 4x4 comparisons: the for body ran 16 times
        self.assertEqual(self._text(13, 20, 3), b'016')

    def test_loop_variable_receives_the_yielded_value(self):
        # sorting 31425 takes 3 swaps: the last yield delivered 3
        self.assertEqual(self._text(17, 20, 3), b'003')

    def test_cpython_twin_agrees(self):
        # the same generator runs as plain Python: for over it gives
        # the identical step and swap counts
        def sort_steps(arr):
            var_swaps = 0
            for var_i in range(4):
                for var_j in range(4):
                    if arr[var_j] > arr[var_j + 1]:
                        arr[var_j], arr[var_j + 1] = (
                            arr[var_j + 1],
                            arr[var_j],
                        )
                        var_swaps += 1
                    yield var_swaps

        arr = [3, 1, 4, 2, 5]
        steps = 0
        for swaps in sort_steps(arr):
            steps += 1
        self.assertEqual(arr, [1, 2, 3, 4, 5])
        self.assertEqual(steps, 16)
        self.assertEqual(swaps, 3)
