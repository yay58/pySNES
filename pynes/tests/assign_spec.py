from unittest import skip


class AssignSpec:
    def test_asssign(self):
        var_q = 1
        var_q = 2

        self.assertEqual(var_q, 2)

    def test_sequencial_assign(self):
        var_q = 1
        var_w = 1
        var_e = 1
        var_q = 2
        var_w = 2
        var_e = 2

        self.assertEqual(var_q, 2)
        self.assertEqual(var_w, 2)
        self.assertEqual(var_e, 2)

    def test_assign_augment_1_plus_1(self):
        var_q = 1
        var_q += 1

        self.assertEqual(var_q, 2)

    def test_assign_augment_2_plus_2(self):
        var_q = 2
        var_q += 2

        self.assertEqual(var_q, 4)

    def test_assign_augment_3_minus_1(self):
        var_e = 3
        var_e -= 1

        self.assertEqual(var_e, 2)

    def test_assign_augment_2_minus_2(self):
        var_e = 2
        var_e -= 2

        self.assertEqual(var_e, 0)

    # @skip('TODO')
    # def test_assign_multiple(self):
    #     var_q = var_w = 22

    #     self.assertEqual(var_q, 22)
    #     self.assertEqual(var_w, 22)

    # @skip('TODO')
    # def test_tuple_assign(self):
    #     var_q, var_w = 30, 31

    #     self.assertEqual(var_q, 30)
    #     self.assertEqual(var_w, 31)
