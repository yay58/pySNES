class SortQuicksortSpec:
    def test_quick_sort(self):
        var_arr = [5, 2, 4, 1, 3]
        # iterative quicksort: no recursion on the 6502 (locals are
        # statically allocated), so lo/hi ranges go on an explicit
        # stack array
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

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
        self.assertEqual(var_arr[4], 5)

    def test_quick_sort_reversed(self):
        var_arr = [5, 4, 3, 2, 1]
        var_stack = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        var_stack[1] = 4
        var_top = 2

        while var_top > 0:
            var_top -= 2
            var_lo = var_stack[var_top]
            var_hi = var_stack[var_top + 1]

            if var_lo < var_hi:
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

                if var_i > var_lo:
                    var_stack[var_top] = var_lo
                    var_t = var_i - 1
                    var_stack[var_top + 1] = var_t
                    var_top += 2
                var_t = var_i + 1
                if var_t < var_hi:
                    var_stack[var_top] = var_t
                    var_stack[var_top + 1] = var_hi
                    var_top += 2

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
        self.assertEqual(var_arr[4], 5)

    def test_quick_sort_duplicates(self):
        var_arr = [2, 1, 2, 1]
        var_stack = [0, 0, 0, 0, 0, 0, 0, 0]
        var_stack[1] = 3
        var_top = 2

        while var_top > 0:
            var_top -= 2
            var_lo = var_stack[var_top]
            var_hi = var_stack[var_top + 1]

            if var_lo < var_hi:
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

                if var_i > var_lo:
                    var_stack[var_top] = var_lo
                    var_t = var_i - 1
                    var_stack[var_top + 1] = var_t
                    var_top += 2
                var_t = var_i + 1
                if var_t < var_hi:
                    var_stack[var_top] = var_t
                    var_stack[var_top + 1] = var_hi
                    var_top += 2

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 1)
        self.assertEqual(var_arr[2], 2)
        self.assertEqual(var_arr[3], 2)
