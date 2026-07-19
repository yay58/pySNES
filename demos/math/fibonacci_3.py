# fibonacci_3: enumerate replaces the manual line counter; the
# start offset makes the index the nametable line itself
from neslib import reset, pal_col, ppu_on_all, put_num, vram_adr, NTADR_A


def fibonacci(n):
    a = 0
    b = 1
    while n > 0:
        next_value = a + b
        a = b
        b = next_value
        yield a
        n -= 1


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    for index, value in enumerate(fibonacci(8), 10):
        vram_adr(NTADR_A(12, index))
        put_num(value)

    ppu_on_all()

    while True:
        pass
