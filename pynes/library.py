class Library:
    """Contract between the compiler core and platform libraries.

    A library provides:
    - externs: function names callable from user code, each backed by an
      emitter ``fn(translator, args)`` that appends 6502 assembly to
      ``translator.output``
    - runtime_asm: 6502 assembly routines linked into the ROM
    """

    def __init__(self, name):
        self.name = name
        self.externs = {}
        self.runtime_asm = []

    def extern(self, func=None, *, name=None):
        """Register an extern emitter. Usable as ``@lib.extern`` or
        ``@lib.extern(name='alias')``."""

        def register(fn):
            self.externs[name or fn.__name__] = fn
            return fn

        if func is not None:
            return register(func)
        return register

    def runtime(self, asm):
        """Register a 6502 assembly routine to be linked into the ROM."""
        self.runtime_asm.append(asm)
