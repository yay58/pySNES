class MathSpec:
    def test_sum_1_plus_1(self):
        var_q = 1
        var_w = 1
        var_e = var_q + var_w

        self.assertEqual(var_e, 2)

    def test_sum_1_plus_2(self):
        var_q = 1
        var_w = 2
        var_e = var_q + var_w

        self.assertEqual(var_e, 3)

    def test_sum_2_plus_2(self):
        var_q = 2
        var_w = 2
        var_e = var_q + var_w

        self.assertEqual(var_e, 4)

    def test_sum_3_plus_1(self):
        var_q = 3
        var_w = 1
        var_e = var_q + var_w

        self.assertEqual(var_e, 4)

    def test_sub_3_minus_1(self):
        var_q = 3
        var_w = 1
        var_e = var_q - var_w

        self.assertEqual(var_e, 2)

    def test_sub_2_minus_2(self):
        var_q = 2
        var_w = 2
        var_e = var_q - var_w

        self.assertEqual(var_e, 0)

    def test_sub_2_minus_1(self):
        var_q = 2
        var_w = 1
        var_e = var_q - var_w

        self.assertEqual(var_e, 1)

    def test_sub_1_minus_1(self):
        var_q = 1
        var_w = 1
        var_e = var_q - var_w

        self.assertEqual(var_e, 0)
