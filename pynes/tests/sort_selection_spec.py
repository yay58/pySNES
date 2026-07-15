class SortSelectionSpec:
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

    def test_selection_sort_tuple_swap(self):
        var_arr = [3, 1, 4, 2]
        var_i = 0

        while var_i < 3:
            var_min = var_i
            var_j = var_i + 1
            while var_j < 4:
                if var_arr[var_j] < var_arr[var_min]:
                    var_min = var_j
                var_j += 1
            var_arr[var_i], var_arr[var_min] = (
                var_arr[var_min],
                var_arr[var_i],
            )
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)

    def test_selection_sort_reversed(self):
        var_arr = [4, 3, 2, 1]
        var_i = 0

        while var_i < 3:
            var_min = var_i
            var_j = var_i + 1
            while var_j < 4:
                if var_arr[var_j] < var_arr[var_min]:
                    var_min = var_j
                var_j += 1
            var_arr[var_i], var_arr[var_min] = (
                var_arr[var_min],
                var_arr[var_i],
            )
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)

    def test_selection_sort_duplicates(self):
        var_arr = [2, 1, 2, 1]
        var_i = 0

        while var_i < 3:
            var_min = var_i
            var_j = var_i + 1
            while var_j < 4:
                if var_arr[var_j] < var_arr[var_min]:
                    var_min = var_j
                var_j += 1
            var_arr[var_i], var_arr[var_min] = (
                var_arr[var_min],
                var_arr[var_i],
            )
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 1)
        self.assertEqual(var_arr[2], 2)
        self.assertEqual(var_arr[3], 2)
