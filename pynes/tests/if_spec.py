class IfSpec:
    def test_if_equal_number_1(self):
        var_q = 1
        var_w = 0

        if var_q == 1:
            var_w = 2

        self.assertEqual(var_w, 2)

    def test_if_equal_number_2(self):
        var_q = 2
        var_w = 0

        if var_q == 2:
            var_w = 3

        self.assertEqual(var_w, 3)

    def test_if_not_called(self):
        var_q = 1
        var_w = 2

        if var_q == 2:
            var_w = 3

        self.assertEqual(var_w, 2)

    def test_if_equal_else(self):
        var_q = 1
        var_w = 2

        if var_q == 2:
            var_w = 3
        else:
            var_w = 4

        self.assertEqual(var_w, 4)

    def test_if_not_equal_else(self):
        var_q = 1
        var_w = 2

        if var_q != 2:
            var_w = 3
        else:
            var_w = 4

        self.assertEqual(var_w, 3)

    def test_elif_number(self):
        var_q = 3
        var_w = 0

        if var_q == 2:
            var_w = 2
        elif var_q == 3:
            var_w = 3

        self.assertEqual(var_w, 3)

    def test_elif_else_number(self):
        var_q = 1
        var_w = 0

        if var_q == 2:
            var_w = 2
        elif var_q == 3:
            var_w = 3
        else:
            var_w = 4

        self.assertEqual(var_w, 4)

    def test_if_greater_number(self):
        var_q = 2
        var_w = 0

        if var_q > 1:
            var_w = 2

        self.assertEqual(var_w, 2)

    def test_if_greater_with_else(self):
        var_q = 5
        var_w = 2

        if var_q > 1:
            var_w = 6
        else:
            var_w = 7

        self.assertEqual(var_w, 6)

    def test_if_less_then_number(self):
        var_q = 1
        var_w = 0

        if var_q < 2:
            var_w = 2

        self.assertEqual(var_w, 2)

    def test_if_less_then_with_else(self):
        var_q = 1
        var_w = 0

        if var_q < 2:
            var_w = 2
        else:
            var_w = 3

        self.assertEqual(var_w, 2)

    def test_if_greater_equal_number(self):
        var_q = 2
        var_w = 0

        if var_q >= 2:  # Equal case
            var_w = 3

        self.assertEqual(var_w, 3)

    def test_if_greater_equal_number_gt(self):
        var_q = 3
        var_w = 0

        if var_q >= 2:  # Greater case
            var_w = 3

        self.assertEqual(var_w, 3)

    def test_if_greater_equal_with_else(self):
        var_q = 1
        var_w = 0

        if var_q >= 2:  # False case
            var_w = 3
        else:
            var_w = 4

        self.assertEqual(var_w, 4)

    def test_if_less_equal_number(self):
        var_q = 2
        var_w = 0

        if var_q <= 2:  # Equal case
            var_w = 3

        self.assertEqual(var_w, 3)

    def test_if_less_equal_number_lt(self):
        var_q = 1
        var_w = 0

        if var_q <= 2:  # Less case
            var_w = 3

        self.assertEqual(var_w, 3)

    def test_if_less_equal_with_else(self):
        var_q = 3
        var_w = 0

        if var_q <= 2:  # False case
            var_w = 3
        else:
            var_w = 4

        self.assertEqual(var_w, 4)

    # def test_if_and_else(self):
    #     var_q = 1
    #     var_w = 2
    #     var_e = 3

    #     if var_q == 1 and var_w == 2:
    #         var_e = 4

    #     self.assertEqual(var_e, 4)

    def test_if_assign(self):
        var_q = 1

        var_w = 2 if var_q == 1 else 3

        self.assertEqual(var_w, 2)

    def test_if_not_equal_assign_variable(self):
        var_q = 1
        var_w = 1
        var_e = 2

        if var_q != var_w:
            var_e = var_w

        self.assertNotEqual(var_e, var_q)
        self.assertNotEqual(var_e, var_w)
        self.assertEqual(var_e, 2)

    # def test_if_true(self):
    #     var_a, var_b = 1
    #     var_c = 2

    #     if True:
    #         var_c = var_a

    #     self.assertEqual(var_a, var_c)
    #     self.assertNotEqual(var_a, var_b)
    #     self.assertEqual(var_c, 1)

    # def test_if_false(self):
    #     var_a, var_b = 1
    #     var_c = 2

    #     if False:
    #         var_c = var_a

    #     self.assertEqual(var_a, 1)
    #     self.assertEqual(var_a, var_b)
    #     self.assertEqual(var_c, 2)

    # def test_if_greater_than_2(self):
    #     var_a = 1
    #     var_b = 2
    #     var_c = 0

    #     if var_a > var_b:
    #         var_c = var_a

    #     self.assertEqual(var_c, 0)

    # def test_if_greater_than_else(self):
    #     var_a = 2
    #     var_b = 1
    #     var_c = 0

    #     if var_a > var_b:
    #         var_c = var_a
    #     else:
    #         var_c = var_b

    #     self.assertEqual(var_c, var_a)
    #     self.assertEqual(var_c, 2)
