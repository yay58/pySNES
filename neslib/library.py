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
'''
)
