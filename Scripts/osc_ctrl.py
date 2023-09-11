#!/usr/bin/env python3

from emotes_v2 import EmotesState
from generate_utils import config
from math import ceil
from paging import MultiLinePager
from pythonosc import udp_client

import argparse
import generate_utils
import random
import time

# Based on a couple experiments, this seems like about as fast as we can go
# before players start losing events.
SYNC_FREQ_HZ = 5.0
SYNC_DELAY_S = 1.0 / SYNC_FREQ_HZ

def getClient(ip = "127.0.0.1", port = 9000):
    return udp_client.SimpleUDPClient(ip, port)

# The characters in the TaSTT are all numbered from top left to bottom right.
# This function provides a mapping from letter ('a') to index (26).
def generateEncoding():
    encoding = {}
    for i in range(0, 65535):
        encoding[chr(i)] = (i % 256, int(i / 256))
    return encoding

class OscState:
    def __init__(self, chars_per_sync: int, rows: int, cols: int,
            bytes_per_char: int,
            ip = "127.0.0.1", port = 9000):
        self.client = getClient(ip, port)
        self.pager = MultiLinePager(chars_per_sync, rows, cols)
        self.encoding= generateEncoding()
        self.bytes_per_char = bytes_per_char
        self.client.bytes_per_char = bytes_per_char
        self.builtin_msg = ""  # The last message sent to the built-in chatbox

    def reset(self):
        self.pager.reset()

def encodeMessage(encoding, msg):
    encoded = []
    for char in msg:
        encoded.append(encoding[char])
    return encoded

def lockWorld(client, lock: bool):
    addr = "/avatar/parameters/" + generate_utils.getLockWorldParam()
    client.send_message(addr, lock)

def toggleBoard(client, show: bool):
    addr = "/avatar/parameters/" + generate_utils.getToggleParam()
    client.send_message(addr, show)

def enable(client):
    addr="/avatar/parameters/" + generate_utils.getEnableParam()
    client.send_message(addr, True)

def disable(client):
    addr="/avatar/parameters/" + generate_utils.getEnableParam()
    client.send_message(addr, False)

def ellipsis(client, enable: bool):
    addr="/avatar/parameters/" + generate_utils.getEllipsisParam()
    client.send_message(addr, enable)

def clear(osc_state: OscState):
    disable(osc_state.client)

    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    osc_state.client.send_message(addr, True)

    time.sleep(SYNC_DELAY_S)

    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    osc_state.client.send_message(addr, False)

    osc_state.reset()

# Note: `nth_audio` is 1-indexed
def playAudio(osc_state: OscState, nth_audio: int, value: bool):
    addr="/avatar/parameters/" + generate_utils.getSoundParam(nth_audio)
    osc_state.client.send_message(addr, value)

def updateRegion(client, region_idx, letter_encoded):
    for byte in range(0, client.bytes_per_char):
        addr="/avatar/parameters/" + generate_utils.getBlendParam(region_idx, byte)
        letter_remapped = (-127.5 + letter_encoded[byte]) / 127.5
        client.send_message(addr, letter_remapped)

# Sends one slice of `msg` to the board then returns. Slices are sent
# in FIFO order; e.g., the most recently spoken words are sent last.
# Returns True if done paging, False otherwise.
def pageMessage(cfg, osc_state: OscState, msg: str, estate: EmotesState) -> bool:
    msg = estate.encode_emotes(msg)

    msg_slice, slice_idx = osc_state.pager.getNextSlice(msg)
    if slice_idx == -1:
        for i in range(5):
            playAudio(osc_state, i+1, False)
        return True

    sounds_to_make = set()
    letter_i = 1
    for letter in ["a", "e", "i", "o", "u"]:
        if letter in msg_slice.lower():
            sounds_to_make.add(letter_i)
        letter_i += 1
    if len(sounds_to_make) > 0:
        for i in range(5):
            if i+1 in sounds_to_make and random.randint(1,3) != 1:
                playAudio(osc_state, i+1, True)
            else:
                playAudio(osc_state, i+1, False)

    #print("sending page {}: {} ({})".format(slice_idx, msg_slice,
    #    len(msg_slice)))

    # Really long messages just wrap back around.

    # if in last region:
    #   how long is it
    num_cells = cfg["rows"] * cfg["cols"]
    num_regions = ceil(num_cells / cfg["chars_per_sync"])
    which_region = slice_idx % num_regions
    #print(f"which_region: {which_region}")
    #print(f"num_regions: {num_regions}")
    #print("num regions: {}".format(num_regions))
    if which_region == num_regions - 1:
        layers_in_last_region = num_cells % cfg["chars_per_sync"]
        #print(f"layers in last region: {layers_in_last_region}")
        if layers_in_last_region == 0:
            layers_in_last_region = cfg["chars_per_sync"]
        #print("layers in last region: {}".format(layers_in_last_region))
        old_len = len(msg_slice)
        msg_slice = msg_slice[0:layers_in_last_region]
        #print("truncate msg_slice from length {} to length {}".format(old_len,
        #    len(msg_slice)))

    #print("send \"{}\" to region {}".format(msg_slice, which_region))

    enable(osc_state.client)

    # Seek to the current region.
    addr="/avatar/parameters/" + generate_utils.getSelectParam()
    osc_state.client.send_message(addr, which_region)

    # Update each letter.
    encoded = encodeMessage(osc_state.encoding, msg_slice)
    #print("len encoded: {}".format(len(encoded)))
    for i in range(0, len(encoded)):
        updateRegion(osc_state.client, i, encoded[i])

    ellipsis(osc_state.client, False)

# Like `pageMessage` but uses the built-in chatbox. The built-in chatbox
# truncates data at about 150 chars, so just send the suffix of the message for
# now.
def pageMessageBuiltin(cfg, osc_state: OscState, msg: str) -> bool:
    if len(msg) == 0 or msg.isspace():
        return False  # Not paging

    msg_begin = max(len(msg) - 140, 0)
    msg_suffix = msg[msg_begin:len(msg)]

    if osc_state.builtin_msg != msg:
        addr="/chatbox/typing"
        osc_state.client.send_message(addr, False)

        addr="/chatbox/input"
        osc_state.client.send_message(addr, (msg_suffix, True))
        osc_state.builtin_msg = msg

    return False  # Not paging

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
    parser.add_argument("-p", type=int, default=9000, help="OSC server port")
    args = parser.parse_args()

