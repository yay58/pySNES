import ast

from pynes.library import Library, NesFunction
from neslib import (
    NTADR_A,
    PAD_A,
    PAD_B,
    PAD_SELECT,
    PAD_START,
    PAD_UP,
    PAD_DOWN,
    PAD_LEFT,
    PAD_RIGHT,
)

lib = Library('neslib')

lib.const(NTADR_A)

lib.constant('PAD_A', PAD_A)
lib.constant('PAD_B', PAD_B)
lib.constant('PAD_SELECT', PAD_SELECT)
lib.constant('PAD_START', PAD_START)
lib.constant('PAD_UP', PAD_UP)
lib.constant('PAD_DOWN', PAD_DOWN)
lib.constant('PAD_LEFT', PAD_LEFT)
lib.constant('PAD_RIGHT', PAD_RIGHT)

# 16-bit string pointer: adjacent registrations guarantee
# str_ptr_hi == str_ptr + 1, as required by (indirect),Y addressing
lib.zeropage('str_ptr')
lib.zeropage('str_ptr_hi')

# scratch byte for put_num decimal conversion
lib.zeropage('num_tmp')

# 16-bit scratch for put_num16: adjacent lo/hi pair
lib.zeropage('num_lo')
lib.zeropage('num_hi')

# 16-bit scratch for stage_col offset math: adjacent lo/hi pair
lib.zeropage('map_lo')
lib.zeropage('map_hi')

# controller shift-in scratch
lib.zeropage('pad_state')


class VramAdr(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg16(args[0])
        translator.output.append('JSR vram_adr')

    def runtime_code(self):
        return '''
vram_adr:
  PHA
  LDA $2002
  PLA
  STX $2006
  STA $2006
  RTS
'''


class VramPut(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg8(args[0])
        translator.output.append('JSR vram_put')

    def runtime_code(self):
        return '''
vram_put:
  STA $2007
  RTS
'''


class PalCol(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg8_x(args[0])
        translator.load_arg8(args[1])
        translator.output.append('JSR pal_col')

    def runtime_code(self):
        return '''
pal_col:
  PHA
  BIT $2002
  LDA #$3F
  STA $2006
  TXA
  AND #$1F
  STA $2006
  PLA
  STA $2007
  RTS
'''


class PpuOnAll(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR ppu_on_all')

    def runtime_code(self):
        return '''
ppu_on_all:
  LDA $2002
  LDA #0
  STA $2000
  STA $2005
  STA $2005
  LDA #%00011110
  STA $2001
  RTS
'''


class NmiOn(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR nmi_on')

    def runtime_code(self):
        return '''
nmi_on:
  LDA #%10000000
  STA $2000
  RTS
'''


class Scroll(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg8_x(args[0])
        translator.load_arg8(args[1])
        translator.output.append('JSR scroll')

    def runtime_code(self):
        return '''
scroll:
  ; X = x scroll, A = y scroll
  TAY
  LDA $2002
  STX $2005
  STY $2005
  RTS
'''


class Step(NesFunction):
    # step(task): resume a generator task until its next yield.
    # Leaves 1 in A while the task is alive, 0 once it finished,
    # so it can be used as a condition: if step(task): ...
    def caller_code(self, translator, args):
        if not isinstance(args[0], ast.Name):
            raise NotImplementedError('step() expects a generator task name')
        translator.output.append(f'JSR {args[0].id}')

    def runtime_code(self):
        return ''


class ResetTask(NesFunction):
    # reset_task(task): rewind a generator task to its beginning
    def caller_code(self, translator, args):
        if not isinstance(args[0], ast.Name):
            raise NotImplementedError(
                'reset_task() expects a generator task name'
            )
        translator.output.append('LDA #0')
        translator.output.append(f'STA {args[0].id}__state')

    def runtime_code(self):
        return ''


class PadPoll(NesFunction):
    # pad_poll(): leaves the controller byte in A (and pad_state),
    # so it can be assigned: var_pad = pad_poll()
    def caller_code(self, translator, args):
        translator.output.append('JSR pad_poll')

    def runtime_code(self):
        return '''
pad_poll:
  ; strobe the controller, then shift the 8 buttons into pad_state
  ; (A ends up in bit 7 down to Right in bit 0)
  LDA #1
  STA $4016
  LDA #0
  STA $4016
  LDX #8
pad_poll_loop:
  LDA $4016
  LSR A
  ROL pad_state
  DEX
  BNE pad_poll_loop
  LDA pad_state
  RTS
'''


class ScrollX(NesFunction):
    # scroll_x(x, nt): fine x scroll plus the nametable select bit,
    # for cameras wider than one nametable (camera = nt*256 + x)
    def caller_code(self, translator, args):
        translator.load_arg8_x(args[0])
        translator.load_arg8(args[1])
        translator.output.append('JSR scroll_x')

    def runtime_code(self):
        return '''
scroll_x:
  ; X = fine x scroll, A = nametable index (bit 0 selects the NT)
  AND #1
  ORA #%10000000
  STA $2000
  LDA $2002
  STX $2005
  LDA #0
  STA $2005
  RTS
'''


class StageColumn(NesFunction):
    # stage_column(level, col): upload one 30-tile column of a stage
    # to its nametable position (columns wrap over the two physical
    # nametables)
    def caller_code(self, translator, args):
        if not isinstance(args[0], ast.Name):
            raise NotImplementedError(
                'stage_column expects a stage variable as first argument'
            )
        name = args[0].id
        translator.output.append(f'LDA #LOW({name})')
        translator.output.append('STA str_ptr')
        translator.output.append(f'LDA #HIGH({name})')
        translator.output.append('STA str_ptr_hi')
        translator.load_arg8_x(args[1])
        translator.output.append('JSR stage_col')

    def runtime_code(self):
        return '''
stage_col:
  ; X = column index, str_ptr = stage base (column-major, 30 b/col)
  ; src pointer += col * 30 (30 = 2 + 4 + 8 + 16, via shifts)
  STX num_lo
  LDA #0
  STA num_hi
  ASL num_lo
  ROL num_hi
  LDA num_lo
  STA map_lo
  LDA num_hi
  STA map_hi
  ASL num_lo
  ROL num_hi
  LDA map_lo
  CLC
  ADC num_lo
  STA map_lo
  LDA map_hi
  ADC num_hi
  STA map_hi
  ASL num_lo
  ROL num_hi
  LDA map_lo
  CLC
  ADC num_lo
  STA map_lo
  LDA map_hi
  ADC num_hi
  STA map_hi
  ASL num_lo
  ROL num_hi
  LDA map_lo
  CLC
  ADC num_lo
  STA map_lo
  LDA map_hi
  ADC num_hi
  STA map_hi
  LDA str_ptr
  CLC
  ADC map_lo
  STA str_ptr
  LDA str_ptr_hi
  ADC map_hi
  STA str_ptr_hi
  ; dest: physical column = col AND 63 over the two nametables
  TXA
  AND #63
  CMP #32
  BCC stage_col_nt_a
  AND #31
  TAY
  LDA #$24
  JMP stage_col_set
stage_col_nt_a:
  TAY
  LDA #$20
stage_col_set:
  ; A = VRAM high byte, Y = low byte
  PHA
  LDA #%00000100
  STA $2000
  LDA $2002
  PLA
  STA $2006
  TYA
  STA $2006
  ; copy 30 bytes downwards (vertical increment)
  LDY #0
stage_col_loop:
  LDA (str_ptr),Y
  STA $2007
  INY
  CPY #30
  BNE stage_col_loop
  ; NMI users must call scroll_x afterwards to restore $2000
  LDA #%00000000
  STA $2000
  RTS
'''


class OamClear(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR oam_clear')

    def runtime_code(self):
        return '''
oam_clear:
  LDA #$FF
  LDX #0
oam_clear_loop:
  STA $0200,X
  INX
  BNE oam_clear_loop
  RTS
'''


class OamSpr(NesFunction):
    # oam_spr(x, y, tile, attr, id): id must be constant so each OAM
    # byte gets a fixed address in the $0200 shadow page
    def caller_code(self, translator, args):
        x_arg, y_arg, tile_arg, attr_arg, id_arg = args
        id_arg = translator._fold_const(id_arg)
        if not isinstance(id_arg, ast.Constant):
            raise NotImplementedError('oam_spr requires a constant sprite id')
        base = 0x0200 + (id_arg.value & 0x3F) * 4
        for offset, arg in enumerate((y_arg, tile_arg, attr_arg, x_arg)):
            translator.load_arg8(arg)
            translator.output.append(f'STA ${base + offset:04X}')

    def runtime_code(self):
        return ''


class OamDma(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR oam_dma')

    def runtime_code(self):
        return '''
oam_dma:
  LDA #0
  STA $2003
  LDA #$02
  STA $4014
  RTS
'''


class PutStr(NesFunction):
    def caller_code(self, translator, args):
        if not isinstance(args[1], ast.Name):
            raise NotImplementedError(
                'put_str expects a string variable as second argument'
            )
        translator.load_arg16(args[0])
        translator.output.append('JSR vram_adr')
        name = args[1].id
        translator.output.append(f'LDA #LOW({name})')
        translator.output.append('STA str_ptr')
        translator.output.append(f'LDA #HIGH({name})')
        translator.output.append('STA str_ptr_hi')
        translator.output.append('JSR put_str')

    def runtime_code(self):
        return '''
put_str:
  LDY #0
put_str_loop:
  LDA (str_ptr),Y
  BEQ put_str_done
  STA $2007
  INY
  JMP put_str_loop
put_str_done:
  RTS
'''


def _is_uint16_expr(translator, arg):
    """True when an expression carries 16 bits: a uint16 variable or
    a call to a function returning uint16."""
    if isinstance(arg, ast.Name):
        return arg.id in translator.uint16_vars
    return (
        isinstance(arg, ast.Call)
        and isinstance(arg.func, ast.Name)
        and arg.func.id in translator.uint16_funcs
    )


class PutNum(NesFunction):
    # polymorphic like print: the width of the argument decides
    # which runtime renders it
    def caller_code(self, translator, args):
        arg = args[0]
        if _is_uint16_expr(translator, arg):
            if isinstance(arg, ast.Name):
                translator.output.append(f'LDA {arg.id}')
                translator.output.append('STA num_lo')
                translator.output.append(f'LDA {arg.id}__hi')
                translator.output.append('STA num_hi')
            else:
                # the call returns A = low byte, X = high byte
                translator.load_arg8(arg)
                translator.output.append('STA num_lo')
                translator.output.append('STX num_hi')
            translator.output.append('JSR put_num16')
            return
        translator.load_arg8(arg)
        translator.output.append('JSR put_num')

    def runtime_code(self):
        return '''
put_num:
  LDX #0
put_num_100:
  CMP #100
  BCC put_num_100_done
  SEC
  SBC #100
  INX
  JMP put_num_100
put_num_100_done:
  STA num_tmp
  TXA
  CLC
  ADC #48
  STA $2007
  LDA num_tmp
  LDX #0
put_num_10:
  CMP #10
  BCC put_num_10_done
  SEC
  SBC #10
  INX
  JMP put_num_10
put_num_10_done:
  STA num_tmp
  TXA
  CLC
  ADC #48
  STA $2007
  LDA num_tmp
  CLC
  ADC #48
  STA $2007
  RTS
'''


class PutNum16(NesFunction):
    def caller_code(self, translator, args):
        arg = args[0]
        if not isinstance(arg, ast.Name):
            raise NotImplementedError('put_num16 requires a variable')
        translator.output.append(f'LDA {arg.id}')
        translator.output.append('STA num_lo')
        if arg.id in translator.uint16_vars:
            translator.output.append(f'LDA {arg.id}__hi')
        else:
            translator.output.append('LDA #0')
        translator.output.append('STA num_hi')
        translator.output.append('JSR put_num16')

    def runtime_code(self):
        return '''
put_num16:
  LDX #0
pn16_10000:
  LDA num_lo
  SEC
  SBC #$10
  TAY
  LDA num_hi
  SBC #$27
  BCC pn16_10000_done
  STY num_lo
  STA num_hi
  INX
  JMP pn16_10000
pn16_10000_done:
  TXA
  CLC
  ADC #48
  STA $2007
  LDX #0
pn16_1000:
  LDA num_lo
  SEC
  SBC #$E8
  TAY
  LDA num_hi
  SBC #$03
  BCC pn16_1000_done
  STY num_lo
  STA num_hi
  INX
  JMP pn16_1000
pn16_1000_done:
  TXA
  CLC
  ADC #48
  STA $2007
  LDX #0
pn16_100:
  LDA num_lo
  SEC
  SBC #$64
  TAY
  LDA num_hi
  SBC #$00
  BCC pn16_100_done
  STY num_lo
  STA num_hi
  INX
  JMP pn16_100
pn16_100_done:
  TXA
  CLC
  ADC #48
  STA $2007
  LDX #0
pn16_10:
  LDA num_lo
  SEC
  SBC #$0A
  TAY
  LDA num_hi
  SBC #$00
  BCC pn16_10_done
  STY num_lo
  STA num_hi
  INX
  JMP pn16_10
pn16_10_done:
  TXA
  CLC
  ADC #48
  STA $2007
  LDA num_lo
  CLC
  ADC #48
  STA $2007
  RTS
'''


lib.function(VramAdr())
lib.function(VramPut())
lib.function(PalCol())
lib.function(PpuOnAll())
lib.function(NmiOn())
lib.function(Scroll())
lib.function(Step())
lib.function(ResetTask())
lib.function(PadPoll())
lib.function(ScrollX())
lib.function(StageColumn())
lib.function(OamClear())
lib.function(OamSpr())
lib.function(OamDma())
lib.function(PutStr())
lib.function(PutNum())
lib.function(PutNum16())
