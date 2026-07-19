from neslib import reset, vram_adr, vram_put, pal_col, ppu_on_all, NTADR_A


@reset
def main():
    pal_col(0, 0x0F)  # background: black
    pal_col(1, 0x30)  # text: white

    var_arr = [3, 1, 4, 2, 5]

    # draw the unsorted array
    vram_adr(NTADR_A(13, 12))
    for var_i in range(5):
        var_t = var_arr[var_i]
        var_t += 48
        vram_put(var_t)

    # iterative quicksort, running on the 6502: no recursion (locals
    # are statically allocated), so lo/hi ranges go on a stack array
    var_stack = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    var_stack[1] = 4
    var_top = 2

    while var_top > 0:
        var_top -= 2
        var_lo = var_stack[var_top]
        var_hi = var_stack[var_top + 1]

        if var_lo < var_hi:
            # Lomuto partition around the last element
            var_p = var_arr[var_hi]
            var_i = var_lo
            var_j = var_lo
            while var_j < var_hi:
                if var_arr[var_j] < var_p:
                    var_arr[var_i], var_arr[var_j] = (
                        var_arr[var_j],
                        var_arr[var_i],
                    )
                    var_i += 1
                var_j += 1
            var_arr[var_i], var_arr[var_hi] = (
                var_arr[var_hi],
                var_arr[var_i],
            )

            # push the left partition
            if var_i > var_lo:
                var_stack[var_top] = var_lo
                var_t = var_i - 1
                var_stack[var_top + 1] = var_t
                var_top += 2
            # push the right partition
            var_t = var_i + 1
            if var_t < var_hi:
                var_stack[var_top] = var_t
                var_stack[var_top + 1] = var_hi
                var_top += 2

    # draw the sorted array
    vram_adr(NTADR_A(13, 16))
    for var_i in range(5):
        var_t = var_arr[var_i]
        var_t += 48
        vram_put(var_t)

    ppu_on_all()

    while True:
        pass
