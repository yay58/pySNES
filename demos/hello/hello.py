from neslib import reset, vram_adr, vram_put, pal_col, ppu_on_all


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    vram_adr(0x21CA)  # NTADR_A(10, 14): centered on screen
    vram_put(72)  # H
    vram_put(69)  # E
    vram_put(76)  # L
    vram_put(76)  # L
    vram_put(79)  # O
    vram_put(32)  #
    vram_put(87)  # W
    vram_put(79)  # O
    vram_put(82)  # R
    vram_put(76)  # L
    vram_put(68)  # D
    vram_put(33)  # !

    ppu_on_all()

    while True:
        pass
