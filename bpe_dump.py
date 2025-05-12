import math
import sentencepiece as spm

def get_tokenizer():
    model_path = "./custom_unigram_tokenizer_65k/unigram.model"
    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    return sp

tokenizer = get_tokenizer()

print(f"vocabulary size: {tokenizer.get_piece_size()}")
# Sentencepiece uses U+2581 (lower one eighth block) to indicate a space before
# a subword.
sp_space = chr(9601)
tokens_with_non_ascii = set()
subword_len_histo = dict()
# The sum of the lengths of each subword in the vocabulary. These are rounded
# up to 4 characters.
vocab_len_4c_quantized = 0

for i in range(tokenizer.get_piece_size()):
    k = tokenizer.id_to_piece(i)
    v = i
    print(f"  Original token ({v}): {repr(k)} ({' '.join(str(ord(k_c)) for k_c in k)})")
    for k_c in k:
        if ord(k_c) > 127 and ord(k_c) != 9601:
            tokens_with_non_ascii.add(k)
            break
    k_processed = k.replace(sp_space, ' ')
    if not k.startswith(sp_space) and k not in ["[UNK]", "[PAD]", "[CLS]", "[SEP]", "[MASK]"]:
        k_processed = k
    else:
        k_processed = k_processed

    current_len = len(k_processed)
    if current_len in subword_len_histo:
        subword_len_histo[current_len] += 1
    else:
        subword_len_histo[current_len] = 1

    vocab_len_4c_quantized += math.ceil(current_len / 4.0) * 4.0
    print(f"  {v}: {k_processed}")

print(f"Num tokens with non-ascii: {len(tokens_with_non_ascii)} ({100 * len(tokens_with_non_ascii) / tokenizer.get_piece_size():.2f})%")

print(f"Subword length histogram:")
avg_subword_len = 0
total_pieces_for_avg = 0
for k_len, v_count in sorted(subword_len_histo.items(), key=lambda x: x[0]):
    avg_subword_len += k_len * v_count
    total_pieces_for_avg += v_count
    print(f"  {k_len}: {v_count}")

if total_pieces_for_avg > 0:
    avg_subword_len /= total_pieces_for_avg
    print(f"Average subword length: {avg_subword_len:.4f}")
else:
    print("Average subword length: N/A (no pieces analyzed)")

print(f"Sum of all subword lengths, quantized to 4 character chunks: {vocab_len_4c_quantized}")
