"""CHR tile encoding for pyNES.

Tiles are defined as 8x8 ASCII art ('#' = pixel) and encoded into
NES CHR format (two 8-byte bitplanes; monochrome art uses color
index 1, so plane 1 is empty).
"""

TILE_SIZE = 16


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
