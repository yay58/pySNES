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

    # def test_add_sequential(self):
    #     var_q = 2 + 2 + 4 + 8

    #     self.assertEqual(var_q, 16)
