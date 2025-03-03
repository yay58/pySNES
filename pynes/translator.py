import ast
from functools import wraps


def debug_comment(func):
    @wraps(func)
    def wrap_visit(self, node):
        self.comment(node)
        return func(self, node)

    return wrap_visit


class Ident:
    def __init__(self, name):
        self.name = name
        self.assigns = 0
        self.address = None
        self.initial_value = None

    @property
    def label(self):
        return self.name


class VarTable(ast.NodeVisitor):
    def __init__(self):
        self.vars = {}

    def get_var(self, name):
        if name not in self.vars:
            self.vars[name] = Ident(name)
        return self.vars[name]

    def visit_Name(self, node: ast.Name):
        self.get_var(node.id)
        # return super().visit_Assign(node)

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1:
            name = node.targets[0].id
            var = self.get_var(name)
            var.assigns += 1
            if isinstance(node.value, ast.Constant):
                var.initial_value = node.value.value
        else:
            raise NotImplementedError()
        # return super().visit_Assign(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        self.get_var(node.target.id).assigns += 1

    def locate(self, python_code):
        self.vars = {}
        tree = ast.parse(python_code)
        self.generic_visit(tree)
        address = 0x00
        for name, value in self.vars.items():
            value.address = address
            address += 1
        return self.vars


class PythonTo6502:
    def __init__(self):
        self.output = []
        self.label_count = 0
        self.context_loop_end_label = None
        self.debug_comment = True

    def translate(self, python_code):
        # Parse Python code into an AST
        tree = ast.parse(python_code)

        # Traverse the AST and generate 6502 assembly code
        self.visit(tree)

        # Return the generated assembly code
        return '\n'.join(self.output)

    def comment(self, node):
        if not self.debug_comment:
            return
        code = ast.unparse(node).split('\n')
        for line in code:
            self.output.append(f'; {line}')

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        raise NotImplementedError(
            f'Visit method not implemented for {type(node).__name__}'
        )

    def visit_Name(self, node):
        # Handle memory location access
        if node.id.startswith('mem_'):
            addr = int(node.id.split('_')[1], 16)
            if addr < 0x100:  # Zero page
                self.output.append(f'LDA ${addr:02X}')
            else:  # Absolute addressing
                self.output.append(f'LDA ${addr:04X}')
        return node.id

    def visit_Constant(self, node):
        return node.value

    def visit_Compare(self, node):
        left = node.left
        ops = node.ops
        comparators = node.comparators
        if len(ops) == 1 and len(comparators) == 1:
            comparator = comparators[0]

            if isinstance(left, ast.Name):
                if isinstance(comparator, ast.Constant):
                    self.output.append(f'LDA {left.id}')
                    self.output.append(f'CMP #{comparator.n}')
                elif isinstance(comparator, ast.Name):
                    self.output.append(f'LDA {left.id}')
                    self.output.append(f'CMP {comparator.id}')
                else:
                    raise NotImplementedError(
                        'Unsupported comparison value type'
                    )
            else:
                raise NotImplementedError(
                    'Unsupported comparison left operand type'
                )
        else:
            raise NotImplementedError('Unsupported comparison')

    def visit_Module(self, node):
        # Set parent references for the AST
        for stmt in ast.walk(node):
            for child in ast.iter_child_nodes(stmt):
                setattr(child, '_parent', stmt)
        # Visit all statements
        for stmt in node.body:
            self.visit(stmt)

    @debug_comment
    def visit_Assign(self, node):
        # Handle variable assignment
        target = node.targets[0]
        var_name = target.id

        # Handle memory location assignment
        if var_name.startswith('mem_'):
            addr = int(var_name.split('_')[1], 16)
            if isinstance(node.value, ast.Name):
                # Load from variable then store to memory
                self.output.append(f'LDA {node.value.id}')
                if addr < 0x100:  # Zero page
                    self.output.append(f'STA ${addr:02X}')
                else:  # Absolute addressing
                    self.output.append(f'STA ${addr:04X}')
            return

        # Load the value into the accumulator
        if isinstance(node.value, ast.Constant):
            self.output.append(f'LDA #{node.value.value}')
        elif isinstance(node.value, ast.Name):
            self.output.append(f'LDA {node.value.id}')
        else:
            # Visit the value first - this handles IfExp and other expressions
            self.visit(node.value)
        # Store the result in the target variable
        self.output.append(f'STA {var_name}')

    @debug_comment
    def visit_AugAssign(self, node):
        var_name = node.target.id
        if isinstance(node.value, ast.Constant):
            var_value = node.value.value
            var_value_str = f'#{var_value}'
        elif isinstance(node.value, ast.Name):
            var_value = None
            var_value_str = node.value.id

        if isinstance(node.op, ast.Add):
            if isinstance(node.value, ast.Constant) and var_value == 1:
                # Use INC for += 1
                self.output.append(f'INC {var_name}')
            else:
                self.output.append(f'LDA {var_name}')
                self.output.append('CLC')
                self.output.append(f'ADC {var_value_str}')
                self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.Sub):
            if isinstance(node.value, ast.Constant) and var_value == 1:
                # Use DEC for -= 1
                self.output.append(f'DEC {var_name}')
            else:
                self.output.append(f'LDA {var_name}')
                self.output.append('SEC')
                self.output.append(f'SBC {var_value_str}')
                self.output.append(f'STA {var_name}')

    def visit_BinOp(self, node):
        # Handle binary operations
        left = node.left
        right = node.right
        if isinstance(left, ast.Name):
            left_value = left.id
        elif isinstance(left, ast.Constant):
            left_value = f'#{left.value}'
        if isinstance(right, ast.Name):
            right_value = right.id
        elif isinstance(right, ast.Constant):
            right_value = f'#{right.value}'

        # Get parent context to find where to store the result
        parent = getattr(node, '_parent', None)
        target_var = None
        if isinstance(parent, ast.Assign):
            target_var = parent.targets[0].id

        if isinstance(node.op, ast.Add):
            self.output.append(f'LDA {left_value}')
            self.output.append('CLC')
            self.output.append(f'ADC {right_value}')
        elif isinstance(node.op, ast.Sub):
            self.output.append(f'LDA {left_value}')
            self.output.append('SEC')
            self.output.append(f'SBC {right_value}')
        elif isinstance(node.op, ast.BitAnd):
            self.output.append(f'LDA {left_value}')
            self.output.append(f'AND {right_value}')
        elif isinstance(node.op, ast.BitOr):
            self.output.append(f'LDA {left_value}')
            self.output.append(f'ORA {right_value}')
        elif isinstance(node.op, ast.BitXor):
            self.output.append(f'LDA {left_value}')
            self.output.append(f'EOR {right_value}')
        elif isinstance(node.op, ast.LShift):
            self.output.append(f'LDA {left_value}')
            # For each shift count, we'll ASL (Arithmetic Shift Left)
            if isinstance(right, ast.Constant):
                for _ in range(right.value):
                    self.output.append('ASL A')
            else:
                self.output.append(f'LDX {right_value}')
                shift_loop = self._generate_label()
                self.output.append(f'{shift_loop}:')
                self.output.append('ASL A')
                self.output.append('DEX')
                self.output.append(f'BNE {shift_loop}')
        elif isinstance(node.op, ast.RShift):
            self.output.append(f'LDA {left_value}')
            # For each shift count, we'll LSR (Logical Shift Right)
            if isinstance(right, ast.Constant):
                for _ in range(right.value):
                    self.output.append('LSR A')
            else:
                self.output.append(f'LDX {right_value}')
                shift_loop = self._generate_label()
                self.output.append(f'{shift_loop}:')
                self.output.append('LSR A')
                self.output.append('DEX')
                self.output.append(f'BNE {shift_loop}')

        # Store the result if we're in an assignment context
        if target_var:
            self.output.append(f'STA {target_var}')

    @debug_comment
    def visit_BoolOp(self, node):
        """Handle boolean operations like AND/OR"""
        if isinstance(node.op, ast.And):
            # For AND, we need all conditions to be true
            false_label = self._generate_label()
            for value in node.values:
                if isinstance(value, ast.Compare):
                    self.visit(value)
                    # For each comparison, if it's false, skip to end
                    if len(value.ops) == 1:
                        op = value.ops[0]
                        if isinstance(op, ast.Eq):
                            self.output.append(f'BNE {false_label}')
                        elif isinstance(op, ast.NotEq):
                            self.output.append(f'BEQ {false_label}')
                        elif isinstance(op, ast.Lt):
                            self.output.append(f'BCS {false_label}')
                        elif isinstance(op, ast.Gt):
                            self.output.append(f'BCC {false_label}')
                        elif isinstance(op, ast.GtE):
                            self.output.append(f'BCC {false_label}')
                        elif isinstance(op, ast.LtE):
                            self.output.append(f'BCS {false_label}')
            return false_label
        else:
            raise NotImplementedError('Only AND operator is supported')

    @debug_comment
    def visit_If(self, node):
        self.comment(node.test)
        true_label = self._generate_label()
        end_label = self._generate_label()

        # Handle boolean operations (AND/OR)
        if isinstance(node.test, ast.BoolOp):
            false_label = self.visit(node.test)
            # Execute true block if all conditions passed
            for stmt in node.body:
                self.comment(stmt)
                self.visit(stmt)
            self.output.append(f'JMP {end_label}')
            # Handle false case
            self.output.append(f'{false_label}:')
            for stmt in node.orelse:
                self.comment(stmt)
                self.visit(stmt)
            self.output.append(f'{end_label}:')
            return

        # Handle simple comparisons
        self.visit(node.test)
        if len(node.test.ops) == 1:
            op = node.test.ops[0]
            if isinstance(op, ast.Eq):
                self.output.append(f'BEQ {true_label}')
            elif isinstance(op, ast.NotEq):
                self.output.append(f'BNE {true_label}')
            elif isinstance(op, ast.Lt):
                self.output.append(
                    f'BCC {true_label}'
                )  # Branch if carry clear (less than)
            elif isinstance(op, ast.Gt):
                self.output.append(f'BEQ skip_{true_label}')  # Skip if equal
                self.output.append(
                    f'BCS {true_label}'
                )  # Branch if carry set (greater than or equal)
                self.output.append(f'skip_{true_label}:')
            elif isinstance(op, ast.GtE):
                self.output.append(
                    f'BCS {true_label}'
                )  # Branch if carry set (greater than or equal)
            elif isinstance(op, ast.LtE):
                self.output.append(
                    f'BCC {true_label}'
                )  # Branch if carry clear (less than)
                self.output.append(f'BEQ {true_label}')  # Also branch if equal
            else:
                raise NotImplementedError(
                    f'Operators not supported {type(op).__name__}'
                )
        else:
            raise NotImplementedError('Multiple operators not supported')
        for stmt in node.orelse:
            self.comment(stmt)
            self.visit(stmt)
        self.output.append(f'JMP {end_label}')
        self.output.append(f'{true_label}:')
        for stmt in node.body:
            self.comment(stmt)
            self.visit(stmt)
        self.output.append(f'{end_label}:')
        self.output.append('NOP')   # TODO: remove this NOP

    def visit_While(self, node):
        # Generate code for while loop
        start_label = self._generate_label()
        end_label = self._generate_label()

        # Start of loop body
        self.output.append(f'{start_label}:')

        # Check condition
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            ops = node.test.ops
            comparators = node.test.comparators

            if len(ops) == 1 and len(comparators) == 1:
                comparator = comparators[0]
                op = ops[0]

                # Load left value
                if isinstance(left, ast.Name):
                    self.output.append(f'LDA {left.id}')
                elif isinstance(left, ast.Constant):
                    self.output.append(f'LDA #{left.n}')

                # Compare with right value
                if isinstance(comparator, ast.Constant):
                    self.output.append(f'CMP #{comparator.n}')
                elif isinstance(comparator, ast.Name):
                    self.output.append(f'CMP {comparator.id}')

                # Branch to end if condition is false
                if isinstance(op, ast.Lt):
                    self.output.append(f'BCS {end_label}')
                elif isinstance(op, ast.Gt):
                    # For A > M, we need A > M which means A >= M AND A != M
                    # Branch to end if A <= M
                    self.output.append(
                        f'BCC {end_label}'
                    )  # Branch to end if A < M
                    self.output.append(
                        f'BEQ {end_label}'
                    )  # Branch to end if A = M
                elif isinstance(op, ast.GtE):
                    self.output.append(f'BCC {end_label}')
                elif isinstance(op, ast.LtE):
                    self.output.append(f'BCS {end_label}')
                elif isinstance(op, ast.Eq):
                    self.output.append(f'BNE {end_label}')
                elif isinstance(op, ast.NotEq):
                    self.output.append(f'BEQ {end_label}')
            else:
                raise NotImplementedError('Multiple operators not supported')
        else:
            raise NotImplementedError('Only comparisons supported in while')

        # Loop body
        self.context_loop_end_label = end_label
        for stmt in node.body:
            self.visit(stmt)
        self.context_loop_end_label = None

        # Jump back to start to check condition again
        self.output.append(f'JMP {start_label}')

        # End of loop
        self.output.append(f'{end_label}:')
        self.output.append('NOP')  # No-op instead of BRK

    def visit_Break(self, node):
        if self.context_loop_end_label is not None:
            self.output.append(f'JMP {self.context_loop_end_label}')
        else:
            raise NotImplementedError('No loop to break')

    def visit_IfExp(self, node):
        """Handle ternary operators like: x = 2 if y == 1 else 3"""
        end_label = self._generate_label()
        false_label = self._generate_label()

        # Visit the test condition
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            ops = node.test.ops
            comparators = node.test.comparators

            if len(ops) == 1 and len(comparators) == 1:
                comparator = comparators[0]
                op = ops[0]

                # Load left value
                if isinstance(left, ast.Name):
                    self.output.append(f'LDA {left.id}')
                elif isinstance(left, ast.Constant):
                    self.output.append(f'LDA #{left.n}')

                # Compare with right value
                if isinstance(comparator, ast.Constant):
                    self.output.append(f'CMP #{comparator.n}')
                elif isinstance(comparator, ast.Name):
                    self.output.append(f'CMP {comparator.id}')

                # Branch based on comparison
                if isinstance(op, ast.Eq):
                    self.output.append(f'BEQ {false_label}')
                elif isinstance(op, ast.NotEq):
                    self.output.append(f'BNE {false_label}')
                elif isinstance(op, ast.Lt):
                    self.output.append(f'BCC {false_label}')
                elif isinstance(op, ast.Gt):
                    self.output.append(f'BCS {false_label}')
                elif isinstance(op, ast.GtE):
                    self.output.append(f'BCC {false_label}')
                elif isinstance(op, ast.LtE):
                    self.output.append(f'BCS {false_label}')

        # False case (condition not met)
        if isinstance(node.orelse, ast.Constant):
            self.output.append(f'LDA #{node.orelse.n}')
        elif isinstance(node.orelse, ast.Name):
            self.output.append(f'LDA {node.orelse.id}')
        self.output.append(f'JMP {end_label}')

        # True case (condition met)
        self.output.append(f'{false_label}:')
        if isinstance(node.body, ast.Constant):
            self.output.append(f'LDA #{node.body.n}')
        elif isinstance(node.body, ast.Name):
            self.output.append(f'LDA {node.body.id}')

        # End of if expression
        self.output.append(f'{end_label}:')

    def _generate_label(self):
        label = f'label_{self.label_count}'
        self.label_count += 1
        return label
