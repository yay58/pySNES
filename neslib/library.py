import ast

from pynes.library import Library
from neslib import NTADR_A

lib = Library('neslib')

lib.const(NTADR_A)

# 16-bit string pointer: adjacent registrations guarantee
# str_ptr_hi == str_ptr + 1, as required by (indirect),Y addressing
lib.zeropage('str_ptr')
lib.zeropage('str_ptr_hi')

# scratch byte for put_num decimal conversion
lib.zeropage('num_tmp')

# 16-bit scratch for put_num16: adjacent lo/hi pair
lib.zeropage('num_lo')
lib.zeropage('num_hi')


@lib.extern
def vram_adr(translator, args):
    translator.load_arg16(args[0])
    translator.output.append('JSR vram_adr')


@lib.extern
def vram_put(translator, args):
    translator.load_arg8(args[0])
    translator.output.append('JSR vram_put')


@lib.extern
def pal_col(translator, args):
    translator.load_arg8_x(args[0])
    translator.load_arg8(args[1])
    translator.output.append('JSR pal_col')


@lib.extern
def ppu_on_all(translator, args):
    translator.output.append('JSR ppu_on_all')


@lib.extern
def nmi_on(translator, args):
    translator.output.append('JSR nmi_on')


@lib.extern
def scroll(translator, args):
    translator.load_arg8_x(args[0])
    translator.load_arg8(args[1])
    translator.output.append('JSR scroll')


@lib.extern
def oam_clear(translator, args):
    translator.output.append('JSR oam_clear')


@lib.extern
def oam_spr(translator, args):
    # oam_spr(x, y, tile, attr, id): id must be constant so each OAM
    # byte gets a fixed address in the $0200 shadow page
    x_arg, y_arg, tile_arg, attr_arg, id_arg = args
    id_arg = translator._fold_const(id_arg)
    if not isinstance(id_arg, ast.Constant):
        raise NotImplementedError('oam_spr requires a constant sprite id')
    base = 0x0200 + (id_arg.value & 0x3F) * 4
    for offset, arg in enumerate((y_arg, tile_arg, attr_arg, x_arg)):
        translator.load_arg8(arg)
        translator.output.append(f'STA ${base + offset:04X}')


@lib.extern
def oam_dma(translator, args):
    translator.output.append('JSR oam_dma')


@lib.extern
def put_str(translator, args):
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


@lib.extern
def put_num(translator, args):
    translator.load_arg8(args[0])
    translator.output.append('JSR put_num')


@lib.extern
def put_num16(translator, args):
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


lib.runtime(
    '''
vram_adr:
  PHA
  LDA $2002
  PLA
  STX $2006
  STA $2006
  RTS

vram_put:
  STA $2007
  RTS

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

nmi_on:
  LDA #%10000000
  STA $2000
  RTS

oam_clear:
  LDA #$FF
  LDX #0
oam_clear_loop:
  STA $0200,X
  INX
  BNE oam_clear_loop
  RTS

oam_dma:
  LDA #0
  STA $2003
  LDA #$02
  STA $4014
  RTS

scroll:
  ; X = x scroll, A = y scroll
  TAY
  LDA $2002
  STX $2005
  STY $2005
  RTS

ppu_on_all:
  LDA $2002
  LDA #0
  STA $2000
  STA $2005
  STA $2005
  LDA #%00011110
  STA $2001
  RTS

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
)
