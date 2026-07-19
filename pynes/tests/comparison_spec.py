class ComparisonSpec:
    # NOTE: asserts check the final state, so each phase of a test
    # uses its own variable

    def test_equal_comparison(self):
        var_q = 0
        if var_q == 0:
            var_q = 1
        self.assertEqual(var_q, 1)

        var_w = 1
        if var_w == 0:
            var_w = 2
        self.assertEqual(var_w, 1)

    def test_not_equal_comparison(self):
        var_q = 0
        if var_q != 0:
            var_q = 1
        self.assertEqual(var_q, 0)

        var_w = 1
        if var_w != 0:
            var_w = 2
        self.assertEqual(var_w, 2)

    def test_less_than_comparison(self):
        var_q = 0
        if var_q < 1:
            var_q = 2
        self.assertEqual(var_q, 2)

        var_w = 1
        if var_w < 1:
            var_w = 3
        self.assertEqual(var_w, 1)

    def test_greater_than_comparison(self):
        var_q = 2
        if var_q > 1:
            var_q = 3
        self.assertEqual(var_q, 3)

        var_w = 1
        if var_w > 1:
            var_w = 4
        self.assertEqual(var_w, 1)

    def test_less_equal_comparison(self):
        var_q = 0
        if var_q <= 1:
            var_q = 2
        self.assertEqual(var_q, 2)

        var_w = 1
        if var_w <= 1:
            var_w = 3
        self.assertEqual(var_w, 3)

        var_e = 2
        if var_e <= 1:
            var_e = 4
        self.assertEqual(var_e, 2)

    def test_greater_equal_comparison(self):
        var_q = 2
        if var_q >= 1:
            var_q = 3
        self.assertEqual(var_q, 3)

        var_w = 1
        if var_w >= 1:
            var_w = 4
        self.assertEqual(var_w, 4)

        var_e = 0
        if var_e >= 1:
            var_e = 5
        self.assertEqual(var_e, 0)

    def test_compare_edge_cases(self):
        var_a = 0
        var_b = 255  # Max 8-bit value

        # Test at boundaries
        var_r1 = 0
        if var_a < var_b:
            var_r1 = 1
        self.assertEqual(var_r1, 1)

        var_r2 = 0
        if var_b > var_a:
            var_r2 = 1
        self.assertEqual(var_r2, 1)

        var_r3 = 0
        if var_a <= 0:
            var_r3 = 1
        self.assertEqual(var_r3, 1)

        var_r4 = 0
        if var_b >= 255:
            var_r4 = 1
        self.assertEqual(var_r4, 1)

    def test_compare_with_expressions(self):
        var_x = 5
        var_y = 3
        var_z = 2

        # Compare with arithmetic expressions
        var_r1 = 0
        if var_x > var_y + var_z:  # 5 > (3 + 2)
            var_r1 = 1
        self.assertEqual(var_r1, 0)  # false since 5 > 5 is false

        var_r2 = 0
        if var_x - var_y > var_z:  # (5 - 3) > 2
            var_r2 = 1
        self.assertEqual(var_r2, 0)  # false since 2 > 2 is false

        var_r3 = 0
        if var_y + var_z == var_x:  # (3 + 2) == 5
            var_r3 = 1
        self.assertEqual(var_r3, 1)

    def test_variable_comparison(self):
        var_q = 0
        var_w = 0
        if var_q == var_w:
            var_q = 1
        self.assertEqual(var_q, 1)

        var_e = 1
        var_r = 2
        if var_e == var_r:
            var_e = 3
        self.assertEqual(var_e, 1)
