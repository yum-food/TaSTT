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

#CELL_TX_TIME_S=3.0
#CELL_TX_TIME_S=1.0
CELL_TX_TIME_S=0.1

def usage():
    print("python3 -m pip install python-osc")
    print("python3 ./osc_ctrl.py")

parser = argparse.ArgumentParser()
parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
parser.add_argument("-p", type=int, default=9000, help="OSC server port")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.i, args.p)

class EvilGlobalState():
    # Mapping from ascii char to encoded byte.
    encoding = {}
state = EvilGlobalState()

def generateEncoding(state):
    for i in range(0, 26):
        state.encoding[chr(ord('A') + i)] = i
    for i in range(26, 52):
        state.encoding[chr(ord('a') + i - 26)] = i
    for i in range(52, 62):
        state.encoding[chr(ord('0') + i - 52)] = i
    state.encoding[','] = 62
    state.encoding['.'] = 63
    state.encoding[' '] = 64
    state.encoding['?'] = 65
    state.encoding['!'] = 66
    state.encoding[';'] = 67
    state.encoding[':'] = 68
    state.encoding['-'] = 69
    state.encoding['_'] = 70
    state.encoding["'"] = 71
    state.encoding['"'] = 72
generateEncoding(state)

# Encodes a list of lines into the character set used by the board.
# Pads lines with spaces and adds lines so that the total number of
# lines sent is a multiple of the number of rows in the board.
def encodeMessage(lines):
    result = []
    # Pad the number of lines up to a multiple of BOARD_ROWS.
    print("Pad {} lines".format(BOARD_ROWS - (len(lines) % BOARD_ROWS)))
    lines += [" "] * ((BOARD_ROWS - len(lines)) % BOARD_ROWS)
    for line in lines:
        print("encode line {}".format(line))
        for char in line:
            result.append(state.encoding[char])
        result += [state.encoding[' ']] * (BOARD_COLS - len(line))
    return result

def updateCell(cell_idx, letter_encoded, s0, s1, s2, s3):
    addr="/avatar/parameters/" + getLayerParam(cell_idx)
    client.send_message(addr, letter_encoded)

    addr="/avatar/parameters/" + getSelectParam(cell_idx, 0)
    client.send_message(addr, s0)

    addr="/avatar/parameters/" + getSelectParam(cell_idx, 1)
    client.send_message(addr, s1)

    addr="/avatar/parameters/" + getSelectParam(cell_idx, 2)
    client.send_message(addr, s2)

    addr="/avatar/parameters/" + getSelectParam(cell_idx, 3)
    client.send_message(addr, s3)

def enable():
    addr="/avatar/parameters/" + getEnableParam()
    client.send_message(addr, True)

def disable():
    addr="/avatar/parameters/" + getEnableParam()
    client.send_message(addr, False)

# Send a cell all at once.
# `which_cell` is an integer in the range [0,2**INDEX_BITS).
def sendMessageCellDiscrete(msg_cell, which_cell):
    # Disable each layer.
    disable()

    time.sleep(CELL_TX_TIME_S / 3.0)

    # Really long messages just wrap back around.
    which_cell = (which_cell % (2 ** generate_utils.INDEX_BITS))

    s0 = ((floor(which_cell / 8) % 2) == 1)
    s1 = ((floor(which_cell / 4) % 2) == 1)
    s2 = ((floor(which_cell / 2) % 2) == 1)
    s3 = ((floor(which_cell / 1) % 2) == 1)

    print("Cell s0/s1/s2/s3: {}/{}/{}/{}".format(s0,s1,s2,s3))
    # Seek each layer to the current cell.
    for i in range(0, len(msg_cell)):
        updateCell(i, msg_cell[i], s0, s1, s2, s3)

    # Wait for convergence.
    time.sleep(CELL_TX_TIME_S / 3.0)

    # Enable each layer.
    # TODO(yum_food) for some reason, if we don't active every layer, the
    # desired subset won't reliably fire. Why?
    enable()

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

        print("append line {}".format(line))
        lines.append(line)
        line = word

    if len(line) > 0:
        lines.append(line)

    return lines

def sendMessage(msg):
    lines = splitMessage(msg)
    msg = encodeMessage(lines)
    msg_len = len(msg)

    print("Encoded message: {}".format(msg))

    #openBoard()

    n_cells = ceil(msg_len / NUM_LAYERS)
    print("n_cells: {}".format(n_cells))
    for cell in range(0, n_cells):
        cell_begin = cell * NUM_LAYERS
        cell_end = (cell + 1) * NUM_LAYERS
        cell_msg = msg[cell_begin:cell_end]
        print("Send cell {}".format(cell))
        sendMessageCellDiscrete(cell_msg, cell)
        #sendMessageCellContinuous(cell_msg, cell)

    #closeBoard()

def sendRawMessage(msg):
    n_cells = ceil(len(msg) / NUM_LAYERS)
    for cell in range(0, n_cells):
        cell_begin = cell * NUM_LAYERS
        cell_end = (cell + 1) * NUM_LAYERS
        cell_msg = msg[cell_begin:cell_end]
        print("Send cell {}".format(cell))
        sendMessageCellDiscrete(cell_msg, cell)

def clear():
    sendRawMessage([state.encoding[' ']] * BOARD_ROWS * BOARD_COLS)

def openBoard():
    addr="/avatar/parameters/" + generate_utils.getResize0Param()
    client.send_message(addr, False)
    addr="/avatar/parameters/" + generate_utils.getResize1Param()
    client.send_message(addr, False)

    time.sleep(0.3)

    addr="/avatar/parameters/" + generate_utils.getResizeEnableParam()
    client.send_message(addr, True)

    time.sleep(0.3)

    addr="/avatar/parameters/" + generate_utils.getResizeEnableParam()
    client.send_message(addr, False)

def closeBoard():
    addr="/avatar/parameters/" + generate_utils.getResize0Param()
    client.send_message(addr, True)
    addr="/avatar/parameters/" + generate_utils.getResize1Param()
    client.send_message(addr, True)

    time.sleep(0.1)

    addr="/avatar/parameters/" + generate_utils.getResizeEnableParam()
    client.send_message(addr, True)

    time.sleep(0.1)

    addr="/avatar/parameters/" + generate_utils.getResizeEnableParam()
    client.send_message(addr, False)

if __name__ == "__main__":
    generateEncoding(state)

    clear()
    for line in fileinput.input():
        sendMessage(line)
        time.sleep(1 + len(line) / 40.0)
    clear()
