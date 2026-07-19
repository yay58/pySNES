# fibonacci_1: the sequence moves into a function with its own
# locals, and the call feeds put_num directly (nested function
# calls as extern arguments)
from neslib import reset, pal_col, ppu_on_all, put_str, put_num, NTADR_A
from pynes.types import string


label = string('FIB 10 = ')


def fibonacci(n):
    a = 0
    b = 1
    while n > 0:
        next_value = a + b
        a = b
        b = next_value
        n -= 1
    return a


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    put_str(NTADR_A(10, 14), label)
    put_num(fibonacci(10))

    ppu_on_all()

    while True:
        pass
