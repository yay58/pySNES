class ComparisonSpec:
    def test_equal_comparison(self):
        var_q = 0
        if var_q == 0:
            var_q = 1
        self.assertEqual(var_q, 1)

        var_q = 1
        if var_q == 0:
            var_q = 2
        self.assertEqual(var_q, 1)

    def test_not_equal_comparison(self):
        var_q = 0
        if var_q != 0:
            var_q = 1
        self.assertEqual(var_q, 0)

        var_q = 1
        if var_q != 0:
            var_q = 2
        self.assertEqual(var_q, 2)

    def test_less_than_comparison(self):
        var_q = 0
        if var_q < 1:
            var_q = 2
        self.assertEqual(var_q, 2)

        var_q = 1
        if var_q < 1:
            var_q = 3
        self.assertEqual(var_q, 1)

    def test_greater_than_comparison(self):
        var_q = 2
        if var_q > 1:
            var_q = 3
        self.assertEqual(var_q, 3)

        var_q = 1
        if var_q > 1:
            var_q = 4
        self.assertEqual(var_q, 1)

    def test_less_equal_comparison(self):
        var_q = 0
        if var_q <= 1:
            var_q = 2
        self.assertEqual(var_q, 2)

    def test_compare_edge_cases(self):
        var_a = 0
        var_b = 255  # Max 8-bit value

        # Test at boundaries
        var_result = 0
        if var_a < var_b:
            var_result = 1
        self.assertEqual(var_result, 1)

        var_result = 0
        if var_b > var_a:
            var_result = 1
        self.assertEqual(var_result, 1)

        var_result = 0
        if var_a <= 0:
            var_result = 1
        self.assertEqual(var_result, 1)

        var_result = 0
        if var_b >= 255:
            var_result = 1
        self.assertEqual(var_result, 1)

    def test_compare_with_expressions(self):
        var_x = 5
        var_y = 3
        var_z = 2
        var_result = 0

        # Compare with arithmetic expressions
        if var_x > var_y + var_z:  # 5 > (3 + 2)
            var_result = 1
        self.assertEqual(var_result, 0)  # Should be false since 5 > 5 is false

        var_result = 0
        if var_x - var_y > var_z:  # (5 - 3) > 2
            var_result = 1
        self.assertEqual(var_result, 0)  # Should be false since 2 > 2 is false

        var_result = 0
        if var_y + var_z == var_x:  # (3 + 2) == 5
            var_result = 1
        self.assertEqual(var_result, 1)

        var_q = 1
        if var_q <= 1:
            var_q = 3
        self.assertEqual(var_q, 3)

        var_q = 2
        if var_q <= 1:
            var_q = 4
        self.assertEqual(var_q, 2)

    def test_greater_equal_comparison(self):
        var_q = 2
        if var_q >= 1:
            var_q = 3
        self.assertEqual(var_q, 3)

        var_q = 1
        if var_q >= 1:
            var_q = 4
        self.assertEqual(var_q, 4)

        var_q = 0
        if var_q >= 1:
            var_q = 5
        self.assertEqual(var_q, 0)

    def test_variable_comparison(self):
        var_q = 0
        var_w = 0
        if var_q == var_w:
            var_q = 1
        self.assertEqual(var_q, 1)

        var_q = 1
        var_w = 2
        if var_q == var_w:
            var_q = 3
        self.assertEqual(var_q, 1)

        if var_q != var_w:
            var_q = 4
        self.assertEqual(var_q, 4)

        var_q = 1
        var_w = 2
        if var_q < var_w:
            var_q = 5
        self.assertEqual(var_q, 5)

        var_q = 2
        var_w = 1
        if var_q > var_w:
            var_q = 6
        self.assertEqual(var_q, 6)
