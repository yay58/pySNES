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

    # def test_if_assign(self):
    #     var_q = 1

    #     var_w = 2 if var_q == 1 else 3

    #     self.assertEqual(var_w, 2)

    # def test_if_not_equal_assign_variable(self):
    #     var_q = 1
    #     var_w = 1
    #     var_e = 2

    #     if var_q != var_w:
    #         var_e = var_w

    #     self.assertNotEqual(var_e, var_q)
    #     self.assertNotEqual(var_e, var_w)
    #     self.assertEqual(var_e, 2)

    # def test_if_true(self):
    #     a, b = 1
    #     c = 2

    #     if True:
    #         c = a

    # def test_if_false(self):
    #     a, b = 1
    #     c = 2

    #     if False:
    #         c = a

    #     self.assertEqual(a, 1)
    #     self.assertEqual(a, b)
    #     self.assertEqual(c, 2)

    # def test_if_greater_than_2(self):
    #     a = 1
    #     b = 2
    #     c = 0

    #     if a > b:
    #         c = a

    #     self.assertEqual(c, 0)

    # def test_if_greater_than_else(self):
    #     a = 2
    #     b = 1
    #     c = 0

    #     if a > b:
    #         c = a
    #     else:
    #         c = b

    #     self.assertEqual(c, a)
    #     self.assertEqual(c, 2)
