class BitwiseSpec:
    def test_logical_4_and_7_with_vars(self):
        var_q = 4
        var_w = 7
        var_e = var_q & var_w

        self.assertEqual(var_e, 4)

    def test_logical_2_and_4_with_vars(self):
        var_q = 2
        var_w = 4
        var_e = var_q & var_w

        self.assertEqual(var_e, 0)

    def test_logical_4_or_7_with_vars(self):
        var_q = 4
        var_w = 7
        var_e = var_q | var_w

        self.assertEqual(var_e, 7)

    def test_logical_2_or_4_with_vars(self):
        var_q = 2
        var_w = 4
        var_e = var_q | var_w

        self.assertEqual(var_e, 6)

    def test_shift_left_2_1(self):
        var_q = 2
        var_w = 1
        var_e = var_q << var_w

        self.assertEqual(var_e, 4)

    def test_shift_left_4_1(self):
        var_q = 4
        var_w = 1
        var_e = var_q << var_w

        self.assertEqual(var_e, 8)

    # def test_shift_left_2_2(self):
    #     var_q = 2
    #     var_w = 2
    #     var_e = var_q << var_w

    #     self.assertEqual(var_e, 8)

    def test_shift_right_4_1(self):
        var_q = 4
        var_w = 1
        var_e = var_q >> var_w

        self.assertEqual(var_e, 2)

    def test_shift_right_8_1(self):
        var_q = 8
        var_w = 1
        var_e = var_q >> var_w

        self.assertEqual(var_e, 4)
