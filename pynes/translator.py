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
        self.size = 1

    @property
    def label(self):
        return self.name


class _Renamer(ast.NodeTransformer):
    def __init__(self, mapping):
        self.mapping = mapping

    def visit_Name(self, node):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node


class ScopeMangler(ast.NodeTransformer):
    """Renames function parameters and local variables to
    '<function>_<name>' so every function gets statically allocated,
    collision-free variable slots (no software stack)."""

    def visit_FunctionDef(self, node):
        local = {arg.arg for arg in node.args.args}
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        local.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                local.add(elt.id)
            elif isinstance(stmt, ast.AugAssign) and isinstance(
                stmt.target, ast.Name
            ):
                local.add(stmt.target.id)
            elif isinstance(stmt, ast.For) and isinstance(
                stmt.target, ast.Name
            ):
                local.add(stmt.target.id)
        mapping = {name: f'{node.name}_{name}' for name in local}
        renamer = _Renamer(mapping)
        for arg in node.args.args:
            arg.arg = mapping[arg.arg]
        node.body = [renamer.visit(stmt) for stmt in node.body]
        return node


TEMP_VARS = ('temp_var', 'temp_left', 'temp_right', 'temp_mul')


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

    def visit_Call(self, node: ast.Call):
        # Function names are labels, not variables
        for arg in node.args:
            self.visit(arg)

    def visit_Assign(self, node: ast.Assign):
        # Handle single and multiple assignments
        for target in node.targets:
            if isinstance(target, ast.Tuple):
                # Handle tuple unpacking
                for elt in target.elts:
                    name = elt.id
                    var = self.get_var(name)
                    var.assigns += 1
            elif isinstance(target, ast.Subscript):
                var = self.get_var(target.value.id)
                var.assigns += 1
                self.visit(target.slice)
            else:
                # Handle single assignment
                name = target.id
                var = self.get_var(name)
                var.assigns += 1
                if isinstance(node.value, ast.Constant):
                    var.initial_value = node.value.value
                elif isinstance(node.value, ast.List):
                    var.size = len(node.value.elts)
                    var.initial_value = [elt.value for elt in node.value.elts]
        self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign):
        self.get_var(node.target.id).assigns += 1
        self.visit(node.value)

    def locate(self, python_code):
        self.vars = {}
        tree = ScopeMangler().visit(ast.parse(python_code))
        self.generic_visit(tree)
        for temp in TEMP_VARS:
            self.get_var(temp)
        address = 0x00
        for name, value in self.vars.items():
            value.address = address
            address += value.size
        return self.vars


class PythonTo6502:
    def __init__(self, libraries=None):
        self.output = []
        self.label_count = 0
        self.loop_end_labels = []
        self.loop_continue_labels = []
        self.debug_comment = True
        self.externs = {}
        self.functions = {}
        for library in libraries or []:
            self.externs.update(library.externs)

    def translate(self, python_code):
        # Parse Python code into an AST, mangling function scopes
        tree = ScopeMangler().visit(ast.parse(python_code))
        ast.fix_missing_locations(tree)

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

    def visit_Expr(self, node):
        self.visit(node.value)

    def visit_Pass(self, node):
        pass

    @debug_comment
    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise NotImplementedError('Only direct calls are supported')
        name = node.func.id
        if name in self.externs:
            self.externs[name](self, node.args)
        elif name in self.functions:
            params = self.functions[name]
            if len(node.args) != len(params):
                raise NotImplementedError(
                    f'{name}() takes {len(params)} arguments '
                    f'({len(node.args)} given)'
                )
            for arg, param in zip(node.args, params):
                self._eval_to_a(arg)
                self.output.append(f'STA {param}')
            self.output.append(f'JSR {name}')
        else:
            raise NotImplementedError(f'Unknown function {name!r}')

    def _eval_to_a(self, node):
        """Evaluate an expression, leaving the result in the A register."""
        if isinstance(node, ast.Constant):
            self.output.append(f'LDA #{node.value}')
        elif isinstance(node, ast.Name):
            self.output.append(f'LDA {node.id}')
        else:
            # BinOp, Subscript and Call all leave their result in A
            self.visit(node)

    def _load_index(self, index, register='X'):
        """Load an array index into the X or Y register."""
        if isinstance(index, ast.Constant):
            self.output.append(f'LD{register} #{index.value}')
        elif isinstance(index, ast.Name):
            self.output.append(f'LD{register} {index.id}')
        else:
            raise NotImplementedError(
                'Only constant or variable array indexes are supported'
            )

    def visit_Subscript(self, node):
        """Load an array element into the A register."""
        if not isinstance(node.value, ast.Name):
            raise NotImplementedError('Only named arrays are supported')
        self._load_index(node.slice, 'X')
        self.output.append(f'LDA {node.value.id},X')

    @debug_comment
    def visit_FunctionDef(self, node):
        self.output.append(f'{node.name}:')
        for stmt in node.body:
            self.visit(stmt)
        if not (node.body and isinstance(node.body[-1], ast.Return)):
            self.output.append('RTS')

    @debug_comment
    def visit_Return(self, node):
        if node.value is not None:
            self._eval_to_a(node.value)
        self.output.append('RTS')

    def load_arg8(self, arg):
        """Load an 8-bit argument into the A register."""
        if isinstance(arg, ast.Constant):
            self.output.append(f'LDA #{arg.value}')
        elif isinstance(arg, ast.Name):
            self.output.append(f'LDA {arg.id}')
        else:
            raise NotImplementedError('Unsupported argument expression')

    def load_arg16(self, arg):
        """Load a 16-bit argument into X (high byte) and A (low byte)."""
        if isinstance(arg, ast.Constant):
            value = arg.value
            self.output.append(f'LDX #{(value >> 8) & 0xFF}')
            self.output.append(f'LDA #{value & 0xFF}')
        else:
            raise NotImplementedError(
                '16-bit variable arguments are not supported yet'
            )

    def load_arg8_x(self, arg):
        """Load an 8-bit argument into the X register."""
        if isinstance(arg, ast.Constant):
            self.output.append(f'LDX #{arg.value}')
        elif isinstance(arg, ast.Name):
            self.output.append(f'LDX {arg.id}')
        else:
            raise NotImplementedError('Unsupported argument expression')

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

            # Load the left operand into A
            if isinstance(left, ast.Name):
                self.output.append(f'LDA {left.id}')
            elif isinstance(left, ast.Subscript):
                self.visit_Subscript(left)
            elif isinstance(left, ast.Call):
                # Call leaves its return value in A
                self.visit(left)
            else:
                raise NotImplementedError(
                    'Unsupported comparison left operand type'
                )

            # Compare against the right operand
            if isinstance(comparator, ast.Constant):
                self.output.append(f'CMP #{comparator.value}')
            elif isinstance(comparator, ast.Name):
                self.output.append(f'CMP {comparator.id}')
            elif isinstance(comparator, ast.Subscript):
                if not isinstance(comparator.value, ast.Name):
                    raise NotImplementedError(
                        'Only named arrays are supported'
                    )
                self._load_index(comparator.slice, 'Y')
                self.output.append(f'CMP {comparator.value.id},Y')
            else:
                raise NotImplementedError('Unsupported comparison value type')
        else:
            raise NotImplementedError('Unsupported comparison')

    def visit_Module(self, node):
        # Set parent references for the AST
        for stmt in ast.walk(node):
            for child in ast.iter_child_nodes(stmt):
                setattr(child, '_parent', stmt)

        # Register user-defined functions first so calls can resolve
        functions = [
            stmt for stmt in node.body if isinstance(stmt, ast.FunctionDef)
        ]
        for function in functions:
            self.functions[function.name] = [
                arg.arg for arg in function.args.args
            ]

        # Visit the main flow
        for stmt in node.body:
            if not isinstance(stmt, ast.FunctionDef):
                self.visit(stmt)

        # Emit function bodies after the main flow, jumping over them
        if functions:
            end_label = self._generate_label()
            self.output.append(f'JMP {end_label}')
            for function in functions:
                self.visit(function)
            self.output.append(f'{end_label}:')
            self.output.append('NOP')

    @debug_comment
    def visit_Assign(self, node):
        # Handle array element assignment: arr[i] = value
        if isinstance(node.targets[0], ast.Subscript):
            target = node.targets[0]
            if not isinstance(target.value, ast.Name):
                raise NotImplementedError('Only named arrays are supported')
            self._eval_to_a(node.value)
            self._load_index(target.slice, 'X')
            self.output.append(f'STA {target.value.id},X')
            return

        # Handle array literal assignment: arr = [1, 2, 3]
        if isinstance(node.value, ast.List):
            array_name = node.targets[0].id
            for i, elt in enumerate(node.value.elts):
                if not isinstance(elt, ast.Constant):
                    raise NotImplementedError(
                        'Only constant array literals are supported'
                    )
                self.output.append(f'LDA #{elt.value}')
                self.output.append(f'LDX #{i}')
                self.output.append(f'STA {array_name},X')
            return

        # Handle memory location assignment first
        if not isinstance(node.targets[0], ast.Tuple) and node.targets[
            0
        ].id.startswith('mem_'):
            target = node.targets[0]
            var_name = target.id
            addr = int(var_name.split('_')[1], 16)
            if isinstance(node.value, ast.Name):
                # Load from variable then store to memory
                self.output.append(f'LDA {node.value.id}')
                if addr < 0x100:  # Zero page
                    self.output.append(f'STA ${addr:02X}')
                else:  # Absolute addressing
                    self.output.append(f'STA ${addr:04X}')
            return

        # Handle tuple unpacking
        if isinstance(node.targets[0], ast.Tuple):
            if isinstance(node.value, ast.Tuple):
                # Unpack values one by one
                for target, value in zip(
                    node.targets[0].elts, node.value.elts
                ):
                    if isinstance(value, ast.Constant):
                        self.output.append(f'LDA #{value.value}')
                    elif isinstance(value, ast.Name):
                        self.output.append(f'LDA {value.id}')
                    else:
                        # Visit the value first - this handles expressions
                        self.visit(value)
                    self.output.append(f'STA {target.id}')
            return

        # Handle regular assignments
        if isinstance(node.value, ast.Constant):
            self.output.append(f'LDA #{node.value.value}')
        elif isinstance(node.value, ast.Name):
            self.output.append(f'LDA {node.value.id}')
        else:
            # Visit the value first - this handles IfExp and other expressions
            self.visit(node.value)

        # Store the result in all target variables
        for target in node.targets:
            self.output.append(f'STA {target.id}')

    @debug_comment
    def visit_AugAssign(self, node):
        var_name = node.target.id

        # Handle complex expressions in the value
        if isinstance(node.value, (ast.BinOp, ast.Subscript, ast.Call)):
            # Visit the expression first (result lands in A)
            self.visit(node.value)
            # Store result in temp variable
            self.output.append('STA temp_var')
            var_value_str = 'temp_var'
        elif isinstance(node.value, ast.Constant):
            var_value = node.value.value
            var_value_str = f'#{var_value}'
        elif isinstance(node.value, ast.Name):
            var_value = None
            var_value_str = node.value.id
        else:
            raise NotImplementedError(
                'Unsupported value type in augmented assignment: '
                f'{type(node.value)}'
            )

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
        elif isinstance(node.op, ast.BitAnd):
            # Handle augmented bitwise AND
            self.output.append(f'LDA {var_name}')
            self.output.append(f'AND {var_value_str}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.BitOr):
            # Handle augmented bitwise OR
            self.output.append(f'LDA {var_name}')
            self.output.append(f'ORA {var_value_str}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.BitXor):
            # Handle augmented bitwise XOR
            self.output.append(f'LDA {var_name}')
            self.output.append(f'EOR {var_value_str}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.LShift):
            # Handle augmented left shift
            if isinstance(node.value, ast.Constant):
                # For constant shifts, we can optimize by multiplying by 2^n
                shift_amount = var_value  # Use the shift amount directly
                self.output.append(f'LDA {var_name}')
                # Multiply by shift_amount using repeated ASL
                for _ in range(shift_amount):
                    self.output.append('ASL A')
                self.output.append(f'STA {var_name}')
            else:
                # For variable shifts, we need a loop
                self.output.append(f'LDA {var_name}')
                loop_label = f'shift_left_loop_{len(self.output)}'
                end_label = f'shift_left_end_{len(self.output)}'
                self.output.append(f'LDX {var_value_str}')
                self.output.append(f'BEQ {end_label}')
                self.output.append(f'{loop_label}:')
                self.output.append('ASL A')
                self.output.append('DEX')
                self.output.append(f'BNE {loop_label}')
                self.output.append(f'{end_label}:')
                self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.RShift):
            # Handle augmented right shift
            if isinstance(node.value, ast.Constant):
                # For constant shifts, we can optimize by dividing by 2^n
                shift_amount = var_value  # Use the shift amount directly
                self.output.append(f'LDA {var_name}')
                # Divide by shift_amount using repeated LSR
                for _ in range(shift_amount):
                    self.output.append('LSR A')
                self.output.append(f'STA {var_name}')
            else:
                # For variable shifts, we need a loop
                self.output.append(f'LDA {var_name}')
                loop_label = f'shift_right_loop_{len(self.output)}'
                end_label = f'shift_right_end_{len(self.output)}'
                self.output.append(f'LDX {var_value_str}')
                self.output.append(f'BEQ {end_label}')
                self.output.append(f'{loop_label}:')
                self.output.append('LSR A')
                self.output.append('DEX')
                self.output.append(f'BNE {loop_label}')
                self.output.append(f'{end_label}:')
                self.output.append(f'STA {var_name}')

    def visit_BinOp(self, node):
        # Get the operands first
        left = node.left
        right = node.right

        # Handle shift operations
        if isinstance(node.op, ast.LShift):
            # Visit the left operand first
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_var')
            # Visit the right operand
            self.visit(right)
            # Store shift amount in X register
            self.output.append('TAX')
            # Load value to shift
            self.output.append('LDA temp_var')
            # Perform shift
            loop_label = f'shift_left_loop_{len(self.output)}'
            end_label = f'shift_left_end_{len(self.output)}'
            self.output.append(f'BEQ {end_label}')
            self.output.append(f'{loop_label}:')
            self.output.append('ASL A')
            self.output.append('DEX')
            self.output.append(f'BNE {loop_label}')
            self.output.append(f'{end_label}:')
        elif isinstance(node.op, ast.RShift):
            # Visit the left operand first
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_var')
            # Visit the right operand
            self.visit(right)
            # Store shift amount in X register
            self.output.append('TAX')
            # Load value to shift
            self.output.append('LDA temp_var')
            # Perform shift
            loop_label = f'shift_right_loop_{len(self.output)}'
            end_label = f'shift_right_end_{len(self.output)}'
            self.output.append(f'BEQ {end_label}')
            self.output.append(f'{loop_label}:')
            self.output.append('LSR A')
            self.output.append('DEX')
            self.output.append(f'BNE {loop_label}')
            self.output.append(f'{end_label}:')
        elif isinstance(node.op, ast.Add):
            # Visit the left operand first
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_var')
            # Visit the right operand
            self.visit(right)
            # Add with carry
            self.output.append('CLC')
            self.output.append('ADC temp_var')
            # Store result in temp variable
            self.output.append('STA temp_var')
            # Visit the right operand
            self.visit(right)
            # Add with carry
            self.output.append('CLC')
            self.output.append('ADC temp_var')

        # Handle nested binary operations on the left side
        if isinstance(left, ast.BinOp):
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_left')
            left_value = 'temp_left'
        elif isinstance(left, ast.Name):
            left_value = left.id
        elif isinstance(left, ast.Constant):
            left_value = f'#{left.value}'
        else:
            raise NotImplementedError(
                f'Unsupported left operand type: {type(left)}'
            )

        # Handle nested binary operations on the right side
        if isinstance(right, ast.BinOp):
            self.visit(right)
            # Store result in temp variable
            self.output.append('STA temp_right')
            right_value = 'temp_right'
        elif isinstance(right, ast.Name):
            right_value = right.id
        elif isinstance(right, ast.Constant):
            right_value = f'#{right.value}'
        else:
            raise NotImplementedError(
                f'Unsupported right operand type: {type(right)}'
            )

        # Get parent context to find where to store the result
        parent = getattr(node, '_parent', None)
        target_var = None
        if isinstance(parent, ast.Assign) and isinstance(
            parent.targets[0], ast.Name
        ):
            target_var = parent.targets[0].id

        # Handle multiplication by repeated addition
        if isinstance(node.op, ast.Mult):
            mul_loop = self._generate_label()
            mul_end = self._generate_label()
            self.output.append(f'LDA {left_value}')
            self.output.append('STA temp_mul')
            self.output.append(f'LDX {right_value}')
            self.output.append('LDA #0')
            self.output.append(f'{mul_loop}:')
            self.output.append('CPX #0')
            self.output.append(f'BEQ {mul_end}')
            self.output.append('CLC')
            self.output.append('ADC temp_mul')
            self.output.append('DEX')
            self.output.append(f'JMP {mul_loop}')
            self.output.append(f'{mul_end}:')
            if target_var:
                self.output.append(f'STA {target_var}')
            return

        # Load left value and perform operation
        self.output.append(f'LDA {left_value}')

        if isinstance(node.op, ast.Add):
            self.output.append('CLC')
            self.output.append(f'ADC {right_value}')
        elif isinstance(node.op, ast.Sub):
            self.output.append('SEC')
            self.output.append(f'SBC {right_value}')
        elif isinstance(node.op, ast.BitAnd):
            self.output.append(f'AND {right_value}')
        elif isinstance(node.op, ast.BitOr):
            self.output.append(f'ORA {right_value}')
        elif isinstance(node.op, ast.BitXor):
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

    def _branch_if_false(self, compare, false_label):
        """Emit a comparison and branch to false_label when it fails."""
        if not isinstance(compare, ast.Compare) or len(compare.ops) != 1:
            raise NotImplementedError('Unsupported condition')
        self.visit(compare)
        op = compare.ops[0]
        if isinstance(op, ast.Eq):
            self.output.append(f'BNE {false_label}')
        elif isinstance(op, ast.NotEq):
            self.output.append(f'BEQ {false_label}')
        elif isinstance(op, ast.Lt):
            self.output.append(f'BCS {false_label}')
        elif isinstance(op, ast.Gt):
            self.output.append(f'BCC {false_label}')
            self.output.append(f'BEQ {false_label}')
        elif isinstance(op, ast.GtE):
            self.output.append(f'BCC {false_label}')
        elif isinstance(op, ast.LtE):
            true_label = self._generate_label()
            self.output.append(f'BEQ {true_label}')
            self.output.append(f'BCS {false_label}')
            self.output.append(f'{true_label}:')
        else:
            raise NotImplementedError(
                f'Operator not supported {type(op).__name__}'
            )

    def _branch_if_true(self, compare, true_label):
        """Emit a comparison and branch to true_label when it succeeds."""
        if not isinstance(compare, ast.Compare) or len(compare.ops) != 1:
            raise NotImplementedError('Unsupported condition')
        self.visit(compare)
        op = compare.ops[0]
        if isinstance(op, ast.Eq):
            self.output.append(f'BEQ {true_label}')
        elif isinstance(op, ast.NotEq):
            self.output.append(f'BNE {true_label}')
        elif isinstance(op, ast.Lt):
            self.output.append(f'BCC {true_label}')
        elif isinstance(op, ast.Gt):
            skip_label = self._generate_label()
            self.output.append(f'BEQ {skip_label}')
            self.output.append(f'BCS {true_label}')
            self.output.append(f'{skip_label}:')
        elif isinstance(op, ast.GtE):
            self.output.append(f'BCS {true_label}')
        elif isinstance(op, ast.LtE):
            self.output.append(f'BCC {true_label}')
            self.output.append(f'BEQ {true_label}')
        else:
            raise NotImplementedError(
                f'Operator not supported {type(op).__name__}'
            )

    def _test_branch_false(self, test, false_label):
        """Emit a condition (Compare, BoolOp or not-Compare) branching to
        false_label when it fails; otherwise execution falls through."""
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            # 'not X' fails exactly when X succeeds
            self._branch_if_true(test.operand, false_label)
            return
        if isinstance(test, ast.BoolOp):
            if isinstance(test.op, ast.And):
                # For AND, every condition must hold; any failure goes
                # false
                for value in test.values:
                    self._branch_if_false(value, false_label)
            elif isinstance(test.op, ast.Or):
                # For OR, any condition holding goes true; only the last
                # condition failing goes false
                true_label = self._generate_label()
                for value in test.values[:-1]:
                    self._branch_if_true(value, true_label)
                self._branch_if_false(test.values[-1], false_label)
                self.output.append(f'{true_label}:')
            else:
                raise NotImplementedError(
                    'Only AND/OR operators are supported'
                )
        else:
            self._branch_if_false(test, false_label)

    @debug_comment
    def visit_BoolOp(self, node):
        """Handle boolean operations like AND/OR"""
        false_label = self._generate_label()
        self._test_branch_false(node, false_label)
        return false_label

    @debug_comment
    def visit_If(self, node):
        self.comment(node.test)
        false_label = self._generate_label()
        end_label = self._generate_label()

        # Handle constant conditions (if True / if False) at compile time
        if isinstance(node.test, ast.Constant):
            branch = node.body if node.test.value else node.orelse
            for stmt in branch:
                self.comment(stmt)
                self.visit(stmt)
            return

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
            self.output.append('NOP')
            return

        # Handle simple comparisons (including 'not')
        self._test_branch_false(node.test, false_label)

        # Handle true block (fall-through case)
        for stmt in node.body:
            self.comment(stmt)
            self.visit(stmt)

        # Handle else block
        if node.orelse:
            self.output.append(f'JMP {end_label}')
            self.output.append(f'{false_label}:')
            for stmt in node.orelse:
                self.comment(stmt)
                self.visit(stmt)
            self.output.append(f'{end_label}:')
            self.output.append('NOP')
        else:
            self.output.append(f'{false_label}:')
            self.output.append('NOP')

    def visit_While(self, node):
        # Generate code for while loop
        start_label = self._generate_label()
        end_label = self._generate_label()

        # Start of loop body
        self.output.append(f'{start_label}:')

        # Check condition
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            # while True - no condition check needed
            pass
        elif isinstance(node.test, (ast.Compare, ast.BoolOp, ast.UnaryOp)):
            self._test_branch_false(node.test, end_label)
        else:
            raise NotImplementedError(
                'Only comparisons, AND/OR/NOT and True constant '
                'supported in while'
            )

        # Loop body
        self.loop_end_labels.append(end_label)
        self.loop_continue_labels.append(start_label)
        for stmt in node.body:
            self.visit(stmt)
        self.loop_end_labels.pop()
        self.loop_continue_labels.pop()

        # Jump back to start to check condition again
        self.output.append(f'JMP {start_label}')

        # End of loop
        self.output.append(f'{end_label}:')
        self.output.append('NOP')  # No-op instead of BRK

    @debug_comment
    def visit_For(self, node):
        # Only 'for <name> in range(...)' is supported
        if (
            not isinstance(node.iter, ast.Call)
            or not isinstance(node.iter.func, ast.Name)
            or node.iter.func.id != 'range'
        ):
            raise NotImplementedError('Only range() iteration is supported')
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                'Only simple loop variables are supported'
            )
        if node.orelse:
            raise NotImplementedError('for/else is not supported')

        args = node.iter.args
        if len(args) == 1:
            start, stop, step = None, args[0], None
        elif len(args) == 2:
            start, stop, step = args[0], args[1], None
        elif len(args) == 3:
            start, stop, step = args[0], args[1], args[2]
        else:
            raise NotImplementedError('range() requires 1 to 3 arguments')

        var_name = node.target.id
        start_label = self._generate_label()
        continue_label = self._generate_label()
        end_label = self._generate_label()

        # Initialize loop variable
        if start is None:
            self.output.append('LDA #0')
        elif isinstance(start, ast.Constant):
            self.output.append(f'LDA #{start.value}')
        elif isinstance(start, ast.Name):
            self.output.append(f'LDA {start.id}')
        else:
            raise NotImplementedError('Unsupported range() start')
        self.output.append(f'STA {var_name}')

        # Loop condition: exit when loop variable >= stop
        self.output.append(f'{start_label}:')
        self.output.append(f'LDA {var_name}')
        if isinstance(stop, ast.Constant):
            self.output.append(f'CMP #{stop.value}')
        elif isinstance(stop, ast.Name):
            self.output.append(f'CMP {stop.id}')
        else:
            raise NotImplementedError('Unsupported range() stop')
        self.output.append(f'BCS {end_label}')

        # Loop body
        self.loop_end_labels.append(end_label)
        self.loop_continue_labels.append(continue_label)
        for stmt in node.body:
            self.visit(stmt)
        self.loop_end_labels.pop()
        self.loop_continue_labels.pop()

        # Increment loop variable by step
        self.output.append(f'{continue_label}:')
        if step is None:
            self.output.append(f'INC {var_name}')
        elif isinstance(step, ast.Constant):
            if step.value <= 0:
                raise NotImplementedError(
                    'Only positive range() steps are supported'
                )
            if step.value == 1:
                self.output.append(f'INC {var_name}')
            else:
                self.output.append(f'LDA {var_name}')
                self.output.append('CLC')
                self.output.append(f'ADC #{step.value}')
                self.output.append(f'STA {var_name}')
        elif isinstance(step, ast.Name):
            self.output.append(f'LDA {var_name}')
            self.output.append('CLC')
            self.output.append(f'ADC {step.id}')
            self.output.append(f'STA {var_name}')
        else:
            raise NotImplementedError('Unsupported range() step')
        self.output.append(f'JMP {start_label}')

        # End of loop
        self.output.append(f'{end_label}:')
        self.output.append('NOP')

    def visit_Break(self, node):
        if self.loop_end_labels:
            self.output.append(f'JMP {self.loop_end_labels[-1]}')
        else:
            raise NotImplementedError('No loop to break')

    def visit_Continue(self, node):
        if self.loop_continue_labels:
            self.output.append(f'JMP {self.loop_continue_labels[-1]}')
        else:
            raise NotImplementedError('No loop to continue')

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
                    self.output.append(f'LDA #{left.value}')

                # Compare with right value
                if isinstance(comparator, ast.Constant):
                    self.output.append(f'CMP #{comparator.value}')
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
            self.output.append(f'LDA #{node.orelse.value}')
        elif isinstance(node.orelse, ast.Name):
            self.output.append(f'LDA {node.orelse.id}')
        self.output.append(f'JMP {end_label}')

        # True case (condition met)
        self.output.append(f'{false_label}:')
        if isinstance(node.body, ast.Constant):
            self.output.append(f'LDA #{node.body.value}')
        elif isinstance(node.body, ast.Name):
            self.output.append(f'LDA {node.body.id}')

        # End of if expression
        self.output.append(f'{end_label}:')

    def _generate_label(self):
        label = f'label_{self.label_count}'
        self.label_count += 1
        return label
