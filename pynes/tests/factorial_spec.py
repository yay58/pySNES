from pynes.types import uint16


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

    def test_factorial_of_eight_with_uint16(self):
        def factorial(n) -> uint16:
            result = 1
            while n > 1:
                result = result * n
                n -= 1
            return result

        var_f = factorial(8)

        # TODO: self.assertEqual(var_f, 40320)

    # TODO:
    # def test_factorial_with_generator(self):
    #     def factorial(n):
    #         result = 1
    #         while n > 1:
    #             result = result * n
    #             yield result
    #             n -= 1

    #     for value in factorial(5):
    #         var_f = value

    #     self.assertEqual(var_f, 120)

    # def test_factorial_with_generator_next(self):
    #     def factorial(n):
    #         result = 1
    #         while n > 1:
    #             result = result * n
    #             yield result
    #             n -= 1

    #     generator = factorial(5)

    #     for _ in range(4):
    #         var_f = next(generator)

    #     self.assertEqual(var_f, 120)

    # def test_factorial_with_generator_array(self):
    #     def factorial(n):
    #         result = 1
    #         while n > 1:
    #             result = result * n
    #             yield result
    #             n -= 1

    #     var_array = [0,0,0,0]
    #     index = 0
    #     for value in factorial(5):
    #         var_array[index] = value
    #         index += 1

    #     self.assertEqual(var_array, [5, 20, 60, 120])

    # def test_factorial_with_generator_array_enumerate(self):
    #     def factorial(n):
    #         result = 1
    #         while n > 1:
    #             result = result * n
    #             yield result
    #             n -= 1

    #     var_array = [0,0,0,0]
    #     for index, value in enumerate(factorial(5)):
    #         var_array[index] = value

    # def test_factorial_with_generator_array_append(self):
    #     def factorial(n):
    #         result = 1
    #         while n > 1:
    #             result = result * n
    #             yield result
    #             n -= 1

    #     var_array = []
    #     for value in factorial(5):
    #         var_array.append(value)

    #     self.assertEqual(result, [5, 20, 60, 120])
