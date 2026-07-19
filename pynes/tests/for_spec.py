class ForSpec:
    def test_for_range_stop(self):
        var_acc = 0

        for var_i in range(5):
            var_acc += 1

        self.assertEqual(var_acc, 5)

    def test_for_range_sum_index(self):
        var_acc = 0

        for var_i in range(5):
            var_acc += var_i

        self.assertEqual(var_acc, 10)

    def test_for_range_start_stop(self):
        var_acc = 0

        for var_i in range(2, 6):
            var_acc += 1

        self.assertEqual(var_acc, 4)

    def test_for_range_start_stop_sum_index(self):
        var_acc = 0

        for var_i in range(2, 6):
            var_acc += var_i

        self.assertEqual(var_acc, 14)

    def test_for_range_step(self):
        var_acc = 0

        for var_i in range(0, 10, 2):
            var_acc += 1

        self.assertEqual(var_acc, 5)

    def test_for_range_step_sum_index(self):
        var_acc = 0

        for var_i in range(0, 10, 2):
            var_acc += var_i

        self.assertEqual(var_acc, 20)

    def test_for_range_variable_stop(self):
        var_n = 3
        var_acc = 0

        for var_i in range(var_n):
            var_acc += 2

        self.assertEqual(var_acc, 6)

    def test_for_range_variable_start_stop(self):
        var_s = 1
        var_n = 4
        var_acc = 0

        for var_i in range(var_s, var_n):
            var_acc += 1

        self.assertEqual(var_acc, 3)

    def test_for_not_executed(self):
        var_acc = 1

        for var_i in range(0):
            var_acc = 9

        self.assertEqual(var_acc, 1)

    def test_for_break(self):
        var_acc = 0

        for var_i in range(10):
            if var_i == 3:
                break
            var_acc += 1

        self.assertEqual(var_acc, 3)

    def test_for_continue(self):
        var_acc = 0

        for var_i in range(5):
            if var_i == 2:
                continue
            var_acc += 1

        self.assertEqual(var_acc, 4)

    def test_nested_for(self):
        var_acc = 0

        for var_i in range(3):
            for var_j in range(4):
                var_acc += 1

        self.assertEqual(var_acc, 12)

    def test_for_after_for(self):
        var_acc = 0

        for var_i in range(2):
            var_acc += 1

        for var_j in range(3):
            var_acc += 1

        self.assertEqual(var_acc, 5)

    def test_for_with_yield_function(self):
        def get_range():
            for var_i in range(3):
                yield var_i

        var_acc = 0
        for var_i in get_range():
            var_acc += var_i

        self.assertEqual(var_acc, 3)


    def test_loop_variable_after_loop(self):
        # Python semantics: the loop variable keeps the last
        # iterated value after the loop ends
        var_acc = 0
        for var_i in range(4):
            var_acc += 1

        self.assertEqual(var_i, 3)

    def test_loop_variable_after_loop_with_step(self):
        var_acc = 0
        for var_i in range(0, 10, 3):
            var_acc += 1

        self.assertEqual(var_i, 9)

    def test_loop_variable_after_break(self):
        # break must not disturb the loop variable
        var_acc = 0
        for var_i in range(10):
            var_acc += 1
            if var_i == 4:
                break

        self.assertEqual(var_i, 4)

    def test_enumerate_index_after_loop(self):
        def counter(n):
            while n > 0:
                yield n
                n -= 1

        var_last = 0
        for var_index, var_value in enumerate(counter(5)):
            var_last = var_value

        self.assertEqual(var_index, 4)
        self.assertEqual(var_last, 1)
