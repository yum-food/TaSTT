from math import ceil, floor
from PIL import Image
from unidecode import unidecode
import sentencepiece as spm

IMG_RES = 512  # square image

def get_tokenizer():
    use_sentencepiece = True

    if not use_sentencepiece:
        from tokenizers import Tokenizer
        tokenizer_json = "./custom_wordpiece_tokenizer_65k/tokenizer.json"
        print(f"Loading Tokenizers library tokenizer from: {tokenizer_json}")
        return Tokenizer.from_file(tokenizer_json)
    else:
        model_path = "./custom_unigram_tokenizer_65k/unigram.model"
        print(f"Loading SentencePiece tokenizer from: {model_path}")
        sp = spm.SentencePieceProcessor()
        sp.load(model_path)
        print(f"Successfully loaded SentencePiece model. Vocab size: {sp.get_piece_size()}")
        return sp

def get_words():
    tokenizer = get_tokenizer()

    print(f"vocabulary size: {tokenizer.get_piece_size()}")
    # sp_space = sentencepiece space.
    # A special character sentencepiece uses to represent spaces before words.
    sp_space = chr(9601)
    words = []

    # Accumulate words into a list, indexed by the token number. Sanitize them as
    # you go.
    for i in range(tokenizer.get_piece_size()):
        word = tokenizer.id_to_piece(i)
        tok = i
        #print(f"  Original token ({tok}): {repr(word)} ({' '.join(str(ord(c)) for c in word)})")
        word_sanitized = ""
        # Dirty hack: convert non-ASCII characters to nearest ASCII equivalent
        for c in word:
            if ord(c) > 127 and c != sp_space:
                c_plain = unidecode(c)
                print(f"  Resolved {c} to {c_plain}")
                word_sanitized += c_plain
            else:
                word_sanitized += c
        # Replace sp_space with ' '
        word_sanitized = word_sanitized.replace(sp_space, ' ')
        #print(f"  {tok}: {word_sanitized}")
        words.append(word_sanitized)

    # Special word: empty string. SentencePiece doesn't support this natively.
    words.append('')

    return words

# Fold a flat index into a IMG_RESxIMG_RES box. Return the (x,y) coordinate of
# the folded index.
def fold_idx(flat_idx):
    return (flat_idx % IMG_RES, int(floor(flat_idx / IMG_RES)))

def unfold_idx(coord):
    return coord[0] + coord[1] * IMG_RES

assert unfold_idx(fold_idx(1533125)) == 1533125
assert unfold_idx(fold_idx(8538235)) == 8538235
assert fold_idx(unfold_idx((192,235))) == (192,235)
assert fold_idx(unfold_idx((83,388))) == (83,388)

def generate_lut(words, filename):
    # Write the texture header.
    black = (0, 0, 0, 255)
    img = Image.new('RGBA', (IMG_RES, IMG_RES), black)

    # The header is `len(words)` slots long. Thus the actual LUT content starts at
    # the index `len(words)`.
    pixel_data = img.load()
    lut_ptr = len(words)
    for i in range(0, len(words)):
        # Get pointer to the actual word data.
        tok_ptr = lut_ptr
        tok_len = len(words[i])
        rgba = ((tok_ptr >>  0) & 0xFF,
                (tok_ptr >>  8) & 0xFF,
                (tok_ptr >> 16) & 0xFF,
                tok_len)
        print(f"Writing {rgba} to {i} / {fold_idx(i)}")
        idx_x, idx_y = fold_idx(i)
        pixel_data[idx_x, idx_y] = rgba

        for j in range(0, ceil(tok_len/4.0)):
            quad_ptr = tok_ptr + j
            tok_0 = ord(words[i][j*4])
            tok_1 = ord(words[i][j*4+1] if tok_len > j*4+1 else ' ')
            tok_2 = ord(words[i][j*4+2] if tok_len > j*4+2 else ' ')
            tok_3 = ord(words[i][j*4+3] if tok_len > j*4+3 else ' ')
            rgba = (tok_0, tok_1, tok_2, tok_3)
            idx_x, idx_y = fold_idx(quad_ptr)
            print(f"  Writing {rgba} to {quad_ptr} / {fold_idx(quad_ptr)}")
            pixel_data[idx_x, idx_y] = rgba

        # Advance the LUT ptr. Since we store 4 chars per pixel (RGBA), we advance
        # it by ceil(tok_len/4).
        lut_ptr += int(ceil(tok_len/4.0))

    pretty = False
    if pretty:
        for y in range(0, IMG_RES):
            for x in range(0, IMG_RES):
                rgba = pixel_data[x, y]
                pixel_data[x, y] = (rgba[0], rgba[1], rgba[2], 255)

    print(f"Saving to {filename}")
    img.save(filename)

if __name__ == "__main__":
    words = get_words()
    generate_lut(words, "bpe_lut.png")
