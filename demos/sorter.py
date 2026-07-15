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

    # bubble sort, running on the 6502
    var_i = 0
    while var_i < 5:
        var_j = 0
        while var_j < 4:
            var_k = var_j + 1
            if var_arr[var_j] > var_arr[var_k]:
                var_tmp = var_arr[var_j]
                var_arr[var_j] = var_arr[var_k]
                var_arr[var_k] = var_tmp
            var_j += 1
        var_i += 1

    # draw the sorted array
    vram_adr(NTADR_A(13, 16))
    for var_i in range(5):
        var_t = var_arr[var_i]
        var_t += 48
        vram_put(var_t)

    ppu_on_all()

    while True:
        pass
