"""Suite ROM builder: collect test cases into one cartridge.

Every case body runs on the NES with its asserts ON the cartridge,
printing 'NNN OK' or 'NNN FAIL' on its own line -- the whole test
suite visually checkable on a NES screen (or an emulator).

Expected values come from the CPython twin: each case body is
executed in Python first and the on-cart asserts compare the NES
variables against what CPython produced.
"""

import ast
import inspect
import os
import textwrap
import unittest
from unittest import TestCase

from pynes.tests.base import CodeFilter

from neslib.font import font_chr
from neslib.library import lib as neslib
from pynes import types as pynes_types
from pynes.cart import Cart
from pynes.tests.unit.fceux_runner import FCEUXRunner


class RenameHelpers(ast.NodeTransformer):
    """Rename a case's helper functions (and every reference to
    them) so same-named helpers in different cases cannot clash in
    the shared module namespace."""

    def __init__(self, mapping):
        self.mapping = mapping

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.name = self.mapping.get(node.name, node.name)
        return node

    def visit_Name(self, node):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node


class SuiteCase:
    def __init__(self, number, name, source, expect):
        self.number = number
        self.name = name
        self.source = source
        self.expect = expect


class SuiteRom:
    OK_COLUMN = 6
    NUMBER_COLUMN = 2
    FIRST_ROW = 2
    # no scrolling (yet): when a column of verdicts fills the screen,
    # wrap to a second column
    ROWS_PER_COLUMN = 30 - FIRST_ROW
    COLUMN_WIDTH = 16
    MAX_CASES = 2 * ROWS_PER_COLUMN

    def __init__(self):
        self.cases = []

    def add_case(self, name, source, expect=None):
        if len(self.cases) >= self.MAX_CASES:
            raise NotImplementedError(
                f'suite screen is full ({self.MAX_CASES} cases): '
                'scrolling through results is not implemented yet'
            )
        if expect is None:
            expect = self._twin_expect(source)
        self.cases.append(
            SuiteCase(len(self.cases) + 1, name, source, expect)
        )

    @staticmethod
    def _twin_expect(source):
        """Run the case body in CPython and capture its variables:
        the twin defines what the cartridge must reproduce."""
        env = {}
        # the pynes declaration types behave as plain values in
        # CPython, so annotated case bodies run unmodified
        types = {
            name: getattr(pynes_types, name)
            for name in ('uint8', 'uint16', 'string', 'rom')
        }
        exec(source, types, env)  # nosec B102 - twin run of the case
        expect = {}
        for name, value in env.items():
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                expect[name] = value
            elif isinstance(value, list) and all(
                isinstance(item, int) and not isinstance(item, bool)
                for item in value
            ):
                expect[name] = value
        return expect

    @staticmethod
    def _split_case(case):
        """Separate helper functions defined in the case body from its
        statements: the compiler only supports module-level defs, so
        helpers are hoisted out of the generated case function, name
        mangled per case to keep the module namespace clash-free."""
        tree = ast.parse(textwrap.dedent(case.source))
        mapping = {
            node.name: f'case_{case.number}_{node.name}'
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }
        tree = RenameHelpers(mapping).visit(tree)
        helpers = [
            node for node in tree.body if isinstance(node, ast.FunctionDef)
        ]
        rest = [
            node
            for node in tree.body
            if not isinstance(node, ast.FunctionDef)
        ]
        return helpers, rest

    def _helper_functions(self):
        """Hoisted (mangled) helpers of every case."""
        return [
            ast.unparse(node)
            for case in self.cases
            for node in self._split_case(case)[0]
        ]

    def _case_function(self, case):
        out = [f'def case_{case.number}():']
        _, statements = self._split_case(case)
        for node in statements:
            for line in ast.unparse(node).splitlines():
                out.append(f'    {line}' if line.strip() else '')
        out.append('    var_suite_ok = 1')
        for name, value in sorted(case.expect.items()):
            if isinstance(value, list):
                for index, item in enumerate(value):
                    out.append(f'    if {name}[{index}] != {item}:')
                    out.append('        var_suite_ok = 0')
            else:
                out.append(f'    if {name} != {value}:')
                out.append('        var_suite_ok = 0')
        out.append('    return var_suite_ok')
        out.append('')
        out.append('')
        return out

    def case_position(self, case):
        """Screen position of a case verdict: (number_x, verdict_x,
        row), wrapping into a new column when rows run out."""
        index = case.number - 1
        column = index // self.ROWS_PER_COLUMN
        row = self.FIRST_ROW + index % self.ROWS_PER_COLUMN
        offset = column * self.COLUMN_WIDTH
        return self.NUMBER_COLUMN + offset, self.OK_COLUMN + offset, row

    def _report(self, case):
        number_x, verdict_x, row = self.case_position(case)
        return [
            f'    # {case.name}',
            f'    vram_adr(NTADR_A({number_x}, {row}))',
            f'    put_num({case.number})',
            f'    var_verdict = case_{case.number}()',
            '    if var_verdict:',
            f'        put_str(NTADR_A({verdict_x}, {row}), ok)',
            '    else:',
            f'        put_str(NTADR_A({verdict_x}, {row}), fail)',
        ]

    def python_source(self):
        out = [
            'from neslib import reset, pal_col, ppu_on_all, put_str, \\',
            '    put_num, vram_adr, NTADR_A',
            'from pynes.types import string, uint8, uint16',
            '',
            "ok = string('OK')",
            "fail = string('FAIL')",
            '',
            '',
        ]
        for source in self._helper_functions():
            out.append(source)
            out.append('')
            out.append('')
        for case in self.cases:
            out.extend(self._case_function(case))
        out.append('@reset')
        out.append('def main():')
        out.append('    pal_col(0, 0x0F)  # background: black')
        out.append('    pal_col(1, 0x30)  # text: white')
        out.append('')
        for case in self.cases:
            out.extend(self._report(case))
            out.append('')
        out.append('    ppu_on_all()')
        out.append('')
        out.append('    while True:')
        out.append('        pass')
        out.append('')
        return '\n'.join(out)

    def to_nes(self):
        cart = Cart(
            libraries=[neslib], chr_banks=1, chr_data=font_chr()
        )
        return cart.to_nes(self.python_source())

    def write_nes(self, path):
        """Build the suite cartridge and write it to path, ready to
        run on an emulator or real hardware."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        rom = self.to_nes()
        with open(path, 'wb') as f:
            f.write(rom)
        return path



class SuiteRomTestCase(TestCase):
    """Test cases that run ON the cartridge.

    Each test_* method gathers its case body with run_case(); after
    the last test, tearDownClass builds output/suite/<ClassName>.nes,
    boots it on FCEUX and checks that every case line reads OK.
    """

    # <project root>/output/suite/
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        '..',
        'output',
        'suite',
    )

    @classmethod
    def setUpClass(cls):
        cls.suite = SuiteRom()

    def run_case(self, source, expect=None):
        """Gather this test's case body (named after the test) into
        the class suite."""
        self.suite.add_case(self._testMethodName, source, expect)

    @classmethod
    def tearDownClass(cls):
        if not cls.suite.cases:
            return
        path = os.path.join(cls.output_dir, f'{cls.__name__}.nes')
        cls.suite.write_nes(path)
        cls._check_verdicts_on_fceux()

    @classmethod
    def _check_verdicts_on_fceux(cls):
        runner = FCEUXRunner(cls.suite.python_source())
        runner.start_fceux()
        try:
            runner.run_reset()
            failures = []
            for case in cls.suite.cases:
                _, verdict_x, row = cls.suite.case_position(case)
                base = 0x2000 + row * 32 + verdict_x
                verdict = bytes(runner.ppu.vram[base : base + 2])
                if verdict != b'OK':
                    failures.append(f'{case.number:03d} {case.name}')
            if failures:
                raise AssertionError(
                    'cases failed on the cartridge: ' + ', '.join(failures)
                )
        finally:
            runner.close_fceux()


def _gather_case(source):
    def test(self):
        self.run_case(source)

    return test


class MetaSuiteRomTest(type):
    """Lift a twin spec onto the cartridge: every test_* body has its
    asserts stripped (CodeFilter, as in MetaNESTest) and becomes a
    gathered suite case, so the same spec that runs on CPython and on
    the headless runner also runs with on-cart asserts on FCEUX.

    Tests listed in on_cart_skip are skipped with the given reason
    instead of gathered:

    Usage:
        class MathOnCartTest(SuiteRomTestCase, MathSpec,
                             metaclass=MetaSuiteRomTest):
            on_cart_skip = {'test_x': 'needs 16-bit comparisons'}
    """

    def __new__(mcs, name, bases, dct):
        klass = super().__new__(mcs, name, bases, dct)
        filter_code = CodeFilter()
        skip = dct.get('on_cart_skip', {})
        tests = [
            method_name
            for method_name in dir(klass)
            if method_name.startswith('test_')
            and callable(getattr(klass, method_name))
        ]
        for test in tests:
            if test in skip:
                setattr(klass, test, unittest.skip(skip[test])(lambda self: None))
                continue
            lines = inspect.getsourcelines(getattr(klass, test))[0]
            code = ''.join(line[4:] for line in lines)
            tree = filter_code.visit(ast.parse(code))
            ast.fix_missing_locations(tree)
            setattr(klass, test, _gather_case(ast.unparse(tree)))
        return klass
