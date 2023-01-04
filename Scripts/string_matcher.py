#!/usr/bin/env python3

# python3 -m pip install editdistance
# License: MIT.
import editdistance

import typing

DEBUG = False

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
                cur_d += editdistance.eval(old_slice[j], new_slice[j])
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

def matchSpaceDelimitedStrings(old_text: str, new_text: str, window_size = 4) -> str:
    old_words = old_text.split()
    new_words = new_text.split()
    return matchStringList(old_words, new_words, window_size)

def matchStrings(old_text: str, new_text: str, window_size = 3) -> str:
    if old_text == new_text:
        if DEBUG:
            print("STRING MATCH exception path 1")
        return old_text
    elif len(old_text) >= window_size and len(new_text) >= window_size:
        # Find the window where the cumulative string distance
        # between the text in that window in the old/new transcription
        # is minimized.

        best_match_i = None
        best_match_j = None
        best_match_d = window_size * 1000

        # The number of old slices to look at. Since the old text can grow
        # unboundedly, it's crucial that we don't compare to every possible
        # slice in the old and new transcriptions (O(N^2) time complexity).
        # This is still wildly inefficient, but good enough for continuous
        # transcription in a game bound by a single CPU core, like VRChat.
        max_old_slices = 150
        old_n_slices = min(max_old_slices, len(old_text))
        last_old_window = len(old_text) - window_size
        first_old_window = max(last_old_window - old_n_slices, 0)

        for i in range(first_old_window, last_old_window + 1):
            old_slice = old_text[i:i + window_size]

            for j in range(0, 1 + len(new_text) - window_size):
                new_slice = new_text[j:j + window_size]
                cur_d = editdistance.eval(old_slice, new_slice)
                if cur_d < best_match_d:
                    best_match_i = i
                    best_match_j = j
                    best_match_d = cur_d

                    if DEBUG:
                        print("optimum at old '{}' i={} new '{}' j={} d={}".format(
                            old_slice, i, new_slice, j, cur_d))

        old_prefix = old_text[0:best_match_i]
        overlap = new_text[best_match_j:best_match_j + window_size]
        new_suffix = new_text[best_match_j + window_size:]

        if DEBUG:
            print("Best match i:    {}".format(best_match_i))
            print("Best match j:    {}".format(best_match_j))
            print("Window size:     {}".format(window_size))
            print("Old prefix:      {}".format(old_prefix))
            print("Overlap:         {}".format(overlap))
            print("New suffix:      {}".format(new_suffix))
            print("Input 1:         {}".format(old_text))
            print("Input 2:         {}".format(new_text))
            print("Output:          {}".format(old_prefix +
                new_text[best_match_j:]))
        return old_prefix + new_text[best_match_j:]
    else:
        if DEBUG:
            print("STRING MATCH exception path 2")
            print("  OLD: {}".format(old_text))
            print("  NEW: {}".format(new_text))
        return new_text

if __name__ == "__main__":
    # Identical transcriptions should not be changed.
    assert(matchSpaceDelimitedStrings("This is a test case.", "This is a test case.", window_size = 3) == "This is a test case.")
    # A suffix should be detected and ignored.
    assert(matchSpaceDelimitedStrings("This is a test case.", "is a test case.", window_size = 3) == "This is a test case.")
    # A lengthening suffix should be correctly appended.
    assert(matchSpaceDelimitedStrings("This is a test", "is a test case.", window_size = 3) == "This is a test case.")
    # A strictly longer transcription should override the old prefix.
    assert(matchSpaceDelimitedStrings("This is a test", "This is a test case.", window_size = 3) == "This is a test case.")
    # Paranoia: repetitive text broke the older implementation, so I included
    # some test cases without fully understanding what the old problem was.
    assert(matchSpaceDelimitedStrings("test test test", "test test test test test test", window_size
        = 3) == "test test test test test test")
    assert(matchSpaceDelimitedStrings("test test test test test test", "test test test", window_size
        = 3) == "test test test test test test")

    print(matchStrings("foo bar", "bar baz"))
    print(matchStrings("alpha beta", "beta gamma"))

    in1 = "Okay, what about now? Looks like it sort of works. Key word being sort of."
    in2 = "okay what about now looks like it sort of works key word being sort of looks"
    bad_out = "Okay, what about now? Looks like it sort of works. Key word being sort of works key word being sort of looks"
    good_out = "Okay what about now looks like it sort of works key word being sort of looks"
    good_out = "Okay, what about now? Looks like it sort of works. Key word being sort of looks"
    print(matchStrings(in1, in2))
    assert(matchStrings(in1, in2) == good_out)

    in1 = "This repository can take"
    in2 = "This repository contains the code for"
    bad_out  = "This repository can tode for"
    good_out = "This repository contains the code for"
    assert(matchStrings(in1, in2) == good_out)

    in1 = "See something."
    in2 = "See something. Say something."
    bad_out  = in1
    good_out = in2
    print(matchStrings(in1, in2))
    assert(matchStrings(in1, in2) == bad_out)

    in1 = "a" * 1000
    in2 = "b" * 10 * 1000
    # This should be fast (< 1 second)
    #matchStrings(in1, in2)

    print("Tests passed.")

