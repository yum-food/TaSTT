#!/usr/bin/env python3

# python3 -m pip install python-Levenshtein
from Levenshtein import distance as levenshtein_distance

import typing

# Find the window where the distance between these two transcriptions is
# minimized and use it to stitch them together.
def matchStringList(old_words: typing.List[str],
        new_words: typing.List[str], window_size = 6) -> str:
    if old_words == new_words:
        return " ".join(old_words)
    elif len(old_words) >= window_size and len(new_words) >= window_size:
        # Find the window where the cumulative string distance
        # between the words in that window in the old/new transcription
        # is minimized.
        old_slice = old_words[len(old_words) - window_size:]

        best_match_i = None
        best_match_d = window_size * 1000

        for i in range(0, 1 + len(new_words) - window_size):
            new_slice = new_words[i:i + window_size]
            cur_d = 0
            for j in range(0, window_size):
                cur_d += levenshtein_distance(old_slice[j], new_slice[j])
            if cur_d < best_match_d:
                best_match_i = i
                best_match_d = cur_d

        old_prefix = old_words[0:len(old_words) - window_size]
        overlap = new_words[best_match_i:best_match_i + window_size]
        new_suffix = new_words[best_match_i + window_size:]

        #print("Best match i:    {}".format(best_match_i))
        #print("Window size:     {}".format(window_size))
        #print("Old prefix:      {}".format(old_prefix))
        #print("Overlap:         {}".format(overlap))
        #print("New suffix:      {}".format(new_suffix))
        return " ".join(old_prefix + new_words[best_match_i:])
    else:
        return " ".join(new_words)

def matchStrings(old_text: str, new_text: str, window_size = 4) -> str:
    old_words = old_text.split()
    new_words = new_text.split()
    return matchStringList(old_words, new_words, window_size)

if __name__ == "__main__":
    # Identical transcriptions should not be changed.
    assert(matchStrings("This is a test case.", "This is a test case.", window_size = 3) == "This is a test case.")
    # A suffix should be detected and ignored.
    assert(matchStrings("This is a test case.", "is a test case.", window_size = 3) == "This is a test case.")
    # A lengthening suffix should be correctly appended.
    assert(matchStrings("This is a test", "is a test case.", window_size = 3) == "This is a test case.")
    # A strictly longer transcription should override the old prefix.
    assert(matchStrings("This is a test", "This is a test case.", window_size = 3) == "This is a test case.")
    # Paranoia: repetitive text broke the older implementation, so I included
    # some test cases without fully understanding what the old problem was.
    assert(matchStrings("test test test", "test test test test test test", window_size
        = 3) == "test test test test test test")
    assert(matchStrings("test test test test test test", "test test test", window_size
        = 3) == "test test test test test test")
    print("Tests passed.")

