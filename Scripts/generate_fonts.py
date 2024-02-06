#!/usr/bin/env python3

# python3 -m pip install pillow
# License: HPND license.
from PIL import Image, ImageFont, ImageDraw

import math

# Use a power of 2 pixels per character so we can evenly divide the plane.
font_pixels = 128
full_ratio = 0.75
half_ratio = 0.5
full_sz = int(font_pixels * full_ratio)
half_sz = int(font_pixels * half_ratio)
layout_engine = ImageFont.Layout.BASIC

unifont = ImageFont.truetype("Fonts/unifont-15.0.01.ttf", full_sz, layout_engine=layout_engine)
unifont_half = ImageFont.truetype("Fonts/unifont-15.0.01.ttf", half_sz, layout_engine=layout_engine)

noto_sans_mono = ImageFont.truetype(
        "Fonts/Noto_Sans_Mono/static/NotoSansMono/NotoSansMono-Bold.ttf",
        full_sz, index=0, layout_engine=layout_engine)

noto_sans_sc_half = ImageFont.truetype("Fonts/Noto_Sans_Simplified_Chinese/NotoSansSC-Regular.otf", half_sz, layout_engine=layout_engine)

noto_sans_kr_half = ImageFont.truetype("Fonts/Noto_Sans_Korean/NotoSansKR-Regular.otf", half_sz, layout_engine=layout_engine)

n_rows = 64
n_cols = 128

class FontInfo:
    def __init__(self, font, dy):
        self.font = font
        self.dy = dy

def allow_range(allowlist, lo_hi, font = None, dy = 0):
    for i in range(lo_hi[0], lo_hi[1] + 1):
        allowlist[i] = FontInfo(font, dy)
def ban_range(allowlist, lo, hi):
    for i in range(lo, hi + 1):
        del allowlist[i]
allowlist = {}
# ASCII
basic_latin = (32, 126)
allow_range(allowlist, basic_latin, font=noto_sans_mono, dy = -20)
# Latin-1 supplement
latin_1_supplement = (0x00A1, 0x00ff)
allow_range(allowlist, latin_1_supplement, font = noto_sans_mono)
# Latin extended-A
latin_extended_a = (0x0100, 0x017f)
allow_range(allowlist, latin_extended_a, font = noto_sans_mono)
# Latin extended-B
latin_extended_b = (0x0180, 0x024f)
allow_range(allowlist, latin_extended_b, font = noto_sans_mono)
# Spacing modifier letters
ipa_extensions = (0x0250, 0x02af)
allow_range(allowlist, ipa_extensions, font = unifont)
# Greek and Coptic
greek = (0x0370, 0x03ff)
allow_range(allowlist, greek, font = noto_sans_mono)
ban_range(allowlist, 0x0378, 0x03a2)
# Cyrillic
cyrillic = (0x0400, 0x04ff)
allow_range(allowlist, cyrillic, font = unifont)
# Currency symbols
currency_symbols = (0x20a0, 0x20c0)
allow_range(allowlist, currency_symbols, font = noto_sans_mono)

# CJK
#
hangul_jamo = (0x1100, 0x11FF)
allow_range(allowlist, hangul_jamo, font = noto_sans_kr_half)
#
general_punctuation = (0x2000, 0x206f)
allow_range(allowlist, general_punctuation, font = noto_sans_mono)
#
kangxi_radicals = (0x2f00, 0x2fdf)
allow_range(allowlist, kangxi_radicals, font = noto_sans_sc_half)
#
cjk_symbols_and_punctuation = (0x3000, 0x303f)
allow_range(allowlist, cjk_symbols_and_punctuation, font = noto_sans_sc_half)
#
hiragana = (0x3041, 0x309f)
allow_range(allowlist, hiragana, font = noto_sans_sc_half)
ban_range(allowlist, 0x3097, 0x3098)
#
katakana = (0x30a0, 0x30ff)
allow_range(allowlist, katakana, font = noto_sans_sc_half)
#
hangul_compatibility_jamo = (0x3130, 0x318f)
allow_range(allowlist, hangul_compatibility_jamo, font = noto_sans_sc_half)
#
enclosed_cjk_letters_and_months = (0x3200, 0x32FF)
allow_range(allowlist, enclosed_cjk_letters_and_months, font = noto_sans_sc_half)
#
cjk_compatibility = (0x3300, 0x33ff)
allow_range(allowlist, cjk_compatibility, font = noto_sans_sc_half)
#
cjk_unified_extension_a = (0x3400, 0x4dbf)
allow_range(allowlist, cjk_unified_extension_a, font = noto_sans_sc_half)
#
cjk_ideographs = (0x4e00, 0x9fff)
allow_range(allowlist, cjk_ideographs, font = noto_sans_sc_half)
#
hangul_syllables = (0xAC00, 0xD7A3)
allow_range(allowlist, hangul_syllables, font = noto_sans_kr_half)
#
halfwidth_and_fullwidth = (0xff00, 0xffef)
allow_range(allowlist, halfwidth_and_fullwidth, font = noto_sans_sc_half)

def in_range(x, range_pair) -> bool:
    return x >= range_pair[0] and x <= range_pair[1]

max_char = max(allowlist)
print("max char: {}".format(max_char))
print("num chars: {}".format(len(allowlist)))

def genUnicode():
    total_rows = math.ceil(max_char / n_cols)
    print("total rows {}".format(total_rows))
    total_textures = math.ceil(total_rows / n_rows)
    print("total textures {}".format(total_textures))

    for nth_texture in range(0, total_textures):
        # Create an 8K grayscale ("L") or black and white ("1") image
        # Unity will re-encode b&w to grayscale, so using b&w just helps keep
        # the package size low (we vendor these, we don't generate them
        # client-side).
        image = Image.new(mode="1", size=(8192,8192), color=0)
        draw = ImageDraw.Draw(image)

        row_begin = nth_texture * n_rows

        for row in range(row_begin, row_begin + n_rows):
            line = ""
            for col in range(0, n_cols):
                # Generate the unicode character for this spot.
                n = row * n_cols + col
                char = None
                font_info = None
                if n in allowlist.keys():
                    char = chr(n)
                    font_info = allowlist[n]
                else:
                    char = " "
                    font_info = FontInfo(unifont, 0)
                # Hack: Chinese, Japanese, and Korean characters are all double
                # width and are all on textures [1,6]. To fit them in the same
                # grid, we use a half-size font.
                draw.text((col * font_pixels / 2, (row - row_begin) * font_pixels +
                    font_info.dy), char, font=font_info.font, fill=255)

        image.save("Fonts/Bitmaps/font-%01d.png" % nth_texture)

def genASCII():
    # Create an 8k grayscale image. 16 glyphs wide, 8 glyphs tall.
    # Only characters on the range [0, 128).
    image = Image.new(mode="RGBA", size=(8192,8192), color=0)
    draw = ImageDraw.Draw(image)
    n_rows = 8
    n_cols = 16

    font = ImageFont.truetype(
            "Fonts/Noto_Sans_Mono/static/NotoSansMono/NotoSansMono-Bold.ttf",
            int((8192 / 8) * 0.75), index=0, layout_engine=layout_engine)

    for row in range(0, n_rows):
        for col in range(0, n_cols):
            n = row * n_cols + col
            char = None
            font_info = None
            if n in allowlist.keys():
                char = chr(n)
            else:
                char = " "
            draw.text((col * font_pixels * 8 / 2, row * font_pixels * 8 - 20),
                    char, font=font, fill=(255,255,255))
    image.save("Fonts/Bitmaps/font-ascii.png")

if __name__ == "__main__":
    print("Generating unicode fonts")
    #genUnicode()
    print("Generating ASCII fonts")
    genASCII()
