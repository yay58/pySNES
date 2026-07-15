"""Data declaration types for pyNES.

In pure Python these behave like plain values, so game code runs
unmodified in CPython. At compile time, the cartridge builder
recognizes these declarations by name and allocates them:
- uint8/uint16 -> RAM (.rs)
- string/rom   -> ROM data segments (.db)
"""

RAM_TYPES = {'uint8': 1, 'uint16': 2}
ROM_TYPES = ('string', 'rom')


def uint8(value=0):
    """One byte in RAM."""
    return value & 0xFF


def uint16(value=0):
    """Two bytes in RAM (little-endian)."""
    return value & 0xFFFF


def string(text):
    """Zero-terminated ASCII string in ROM."""
    return text


def rom(data):
    """Read-only byte array in ROM (e.g. palettes, tiles, level maps)."""
    return list(data)
