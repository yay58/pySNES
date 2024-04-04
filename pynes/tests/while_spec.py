class WhileSpec:
    def test_while_equal(self):
        var_q = 0
        var_w = 0
        while var_q == 0:
            var_q = 5
            var_w += 1

        self.assertEqual(var_q, 5)
        self.assertEqual(var_w, 1)

    def test_while_if_equal_5(self):
        var_q = 0
        var_w = 0
        while var_q == 0:
            var_w += 1
            if var_w == 5:
                var_q = 2

        self.assertEqual(var_q, 2)
        self.assertEqual(var_w, 5)

    def test_while_not_equal(self):
        var_q = 1
        var_w = 0
        while var_q != 0:
            var_q = 0
            var_w += 1

        self.assertEqual(var_q, 0)
        self.assertEqual(var_w, 1)

    def test_while_less_then(self):
        var_q = 0

        while var_q < 10:
            var_q += 1

        self.assertEqual(var_q, 10)

    # def test_while_greater_then(self):
    #     var_q = 10

    #     while var_q > 1:
    #         var_q -= 1

    #     self.assertEqual(var_q, 0)

    def test_while_break(self):
        var_q = 0
        var_w = 0
        while var_q == 0:
            var_w += 1
            if var_w == 5:
                break

        self.assertEqual(var_q, 0)
        self.assertEqual(var_w, 5)
