import ast

from nesasm.compiler import Cartridge, lexical, semantic, syntax

from pynes.translator import (
    TEMP_VARS,
    PythonTo6502,
    ScopeMangler,
    VarTable,
)
from pynes.types import RAM_TYPES, ROM_TYPES

ENTRY_POINTS = ('reset', 'nmi', 'irq')

RESET_PREAMBLE = [
    'SEI',
    'CLD',
    'LDX #$FF',
    'TXS',
    'INX',
    'STX $2000',
    'STX $2001',
    'vblank_wait_1:',
    'BIT $2002',
    'BPL vblank_wait_1',
    'vblank_wait_2:',
    'BIT $2002',
    'BPL vblank_wait_2',
]


class CartVarTable(VarTable):
    """Variable collector that ignores called function names."""

    def visit_Call(self, node):
        for arg in node.args:
            self.visit(arg)


class Cart:
    """NES cartridge builder: turns a Python module with entry point
    decorators (@reset, @nmi, @irq) into a complete nesasm source,
    linking the runtime of the given libraries."""

    def __init__(
        self,
        libraries=None,
        prg_banks=1,
        chr_banks=0,
        mapper=0,
        mirroring=1,
        org=0xC000,
        chr_data=None,
    ):
        self.libraries = libraries or []
        self.prg_banks = prg_banks
        self.chr_banks = chr_banks
        self.mapper = mapper
        self.mirroring = mirroring
        self.org = org
        self.chr_data = chr_data

    def _entry_name(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in (
                ENTRY_POINTS
            ):
                return decorator.id
        return None

    def _collect_entries(self, tree):
        entries = {}
        declarations = []
        functions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                entry = self._entry_name(node)
                if entry is None:
                    # plain user-defined function, statically allocated
                    functions.append(ScopeMangler().visit(node))
                else:
                    entries[entry] = node
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            elif isinstance(node, ast.Assign):
                declarations.append(node)
            else:
                raise NotImplementedError(
                    'Unsupported top-level statement: '
                    f'{type(node).__name__}'
                )
        if 'reset' not in entries:
            raise ValueError('Missing @reset entry point')
        return entries, declarations, functions

    def _collect_declarations(self, declarations):
        """Classify module-level declarations into RAM variables,
        RAM initial values and ROM data."""
        ram_vars = {}
        ram_init = {}
        rom_data = {}
        for node in declarations:
            if len(node.targets) != 1 or not isinstance(
                node.targets[0], ast.Name
            ):
                raise NotImplementedError(
                    'Only simple top-level declarations are supported'
                )
            name = node.targets[0].id
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(
                value.value, int
            ):
                ram_vars[name] = 1
                ram_init[name] = value.value
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in RAM_TYPES
            ):
                ram_vars[name] = RAM_TYPES[value.func.id]
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in ROM_TYPES
            ):
                arg = value.args[0]
                if value.func.id == 'string':
                    rom_data[name] = [ord(c) for c in arg.value] + [0]
                else:  # rom
                    rom_data[name] = [elt.value for elt in arg.elts]
            else:
                raise NotImplementedError(
                    f'Unsupported top-level declaration: {name!r}'
                )
        return ram_vars, ram_init, rom_data

    def _make_translator(self, functions):
        translator = PythonTo6502(libraries=self.libraries)
        for function in functions:
            translator.functions[function.name] = [
                arg.arg for arg in function.args.args
            ]
        return translator

    @staticmethod
    def _set_parents(node):
        for stmt in ast.walk(node):
            for child in ast.iter_child_nodes(stmt):
                setattr(child, '_parent', stmt)

    def _translate_body(self, translator, node):
        self._set_parents(node)
        start = len(translator.output)
        for stmt in node.body:
            translator.visit(stmt)
        return translator.output[start:]

    def _translate_functions(self, translator, functions):
        start = len(translator.output)
        for function in functions:
            self._set_parents(function)
            translator.visit_FunctionDef(function)
        return translator.output[start:]

    def _collect_vars(self, entries, functions=()):
        vartable = CartVarTable()
        for node in list(entries.values()) + list(functions):
            for stmt in node.body:
                vartable.visit(stmt)
        for temp in TEMP_VARS:
            vartable.get_var(temp)
        address = 0x00
        for var in vartable.vars.values():
            var.address = address
            address += var.size
        return vartable.vars

    def compile(self, source):
        tree = ast.parse(source)
        entries, declarations, functions = self._collect_entries(tree)
        ram_vars, ram_init, rom_data = self._collect_declarations(declarations)
        variables = self._collect_vars(entries, functions)
        translator = self._make_translator(functions)

        out = []
        out.append('; Generated by pyNES')
        out.append(f'.inesprg {self.prg_banks}')
        out.append(f'.ineschr {self.chr_banks}')
        out.append(f'.inesmap {self.mapper}')
        out.append(f'.inesmir {self.mirroring}')
        out.append('')

        library_ram = {}
        for library in self.libraries:
            library_ram.update(getattr(library, 'ram', {}))

        if variables or ram_vars or library_ram:
            out.append('.rsset $0000')
            for name, size in library_ram.items():
                out.append(f'{name} .rs {size}')
            for name, size in ram_vars.items():
                out.append(f'{name} .rs {size}')
            allocated = set(library_ram) | set(ram_vars) | set(rom_data)
            for var in variables.values():
                if var.label not in allocated:
                    out.append(f'{var.label} .rs {var.size}')
            out.append('')

        out.append('.bank 0')
        out.append(f'.org ${self.org:04X}')
        out.append('')

        out.append('RESET:')
        out.extend(RESET_PREAMBLE)
        for name, value in ram_init.items():
            out.append(f'LDA #{value}')
            out.append(f'STA {name}')
        out.extend(self._translate_body(translator, entries['reset']))
        out.append('forever:')
        out.append('JMP forever')
        out.append('')

        out.append('NMI:')
        if 'nmi' in entries:
            out.extend(self._translate_body(translator, entries['nmi']))
        out.append('RTI')
        out.append('')

        out.append('IRQ:')
        if 'irq' in entries:
            out.extend(self._translate_body(translator, entries['irq']))
        out.append('RTI')
        out.append('')

        if functions:
            out.append('; functions')
            out.extend(self._translate_functions(translator, functions))
            out.append('')

        for library in self.libraries:
            out.append(f'; runtime: {library.name}')
            out.extend(library.runtime_asm)
            out.append('')

        if rom_data:
            out.append('; data')
            for name, data in rom_data.items():
                out.append(f'{name}:')
                out.append('.db ' + ', '.join(f'${byte:02X}' for byte in data))
            out.append('')

        out.append(f'.bank {self.prg_banks * 2 - 1}')
        out.append('.org $E000')
        out.append('.org $FFFA')
        out.append('.dw NMI')
        out.append('.dw RESET')
        out.append('.dw IRQ')
        out.append('')

        if self.chr_banks and self.chr_data:
            out.append(f'.bank {self.prg_banks * 2}')
            out.append('.org $0000')
            for i in range(0, len(self.chr_data), 16):
                chunk = self.chr_data[i : i + 16]
                out.append(
                    '.db ' + ', '.join(f'${byte:02X}' for byte in chunk)
                )
            out.append('')

        return '\n'.join(out)

    def to_nes(self, source):
        """Compile Python source all the way to iNES ROM bytes."""
        asm = self.compile(source)
        cartridge = Cartridge()
        tokens = lexical(asm)
        tree = syntax(tokens)
        semantic(tree, True, cartridge)
        return bytes(bytearray(cartridge.get_ines_code()))
