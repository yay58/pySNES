import ast


class PythonTo6502:
    def __init__(self):
        self.output = []
        self.label_count = 0

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
        value = self.visit(node.value)
        self.output.append(f'LDA #{value}')
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
        else:
            raise NotImplementedError(
                f'Operation not supported {type(node.op).__name__}'
            )

    def visit_BinOp(self, node):
        # Handle binary operations
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return f'{left}+{right}'
        elif isinstance(node.op, ast.Sub):
            return f'{left}-{right}'
        # Implement other binary operations as needed

    def _generate_label(self):
        label = f'label_{self.label_count}'
        self.label_count += 1
        return label
