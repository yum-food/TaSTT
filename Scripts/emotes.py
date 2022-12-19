#!/usr/bin/env python3

import argparse
from math import floor
import os
# python3 -m pip install pillow
from PIL import Image
import sys

# (row, col)
TEX_SZ = (2048, 2048)

IMG_SZ_PX = 256
IMG_PER_ROW = int(TEX_SZ[0] / IMG_SZ_PX)
IMG_PER_COL = int(TEX_SZ[1] / IMG_SZ_PX)

# TODO(yum) this should live in a config file.
# Note: the name of the emote must be no longer than 6 characters.
IMG_TEX_DATA = []
IMG_TEX_DATA.append(("Images/Emotes/xdd.png", "xdd"))
IMG_TEX_DATA.append(("Images/Emotes/pog.png", "pog"))
IMG_TEX_DATA.append(("Images/Emotes/lulw.png", "laugh"))
IMG_TEX_DATA.append(("Images/Emotes/bighardo.png", "hard"))
IMG_TEX_DATA.append(("Images/Emotes/peepoHappy.png", "happy"))
IMG_TEX_DATA.append(("Images/Emotes/peepoSad.png", "sad"))
IMG_TEX_DATA.append(("Images/Emotes/bedge.png", "bed"))
IMG_TEX_DATA.append(("Images/Emotes/reallymad.png", "mad"))
IMG_TEX_DATA.append(("Images/Emotes/clueless.png", "surely"))
IMG_TEX_DATA.append(("Images/Emotes/what.png", "what"))
IMG_TEX_DATA.append(("Images/Emotes/based.png", "based"))
IMG_TEX_DATA.append(("Images/Emotes/chad.png", "chad"))
IMG_TEX_DATA.append(("Images/Emotes/aware.png", "aware"))
IMG_TEX_DATA.append(("Images/Emotes/girl.png", "girl"))
IMG_TEX_DATA = []

IMG_TEX_KEYWORD_TO_COORD = {}
for i in range(0, len(IMG_TEX_DATA)):
    IMG_TEX_KEYWORD_TO_COORD[IMG_TEX_DATA[i][1]] = i

# We treat images like words. To keep things simple, they're the same height as
# a word, and they're a fixed width.
IMG_SZ_LETTER_ROWS = 1
IMG_SZ_LETTER_COLS = 6

def lookup(word: str):
    word = word.lower()
    word = ''.join(c for c in word.lower() if c.isalpha())
    if word in IMG_TEX_KEYWORD_TO_COORD.keys():
        return word, IMG_TEX_KEYWORD_TO_COORD[word]
    return None, None

def openTexture(tex_path: str):
    if not os.path.exists(args.texture_path):
        return Image.new("RGB", TEX_SZ)
    tex = Image.open(args.texture_path)
    if tex.size != TEX_SZ:
        print("Texture at {} has mismatching size {}, creating new texture".format(
            tex_path, tex.size), file=sys.stderr)
        return Image.new("RGB", TEX_SZ)
    return tex

# Add an image to the texture at the coordinates (x, y). x and y should be in
# the range [0, IMG_PER_COL) and [0, IMG_PER_ROW) respectively.
def addImageToTexture(tex: Image, img_path: str, x: int, y:int):
    # Transparent images will be composited on top of a black background.
    img = Image.open(img_path).convert('RGBA')
    img_bg = Image.new('RGBA', img.size, (0, 0, 0))
    img = Image.alpha_composite(img_bg, img).convert('RGB')

    max_px = IMG_SZ_PX

    # Scale the image up so it uses as much space as is given to it.
    # I originally planned to support multiple scales, but this proved to be
    # too much work - getting line wrapping to work with this would be a pain.
    # So for now, all images are the same height as words.
    scale = 1
    img_x, img_y = img.size
    max_dim = max(img_x, img_y)
    img_scale = (max_px / max_dim) * scale
    new_sz = (int(floor(img.size[0] * img_scale)),
            int(floor(img.size[1] * img_scale)))
    print("Add image {}".format(img_path))
    print("  Original size: {}".format(img.size))
    print("  Scaled size: {}".format(new_sz))
    img = img.resize(new_sz)

    # Center the image within its new coordinate space.
    padded_img_sz = (IMG_SZ_PX * scale, IMG_SZ_PX * scale)
    padded_img = Image.new("RGB", padded_img_sz)
    centered_x = int(floor((padded_img_sz[0] - new_sz[0]) / 2))
    centered_y = int(floor((padded_img_sz[1] - new_sz[1]) / 2))
    padded_img.paste(img, box=(centered_x, centered_y))
    img = padded_img

    # Break the image into tiles and write them into the texture.
    for slot in range(0, scale * scale):
        tile_x = slot % scale
        tile_y = int(floor(slot / scale))
        tile_bbox = (tile_x * IMG_SZ_PX, tile_y * IMG_SZ_PX, (tile_x + 1) * IMG_SZ_PX, (tile_y + 1) * IMG_SZ_PX)
        tile = img.crop(tile_bbox)
        print("  tile {},{} (bbox={})".format(tile_x, tile_y, tile_bbox))

        slot_x = x + slot % IMG_PER_ROW
        slot_y = y + int(floor(slot / IMG_PER_ROW))
        slot_x_px = slot_x * IMG_SZ_PX
        slot_y_px = slot_y * IMG_SZ_PX
        print("  Add img at {},{} (px {},{})".format(slot_x, slot_y, slot_x_px, slot_y_px))

        tex.paste(tile, box=(slot_x_px, slot_y_px))

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texture_path", type=str, help="Path to save the generated texture.")
    args = parser.parse_args()

    if not args.texture_path:
        args.texture_path = "img_texture.png"

    return args

if __name__ == "__main__":
    args = parseArgs()

    tex = openTexture(args.texture_path)
    for i in range(0, len(IMG_TEX_DATA)):
        filename = IMG_TEX_DATA[i][0]
        x = i % IMG_PER_ROW
        y = int(floor(i / IMG_PER_ROW))
        addImageToTexture(tex, filename, x, y)
    tex.save(args.texture_path)

