class DefSpec:
    # def test_function_definiton(self):
    #     var_q = 1
    #     var_w = 1
    #     var_e = 0

    #     def mycall():
    #         var_e = var_q + var_w

    #     mycall()

    #     self.assertEqual(var_e, 0)

    # def test_function_definiton_with_global(self):
    #     a = 1
    #     b = 1
    #     c = 0

    #     def mycall():
    #         global c
    #         c = a + b

    #     self.assertEqual(c, 2)

    def test_function_return_three(self):
        var_q = 1

        def three():
            return 3

        var_q = three()

        self.assertEqual(var_q, 3)

    def test_function_return_five(self):
        var_q = 1

        def five():
            return 5

        var_q = five()

        self.assertEqual(var_q, 5)
