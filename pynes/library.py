import re


class NesFunction:
    """A library function as one object holding both sides of the
    contract (template method pattern):

    - ``caller_code(translator, args)``: assembly emitted at each
      call site
    - ``runtime_code()``: the 6502 routine bundled into the ROM,
      or '' when the caller expands entirely inline

    The extern name defaults to the snake_case of the class name
    (``PpuOnAll`` -> ``ppu_on_all``).
    """

    @property
    def name(self):
        return re.sub(
            r'(?<=[a-z0-9])(?=[A-Z])', '_', type(self).__name__
        ).lower()

    def runtime_code(self):
        raise NotImplementedError

    def caller_code(self, translator, args):
        raise NotImplementedError

    def __call__(self, translator, args):
        # authors write natural assembly (JSR put_str); the label
        # rewrite into the library namespace happens centrally here
        start = len(translator.output)
        self.caller_code(translator, args)
        library = getattr(self, 'library', None)
        if library is not None:
            translator.output[start:] = [
                library.namespaced(line) for line in translator.output[start:]
            ]


class Library:
    """Contract between the compiler core and platform libraries.

    A library provides:
    - externs: function names callable from user code, each backed by a
      NesFunction whose caller_code appends 6502 assembly to
      ``translator.output``
    - const_funcs: pure functions evaluated at compile time when all
      their arguments are constants (e.g. nametable address helpers)
    - runtime_asm: 6502 assembly routines linked into the ROM
    - ram: zero-page variables required by the runtime routines,
      allocated by the cartridge in registration order (adjacent
      registrations get adjacent addresses)
    """

    def __init__(self, name):
        self.name = name
        self.externs = {}
        self.const_funcs = {}
        self.constants = {}
        self.runtime_asm = []
        self.ram = {}

    def constant(self, name, value):
        """Register a named constant (e.g. button masks) substituted
        into user code at compile time."""
        self.constants[name] = value

    def function(self, fn):
        """Register a NesFunction: its caller side becomes an extern
        and its runtime side is linked into the ROM."""
        fn.library = self
        self.externs[fn.name] = fn
        runtime = fn.runtime_code()
        if runtime:
            self.runtime(runtime)
        return fn

    def const(self, func):
        """Register a compile-time constant function. When called with
        constant arguments, the call is folded into its result."""
        self.const_funcs[func.__name__] = func
        return func

    def zeropage(self, name, size=1):
        """Reserve a zero-page RAM variable for the runtime."""
        self.ram[name] = size

    def runtime(self, asm):
        """Register a 6502 assembly routine to be linked into the ROM."""
        self.runtime_asm.append(asm)
        self._labels = None

    @property
    def runtime_labels(self):
        """Every label defined by the library's runtime routines."""
        if getattr(self, '_labels', None) is None:
            self._labels = {
                match.group(1)
                for asm in self.runtime_asm
                for line in asm.splitlines()
                for match in [re.match(r'^\s*([A-Za-z_]\w*):', line)]
                if match
            }
        return self._labels

    def namespaced(self, text):
        """Rewrite the library's own labels into its namespace
        (put_str -> neslib__put_str), so library routines can never
        collide with user labels or with other libraries. NesFunction
        authors keep writing natural assembly."""
        for label in self.runtime_labels:
            text = re.sub(rf'\b{label}\b', f'{self.name}__{label}', text)
        return text
