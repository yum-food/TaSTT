#!/usr/bin/env python3

# This module is used to implement obfuscation of TaSTT network
# speech data. At a high level, TaSTT is simply streaming N bits of
# arbitrary data to a shader via VRChat's parameter sync mechanism.
#
# It would be trivial to mine this data for speech information, since
# we're sending unicode (or ASCII) characters to peers.
#
# To raise the cost for the casual data collector, we can obfuscate
# this data using a one-time pad in cipher-block chaining mode.
#
# Making things interesting, encrypted data will arrive at the Unity
# animator,  which processes them in 8 bit chunks. They are written
# into contiguous blocks of the animator. Thus the shader can decrypt
# the board by decrypting each block. This is thus stronger than
# applying a one-time pad to each byte of the plaintext, since the
# statistical distribution of individual letters is destroyed.
# Obviously due to the lack of an initialization vector, the
# distribution of phrases (blocks) is preserved.

import math
import os

def genKey(n_bits = 128) -> bytearray:
    return os.urandom(int(n_bits / 8))

def saveKey(filename: str, key: str):
    with open(filename, "wb") as f:
        f.write(key)

def loadKey(filename: str) -> bytearray:
    with open(filename, "rb") as f:
        return f.read()

# Apply a symmetric cypher to `data` using cypher-block chaining.
def obfuscate(data: bytearray, key: bytearray) -> str:
    n_blocks = int(math.ceil(len(data) / len(key)))
    # This is a misnomer. A true IV would be randomized, but we can't
    # do that since the shader doesn't have access to it. We just use
    # this to implement the "chaining" aspect of CBC.
    iv = bytearray(b'\x00') * len(key)
    result = bytearray()
    for i in range(0, n_blocks):
        block_begin = i * len(key)
        block_end = (i + 1) * len(key)
        block_plain = data[block_begin:block_end]
        block_cypher = block_plain.copy()
        for i in range(0, len(block_cypher)):
            block_cypher[i] ^= iv[i]
            block_cypher[i] ^= key[i]
        result += block_cypher
        iv = block_cypher
    return result

def deobfuscate(data: bytearray, key: bytearray) -> str:
    n_blocks = int(math.ceil(len(data) / len(key)))
    # This is a misnomer. A true IV would be randomized, but we can't
    # do that since the shader doesn't have access to it. We just use
    # this to implement the "chaining" aspect of CBC.
    iv = bytearray(b'\x00') * len(key)
    result = bytearray()
    for i in range(0, n_blocks):
        block_begin = i * len(key)
        block_end = (i + 1) * len(key)
        block_cypher = data[block_begin:block_end]
        block_plain = block_cypher.copy()
        for i in range(0, len(block_plain)):
            block_plain[i] ^= key[i]
            block_plain[i] ^= iv[i]
        result += block_plain
        iv = block_cypher
    return result

def test():
    key = genKey()
    saveKey("test.key", key)
    new_key = loadKey("test.key")
    os.remove("test.key")
    assert(key == new_key)

    plaintext_original = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    plaintext_bytes = bytearray(plaintext_original, "utf-8")
    cyphertext = obfuscate(plaintext_bytes, key)
    assert(len(plaintext_bytes) == len(cyphertext))
    plaintext_recovered = deobfuscate(cyphertext, key).decode("utf-8")
    assert(plaintext_original == plaintext_recovered)
    assert(plaintext_bytes != cyphertext)

if __name__ == "__main__":
    test()

