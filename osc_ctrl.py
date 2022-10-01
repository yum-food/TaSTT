#!/usr/bin/env python3

import argparse
import random
import time
import fileinput

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

#MSG_DELAY_S=0.3
MSG_DELAY_S=0.1

def usage():
    print("python3 -m pip install python-osc")
    print("python3 ./osc_ctrl.py")

parser = argparse.ArgumentParser()
parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
parser.add_argument("-p", type=int, default=9000, help="OSC server port")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.i, args.p)

def encodeMessage(lines):
    result = []
    for line in lines:
        for char in line:
            char_int = ord(char)
            if char_int >= ord('A') and char_int <= ord('Z'):
                result.append(ord(char) - ord('A'))
            elif char >= 'a' and char <= 'z':
                result.append((ord(char) - ord('a')) + 26)
            elif char >= '0' and char <= '9':
                result.append((ord(char) - ord('0')) + 52)
            elif char == '.':
                result.append(63)
            elif char == ',':
                result.append(62)
            elif char == ' ':
                result.append(64)
        # Pad message with spaces so that it overwrites any leftover text.
        result += [65] * (BOARD_COLS - len(line))
    #print("Encoded message: {}".format(result))
    return result

# `which_cell` is an integer in the range [0,8).
def sendMessageCell(msg_cell, which_cell):

    s0 = ((floor(which_cell / 4) % 2) == 1)
    s1 = ((floor(which_cell / 2) % 2) == 1)
    s2 = ((floor(which_cell / 1) % 2) == 1)

    print("Cell s0/s1/s2: {}/{}/{}".format(s0,s1,s2))
    # Seek each layer to the current cell.
    for i in range(0, len(msg_cell)):
        print("Board index: {}".format(getBoardIndex(i, s0, s1, s2)))

        addr="/avatar/parameters/" + getLayerParam(i)
        client.send_message(addr, msg_cell[i])

        addr="/avatar/parameters/" + getSelectParam(i, 0)
        client.send_message(addr, (floor(which_cell / 4) % 2) == 1)

        addr="/avatar/parameters/" + getSelectParam(i, 1)
        client.send_message(addr, (floor(which_cell / 2) % 2) == 1)

        addr="/avatar/parameters/" + getSelectParam(i, 2)
        client.send_message(addr, (which_cell % 2) == 1)

    # Wait for convergence.
    time.sleep(MSG_DELAY_S)

    # Enable each layer.
    # TODO(yum_food) for some reason, if we don't active every layer, the
    # desired subset won't reliably fire. Why?
    for i in range(0, NUM_LAYERS):
        addr="/avatar/parameters/" + getEnableParam(i)
        client.send_message(addr, True)

    # Wait for convergence.
    time.sleep(MSG_DELAY_S)

    # Disable each layer.
    for i in range(0, NUM_LAYERS):
        addr="/avatar/parameters/" + getEnableParam(i)
        client.send_message(addr, False)

    # Wait for convergence.
    time.sleep(MSG_DELAY_S)

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

    n_cells = ceil(msg_len / NUM_LAYERS)
    print("n_cells: {}".format(n_cells))
    for cell in range(0, n_cells):
        # Really long messages just wrap back around.
        cell = cell % NUM_LAYERS

        cell_begin = cell * NUM_LAYERS
        cell_end = (cell + 1) * NUM_LAYERS
        cell_msg = msg[cell_begin:cell_end]
        print("Send cell {}".format(cell))
        sendMessageCell(cell_msg, cell)

if __name__ == "__main__":
    for line in fileinput.input():
        sendMessage(line)

    sendMessage("")

