class FunctionSpec:
    def test_function_no_args(self):
        def get_five():
            return 5

        var_a = get_five()

        self.assertEqual(var_a, 5)

    def test_function_with_arg(self):
        def add_three(n):
            return n + 3

        var_a = add_three(4)

        self.assertEqual(var_a, 7)

    def test_function_with_variable_arg(self):
        def add_two(n):
            return n + 2

        var_x = 5
        var_y = add_two(var_x)

        self.assertEqual(var_y, 7)

    def test_function_with_two_args(self):
        def add(a, b):
            return a + b

        var_r = add(3, 4)

        self.assertEqual(var_r, 7)

    def test_function_with_local_var(self):
        def compute(n):
            result = n + 1
            result += 2
            return result

        var_a = compute(1)

        self.assertEqual(var_a, 4)

    def test_function_called_twice(self):
        def add_one(n):
            return n + 1

        var_a = add_one(1)
        var_b = add_one(var_a)

        self.assertEqual(var_a, 2)
        self.assertEqual(var_b, 3)

    def test_two_functions(self):
        def add_one(n):
            return n + 1

        def sub_one(n):
            return n - 1

        var_a = add_one(5)
        var_b = sub_one(5)

        self.assertEqual(var_a, 6)
        self.assertEqual(var_b, 4)

    def test_function_with_same_param_names(self):
        def add_ten(n):
            return n + 10

        def add_twenty(n):
            return n + 20

        var_a = add_ten(1)
        var_b = add_twenty(1)

        self.assertEqual(var_a, 11)
        self.assertEqual(var_b, 21)

    def test_function_called_in_loop(self):
        def add_one(n):
            return n + 1

        var_a = 0
        for var_i in range(5):
            var_a = add_one(var_a)

        self.assertEqual(var_a, 5)

    def test_function_with_condition(self):
        def clamp_at_ten(n):
            if n > 10:
                return 10
            return n

        var_a = clamp_at_ten(15)
        var_b = clamp_at_ten(7)

        self.assertEqual(var_a, 10)
        self.assertEqual(var_b, 7)
