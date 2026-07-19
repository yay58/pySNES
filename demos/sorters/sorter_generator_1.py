from neslib import (
    reset,
    vram_adr,
    vram_put,
    put_num,
    pal_col,
    ppu_on_all,
    NTADR_A,
)


def sort_steps(arr):
    # generator receiving the array to sort: after every comparison
    # it yields the number of swaps made so far
    var_swaps = 0
    for var_i in range(4):
        for var_j in range(4):
            if arr[var_j] > arr[var_j + 1]:
                arr[var_j], arr[var_j + 1] = (
                    arr[var_j + 1],
                    arr[var_j],
                )
                var_swaps += 1
            yield var_swaps


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

    # consume the generator with a plain for: one iteration per
    # comparison, the loop variable receiving each yielded value
    var_steps = 0
    for var_swaps in sort_steps(var_arr):
        var_steps += 1

    # draw the sorted array
    vram_adr(NTADR_A(13, 16))
    for var_k in range(5):
        var_t = var_arr[var_k]
        var_t += 48
        vram_put(var_t)

    # comparisons made, and total swaps as counted by the generator
    vram_adr(NTADR_A(13, 20))
    put_num(var_steps)
    vram_adr(NTADR_A(17, 20))
    put_num(var_swaps)

    ppu_on_all()

    while True:
        pass
