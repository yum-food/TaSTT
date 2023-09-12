#!/usr/bin/env python3

from transcribe_v2 import MicStream

if __name__ == "__main__":
    # This implicitly prints mic devices.
    s = MicStream(0)

