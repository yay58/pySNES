class Library:
    """Contract between the compiler core and platform libraries.

    A library provides:
    - externs: function names callable from user code, each backed by an
      emitter ``fn(translator, args)`` that appends 6502 assembly to
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

    def extern(self, func=None, *, name=None):
        """Register an extern emitter. Usable as ``@lib.extern`` or
        ``@lib.extern(name='alias')``."""

        def register(fn):
            self.externs[name or fn.__name__] = fn
            return fn

        if func is not None:
            return register(func)
        return register

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
