"""CHR tile encoding for pyNES.

Tiles are defined as 8x8 ASCII art ('#' = pixel) and encoded into
NES CHR format (two 8-byte bitplanes; monochrome art uses color
index 1, so plane 1 is empty).
"""

TILE_SIZE = 16
STAGE_HEIGHT = 30


def encode_stage(rows, legend):
    """Encode ASCII stage rows into column-major bytes (30 bytes per
    column, top to bottom), ready for streaming one column at a time.
    Rows are anchored to the bottom of the screen: missing top rows
    are empty. legend maps characters to tile indexes ('.' is always
    the blank tile 0)."""
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError('All stage rows must have the same width')
    if len(rows) > STAGE_HEIGHT:
        raise ValueError(f'A stage has at most {STAGE_HEIGHT} rows')
    pad = STAGE_HEIGHT - len(rows)
    full = ['.' * width] * pad + list(rows)
    data = bytearray()
    for col in range(width):
        for row in full:
            char = row[col]
            data.append(0 if char == '.' else legend[char])
    return bytes(data)


def encode_tile(art):
    """Encode 8x8 ASCII art into a 16-byte CHR tile."""
    rows = []
    for line in art:
        byte = 0
        for i, pixel in enumerate(line):
            if pixel == '#':
                byte |= 0x80 >> i
        rows.append(byte)
    return bytes(rows) + bytes(8)
