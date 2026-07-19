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
        # var_n is a local of main, mangled like any function local
        self.assertIn('LDA main_var_n', self.asm)
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
    global var_big
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
    global var_i
    var_i = 0
    nmi_on()
    ppu_on_all()

@nmi
def frame():
    global var_i
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


class CartFunctionScopeTest(TestCase):
    """Functions see the global context; unknown names are errors."""

    def _compile(self, source):
        from neslib.library import lib

        return Cart(libraries=[lib]).compile(source)

    def test_undefined_var_in_function_fails(self):
        with self.assertRaises(NameError) as ctx:
            self._compile(
                '''
def helper():
    var_x = var_never_assigned + 1

@reset
def main():
    helper()
'''
            )
        self.assertIn('var_never_assigned', str(ctx.exception))

    def test_undefined_var_in_entry_fails(self):
        with self.assertRaises(NameError):
            self._compile(
                '''
@reset
def main():
    var_x = var_missing
'''
            )

    def test_function_reads_a_global(self):
        # reading needs no global statement: a name not assigned
        # locally falls through to the module scope, like Python
        asm = self._compile(
            '''
var_total = 0

def show():
    var_copy = var_total + 1

@reset
def main():
    global var_total
    var_total = 5
    show()
'''
        )
        self.assertIn('show:', asm)
        self.assertIn('LDA var_total', asm)
        self.assertIn('STA show_var_copy', asm)

    def test_assignment_without_global_is_local(self):
        # assigning without a global statement declares a local,
        # exactly like Python: main gets its own var_total
        asm = self._compile(
            '''
var_total = 0

@reset
def main():
    var_total = 5
'''
        )
        self.assertIn('main_var_total .rs 1', asm)
        self.assertIn('STA main_var_total', asm)

    def test_global_statement_shares_state_between_entries(self):
        asm = self._compile(
            '''
@reset
def main():
    global var_count
    var_count = 0
    nmi_on()
    ppu_on_all()

@nmi
def frame():
    global var_count
    var_count += 1
'''
        )
        self.assertIn('var_count .rs 1', asm)
        self.assertNotIn('main_var_count', asm)
        self.assertIn('INC var_count', asm)

    def test_augmented_assignment_without_binding_fails(self):
        # in Python this is an UnboundLocalError at runtime; the
        # compiler reports it upfront
        with self.assertRaises(UnboundLocalError) as ctx:
            self._compile(
                '''
@reset
def main():
    global var_count
    var_count = 0

@nmi
def frame():
    var_count += 1
'''
            )
        self.assertIn('var_count', str(ctx.exception))

    def test_function_mutates_a_global_array(self):
        # subscript stores do not rebind the name, so a function can
        # mutate a global array in place (like Python)
        asm = self._compile(
            '''
var_data = [0, 0, 0]

def clear_first():
    var_data[0] = 0

@reset
def main():
    global var_data
    var_data = [1, 2, 3]
    clear_first()
'''
        )
        self.assertIn('STA var_data,X', asm)

    def test_locals_are_mangled_globals_are_not(self):
        asm = self._compile(
            '''
var_shared = 0

def helper():
    var_local = var_shared + 1

@reset
def main():
    helper()
'''
        )
        self.assertIn('helper_var_local .rs 1', asm)
        self.assertIn('var_shared .rs 1', asm)
        self.assertNotIn('helper_var_shared', asm)


ENUMERATE_SOURCE = '''
def countdown(n):
    while n > 0:
        yield n
        n -= 1

@reset
def main():
    for var_i, var_v in enumerate(countdown(3)):
        put_num(var_v)
'''


class CartEnumerateTest(TestCase):
    """enumerate() over a generator: the loop unpacks (index, value),
    the index counting from the optional start."""

    def _compile(self, source):
        from neslib.library import lib

        return Cart(libraries=[lib]).compile(source)

    def setUp(self):
        self.asm = self._compile(ENUMERATE_SOURCE)

    def test_both_loop_variables_are_allocated(self):
        self.assertIn('main_var_i .rs 1', self.asm)
        self.assertIn('main_var_v .rs 1', self.asm)

    def test_index_starts_at_zero_and_counts_the_yields(self):
        self.assertIn('STA main_var_i', self.asm)
        self.assertIn('INC main_var_i', self.asm)

    def test_value_comes_from_the_yield(self):
        self.assertIn('LDA yield_value', self.asm)
        self.assertIn('STA main_var_v', self.asm)

    def test_start_offset_initializes_the_index(self):
        asm = self._compile(
            ENUMERATE_SOURCE.replace(
                'enumerate(countdown(3))', 'enumerate(countdown(3), 10)'
            )
        )
        self.assertIn('LDA #10', asm)

    def test_enumerate_requires_a_tuple_target(self):
        with self.assertRaises(NotImplementedError):
            self._compile(
                '''
def countdown(n):
    while n > 0:
        yield n
        n -= 1

@reset
def main():
    for var_pair in enumerate(countdown(3)):
        put_num(var_pair)
'''
            )

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


UINT16_RETURN_SOURCE = '''
from pynes.types import uint16

def factorial(n) -> uint16:
    result = 1
    while n > 1:
        result = result * n
        n -= 1
    return result

@reset
def main():
    put_num(factorial(8))
'''


class CartUint16ReturnTest(TestCase):
    """A function annotated -> uint16 returns 16 bits (A holds the
    low byte, X the high byte) and put_num dispatches on the width
    of its argument (8! = 40320 needs the put_num16 runtime)."""

    def setUp(self):
        from neslib.library import lib

        self.cart = Cart(libraries=[lib])
        self.asm = self.cart.compile(UINT16_RETURN_SOURCE)

    def test_returned_local_is_allocated_16_bit(self):
        self.assertIn('factorial_result .rs 1', self.asm)
        self.assertIn('factorial_result__hi .rs 1', self.asm)

    def test_return_loads_both_bytes(self):
        self.assertIn('LDX factorial_result__hi', self.asm)
        self.assertIn('LDA factorial_result', self.asm)

    def test_put_num_dispatches_to_the_16_bit_runtime(self):
        self.assertIn('JSR factorial', self.asm)
        self.assertIn('STA num_lo', self.asm)
        self.assertIn('STX num_hi', self.asm)
        self.assertIn('JSR put_num16', self.asm)

    def test_put_num_stays_8_bit_for_8_bit_arguments(self):
        from neslib.library import lib

        asm = Cart(libraries=[lib]).compile(
            '''
def double(n):
    return n + n

@reset
def main():
    put_num(double(21))
'''
        )
        self.assertIn('JSR put_num', asm)
        self.assertNotIn('JSR put_num16', asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


ARRAY_PARAM_SOURCE = '''
def fill(arr, value):
    for var_i in range(5):
        arr[var_i] = value

@reset
def main():
    var_data = [0, 0, 0, 0, 0]
    fill(var_data, 7)
'''


class CartArrayParamTest(TestCase):
    """Array arguments bind at compile time: the call targets a
    specialized copy of the function."""

    def setUp(self):
        from neslib.library import lib

        self.cart = Cart(libraries=[lib])
        self.asm = self.cart.compile(ARRAY_PARAM_SOURCE)

    def test_call_targets_the_specialized_copy(self):
        # var_data is a local of main (mangled), and the call binds
        # the array at compile time
        self.assertIn('JSR fill__main_var_data', self.asm)
        self.assertIn('fill__main_var_data:', self.asm)

    def test_body_operates_on_the_array_itself(self):
        self.assertIn('STA main_var_data,X', self.asm)

    def test_scalar_parameter_still_passed(self):
        self.assertIn('STA fill__main_var_data_value', self.asm)

    def test_unused_original_is_dropped(self):
        self.assertNotIn('\nfill:', self.asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


GENERATOR_SOURCE = '''
def blink():
    var_on = 1
    yield
    var_on = 0
    yield

@reset
def main():
    ppu_on_all()
    nmi_on()

@nmi
def frame():
    step(blink)
'''


class CartGeneratorTest(TestCase):
    def setUp(self):
        from neslib.library import lib

        self.cart = Cart(libraries=[lib])
        self.asm = self.cart.compile(GENERATOR_SOURCE)

    def test_state_variable_allocated_and_zeroed_at_boot(self):
        self.assertIn('blink__state .rs 1', self.asm)
        self.assertIn('STA blink__state', self.asm)

    def test_function_name_is_a_label_not_a_variable(self):
        self.assertIn('blink:', self.asm)
        self.assertNotIn('blink .rs', self.asm)

    def test_dispatch_and_resume_points(self):
        self.assertIn('JMP blink__begin', self.asm)
        self.assertIn('JMP blink__resume_1', self.asm)
        self.assertIn('JMP blink__resume_2', self.asm)
        self.assertIn('blink__resume_2:', self.asm)

    def test_step_calls_the_task(self):
        self.assertIn('JSR blink', self.asm)

    def test_parseable_by_nesasm(self):
        tokens = lexical(self.asm)
        ast = syntax(tokens)
        self.assertTrue(len(ast) > 0)


PAD_SOURCE = '''
@reset
def main():
    var_pad = 0
    ppu_on_all()
    nmi_on()

@nmi
def frame():
    var_pad = pad_poll()
    if var_pad & PAD_RIGHT:
        var_pad = 0
'''


class CartPadTest(TestCase):
    def setUp(self):
        from neslib.library import lib

        self.cart = Cart(libraries=[lib])
        self.asm = self.cart.compile(PAD_SOURCE)

    def test_pad_poll_extern_and_runtime(self):
        self.assertIn('JSR pad_poll', self.asm)
        self.assertIn('pad_poll:', self.asm)
        self.assertIn('STA $4016', self.asm)

    def test_button_constant_substituted(self):
        # PAD_RIGHT folds to 1: the truthiness test ANDs against it
        self.assertIn('AND #1', self.asm)
        self.assertNotIn('PAD_RIGHT', self.asm)

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
