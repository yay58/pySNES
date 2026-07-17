from neslib import reset, pal_col, ppu_on_all, put_num, vram_adr, NTADR_A


def factorial(n):
    result = 1
    while n > 1:
        result = result * n
        yield result
        n -= 1

@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    line = 10
    for value in factorial(5):
        vram_adr(NTADR_A(12, line))
        put_num(value)
        line += 1

    ppu_on_all()

    while True:
        pass
