class MathSpec:
    def test_sum_1_plus_1_with_vars(self):
        var_q = 1
        var_w = 1
        var_e = var_q + var_w

        self.assertEqual(var_e, 2)

    def test_sum_1_plus_2_with_vars(self):
        var_q = 1
        var_w = 2
        var_e = var_q + var_w

        self.assertEqual(var_e, 3)

    def test_sum_2_plus_2_with_vars(self):
        var_q = 2
        var_w = 2
        var_e = var_q + var_w

        self.assertEqual(var_e, 4)

    def test_sum_3_plus_1_with_vars(self):
        var_q = 3
        var_w = 1
        var_e = var_q + var_w

        self.assertEqual(var_e, 4)

    def test_sub_3_minus_1_with_vars(self):
        var_q = 3
        var_w = 1
        var_e = var_q - var_w

        self.assertEqual(var_e, 2)

    def test_sub_2_minus_2_with_vars(self):
        var_q = 2
        var_w = 2
        var_e = var_q - var_w

        self.assertEqual(var_e, 0)

    def test_sub_2_minus_1_with_vars(self):
        var_q = 2
        var_w = 1
        var_e = var_q - var_w

        self.assertEqual(var_e, 1)

    def test_sub_1_minus_1_with_vars(self):
        var_q = 1
        var_w = 1
        var_e = var_q - var_w

        self.assertEqual(var_e, 0)

    def test_sum_1_plus_1_with_const(self):
        var_q = 1 + 1

        self.assertEqual(var_q, 2)

    def test_sum_1_plus_2_with_const(self):
        var_q = 1 + 2

        self.assertEqual(var_q, 3)

    def test_sum_2_plus_2_with_const(self):
        var_q = 2 + 2

        self.assertEqual(var_q, 4)

    def test_sum_3_plus_1_with_const(self):
        var_q = 3 + 1

        self.assertEqual(var_q, 4)

    def test_sub_3_minus_1_with_const(self):
        var_q = 3 - 1

        self.assertEqual(var_q, 2)

    def test_sub_2_minus_2_with_const(self):
        var_q = 2 - 2

        self.assertEqual(var_q, 0)

    def test_sub_2_minus_1_with_const(self):
        var_q = 2 - 1

        self.assertEqual(var_q, 1)

    def test_sub_1_minus_1_with_const(self):
        var_q = 1 - 1

        self.assertEqual(var_q, 0)

    def test_add_sequential(self):
        var_q = 2 + 2 + 4 + 8

        self.assertEqual(var_q, 16)

    def test_sub_sequential(self):
        var_q = 20 - 2 - 4 - 6

        self.assertEqual(var_q, 8)

    def test_mixed_operations(self):
        var_q = 10 + 4 - 2 + 8

        self.assertEqual(var_q, 20)

    def test_operations_with_parentheses(self):
        var_q = (2 + 3) - (1 + 1)

        self.assertEqual(var_q, 3)

    def test_nested_parentheses(self):
        var_q = ((2 + 3) - 1) + (4 - (1 + 1))

        self.assertEqual(var_q, 6)  # (5 - 1) + (4 - 2) = 4 + 2 = 6

    def test_mixed_operations_with_vars(self):
        var_a = 5
        var_b = 3
        var_c = var_a + 2 - var_b + 1

        self.assertEqual(var_c, 5)  # 5 + 2 - 3 + 1 = 5

    def test_operations_with_temp_results(self):
        var_a = 2 + 3  # First store 5
        var_b = var_a - 1  # Then use it: 5 - 1
        var_c = var_b + var_a  # Finally: 4 + 5

        self.assertEqual(var_c, 9)

    def test_complex_expression(self):
        var_x = 10
        var_y = 4
        var_z = (var_x - 2) + (var_y + 3) - (1 + 1)

        self.assertEqual(var_z, 13)  # (10 - 2) + (4 + 3) - 2 = 13

    def test_multiple_parentheses(self):
        var_q = (2 + 3) + (4 + 5) - (1 + 2)

        self.assertEqual(var_q, 11)  # 5 + 9 - 3 = 11
