from unittest import TestCase
from os.path import abspath, dirname, join
from pynes.tests.base import MetaVarTableTest

here = abspath(dirname(__file__))
fixture_path = abspath(join(here, '..', '..', '..', 'fixtures'))


class VarTableTest(TestCase, metaclass=MetaVarTableTest):
    def test_var_a(self):
        a = 1

        self.assertIn('a', self.vars)

    def test_var_b(self):
        b = 3

        self.assertIn('b', self.vars)

    def test_var_count_assigns(self):
        a = 1

        self.assertIn('a', self.vars)
        self.assertIsNotNone(self.vars['a'])
        self.assertEqual(self.vars['a'].assigns, 1)

    def test_var_count_assigns_a_and_b(self):
        a = 1
        b = 2 + a

        self.assertEqual(self.vars['a'].assigns, 1)
        self.assertEqual(self.vars['b'].assigns, 1)

    def test_var_count_aug_assign_a_and_b(self):
        a = 1
        b = 2
        b += a

        self.assertEqual(self.vars['a'].assigns, 1)
        self.assertEqual(self.vars['b'].assigns, 2)

    def test_var_address_a_b_c(self):
        a = 1
        b = 2
        c = 3

        self.assertEqual(self.vars['a'].address, 0)
        self.assertEqual(self.vars['b'].address, 1)
        self.assertEqual(self.vars['c'].address, 2)

    # @skip('TODO')
    # def test_var_default_number_type(self):
    #     a = 1

    #     self.assertEqual(self.vars['a'].type, 'short')

    # @skip('TODO')
    # def test_var_string_type(self):
    #     s = 'hello world'

    #     self.assertEqual(self.vars['s'].type, 'string')
