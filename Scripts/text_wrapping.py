#!/usr/bin/env python3

class TextWrapper:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    # Split `msg` along line boundaries. Long words tend to just go onto new
    # lines. Words that are too long to fit on any line are hyphenated and
    # split.
    # Lines are padded with space (" ") characters so they're all `self.cols`
    # characters long. Pages are padded with lines full of space characters so
    # they're all `self.rows` lines long.
    def wrap(self, msg: str) -> list[list[str]]:
        pages = []
        lines = []
        line = ""
        for word in msg.split():
            if len(line) + 1 + len(word) <= self.cols:
                if len(line):
                    line += " "
                line += word
                continue
            # Word won't fit onto this line. End the line.
            if len(line):
                line += " " * (self.cols - len(line))
                lines.append(line)
                line = ""
            while len(word) > self.cols:
                prefix = word[0:self.cols-1] + "-"
                lines.append(prefix)
                suffix = word[self.cols-1:]
                word = suffix
            if len(word):
                line = word
        if len(line):
            line += " " * (self.cols - len(line))
            lines.append(line)
        while len(lines):
            pages.append(lines[0:self.rows])
            lines = lines[self.rows:]
        if len(pages):
            num_extra_lines = (self.rows - (len(pages[-1]) % self.rows)) % self.rows
            pages[-1] += [" " * self.cols] * num_extra_lines
        return pages

if __name__ == "__main__":
    w = TextWrapper(2, 5)

    assert(w.wrap("foo") == [["foo  ", "     "]])
    assert(w.wrap("foo bar") == [["foo  ", "bar  "]])
    assert(w.wrap("bagel") == [["bagel", "     "]])
    assert(w.wrap("bagels") == [["bage-", "ls   "]])
    assert(w.wrap("hot bagels") == [["hot  ", "bage-"], ["ls   ", "     "]])

