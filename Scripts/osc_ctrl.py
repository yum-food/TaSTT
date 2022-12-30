#!/usr/bin/env python3

import argparse
from generate_utils import config
import generate_utils
from paging import MultiLinePager
from pythonosc import udp_client
from math import ceil
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
            ip = "127.0.0.1", port = 9000):
        self.client = getClient(ip, port)
        self.pager = MultiLinePager(chars_per_sync, rows, cols)
        self.encoding= generateEncoding()

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

def indicateSpeech(client, is_speaking: bool):
    addr = "/avatar/parameters/" + generate_utils.getIndicator0Param()
    client.send_message(addr, is_speaking)

def indicatePaging(client, is_paging: bool):
    addr = "/avatar/parameters/" + generate_utils.getIndicator1Param()
    client.send_message(addr, is_paging)

def enable(client):
    addr="/avatar/parameters/" + generate_utils.getEnableParam()
    client.send_message(addr, True)

def disable(client):
    addr="/avatar/parameters/" + generate_utils.getEnableParam()
    client.send_message(addr, False)

def clear(osc_state: OscState):
    disable(osc_state.client)

    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    osc_state.client.send_message(addr, True)

    time.sleep(SYNC_DELAY_S)

    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    osc_state.client.send_message(addr, False)

    osc_state.reset()

def updateRegion(client, region_idx, letter_encoded):
    for byte in range(0, generate_utils.config.BYTES_PER_CHAR):
        addr="/avatar/parameters/" + generate_utils.getBlendParam(region_idx, byte)
        letter_remapped = (-127.5 + letter_encoded[byte]) / 127.5
        client.send_message(addr, letter_remapped)

# Sends one slice of `msg` to the board then returns. Slices are sent
# in FIFO order; e.g., the most recently spoken words are sent last.
# Returns True if done paging, False otherwise.
def pageMessage(osc_state: OscState, msg: str) -> bool:
    msg_slice, slice_idx = osc_state.pager.getNextSlice(msg)
    if slice_idx == -1:
        return True
    #print("sending page {}: {} ({})".format(slice_idx, msg_slice,
    #    len(msg_slice)))

    empty_slice = " " * len(msg_slice)
    if msg_slice != empty_slice:
        addr="/avatar/parameters/" + generate_utils.getSpeechNoiseToggleParam()
        osc_state.client.send_message(addr, True)

    # Really long messages just wrap back around.
    which_region = (slice_idx % generate_utils.config.numRegions(0))
    #print("send to region {}".format(which_region))

    # if in last region:
    #   how long is it
    num_cells = generate_utils.config.BOARD_ROWS * generate_utils.config.BOARD_COLS
    num_regions = ceil(num_cells / generate_utils.config.CHARS_PER_SYNC)
    #print("num regions: {}".format(num_regions))
    if which_region == num_regions - 1:
        layers_in_last_region = num_cells % generate_utils.config.CHARS_PER_SYNC
        #print("layers in last region: {}".format(layers_in_last_region))
        old_len = len(msg_slice)
        msg_slice = msg_slice[0:layers_in_last_region]
        #print("truncate msg_slice from length {} to length {}".format(old_len,
        #    len(msg_slice)))

    enable(osc_state.client)

    # Seek to the current region.
    addr="/avatar/parameters/" + generate_utils.getSelectParam()
    osc_state.client.send_message(addr, which_region)

    # Update each letter.
    encoded = encodeMessage(osc_state.encoding, msg_slice)
    #print("len encoded: {}".format(len(encoded)))
    for i in range(0, len(encoded)):
        updateRegion(osc_state.client, i, encoded[i])

    # Wait for parameter sync.
    time.sleep(SYNC_DELAY_S)

    if msg_slice != empty_slice:
        addr="/avatar/parameters/" + generate_utils.getSpeechNoiseToggleParam()
        osc_state.client.send_message(addr, False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
    parser.add_argument("-p", type=int, default=9000, help="OSC server port")
    args = parser.parse_args()

