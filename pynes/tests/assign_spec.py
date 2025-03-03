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

    def test_assign_edge_cases(self):
        # Test max 8-bit value
        var_a = 255
        self.assertEqual(var_a, 255)

        # Test min value
        var_b = 0
        self.assertEqual(var_b, 0)

    def test_assign_with_expressions(self):
        var_x = 5
        var_y = 3

        # Test addition in assignment
        var_z = var_x + var_y
        self.assertEqual(var_z, 8)

        # Test subtraction in assignment
        var_w = var_x - var_y
        self.assertEqual(var_w, 2)

        # Test compound expression
        var_v = var_x + var_y - 2
        self.assertEqual(var_v, 6)

    def test_multiple_assignments(self):
        # Test multiple assignments in sequence
        var_x = 1
        var_y = var_x
        var_z = var_y

        self.assertEqual(var_x, 1)
        self.assertEqual(var_y, 1)
        self.assertEqual(var_z, 1)

    def test_assign_with_operations(self):
        # Test assigning result of operation
        var_a = 5
        var_b = var_a + 2
        var_c = var_b - 1

        self.assertEqual(var_a, 5)
        self.assertEqual(var_b, 7)
        self.assertEqual(var_c, 6)

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

    def test_assign_augment_with_add(self):
        var_q = 1
        var_e = 2
        var_w = 3
        var_w += var_q + var_e

        self.assertEqual(var_w, 6)

    def test_assign_multiple(self):
        var_q = var_w = 22

        self.assertEqual(var_q, 22)
        self.assertEqual(var_w, 22)

    def test_tuple_assign(self):
        var_q, var_w = 30, 31

        self.assertEqual(var_q, 30)
        self.assertEqual(var_w, 31)

    def test_increment_direct(self):
        var_q = 41
        var_q += 1  # This should use INC instead of ADC
        self.assertEqual(var_q, 42)

    def test_decrement_direct(self):
        var_q = 43
        var_q -= 1  # This should use DEC instead of SBC
        self.assertEqual(var_q, 42)

    def test_increment_multiple(self):
        var_q = 40
        var_q += 1  # First increment
        var_q += 1  # Second increment
        self.assertEqual(var_q, 42)

    def test_decrement_multiple(self):
        var_q = 44
        var_q -= 1  # First decrement
        var_q -= 1  # Second decrement
        self.assertEqual(var_q, 42)
