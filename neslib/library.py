import ast

from pynes.library import Library, NesFunction
# Importando as constantes do arquivo sneslib recém-modificado
from sneslib import (
    BG_ADR,
    PAD_B,
    PAD_Y,
    PAD_SELECT,
    PAD_START,
    PAD_UP,
    PAD_DOWN,
    PAD_LEFT,
    PAD_RIGHT,
    PAD_A,
    PAD_X,
    PAD_L,
    PAD_R,
)

lib = Library('sneslib')

lib.const(BG_ADR)

# Constantes de controle de 16 bits do SNES
lib.constant('PAD_B', PAD_B)
lib.constant('PAD_Y', PAD_Y)
lib.constant('PAD_SELECT', PAD_SELECT)
lib.constant('PAD_START', PAD_START)
lib.constant('PAD_UP', PAD_UP)
lib.constant('PAD_DOWN', PAD_DOWN)
lib.constant('PAD_LEFT', PAD_LEFT)
lib.constant('PAD_RIGHT', PAD_RIGHT)
lib.constant('PAD_A', PAD_A)
lib.constant('PAD_X', PAD_X)
lib.constant('PAD_L', PAD_L)
lib.constant('PAD_R', PAD_R)

# Ponteiros de 16 bits na Direct Page (Zero Page do SNES)
lib.zeropage('str_ptr')
lib.zeropage('str_ptr_hi')

# Scratch de 16 bits para conversões decimais e cálculos de offset
lib.zeropage('num_lo')
lib.zeropage('num_hi')
lib.zeropage('map_lo')
lib.zeropage('map_hi')

# Estado do controle expandido para 16 bits (Word de 2 bytes na Direct Page)
lib.zeropage('pad_state')      # Low byte (A, X, L, R...)
lib.zeropage('pad_state_hi')   # High byte (B, Y, Select, Start, D-Pad...)


class VramAdr(NesFunction):
    def caller_code(self, translator, args):
        # Carrega endereço de 16 bits (0x0000 - 0xFFFF palavras de VRAM)
        translator.load_arg16(args[0])
        translator.output.append('JSR vram_adr')

    def runtime_code(self):
        return '''
vram_adr:
  ; Configura o endereço de escrita da VRAM do SNES ($2116/$2117)
  ; O acumulador deve estar em modo 8 ou 16 bits dependendo da pynes original, 
  ; assumindo passagem padrão via registros A/X ou pilha.
  STA $2116
  RTS
'''


class VramPut(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg16(args[0]) # SNES VRAM recebe dados de 16 bits (Tile + Atributos)
        translator.output.append('JSR vram_put')

    def runtime_code(self):
        return '''
vram_put:
  ; Grava a palavra de 16 bits nos registradores de dados da VRAM ($2118/$2119)
  ; O SNES incrementa o endereço automaticamente baseado no registro $2115 (padrão +1)
  STA $2118
  RTS
'''


class PalCol(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg8_x(args[0]) # Index da Paleta / Cor
        translator.load_arg16(args[1])  # Cor em formato 15-bit BGR (0-32767)
        translator.output.append('JSR pal_col')

    def runtime_code(self):
        return '''
pal_col:
  ; Configura o endereço da CGRAM (Paleta do SNES) através do $2121
  STX $2121
  ; Grava os 15 bits de cor (Low byte em $2122, High byte em $2122 subsequente)
  STA $2122
  RTS
'''


class PpuOnAll(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR ppu_on_all')

    def runtime_code(self):
        return '''
ppu_on_all:
  ; Ativa as camadas principais na tela do SNES (Main Screen Designation $212C)
  ; Bit 0: BG1, Bit 4: Sprites (OBJ) -> %00010001
  LDA #%00010001
  STA $212C
  ; Desliga o Screen Blanking do SNES ($2100) definindo o brilho máximo (15)
  LDA #$0F
  STA $2100
  RTS
'''


class NmiOn(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR nmi_on')

    def runtime_code(self):
        return '''
nmi_on:
  ; Ativa NMI e habilita Auto-Polling de controles no SNES via registro $4200
  LDA #%10000001
  STA $4200
  RTS
'''


class Scroll(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg8_x(args[0]) # X Scroll
        translator.load_arg8(args[1])  # Y Scroll
        translator.output.append('JSR scroll')

    def runtime_code(self):
        return '''
scroll:
  ; No SNES, cada camada (BG1-BG4) possui seu próprio par de registradores de scroll de escrita dupla.
  ; Assumindo BG1 para esta função básica ($210D para Horizontal, $210E para Vertical).
  STX $210D
  STX $210D ; Escrita dupla (Low byte, High byte)
  STA $210E
  STA $210E ; Escrita dupla (Low byte, High byte)
  RTS
'''


class Step(NesFunction):
    def caller_code(self, translator, args):
        if not isinstance(args[0], ast.Name):
            raise NotImplementedError('step() espera o nome de uma tarefa geradora')
        translator.output.append(f'JSR {args[0].id}')

    def runtime_code(self):
        return ''


class ResetTask(NesFunction):
    def caller_code(self, translator, args):
        if not isinstance(args[0], ast.Name):
            raise NotImplementedError('reset_task() espera o nome de uma tarefa geradora')
        translator.output.append('LDA #0')
        translator.output.append(f'STA {args[0].id}__state')

    def runtime_code(self):
        return ''


class PadPoll(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR pad_poll')

    def runtime_code(self):
        return '''
pad_poll:
  ; Leitura Manual via $4016 modificado para extrair 16 bits em vez de 8
  LDA #1
  STA $4016
  LDA #0
  STA $4016
  LDX #16
pad_poll_loop:
  LDA $4016
  LSR A
  ; Rotaciona o bit para dentro do estado de 16 bits (Através da Direct Page)
  ROL pad_state      ; Move Carry para o bit inferior de pad_state
  ROL pad_state_hi   ; Arrasta o bit estourado para o byte alto
  DEX
  BNE pad_poll_loop
  
  ; Retorna o resultado de 16 bits combinado
  ; Nota: O formato final respeita a ordem de rotação manual (B em bit 15, R em bit 4)
  LDA pad_state
  LDX pad_state_hi
  RTS
'''


class ScrollX(NesFunction):
    def caller_code(self, translator, args):
        translator.load_arg8_x(args[0]) # Fine X Scroll
        translator.load_arg8(args[1])  # Base do espelhamento do mapa
        translator.output.append('JSR scroll_x')

    def runtime_code(self):
        return '''
scroll_x:
  ; No SNES, mapas grandes de BG usam configurações de tela no registro $2107-$210A.
  ; Esta rotina espelha a troca de telas do NES atualizando o BG1 Scroll diretamente.
  STX $210D
  STA $210D
  RTS
'''


class StageColumn(NesFunction):
    def caller_code(self, translator, args):
        if not isinstance(args[0], ast.Name):
            raise NotImplementedError('stage_column espera uma variável de estágio como primeiro argumento')
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
  ; X = índice da coluna. Como as telas do SNES usam colunas padrão de 32 bytes de altura (ou mais),
  ; alteramos o multiplicador de colunas de 30 para 32. 
  ; Multiplicar por 32 é muito mais rápido: basta dar 5 rotações à esquerda (ASL)!
  STX num_lo
  LDA #0
  STA num_hi
  
  .repeat 5
  ASL num_lo
  ROL num_hi
  .endr
  
  LDA str_ptr
  CLC
  ADC num_lo
  STA str_ptr
  LDA str_ptr_hi
  ADC num_hi
  STA str_ptr_hi

  ; Destino na VRAM do SNES: Colunas alternam entre bases físicas a cada 32 blocos
  TXA
  AND #63
  CMP #32
  BCC stage_col_map_a
  AND #31
  TAY
  LDA #$24  ; Mapa B fictício do SNES (ex: offset 0x0400 palavras à frente)
  JMP stage_col_set
stage_col_map_a:
  TAY
  LDA #$20  ; Mapa A fictício do SNES (Base VRAM padrão mapeada em 0x2000)
stage_col_set:
  ; Configura o registrador de incremento de VRAM do SNES ($2115) 
  ; para avançar +32 a cada escrita (Incremento Vertical de Coluna)
  LDX #%10000001 ; Bit 7=1 (incrementa após ler/escrever byte alto), Bits 0-1 = 01 (avanço de 32)
  STX $2115
  
  ; Define o endereço inicial da VRAM ($2116)
  STA $2117
  STY $2116
  
  ; Copia 32 bytes verticalmente na tela
  LDY #0
stage_col_loop:
  LDA (str_ptr),Y
  ; No SNES gravamos em formato Word ($2118 para o byte baixo, automático)
  STA $2118
  INY
  CPY #32
  BNE stage_col_loop
  
  ; Restaura o incremento padrão de VRAM para +1 (horizontal) para não quebrar outras funções
  LDX #%10000000
  STX $2115
  RTS
'''


class OamClear(NesFunction):
    def caller_code(self, translator, args):
        translator.output.append('JSR oam_clear')

    def runtime_code(self):
        return '''
oam_clear:
  ; O SNES limpa a memória OAM principal escrevendo em $2102/$2103
  ; Move os 128 sprites mudando a coordenada Y para fora da tela visível (ex: 225)
  LDA #0
  STA $2102
  STA $2103
  LDA #225
  LDX #0
oam_clear_loop:
  STA $2104 ; Passa X (espera duas escritas por sprite antes de aplicar Y)
  STA $2104 ; Passa Y (Atualizado para ocultar)
  INX
  CPX #128
  BNE oam_clear_loop
  RTS
'''


class OamSpr(NesFunction):
    def caller_code(self, translator, args):
        x_arg, y_arg, tile_arg, attr_arg, id_arg = args
        id_arg = translator._fold_const(id_arg)
        if not isinstance(id_arg, ast.Constant):
            raise NotImplementedError('oam_spr requer um ID constante de sprite')
        
        # O SNES agrupa dados em buffers de sombra para fazer o upload via DMA de uma vez só.
        # Mapeando os buffers temporários em uma página RAM do SNES (Ex: página $0200)
        base = 0x0200 + (id_arg.value & 0x7F) * 4
        
        # Formato OAM do SNES por entrada: Byte 0=X, Byte 1=Y, Byte 2=Tile, Byte 3=Atributos
        for offset, arg in enumerate((x_arg, y_arg, tile_arg, attr_arg)):
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
  ; Configura o canal de DMA 0 do SNES para transferir o buffer OAM da RAM ($0200)
  LDA #%00000000 ; Transferência direta de 1 byte por escrita (passo simples para OAM)
  STA $4300
  LDA #$04       ; Registrador de destino: $2104 (OAM Data Port)
  STA $4301
  ; Endereço de origem: buffer $0200 da RAM
  LDA #LOW($0200)
  STA $4302
  LDA #HIGH($0200)
  STA $4303
  LDA #0         
  ; Bank 0
  STA $4304
  ; Tamanho da transferência: 128 sprites * 4 bytes = 512 bytes
  LDA #LOW(512)
  STA $4305
  LDA #HIGH(512)
  STA $4306
  ; Dispara o DMA do SNES no canal 0 ativando o bit 0 de $420B
  LDA #1
  STA $420B
  RTS
'''

class PutStr(NesFunction):
    def caller_code(self, translator, args):
        if not isinstance(args[1], ast.Name):
            raise NotImplementedError('put_str() needs a valid string')
