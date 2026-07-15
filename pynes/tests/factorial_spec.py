class FactorialSpec:
    # NOTE: results are 8-bit, so factorial is only defined up to 5! = 120

    def test_multiply_constants(self):
        var_a = 3 * 4

        self.assertEqual(var_a, 12)

    def test_multiply_variables(self):
        var_a = 6
        var_b = 7
        var_c = var_a * var_b

        self.assertEqual(var_c, 42)

    def test_multiply_by_zero(self):
        var_a = 5
        var_b = 0
        var_c = var_a * var_b

        self.assertEqual(var_c, 0)

    def test_factorial_of_zero(self):
        def factorial(n):
            result = 1
            while n > 1:
                result = result * n
                n -= 1
            return result

        var_f = factorial(0)

        self.assertEqual(var_f, 1)

    def test_factorial_of_one(self):
        def factorial(n):
            result = 1
            while n > 1:
                result = result * n
                n -= 1
            return result

        var_f = factorial(1)

        self.assertEqual(var_f, 1)

    def test_factorial_of_three(self):
        def factorial(n):
            result = 1
            while n > 1:
                result = result * n
                n -= 1
            return result

        var_f = factorial(3)

        self.assertEqual(var_f, 6)

    def test_factorial_of_five(self):
        def factorial(n):
            result = 1
            while n > 1:
                result = result * n
                n -= 1
            return result

        var_f = factorial(5)

        self.assertEqual(var_f, 120)
