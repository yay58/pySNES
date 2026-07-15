from neslib import (
    reset,
    nmi,
    nmi_on,
    scroll,
    vram_adr,
    vram_put,
    pal_col,
    ppu_on_all,
    NTADR_A,
)


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    var_arr = [3, 1, 4, 2, 5]

    # draw the unsorted array
    vram_adr(NTADR_A(13, 12))
    for var_k in range(5):
        var_t = var_arr[var_k]
        var_t += 48
        vram_put(var_t)

    # bubble sort progress, advanced one step per frame by the NMI
    var_i = 0
    var_j = 0

    # ppu_on_all resets PPUCTRL, so enable the NMI afterwards
    ppu_on_all()
    nmi_on()

    while True:
        pass


@nmi
def frame():
    # one bubble-sort step per vblank: the sort animates at 60 fps
    if var_i < 5:
        if var_arr[var_j] > var_arr[var_j + 1]:
            var_arr[var_j], var_arr[var_j + 1] = (
                var_arr[var_j + 1],
                var_arr[var_j],
            )
        var_j += 1
        if var_j >= 4:
            var_j = 0
            var_i += 1

        # redraw the working row during vblank
        vram_adr(NTADR_A(13, 16))
        for var_k in range(5):
            var_t = var_arr[var_k]
            var_t += 48
            vram_put(var_t)
        scroll(0, 0)
