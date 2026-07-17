"""Factorial demo specs"""


class FactorialOneLineSpec:

    def get_factorial_factor(self):
        raise NotImplementedError()

    def when_factorial_demo_runs(self):
        raise NotImplementedError()

    def assert_text(self, x, y, expected):
        raise NotImplementedError()

    def assert_factorial_result(self, x, y):
        raise NotImplementedError()

    def test_label_draw(self):

        self.when_factorial_demo_runs()

        self.assert_text(12, 14, b'%d! = ' % self.get_factorial_factor())

    def test_result_printed_after_the_label(self):
        self.when_factorial_demo_runs()

        self.assert_factorial_result(17, 14)


class FactorialMultilineSpec:

    def when_factorial_demo_runs(self):
        raise NotImplementedError()

    def assert_each_line_has_its_factorial(self):
        raise NotImplementedError()

    def test_each_line_show_its_factorial(self):
        self.when_factorial_demo_runs()

        self.assert_each_line_has_its_factorial()
