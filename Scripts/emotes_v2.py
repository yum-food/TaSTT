#!/usr/bin/env python3

import argparse
import os
import pickle
import sys

from math import floor
from PIL import Image
from typing import Any, Dict, List, Tuple

# The character range [0x0000, 0xDFFF] is reserved for text.
# The range [0xE000, infinity) is left over for emotes.
EMOTES_LETTER_OFFSET = 0xE000
EMOTES_HEIGHT = 512
EMOTES_TEX_SZ = 4096

def superimpose_image(base_img: Image, overlay_img: Image, position: Tuple[int, int]) -> Image:
    base_img.paste(overlay_img, position, overlay_img)
    return base_img

def i_to_pos(i, sm_wd, sm_ht, big_wd, big_ht) -> Tuple[int, int]:
    x = i * sm_wd % big_wd
    row = floor((i * sm_wd) / big_wd)
    y = row * sm_ht
    return int(x), int(y)

def get_images_from_directory(directory_path: str) -> List[Tuple[Any, str]]:
    images = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and file_path.endswith(".png"):
            image = Image.open(file_path).convert("RGBA")
            name = os.path.basename(filename).split('.')[0]
            images.append((image, name))
    return images

def split_resized_image(img, wd: int, ht: int) -> List[Any]:
    aspect_ratio = img.width / img.height
    width = int(ht * aspect_ratio)
    img = img.resize((width, ht))

    split_images = []
    for i in range(0, img.width, wd):
        split_image = img.crop((i, 0, i + wd, ht))
        split_images.append(split_image)

    return split_images

def resize_image_with_aspect_ratio(img: Image, aspect_ratio: float) -> Image:
    original_width, original_height = img.size
    new_width = int(original_height * aspect_ratio)
    new_height = original_height
    return img.resize((new_width, new_height))

def resize_image_to_height(img: Image, height: int) -> Image:
    aspect_ratio = img.width / img.height
    new_width = int(height * aspect_ratio)
    return img.resize((new_width, height))

class EmotesState:
    def __init__(self):
        self.bits = {}

    def load(self, pickle_path):
        try:
            with open(pickle_path, 'rb') as f:
                self.bits = pickle.load(f)
        except FileNotFoundError:
            print(f"Emotes map does not exist at {pickle_path}",
                    file=sys.stderr)

    # This is quite slow since we do a search and replace (O(n))
    # for each keyword O(m) times each variant of said keyword (O(k)).
    # Thus total complexity is O(m*n*k). All three of these numbers are
    # typically small: m and k typically < 10, n typically < 200.
    #
    # Naively one might split the input into words, but this only works for
    # English-like languages. Eastern Asian languages like Japanese don't
    # really divide into words AFAIK so this wouldn't work for them.
    #
    # Unless the performance becomes a user-reported problem, stick with this
    # inefficient but reliable method.
    def encode_emotes(self, msg: str):
        for keyword, bits in self.bits.items():
            bits_str = ""
            for bit in bits:
                bits_str += chr(bit)
            # ALL CAPS
            tmp = keyword.upper()
            msg = msg.replace(tmp, bits_str)
            # lowercase
            tmp = keyword.lower()
            msg = msg.replace(tmp, bits_str)
            # Capitalized
            tmp = keyword.lower().capitalize()
            msg = msg.replace(tmp, bits_str)
            # dashes inserted
            tmp = '-'.join(keyword.upper())
            msg = msg.replace(tmp, bits_str)
            # uppercase, spaces inserted
            tmp = ' '.join(keyword.upper())
            msg = msg.replace(tmp, bits_str)
            # lowercase, spaces inserted
            tmp = ' '.join(keyword.lower())
            msg = msg.replace(tmp, bits_str)
            # uppercase, commas and spaces inserted
            tmp = ', '.join(keyword.upper())
            msg = msg.replace(tmp, bits_str)
        return msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=str, help="directory to get images from")
    parser.add_argument("board_aspect_ratio", help="aspect ratio of a cell in the board")
    parser.add_argument("texture_aspect_ratio", help="aspect ratio of a cell in the texture")
    parser.add_argument("tex_path", type=str, help="path to save the texture to")
    parser.add_argument("pickle_path", type=str, help="path to save the texture index to")
    args = parser.parse_args()

    directory_path = args.dir
    board_aspect_ratio = int(args.board_aspect_ratio)
    texture_aspect_ratio = int(args.texture_aspect_ratio)

    base_img = Image.new("RGBA", (EMOTES_TEX_SZ, EMOTES_TEX_SZ), (0, 0, 0, 0))
    images_and_filenames = get_images_from_directory(directory_path)
    i = 0
    bits = {}  # Dict[str, List[int]]
    for img, filename in images_and_filenames:
        print(f"Adding {filename}")
        img = resize_image_with_aspect_ratio(img, board_aspect_ratio)
        img = resize_image_to_height(img, EMOTES_HEIGHT)
        img_fragments = split_resized_image(img, int(EMOTES_HEIGHT / texture_aspect_ratio), EMOTES_HEIGHT)
        img_bits = []  # List[int]
        for img_fragment in img_fragments:
            i = i + 1
            img_pos = i_to_pos(i, 
                    EMOTES_HEIGHT / texture_aspect_ratio, EMOTES_HEIGHT,
                    EMOTES_TEX_SZ, EMOTES_TEX_SZ)
            print(f"{img_pos}")
            superimpose_image(base_img, img_fragment, img_pos)
            img_bits.append(EMOTES_LETTER_OFFSET + i)
        emote_name = os.path.basename(filename).split('.')[0]
        print(f"{emote_name} -> {img_bits}")
        bits[emote_name] = img_bits
    base_img.save(args.tex_path)
    with open(args.pickle_path, 'wb') as f:
        pickle.dump(bits, f)

