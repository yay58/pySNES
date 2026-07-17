from neslib import reset, pal_col, ppu_on_all, put_str, put_num16, NTADR_A
from pynes.types import string, uint16

label = string('8! = ')


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    # 8! = 40320 does not fit in one byte: var_f is a uint16
    var_f: uint16 = 1
    var_n = 8
    while var_n > 1:
        var_f = var_f * var_n
        var_n -= 1

    put_str(NTADR_A(12, 14), label)
    put_num16(var_f)

    ppu_on_all()

    while True:
        pass
