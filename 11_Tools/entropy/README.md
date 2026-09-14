# Ghidra's entropy bar: the encoding shows in the histogram

**Level:** 201 · for anyone who has opened a binary in Ghidra and wondered what the coloured strip down the right edge of the Listing is saying

**One line:** Every encoding wastes bits in its own way — ASCII never sets the top bit, UTF-16 puts a `00` after every Latin letter, machine code repeats its opcodes, compressed data wastes nothing at all — and a histogram of the byte values in a 1 KB chunk measures that waste as one number from 0.0 to 8.0 without decoding a byte. Ghidra's Entropy overview bar paints that number down the side of the program, with four named bands for the encodings it expects, so a binary's string table, its code and its packed payload show up before any header has been read. What the number cannot see is just as useful to know: the order of the bytes, how often a chunk repeats, and whether the text is ASCII or EBCDIC.

Ghidra's Listing window can show one or more **overview bars** along its right edge. Each bar squashes the program's whole address space into the height of the window — one row of pixels stands for a slice of addresses — and colours each row by some property of what is there. Hover for a tooltip naming the property and the address, left-click to jump the Listing there, right-click for a menu that includes **Show Legend**; a button on the Listing's toolbar turns the bars on and off. Two bars ship. The **Address Type** bar colours by what Ghidra's analysis has *defined* at an address — function, external reference, instruction, defined data, undefined bytes, uninitialised memory, in that order of precedence — so it is only as good as the analysis so far. The **Entropy** bar colours by a statistic of the *raw bytes* and nothing else, which is why it works on a packed executable, a firmware dump, or a file with no format header, and why it belongs in this library: the statistic is a property of the encoding.

This page takes Ghidra's own help page for the bar — *Overview*, under `OverviewPlugin` in Ghidra's help, [`Overview.htm` at the 12.1.3 tag ↗](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/help/help/topics/OverviewPlugin/Overview.htm) — and runs each claim it makes once, on bytes chosen in a program. The seven named ranges, the chunk sizes, the palette arithmetic and the log table are read off the plugin's source at the same tag, in [`ghidra/app/plugin/core/overview/entropy` ↗](https://github.com/NationalSecurityAgency/ghidra/tree/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/java/ghidra/app/plugin/core/overview/entropy), which is the build installed on this Mac. **Nothing here was run through Ghidra.** The three programs do the same arithmetic on chunks built in memory, so their keys are the same on every machine, and the [real files at the end](#measured-on-this-mac) are in a dated fence.

## The score

Cut the bytes into chunks — 1024 by default — and for each chunk count how often each of the 256 byte values occurs. Divide each count by the chunk length to get a probability `p(x)` for each value `x`, and sum:

```text
H = - sum over x of  p(x) * log2 p(x)        x = 0 .. 255, only the values present
```

That is Shannon's entropy of the histogram, in bits. The help page shows it as an image; there is nothing in it but the counts. Two ends and a reading:

- **0.0** — the chunk is one byte value repeated. `p = 1`, `log2 1 = 0`, nothing to add.
- **8.0** — all 256 values appear equally often. `p = 1/256` for each, and `256 * (1/256) * 8 = 8`.
- **`2^H`** is how many *equally likely* values would spread as widely as this chunk does. 1.5 bits is not one and a half of anything; it is a chunk spread like 2.83 equally likely values.

Because the sum runs over a histogram, three things about the chunk never reach it: the *order* of its bytes, how many times a pattern *repeats* inside it, and which value sits in which bucket — a one-to-one substitution of byte values moves the bars of the histogram without changing their heights. Section 3 of the Python example makes all three concrete, and the last is the one to remember: ROT13 and ASCII-to-EBCDIC both leave the score exactly where it was.

The chapter's [three questions](../README.md#the-three-questions), for this tool:

| | The question | Ghidra's entropy bar |
|---|---|---|
| 1 | Bytes or characters? | **Bytes**, always — 256 buckets, and nothing is ever decoded |
| 2 | Who decided? | Two options in the Tool Options dialog: the **chunk size** (256, 512 or 1024 bytes) and which of seven **named ranges** fill the five slots. The ranges' centres and widths are constants in the source; the defaults light *Compressed*, *x86 code*, *ASCII strings* and *Unicode UTF16* |
| 3 | What happens to text that is not valid? | **Nothing is invalid** — every byte has a bucket and every chunk has a score. The one thing it cannot score is a block with no bytes: `computeEntropy` catches the memory error and returns 0, so an uninitialised block and a kilobyte of `00` paint the same colour |

## In Python

<!-- output:entropy_bar_py -->
*Verified output of [`entropy_bar_py.py`](examples/entropy_bar_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SCORE, ON CHUNKS BUILT BY HAND
------------------------------------------------------------------------
   chunk                                values   score   2^score
   1024 bytes of 00                          1    0.00      1.00
   512 x 'a', then 512 x 'b'                 2    1.00      2.00
   'abcd' x 256                              4    2.00      4.00
   512 x 'a', 256 x 'b', 256 x 'c'           3    1.50      2.83
   every byte value, four times over       256    8.00    256.00

   The fourth row, written out: p(a) = 1/2, p(b) = p(c) = 1/4, so
   H = -(1/2)log2(1/2) - 2 x (1/4)log2(1/4) = 0.5 + 1.0 = 1.5 bits.
   Read 2^H as how many EQUALLY likely values would spread this much:
   one value is 0 bits, two are 1 bit, all 256 are 8 bits, and the
   1.5-bit chunk is spread like 2.83 equally likely values.

2. ONE PARAGRAPH OF ENGLISH, SIX ENCODINGS, THE FIRST 1024 BYTES OF EACH
------------------------------------------------------------------------
   encoding  values   score   log2(values)   Ghidra's name for it
   utf-8         41    4.21           5.36   ascii
   cp037         41    4.21           5.36   ascii
   utf-16le      34    3.06           5.09   utf16
   utf-16be      34    3.06           5.09   utf16
   utf-32le      29    1.83           4.86   -
   utf-32be      29    1.83           4.86   -

   Where the encoding itself caps the score. A fraction f of every
   chunk is one fixed byte, and the rest is spread over at most k values:
   ASCII: bit 7 is never set, so 128 values at most     cap 7.00
   UTF-16 of ASCII: every other byte is 00              cap 4.50
   UTF-32 of ASCII: three bytes in four are 00          cap 2.56
   any byte at all                                      cap 8.00

   English is well under its cap in every encoding -- letters are not
   equally likely -- but the caps are why the encodings sort into
   Ghidra's bands: the same paragraph is 'ascii' in UTF-8 and in
   EBCDIC, 'utf16' in either byte order, and below every named range
   in UTF-32.

3. ORDER, REPETITION AND A SUBSTITUTION ARE INVISIBLE TO IT
------------------------------------------------------------------------
   as written                          1024 bytes    4.21
   the same bytes, sorted              1024 bytes    4.21
   the same bytes, reversed            1024 bytes    4.21
   the same 1024 bytes twice over      2048 bytes    4.21
   ROT13                               1024 bytes    4.21
   EBCDIC (cp037)                      1024 bytes    4.21

   Six inputs, one score. The histogram is the whole input: the order
   of the bytes never enters the sum, a chunk repeated has the same
   proportions, and a one-to-one substitution of values -- ROT13, or
   ASCII to EBCDIC -- moves the bars of the histogram without changing
   their heights. So 'ascii' is Ghidra's name for a text-shaped
   histogram, and an EBCDIC string table earns it too.

4. WHAT SCORES 8.0, AND WHETHER IT WOULD COMPRESS
------------------------------------------------------------------------
   chunk                                    score   name         zlib -9 shrinks it below a third
   00 01 02 .. ff, four times over           8.00   compressed   True
   1024 bytes of chained SHA-256             7.84   compressed   False

   The counter scores a perfect 8.0 and compresses to a fraction; the
   hash chain scores less -- 1024 draws over 256 values leave the
   histogram bumpy -- and does not compress at all. Entropy measures
   how evenly the values are spread, not whether the bytes carry
   information, so 'compressed' is Ghidra's name for a flat histogram:
   compressed data has one, encrypted data has one, and so does a
   table that walks through every value.

5. WHERE EACH CHUNK LANDS, IN THE DEFAULT PALETTE
------------------------------------------------------------------------
   Ghidra's four default ranges, in slot order, as integer bands of
   the 256-entry palette (the Rust example derives them):
   Compressed     compressed  index 239 to 256   score 7.47 to 8.03
   x86 code       x86         index 178 to 203   score 5.56 to 6.38
   ASCII strings  ascii       index 134 to 167   score 4.19 to 5.25
   Unicode UTF16  utf16       index  96 to 109   score 3.00 to 3.44

   chunk                        score   index   tooltip prints   name
   English, UTF-8                4.21     134           4.2039   ascii
   English, UTF-16LE             3.06      97           3.0431   utf16
   English, UTF-32LE             1.83      58           1.8196   -
   'abcd' x 256                  2.00      64           2.0078   -
   chained SHA-256               7.84     251           7.8745   compressed
   00 01 02 .. ff, x 4           8.00     255           8.0000   compressed

   The tooltip does not print the score. Ghidra keeps floor(score x 32)
   as a palette index and prints index x 8 / 255 -- 256 steps in, 255
   steps out -- so every number it shows is a little high, by up to
   1/32 plus 0.4%. Its format is #0.0, which hides all of that.

6. THE LAST CHUNK OF A MEMORY BLOCK IS SCORED AGAINST A FULL ONE
------------------------------------------------------------------------
   chunk read from the block               true   ghidra index   tooltip   name
   every value x 4 (1024 bytes)            8.00            255      8.00   compressed
   every value x 2 (512 bytes)             8.00            144      4.52   ascii
   every value x 1 (256 bytes)             8.00             80      2.51   -
   English, UTF-8 (1024 bytes)             4.21            134      4.20   ascii
   English, UTF-8 (512 bytes)              4.12             81      2.54   -

   Chunks are cut from the start of each memory block, so a block whose
   length is not a multiple of the chunk size ends in a short one, and
   the short one is scored with its counts divided by 1024 rather than
   by the bytes it has. A 512-byte tail of perfectly flat data scores
   4.5 instead of 8.0 -- and 4.5 is inside the 'ascii' band, which is
   what the tooltip would then call it. Read off the 12.1.3 source, not
   run through Ghidra; the page links the three methods involved.

7. CHUNK SIZE: THE OPTION TRADES DETAIL FOR STEADINESS
------------------------------------------------------------------------
   the paragraph is 2031 bytes; full chunks only
   chunk size   chunks   lowest   highest   spread   all in the 'ascii' band
         1024        1     4.21      4.21     0.00   True
          512        3     4.12      4.28     0.16   False
          256        7     4.07      4.24     0.17   False

   Smaller chunks draw finer detail down the bar and score less
   steadily, because a histogram of 256 buckets filled from 256 bytes
   is mostly empty buckets. The same paragraph, cut finer, spreads
   over a wider range of scores.
```
<!-- /output -->

**Section 1 is the formula on chunks whose histogram you can see.** One value is 0.00, two equally often is 1.00, four is 2.00, all 256 is 8.00, and the row with a half and two quarters is the whole calculation written out.

**Section 2 is the reason the bar can name an encoding.** One paragraph of English, cut to its first 1024 bytes in six spellings. In UTF-8 it scores 4.21 and lands in Ghidra's *ascii* band; in EBCDIC it scores 4.21 and lands in the same band, because `cp037` maps ASCII's letters one-to-one onto other bytes. In UTF-16, either byte order, it scores 3.06 — every other byte is `00`, so half the histogram's mass sits on one value and the *cap* for such a chunk is 4.5 bits. In UTF-32, three bytes in four are `00`, the cap is 2.56, and English scores 1.83, below every band Ghidra has. English never reaches its cap in any of them — letters are not equally likely, and `e` and space dominate — but the caps are what sort the encodings into bands: an encoding's waste is a ceiling on its score.

**Section 3 is what the score cannot see.** The same 1024 bytes sorted, reversed, doubled, rotated by thirteen and re-spelled in EBCDIC: six inputs, one score, 4.21. So *ascii* is Ghidra's name for a text-shaped histogram, not for ASCII, and an EBCDIC string table in a mainframe binary earns the label too. [Rotation is not encryption](../../02_Characters/rotation_is_not_encryption/README.md) is the same fact from the other side — a substitution cipher hides the letters and not the letter frequencies, which is how it is broken.

**Section 4 is what *compressed* means to the bar.** A counter — `00 01 02 .. ff`, four times over — scores a perfect 8.0 and compresses to a fraction of its size; a kilobyte of chained SHA-256 scores 7.84, because 1024 draws over 256 values leave the histogram bumpy, and does not compress at all. Both are named *compressed*. Entropy measures how evenly the values are spread, not whether the bytes carry any information, so the band's real name is *flat histogram*: compressed data has one, encrypted data has one, and so does a lookup table that walks through every value once.

**Section 5 is the tooltip's number, which is not the score.** Ghidra keeps `floor(score * 32)` as an index into a 256-entry palette and prints `index * 8 / 255` back — 256 steps in, 255 steps out — so every number it shows is a little high, by up to `1/32` plus 0.4 %; the format is `#0.0`, one decimal, which rounds most of that away. The table also puts each chunk of this program into a band: English is *ascii* in UTF-8 and *utf16* in UTF-16, and the `'abcd'` chunk and the UTF-32 chunk are named nothing at all.

**Section 6 is the finding.** Chunks are cut from the start of each memory block, so a block whose length is not a multiple of the chunk size ends in a short one — and `buildLogTable` divides every count by the *chunk size*, not by the number of bytes read, so the short chunk is scored as if its missing bytes contributed nothing. A 512-byte tail of perfectly flat data scores 4.5 instead of 8.0, and 4.5 is inside the *ascii* band, which is what the tooltip would call it. Read off the source — [`computeEntropy`, `computeHistogram` and `quantizeChunk` in `EntropyOverviewColorService.java` ↗](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/java/ghidra/app/plugin/core/overview/entropy/EntropyOverviewColorService.java) — and not run through Ghidra, so a block that happens to be a multiple of 1024 bytes long will never show it. The general form: a tail of `n` bytes with true entropy `H` scores `(n / N) * (H + log2(N / n))` against a chunk size of `N`.

**Section 7 is the one option that is a trade.** The paragraph in 1024-byte chunks is one score; in 512-byte chunks it spans 0.16; in 256-byte chunks, 0.17, and two of the seven land outside the *ascii* band. Smaller chunks draw finer detail down the bar and score less steadily, because 256 buckets filled from 256 bytes are mostly empty buckets — which is what the help page means by *trade off the granularity of the Entropy window with how much variation to expect*.

## In the terminal

<!-- output:entropy_bar_sh -->
*Verified output of [`entropy_bar_sh.sh`](examples/entropy_bar_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE HISTOGRAM IS THE WHOLE INPUT

$ printf 'Hello, World!' | hist
1 32
1 33
1 44
1 72
1 87
1 100
1 101
3 108
2 111
1 114
   Thirteen bytes, ten values: l three times, o twice, eight once each.
   Nothing about their order survives into this table, and the score is
   computed from the table alone:

$ printf 'Hello, World!' | score
3.18

2. THE SAME TEXT IN UTF-16LE

$ printf 'Hello, World!' | iconv -f UTF-8 -t UTF-16LE | hist | head -1
13 0

$ printf 'Hello, World!' | iconv -f UTF-8 -t UTF-16LE | score
2.59
   Twenty-six bytes now, and the first row of the histogram is the whole
   story: half of them are 00. Half the mass on one value pulls the
   score down, which is why UTF-16 text has a band of its own in
   Ghidra's palette, below ASCII's.

3. THE ENDS OF THE SCALE

$ head -c 1024 /dev/zero | score
0.00

$ for i in $(seq 0 255); do printf "\\$(printf '%03o' "$i")"; done | score
8.00
   One value is 0.00. Every value, equally often, is 8.00 -- and this
   input is a counter, not noise. The scale measures spread, not
   randomness.

4. ORDER DOES NOT MATTER; THE ENCODING DOES

$ printf 'abcabcabc' | score
1.58

$ printf 'aaabbbccc' | score
1.58

$ printf 'cbacbacba' | score
1.58

$ printf 'Hello, World!' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | score
3.18
   Three arrangements of the same nine bytes, and ROT13 of section 1's
   string, all keep their score: a rearrangement or a one-to-one
   substitution leaves the histogram's heights alone. What changes the
   score is a different set of bytes for the same text:

$ printf 'caf\303\251' | score
2.32

$ printf 'caf\351' | score
2.00
   café is five distinct bytes in UTF-8 and four in Latin-1, so the
   UTF-8 spelling scores log2(5) and the Latin-1 spelling log2(4). Short
   strings sit low on the scale whatever they hold; the named bands on
   the page are for chunks of a thousand bytes.
```
<!-- /output -->

**The histogram is `od | sort | uniq -c`**, and the score is one `awk` loop over it — summed in value order, so the last digit does not depend on which of [the three `awk`s](../awk/README.md) is running. Section 1 is the whole tool on thirteen bytes: the table has ten rows, the order of the bytes is gone from it, and 3.18 comes from the table alone. Section 2 pipes the same string through `iconv -t UTF-16LE` (the byte order named, [as it has to be](../../03_Encodings/byte_order_and_bom/README.md)), and the first row of the histogram says why UTF-16 has a band of its own: `13 0`, half the bytes. Section 3 is the two ends of the scale, and the top end is a counter: `printf` of every byte value once, which is not noise and scores 8.00. Section 4 is the invisibility again — three arrangements and a ROT13 keep 1.58 and 3.18 — followed by the one thing that does move the score, a different set of bytes for the same word: `café` is five distinct bytes in UTF-8 and four in Latin-1, `log2(5)` against `log2(4)`.

Everything in that block scores well below Ghidra's bands, because a thirteen-byte string is not a thousand-byte chunk: the score of a short string is capped by how few values it has room for. The bands are calibrated for chunks, which is the subject of [the kata](#practice).

## In Rust

<!-- output:entropy_bar_rs -->
*Verified output of [`entropy_bar_rs.rs`](examples/entropy_bar_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A HISTOGRAM IS 256 COUNTS, INDEXED BY THE BYTE
------------------------------------------------------------------------
   string           encoding  bytes values   score   log2(values)
   Hello, World!    UTF-8        13     10    3.18           3.32
   Hello, World!    UTF-16LE     26     11    2.59           3.46
   café             UTF-8         5      5    2.32           2.32
   café             UTF-16LE      8      5    2.00           2.32
   żółw             UTF-8         7      6    2.52           2.58
   żółw             UTF-16LE      8      6    2.50           2.58
   日本語              UTF-8         9      8    2.95           3.00
   日本語              UTF-16LE      6      6    2.58           2.58
   😀                UTF-8         4      4    2.00           2.00
   😀                UTF-16LE      4      4    2.00           2.00

   [0u32; 256] indexed by b as usize: the type is the whole guarantee that
   every byte has a bucket. Ghidra is Java, whose byte is signed, so its
   histogram is indexed 128 + b -- the same 256 buckets, shifted, and the
   sum does not care which bucket is which. When every byte is distinct
   the score IS log2 of the count, which is why café is 2.32 in UTF-8
   and 2.00 in Latin-1: the ceiling is the number of values in use.

2. ONE NUMBER FROM 0.0 TO 8.0 BECOMES ONE OF 256 COLOURS
------------------------------------------------------------------------
   score   floor(score x 32)   tooltip prints   difference
    0.00                   0           0.0000   +0.0000
    1.00                  32           1.0039   +0.0039
    3.21                 102           3.2000   -0.0100
    4.70                 150           4.7059   +0.0059
    5.94                 190           5.9608   +0.0208
    7.99                 255           8.0000   +0.0100
    8.00                 255           8.0000   +0.0000

   The palette has 256 entries, so a score is floored to a step of 1/32
   before it is a colour, and a chunk of exactly 8.0 has to be capped
   at entry 255. The tooltip turns the entry back into a number by
   dividing by 255 -- 256 steps in, 255 steps out -- so every score
   above zero comes back a little high. #0.0 rounds most of that away.

3. THE SEVEN NAMED RANGES ARE INTEGER BANDS
------------------------------------------------------------------------
   option         tooltip     centre   +/-   as written       indexes   as applied
   x86 code       x86         5.9400  0.40   5.54 to 6.34   178 to 203   5.56 to 6.38
   ARM code       arm         5.1252  0.51   4.62 to 5.64   148 to 181   4.62 to 5.69
   THUMB code     thumb       6.2953  0.50   5.80 to 6.80   185 to 218   5.78 to 6.84
   PowerPC code   powerpc     5.6674  0.52   5.15 to 6.19   165 to 198   5.16 to 6.22
   ASCII strings  ascii       4.7000  0.50   4.20 to 5.20   134 to 167   4.19 to 5.25
   Compressed     compressed  8.0000  0.50   7.50 to 8.50   239 to 256   7.47 to 8.03
   Unicode UTF16  utf16       3.2100  0.20   3.01 to 3.41    96 to 109   3.00 to 3.44

   Every band is a little wider than its centre plus or minus its
   half-width says, because both are floored to 1/32 before the end is
   mirrored from the start. Compressed's centre of 8.0 is the one that
   hits the cap: entry 256 does not exist, so it is pinned to 255 and the
   band is 17 entries below it and none above.

   Ranges that overlap, so a score inside both is named by the lower slot:
   x86      and arm        share entries 178 to 181   (5.56 to 5.69)
   x86      and thumb      share entries 185 to 203   (5.78 to 6.38)
   x86      and powerpc    share entries 178 to 198   (5.56 to 6.22)
   arm      and powerpc    share entries 165 to 181   (5.16 to 5.69)
   arm      and ascii      share entries 148 to 167   (4.62 to 5.25)
   thumb    and powerpc    share entries 185 to 198   (5.78 to 6.22)
   powerpc  and ascii      share entries 165 to 167   (5.16 to 5.25)

   The four machine-code ranges are one region of the scale, 4.6 to 6.8,
   sliced four ways; x86 lies wholly inside PowerPC's and THUMB's
   overlap. Which name the tooltip prints for a score in two of them
   is decided by which Entropy Range slot holds each, not by the score.
```
<!-- /output -->

**Section 1 is the histogram as a type.** `[u32; 256]` indexed by `b as usize` is the entire guarantee that every byte has a bucket: a `u8` cannot be out of range, so there is nothing to check and no offset to add. Ghidra is Java, whose `byte` runs from −128 to 127, so its `computeHistogram` writes `histogram[128 + chunkBuffer[i]]` — the same 256 buckets, shifted by half — and the sum does not care which bucket holds which value. The table is [the cast](../../CAST.md) in UTF-8 and UTF-16LE, and its last two columns say the same thing every time: when every byte in a short string is distinct, the score *is* `log2` of the count, so the ceiling on a score is the number of values in use.

**Section 2 is the palette.** A score is floored to a step of `1/32` before it is a colour, a chunk of exactly 8.0 is capped at entry 255, and the tooltip divides by 255 on the way back out — so 1.0 prints as 1.0039 and 5.94 as 5.9608, before `#0.0` rounds them. The difference column is the whole discrepancy: never below zero, never above `1/32 + 0.4 %`.

**Section 3 is the seven ranges as Ghidra applies them.** The source stores each as a centre and a half-width — `("ascii", 4.7, 0.5)` — and the help page says *4.2 to 5.2*; the palette turns both numbers into integers first, and the band that results is entries 134 to 167, which is 4.19 to 5.25. Every band is a little wider than written. *Compressed* is the odd one: its centre of 8.0 is entry 256, which does not exist, so it is pinned to 255 and the band runs seventeen entries below and none above. And the four machine-code ranges are one region of the scale, 4.6 to 6.8, sliced four ways — x86's band lies wholly inside the overlap of PowerPC's and THUMB's — so when two of them are lit at once, which name the tooltip prints for a score inside both is decided by which *Entropy Range* slot holds each, and not by the score. The x86 defaults were measured, by Ghidra's authors, on x86; a 64-bit ARM program has no range of its own, and [lands in x86's](#measured-on-this-mac).

## The legend and the options, line by line

The legend — right-click the bar, **Show Legend** — is the palette drawn vertically, with 0.0 at the top and 8.0 at the bottom, and a label beside each lit range. The palette itself is read off [`OverviewPalette.java` ↗](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/java/ghidra/app/plugin/core/overview/entropy/OverviewPalette.java): a straight gradient from the theme's *low* colour to its *high* colour, black to white in the default theme, and then each lit range painted over it as a raised cosine — the range's colour exactly at its centre entry, fading back into the gradient at both ends — so a range is a bump of colour on a grey ramp, which is what the help page calls *a steep gradient*. The labels are the ranges' short names, `utf16`, `ascii`, `x86`, `compressed`, and they are the same strings the tooltip prints after the score. One line of that file is worth knowing about: `setBase` mixes the blue channel of the gradient from the high colour's *green*, a slip that is invisible while the high colour is white, whose green and blue are equal, and would show the moment somebody set it to anything else.

The options — **Edit › Tool Options…**, then **Entropy** in the tree — are the six lines below, with the defaults read off [`EntropyOverviewOptionsManager.java` ↗](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/java/ghidra/app/plugin/core/overview/entropy/EntropyOverviewOptionsManager.java) and the theme:

| Option | Default | What it decides | Read more |
|---|---|---|---|
| **Chunk size** | 1024 Bytes | how many bytes share one score: 256, 512 or 1024. Smaller is finer down the bar and noisier per chunk | [section 7](#in-python) |
| **Entropy Range 1** | Compressed | the first of five slots, each holding one of the seven named ranges or *None*. The slot's number is its **priority** in the tooltip when bands overlap | [section 3, Rust](#in-rust) |
| **Entropy Range 2** | x86 code | 5.56 to 6.38 as applied. ARM, THUMB and PowerPC are the alternatives; there is no ARM64 range | the same |
| **Entropy Range 3** | ASCII strings | 4.19 to 5.25 as applied — the band English prose lands in, whatever the 8-bit table | [section 2](#in-python) |
| **Entropy Range 4** | Unicode UTF16 | 3.00 to 3.44 — a `00` after every Latin letter | [section 2](#in-python) |
| **Entropy Range 5** | None | an empty slot; the fifth colour, blue, is defined for it in the theme | |
| **Range *n* color** | red, blue, green, yellow, blue | the colour at the centre of range *n*; click the swatch for a chooser | the legend, above |

The seven ranges, in the enum's order, as the source writes them and as the palette applies them — the second pair of columns is what a score is actually tested against:

| Option label | Tooltip name | Centre ± half-width | Written as | Applied as |
|---|---|---|---|---|
| x86 code | `x86` | 5.94 ± 0.4 | 5.54 to 6.34 | 5.56 to 6.38 |
| ARM code | `arm` | 5.1252 ± 0.51 | 4.62 to 5.64 | 4.62 to 5.69 |
| THUMB code | `thumb` | 6.2953 ± 0.5 | 5.80 to 6.80 | 5.78 to 6.84 |
| PowerPC code | `powerpc` | 5.6674 ± 0.52 | 5.15 to 6.19 | 5.16 to 6.22 |
| ASCII strings | `ascii` | 4.7 ± 0.5 | 4.20 to 5.20 | 4.19 to 5.25 |
| Compressed | `compressed` | 8.0 ± 0.5 | 7.50 to 8.50 | 7.47 to 8.00 |
| Unicode UTF16 | `utf16` | 3.21 ± 0.2 | 3.01 to 3.41 | 3.00 to 3.44 |

*Centre and half-width are [`EntropyKnot.java` at the 12.1.3 tag ↗](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/java/ghidra/app/plugin/core/overview/entropy/EntropyKnot.java); the applied bands are section 3 of the Rust example, and the top of each is exclusive. The help page's *4.2 - 5.2* for ASCII is the written pair, rounded.*

## Measured on this Mac

The programs above score chunks they built. These are files this machine has, scored by the same arithmetic — 1024-byte chunks, full chunks only, the four default ranges as the names — and none of it is an answer key, because every file belongs to this Mac.

```text title="Measured 2026-09-13 — macOS 26.6.2, python3 3.14.7 running the Python example's entropy() over 1024-byte chunks; Apple gzip 479, bzip2 1.0.8, and lipo and otool from the Command Line Tools to cut the (__TEXT,__text) section out of each slice of the universal /bin/ls. The UTF-16LE and UTF-32LE rows are the word list re-encoded in Python. Ghidra itself was not run."
file                                              bytes chunks    min   med   max   chunks per default range
/usr/share/dict/words                         2,493,885   2435   3.49  3.90  4.30   ascii   1%  -  99%
the same, as UTF-16LE                         4,987,770   4870   2.70  2.92  3.15   utf16   6%  -  94%
the same, as UTF-32LE                         9,975,540   9741   1.57  1.75  1.87   - 100%
the same, gzip -9                               754,289    736   7.73  7.80  7.85   compressed 100%
the same, bzip2 -9                              857,578    837   7.31  7.78  7.84   compressed  99%  -   1%
man bash | col -b (prose, ASCII)                251,531    245   3.83  4.25  4.71   ascii  75%  -  25%
strings - /bin/ls (the binary's own text)        21,412     20   4.20  5.38  6.48   x86  25%  ascii  50%  -  25%
/bin/ls, x86_64 slice, (__TEXT,__text)           15,095     14   5.01  5.74  6.07   x86  86%  ascii   7%  -   7%
/bin/ls, arm64e slice, (__TEXT,__text)           15,268     14   5.12  5.92  6.16   x86  86%  ascii  14%
/bin/ls, whole universal file                   154,208    150   0.00  0.00  7.32   x86  16%  ascii   6%  utf16   1%  -  77%
Ghidra's Base.jar (a zip of class files)     23,104,674  22563   4.98  7.78  7.87   compressed  97%  x86   0%  ascii   2%  -   1%
```

Five things to read off it. **The compressed rows are the clean ones**: gzip and bzip2 of the same text are 7.7 to 7.85 in every chunk, and Ghidra's jar, a zip of deflated class files, is 97 % *compressed* — a bar over any of those would be one colour, top to bottom. **The x86 code is where the source said it would be**, 86 % of the `__text` chunks inside the band, with the chunks at the section's ends — the ones sharing their kilobyte with padding or data — falling out of it. **The ARM64 slice lands in the same band**, 86 % *x86*, because Ghidra has no ARM64 range and 64-bit ARM packs its bytes about as evenly as x86 does; the 32-bit `arm` and `thumb` presets are for a different instruction set. **Real text is not always *ascii*.** The bash manual, prose with capitals and punctuation, is 75 % in the band; the system word list — one lowercase word per line, so `a` to `z` and newline and little else — is 99 % *below* it, at 3.9, and only its UTF-16 spelling reaches the *utf16* band by a margin. The band is calibrated on the error messages and format strings a binary carries, and the binary's own `strings` output straddles it: half *ascii*, a quarter high enough to read as code. **And the whole universal file is 77 % unnamed**, with a median of exactly 0.00: a fat Mach-O is mostly the page-aligned zero padding between its slices, and every one of those chunks scores 0 — the colour of the bar is the colour of the padding, and the code is the sixteen per cent.

## If you are coming from Python or ABAP

**Python.** `collections.Counter(data)` is the histogram and the score is a one-line sum over its values, which is section 1 of the example; `math.log2` is exact enough that `-p * log2(p)` summed over 256 terms agrees with Rust and `awk` to two decimals on every chunk here. Two habits transfer. Score `bytes`, never `str` — a `str` has no histogram until it is encoded, and section 2 is the proof that the encoding is what you are measuring. And when a score surprises you, look at the histogram before the file: `Counter(chunk).most_common(3)` names the value that is pulling the score down, which for UTF-16 is `0` with half the count.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* An `xstring` is the chunk, and a loop over its bytes with `xstr+off(1)` into a 256-row internal table is the histogram; `LOG` takes the natural logarithm, so divide by `LOG( 2 )` for bits. What this page changes is what to expect of the number. A UTF-16 system string — ABAP's own `string` type on a Unicode system is UTF-16 in memory — exported `IN BINARY MODE` will score around 3, and the same text written `IN TEXT MODE ENCODING UTF-8` around 4.5; a Latin-1 export, its Windows-1252 twin and the same file in a mainframe's EBCDIC code page will all score alike, because a code page is a one-to-one substitution and the histogram cannot tell them apart. So entropy can tell you *that* a segment is text and roughly how wide its characters are; which table it is in has to come from [the interface specification](../../07_Real_Data/sap_code_pages/README.md), verified against the system, as it always did.

## Try it

```bash
cd 11_Tools/entropy/examples
python3 entropy_bar_py.py
bash entropy_bar_sh.sh
rustc --edition 2024 entropy_bar_rs.rs && ./entropy_bar_rs
```

Then, on your own files:

1. Open any executable in Ghidra, turn on the overview bars from the Listing's toolbar, and hover down the entropy bar from top to bottom. Write down the four names the tooltip gives you and where each one starts; then open **Window › Memory Map** and see which block each boundary is.
2. Take an exported string table or a `.strings` file from a Mac app bundle — many are UTF-16 — and run it through the shell example's `score` in 1024-byte pieces: `split -b 1024`, then `score` on each piece. Then `iconv` it to UTF-8 and score again.
3. Pick a file you *know* is compressed or encrypted, and one you suspect is. Score both in chunks. A chunk that scores 8.0 exactly is worth a second look: [section 4](#in-python) says what else scores that.
4. In Ghidra, set **Chunk size** to 256, look at the same bar, and count how many more boundaries you can see — then how many of them are real.
5. If you have an EBCDIC file from a mainframe interface, score it beside its converted copy. Same score, different bytes: the bar would call both *ascii*.

## Practice

**Five chunks, one score each, and the band a thirteen-byte string lands in.** Before running anything, write down the score to two decimals for each of the five inputs below, and for each say which of Ghidra's four default names — `compressed`, `x86`, `ascii`, `utf16` — its palette entry would carry, or none. The bands are the *applied* column of the table above, and the palette entry is `floor(score × 32)`.

1. 1024 bytes of `00`.
2. `ab`, 512 times over.
3. Every byte value, four times over.
4. `Hello, World!` in UTF-8, then the same string in UTF-16LE.
5. `café` in UTF-8, then in Latin-1.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:entropy_bar_kata_sh -->
*Verified output of [`entropy_bar_kata_sh.sh`](examples/entropy_bar_kata_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. 1024 bytes of 00
0.00  -
2. 'ab', 512 times over
1.00  -
3. every byte value, four times over
8.00  compressed
4. 'Hello, World!' in UTF-8, then in UTF-16LE
3.18  utf16
2.59  -
5. 'café' in UTF-8, then in Latin-1
2.32  -
2.00  -
```
<!-- /output -->

**1 and 2 are the two smallest histograms there are**: one value is 0 bits, two equal values are 1 bit, and neither is near a band. **3 is the top of the scale from a counter**, 8.00, entry 255, *compressed* — the band names the histogram's flatness and cannot see that the bytes count from 0 to 255. **4 is the trap.** Thirteen bytes of ASCII score 3.18, whose entry is 101 — inside the `utf16` band, 96 to 109 — so a short ASCII string gets UTF-16's name, while the real UTF-16 spelling scores 2.59 and gets none. The bands are calibrated for 1024-byte chunks, where a text-shaped histogram has room to reach 4.2; a string this short is capped by its ten distinct values at `log2(10) = 3.32`, and nothing about its score says which encoding it is in. **5 is the encoding changing the score** while the word does not: five distinct bytes against four, `log2(5)` against `log2(4)`.

</details>

## See also

- [`strings` has a printable set, not an encoding](../strings/README.md) — the other tool that reads a binary for its text, and the one whose output this page's dated fence scores
- [`file` guesses](../../06_Terminal/file_guesses/README.md) and [The five worth installing](../worth_installing/README.md) — `file` and `uchardet`, the two other detectors here; entropy is the third, and the only one that never reads a character
- [Binary is a verdict, not a property](../../06_Terminal/binary_or_text/README.md) — what other readers test to decide a file is not text; the entropy bar tests nothing and scores everything
- [Rotation is not encryption](../../02_Characters/rotation_is_not_encryption/README.md) — why section 3's ROT13 keeps its score, and why that is how a substitution cipher is broken
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — the `00` after every Latin letter that gives UTF-16 a band of its own
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — why the shell example names `UTF-16LE` rather than `UTF-16`
- [Decompress, then decode](../decompress_then_decode/README.md) — what to do with a region the bar has called *compressed*
- [Raw binary](../../16_Formats/raw_binary/README.md) — the import that gives Ghidra no header at all, and where this bar is the first thing that says what the bytes are
- [16_Formats](../../16_Formats/README.md) — the other Ghidra dialog in this library, read the same way: the source at the 12.1.3 tag, nothing run through Ghidra, real files in dated fences
- [Ghidra's `Overview.htm` at 12.1.3 ↗](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/help/help/topics/OverviewPlugin/Overview.htm) — the help page this one runs, and the same text as **Help › Contents › Overview** in the tool
