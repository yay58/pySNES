from neslib import reset, vram_adr, vram_put, pal_col, ppu_on_all, NTADR_A


def bubble_sort(arr):
    # the sort as a reusable function receiving the array: the
    # compiler binds the argument at compile time (no pointers on
    # the 6502), specializing the routine for each array passed
    for var_i in range(5):
        for var_j in range(4):
            if arr[var_j] > arr[var_j + 1]:
                arr[var_j], arr[var_j + 1] = (
                    arr[var_j + 1],
                    arr[var_j],
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

    bubble_sort(var_arr)

    # draw the sorted array
    vram_adr(NTADR_A(13, 16))
    for var_k in range(5):
        var_t = var_arr[var_k]
        var_t += 48
        vram_put(var_t)

    ppu_on_all()

    while True:
        pass
