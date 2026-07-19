# fibonacci_2: the sequence becomes a generator task; a for loop
# consumes the yields, printing each value on its own line
# (runtime nametable addresses from a variable)
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

    line = 10
    for value in fibonacci(8):
        vram_adr(NTADR_A(12, line))
        put_num(value)
        line += 1

    ppu_on_all()

    while True:
        pass
