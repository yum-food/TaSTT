#!/usr/bin/env python3

from PIL import Image, ImageFont, ImageDraw

import math

# Use a power of 2 pixels per character so we can evenly divide the plane.
font_pixels = 64
font = ImageFont.truetype("unifont-15.0.01.ttf", font_pixels)

n_rows = 64
n_cols = 128

def allow_range(allowlist, lo, hi):
    for i in range(lo, hi + 1):
        allowlist.add(i)
def ban_range(allowlist, lo, hi):
    for i in range(lo, hi + 1):
        allowlist.remove(i)
allowlist = set()
# ASCII
allow_range(allowlist, 32, 126)
# Latin-1 supplement
allow_range(allowlist, 0x00A1, 255)
# Latin extended-A
allow_range(allowlist, 0x0100, 0x017F)
# Latin extended-B
allow_range(allowlist, 0x0180, 0x024F)
# Spacing modifier letters
allow_range(allowlist, 0x0250, 0x02AF)
# Greek and Coptic
allow_range(allowlist, 880, 1023)
ban_range(allowlist, 0x0378, 0x03a2)
# Cyrillic
allow_range(allowlist, 0x0400, 0x04FF)
# Currency symbols
allow_range(allowlist, 0x20A0, 0x20C0)

# Japanese
# Punctuation
allow_range(allowlist, 0x3000, 0x303F)
# Hiragana
allow_range(allowlist, 0x3041, 0x30FF)
ban_range(allowlist, 0x3097, 0x3098)
# Katakana
allow_range(allowlist, 0x30A0, 0x30FF)
# CJK Unified Ideographs (Kanji)
allow_range(allowlist, 0x4E00, 0x9FFF)
# CJK Unified Ideographs extension A (rare Kanji)
allow_range(allowlist, 0x3400, 0x4dbf)

# Korean
allow_range(allowlist, 0x1100, 0x11FF)
allow_range(allowlist, 0xAC00, 0xD7A3)

max_char = max(allowlist)
total_rows = math.ceil(max_char / n_cols)
print("total rows {}".format(total_rows))
total_textures = math.ceil(total_rows / n_rows)
print("total textures {}".format(total_textures))

for nth_texture in range(0, total_textures):
    # Create a 4K grayscale ("L") image
    image = Image.new(mode="L", size=(4096,4096), color=255)
    draw = ImageDraw.Draw(image)

    row_begin = nth_texture * n_rows

    for row in range(row_begin, row_begin + n_rows):
        line = ""
        for col in range(0, n_cols):
            # Generate the unicode character for this spot.
            n = row * n_cols + col
            if n in allowlist:
                line += chr(n)
            else:
                line += " "
        draw.text((0, (row - row_begin) * font_pixels), line, font=font)

    image.save("font-%01d.png" % nth_texture)

