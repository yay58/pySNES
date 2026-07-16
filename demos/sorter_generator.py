from neslib import (
    reset,
    nmi,
    nmi_on,
    scroll,
    step,
    vram_adr,
    vram_put,
    pal_col,
    ppu_on_all,
    NTADR_A,
)


def sort_task():
    # plain pythonic bubble sort: each yield suspends until the next
    # frame, so the sort animates without hand-written state juggling
    for var_i in range(4):
        for var_j in range(4):
            if var_arr[var_j] > var_arr[var_j + 1]:
                var_arr[var_j], var_arr[var_j + 1] = (
                    var_arr[var_j + 1],
                    var_arr[var_j],
                )
            yield


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

    # ppu_on_all resets PPUCTRL, so enable the NMI afterwards
    ppu_on_all()
    nmi_on()

    while True:
        pass


@nmi
def frame():
    # one sort step per vblank; when the task finishes, the working
    # row keeps showing the sorted array
    step(sort_task)
    vram_adr(NTADR_A(13, 16))
    for var_k in range(5):
        var_t = var_arr[var_k]
        var_t += 48
        vram_put(var_t)
    scroll(0, 0)
