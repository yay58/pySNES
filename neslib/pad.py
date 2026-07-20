class Pad:
    """Controller model: button state plus the $4016 strobe/shift
    register protocol, so compiled code polling the hardware sees the
    same buttons as the pure-Python twin."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 0  # No SNES, armazena até 16 bits (0xFFFF)
        self.strobe = False
        self.index = 0

    def write(self, value):
        """$4016 write: strobe high reloads the shift register;
        strobe low starts shifting buttons out (same line handles both ports on SNES)."""
        if value & 1:
            self.strobe = True
        else:
            self.strobe = False
            self.index = 0

    def read(self):
        """$4016 read: one button per read, B first (bit 15 of state).
        After all 16 cycles, official SNES controllers return 0."""
        if self.strobe:
            # Se o strobe estiver ativo, o registrador fica travado no primeiro bit (B)
            return (self.state >> 15) & 1
            
        if self.index >= 16:
            # Após ler os 12 botões + 4 bits de ID, o SNES devolve 0
            return 0
            
        # Desloca os bits a partir do bit 15 (B, Y, Select, Start, Up...) descendo até o bit 0
        bit = (self.state >> (15 - self.index)) & 1
        self.index += 1
        return bit
