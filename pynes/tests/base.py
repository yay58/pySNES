import ast
import inspect
from pynes.translator import PythonTo6502
from nesasm.compiler import lexical, semantic, syntax, Cartridge
from nesasm.tests.bridge import Py65CPUBridge


class CodeFilter(ast.NodeTransformer):
    def visit_Expr(self, node):
        # TODO: check this
        return None

    def visit_FunctionDef(self, node):
        if node.name.startswith('test_'):
            new_body = []
            for stmt in node.body:
                new_stmt = self.visit(stmt)
                if new_stmt is not None:
                    new_body.append(new_stmt)
            return new_body
        return self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith(
            'assert'
        ):
            return None
        else:
            return self.generic_visit(node)


class AssertFilter(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        if node.name.startswith('test_'):
            new_body = []
            for stmt in node.body:
                new_stmt = self.visit(stmt)
                if (
                    new_stmt is not None
                    and isinstance(new_stmt, ast.Expr)
                    and new_stmt.value is not None
                    and isinstance(new_stmt.value, ast.Call)
                    and isinstance(new_stmt.value.func, ast.Attribute)
                    and new_stmt.value.func.attr.startswith('assert')
                ):
                    new_body.append(new_stmt)
            return new_body
        return self.generic_visit(node)


def attach_test(self, code_tree, asserts_tree):
    def test(self):
        # opcodes = self.compile()
        translator = PythonTo6502()
        asm_code = translator.translate(code_tree)
        print(asm_code)
        start_addr = 0xC000
        cart = Cartridge()
        cart.set_org(start_addr)
        labels = dict(var_q=0, var_w=1, var_e=2)
        opcodes = semantic(
            syntax(lexical(asm_code)),
            False,
            cart=cart,
            labels=labels,
        )
        self._execute(opcodes)
        context = {'self': self}
        for label, address in labels.items():
            context[label] = self.cpu.memory_fetch(address)
        print(context)
        executable = compile(asserts_tree, '<string>', 'exec')
        exec(executable, {}, context)

    return test


class MetaNESTest(type):
    def __new__(cls, name, bases, dct):
        klass = super().__new__(cls, name, bases, dct)

        tests = [
            method_name
            for method_name in dir(klass)
            if callable(getattr(klass, method_name))
            and method_name.startswith('test_')
        ]

        filter_code = CodeFilter()
        filter_assert = AssertFilter()

        def setUp(self):
            self.cpu = Py65CPUBridge()

        def _compile(self, code_tree, labels=None):
            if labels is None:
                labels = dict(var_q=0, var_w=1, var_e=2)
            translator = PythonTo6502()
            asm_code = translator.translate(code_tree)
            start_addr = 0xC000
            cart = Cartridge()
            cart.set_org(start_addr)
            return semantic(
                syntax(lexical(asm_code)),
                False,
                cart=cart,
                labels=labels,
            )

        def _execute(self, opcodes):
            addr = 0
            start_addr = 0xC000
            self.cpu.cpu_pc(start_addr)
            for addr, val in enumerate(opcodes, start=start_addr):
                self.cpu.memory_set(addr, val)
            stop_addr = addr + 1

            while self.cpu.cpu.pc < stop_addr:
                self.cpu.execute()

        for test in tests:
            setattr(klass, 'setUp', setUp)
            setattr(klass, '_compile', _compile)
            setattr(klass, '_execute', _execute)
            method = getattr(klass, test)
            lines = inspect.getsourcelines(method)
            code = ''
            for line in lines[0]:
                code += line[4:]
            code_tree = filter_code.visit(ast.parse(code))
            ast.fix_missing_locations(code_tree)
            asserts_tree = filter_assert.visit(ast.parse(code))
            ast.fix_missing_locations(asserts_tree)
            setattr(klass, test, attach_test(klass, code_tree, asserts_tree))

        return klass
