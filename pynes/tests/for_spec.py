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

