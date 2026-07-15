from unittest import TestCase

from nesasm.compiler import lexical, syntax

from pynes.cart import Cart


HELLO_SOURCE = '''
@reset
def main():
    pal_col(1, 0x30)
    vram_adr(0x2042)
    vram_put(0x28)
    ppu_on_all()

@nmi
def render():
    pass
'''


def make_cart():
    from neslib.library import lib

    return Cart(libraries=[lib])


class CartTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(HELLO_SOURCE)

    def test_ines_header_directives(self):
        self.assertIn('.inesprg 1', self.asm)
        self.assertIn('.ineschr', self.asm)
        self.assertIn('.inesmap 0', self.asm)
        self.assertIn('.inesmir 1', self.asm)

    def test_reset_entry_point(self):
        self.assertIn('RESET:', self.asm)
        # standard init preamble
        self.assertIn('SEI', self.asm)
        self.assertIn('CLD', self.asm)
        self.assertIn('TXS', self.asm)

    def test_nmi_entry_point(self):
        self.assertIn('NMI:', self.asm)
        self.assertIn('RTI', self.asm)

    def test_vectors(self):
        self.assertIn('.org $FFFA', self.asm)
        self.assertIn('.dw NMI', self.asm)
        self.assertIn('.dw RESET', self.asm)
        self.assertIn('.dw IRQ', self.asm)

    def test_user_code_compiled(self):
        self.assertIn('JSR pal_col', self.asm)
        self.assertIn('JSR vram_adr', self.asm)
        self.assertIn('JSR vram_put', self.asm)
        self.assertIn('JSR ppu_on_all', self.asm)

    def test_runtime_linked(self):
        self.assertIn('vram_adr:', self.asm)
        self.assertIn('vram_put:', self.asm)
        self.assertIn('pal_col:', self.asm)
        self.assertIn('ppu_on_all:', self.asm)

    def test_asm_is_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


class CartDefaultsTest(TestCase):
    def test_missing_nmi_gets_stub(self):
        asm = make_cart().compile(
            '''
@reset
def main():
    ppu_on_all()
'''
        )
        self.assertIn('NMI:', asm)
        self.assertIn('.dw NMI', asm)

    def test_missing_reset_raises(self):
        with self.assertRaises(ValueError):
            make_cart().compile(
                '''
@nmi
def render():
    pass
'''
            )

    def test_variables_get_addresses(self):
        asm = make_cart().compile(
            '''
@reset
def main():
    var_a = 1
    vram_put(var_a)
'''
        )
        self.assertIn('.rsset', asm)
        self.assertIn('var_a .rs 1', asm)
