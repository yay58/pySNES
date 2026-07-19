# fibonacci: the sequence computed inline with a while loop and
# plain 8-bit variables, printing fib(10) = 55 after a label
from neslib import reset, pal_col, ppu_on_all, put_str, put_num, NTADR_A
from pynes.types import string


label = string('FIB 10 = ')


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    var_a = 0
    var_b = 1
    var_n = 10
    while var_n > 0:
        var_next = var_a + var_b
        var_a = var_b
        var_b = var_next
        var_n -= 1

    put_str(NTADR_A(10, 14), label)
    put_num(var_a)

    ppu_on_all()

    while True:
        pass
