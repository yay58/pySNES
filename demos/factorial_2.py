from neslib import reset, pal_col, ppu_on_all, put_str, put_num, NTADR_A
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

    put_str(NTADR_A(12, 14), label)
    var_f = factorial(5)
    put_num(var_f)

    ppu_on_all()

    while True:
        pass
