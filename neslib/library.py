from pynes.library import Library

lib = Library('neslib')


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


lib.runtime(
    '''
vram_adr:
  STX $2006
  STA $2006
  RTS

vram_put:
  STA $2007
  RTS

pal_col:
  PHA
  LDA #$3F
  STA $2006
  TXA
  AND #$1F
  STA $2006
  PLA
  STA $2007
  RTS

ppu_on_all:
  LDA #%00011110
  STA $2001
  RTS
'''
)
