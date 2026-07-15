class ArraySpec:
    def test_array_literal(self):
        var_arr = [3, 1, 2]

        self.assertEqual(var_arr[0], 3)
        self.assertEqual(var_arr[1], 1)
        self.assertEqual(var_arr[2], 2)

    def test_array_read_constant_index(self):
        var_arr = [4, 5, 6]
        var_x = var_arr[1]

        self.assertEqual(var_x, 5)

    def test_array_write_constant_index(self):
        var_arr = [0, 0, 0]
        var_arr[1] = 7

        self.assertEqual(var_arr[0], 0)
        self.assertEqual(var_arr[1], 7)
        self.assertEqual(var_arr[2], 0)

    def test_array_read_variable_index(self):
        var_arr = [4, 5, 6]
        var_i = 2
        var_x = var_arr[var_i]

        self.assertEqual(var_x, 6)

    def test_array_write_variable_index(self):
        var_arr = [0, 0, 0]
        var_i = 1
        var_arr[var_i] = 9

        self.assertEqual(var_arr[1], 9)

    def test_array_copy_element(self):
        var_arr = [1, 2, 3]
        var_i = 0
        var_j = 2
        var_arr[var_i] = var_arr[var_j]

        self.assertEqual(var_arr[0], 3)
        self.assertEqual(var_arr[2], 3)

    def test_array_sum_with_loop(self):
        var_arr = [1, 2, 3, 4]
        var_sum = 0

        for var_i in range(4):
            var_sum += var_arr[var_i]

        self.assertEqual(var_sum, 10)

    def test_array_fill_with_loop(self):
        var_arr = [0, 0, 0, 0]

        for var_i in range(4):
            var_arr[var_i] = var_i

        self.assertEqual(var_arr[0], 0)
        self.assertEqual(var_arr[1], 1)
        self.assertEqual(var_arr[2], 2)
        self.assertEqual(var_arr[3], 3)

    def test_two_arrays(self):
        var_src = [7, 8]
        var_dst = [0, 0]

        for var_i in range(2):
            var_dst[var_i] = var_src[var_i]

        self.assertEqual(var_dst[0], 7)
        self.assertEqual(var_dst[1], 8)

    def test_array_element_in_condition(self):
        var_arr = [1, 5]
        var_r = 0

        if var_arr[1] > var_arr[0]:
            var_r = 1

        self.assertEqual(var_r, 1)
