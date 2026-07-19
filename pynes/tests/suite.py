"""Suite ROM builder: collect test cases into one cartridge.

Every case body runs on the NES with its asserts ON the cartridge,
printing 'NNN OK' or 'NNN FAIL' on its own line -- the whole test
suite visually checkable on a NES screen (or an emulator).

Expected values come from the CPython twin: each case body is
executed in Python first and the on-cart asserts compare the NES
variables against what CPython produced.
"""

import os
import textwrap
from unittest import TestCase

from neslib.font import font_chr
from neslib.library import lib as neslib
from pynes.cart import Cart
from pynes.tests.unit.fceux_runner import FCEUXRunner


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

    def __init__(self):
        self.cases = []

    def add_case(self, name, source, expect=None):
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
        exec(source, {}, env)  # nosec B102 - twin run of the case body
        return {
            name: value
            for name, value in env.items()
            if isinstance(value, int)
        }

    def _case_function(self, case):
        out = [f'def case_{case.number}():']
        body = textwrap.dedent(case.source).strip('\n')
        for line in body.splitlines():
            out.append(f'    {line}' if line.strip() else '')
        out.append('    var_suite_ok = 1')
        for name, value in sorted(case.expect.items()):
            out.append(f'    if {name} != {value}:')
            out.append('        var_suite_ok = 0')
        out.append('    return var_suite_ok')
        out.append('')
        out.append('')
        return out

    def _report(self, case):
        row = self.FIRST_ROW + case.number - 1
        return [
            f'    # {case.name}',
            f'    vram_adr(NTADR_A({self.NUMBER_COLUMN}, {row}))',
            f'    put_num({case.number})',
            f'    var_verdict = case_{case.number}()',
            '    if var_verdict:',
            f'        put_str(NTADR_A({self.OK_COLUMN}, {row}), ok)',
            '    else:',
            f'        put_str(NTADR_A({self.OK_COLUMN}, {row}), fail)',
        ]

    def python_source(self):
        out = [
            'from neslib import reset, pal_col, ppu_on_all, put_str, \\',
            '    put_num, vram_adr, NTADR_A',
            'from pynes.types import string',
            '',
            "ok = string('OK')",
            "fail = string('FAIL')",
            '',
            '',
        ]
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

    def case_row(self, case):
        return self.FIRST_ROW + case.number - 1


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
                row = cls.suite.case_row(case)
                base = 0x2000 + row * 32 + cls.suite.OK_COLUMN
                verdict = bytes(runner.ppu.vram[base : base + 2])
                if verdict != b'OK':
                    failures.append(f'{case.number:03d} {case.name}')
            if failures:
                raise AssertionError(
                    'cases failed on the cartridge: ' + ', '.join(failures)
                )
        finally:
            runner.close_fceux()
