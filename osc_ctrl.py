#!/usr/bin/env python3

import argparse
import random
import time
import fileinput
import generate_utils

from pythonosc import udp_client
from math import ceil
from math import floor
from generate_utils import getLayerParam
from generate_utils import getSelectParam
from generate_utils import getEnableParam
from generate_utils import getBoardIndex
from generate_utils import NUM_LAYERS
from generate_utils import BOARD_ROWS
from generate_utils import BOARD_COLS

# Based on a couple experiments, this seems like about as fast as we can go
# before players start losing events.
CELL_TX_TIME_S=0.3

def usage():
    print("python3 -m pip install python-osc")
    print("python3 ./osc_ctrl.py")

def getClient(ip = "127.0.0.1", port = 9000):
    return udp_client.SimpleUDPClient(ip, port)

class EvilGlobalState():
    # Mapping from ascii char to encoded byte.
    encoding = {}
state = EvilGlobalState()

# The characters in the TaSTT are all numbered from top left to bottom right.
# This function provides a mapping from letter ('a') to index (26).
def generateEncoding():
    encoding = {}
    for i in range(0, 26):
        encoding[chr(ord('A') + i)] = i
    for i in range(26, 52):
        encoding[chr(ord('a') + i - 26)] = i
    for i in range(52, 62):
        encoding[chr(ord('0') + i - 52)] = i
    encoding[','] = 62
    encoding['.'] = 63
    encoding[' '] = 64
    encoding['?'] = 65
    encoding['!'] = 66
    encoding[';'] = 67
    encoding[':'] = 68
    encoding['-'] = 69
    encoding['_'] = 70
    encoding["'"] = 71
    encoding['"'] = 72
    return encoding
state.encoding = generateEncoding()

# Encodes a list of lines into the character set used by the board.
# Pads lines with spaces and adds lines so that the total number of
# lines sent is a multiple of the number of rows in the board.
def encodeMessage(lines):
    result = []
    lines_tmp = lines + [" "] * ((BOARD_ROWS - len(lines)) % BOARD_ROWS)
    for line in lines_tmp:
        #print("encode line {}".format(line))
        for char in line:
            if not char in state.encoding:
                print("skip unrecognized char {}".format(char))
                continue
            result.append(state.encoding[char])
        result += [state.encoding[' ']] * (BOARD_COLS - len(line))
    return result

def updateCell(client, cell_idx, letter_encoded):
    addr="/avatar/parameters/" + getLayerParam(cell_idx)
    client.send_message(addr, letter_encoded)

def enable(client):
    addr="/avatar/parameters/" + getEnableParam()
    client.send_message(addr, True)

def disable(client):
    addr="/avatar/parameters/" + getEnableParam()
    client.send_message(addr, False)

# Send a cell all at once.
# `which_cell` is an integer in the range [0,2**INDEX_BITS).
def sendMessageCellDiscrete(client, msg_cell, which_cell):
    # Disable each layer.
    disable(client)

    empty_cell = [state.encoding[' ']] * NUM_LAYERS
    if msg_cell != state.encoding[' '] * BOARD_COLS:
        addr="/avatar/parameters/" + generate_utils.getSpeechNoiseToggleParam()
        client.send_message(addr, False)

    time.sleep(CELL_TX_TIME_S / 3.0)

    # Really long messages just wrap back around.
    which_cell = (which_cell % (2 ** generate_utils.INDEX_BITS))

    s0 = ((floor(which_cell / 8) % 2) == 1)
    s1 = ((floor(which_cell / 4) % 2) == 1)
    s2 = ((floor(which_cell / 2) % 2) == 1)
    s3 = ((floor(which_cell / 1) % 2) == 1)

    # Seek to the current cell.
    addr="/avatar/parameters/" + getSelectParam(0)
    client.send_message(addr, s0)

    addr="/avatar/parameters/" + getSelectParam(1)
    client.send_message(addr, s1)

    addr="/avatar/parameters/" + getSelectParam(2)
    client.send_message(addr, s2)

    addr="/avatar/parameters/" + getSelectParam(3)
    client.send_message(addr, s3)

    # Update each letter
    for i in range(0, len(msg_cell)):
        updateCell(client, i, msg_cell[i])

    if msg_cell != empty_cell:
        addr="/avatar/parameters/" + generate_utils.getSpeechNoiseToggleParam()
        client.send_message(addr, False)

    # If we're drawing something, turn the beep on.
    if msg_cell != empty_cell:
        addr="/avatar/parameters/" + generate_utils.getSpeechNoiseToggleParam()
        client.send_message(addr, True)

    # Wait for convergence.
    time.sleep(CELL_TX_TIME_S / 3.0)

    # Enable each layer.
    enable(client)

    # Wait for convergence.
    time.sleep(CELL_TX_TIME_S / 3.0)

# The board is broken down into contiguous collections of characters called
# cells. Each cell contains `NUM_LAYERS` characters. We can update one cell
# every ~1.0 seconds. Going faster causes the board to display garbage to
# remote players.
def splitMessage(msg):
    lines = []
    line = ""
    for word in msg.split():
        while len(word) > BOARD_COLS:
            if len(line) != 0:
                lines.append(line)
                line = ""
            word_prefix = word[0:BOARD_COLS-1] + "-"
            word_suffix = word[BOARD_COLS-1:]
            print("append prefix {}".format(word_prefix))
            lines.append(word_prefix)
            word = word_suffix

        if len(line) == 0:
            line = word
            continue

        if len(line) + len(" ") + len(word) <= BOARD_COLS:
            line += " " + word
            continue

        #print("append line {}".format(line))
        lines.append(line)
        line = word

    if len(line) > 0:
        lines.append(line)

    return lines

class OscTxState:
    # The message last sent to the board.
    last_msg_encoded = []
    empty_cells_to_send_per_call = 1
    nonempty_cells_to_send_per_call = 1

    # 0 indicates it's closed. 1 indicates half size. 2 indicates full size.
    board_size = 0

def resizeBoard(num_lines, tx_state, shrink_only):

    resize_params = []

    resize_param0 = None
    resize_param1 = None

    if num_lines > BOARD_ROWS / 2:
        # Board must be expanded to full size.
        if shrink_only:
            return

        if tx_state.board_size == 2:
            return
        elif tx_state.board_size == 1:
            resize_params.append((False, True))
        else:
            resize_params.append((False, False))
            resize_params.append((False, True))
        tx_state.board_size = 2
    elif num_lines == 0:
        if not shrink_only:
            return
        # Board must be shrunk to 0 size
        if tx_state.board_size == 0:
            return
        elif tx_state.board_size == 1:
            resize_params.append((True, True))
        else:
            resize_params.append((True, False))
            resize_params.append((True, True))
        tx_state.board_size = 0
    else:
        # Board must be expanded or shrunk to half size.
        if tx_state.board_size == 0:
            if shrink_only:
                return
            resize_params.append((False, False))
        elif tx_state.board_size == 1:
            return
        else:
            if not shrink_only:
                return
            resize_params.append((True, False))
        tx_state.board_size = 1

    for resize_param_pair in resize_params:
        print("Resizing board... "),
        addr="/avatar/parameters/" + generate_utils.getResize0Param()
        client.send_message(addr, resize_param_pair[0])
        addr="/avatar/parameters/" + generate_utils.getResize1Param()
        client.send_message(addr, resize_param_pair[1])

        time.sleep(0.25)

        addr="/avatar/parameters/" + generate_utils.getResizeEnableParam()
        client.send_message(addr, True)

        # The animation is 0.5 seconds, with another 0.5 second buffer after. We
        # want to stop in that buffer.
        time.sleep(0.5)

        addr="/avatar/parameters/" + generate_utils.getResizeEnableParam()
        client.send_message(addr, False)

    # Wait a while for the animation to complete.
    time.sleep(1)
    print("done")


# Send a message to the board, but only overwrite cells that we know need to
# change.
# This may take multiple calls to complete. Returns True once it's done.
def sendMessageLazy(client, msg, tx_state):
    lines = splitMessage(msg)
    msg_encoded = encodeMessage(lines)
    msg_encoded_len = len(msg_encoded)

    empty_cells_sent = 0
    nonempty_cells_sent = 0
    n_cells = ceil(msg_encoded_len / NUM_LAYERS)
    for cell in range(0, n_cells):
        cell_begin = cell * NUM_LAYERS
        cell_end = (cell + 1) * NUM_LAYERS
        cell_msg = msg_encoded[cell_begin:cell_end]
        last_cell_msg = []

        # Skip cells we've already sent. This makes the board much more
        # responsive.
        if cell_end < len(tx_state.last_msg_encoded):
            last_cell_msg = tx_state.last_msg_encoded[cell_begin:cell_end]
        if cell_msg == last_cell_msg:
            continue

        if cell_msg == [state.encoding[' ']] * NUM_LAYERS:
            if empty_cells_sent >= tx_state.empty_cells_to_send_per_call:
                #print("empty cell budget exceeded")
                tx_state.last_msg_encoded = msg_encoded[0:cell_end]
                return False
            empty_cells_sent += 1
        else:
            if nonempty_cells_sent >= tx_state.nonempty_cells_to_send_per_call:
                #print("nonempty cell budget exceeded")
                tx_state.last_msg_encoded = msg_encoded[0:cell_end]
                return False
            nonempty_cells_sent += 1

        sendMessageCellDiscrete(client, cell_msg, cell)

    tx_state.last_msg_encoded = msg_encoded
    #resizeBoard(len(lines), tx_state, shrink_only=True)
    return True

def sendMessage(client, msg, page_sleep_s):
    lines = splitMessage(msg)
    msg = encodeMessage(lines)
    msg_len = len(msg)

    print("Encoded message: {}".format(msg))

    #openBoard()

    n_cells = ceil(msg_len / NUM_LAYERS)
    print("n_cells: {}".format(n_cells))
    for cell in range(0, n_cells):
        if cell > 0 and cell % (2 ** generate_utils.INDEX_BITS) == 0:
            print("Sleeping before sending next page")
            time.sleep(page_sleep_s)

        cell_begin = cell * NUM_LAYERS
        cell_end = (cell + 1) * NUM_LAYERS
        cell_msg = msg[cell_begin:cell_end]
        print("Send cell {}".format(cell))
        sendMessageCellDiscrete(client, cell_msg, cell)

    #closeBoard()
    #clear()

def sendRawMessage(client, msg):
    n_cells = ceil(len(msg) / NUM_LAYERS)
    for cell in range(0, n_cells):
        cell_begin = cell * NUM_LAYERS
        cell_end = (cell + 1) * NUM_LAYERS
        cell_msg = msg[cell_begin:cell_end]
        #print("Send cell {}".format(cell))
        sendMessageCellDiscrete(client, cell_msg, cell)

def clear(client):
    disable(client)

    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    client.send_message(addr, True)

    time.sleep(CELL_TX_TIME_S / 3.0)

    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    client.send_message(addr, False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
    parser.add_argument("-p", type=int, default=9000, help="OSC server port")
    args = parser.parse_args()

    client = getClient(args.i, args.p)

    state.encoding = generateEncoding()

    tx_state = OscTxState()
    for line in fileinput.input():
        while not sendMessageLazy(client, line, tx_state):
            continue
    clear()

