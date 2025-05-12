import argparse
import sentencepiece as spm

def get_tokenizer():
    model_path = "./custom_unigram_tokenizer_65k/unigram.model"
    print(f"Loading SentencePiece tokenizer from: {model_path}")
    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    print(f"Successfully loaded SentencePiece model. Vocab size: {sp.get_piece_size()}")
    return sp

def parse_args():
    parser = argparse.ArgumentParser(description="Tokenize a given string using a SentencePiece model.")
    parser.add_argument("text", type=str, help="The string to tokenize.")
    args = parser.parse_args()
    return args

args = parse_args()
tok = get_tokenizer()
tokens = tok.encode_as_pieces(args.text)
print("Tokens:", tokens)

token_ids = tok.encode_as_ids(args.text)
print("Token IDs:", token_ids)

# Split each token ID into two 8-bit chunks (high byte, low byte)
byte_pairs = [(tid >> 8, tid & 0xFF) for tid in token_ids]
print("Token ID Byte Pairs:", byte_pairs)
