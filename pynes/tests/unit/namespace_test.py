"""Function namespaces follow Python's own resolution order.

- names imported with `from neslib import x` bind exactly x (and
  `from neslib import x as y` binds y), so two libraries exporting
  the same name coexist through aliasing
- a function defined in the program shadows any library extern,
  exactly like a module-level def shadows an import in Python
- sources without imports keep the implicit binding of every
  library extern (the twin specs have no import lines)
"""

from unittest import TestCase

from neslib.library import lib
from pynes.cart import Cart


def compile_source(source):
    return Cart(libraries=[lib]).compile(source)


MAIN = '''
@reset
def main():
    %s

    while True:
        pass
'''


class ImplicitBindingTest(TestCase):
    """Without import lines every extern stays visible: the twin
    specs and generated test programs rely on it."""

    def test_all_externs_bound(self):
        asm = compile_source(MAIN % 'pal_col(0, 0x0F)')
        self.assertIn('JSR neslib__pal_col', asm)


class ImportBindingTest(TestCase):
    """With import lines, only the imported names are callable."""

    def test_imported_name_is_bound(self):
        asm = compile_source(
            'from neslib import pal_col\n' + MAIN % 'pal_col(0, 0x0F)'
        )
        self.assertIn('JSR neslib__pal_col', asm)

    def test_unimported_name_is_not_defined(self):
        with self.assertRaises(NameError):
            compile_source(
                'from neslib import pal_col\n' + MAIN % 'ppu_on_all()'
            )

    def test_alias_binds_the_new_name(self):
        asm = compile_source(
            'from neslib import pal_col as color\n' + MAIN % 'color(0, 0x0F)'
        )
        self.assertIn('JSR neslib__pal_col', asm)

    def test_alias_frees_the_original_name(self):
        with self.assertRaises(NameError):
            compile_source(
                'from neslib import pal_col as color\n'
                + MAIN % 'pal_col(0, 0x0F)'
            )

    def test_imported_const_func_is_bound(self):
        asm = compile_source(
            'from neslib import vram_adr, NTADR_A\n'
            + MAIN % 'vram_adr(NTADR_A(2, 2))'
        )
        self.assertIn('JSR neslib__vram_adr', asm)


class NamespacedLabelTest(TestCase):
    """Library functions own their namespace in the assembly: the
    label is <library>__<function>, so a user label can never collide
    with a library routine, nor two libraries with each other."""

    def test_routine_label_is_namespaced(self):
        asm = compile_source(MAIN % 'pal_col(0, 0x0F)')
        self.assertIn('neslib__pal_col:', asm)
        self.assertIn('JSR neslib__pal_col', asm)

    def test_internal_labels_are_namespaced(self):
        asm = compile_source(
            MAIN % "put_str(NTADR_A(2, 2), msg)"
            + "\nmsg = string('HI')\n"
            + 'from pynes.types import string\n'
        )
        self.assertIn('neslib__put_str_loop:', asm)
        self.assertNotIn('\nput_str_loop:', asm)


class ShadowingTest(TestCase):
    """A def in the program wins over a library extern, exactly like
    Python scoping."""

    def test_user_function_shadows_extern(self):
        asm = compile_source(
            '''
def ppu_on_all():
    var_marker = 42
    return var_marker

@reset
def main():
    var_x = ppu_on_all()

    while True:
        pass
'''
        )
        # the user function is called and its body is in the ROM
        self.assertIn('JSR ppu_on_all\n', asm)
        self.assertIn('LDA #42', asm)
        # the library runtime routine is not bundled
        self.assertNotIn('STA $2001', asm)
