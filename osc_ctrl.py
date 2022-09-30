#!/usr/bin/env python3

import argparse
import random
import time
import fileinput

from pythonosc import udp_client

def usage():
    print("python3 -m pip install python-osc")
    print("python3 ./osc_ctrl.py")

parser = argparse.ArgumentParser()
parser.add_argument("-i", default="127.0.0.1", help="OSC server IP")
parser.add_argument("-p", type=int, default=9000, help="OSC server port")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.i, args.p)

seed = random.randrange(3) * 26
for row in range(0, 6):
    addr="/avatar/parameters/TaSTT_Row"
    client.send_message(addr, row)
    for col in range(0, 14):
        addr="/avatar/parameters/TaSTT_Col"
        client.send_message(addr, col)

        time.sleep(.5)

        addr="/avatar/parameters/TaSTT_Active"
        client.send_message(addr, True)

        addr="/avatar/parameters/TaSTT_Letter"
        client.send_message(addr, (seed + row * 14 + col) % 65)
        print("sent {} at {},{}".format((seed + row * 14 + col) % 65, row, col))

        time.sleep(.5)

        addr="/avatar/parameters/TaSTT_Active"
        client.send_message(addr, False)

time.sleep(1000)
