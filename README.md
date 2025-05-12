# Optimized text paging for VRChat

It is sometimes useful to send text data into VRChat, for example for
speech-to-text (STT). This is typically done naively, with a "block" of
n 8-bit characters\* sent in along with an 8-bit pointer. Since avatars can only
send 256 bits at 3 Hz\*\* with OSC, this means you can only send (256 - 8) / 8 =
31 characters per sync. The average English word is 4.79 characters long, so
if we naively send in 1 character per byte, then we get a speed limit of 6.47
words per sync. The works out to ~20 words per second or ~1200 words per minute
(wpm). Adults typically read at about 238-260 wpm.

\* Typically ASCII encoding is used.

\*\* Experimentally, 3 Hz is the fastest you can reliably page data with OSC in
busy instances.

Sending in one character per byte gives you (1200/256) ~= 4.7 wpm per OSC bit
used. Thus to reach a typical reading speed, you need to use (260/4.7) = 55.5
OSC bits. The goal of this module is to get more out of these bits by
compressing text over the wire.

## Unigram tokenizer

Byte pair encoding (BPE) is an encoding scheme frequently used in natural
language processing (NLP) contexts. For any language with a fixed character set
(e.g. an alphabet), you can count up how often each character is used in a
large corpus of text. Then you can repeatedly join together characters and
assign a unique token to joined characters in the order of the most frequently
occurring sequences. You wind up with a lookup table like this:

```
0: [UNK]
1: <s>
2: </s>
3: [CLS]
4: [SEP]
...
100:  from
101:  but
102:  he
103: e
104:  now
...
10000: eo
10001:  is currently
10002:  dish
10003: Mi
10004: 6)
```

The above example is from a unigram\* sentencepiece organizer that I trained.

\* A unigram tokenizer is a variant of the byte-pair tokenizer. Where a byte
pair tokenizer views inputs as arbitrary sequences of bytes, a unigram
tokenizer views it as a sequence of letters.

The tokenizer has a vocabulary size of 65,536 tokens. It was trained on
opensubtitles and 5% of wikipedia, with `unidecode` normalization applied to
limit training data to ASCII. Subword lengths are distributed as follows:

Subword length histogram:
1: 95
2: 1032
3: 3350
4: 5439
5: 5445
6: 5082
7: 5334
8: 5866
9: 6172
10: 5934
11: 5329
12: 4698
13: 4016
14: 3191
15: 2434
16: 2095

In the test set - 25% wikipedia 75% conversational English -
this tokenizer yields 4.896 characters per token. (Recall that
the average English word is 4.8 characters long. Not bad!)

If we naively send these tokens into the game with a 16-bit number, we can send
floor((256-8)/16) = 15 tokens per sync. This gives us an average of 73.44
characters per sync - more than 2x higher than the naive approach's 31.

Here is how the unigram-tokenized scheme fairs against the naive scheme in
every possible configuration of bits used:

```
bits    naive rate  bpe rate    speedup factor
8       n/a         n/a         n/a
16      1           n/a         0.000
24      2           4.896       2.448
32      3           4.896       1.632
40      4           9.792       2.448
48      5           9.792       1.958
56      6           14.688      2.448
64      7           14.688      2.098
72      8           19.584      2.448
80      9           19.584      2.176
88      10          24.480      2.448
96      11          24.480      2.225
104     12          29.376      2.448
112     13          29.376      2.260
120     14          34.272      2.448
128     15          34.272      2.285
136     16          39.168      2.448
144     17          39.168      2.304
152     18          44.064      2.448
160     19          44.064      2.319
168     20          48.960      2.448
176     21          48.960      2.331
184     22          53.856      2.448
192     23          53.856      2.342
200     24          58.752      2.448
208     25          58.752      2.350
216     26          63.648      2.448
224     27          63.648      2.357
232     28          68.544      2.448
240     29          68.544      2.364
248     30          73.440      2.448
256     31          73.440      2.369
```

([Spreadsheet](https://docs.google.com/spreadsheets/d/1d9SEZvo3Q-6U_Wf9nuGRKXxndUhKn2V3Q0Ox0nOB4T4/edit?usp=sharing))

I reserve 39 token slots for sequences of whitespace characters of length 2-40. This helps simplify formatting. To end a line or position text, you can just send in the exact right number of spaces, and a fixed-width font renderer will position things as intended.

## Paging data into shader

Sending this data to a shader is pretty simple:

- An OSC app encodes a string into tokens and pages it into the game with OSC.
  - The app sends a pointer of *where* the tokens should be rendered along with them. Since the tokens can encode a variable length string, the pointer must be able to point to any spot in the rendering window. Thus we are limited to a 256-bit display with an 8-bit pointer, or a 64K display with a 16-bit pointer. We call this the visual pointer.
  - A second pointer tells the animator which shader parameters the tokens and visual pointer should be written to. This can be 8-bit. We call this the logical pointer.
- Animator uses the logical pointer to decide which shader parameters to send the visual pointer and tokens to.

Here is the expected speedup in every possible configuration with a 1-byte
overhead (1BO) or a 2-byte overhead (2BO):

```
bits	naive rate	bpe rate (1BO)	speedup	bpe rate (2BO)	speedup
8		n/a			n/a				n/a		n/a				n/a
16		1			0.000			0.000	0.000			0.000
24		2			0.000			0.000	0.000			0.000
32		3			4.896			1.632	0.000			0.000
40		4			4.896			1.224	4.896			1.224
48		5			9.792			1.958	4.896			0.979
56		6			9.792			1.632	9.792			1.632
64		7			14.688			2.098	9.792			1.399
72		8			14.688			1.836	14.688			1.836
80		9			19.584			2.176	14.688			1.632
88		10			19.584			1.958	19.584			1.958
96		11			24.480			2.225	19.584			1.780
104		12			24.480			2.040	24.480			2.040
112		13			29.376			2.260	24.480			1.883
120		14			29.376			2.098	29.376			2.098
128		15			34.272			2.285	29.376			1.958
136		16			34.272			2.142	34.272			2.142
144		17			39.168			2.304	34.272			2.016
152		18			39.168			2.176	39.168			2.176
160		19			44.064			2.319	39.168			2.061
168		20			44.064			2.203	44.064			2.203
176		21			48.960			2.331	44.064			2.098
184		22			48.960			2.225	48.960			2.225
192		23			53.856			2.342	48.960			2.129
200		24			53.856			2.244	53.856			2.244
208		25			58.752			2.350	53.856			2.154
216		26			58.752			2.260	58.752			2.260
224		27			63.648			2.357	58.752			2.176
232		28			63.648			2.273	63.648			2.273
240		29			68.544			2.364	63.648			2.195
248		30			68.544			2.285	68.544			2.285
256		31			73.440			2.369	68.544			2.211
```

([Spreadsheet](https://docs.google.com/spreadsheets/d/1d9SEZvo3Q-6U_Wf9nuGRKXxndUhKn2V3Q0Ox0nOB4T4/edit?usp=sharing))

As you can see, a 2-byte visual pointer is very damaging to the speedup at low bit budgets. So in bit-constrained setups we should definitely use a smaller display.

Notably, *there is only one crossover point*. If all configurations except the 2-byte overhead 48-bit configuration, BPE-based paging is always\* faster.

\* Always, going off of the *expected* rate. If you get unlucky and your tokens all decode to 1 character, then BPE-based paging is about 50% *slower* than naive encoding.

Because the Unity animator sucks shit, we're going to decode tokens on the GPU. As a refresher, the GPU sees data like this:

```
_Text_Block00_Visual_Ptr: 0
_Text_Block00_Token00: 13,766
_Text_Block00_Token01: 84
_Text_Block01_Visual_Ptr: 13
_Text_Block01_Token00: 599
_Text_Block01_Token01: 8,301
...
```

I.e. it sees "blocks" of data with tokens and visual pointers. The visual pointer just says where on a grid it should draw the subwords represented by the tokens.

The pixel shader can trivially work out what grid location the current pixel belongs to. By scanning through the visual pointers, it can work out which block it has to draw.

We can generate a function like this:

```c
#define BLOCK_WIDTH 2
void GetBlock(uint which_block, out float data[BLOCK_WIDTH]) {
  [loop]
  for (uint i = 0; i < BLOCK_WIDTH; i++) {
    data[i] = _Text_Blocks[which_block][i];
  }
}

// Get the tokens that cover `screen_ptr`. Also returns `block_ptr`, the
// location where this block of tokens begins.
void GetTokens(uint screen_ptr, out uint block_ptr, out uint tokens[BLOCK_WIDTH]) {
  uint which_block;
  [loop]
  for (uint i = 0; i < BLOCK_WIDTH; i++) {
    if (screen_ptr >= _Text_Block_Visual_Ptrs[i]) {
      which_block = i;
    }
  }
  GetBlock(which_block, tokens);
}
```

## GPU decoding

Now we have to translate the tokens into text. I do this with a texture laid out as follows:

1. A fixed-length array of (offset, length) pairs. Offset is 24 bits, giving us an address space of about 16 million slots. Length is 8 bits, but as established above, the longest token is only 16 characters long. So we're wasting about 4 bits. This tells us we should use an RGBA texture.

2. A variable length array of ASCII-encoded strings. Each slot is RGBA, so it can hold 4 characters.

My tokenizer's vocabulary is 65,536 tokens. If we add up the lengths of every token, rounding them up to the nearest multiple of 4, we get the length 667,532 This means that we need 166,883 slots to fit the actual content of the vocabulary.

So, the entire vocabulary - length+offset head and content - requires a 32-bit RGBA texture with 232,419 slots. We'll just jam this into a 512x512 texture, at an occupancy ratio of 88.66% (11.34% waste). The total VRAM usage of that lookup table (LUT) is 1 MiB.

We want to implement this API:

```c
uint GetChar(uint screen_ptr);
```

Internally, it must:

1. Get tokens. (GetTokens - already done)
2. Figure out which token covers the screen\_ptr.
3. Figure out which character in the token covers the screen\_ptr.

Let's break down [2]. We can get the length of a token with a single texture tap. So, naively, we can just scan through the tokens in the current block, add up their lengths, and stop once we find a token covering the current slot. The scan incurs a worst-case cost of `BLOCK_WIDTH` texture taps. The character lookup is then a single tap.

```c
// Gets the length of the subword encoded by the token. Performs one texture
// tap.
void TokenLengthOffset(uint token, out uint length, out uint offset);
// Gets the nth character of the token stored at `token_offset`.
uint GetTokenChar(uint token_offset, uint nth);

uint GetChar(uint screen_ptr) {
  uint block_ptr;
  uint tokens[BLOCK_WIDTH];
  GetTokens(screen_ptr, tokens, block_ptr);
  uint start = block_ptr;
  uint covering_token = 0;
  uint token_ptr = block_ptr;
  uint token_offset;
  for (uint ii = 0; ii < BLOCK_WIDTH; ii++) {
    uint token_length;
    TokenLengthOffset(tokens[ii], token_length, token_offset);
    if (token_ptr + token_length >= screen_ptr) {
      covering_token = tokens[ii];
    }
    token_ptr += token_length;
  }
  // covering_token covers screen_ptr. It starts at token_ptr.
  return GetTokenChar(token_offset, screen_ptr - token_ptr);
}
```

That's actually it for the GPU decoding. Once you have the character, you can use standard fixed-width font rendering techniques to display it (e.g. [disinfo](https://github.com/yum-food/disinfo) and [msdf](https://github.com/Chlumsky/msdfgen)).

