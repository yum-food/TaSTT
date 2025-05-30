#!/usr/bin/env python3

class ProfanityFilter:
    def __init__(self, en_path: str):
        self.en_path = en_path
        self.en_profanity = set()

    def load(self):
        with open(self.en_path, 'r') as f:
            for line in f:
                self.en_profanity.add(line.strip())

    def filter(self, line: str, language_code: str = "en") -> str:
        filtered = ""

        if language_code not in {"en"}:
            raise ValueError(f"Language code \"{language_code}\" is " +
                    "unsupported by the profanity filter")

        # Translation table converting vowels to asterisks.
        vowel_to_asterisk = str.maketrans('aeiouAEIOU', '**********')

        result = []
        for word in line.split():
            word_clean = word.lower()
            # Filter out non-alphabet characters from the word.
            word_clean = ''.join([char for char in word_clean if char.isalpha()])
            if word_clean in self.en_profanity:
                result.append(word.translate(vowel_to_asterisk))
            else:
                result.append(word)

        return " ".join(result)

if __name__ == "__main__":
    en_path = "/mnt/d/vrc/TaSTT/GUI/Profanity/Profanity/en"
    p = ProfanityFilter(en_path)
    p.load()
    assert(p.filter("fuck") == "f*ck")
    assert(p.filter("fuck!") == "f*ck!")
    assert(p.filter("fuck shit") == "f*ck sh*t")
    assert(p.filter("fuck shit this should not be filtered") == "f*ck sh*t this should not be filtered")
    assert(p.filter("ASS") == "*SS")
