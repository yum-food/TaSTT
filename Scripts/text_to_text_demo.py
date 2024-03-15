#!/usr/bin/env python3
# python3 -m pip install python-osc pillow

from math import ceil
from paging import MultiLinePager
from pythonosc import udp_client

import generate_utils
import osc_ctrl
import time

class AppConfig:
    def __init__(self,
            rows: int = 4,
            cols: int = 40,
            chars_per_sync: int = 10,
            osc_sync_rate_hz: int = 3):
        self.rows = rows
        self.cols = cols
        self.chars_per_sync = chars_per_sync
        self.osc_sync_rate_hz = osc_sync_rate_hz
        self.client = osc_ctrl.getClient()

def encodeMessage(msg):
    encoded = []
    for char in msg:
        encoded.append(ord(char))
    return encoded

class OSCSyncHelper:
    def __init__(self,
            config: AppConfig):
        self.sync_delay_s = 1.0 / config.osc_sync_rate_hz
        self.last = time.time() - self.sync_delay_s

    def waitForSync(self) -> None:
        # sleep() can sleep for too short a time, so use a loop to ensure that
        # we sleep at least a full sync window's worth of time.
        while time.time() - self.last < self.sync_delay_s:
            time.sleep(0.01)
        self.last = time.time()

def sendMessage(msg: str, cfg: AppConfig, osc: OSCSyncHelper) -> None:
    num_cells = cfg.rows * cfg.cols
    num_regions = ceil(num_cells / cfg.chars_per_sync)

    pager = MultiLinePager(cfg.chars_per_sync, cfg.rows, cfg.cols)

    # Show the chatbox
    osc.waitForSync()
    osc_ctrl.toggleBoard(cfg.client, True)
    osc_ctrl.ellipsis(cfg.client, False)
    osc_ctrl.disable(cfg.client)

    # Ensure that the chatbox is cleared.
    addr="/avatar/parameters/" + generate_utils.getClearBoardParam()
    cfg.client.send_message(addr, True)
    osc.waitForSync()
    cfg.client.send_message(addr, False)

    slice_idx = 0
    while slice_idx != -1:

        msg_slice, slice_idx = pager.getNextSlice(msg)
        which_region = slice_idx % num_regions

        print(f"Sending slice '{msg_slice}' to region {which_region}")

        # Wait until OSC has had enough time to sync the previous window of
        # data.
        osc.waitForSync()

        # Enable chatbox animations.
        osc_ctrl.enable(cfg.client)

        # Seek to the current region.
        addr="/avatar/parameters/" + generate_utils.getSelectParam()
        cfg.client.send_message(addr, which_region)

        # Send all characters in the current region.
        encoded = encodeMessage(msg_slice)
        for i in range(0, len(msg_slice)):
            print(f"Sending char {msg_slice[i]} / {encoded[i]}")
            addr="/avatar/parameters/" + generate_utils.getBlendParam(i, 0)
            letter_remapped = (-127.5 + encoded[i]) / 127.5
            cfg.client.send_message(addr, letter_remapped)

    # Disable chatbox animations to ensure stability.
    osc.waitForSync()
    osc_ctrl.disable(cfg.client)

if __name__ == "__main__":
    cfg = AppConfig()
    osc = OSCSyncHelper(cfg)
    sendMessage("Hello, world! aiueo aiueo aiueo aiueo aiueo eeeeeeeeeeeeeeeeeeeeeeee", cfg, osc)

