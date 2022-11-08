#!/usr/bin/env python3

import argparse
import osc_ctrl
import time

parser = argparse.ArgumentParser()
parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
parser.add_argument("-p", type=int, default=9000, help="OSC server port")
args = parser.parse_args()

state = osc_ctrl.EvilGlobalState()
client = osc_ctrl.getClient(args.i, args.p)
tx_state = osc_ctrl.OscTxState()
state.encoding = osc_ctrl.generateEncoding()

osc_ctrl.clear(client)

i = 0x3400
line = ""
while True:
    for j in range(0, 256):
        letter = chr(i)
        line += letter
        i = i + 1

    while not osc_ctrl.sendMessageLazy(client, line, tx_state):
        continue

