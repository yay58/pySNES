from unittest import TestCase

from pynes.library import Library, NesFunction
from pynes.translator import PythonTo6502


class Beep(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR beep')

    def runtime_code(self):
        return 'beep:\n  RTS'


class Poke16(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg16(args[0])
        translator.output.append('JSR poke16')

    def runtime_code(self):
        return ''


class NesFunctionTest(TestCase):
    """A library function is one object holding both sides of the
    contract: caller_code emitted at the call site and runtime_code
    bundled into the ROM (template method pattern)."""

    def test_name_derived_from_class_name(self):
        class PpuOnAll(NesFunction):
            def caller_code(self, translator, args):
                pass

            def runtime_code(self):
                return ''

        self.assertEqual(Beep().name, 'beep')
        self.assertEqual(PpuOnAll().name, 'ppu_on_all')

    def test_caller_code_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            NesFunction().caller_code(None, [])

    def test_runtime_code_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            NesFunction().runtime_code()

    def test_registration_binds_both_sides(self):
        lib = Library('mylib')
        lib.function(Beep())
        self.assertIn('beep', lib.externs)
        self.assertIn('beep:\n  RTS', lib.runtime_asm)

    def test_inline_functions_register_no_runtime(self):
        class Nop(NesFunction):
            def caller_code(self, translator, args):
                translator.output.append('NOP')

            def runtime_code(self):
                return ''

        lib = Library('mylib')
        lib.function(Nop())
        self.assertIn('nop', lib.externs)
        self.assertEqual(lib.runtime_asm, [])

    def test_call_emits_caller_code(self):
        lib = Library('mylib')
        lib.function(Beep())
        translator = PythonTo6502(libraries=[lib])
        asm = translator.translate('beep()')
        self.assertIn('JSR beep', asm)


class ConstFunctionTest(TestCase):
    """Const functions are evaluated at compile time when all
    arguments are constants (e.g. NTADR_A)."""

    def test_const_registration(self):
        lib = Library('mylib')

        @lib.const
        def double(x):
            return x * 2

        self.assertIn('double', lib.const_funcs)
        self.assertEqual(lib.const_funcs['double'](21), 42)

    def test_const_folding_in_extern_args(self):
        lib = Library('mylib')

        @lib.const
        def addr(x, y):
            return 0x2000 | (y << 5) | x

        lib.function(Poke16())

        translator = PythonTo6502(libraries=[lib])
        asm = translator.translate('poke16(addr(10, 14))')
        # 0x2000 | (14 << 5) | 10 = 0x21CA -> high 0x21, low 0xCA
        self.assertIn('LDX #33', asm)
        self.assertIn('LDA #202', asm)
        self.assertIn('JSR poke16', asm)


class RuntimeConstCallTest(TestCase):
    """A const function called with one runtime argument expands to
    runtime address math that behaves exactly like the compile-time
    fold, including the masking of out-of-range tile coordinates."""

    def _translate(self, source):
        lib = Library('mylib')

        @lib.const
        def addr(x, y):
            # NTADR_A twin: tile coordinates are 5-bit fields
            return 0x2000 | ((y & 0x1F) << 5) | (x & 0x1F)

        lib.function(Poke16())

        translator = PythonTo6502(libraries=[lib])
        return translator.translate(source)

    def test_shift_add_against_the_folded_base(self):
        asm = self._translate('var_y = 14\npoke16(addr(10, var_y))')
        # base = addr(10, 0) = 0x200A: lo 10, hi 32; slope 32 = 5 shifts
        self.assertEqual(asm.count('ASL temp16_lo'), 5)
        self.assertEqual(asm.count('ROL temp16_hi'), 5)
        self.assertIn('ADC #10', asm)
        self.assertIn('ADC #32', asm)
        self.assertIn('JSR poke16', asm)

    def test_runtime_argument_masked_like_the_const_function(self):
        # addr masks y & 0x1F: y = 40 must wrap to row 8, exactly as
        # the compile-time fold would
        asm = self._translate('var_y = 40\npoke16(addr(10, var_y))')
        self.assertIn('AND #31', asm)

    def test_non_linear_functions_are_rejected(self):
        lib = Library('mylib')

        @lib.const
        def crooked(v):
            return v * v

        lib.function(Poke16())

        translator = PythonTo6502(libraries=[lib])
        with self.assertRaises(NotImplementedError):
            translator.translate('var_v = 3\npoke16(crooked(var_v))')


class LibraryContractTest(TestCase):
    """The library contract: externs, runtime asm and entry points."""

    def test_extern_registration(self):
        lib = Library('mylib')
        lib.function(Beep())
        self.assertIn('beep', lib.externs)

    def test_extern_registration_with_name_override(self):
        class Anything(NesFunction):
            name = 'boop'

            def caller_code(self, translator, args):
                translator.output.append('JSR boop')

            def runtime_code(self):
                return ''

        lib = Library('mylib')
        lib.function(Anything())
        self.assertIn('boop', lib.externs)

    def test_runtime_registration(self):
        lib = Library('mylib')
        lib.runtime('beep:\n  RTS')
        self.assertIn('beep:\n  RTS', lib.runtime_asm)

    def test_translator_emits_extern_call(self):
        lib = Library('mylib')
        lib.function(Beep())

        translator = PythonTo6502(libraries=[lib])
        asm = translator.translate('beep()')
        self.assertIn('JSR beep', asm)

    def test_extern_receives_call_arguments(self):
        lib = Library('mylib')
        seen = {}

        class Probe(Beep):
            def caller_code(self, translator, args):
                seen['count'] = len(args)
                super().caller_code(translator, args)

        lib.function(Probe())
        self.assertIn('probe', lib.externs)

        translator = PythonTo6502(libraries=[lib])
        translator.translate('probe(1, 2)')
        self.assertEqual(seen['count'], 2)

    def test_unknown_call_raises(self):
        translator = PythonTo6502()
        with self.assertRaises(NotImplementedError):
            translator.translate('unknown_function()')

    def test_multiple_libraries(self):
        lib_a = Library('a')
        lib_b = Library('b')

        class Boop(NesFunction):
            def caller_code(self, translator, args):
                translator.output.append('JSR boop')

            def runtime_code(self):
                return ''

        lib_a.function(Beep())
        lib_b.function(Boop())

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
