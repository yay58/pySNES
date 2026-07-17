"""Hello World demo specs: simple text rendering."""

from unittest import TestCase

from pynes.tests.mixins.demos import load_runner, text


class HelloWorldSpec:

    def get_hello_world_text(self):
        raise NotImplementedError()

    def when_hello_world_demos_runs(self):
        raise NotImplementedError()

    def assert_text(self, x, y, expected):
        raise NotImplementedError()

    def assert_hello_world_text(self, x, y):
        self.assert_text(12, 14, self.get_hello_world_text())

    def test_hello_world_draw(self):

        self.when_hello_world_demos_runs()


class HelloWorldDemoTest(HelloWorldSpec, TestCase):
    demo_filename = 'hello.py'

    def get_demo_filename(self):
        return self.demo_filename

    def get_hello_world_text(self):
        return b'HELLO WORLD!'

    def when_hello_world_demos_runs(self):
        self.runner = load_runner(self.get_demo_filename())

    def assert_hello_world_text(self, x, y):
        self.assertEqual(
            text(self.runner, x, y, len(self.get_hello_world_text())),
            self.get_hello_world_text(),
        )


class HelloWorld1DemoTest(HelloWorldDemoTest):
    demo_filename = 'hello_1.py'


class HelloWorld2DemoTest(HelloWorldDemoTest):
    demo_filename = 'hello_2.py'
