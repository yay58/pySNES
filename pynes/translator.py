import ast


class PythonTo6502:
    def __init__(self):
        self.output = []
        self.label_count = 0
        self.context_loop_end_label = None

    def translate(self, python_code):
        # Parse Python code into an AST
        tree = ast.parse(python_code)

        # Traverse the AST and generate 6502 assembly code
        self.visit(tree)

        # Return the generated assembly code
        return '\n'.join(self.output)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        raise NotImplementedError(
            f'Visit method not implemented for {type(node).__name__}'
        )

    def visit_Name(self, node):
        pass

    def visit_Constant(self, node):
        return node.value

    def visit_Compare(self, node):
        left = node.left
        ops = node.ops
        comparators = node.comparators
        if len(ops) == 1 and len(comparators) == 1:
            comparator = comparators[0]

            if isinstance(left, ast.Name) and isinstance(
                comparator, ast.Constant
            ):
                self.output.append(f'LDA {left.id}')
                self.output.append(f'CMP #{comparator.n}')
            else:
                raise NotImplementedError('Unsupported comparison')
        else:
            raise NotImplementedError('Unsupported comparison')

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Assign(self, node):
        # Handle variable assignment
        var_name = node.targets[0].id
        var_value = None
        self.visit(node.value)
        if isinstance(node.value, ast.Constant):
            var_value = f'#{node.value.value}'
        elif isinstance(node.value, ast.Name):
            var_value = node.value.id

        if var_value is not None:
            self.output.append(f'LDA {var_value}')
        self.output.append(f'STA {var_name}')

    def visit_AugAssign(self, node):
        var_name = node.target.id
        value = self.visit(node.value)
        if isinstance(node.op, ast.Add):
            self.output.append(f'LDA {var_name}')
            self.output.append('CLC')
            self.output.append(f'ADC #{value}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.Sub):
            self.output.append(f'LDA {var_name}')
            self.output.append('SEC')
            self.output.append(f'SBC #{value}')
            self.output.append(f'STA {var_name}')

    def visit_BinOp(self, node):
        # Handle binary operations
        left = node.left
        right = node.right
        left_value = left.id
        right_value = right.id
        if isinstance(node.op, ast.Add):
            self.output.append(f'LDA {left_value}')
            self.output.append('CLC')
            self.output.append(f'ADC {right_value}')
        elif isinstance(node.op, ast.Sub):
            self.output.append(f'LDA {left_value}')
            self.output.append('SEC')
            self.output.append(f'SBC {right_value}')
        else:
            raise NotImplementedError(
                f'Unsupported BinOp {type(node.op).__name__}'
            )

    def visit_If(self, node):
        self.visit(node.test)
        true_label = self._generate_label()
        end_label = self._generate_label()
        if len(node.test.ops) == 1:
            op = node.test.ops[0]
            if isinstance(op, ast.Eq):
                self.output.append(f'BEQ {true_label}')
            elif isinstance(op, ast.NotEq):
                self.output.append(f'BNE {true_label}')
            elif isinstance(op, ast.Lt):
                self.output.append(f'BMI {true_label}')
            elif isinstance(op, ast.Gt):
                self.output.append(f'BPL {true_label}')
            else:
                raise NotImplementedError(
                    f'Operators not supported {type(op).__name__}'
                )
        else:
            raise NotImplementedError('Multiple operators not supported')
        for stmt in node.orelse:
            self.visit(stmt)
        self.output.append(f'JMP {end_label}')
        self.output.append(f'{true_label}:')
        for stmt in node.body:
            self.visit(stmt)
        self.output.append(f'{end_label}:')
        self.output.append('NOP')   # TODO: remove this NOP

    def visit_While(self, node):
        # Generate code for while loop
        start_label = self._generate_label()
        true_label = self._generate_label()
        end_label = self._generate_label()
        self.output.append(f'{start_label}:')
        self.visit(node.test)
        if len(node.test.ops) == 1:
            op = node.test.ops[0]
            if isinstance(op, ast.Eq):
                self.output.append(f'BEQ {true_label}')
            elif isinstance(op, ast.NotEq):
                self.output.append(f'BNE {true_label}')
            elif isinstance(op, ast.Lt):
                self.output.append(f'BMI {true_label}')
            elif isinstance(op, ast.Gt):
                self.output.append(f'BPL {true_label}')
            else:
                raise NotImplementedError(
                    f'Operators not supported {type(op).__name__}'
                )
        else:
            raise NotImplementedError('Multiple operators not supported')
        self.output.append(f'JMP {end_label}')
        self.output.append(f'{true_label}:')
        self.context_loop_end_label = end_label
        for stmt in node.body:
            self.visit(stmt)
        self.context_loop_end_label = None
        self.output.append(f'JMP {start_label}')
        self.output.append(f'{end_label}:')
        self.output.append('NOP')   # TODO: remove this NOP

    def visit_Break(self, node):
        if self.context_loop_end_label is not None:
            self.output.append(f'JMP {self.context_loop_end_label}')
        else:
            raise NotImplementedError(f'No loop to break')

    def _generate_label(self):
        label = f'label_{self.label_count}'
        self.label_count += 1
        return label
