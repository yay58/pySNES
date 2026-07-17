import os
import importlib

from pynes.tests.nes_runner import NESRunner
from pynes.tests.factorial_demo_spec import FactorialOneLineSpec


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


class AbstractFactorialOneLine(FactorialOneLineSpec):
    demo_filename = None

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
            print(
                f"Error: The function '{function_name}' "
                f"does not exist in '{module_path}'."
            )
            raise

    def get_factorial_result(self):
        func = self.get_factorial_function()
        return func(self.get_factorial_factor())

    def when_factorial_demos_runs(self):
        self.runner = load_runner(self.get_demo_filename())

    def assert_text(self, x, y, expected):
        self.assertEqual(text(self.runner, x, y, len(expected)), expected)

    def assert_factorial_result(self, x, y):
        self.assertEqual(
            text(self.runner, x, y, len(str(self.get_factorial_result()))),
            str(self.get_factorial_result()).encode(),
        )
