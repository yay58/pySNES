import ast
import inspect
from pynes.translator import PythonTo6502, VarTable
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


def attach_test(code_tree, asserts_tree):
    def test(self):
        opcodes = self._compile(code_tree)
        self._execute(opcodes)
        context = {'self': self}
        for v in self.vars.values():
            context[v.name] = self.cpu.memory_fetch(v.address)
        executable = compile(asserts_tree, '<string>', 'exec')
        exec(executable, {}, context)  # nosec B102

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
            vartable = VarTable()
            translator = PythonTo6502()
            self.vars = vartable.locate(code_tree)

            # Initialize labels with variable addresses
            self.labels = {}
            for var in self.vars.values():
                self.labels[var.label] = var.address
                # Initialize variable in CPU memory
                if hasattr(var, 'initial_value'):
                    self.cpu.memory_set(var.address, var.initial_value)

            # Generate assembly code
            asm_code = translator.translate(code_tree)
            print('Generated assembly:')
            print(asm_code)

            # Parse assembly to get label addresses
            tokens = lexical(asm_code)
            ast = syntax(tokens)

            # Set up cartridge
            start_addr = 0xC000
            cart = Cartridge()
            cart.set_org(start_addr)

            # First pass to collect all label references and definitions
            addr = start_addr
            for leaf in ast:
                if leaf['type'] == 'S_LABEL':
                    self.labels[leaf['value']] = addr
                elif (
                    leaf['type'] == 'S_DIRECTIVE'
                    and leaf['instruction'] == 'db'
                ):
                    addr += 1
                else:
                    addr += 1
                    # Add any label references from operands
                    if 'children' in leaf:
                        for child in leaf['children']:
                            if child['type'] == 'T_MARKER':
                                label = child['value']
                                if label not in self.labels:
                                    self.labels[label] = addr

            # Second pass to update label addresses
            addr = start_addr
            for leaf in ast:
                if leaf['type'] == 'S_LABEL':
                    self.labels[leaf['value']] = addr
                elif (
                    leaf['type'] == 'S_DIRECTIVE'
                    and leaf['instruction'] == 'db'
                ):
                    addr += 1
                else:
                    addr += 1

            # Third pass to generate code
            return semantic(
                ast,
                False,
                cart=cart,
                labels=self.labels,
            )

        def _execute(self, opcodes):
            addr = 0
            start_addr = 0xC000
            self.cpu.cpu_pc(start_addr)
            for addr, val in enumerate(opcodes, start=start_addr):
                self.cpu.memory_set(addr, val)
            stop_addr = addr + 1

            max_iterations = 1000  # Prevent infinite loops
            iterations = 0
            while self.cpu.cpu.pc < stop_addr and iterations < max_iterations:
                iterations += 1
                if iterations == max_iterations:
                    print(
                        f'Debug - var_q: {self.cpu.memory_fetch(0)}'
                    )  # Assuming var_q is at address 0
                    print(f'Debug - PC: {self.cpu.cpu.pc:04X}')
                    raise Exception(
                        f'Test exceeded {max_iterations} iterations - possible infinite loop'
                    )
                self.cpu.execute()

        def _run_asserts(self, asserts_tree):
            executable = compile(asserts_tree, '<string>', 'exec')
            context = {'self': self}
            exec(executable, {}, context)  # nosec B102

        setattr(klass, 'setUp', setUp)
        setattr(klass, '_compile', _compile)
        setattr(klass, '_execute', _execute)
        setattr(klass, '_run_asserts', _run_asserts)

        for test in tests:
            method = getattr(klass, test)
            lines = inspect.getsourcelines(method)
            code = ''
            for line in lines[0]:
                code += line[4:]
            code_tree = filter_code.visit(ast.parse(code))
            ast.fix_missing_locations(code_tree)
            asserts_tree = filter_assert.visit(ast.parse(code))
            ast.fix_missing_locations(asserts_tree)
            setattr(klass, test, attach_test(code_tree, asserts_tree))

        return klass


def gen_var_test(code_tree, asserts_tree):
    def test(self):
        self.vars = self._get_vars(code_tree)
        self._run_asserts(asserts_tree)

    return test


class MetaVarTableTest(type):
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
            self.vars = {}

        def _get_vars(self, code_tree, labels=None):
            vartable = VarTable()
            return vartable.locate(code_tree)

        def _run_asserts(self, asserts_tree):
            executable = compile(asserts_tree, '<string>', 'exec')
            context = {'self': self}
            exec(executable, {}, context)  # nosec B102

        setattr(klass, 'setUp', setUp)
        setattr(klass, '_get_vars', _get_vars)
        setattr(klass, '_run_asserts', _run_asserts)

        for test in tests:
            method = getattr(klass, test)
            lines = inspect.getsourcelines(method)
            code = ''
            for line in lines[0]:
                code += line[4:]
            code_tree = filter_code.visit(ast.parse(code))
            ast.fix_missing_locations(code_tree)
            asserts_tree = filter_assert.visit(ast.parse(code))
            ast.fix_missing_locations(asserts_tree)
            setattr(klass, test, gen_var_test(code_tree, asserts_tree))

        return klass
