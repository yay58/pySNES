class FibonacciSpec:
    # NOTE: results are 8-bit, so fibonacci is only defined up to
    # fib(13) = 233

    def test_fibonacci_with_while(self):
        var_a = 0
        var_b = 1
        var_n = 10
        while var_n > 0:
            var_next = var_a + var_b
            var_a = var_b
            var_b = var_next
            var_n -= 1

        self.assertEqual(var_a, 55)

    def test_fibonacci_with_function(self):
        def fibonacci(n):
            a = 0
            b = 1
            while n > 0:
                next_value = a + b
                a = b
                b = next_value
                n -= 1
            return a

        var_f = fibonacci(10)

        self.assertEqual(var_f, 55)

    def test_fibonacci_with_generator(self):
        def fibonacci(n):
            a = 0
            b = 1
            while n > 0:
                next_value = a + b
                a = b
                b = next_value
                yield a
                n -= 1

        for value in fibonacci(10):
            var_f = value

        self.assertEqual(var_f, 55)

    def test_fibonacci_with_generator_array_enumerate(self):
        def fibonacci(n):
            a = 0
            b = 1
            while n > 0:
                next_value = a + b
                a = b
                b = next_value
                yield a
                n -= 1

        var_array = [0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(fibonacci(8)):
            var_array[index] = value

        self.assertEqual(var_array, [1, 1, 2, 3, 5, 8, 13, 21])
