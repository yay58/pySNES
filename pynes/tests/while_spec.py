class WhileSpec:
    def test_while_equal(self):
        var_q = 0
        var_w = 0
        while var_q == 0:
            var_q = 5
            var_w += 1

        self.assertEqual(var_q, 5)
        self.assertEqual(var_w, 1)

    def test_while_if_equal_5(self):
        var_q = 0
        var_w = 0
        while var_q == 0:
            var_w += 1
            if var_w == 5:
                var_q = 2

        self.assertEqual(var_q, 2)
        self.assertEqual(var_w, 5)

    def test_while_not_equal(self):
        var_q = 1
        var_w = 0
        while var_q != 0:
            var_q = 0
            var_w += 1

        self.assertEqual(var_q, 0)
        self.assertEqual(var_w, 1)

    def test_while_less_than(self):
        var_q = 0

        while var_q < 10:
            var_q += 1

        self.assertEqual(var_q, 10)

    def test_while_greater_than(self):
        var_q = 10

        while var_q > 0:
            var_q -= 1

        self.assertEqual(var_q, 0)

    def test_while_break(self):
        var_q = 0
        var_w = 0
        while var_q == 0:
            var_w += 1
            if var_w == 5:
                break

        self.assertEqual(var_q, 0)
        self.assertEqual(var_w, 5)

    def test_while_true(self):
        var_w = 0
        while True:
            var_w += 1
            if var_w == 5:
                break

        self.assertEqual(var_w, 5)

    def test_while_continue(self):
        var_x = 0
        var_y = 0
        while var_x < 5:
            var_x += 1
            if var_x == 3:
                continue
            var_y += 1

        self.assertEqual(var_x, 5)
        self.assertEqual(var_y, 4)  # y skips increment when x is 3

    def test_nested_while(self):
        var_i = 0
        var_j = 0
        var_sum = 0
        while var_i < 3:
            var_j = 0
            while var_j < 2:
                var_sum += 1
                var_j += 1
            var_i += 1

        self.assertEqual(var_sum, 6)  # 3 outer loops * 2 inner loops

    def test_while_with_multiple_vars(self):
        var_a = 0
        var_b = 5
        var_count = 0
        while var_a < 3:
            var_a += 1
            var_b -= 1
            var_count += 1

        self.assertEqual(var_count, 3)
        self.assertEqual(var_a, 3)
        self.assertEqual(var_b, 2)

    def test_while_less_equal(self):
        var_q = 0

        while var_q <= 5:
            var_q += 1

        self.assertEqual(var_q, 6)

    def test_while_greater_equal(self):
        var_q = 5

        while var_q >= 1:
            var_q -= 1

        self.assertEqual(var_q, 0)

    def test_while_and_condition(self):
        var_a = 0
        var_b = 1
        while var_a < 5 and var_b == 1:
            var_a += 1
            if var_a == 3:
                var_b = 0

        self.assertEqual(var_a, 3)
        self.assertEqual(var_b, 0)

    def test_while_or_condition(self):
        var_a = 0
        var_b = 0
        while var_a < 3 or var_b < 2:
            var_a += 1
            var_b += 1

        self.assertEqual(var_a, 3)
        self.assertEqual(var_b, 3)

    def test_while_variable_comparison(self):
        var_a = 0
        var_b = 4

        while var_a < var_b:
            var_a += 1

        self.assertEqual(var_a, 4)

    def test_while_array_condition(self):
        var_arr = [3, 2, 1, 0]
        var_i = 0
        var_sum = 0

        while var_arr[var_i] > 0:
            var_sum += var_arr[var_i]
            var_i += 1

        self.assertEqual(var_sum, 6)
        self.assertEqual(var_i, 3)

    def test_while_function_call_condition(self):
        def next_value(n):
            return n - 1

        var_q = 5
        var_steps = 0

        while next_value(var_q) > 0:
            var_q -= 1
            var_steps += 1

        self.assertEqual(var_q, 1)
        self.assertEqual(var_steps, 4)

    def test_while_not_condition(self):
        var_done = 0
        var_count = 0

        while not var_done == 1:
            var_count += 1
            if var_count == 4:
                var_done = 1

        self.assertEqual(var_count, 4)

    def test_break_in_nested_while(self):
        var_i = 0
        var_count = 0

        while var_i < 3:
            var_j = 0
            while var_j < 10:
                if var_j == 2:
                    break
                var_j += 1
                var_count += 1
            var_i += 1

        self.assertEqual(var_count, 6)

    def test_while_true_continue(self):
        var_x = 0
        var_y = 0

        while True:
            var_x += 1
            if var_x == 3:
                continue
            var_y += 1
            if var_x == 5:
                break

        self.assertEqual(var_x, 5)
        self.assertEqual(var_y, 4)
