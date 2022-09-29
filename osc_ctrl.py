#!/usr/bin/env python3

import argparse
import random
import time

from pythonosc import udp_client

def usage():
    print("python3 -m pip install python-osc")
    print("python3 ./osc_ctrl.py")

parser = argparse.ArgumentParser()
parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
parser.add_argument("-p", type=int, default=9000, help="OSC server port")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.i, args.p)

for i in range(1,100):
    addr="/avatar/parameters/_Letter_Row00_Col00_03"
    #addr="/avatar/parameters/_Letter_Row00_Col00"
    #msg = ((15 << 24) | (16 << 16) | (17 << 8) | 18)
    msg = i % 2
    print("send {} to {}".format(msg, addr))
    client.send_message(addr, msg)
    time.sleep(1)
