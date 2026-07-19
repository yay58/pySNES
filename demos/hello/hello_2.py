from neslib import reset, pal_col, ppu_on_all, put_str, NTADR_A
from pynes.types import string

hello = string('HELLO WORLD!')


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    put_str(NTADR_A(10, 14), hello)

    ppu_on_all()

    while True:
        pass
