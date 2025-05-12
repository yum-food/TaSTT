# !!! AI ARTIFACT !!!
# This file was primarily written with AI.

import os
import argparse
from datasets import load_dataset, interleave_datasets
import sentencepiece as spm
import itertools
import random
from unidecode import unidecode

# --- Dataset 1: Wikipedia ---
DATASET_NAME_WIKI = "wikipedia"
DATASET_CONFIG_WIKI = "20220301.en"

DATASET_SPLIT_WIKI = "train"
TEXT_COLUMN_WIKI = "text"

# --- Dataset 2: DailyDialog ---
DATASET_NAME_DD = "daily_dialog"
DATASET_SPLIT_DD = "train"
UTTERANCE_COLUMN_DD = "dialog"

# --- Dataset 3: BlendedSkillTalk (includes Persona-Chat) ---
DATASET_NAME_BST = "blended_skill_talk"
DATASET_SPLIT_BST = "train"

# --- Dataset 4: OpenSubtitles ---
DATASET_NAME_OS = "Helsinki-NLP/open_subtitles"
DATASET_LANG_PAIR_OS = ("en", "fr") # Load en-fr and use the 'en' part
DATASET_SPLIT_OS = "train"
TEXT_COLUMN_OS = "en" # Access via item['translation']['en']

# Reserve one space for special "empty" token.
VOCAB_SIZE = 65535
OUTPUT_DIR = "./custom_unigram_tokenizer_65k"
MODEL_PREFIX = os.path.join(OUTPUT_DIR, "unigram")
MODEL_FILE = MODEL_PREFIX + ".model"
VOCAB_FILE = MODEL_PREFIX + ".vocab"

UNK_TOKEN = "[UNK]"
PAD_TOKEN = "[PAD]"
CONTROL_SYMBOLS = ["[CLS]", "[SEP]", "[MASK]"]

BATCH_SIZE = 1000

def wiki_iterator(dataset_wiki, batch_size=BATCH_SIZE):
    if dataset_wiki:
        for i in range(0, len(dataset_wiki), batch_size):
            yield [unidecode(text) for text in dataset_wiki[i : i + batch_size][TEXT_COLUMN_WIKI] if text]

def dd_iterator(dataset_dd, batch_size=BATCH_SIZE):
    if dataset_dd:
        current_batch = []
        for dialogue in dataset_dd:
            utterances = dialogue[UTTERANCE_COLUMN_DD]
            for utterance in utterances:
                if utterance:
                    normalized_utterance = unidecode(utterance)
                    current_batch.append(normalized_utterance)
                    if len(current_batch) == batch_size:
                        yield current_batch
                        current_batch = []
        if current_batch:
            yield current_batch

def bst_iterator(dataset_bst, batch_size=BATCH_SIZE):
    if dataset_bst:
        current_batch = []
        for session in dataset_bst:
            texts_to_add = []
            if session.get("previous_utterance"):
                texts_to_add.append(session["previous_utterance"])
            if session.get("free_messages"):
                texts_to_add.extend(session["free_messages"])
            if session.get("guided_messages"):
                texts_to_add.extend(session["guided_messages"])

            for text in texts_to_add:
                if text and isinstance(text, str):
                    normalized_text = unidecode(text)
                    current_batch.append(normalized_text)
                    if len(current_batch) == batch_size:
                        yield current_batch
                        current_batch = []
        if current_batch:
            yield current_batch

def os_iterator(dataset_os, batch_size=BATCH_SIZE, lang_code=TEXT_COLUMN_OS):
    if dataset_os:
        current_batch = []
        for item in dataset_os:
            text = item['translation'][lang_code]
            if text:
                normalized_text = unidecode(text)
                current_batch.append(normalized_text)
                if len(current_batch) == batch_size:
                    yield current_batch
                    current_batch = []
        if current_batch:
            yield current_batch

def count_wiki_items_chars(dataset_wiki):
    item_count = 0
    char_count = 0
    if dataset_wiki:
        item_count = len(dataset_wiki)
        try:
            char_count = sum(len(unidecode(text)) for text in dataset_wiki[TEXT_COLUMN_WIKI] if text and isinstance(text, str))
        except Exception:
            print(f"Warning: Direct column access for char count failed for {DATASET_NAME_WIKI}. Iterating row by row (slower).")
            char_count = sum(len(unidecode(row[TEXT_COLUMN_WIKI])) for row in dataset_wiki if row.get(TEXT_COLUMN_WIKI) and isinstance(row[TEXT_COLUMN_WIKI], str))

    return item_count, char_count

def count_dd_items_chars(dataset_dd):
    item_count = 0
    char_count = 0
    if dataset_dd:
        for dialogue in dataset_dd:
            utterances = dialogue[UTTERANCE_COLUMN_DD]
            for utterance in utterances:
                if utterance and isinstance(utterance, str):
                    item_count += 1
                    char_count += len(unidecode(utterance))
    return item_count, char_count

def count_bst_items_chars(dataset_bst):
    item_count = 0
    char_count = 0
    if dataset_bst:
        for session in dataset_bst:
            texts_to_process = []
            # Gather all potential text strings first
            prev_utt = session.get("previous_utterance")
            if prev_utt and isinstance(prev_utt, list):
                 if len(prev_utt) > 0 and isinstance(prev_utt[0], str):
                      texts_to_process.append(prev_utt[0])
            elif prev_utt and isinstance(prev_utt, str):
                texts_to_process.append(prev_utt)

            free_msgs = session.get("free_messages")
            if free_msgs and isinstance(free_msgs, list):
                 for item in free_msgs:
                     if isinstance(item, list):
                         texts_to_process.extend(msg for msg in item if msg and isinstance(msg, str))
                     elif isinstance(item, str):
                          texts_to_process.append(item)

            guided_msgs = session.get("guided_messages")
            if guided_msgs and isinstance(guided_msgs, list):
                 for item in guided_msgs:
                     if isinstance(item, list):
                         texts_to_process.extend(msg for msg in item if msg and isinstance(msg, str))
                     elif isinstance(item, str):
                          texts_to_process.append(item)

            # Count items and chars from the gathered list
            for text in texts_to_process:
                 if text and isinstance(text, str):
                     normalized_text = unidecode(text)
                     if normalized_text:
                         item_count += 1
                         char_count += len(normalized_text)

    return item_count, char_count

def count_os_items_chars(dataset_os, lang_code=TEXT_COLUMN_OS):
    item_count = 0
    char_count = 0
    if dataset_os:
        for item in dataset_os:
            text = item['translation'][lang_code]
            if text and isinstance(text, str):
                normalized_text = unidecode(text)
                if normalized_text: # Ensure not empty after unidecode
                    item_count += 1
                    char_count += len(normalized_text)
    return item_count, char_count

def load_and_count_datasets(wiki_fraction, subtitles_fraction):
    """Loads, potentially shrinks, and counts items/chars in datasets."""
    datasets = {}
    counts = {}
    total_items = 0
    total_chars = 0

    # --- Wikipedia ---
    print(f"Loading dataset 1: {DATASET_NAME_WIKI} ({DATASET_CONFIG_WIKI}), split: {DATASET_SPLIT_WIKI}")
    dataset_wiki_full = load_dataset(DATASET_NAME_WIKI, DATASET_CONFIG_WIKI, split=DATASET_SPLIT_WIKI, trust_remote_code=True)
    print(f"Original Wikipedia dataset size: {len(dataset_wiki_full):,}")

    # Shrink the Wikipedia dataset
    split_test_size = 1.0 - wiki_fraction
    shrunk_dataset_split = dataset_wiki_full.train_test_split(test_size=split_test_size, seed=random.randint(0, 1000000))
    dataset_wiki = shrunk_dataset_split['train']
    print(f"Using {wiki_fraction*100:.3f}% of Wikipedia dataset: {len(dataset_wiki):,} items")

    count_wiki, chars_wiki = count_wiki_items_chars(dataset_wiki)
    print(f"Wikipedia dataset loaded (shrunk). Precise text items: {count_wiki:,}, Characters: {chars_wiki:,}")
    datasets['wiki'] = dataset_wiki
    counts['wiki'] = (count_wiki, chars_wiki)
    total_items += count_wiki
    total_chars += chars_wiki

    # --- DailyDialog ---
    print(f"\nLoading dataset 2: {DATASET_NAME_DD}, split: {DATASET_SPLIT_DD}")
    dataset_dd = load_dataset(DATASET_NAME_DD, split=DATASET_SPLIT_DD, trust_remote_code=True)
    count_dd, chars_dd = count_dd_items_chars(dataset_dd)
    print(f"DailyDialog dataset loaded. Precise text items (utterances): {count_dd:,}, Characters: {chars_dd:,}")
    datasets['dd'] = dataset_dd
    counts['dd'] = (count_dd, chars_dd)
    total_items += count_dd
    total_chars += chars_dd

    # --- BlendedSkillTalk ---
    print(f"\nLoading dataset 3: {DATASET_NAME_BST}, split: {DATASET_SPLIT_BST}")
    dataset_bst = load_dataset(DATASET_NAME_BST, split=DATASET_SPLIT_BST, trust_remote_code=True)
    count_bst, chars_bst = count_bst_items_chars(dataset_bst)
    print(f"BlendedSkillTalk dataset loaded. Precise text items (extracted): {count_bst:,}, Characters: {chars_bst:,}")
    datasets['bst'] = dataset_bst
    counts['bst'] = (count_bst, chars_bst)
    total_items += count_bst
    total_chars += chars_bst

    # --- OpenSubtitles ---
    print(f"\nLoading dataset 4: {DATASET_NAME_OS}, lang_pair: {DATASET_LANG_PAIR_OS}, split: {DATASET_SPLIT_OS}")
    # Note: OpenSubtitles can be very large. Consider streaming or specific configurations if memory is an issue.
    # For now, loading a standard configuration.
    dataset_os = load_dataset(DATASET_NAME_OS, lang1=DATASET_LANG_PAIR_OS[0], lang2=DATASET_LANG_PAIR_OS[1], split=DATASET_SPLIT_OS, trust_remote_code=True)
    split_test_size = 1.0 - subtitles_fraction
    dataset_os = dataset_os.train_test_split(test_size=split_test_size, seed=random.randint(0, 1000000))['train']
    count_os, chars_os = count_os_items_chars(dataset_os, lang_code=TEXT_COLUMN_OS)
    print(f"OpenSubtitles dataset loaded. Precise text items: {count_os:,}, Characters: {chars_os:,}")
    datasets['os'] = dataset_os
    counts['os'] = (count_os, chars_os)
    total_items += count_os
    total_chars += chars_os

    print(f"\nTotal precise text items from loaded datasets: {total_items:,}")
    print(f"Total characters from loaded datasets: {total_chars:,}")

    return datasets, counts

def train_tokenizer(model_prefix, datasets, counts):
    """Trains a Unigram tokenizer using SentencePiece and saves it."""
    total_items = sum(c[0] for c in counts.values())
    total_chars = sum(c[1] for c in counts.values())
    if total_items == 0:
        print("Error: No items found in the datasets to train on. Exiting training.")
        return

    print(f"\nTotal precise text items for training: {total_items:,}")
    print(f"Total characters for training: {total_chars:,}")

    output_dir = os.path.dirname(model_prefix)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nStarting SentencePiece Unigram tokenizer training with vocab size: {VOCAB_SIZE}")
    print(f"Using combined dataset iterator.")
    print(f"Output model prefix: {model_prefix}")

    iterators_to_chain = []
    def flatten_iterator(iterator):
        for batch in iterator:
            for item in batch:
                yield item

    if datasets.get('wiki') and counts['wiki'][0] > 0:
        iterators_to_chain.append(flatten_iterator(wiki_iterator(datasets['wiki'])))
    if datasets.get('dd') and counts['dd'][0] > 0:
        iterators_to_chain.append(flatten_iterator(dd_iterator(datasets['dd'])))
    if datasets.get('bst') and counts['bst'][0] > 0:
        iterators_to_chain.append(flatten_iterator(bst_iterator(datasets['bst'])))
    if datasets.get('os') and counts['os'][0] > 0:
        iterators_to_chain.append(flatten_iterator(os_iterator(datasets['os'])))

    if not iterators_to_chain:
        print("Error: No valid dataset iterators available for training. Exiting.")
        return

    combined_iterator = itertools.chain(*iterators_to_chain)

    # Include whitespace symbols so we can efficiently break lines.
    # If we include the single space, it prevents the tokenizer from merging
    # spaces with regular words, and tanks the average chars/token.
    # This many tokens is kinda overkill, but it gives us a way to efficiently
    # clear even fairly large boards, so I think it's worth.
    whitespace_symbols = []
    for i in range(2, 40):
        whitespace_symbols.append('▁' * i)

    spm.SentencePieceTrainer.train(
        sentence_iterator=combined_iterator,
        model_prefix=model_prefix,
        vocab_size=VOCAB_SIZE,
        model_type='unigram',
        character_coverage=1.0,
        unk_piece=UNK_TOKEN,
        pad_piece=PAD_TOKEN,
        control_symbols=CONTROL_SYMBOLS,
        user_defined_symbols=whitespace_symbols,
        # These whitespace options must be false, or else whitespace won't
        # be respected when encoding.
        add_dummy_prefix=False,
        remove_extra_whitespaces=False,
        split_by_whitespace=False,
        num_threads=os.cpu_count(),
        input_sentence_size=total_items,
    )
    print("\nTraining finished.")
    print(f"SentencePiece model saved to: {model_prefix}.model")
    print(f"SentencePiece vocabulary saved to: {model_prefix}.vocab")

def extract_text_samples(dataset, count, num_samples, text_extractor_func):
    """Extracts a specified number of text samples from a dataset."""
    samples = []
    if dataset is None or count == 0 or num_samples == 0:
        return samples
    # Take samples from the beginning, ensure we don't exceed dataset size
    actual_samples_to_take = min(num_samples, count)
    # Use the provided function to extract text correctly for this dataset type
    samples = text_extractor_func(dataset.select(range(actual_samples_to_take)))
    return [unidecode(s) for s in samples if s and isinstance(s,str)]

def wiki_text_extractor(dataset_slice):
    """Extracts text from a slice of the Wikipedia dataset."""
    return [text for text in dataset_slice[TEXT_COLUMN_WIKI] if text]

def dd_text_extractor(dataset_slice):
    """Extracts text from a slice of the DailyDialog dataset."""
    texts = []
    for dialogue in dataset_slice:
        texts.extend(utterance for utterance in dialogue[UTTERANCE_COLUMN_DD] if utterance)
    return texts

def bst_text_extractor(dataset_slice):
    """Extracts text from a slice of the BlendedSkillTalk dataset."""
    texts = []
    for session in dataset_slice:
        if session.get("previous_utterance"):
            texts.append(session["previous_utterance"])
        if session.get("free_messages"):
            texts.extend(session["free_messages"])
        if session.get("guided_messages"):
            texts.extend(session["guided_messages"])
    return [t for t in texts if t and isinstance(t,str)] # Ensure only valid strings

def os_text_extractor(dataset_slice, lang_code=TEXT_COLUMN_OS):
    """Extracts text from a slice of the OpenSubtitles dataset."""
    texts = []
    for item in dataset_slice:
        text = item['translation'][lang_code]
        if text and isinstance(text, str):
            texts.append(text)
    return texts

def test_tokenizer(model_path, datasets, counts, sample_size=1000):
    print("\n--- Testing the trained Unigram (SentencePiece) tokenizer on data sample ---")
    if sample_size <= 0:
        print("Error: Sample size for testing must be positive.")
        return

    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    print(f"Successfully loaded SentencePiece model from: {model_path}")
    print(f"Vocabulary size: {sp.get_piece_size()}")

    # Identify available datasets with content
    available_datasets = {
        name: data
        for name, data in datasets.items()
        if counts[name][0] > 0
    }
    num_available_datasets = len(available_datasets)

    if num_available_datasets == 0:
        print("Warning: No data available in loaded datasets to sample for testing.")
        return

    print(f"Found {num_available_datasets} non-empty dataset(s) for testing.")
    print(f"Attempting to sample up to {sample_size} total items equally from these datasets...")

    # Calculate equal number of samples per available dataset
    samples_per_dataset = sample_size // num_available_datasets
    print(f"Targeting approximately {samples_per_dataset} samples per dataset.")

    test_samples = []
    dataset_extractors = {
        'wiki': wiki_text_extractor,
        'dd': dd_text_extractor,
        'bst': bst_text_extractor,
        'os': os_text_extractor,
    }

    actual_samples_collected = {}

    # Sample equally from each available dataset
    for name, dataset in available_datasets.items():
        count = counts[name][0]
        extractor = dataset_extractors[name]

        # Determine the target number of samples for *this* dataset
        num_samples_to_target = min(samples_per_dataset, count)
        if num_samples_to_target <= 0:
            print(f"  Skipping '{name}' (no items requested or available).")
            actual_samples_collected[name] = 0
            continue

        print(f"  Sampling from '{name}' (target: {num_samples_to_target} items)...")

        items_before = len(test_samples)
        # For OpenSubtitles, pass the lang_code if the extractor needs it
        if name == 'os':
            extracted_items = extract_text_samples(dataset, count, num_samples_to_target, lambda ds_slice: extractor(ds_slice, lang_code=TEXT_COLUMN_OS))
        else:
            extracted_items = extract_text_samples(dataset, count, num_samples_to_target, extractor)

        # Limit the extracted items to the target number
        final_samples_for_dataset = extracted_items[:num_samples_to_target]

        test_samples.extend(final_samples_for_dataset)
        items_added = len(final_samples_for_dataset)
        actual_samples_collected[name] = items_added
        print(f"    Added {items_added} items from '{name}'.")

    actual_sample_size = len(test_samples)
    if actual_sample_size == 0:
        print("\nCould not gather any samples for testing.")
        print("--- Test finished ---")
        return

    print(f"\n--- Starting Test Run ---")
    print(f"Testing on {actual_sample_size} sampled text items (final count).")
    print(f"Samples breakdown: {actual_samples_collected}")

    total_chars = 0
    total_tokens = 0
    examples_to_show = 5
    examples_shown = 0

    random.shuffle(test_samples)

    for i, text_sample in enumerate(test_samples):
        if not text_sample: # Should already be filtered by extractor, but double-check
            continue
        try:
            tokens = sp.encode_as_pieces(text_sample)
            num_tokens = len(tokens)
            num_chars = len(text_sample)
            total_tokens += num_tokens
            total_chars += num_chars

            if examples_shown < examples_to_show:
                print(f"\nSample {examples_shown + 1} (Overall index {i}):") # Clarify sample index
                print(f"  Text ({num_chars} chars): {text_sample[:100]}{'...' if len(text_sample)>100 else ''}")
                print(f"  Tokens ({num_tokens}): {tokens}")
                examples_shown += 1
        except Exception as e:
            print(f"\nWarning: Error encoding sample (Overall index {i}) with SentencePiece. Skipping sample. Error: {e}")
            print(f"Problematic sample text: {text_sample[:100]}...") # Show problematic text

    # --- Test Summary ---
    if total_tokens > 0 and total_chars > 0 : # Avoid division by zero
        avg_chars_per_token = total_chars / total_tokens
        print(f"\n--- Test Summary ---")
        print(f"Tested on {actual_sample_size} text items.")
        print(f"Final samples breakdown: {actual_samples_collected}")
        print(f"Total characters in final sample: {total_chars:,}")
        print(f"Total tokens in final sample: {total_tokens:,}")
        print(f"Average characters per token: {avg_chars_per_token:.4f}")
    elif actual_sample_size > 0:
         print("\n--- Test Summary ---")
         print(f"Tested on {actual_sample_size} text items.")
         print(f"Final samples breakdown: {actual_samples_collected}")
         print("No valid tokens were generated from the sample data (or samples were empty after unidecode).")
    else:
        # This case should be caught earlier, but included for completeness
        print("\n--- Test Summary ---")
        print("No samples were collected or processed.")

    print("--- Test finished ---")

def parse_args():
    parser = argparse.ArgumentParser(description="Train and test a Unigram tokenizer on combined datasets.")
    parser.add_argument("--train", action="store_true", help="Train the tokenizer on datasets")
    parser.add_argument("--test", action="store_true", help="Test the trained tokenizer")
    parser.add_argument("--sample_size", type=int, default=1000, help="Number of items to sample for testing")
    parser.add_argument("--wiki_fraction", type=float, default=0.05, help="Fraction of Wikipedia dataset to use (e.g., 0.05 for 5%)")
    parser.add_argument("--subtitles_fraction", type=float,
                        default=0.05, help="Fraction of opensubtitles dataset to use (e.g., 0.05 for 5%)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Load datasets and calculate counts once
    print("--- Loading and Counting Datasets ---")
    datasets, counts = load_and_count_datasets(wiki_fraction=args.wiki_fraction, subtitles_fraction=args.subtitles_fraction)
    print("--- Dataset Loading Finished ---")

    run_train = args.train
    run_test = args.test

    # If no arguments provided, run both by default
    if not args.train and not args.test:
        run_train = True
        run_test = True

    if run_train:
        print("\n--- Starting Tokenizer Training ---")
        train_tokenizer(MODEL_PREFIX, datasets, counts)
        print("--- Training Finished ---")

    if run_test:
        # Ensure tokenizer file exists if training didn't just run
        if not os.path.exists(MODEL_FILE):
            print(f"\nError: SentencePiece model file {MODEL_FILE} not found. Cannot run test.")
            print("Please run with --train first or ensure the file exists.")
        else:
            print("\n--- Starting Tokenizer Testing ---")
            test_tokenizer(MODEL_FILE, datasets, counts, sample_size=args.sample_size)
            print("--- Testing Finished ---")

    print("\nScript finished.")
