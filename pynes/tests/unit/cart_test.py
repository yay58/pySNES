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


FUNCTION_SOURCE = '''
def double(n):
    return n + n

@reset
def main():
    var_a = double(21)
    vram_put(var_a)
'''


class CartFunctionTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(FUNCTION_SOURCE)

    def test_function_emitted_with_label(self):
        self.assertIn('double:', self.asm)
        self.assertIn('JSR double', self.asm)

    def test_function_args_statically_allocated(self):
        self.assertIn('double_n .rs 1', self.asm)
        self.assertIn('STA double_n', self.asm)

    def test_function_placed_after_entries(self):
        self.assertGreater(self.asm.index('double:'), self.asm.index('IRQ:'))

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


class CartConstFoldingTest(TestCase):
    def test_ntadr_a_folds_to_constant(self):
        asm = make_cart().compile(
            '''
@reset
def main():
    vram_adr(NTADR_A(10, 14))
'''
        )
        # 0x2000 | (14 << 5) | 10 = 0x21CA
        self.assertIn('LDX #33', asm)
        self.assertIn('LDA #202', asm)


PUT_STR_SOURCE = '''
hello = string('HI')

@reset
def main():
    put_str(NTADR_A(10, 14), hello)
    ppu_on_all()
'''


class CartPutStrTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(PUT_STR_SOURCE)

    def test_string_pointer_setup(self):
        self.assertIn('LDA #LOW(hello)', self.asm)
        self.assertIn('STA str_ptr', self.asm)
        self.assertIn('LDA #HIGH(hello)', self.asm)
        self.assertIn('STA str_ptr_hi', self.asm)
        self.assertIn('JSR put_str', self.asm)

    def test_zeropage_pointer_is_adjacent(self):
        # (indirect),Y requires str_ptr_hi right after str_ptr
        lines = self.asm.splitlines()
        lo = lines.index('str_ptr .rs 1')
        self.assertEqual(lines[lo + 1], 'str_ptr_hi .rs 1')

    def test_string_not_allocated_in_ram(self):
        self.assertNotIn('hello .rs', self.asm)
        self.assertIn('hello:', self.asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


DATA_SOURCE = '''
hello = string('HI!')
tiles = rom([1, 2, 3])
counter = uint8()
score = uint16()
lives = 3

@reset
def main():
    ppu_on_all()
'''


class CartDataTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(DATA_SOURCE)

    def test_string_in_rom(self):
        # ASCII bytes with a zero terminator ('H', 'I', '!', 0)
        self.assertIn('hello:', self.asm)
        self.assertIn('.db $48, $49, $21, $00', self.asm)

    def test_rom_array(self):
        self.assertIn('tiles:', self.asm)
        self.assertIn('.db $01, $02, $03', self.asm)

    def test_rom_data_placed_after_code(self):
        self.assertGreater(self.asm.index('hello:'), self.asm.index('RESET:'))

    def test_uint8_in_ram(self):
        self.assertIn('counter .rs 1', self.asm)

    def test_uint16_in_ram(self):
        self.assertIn('score .rs 2', self.asm)

    def test_constant_in_ram_with_init(self):
        self.assertIn('lives .rs 1', self.asm)
        # initialized in the reset preamble
        reset_code = self.asm[self.asm.index('RESET:') :]
        self.assertIn('LDA #3', reset_code)
        self.assertIn('STA lives', reset_code)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)
