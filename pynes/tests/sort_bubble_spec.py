class SortBubbleSpec:
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

    def test_bubble_sort_already_sorted(self):
        var_arr = [1, 2, 3]

        for var_i in range(3):
            for var_j in range(2):
                if var_arr[var_j] > var_arr[var_j + 1]:
                    var_arr[var_j], var_arr[var_j + 1] = (
                        var_arr[var_j + 1],
                        var_arr[var_j],
                    )

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)

    def test_bubble_sort_reversed(self):
        var_arr = [4, 3, 2, 1]

        for var_i in range(4):
            for var_j in range(3):
                if var_arr[var_j] > var_arr[var_j + 1]:
                    var_arr[var_j], var_arr[var_j + 1] = (
                        var_arr[var_j + 1],
                        var_arr[var_j],
                    )

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)

    def test_bubble_sort_duplicates(self):
        var_arr = [2, 1, 2, 1]

        for var_i in range(4):
            for var_j in range(3):
                if var_arr[var_j] > var_arr[var_j + 1]:
                    var_arr[var_j], var_arr[var_j + 1] = (
                        var_arr[var_j + 1],
                        var_arr[var_j],
                    )

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 1)
        self.assertEqual(var_arr[2], 2)
        self.assertEqual(var_arr[3], 2)
