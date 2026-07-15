class SortSpec:
    def test_bubble_sort(self):
        var_arr = [5, 2, 4, 1, 3]
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

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
        self.assertEqual(var_arr[4], 5)

    def test_bubble_sort_pythonic(self):
        var_arr = [5, 2, 4, 1, 3]

        for var_i in range(5):
            for var_j in range(4):
                if var_arr[var_j] > var_arr[var_j + 1]:
                    var_tmp = var_arr[var_j]
                    var_arr[var_j] = var_arr[var_j + 1]
                    var_arr[var_j + 1] = var_tmp

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
        self.assertEqual(var_arr[4], 5)

    def test_bubble_sort_tuple_swap(self):
        var_arr = [5, 2, 4, 1, 3]

        for var_i in range(5):
            for var_j in range(4):
                if var_arr[var_j] > var_arr[var_j + 1]:
                    var_arr[var_j], var_arr[var_j + 1] = (
                        var_arr[var_j + 1],
                        var_arr[var_j],
                    )

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
        self.assertEqual(var_arr[4], 5)

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

    def test_selection_sort(self):
        var_arr = [3, 1, 4, 2]
        var_i = 0

        while var_i < 3:
            var_min = var_i
            var_j = var_i + 1
            while var_j < 4:
                if var_arr[var_j] < var_arr[var_min]:
                    var_min = var_j
                var_j += 1
            var_tmp = var_arr[var_i]
            var_arr[var_i] = var_arr[var_min]
            var_arr[var_min] = var_tmp
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)

    def test_insertion_sort(self):
        var_arr = [4, 3, 1, 2]
        var_i = 1

        while var_i < 4:
            var_key = var_arr[var_i]
            var_j = var_i
            while var_j > 0:
                var_k = var_j - 1
                if var_arr[var_k] > var_key:
                    var_arr[var_j] = var_arr[var_k]
                    var_j -= 1
                else:
                    break
            var_arr[var_j] = var_key
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)

    def test_bubble_sort_already_sorted(self):
        var_arr = [1, 2, 3]
        var_i = 0

        while var_i < 3:
            var_j = 0
            while var_j < 2:
                var_k = var_j + 1
                if var_arr[var_j] > var_arr[var_k]:
                    var_tmp = var_arr[var_j]
                    var_arr[var_j] = var_arr[var_k]
                    var_arr[var_k] = var_tmp
                var_j += 1
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)

    def test_bubble_sort_reversed(self):
        var_arr = [4, 3, 2, 1]
        var_i = 0

        while var_i < 4:
            var_j = 0
            while var_j < 3:
                var_k = var_j + 1
                if var_arr[var_j] > var_arr[var_k]:
                    var_tmp = var_arr[var_j]
                    var_arr[var_j] = var_arr[var_k]
                    var_arr[var_k] = var_tmp
                var_j += 1
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
