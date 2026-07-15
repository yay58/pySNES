from neslib import reset, vram_put, pal_col, ppu_on_all, put_str, NTADR_A
from pynes.types import string

label = string('5! = ')


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

    # the VRAM address keeps incrementing after the string,
    # so the digits land right after the label
    put_str(NTADR_A(12, 14), label)

    var_f = factorial(5)

    # print var_f as three decimal digits (computed at runtime!)
    var_d = 0
    while var_f >= 100:
        var_f -= 100
        var_d += 1
    var_t = 48 + var_d
    vram_put(var_t)

    var_d = 0
    while var_f >= 10:
        var_f -= 10
        var_d += 1
    var_t = 48 + var_d
    vram_put(var_t)

    var_t = 48 + var_f
    vram_put(var_t)

    ppu_on_all()

    while True:
        pass
