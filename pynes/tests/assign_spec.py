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

    def test_assign_variable(self):
        var_q = 5
        var_e = var_q

        self.assertEqual(var_e, 5)

    def test_assign_augment_2_plus_1_with_variable(self):
        var_q = 2
        var_e = 1
        var_e += var_q

        self.assertEqual(var_e, 3)

    def test_assign_augment_2_plus_2_with_variable(self):
        var_q = 2
        var_e = 2
        var_e += var_q

        self.assertEqual(var_e, 4)

    def test_assign_augment_2_minus_1_with_variable(self):
        var_q = 1
        var_e = 2
        var_e -= var_q

        self.assertEqual(var_e, 1)

    def test_assign_augment_2_minus_2_with_variable(self):
        var_q = 2
        var_e = 2
        var_e -= var_q

        self.assertEqual(var_e, 0)

    # def test_assign_augment_with_add(self):
    #     var_q = 1
    #     var_e = 2
    #     var_w = 3
    #     var_w += var_q + var_e

    #     self.assertEqual(var_e, 6)


    # def test_assign_multiple(self):
    #     var_q = var_w = 22

    #     self.assertEqual(var_q, 22)
    #     self.assertEqual(var_w, 22)

    # def test_tuple_assign(self):
    #     var_q, var_w = 30, 31

    #     self.assertEqual(var_q, 30)
    #     self.assertEqual(var_w, 31)
