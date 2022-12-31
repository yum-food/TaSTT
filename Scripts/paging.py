#!/usr/bin/env python3

from math import ceil
from text_wrapping import TextWrapper

def getSlice(msg: str, idx: int, slice_len: int) -> str:
    begin = idx * slice_len
    end = (idx + 1) * slice_len
    msg_len = len(msg)
    if msg_len >= end:
        return msg[begin:end]
    if msg_len > begin:
        return msg[begin:end] + (" " * (end - msg_len))
    return None

def setSlice(msg: str, idx: int, slice_len: int, msg_slice: str,
        include_suffix: bool = True) -> str:
    begin = idx * slice_len
    end = (idx + 1) * slice_len
    prefix = msg[0:begin]
    prefix += " " * (begin - len(prefix))
    suffix = msg[end:]
    msg = prefix + msg_slice
    if include_suffix:
        msg += suffix
    return msg

class SingleLinePager:
    def __init__(self, slice_len: int):
        self.msg = ""
        self.slice_len = slice_len

    def reset(self):
        self.msg = ""

    def getNextSlice(self, msg) -> tuple[str, int]:
        for i in range(0, ceil(len(msg) / self.slice_len)):
            old_slice = getSlice(self.msg, i, self.slice_len)
            new_slice = getSlice(msg, i, self.slice_len)
            if old_slice != new_slice:
                self.msg = setSlice(self.msg, i, self.slice_len, new_slice)
                return new_slice, i
        return "", -1

class MultiLinePager:
    def __init__(self, slice_len: int, rows: int, cols: int):
        # This is a list of lists of SingleLinePagers.
        # It represents a list of pages, each containing a list of lines.
        self.pages = []
        self.slice_len = slice_len
        self.rows = rows
        self.cols = cols

    def reset(self):
        self.pages = []

    def getNextSlice(self, msg) -> tuple[str, int]:
        pages = TextWrapper(self.rows, self.cols).wrap(msg)

        # Wrapping split the input message along line boundaries and along page
        # boundaries. However, we're going to treat each page like a single
        # line, so that `slice_idx` can be used as a region index. Therefore,
        # we need exactly one SingleLinePager per page.
        for pi in range(len(self.pages), len(pages)):
            self.pages.append(SingleLinePager(self.slice_len))

        for pi in range(0, len(pages)):
            line = "".join(pages[pi])
            pager = self.pages[pi]
            msg_slice, slice_idx = pager.getNextSlice(line)
            if slice_idx != -1:
                # Reset every page after this. This guarantees that any text
                # written in this operation will eventually be redrawn.
                for pj in range(pi + 1, len(pages)):
                    self.pages[pj].reset()
                return msg_slice, slice_idx
        return "", -1

if __name__ == "__main__":
    assert(getSlice("abcdefghij", 0, 1) == "a")
    assert(getSlice("abcdefghij", 9, 1) == "j")
    assert(getSlice("abcdefghij", 0, 2) == "ab")
    assert(getSlice("abcdefghij", 1, 2) == "cd")
    assert(getSlice("abcdefghij", 3, 3) == "j  ")
    assert(getSlice("abcdefghij", 10, 1) == None)
    assert(getSlice("abcdefghij", 11, 1) == None)

    assert(setSlice("abcdefghij", 1, 2, "kl") == "abklefghij")
    assert(setSlice("abc", 1, 2, "de") == "abde")
    assert(setSlice("abc", 0, 2, "de") == "dec")

    slice_len = 2
    p = SingleLinePager(slice_len)
    p.msg = "test"
    assert(p.getNextSlice("test")[0] == "")
    assert(p.getNextSlice("tast")[0] == "ta")
    assert(p.getNextSlice("tast")[0] == "")

    p.msg = ""
    assert(p.getNextSlice("test")[0] == "te")
    assert(p.msg == "te")
    assert(p.getNextSlice("test")[0] == "st")
    assert(p.msg == "test")
    assert(p.getNextSlice("test")[0] == "")
    assert(p.msg == "test")
    assert(p.getNextSlice("tests")[0] == "s ")

    slice_len = 2
    rows = 2
    cols = 4
    p = MultiLinePager(slice_len, rows, cols)
    assert(p.getNextSlice("")[0] == "")
    assert(p.getNextSlice("yo")[0] == "yo")
    assert(p.getNextSlice("yogi")[0] == "gi")
    assert(p.getNextSlice("yugi")[0] == "yu")
    assert(p.getNextSlice("yugi is a")[0] == "is")
    assert(p.getNextSlice("yugi is a")[0] == " a")
    assert(p.getNextSlice("yugi is a pussy")[0] == "pu")
    assert(p.getNextSlice("yugi is a pussy")[0] == "s-")
    assert(p.getNextSlice("yugi is a pussy")[0] == "sy")

    p = MultiLinePager(slice_len, rows, cols)
    assert(p.getNextSlice("yo")[0] == "yo")
    assert(p.getNextSlice("yo")[0] == "  ")
    assert(p.getNextSlice("yo")[0] == "  ")
    assert(p.getNextSlice("yo")[0] == "  ")
    assert(p.getNextSlice("yo")[0] == "")

