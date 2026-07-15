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


class CartPutNumTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(
            '''
@reset
def main():
    var_n = 120
    put_num(var_n)
'''
        )

    def test_put_num_call(self):
        self.assertIn('LDA var_n', self.asm)
        self.assertIn('JSR put_num', self.asm)

    def test_runtime_linked(self):
        self.assertIn('put_num:', self.asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


class CartPutNum16Test(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(
            '''
var_big = uint16()

@reset
def main():
    var_big = 40320
    put_num16(var_big)
'''
        )

    def test_uint16_assign(self):
        self.assertIn('STA var_big', self.asm)
        self.assertIn('STA var_big__hi', self.asm)

    def test_put_num16_call(self):
        self.assertIn('STA num_lo', self.asm)
        self.assertIn('STA num_hi', self.asm)
        self.assertIn('JSR put_num16', self.asm)

    def test_runtime_linked(self):
        self.assertIn('put_num16:', self.asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


class CartAnnotatedDeclarationTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(
            '''
score: uint16 = 40320
lives: uint8 = 3

@reset
def main():
    put_num16(score)
'''
        )

    def test_uint16_annotation_allocates_pair(self):
        lines = self.asm.splitlines()
        lo = lines.index('score .rs 1')
        self.assertEqual(lines[lo + 1], 'score__hi .rs 1')

    def test_uint16_initialized_16bit(self):
        reset_code = self.asm[self.asm.index('RESET:') :]
        # 40320 = 0x9D80 -> lo 128, hi 157
        self.assertIn('LDA #128', reset_code)
        self.assertIn('STA score', reset_code)
        self.assertIn('LDA #157', reset_code)
        self.assertIn('STA score__hi', reset_code)

    def test_uint8_annotation(self):
        self.assertIn('lives .rs 1', self.asm)
        reset_code = self.asm[self.asm.index('RESET:') :]
        self.assertIn('LDA #3', reset_code)
        self.assertIn('STA lives', reset_code)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


class CartNmiAnimationTest(TestCase):
    def setUp(self):
        self.asm = make_cart().compile(
            '''
@reset
def main():
    var_i = 0
    nmi_on()
    ppu_on_all()

@nmi
def frame():
    var_i += 1
    scroll(0, 0)
'''
        )

    def test_nmi_on_call(self):
        self.assertIn('JSR nmi_on', self.asm)
        self.assertIn('nmi_on:', self.asm)

    def test_scroll_call(self):
        self.assertIn('JSR scroll', self.asm)
        self.assertIn('scroll:', self.asm)

    def test_nmi_body_compiled(self):
        nmi_code = self.asm[self.asm.index('NMI:') :]
        self.assertIn('INC var_i', nmi_code)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


SPRITE_SOURCE = '''
ball = tile([
    '..####..',
    '.######.',
    '########',
    '########',
    '########',
    '########',
    '.######.',
    '..####..',
])

@reset
def main():
    oam_clear()
    oam_spr(100, 120, ball, 0, 0)
    oam_dma()
    ppu_on_all()
'''


class CartSpriteTest(TestCase):
    def setUp(self):
        from neslib.library import lib

        self.cart = Cart(libraries=[lib], chr_banks=1, chr_data=bytes(8192))
        self.asm = self.cart.compile(SPRITE_SOURCE)

    def test_tile_name_becomes_constant_index(self):
        # first declared tile gets CHR index 1
        self.assertIn('LDA #1', self.asm)

    def test_oam_spr_writes_shadow_page(self):
        self.assertIn('STA $0200', self.asm)  # y
        self.assertIn('STA $0201', self.asm)  # tile
        self.assertIn('STA $0202', self.asm)  # attributes
        self.assertIn('STA $0203', self.asm)  # x

    def test_oam_runtime_linked(self):
        self.assertIn('oam_clear:', self.asm)
        self.assertIn('oam_dma:', self.asm)
        self.assertIn('STA $4014', self.asm)

    def test_tile_encoded_into_chr_bank(self):
        # tile 1 -> CHR offset 16: first row of the ball is $3C
        chr_section = self.asm[self.asm.index('.bank 2') :]
        self.assertIn('$3C, $7E, $FF, $FF, $FF, $FF, $7E, $3C', chr_section)

    def test_tile_not_allocated_in_ram(self):
        self.assertNotIn('ball .rs', self.asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


STAGE_SOURCE = '''
block = tile([
    '########',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '########',
])

level = stage(
    [
        '#...' + '.' * 124,
        '#' * 128,
    ],
    {'#': block},
)

@reset
def main():
    var_col = 0
    while var_col < 64:
        stage_column(level, var_col)
        var_col += 1
    ppu_on_all()
    nmi_on()

@nmi
def frame():
    scroll_x(0, 0)
'''


class CartStageTest(TestCase):
    def setUp(self):
        from neslib.library import lib

        self.cart = Cart(libraries=[lib], chr_banks=1, chr_data=bytes(8192))
        self.asm = self.cart.compile(STAGE_SOURCE)

    def _level_data(self):
        start = self.asm.index('level:')
        end = self.asm.index('.bank', start)
        return self.asm[start:end]

    def test_stage_data_emitted_column_major(self):
        # column 0 has '#' (tile 1) at rows 28 and 29
        data_section = self._level_data()
        data = [
            int(byte.strip().lstrip('$'), 16)
            for line in data_section.splitlines()
            if line.startswith('.db')
            for byte in line[4:].split(',')
        ]
        self.assertEqual(data[28], 1)
        self.assertEqual(data[29], 1)
        # column 1 has '#' only at row 29 (the ground row)
        self.assertEqual(data[30 + 28], 0)
        self.assertEqual(data[30 + 29], 1)

    def test_stage_data_is_chunked(self):
        # 128 columns x 30 bytes = 3840 bytes -> 240 lines of 16
        data_section = self._level_data()
        lines = [
            line
            for line in data_section.splitlines()
            if line.startswith('.db')
        ]
        self.assertEqual(len(lines), 240)

    def test_stage_column_extern(self):
        self.assertIn('LDA #LOW(level)', self.asm)
        self.assertIn('LDA #HIGH(level)', self.asm)
        self.assertIn('JSR stage_col', self.asm)

    def test_scroll_x_extern(self):
        self.assertIn('JSR scroll_x', self.asm)

    def test_runtime_linked(self):
        self.assertIn('stage_col:', self.asm)
        self.assertIn('scroll_x:', self.asm)

    def test_vertical_mirroring(self):
        self.assertIn('.inesmir 1', self.asm)

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
        # two adjacent one-byte labels (no label arithmetic in nesasm)
        lines = self.asm.splitlines()
        lo = lines.index('score .rs 1')
        self.assertEqual(lines[lo + 1], 'score__hi .rs 1')

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
