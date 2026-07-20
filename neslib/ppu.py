# Registradores e Máscaras de Tela do SNES
MASK_BG1_ON   = 0x01  # Habilita Background 1 na tela principal ($212C)
MASK_OBJ_ON   = 0x10  # Habilita Sprites na tela principal ($212C)
MASK_ON_ALL   = MASK_BG1_ON | MASK_OBJ_ON
INCDIM_32     = 0x01  # Incremento em bloco vertical de 32 (específico para colunas)

class PPU:
    """Minimal S-PPU state mock used by the pure-Python sneslib
    implementation, so game specs can run and be asserted in CPython."""

    def __init__(self):
        self.reset()

    def reset(self):
        # SNES VRAM possui 64KB e armazena Words de 16 bits (0x8000 palavras no total)
        self.vram = [0] * 0x8000  
        self.addr = 0             # Endereço atual da VRAM (Palavra de 16 bits)
        self.main_screen = 0      # Registrador $212C (Main Screen Designation)
        self.screen_display = 0x80 # Registrador $2100 (Inicia em Force Blanking)
        self.vram_inc_mode = 0x80 # Registrador $2115 (Controle de incremento de VRAM)
        self.bg_scroll = {}       # Armazena scroll (X, Y) para as camadas 1 a 4
        
        # SNES OAM principal: 128 sprites x 4 bytes (x, y, tile, attr) = 512 bytes
        self.oam = bytearray(b'\xe0' * 512) 
        # SNES OAM alta: 32 bytes para armazenar tamanhos e o 9º bit do X dos sprites
        self.oam_high = bytearray(32)
        self.oam_addr = 0         # Ponteiro de endereço da OAM ($2102/$2103)
        self.oam_flip = False     # Toggle interno de escrita de 16 bits da OAM
        
        # SNES CGRAM (Palette RAM): 256 entradas de cores de 16-bit (15-bit BGR555 efetivos)
        self.cgram = [0] * 256
        self.cgram_addr = 0       # Ponteiro de endereço da CGRAM ($2121)
        self.cgram_flip = False   # Toggle interno de escrita baixa/alta para CGRAM
        
        self.oam_tiles = {}
        self.latch_scroll = None  # Latches de escrita dupla de Scroll do SNES

    @property
    def rendering_enabled(self):
        # Desliga se o bit 7 de $2100 (Forced Blank) estiver ativo, ou se as camadas principais estiverem ocultas
        if self.screen_display & 0x80:
            return False
        return (self.main_screen & MASK_ON_ALL) == MASK_ON_ALL

    def write_register(self, register, value):
        """Hardware-register write ($2100-$213F), as performed by
        compiled 65c816 code running against this model."""
        value &= 0xFF
        
        if register == 0x2100:
            self.screen_display = value
            
        elif register == 0x2102:
            # Endereço OAM byte baixo
            self.oam_addr = (self.oam_addr & 0x0100) | value
        elif register == 0x2103:
            # Endereço OAM bit mais significativo (Modo objeto e bit 9)
            self.oam_addr = (self.oam_addr & 0x00FF) | ((value & 1) << 8)
            
        elif register == 0x2104:
            # Dados da OAM ($2104) - Mapeia direto no buffer de 512 ou 32 bytes
            actual_addr = self.oam_addr & 0x01FF
            if self.oam_addr < 512:
                self.oam[actual_addr] = value
            else:
                self.oam_high[actual_addr - 512] = value
            self.oam_addr = (self.oam_addr + 1) & 0x03FF
            
        elif register in (0x210D, 0x210E):
            # Exemplo simplificado para BG1 Scroll (Horizontal/Vertical) de escrita dupla
            bg_id = 1
            if bg_id not in self.bg_scroll:
                self.bg_scroll[bg_id] = [0, 0]
            if self.latch_scroll is None:
                self.latch_scroll = value
            else:
                scroll_val = (self.latch_scroll | (value << 8)) & 0x03FF
                if register == 0x210D:
                    self.bg_scroll[bg_id][0] = scroll_val # X Scroll
                else:
                    self.bg_scroll[bg_id][1] = scroll_val # Y Scroll
                self.latch_scroll = None
                
        elif register == 0x2115:
            self.vram_inc_mode = value
            
        elif register == 0x2116:
            # Endereço de VRAM Byte Baixo
            self.addr = (self.addr & 0xFF00) | value
        elif register == 0x2117:
            # Endereço de VRAM Byte Alto
            self.addr = (self.addr & 0x00FF) | (value << 8)
            
        elif register == 0x2118:
            # Escreve no Byte Baixo da palavra atual da VRAM
            current_word = self.vram[self.addr & 0x7FFF]
            self.vram[self.addr & 0x7FFF] = (current_word & 0xFF00) | value
            if not (self.vram_inc_mode & 0x80): # Se incrementa no acesso ao byte baixo
                self._apply_vram_step()
                
        elif register == 0x2119:
            # Escreve no Byte Alto da palavra atual da VRAM
            current_word = self.vram[self.addr & 0x7FFF]
            self.vram[self.addr & 0x7FFF] = (current_word & 0x00FF) | (value << 8)
            if self.vram_inc_mode & 0x80: # Se incrementa no acesso ao byte alto (padrão)
                self._apply_vram_step()
                
        elif register == 0x2121:
            self.cgram_addr = value
            self.cgram_flip = False
            
        elif register == 0x2122:
            # Escrita de 15 bits na CGRAM (Paleta) alternando entre bytes baixo/alto
            if not self.cgram_flip:
                current_color = self.cgram[self.cgram_addr]
                self.cgram[self.cgram_addr] = (current_color & 0x7F00) | value
                self.cgram_flip = True
            else:
                current_color = self.cgram[self.cgram_addr]
                self.cgram[self.cgram_addr] = (current_color & 0x00FF) | ((value & 0x7F) << 8)
                self.cgram_flip = False
                self.cgram_addr = (self.cgram_addr + 1) & 0xFF
                
        elif register == 0x212C:
            self.main_screen = value

    def read_register(self, register):
        """Hardware-register read. $213F acts as status register reporting vblank."""
        if register == 0x213F:
            # Mock assume que está sempre no VBLANK para destravar loops de sincronismo
            return 0x80 
        return 0

    def _apply_vram_step(self):
        """Calculates and applies internal SNES VRAM pointer increment step."""
        step_type = self.vram_inc_mode & 0x03
        if step_type == 0:
            step = 1
        elif step_type == 1:
            step = 32
        elif step_type == 2:
            step = 64
        else:
            step = 128
        self.addr = (self.addr + step) & 0x7FFF
