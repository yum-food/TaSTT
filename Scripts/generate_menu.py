#!/usr/bin/env python3

import argparse
import sys

MENU_SUFFIX = """
  - name: TaSTT
    icon: {fileID: 0}
    type: 103
    parameter:
      name: 
    value: 1
    style: 0
    subMenu: {fileID: 11400000, guid: 111d8d5f909f534429bfe46268723200, type: 2}
    subParameters: []
    labels: []
"""[1:]

def append(old_path, new_path):
    merged = ""
    with open(old_path, "r") as f:
        merged = f.read()
    merged += MENU_SUFFIX
    with open(new_path, "w") as f:
        f.write(merged)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--old_menu", type=str, help="The menu to append to")
    parser.add_argument("--new_menu", type=str, help="The menu to create")
    args = parser.parse_args()

    if not args.old_menu or not args.new_menu:
        print("--old_menu and --new_menu are both required",
                file=sys.stderr)
        parser.print_help()
        parser.exit(1)

    append(args.old_menu, args.new_menu)

