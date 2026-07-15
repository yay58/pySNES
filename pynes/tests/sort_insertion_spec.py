class SortInsertionSpec:
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

    def test_insertion_sort_pythonic(self):
        var_arr = [3, 1, 4, 2, 5]
        var_i = 1

        while var_i < 5:
            var_key = var_arr[var_i]
            var_j = var_i
            while var_j > 0:
                if var_arr[var_j - 1] > var_key:
                    var_arr[var_j] = var_arr[var_j - 1]
                    var_j -= 1
                else:
                    break
            var_arr[var_j] = var_key
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)
        self.assertEqual(var_arr[4], 5)

    def test_insertion_sort_already_sorted(self):
        var_arr = [1, 2, 3]
        var_i = 1

        while var_i < 3:
            var_key = var_arr[var_i]
            var_j = var_i
            while var_j > 0:
                if var_arr[var_j - 1] > var_key:
                    var_arr[var_j] = var_arr[var_j - 1]
                    var_j -= 1
                else:
                    break
            var_arr[var_j] = var_key
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)

    def test_insertion_sort_reversed(self):
        var_arr = [4, 3, 2, 1]
        var_i = 1

        while var_i < 4:
            var_key = var_arr[var_i]
            var_j = var_i
            while var_j > 0:
                if var_arr[var_j - 1] > var_key:
                    var_arr[var_j] = var_arr[var_j - 1]
                    var_j -= 1
                else:
                    break
            var_arr[var_j] = var_key
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 2)
        self.assertEqual(var_arr[2], 3)
        self.assertEqual(var_arr[3], 4)

    def test_insertion_sort_duplicates(self):
        var_arr = [2, 1, 2, 1]
        var_i = 1

        while var_i < 4:
            var_key = var_arr[var_i]
            var_j = var_i
            while var_j > 0:
                if var_arr[var_j - 1] > var_key:
                    var_arr[var_j] = var_arr[var_j - 1]
                    var_j -= 1
                else:
                    break
            var_arr[var_j] = var_key
            var_i += 1

        self.assertEqual(var_arr[0], 1)
        self.assertEqual(var_arr[1], 1)
        self.assertEqual(var_arr[2], 2)
        self.assertEqual(var_arr[3], 2)
