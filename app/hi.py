import app_config
import argparse
import io
from math import floor, ceil
import msvcrt
import os
from pythonosc import udp_client
import sentencepiece as spm
from shared_thread_data import SharedThreadData
import stt
import sys
import threading
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

TESTS_ENABLED = True

# 0 = quiet, 1 = verbose, 2 = very verbose
LOG_LEVEL = 0

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_ROOT)

def get_tokenizer():
    model_path = os.path.join(PROJECT_ROOT, "custom_unigram_tokenizer_65k", "unigram.model")
    print(f"Loading SentencePiece tokenizer from: {model_path}")
    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    print(f"Successfully loaded SentencePiece model. Vocab size: {sp.get_piece_size()}")
    return sp

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="Path to config file (YAML).", required=True)
    return parser.parse_args()

def assert_equal(a, b):
    err_msg = f"{a} != {b}"
    assert a == b, err_msg

# Turn a whitespace-delimited string into a list of strings no longer than
# `cols`.
# Preferentially breaks strings at whitespace boundaries. Preserves whitespace
# between words, except if that whitespace comes between lines. Breaks words
# longer than `cols` with a hyphen.
def wrap_line(line: str, cols):
    # First, split line into alternating chunks of words and whitespace.
    def get_sequences(line):
        is_space = False
        sequences = []
        seq_start = 0
        seq_end = -1
        for i in range(0, len(line)):
            if line[i].isspace():
                if is_space:
                    seq_end = i
                    continue
                # We were looking at text, now we see whitespace.
                seq = line[seq_start:seq_end+1]
                if len(seq) > 0:
                    sequences.append(seq)
                seq_start = i
                seq_end = i
                is_space = True
            else:
                if not is_space:
                    seq_end = i
                    continue
                # We were looking at whitespace, now we see text.
                seq = line[seq_start:seq_end+1]
                if len(seq) > 0:
                    sequences.append(seq)
                seq_start = i
                seq_end = i
                is_space = False
        sequences.append(line[seq_start:seq_end+1])
        return sequences
    if TESTS_ENABLED:
        assert_equal(get_sequences("foo"), ["foo"])
        assert_equal(get_sequences("foo bar"), ["foo", " ", "bar"])
        assert_equal(get_sequences(" foo bar"), [" ", "foo", " ", "bar"])
        assert_equal(get_sequences(" foo  bar"), [" ", "foo", "  ", "bar"])

    # Next, greedily construct lines out of those sequences.
    # Whitespace gets treated specially. If it would push us over the limit, we
    # end the line and drop the whitespace.
    sequences = get_sequences(line)
    def coalesce_sequences(sequences, cols):
        cur_line = ""
        lines = []
        for seq in sequences:
            if len(cur_line) + len(seq) <= cols:
                cur_line += seq
                continue
            if seq.isspace():
                lines.append(cur_line)
                cur_line = ""
                continue
            if len(cur_line) > 0:
                lines.append(cur_line)
            # Edge case: text sequence is longer than a line.
            while len(seq) > cols:
                seq_prefix = seq[0:cols-1] + "-"
                seq = seq[cols-1:]
                lines.append(seq_prefix)
            cur_line = seq
        if len(cur_line) > 0:
            lines.append(cur_line)
        return lines
    if TESTS_ENABLED:
        assert_equal(coalesce_sequences(get_sequences("foo bar"), 3), ["foo", "bar"])
        assert_equal(coalesce_sequences(get_sequences("foo bar"), 4), ["foo ", "bar"])
        assert_equal(coalesce_sequences(get_sequences("foo  bar"), 4), ["foo", "bar"])
        assert_equal(coalesce_sequences(get_sequences("foobar"), 3), ["fo-", "ob-", "ar"])
        assert_equal(coalesce_sequences(get_sequences("f obar"), 3), ["f ", "ob-", "ar"])

    lines = coalesce_sequences(sequences, cols)

    # Next, pad each line with whitespace.
    def pad_lines(lines, cols):
        for i in range(0, len(lines)):
            lines[i] += ' ' * (cols - len(lines[i]))
        return lines
    if TESTS_ENABLED:
        assert_equal(pad_lines(["foo", "ba"], 4), ["foo ", "ba  "])
        assert_equal(pad_lines(["foo"], 2), ["foo"])

    return pad_lines(lines, cols)

def get_blocks(lines, tokenizer, block_width, num_blocks):
    if LOG_LEVEL == 2:
        print(f"Lines sent to tokenizer: {''.join(lines)}")
    tokens = tokenizer.encode_as_ids(''.join(lines))
    if LOG_LEVEL == 2:
        print(f"Tokens: {tokens}")
    pieces = []
    for tok in tokens:
        piece = tokenizer.id_to_piece(tok)
        pieces.append(piece)
    if LOG_LEVEL == 2:
        print(f"Pieces: {pieces}")

    # Group tokens into blocks and pad with empty characters.
    # Also get visual pointers - the location where each block will be rendered.
    def get_blocks():
        blocks = []
        visual_pointer = 0
        visual_pointers = []
        for i in range(0, ceil(len(tokens) / block_width)):
            visual_pointers.append(visual_pointer)
            block = []
            for j in range(0, block_width):
                if i*block_width + j >= len(tokens):
                    # Pad block with empty characters. 65535 is a special token.
                    block += [65535] * (block_width - len(block))
                    break
                block.append(tokens[i*block_width+j])
                visual_pointer += len(pieces[i*block_width+j])
            blocks.append(block)
        return (blocks, visual_pointers)
    blocks, visual_pointers = get_blocks()
    if LOG_LEVEL == 2:
        print(f"Blocks: {blocks}")
        print(f"Visual pointers: {visual_pointers}")

    # Set all blocks up to the next `num_blocks` boundary to blank tokens.
    # This handles the edge case where a prior message wrote data there which
    # is covering up our new data.
    def pad_blocks(blocks, visual_pointers):
        cur_num_blocks = len(blocks)
        num_pad_blocks = num_blocks - cur_num_blocks
        for i in range(0, num_pad_blocks):
            blocks.append([65535] * block_width)
            visual_pointers.append(255)
        return blocks, visual_pointers
    blocks, visual_pointers = pad_blocks(blocks, visual_pointers)
    if LOG_LEVEL == 2:
        print(f"Blocks (padded): {blocks}")
        print(f"Visual pointers (padded): {visual_pointers}")

    return blocks, visual_pointers

def calc_diff(prev_blocks, prev_visual_pointers, cur_blocks,
              cur_visual_pointers):
    diff_indices = []
    diff_blocks = []
    diff_visual_pointers = []

    for i in range(0, len(cur_blocks)):
        if i >= len(prev_blocks):
            diff_blocks.append(cur_blocks[i])
            diff_visual_pointers.append(cur_visual_pointers[i])
            diff_indices.append(i)
            continue
        if prev_blocks[i] != cur_blocks[i] or prev_visual_pointers[i] != cur_visual_pointers[i]:
            diff_blocks.append(cur_blocks[i])
            diff_visual_pointers.append(cur_visual_pointers[i])
            diff_indices.append(i)

    return diff_indices, diff_blocks, diff_visual_pointers

def send_data(osc_client, indices, blocks, visual_pointers):
    def split_blocks_by_byte(blocks):
        blocks_byte00 = []
        blocks_byte01 = []
        for block in blocks:
            block_byte00 = []
            block_byte01 = []
            for datum in block:
                block_byte00.append((datum >> 0) & 0xFF)
                block_byte01.append((datum >> 8) & 0xFF)
            blocks_byte00.append(block_byte00)
            blocks_byte01.append(block_byte01)
        return blocks_byte00, blocks_byte01

    blocks_byte00, blocks_byte01 = split_blocks_by_byte(blocks)
    if LOG_LEVEL == 2:
        print(f"Blocks (byte 00): {blocks_byte00}")
        print(f"Blocks (byte 01): {blocks_byte01}")

    def send_osc(osc_client, addr, data):
        #print(f"Sending {data} to {addr}")
        osc_client.send_message(addr, data)

    for i in range(0, len(blocks)):
        lp_int = indices[i]
        lp_param = "_Unigram_Letter_Grid_OSC_Pointer"
        addr = "/avatar/parameters/" + lp_param
        send_osc(osc_client, addr, lp_int)

        vp_float = (-127.5 + visual_pointers[i]) / 127.5
        vp_param = f"_Unigram_Letter_Grid_OSC_Visual_Pointer"
        addr = "/avatar/parameters/" + vp_param
        send_osc(osc_client, addr, vp_float)
        if LOG_LEVEL == 2:
            print(f"Sending block {blocks[i]} at {visual_pointers[i]} index {indices[i]}")
        for j in range(0, len(blocks[i])):
            byte00_float = (-127.5 + blocks_byte00[i][j]) / 127.5
            byte01_float = (-127.5 + blocks_byte01[i][j]) / 127.5
            byte00_param  = f"_Unigram_Letter_Grid_OSC_Datum{j:02}_Byte00"
            byte01_param  = f"_Unigram_Letter_Grid_OSC_Datum{j:02}_Byte01"
            addr = "/avatar/parameters/" + byte00_param
            send_osc(osc_client, addr, byte00_float)
            addr = "/avatar/parameters/" + byte01_param
            send_osc(osc_client, addr, byte01_float)
        time.sleep(0.34)

def getOscClient(ip = "127.0.0.1", port = 9000):
    return udp_client.SimpleUDPClient(ip, port)

class InputState:
    def __init__(self):
        self.page = 0
        # Initialize the known state of the board to empty array. This will cause
        # our paging logic to re-send everything the first time around.
        self.blocks = []
        self.visual_pointers = []
        pass

def handle_input(state: InputState, line: str, tokenizer, osc_client, cfg):
    line_wrapped = wrap_line(line, cfg["cols"])
    if TESTS_ENABLED:
        for line in line_wrapped:
            assert_equal(len(line), cfg["cols"])
    if LOG_LEVEL == 2:
        print(f"Wrapped lines: {line_wrapped}")

    # Get several blank lines whenever we roll over.
    # It's better for the reader to have some continuity when the board pages
    # over. If we simply replaced the entire screen, it would be harder to
    # understand.
    line_rollover = cfg["rows"] - 2
    blank_line = ' ' * cfg["cols"]
    # We show a full page, then only `line_rollover` additional lines per page.
    end_ptr = cfg["rows"]
    which_page = 0
    while end_ptr < len(line_wrapped):
        end_ptr += line_rollover
        which_page += 1
    if state.page != which_page:
        state.blocks = []
        state.visual_pointers = []
        state.page = which_page
    line_wrapped = line_wrapped[end_ptr-cfg["rows"]:]

    # Get blocks and visual pointers.
    blocks, visual_pointers = get_blocks(line_wrapped, tokenizer,
                                         cfg["block_width"], cfg["num_blocks"])

    # Note that because we only send one page of data at a time, we don't have
    # to worry about wrapping visual pointers! We will basically never run out
    # of space.
    indices, diff_blocks, diff_visual_pointers = calc_diff(state.blocks, state.visual_pointers, blocks, visual_pointers)
    indices = [idx % cfg["num_blocks"] for idx in indices]
    # Send only one block at a time to make things snappier in interactive use
    # case.
    # TODO use a continuation (yield) instead of returning. Then we can be a
    # little lighter on the cpu. Measurements show that this script is
    # already very light but we're clearly wasting a lot of work by
    # re-tokenizing the entire input every time we send a block.
    if len(indices) == 0:
        return
    if indices[0] == len(state.blocks):
        state.blocks.append(diff_blocks[0])
        state.visual_pointers.append(diff_visual_pointers[0])
    elif indices[0] > len(state.blocks):
        print(f"This should never happen!")
        sys.exit(1)
    else:
        state.blocks[indices[0]] = diff_blocks[0]
        state.visual_pointers[indices[0]] = diff_visual_pointers[0]

    send_data(osc_client, [indices[0]], [diff_blocks[0]], [diff_visual_pointers[0]])

def osc_thread(shared_data: SharedThreadData):
    tokenizer = get_tokenizer()
    osc_client = getOscClient()

    # Prime the board
    print("Priming the board")
    input_state = InputState()
    handle_input(input_state, "", tokenizer, osc_client, shared_data.cfg)

    while not shared_data.exit_event.is_set():
        word_copy = ""
        with shared_data.word_lock:
            word_copy = shared_data.word
        handle_input(input_state, word_copy, tokenizer, osc_client, shared_data.cfg)
        time.sleep(0.01)

if __name__ == "__main__":
    cli_args = parse_args()
    cfg = app_config.getConfig(cli_args.config)
    shared_data = SharedThreadData(cfg)
    if False:
        osc_thread = threading.Thread(
                target=osc_thread,
                args=(shared_data,))
        osc_thread.start()

    transcribe_thread = threading.Thread(
            target=stt.transcriptionThread,
            args=(shared_data,))
    transcribe_thread.start()

    word_is_over = False
    local_word = ""
    while True:
        char_bytes = msvcrt.getch()
        if char_bytes == b'\x03':  # ctrl+C
            break

        time.sleep(0.1)
        continue

        try:
            char = char_bytes.decode('utf-8')
            if char == '\r' or char == '\n':
                word_is_over = True
                continue
        except UnicodeDecodeError:
            print(f"Unsupported character: {char_bytes}")
            if char_bytes == b'\x00' or char_bytes == b'\xe0':
                special_char = msvcrt.getch()
            continue

        if char_bytes == b'\x03':  # ctrl+C
            break
        elif char_bytes == b'\x08':  # backspace
            with shared_data.word_lock:
                shared_data.word = shared_data.word[:-1]
                local_word = shared_data.word
        elif char_bytes == b'\x0c':  # ctrl+L
            with shared_data.word_lock:
                shared_data.word = ""
                local_word = shared_data.word
        elif word_is_over:
            with shared_data.word_lock:
                shared_data.word = char
                local_word = shared_data.word
            word_is_over = False
        else:
            with shared_data.word_lock:
                shared_data.word += char
                local_word = shared_data.word
        print(local_word + "_")
    shared_data.exit_event.set()
    if False:
        osc_thread.join()
    transcribe_thread.join()

