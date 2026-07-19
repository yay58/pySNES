from neslib import reset, pal_col, ppu_on_all, put_num, vram_adr, NTADR_A


def factorial(n):
    result = 1
    while n > 1:
        result = result * n
        n -= 1
    return result

@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    for value in range(5):
        line  = 10 + value
        vram_adr(NTADR_A(12, line))
        put_num(factorial(value))

    ppu_on_all()

    while True:
        pass
