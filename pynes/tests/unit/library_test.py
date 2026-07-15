from unittest import TestCase

from pynes.library import Library
from pynes.translator import PythonTo6502


class LibraryContractTest(TestCase):
    """The library contract: externs, runtime asm and entry points."""

    def test_extern_registration(self):
        lib = Library('mylib')

        @lib.extern
        def beep(translator, args):
            translator.output.append('JSR beep')

        self.assertIn('beep', lib.externs)

    def test_extern_registration_with_name(self):
        lib = Library('mylib')

        @lib.extern(name='boop')
        def anything(translator, args):
            translator.output.append('JSR boop')

        self.assertIn('boop', lib.externs)

    def test_runtime_registration(self):
        lib = Library('mylib')
        lib.runtime('beep:\n  RTS')
        self.assertIn('beep:\n  RTS', lib.runtime_asm)

    def test_translator_emits_extern_call(self):
        lib = Library('mylib')

        @lib.extern
        def beep(translator, args):
            translator.output.append('JSR beep')

        translator = PythonTo6502(libraries=[lib])
        asm = translator.translate('beep()')
        self.assertIn('JSR beep', asm)

    def test_extern_receives_call_arguments(self):
        lib = Library('mylib')
        seen = {}

        @lib.extern
        def beep(translator, args):
            seen['count'] = len(args)
            translator.output.append('JSR beep')

        translator = PythonTo6502(libraries=[lib])
        translator.translate('beep(1, 2)')
        self.assertEqual(seen['count'], 2)

    def test_unknown_call_raises(self):
        translator = PythonTo6502()
        with self.assertRaises(NotImplementedError):
            translator.translate('unknown_function()')

    def test_multiple_libraries(self):
        lib_a = Library('a')
        lib_b = Library('b')

        @lib_a.extern
        def beep(translator, args):
            translator.output.append('JSR beep')

        @lib_b.extern
        def boop(translator, args):
            translator.output.append('JSR boop')

        translator = PythonTo6502(libraries=[lib_a, lib_b])
        asm = translator.translate('beep()\nboop()')
        self.assertIn('JSR beep', asm)
        self.assertIn('JSR boop', asm)

    def test_argument_loading_helpers(self):
        import ast

        translator = PythonTo6502()
        translator.load_arg8(ast.parse('65').body[0].value)
        self.assertIn('LDA #65', translator.output)

        translator = PythonTo6502()
        translator.load_arg16(ast.parse('0x2042').body[0].value)
        self.assertIn('LDX #32', translator.output)
        self.assertIn('LDA #66', translator.output)
