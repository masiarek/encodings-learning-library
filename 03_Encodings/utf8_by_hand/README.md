# UTF-8 by hand

**Level:** 101 → 201 · the lesson this library is built around

**One line:** UTF-8 writes a code point as one to four bytes — a lead byte whose top bits announce the length, then continuation bytes that all start `10` — so the whole encoding is a pencil, some binary, and four templates you can hold in your head.

A [code point](../../02_Characters/unicode_code_points/README.md) is a number. A file is [bytes](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md). This page is the rule that turns the first into the second, and it is small enough to do on paper — which is the point. Once you have encoded `é` to `C3 A9` yourself, a hex dump stops being a wall of numbers, `Ã©` stops being mysterious, and the rest of this chapter is variations on a mechanism you already own.

Nothing here needs memorising. Every number on this page falls out of one idea: **a byte has eight bits, and some of them have to be spent saying what kind of byte this is.**

## The four templates

An `x` is a payload bit — a bit of the actual number. Every other bit is a marker.

| bytes | template | payload bits | code points |
|---|---|---|---|
| 1 | `0xxxxxxx` | 7 | `U+0000`–`U+007F` |
| 2 | `110xxxxx 10xxxxxx` | 11 | `U+0080`–`U+07FF` |
| 3 | `1110xxxx 10xxxxxx 10xxxxxx` | 16 | `U+0800`–`U+FFFF` |
| 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 21 | `U+10000`–`U+10FFFF` |

Two rules do all the work, and everything else on this page is a consequence of them:

- **A byte starting `0` is a whole character by itself.** So all 128 ASCII bytes mean in UTF-8 exactly what they meant in ASCII, and an ASCII file is already a UTF-8 file — not converted, not compatible-with, the same bytes.
- **A byte starting `10` is never a lead byte.** It only ever continues one. That single decision is what lets you drop into the middle of a stream and find your footing, and it is the property the shell example below cuts a pipe in half to show.

The lead byte's marker is a count in unary: `110` for two bytes, `1110` for three, `11110` for four. Count the leading `1`s and you know the length before reading a single byte further.

## Encoding, with a pencil

`é` is `U+00E9`. Do it in five steps.

1. **Write the number in binary.** `0xE9` is `1110 1001` — eight bits.
2. **Pick the template.** Eight bits will not fit in the one-byte template's seven payload slots, so it is the two-byte one, which has eleven.
3. **Pad to eleven.** `000 1110 1001`, or `00011101001`.
4. **Cut at the slot boundaries.** The two-byte template takes 5 payload bits then 6: `00011` and `101001`.
5. **Put the markers back in front.** `110` + `00011` = `11000011`; `10` + `101001` = `10101001`.

That is `C3 A9` — the one pair in this library worth knowing on sight, since every mojibake demonstration starts from it ([the cast](../../CAST.md)). The same five steps give every other character:

| character | code point | bits to carry | template | bytes |
|---|---|---|---|---|
| `A` | `U+0041` | 7 | 1 byte | `41` |
| `é` | `U+00E9` | 8 | 2 bytes | `C3 A9` |
| `ż` | `U+017C` | 9 | 2 bytes | `C5 BC` |
| `€` | `U+20AC` | 14 | 3 bytes | `E2 82 AC` |
| `😀` | `U+1F600` | 17 | 4 bytes | `F0 9F 98 80` |

**`A` is the row to notice first.** `U+0041` needs seven bits, the one-byte template has seven slots, and the byte that comes out is `41` — the same `41` ASCII has used since 1963. Nothing was converted. That is compatibility as arithmetic rather than as a promise.

**`é` is the row to sit with.** `U+00E9` is 233, which fits in a byte with room to spare — and it still takes two bytes, because the one-byte template has seven payload slots and 233 needs eight. *Does the number fit in a byte* is not the question UTF-8 asks; *does it fit in this template's payload* is. That one confusion is behind most of the "but é is one character" arguments, and this is where it dies.

**`ż` and `é` share a template and not a story.** `é` is `E9` in [Latin-1](../../02_Characters/code_pages/README.md) — one byte, if you have the right table. `ż` is `U+017C`, past `U+00FF` entirely, so no 8-bit table has room for it at all. In UTF-8 they cost the same two bytes and neither needs a table to be chosen. That is the whole argument for Unicode in one comparison.

## Where the thresholds come from

`0x80`, `0x800` and `0x10000` are not conventions to look up. Each is two raised to a template's payload width — the first number that template can no longer hold, which is exactly where the next one has to start:

```text
 7 payload slots reach U+007F     ->  1 byte  covers U+0000  - U+007F
11 payload slots reach U+07FF     ->  2 bytes covers U+0080  - U+07FF
16 payload slots reach U+FFFF     ->  3 bytes covers U+0800  - U+FFFF
21 payload slots reach U+1FFFFF   ->  4 bytes covers U+10000 - U+10FFFF
```

Only the last row stops early. Its 21 slots reach `U+1FFFFF`, and UTF-8 stops at `U+10FFFF` — 983,040 numbers it could express and does not. That ceiling is not this table's. It is the largest number [UTF-16 can reach](../utf16_and_surrogates/README.md), and the arithmetic says so exactly: a surrogate pair carries twenty bits above `U+FFFF`, and `0x10000 + 2²⁰ − 1 = 0x10FFFF`. [RFC 3629 ↗](https://www.rfc-editor.org/rfc/rfc3629#section-3) capped UTF-8 there in 2003 for that reason, retiring the older definition that ran to six bytes.

## Decoding is the same table backwards

Count the leading `1`s of the first byte: none means one byte, two means two, three means three, four means four. Strip every marker, concatenate what is left, read the number.

```text
E2 82 AC   ->  1110 0010   10 000010   10 101100
               ^^^^        ^^          ^^          markers, discarded
                    0010      000010      101100    payload, concatenated
           ->  0010 0000 1010 1100  =  0x20AC  =  €
```

The width came out of the first byte alone. Nothing had to be counted ahead of time, nothing had to be remembered from earlier in the stream, and no table was consulted — which is the property the next section is about.

## Reading from the middle

Every byte value falls into exactly one of four classes, and a byte announces its class with no context at all:

| bytes | how many | what it is |
|---|---|---|
| `00`–`7F` | 128 | a whole character by itself |
| `C2`–`F4` | 51 | starts a two-, three- or four-byte character |
| `80`–`BF` | 64 | continues one, and can never start one |
| `C0`, `C1`, `F5`–`FF` | 13 | appear in no well-formed UTF-8 at all |

So if you are handed a byte offset in the middle of a file — a seek into a log, a chunk boundary, a truncated packet — walk backwards while the byte is in `80`–`BF`, and the first byte that is not one is the start of the character you landed in. It is never more than three steps, because no template is longer. **That is what "self-synchronising" means**, and the cost of a corrupt byte is one character rather than the rest of the stream.

Why the design is shaped to give you that, and the five other properties that came with it, is [Why UTF-8 won](../../09_History/why_utf8_won/README.md). This page is the mechanism; that page is the argument.

## Table 3-7, checked rather than quoted

The templates are a recipe, and they are also a *rule* — there are byte sequences that match a template perfectly and are still not UTF-8. The standard writes the rule out as [Table 3-7, *Well-Formed UTF-8 Byte Sequences* ↗](https://www.unicode.org/versions/latest/core-spec/chapter-3/), which is what every real decoder is compiled from, and which is why a UTF-8 decoder is a small state machine rather than a shift-and-mask:

| code points | byte 1 | byte 2 | byte 3 | byte 4 |
|---|---|---|---|---|
| `U+0000`–`U+007F` | `00`–`7F` | | | |
| `U+0080`–`U+07FF` | `C2`–`DF` | `80`–`BF` | | |
| `U+0800`–`U+0FFF` | `E0` | **`A0`–`BF`** | `80`–`BF` | |
| `U+1000`–`U+CFFF` | `E1`–`EC` | `80`–`BF` | `80`–`BF` | |
| `U+D000`–`U+D7FF` | `ED` | **`80`–`9F`** | `80`–`BF` | |
| `U+E000`–`U+FFFF` | `EE`–`EF` | `80`–`BF` | `80`–`BF` | |
| `U+10000`–`U+3FFFF` | `F0` | **`90`–`BF`** | `80`–`BF` | `80`–`BF` |
| `U+40000`–`U+FFFFF` | `F1`–`F3` | `80`–`BF` | `80`–`BF` | `80`–`BF` |
| `U+100000`–`U+10FFFF` | `F4` | **`80`–`8F`** | `80`–`BF` | `80`–`BF` |

Five cells carry the entire difference between the templates and the rule: the four in bold, and the `C2` floor in row two. Three of those five forbid a *padded second spelling* of a character that already has one — the `C2` floor, `E0`'s `A0` and `F0`'s `90` — which is [Overlong sequences](../overlong_sequences/README.md). The `ED` row capped at `9F` excludes the [surrogates](../utf16_and_surrogates/README.md). `F4` capped at `8F` is the top of Unicode. Every *continuation* cell not in bold is the full `80`–`BF`.

**None of that is quoted here.** The table above was expanded and walked from both ends:

- The Python example takes **every scalar value Unicode can hold**, encodes it by the pencil method in the section above, drops it into the one row whose code point range contains it, and checks the bytes against that row's columns.
- The Rust example goes the other way: **every byte combination the nine rows permit**, decoded by hand, checked against the code point range its row claims, then handed to `str::from_utf8`.
- The C example does the round trip in a third independent implementation — its own encoder into its own decoder, over the same set.

Both directions come out at **1,112,064**, and that is the finding worth carrying away. It is the same set counted from the two opposite sides of the table — once as numbers on the number line, once as products of byte ranges. Subtract the surrogate hole from the ceiling and you get `0x110000 − 2048 = 1112064`. Add up nine rows of a *byte* table — `128 + 1920 + 2048 + 49152 + 2048 + 8192 + 196608 + 786432 + 65536` — and you get 1,112,064 again. **So Table 3-7 is a bijection:** one byte sequence per scalar value, one scalar value per byte sequence, nothing on either side without a partner on the other, and no exceptions to remember.

The hole is visible in the table itself, if you look at where the rows stop. Row five ends at `U+D7FF` and row six begins at `U+E000`; the 2,048 numbers between them are the surrogates, and the thing that removes them is that one `9F` in row five's second column. Nothing was deleted from the table — the cap *is* the deletion.

### And this one has no version

[The table has a version](../../02_Characters/the_table_has_a_version/README.md) is the page that says a fact read out of the Unicode database is a fact about your runner: `python3` and `rustc` answer from different Unicode versions on the same machine, so a character's category, a count of assigned code points, or whether some recent emoji exists at all cannot become an answer key here.

**That rule does not reach this page.** Nothing above is a lookup. The row shapes are fixed by the encoding form; the thresholds are powers of two; the surrogate hole and the `U+10FFFF` ceiling are both fixed by [RFC 3629 ↗](https://www.rfc-editor.org/rfc/rfc3629), which has said so since 2003; and the exhaustion is arithmetic over an interval of the number line. `1112064` is not a count of anything Unicode assigns — it is `0x110000 − 2048`, and it was the same number before any of the characters in it were named. So it is one of the few numbers in this library you can put in a bug report with no version stamp beside it — which is the distinction that page's own kata asks you to draw.

### What it cost

The timing is the one thing here that *is* about a machine, so it goes in a fence with a date on it rather than into a program's output:

```text
Measured 2026-09-07 on one machine — macOS 26.6.2, x86_64, python3 3.14.7,
rustc 1.98.0, Apple clang 21.0.0. Whole programs, timed the way
tools/run_examples.py runs them, with no optimisation flag on either compile.

  utf8_by_hand_py.py    2.9 s    1,112,064 code points encoded by hand,
                                 each cross-checked against CPython's codec
  utf8_by_hand_rs.rs    0.09 s   1,112,064 byte sequences decoded by hand,
                                 each cross-checked against str::from_utf8
  utf8_by_hand_c.c      0.05 s   1,112,064 round trips, own encoder into own
                                 decoder, plus the zero-byte sweep

And the price of the pencil, isolated: the same 1,112,064-iteration Python
loop takes 1.5 s calling the hand-written encoder and 0.28 s calling
chr(cp).encode('utf-8') — five times slower, which is the cost of a
Python-level function call and not of the encoding.
```

Worth stating plainly, because this library's backlog predicted otherwise: [TODO.md](../../TODO.md) promised this check "in about a second". In Rust and C it is far under that, and in Python — the language where the hand-written encoder is most readable, which is why it lives there — it is about three. The number that mattered turned out not to be the clock anyway. It was the two 1,112,064s meeting in the middle.

## In Python

<!-- output:utf8_by_hand_py -->
*Verified output of [`utf8_by_hand_py.py`](examples/utf8_by_hand_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE FOUR TEMPLATES
   An x is a payload bit. Every other bit is a marker, and it announces
   one of two things: how long this character is, or that this byte is
   the continuation of one.

   bytes  template                              payload  code points
   1      0xxxxxxx                               7 bits  U+0000 - U+007F
   2      110xxxxx 10xxxxxx                     11 bits  U+0080 - U+07FF
   3      1110xxxx 10xxxxxx 10xxxxxx            16 bits  U+0800 - U+FFFF
   4      11110xxx 10xxxxxx 10xxxxxx 10xxxxxx   21 bits  U+10000 - U+10FFFF

   Two rules do all the work. A byte starting 0 is a whole character by
   itself, so all 128 ASCII bytes mean in UTF-8 exactly what they meant
   in ASCII. And a byte starting 10 is never a lead byte, only ever the
   continuation of one -- which is what makes a UTF-8 stream readable
   from any position, and is why the shell example can cut one in half
   and still find its footing.

2. FIVE CHARACTERS, DONE WITH A PENCIL
   Write the number in binary. Pad it to the payload width of the
   narrowest template that fits. Cut it at the slot boundaries. Put the
   markers back in front. Read off the hex.

   A   U+0041   ASCII: one byte, and the byte is unchanged
      the number in binary        1000001
      padded to 7 payload slots   1000001
      cut at the slot boundaries  1000001
      markers put back in front   01000001
      the bytes                   41
      CPython's own codec         41   agrees

   é   U+00E9   the number fits in a byte; the character needs two
      the number in binary        11101001
      padded to 11 payload slots  00011101001
      cut at the slot boundaries  00011 101001
      markers put back in front   11000011 10101001
      the bytes                   C3 A9
      CPython's own codec         C3 A9   agrees

   ż   U+017C   Polish: past U+00FF, so no 8-bit table can hold it
      the number in binary        101111100
      padded to 11 payload slots  00101111100
      cut at the slot boundaries  00101 111100
      markers put back in front   11000101 10111100
      the bytes                   C5 BC
      CPython's own codec         C5 BC   agrees

   €   U+20AC   three bytes -- 16 slots for a 14-bit number
      the number in binary        10000010101100
      padded to 16 payload slots  0010000010101100
      cut at the slot boundaries  0010 000010 101100
      markers put back in front   11100010 10000010 10101100
      the bytes                   E2 82 AC
      CPython's own codec         E2 82 AC   agrees

   😀   U+1F600   above U+FFFF: the four-byte row, 17 bits in 21 slots
      the number in binary        11111011000000000
      padded to 21 payload slots  000011111011000000000
      cut at the slot boundaries  000 011111 011000 000000
      markers put back in front   11110000 10011111 10011000 10000000
      the bytes                   F0 9F 98 80
      CPython's own codec         F0 9F 98 80   agrees

   The second character is the one to sit with. U+00E9 is 233, which fits
   in a byte with room to spare -- and it still takes two bytes, because
   the one-byte template has seven payload slots and 233 needs eight.
   'Does the number fit in a byte' is not the question UTF-8 asks.

3. WHERE THE THRESHOLDS COME FROM
   0x80, 0x800 and 0x10000 are not conventions to memorise. Each is two
   raised to a template's payload width: the first number that template
   can no longer hold, which is where the next one starts.

    7 payload slots reach U+007F   -> 1 byte  covers U+0000 - U+007F
   11 payload slots reach U+07FF   -> 2 bytes covers U+0080 - U+07FF
   16 payload slots reach U+FFFF   -> 3 bytes covers U+0800 - U+FFFF
   21 payload slots reach U+1FFFFF -> 4 bytes covers U+10000 - U+10FFFF

   Only the last row stops early. Its 21 slots reach U+1FFFFF, and UTF-8
   stops at U+10FFFF, so 983040 of the numbers it could express name
   nothing. That ceiling is not this table's -- it is the largest number
   UTF-16 can reach, and the arithmetic says so exactly:
      0x10000 + 2**20 - 1 = 0x10FFFF   (a surrogate pair carries 20 bits)

4. DECODING IS THE SAME TABLE READ BACKWARDS
   Count the leading 1s of the first byte: none means one byte, two means
   two, three means three, four means four. Strip every marker, join what
   is left, and that is the number.

   41            payload 1000001                = U+0041   ok
   C3 A9         payload 00011101001            = U+00E9   ok
   C5 BC         payload 00101111100            = U+017C   ok
   E2 82 AC      payload 0010000010101100       = U+20AC   ok
   F0 9F 98 80   payload 000011111011000000000  = U+1F600  ok

   The width came out of the first byte alone. Nothing had to be counted
   ahead, and nothing had to be remembered from earlier in the stream.

5. TABLE 3-7, CHECKED BY EXHAUSTION -- THE CODE POINT SIDE
   Every scalar value Unicode can hold, encoded by the pencil method in
   section 2, placed in the one row whose code point range contains it,
   then checked byte by byte against that row's byte columns.

   code points            the row's byte columns                   scalars
   U+0000 - U+007F        00-7F                                       128
   U+0080 - U+07FF        C2-DF 80-BF                                1920
   U+0800 - U+0FFF        E0-E0 A0-BF 80-BF                          2048
   U+1000 - U+CFFF        E1-EC 80-BF 80-BF                         49152
   U+D000 - U+D7FF        ED-ED 80-9F 80-BF                          2048
   U+E000 - U+FFFF        EE-EF 80-BF 80-BF                          8192
   U+10000 - U+3FFFF      F0-F0 90-BF 80-BF 80-BF                  196608
   U+40000 - U+FFFFF      F1-F3 80-BF 80-BF 80-BF                  786432
   U+100000 - U+10FFFF    F4-F4 80-8F 80-BF 80-BF                   65536

   1112064 scalar values, every one encoding to bytes that lie
   inside the row claiming it. None fell outside all nine rows, none
   matched two, and CPython's codec agreed on every answer.

6. THE HOLE IN THE MIDDLE IS THE SURROGATES
   Rows five and six are neighbours in the table and their code point
   ranges are not neighbours. Nothing was left out: the gap is what the
   ED row's second byte, capped at 9F where every other row reaches BF,
   is for.

   row 5 (ED 80-9F ..) ends at    U+D7FF
   row 6 (EE-EF ..) begins at     U+E000
   the gap                        U+D800 - U+DFFF
                                  2048 numbers that are not characters

   0x110000 - 2048 = 1112064, which is the total in section 5.
   Two ways of counting one set: subtract the hole from the ceiling, or
   add up nine rows of a byte table. They have to agree, and they do.

7. WHAT A CHARACTER COSTS, AND WHY BYTES >= CHARACTERS ALWAYS
   A template row is a range of code points, so the byte cost of a letter
   is settled by where its script sits on the number line. The library's
   whole cast, sorted into the four rows:

   1 byte   U+0000 - U+007F     A U+0041  ~ U+007E
   2 bytes  U+0080 - U+07FF     ß U+00DF  é U+00E9  ż U+017C
   3 bytes  U+0800 - U+FFFF     ಠ U+0CA0  € U+20AC  日 U+65E5
   4 bytes  U+10000 - U+10FFFF  😀 U+1F600

   And the cast's strings, measured rather than described:

   code points   bytes   what costs what
            13      13   ASCII only: the two rulers agree       Hello, World!
             4       5   one two-byte letter                    café
             4       7   Polish: three of four letters cost two żółw
             3       9   CJK: three bytes each                  日本語
             1       4   one emoji, and the widest row there is 😀

   len(bytes) >= len(str), always, and never the other way, because the
   narrowest template is one byte wide. The two are equal exactly when
   every character is ASCII -- which is the whole compatibility story in
   one sentence, and the reason an ASCII file is already a UTF-8 file.
```
<!-- /output -->

Sections 1 to 4 are the pencil, written out: the encoder is the five steps from the top of this page, and CPython's codec appears only as the second opinion each answer is checked against. That ordering is deliberate — a page about doing the thing yourself should not open by calling the library that does it for you.

Section 5 is the exhaustion, and section 6 is the count identity. Section 7 is the consequence for real text: `len(bytes) >= len(str)` always, and never the other way, because the narrowest template is one byte wide — the two numbers being equal is exactly the definition of an ASCII-only string.

## In the terminal

<!-- output:utf8_by_hand_sh -->
*Verified output of [`utf8_by_hand_sh.sh`](examples/utf8_by_hand_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE TEMPLATES, ON A REAL PIPE
   printf writes the bytes; xxd -b prints them back as bits. The markers
   are in plain view: a lone 0, or 110/1110/11110 and then 10 each time.

   A              01000001
   e-acute        11000011 10101001
   z-dot          11000101 10111100
   euro           11100010 10000010 10101100
   grinning face  11110000 10011111 10011000 10000000

   Count the leading 1s of the first group and you have the length,
   before reading any further byte. That is the whole decoder.

2. FROM A HEX DUMP BACK TO A CHARACTER
   The pencil loop closed: type the bytes you worked out, and the
   terminal shows you what they say. No library, no table lookup.

   printf '\x41'              writes 41         and the terminal shows  A
   printf '\xc3\xa9'          writes c3a9       and the terminal shows  é
   printf '\xc5\xbc'          writes c5bc       and the terminal shows  ż
   printf '\xe2\x82\xac'      writes e282ac     and the terminal shows  €
   printf '\xf0\x9f\x98\x80'  writes f09f9880   and the terminal shows  😀

   That is also how you make a test file for a character you cannot
   type -- and how you make one your editor would quietly repair.

3. ONE FILE, AND WHY THE TWO RULERS DISAGREE
   Four letters either way, and one file is bigger. Every non-ASCII
   letter is paying for its second byte.

    5 bytes on disk   7a6f6c770a         the word: zolw
    8 bytes on disk   c5bcc3b3c582770a   the word: żółw

   0a is the newline, one byte in both. Strip it and the Polish word is
   7 bytes for 4 letters: three letters at two bytes, one at one. The
   file records none of that -- a reader has to be told the encoding,
   which is this chapter's whole argument.

4. CUT THE PIPE IN THE MIDDLE OF A CHARACTER
   The stream is 'a', z-dot, a grinning face, 'b' -- 8 bytes:

      61c5bcf09f988062

   Start reading at each byte in turn, as a program joining a stream
   late would. A first byte in 80-BF says you have landed inside a
   character: skip while that is true, and the next one starts there.

   start  byte  class         skip  starts at  width  the character
       1    61  ASCII            0          1      1  a
       2    c5  lead of 2        0          2      2  ż
       3    bc  continuation     1          4      4  😀
       4    f0  lead of 4        0          4      4  😀
       5    9f  continuation     3          8      1  b
       6    98  continuation     2          8      1  b
       7    80  continuation     1          8      1  b
       8    62  ASCII            0          8      1  b

   Never more than three bytes skipped, because no template is longer.
   So a truncated or corrupted file costs you one character and not the
   rest of the stream. Note what the resync did NOT need: no state from
   earlier in the file, no byte count from the top, and no lookahead.
   That is what self-synchronising means, and it is a consequence of one
   decision -- continuation bytes start 10, and nothing else does.

5. HALF A CHARACTER IS NOT TEXT
   The templates are a rule as well as a recipe, so a piece of a
   character is refused rather than decoded into something.

   printf '\xc5\xbc'            exit 0   valid UTF-8
   printf '\xc5'                exit 1   refused
   printf '\xbc'                exit 1   refused
   printf '\xf0\x9f\x98\x80'    exit 0   valid UTF-8
   printf '\xf0\x9f'            exit 1   refused
   printf '\x80\x80'            exit 1   refused

   A lead byte with its continuations missing is refused, and so is a
   continuation byte with no lead byte in front of it. Both are the
   templates being read as a specification. Who runs that check, and
   what is left of it downstream, is the next lesson.
```
<!-- /output -->

**Section 4 is why this page has a shell example at all.** Python and Rust can tell you a character is four bytes; only a pipe can be cut in the middle of one so you can watch a reader recover. The script starts reading the same eight-byte stream at each of its eight offsets, in turn, and prints how far it had to skip and which character it landed on. Three of the eight offsets land inside a character, the worst skip is three bytes, and none of it needs a byte count from the top of the file or any state at all.

Everything here writes bytes with `\xHH`, which names a *byte* and asks nothing of the locale or the bash version. The other spelling does not travel: `printf '\u20ac'` — the escape that names a *code point* rather than a byte — gives three different answers on three configurations, and only one of them is a euro sign — that story is on [Writing a code point](../../02_Characters/writing_a_code_point/README.md).

## In Rust

<!-- output:utf8_by_hand_rs -->
*Verified output of [`utf8_by_hand_rs.rs`](examples/utf8_by_hand_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. char IS A SCALAR VALUE, AND THAT IS A TYPE
   Rust's char is not a byte and not a UTF-16 unit. It is one code
   point that is not a surrogate -- exactly the set Table 3-7 covers
   -- and the type refuses everything outside it at construction.

   size_of::<char>()        = 4 bytes, the same for every char
   char::MAX                = U+10FFFF
   char::from_u32(0x41)     = Some('A')  1 byte(s) in a String
   char::from_u32(0xE9)     = Some('é')  2 byte(s) in a String
   char::from_u32(0x17C)    = Some('ż')  2 byte(s) in a String
   char::from_u32(0x20AC)   = Some('€')  3 byte(s) in a String
   char::from_u32(0x1F600)  = Some('😀')  4 byte(s) in a String
   char::from_u32(0xD800)   = None      a surrogate is not a scalar value
   char::from_u32(0x110000) = None      above the top of Unicode

   Two numbers that disagree on purpose. A char is always 4 bytes in
   memory, because a fixed width is what makes it a type you can put
   in an array; len_utf8() is 1 to 4, because that is what it costs
   in a String. Neither is wrong and neither answers the other's
   question.

2. THE BUFFER IS FOUR BYTES, AND THAT IS THE WHOLE PROMISE
   encode_utf8 writes into a caller's [u8; 4]. The 4 is not a guess:
   it is the width of the last template, and the type system is
   where this page's table ends up living.

   U+0041   'A'  len_utf8() 1   returns 41           buf 41 00 00 00
   U+00E9   'é'  len_utf8() 2   returns C3 A9        buf C3 A9 00 00
   U+017C   'ż'  len_utf8() 2   returns C5 BC        buf C5 BC 00 00
   U+20AC   '€'  len_utf8() 3   returns E2 82 AC     buf E2 82 AC 00
   U+1F600  '😀'  len_utf8() 4   returns F0 9F 98 80  buf F0 9F 98 80

   The trailing zeros are the buffer, not the character: encode_utf8
   hands back a &str borrowing only the bytes it wrote. len_utf8()
   answered the same question before a single byte was written.

3. TABLE 3-7, CHECKED BY EXHAUSTION -- THE BYTE SIDE
   Every byte combination the nine rows permit, decoded by hand, and
   checked against the code point range the row claims. Then handed
   to str::from_utf8, which is the decoder Rust ships.

   the row's byte columns                    sequences   decoding into
   00-7F                                          128   U+0000 - U+007F
   C2-DF 80-BF                                   1920   U+0080 - U+07FF
   E0-E0 A0-BF 80-BF                             2048   U+0800 - U+0FFF
   E1-EC 80-BF 80-BF                            49152   U+1000 - U+CFFF
   ED-ED 80-9F 80-BF                             2048   U+D000 - U+D7FF
   EE-EF 80-BF 80-BF                             8192   U+E000 - U+FFFF
   F0-F0 90-BF 80-BF 80-BF                     196608   U+10000 - U+3FFFF
   F1-F3 80-BF 80-BF 80-BF                     786432   U+40000 - U+FFFFF
   F4-F4 80-8F 80-BF 80-BF                      65536   U+100000 - U+10FFFF

   1112064 byte sequences -- the same number the Python example
   counted from the other end. The rows do not overlap and they leave
   nothing out, so the table is a bijection: one sequence per scalar
   value, one scalar value per sequence, and no exceptions to learn.

4. WHAT MAKES A STREAM READABLE FROM THE MIDDLE
   Four classes of byte value, and they do not overlap -- so any
   byte announces which class it is in with no context at all:

   00-7F          128  a whole character by itself
   C2-F4           51  starts a two-, three- or four-byte character
   80-BF           64  continues one, and can never start one
   C0, C1, F5-FF   13  appear in no well-formed UTF-8 at all
                  ---
                  256  every byte value, in exactly one class

   So from any offset, walk backwards over 80-BF and the first byte
   that is not one is the start of the character you landed in. It
   is never more than three steps, because no template is longer.

   "aż😀b" is 8 bytes: 61 C5 BC F0 9F 98 80 62

   offset  byte  is_char_boundary  the character it belongs to
        0  61    true              'a' starting at offset 0
        1  C5    true              'ż' starting at offset 1
        2  BC    false             'ż' starting at offset 1
        3  F0    true              '😀' starting at offset 3
        4  9F    false             '😀' starting at offset 3
        5  98    false             '😀' starting at offset 3
        6  80    false             '😀' starting at offset 3
        7  62    true              'b' starting at offset 7

   is_char_boundary is that backward walk with a name. Rust exposes
   it because &str indexing is by BYTE offset and the language will
   not let you cut a character in half -- so the question the shell
   answers with a hex dump is, here, a method on the type.
```
<!-- /output -->

Rust is where this page's table stops being knowledge and becomes a type. `char` is *defined* as a scalar value — a code point that is not a surrogate, exactly the set Table 3-7 covers — so `char::from_u32(0xD800)` is `None` and there is no later point at which the question can be reopened. The buffer that `encode_utf8` writes into is `[u8; 4]`, and the `4` is not a safety margin; it is the width of the last template.

The two sizes disagree on purpose, and it is the checkpoint this chapter builds toward: `size_of::<char>()` is always 4 because a fixed width is what makes `char` a type you can put in an array, while `len_utf8()` is 1 to 4 because that is what it costs inside a [`String`](../../05_Rust/string_is_bytes_that_promise_utf8/README.md). Neither answers the other's question. Section 4's `is_char_boundary` is the backwards walk from *Reading from the middle*, with a name — Rust exposes it because `&str` is indexed by byte offset and the language will not let you cut a character in half.

## The C view

<!-- output:utf8_by_hand_c -->
*Verified output of [`utf8_by_hand_c.c`](examples/utf8_by_hand_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE ENCODER IS THE PENCIL METHOD, IN TEN LINES
   No character type, no string type, no library. Choose the
   template by comparing against 0x80 / 0x800 / 0x10000, shift the
   payload bits into place, or with the markers. That is all of it.

   code point   bytes  the encoder's answer  as text
   U+0041        1      41           A   ASCII
   U+00E9        2      C3 A9        é   233 needs 8 bits, and 7 fit
   U+017C        2      C5 BC        ż   past U+00FF
   U+20AC        3      E2 82 AC     €   14 bits in 16 slots
   U+1F600       4      F0 9F 98 80  😀   above U+FFFF

2. AND THE DECODER IS THE SAME TABLE BACKWARDS
   The first byte announces the width; every other byte gives up its
   low six bits. Round-tripped over every scalar value below.

   41           announced width 1   decodes to U+0041    ok
   C3 A9        announced width 2   decodes to U+00E9    ok
   C5 BC        announced width 2   decodes to U+017C    ok
   E2 82 AC     announced width 3   decodes to U+20AC    ok
   F0 9F 98 80  announced width 4   decodes to U+1F600   ok

3. THE ROUND TRIP, OVER EVERY SCALAR VALUE UNICODE HAS
   1112064 scalar values encoded, and every one decoded back to
   the number it came from. No table, no library, no allocation.

   1 byte        128   ASCII
   2 bytes      1920
   3 bytes     61440   (the surrogate hole is subtracted here)
   4 bytes   1048576
             1112064   = 0x110000 - 2048

   Worst backward walk from a byte to its character's start: 3
   -- three, because no template is longer. That loop is the whole
   of self-synchronisation and it needs no state at all.

4. WHY strlen NEVER HAD TO CHANGE
   C strings end at a zero byte, so an encoding that put a zero byte
   inside a character would have broken every C program ever written.
   UTF-8 does not, and that is checkable rather than promised:

   zero bytes found inside a multi-byte character : 0
   bytes below 0x80 found inside one              : 0

   "żółw"  strlen = 7   bytes: C5 BC C3 B3 C5 82 77
   strchr(word, 'w') found the 'w' at byte 6, and it really is
   a 'w' -- not the tail of a letter that happened to end in 0x77.

   strlen counts bytes, and on this page that is not a bug: there is
   no character type in C to count instead. What matters is that it
   terminates in the right place and that a byte search cannot land
   inside a character. Both fall out of the templates, and both are
   why UTF-8 could be adopted without a flag day.
```
<!-- /output -->

C has no character type, no string type and no opinion about text, so the encoder in section 1 *is* the pencil method — ten lines of shifting and masking, and after this page you could write it from the table. It is also the one language where the encoding's compatibility argument is something you can measure rather than assert.

Section 4 is that measurement. A C string ends at a zero byte, so an encoding that put a zero byte *inside* a character would have broken every C program ever written; UTF-8 does not, and the sweep over all 1,112,064 encodings finds zero of them — along with zero bytes below `0x80` inside a multi-byte character, which is why `strchr(word, 'w')` finds a real `w` and never the tail of some other letter. Shift-JIS could not promise that, and the [decade of Japanese filename bugs](../../09_History/why_utf8_won/README.md) that followed is the counter-example.

## If you are coming from Python or ABAP

**Python.** You have already been using this table; `'é'.encode('utf-8')` is the five steps from the top of this page, implemented in C inside CPython, and `b'\xc3\xa9'.decode('utf-8')` is them backwards. What the by-hand version changes is that the two `len`s stop being surprising: `len('é')` is 1 because `str` counts code points, `len('é'.encode())` is 2 because `bytes` counts bytes, and the second is never smaller than the first. The gap Python leaves open is the surrogates — a `str` can hold `chr(0xD800)`, because `str` is a sequence of *code points* and not of scalar values, so `chr(0xD800).encode('utf-8')` raises rather than producing the `ED A0 80` your pencil would. That is the kata below, and the handlers that soften it are [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md).

**ABAP.** A Unicode ABAP system holds `string` in a fixed-width UTF-16 form internally, so on this page's terms it never sees a UTF-8 byte at all until you ask for one — which means the templates matter to you at exactly one place, the boundary. `cl_abap_codepage=>convert_to( )` encodes a `string` into an `xstring`, `convert_from( )` goes back, and `cl_abap_conv_*` is the older spelling of the same job. Two consequences worth holding onto. `STRLEN` counts UTF-16 units, so it agrees with this page's code point count for everything below `U+10000` and disagrees above it — an emoji is one code point and *two* to `STRLEN`, which is the same arithmetic as [UTF-16 and surrogates](../utf16_and_surrogates/README.md), not a bug. And a field declared as N bytes is N *bytes*: `ż` costs two of them, so truncating a UTF-8 `xstring` at a byte count can cut a character in half and produce something that is no longer text. Verify any code page number against your own system rather than trusting one from a document. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

All four programs, from the repository root:

```bash
cd 03_Encodings/utf8_by_hand/examples
python3 utf8_by_hand_py.py
bash utf8_by_hand_sh.sh
rustc --edition 2024 utf8_by_hand_rs.rs -o /tmp/u8 && /tmp/u8
cc -std=c11 -Wall -Wextra utf8_by_hand_c.c -o /tmp/u8c && /tmp/u8c
```

Then, on your own files:

1. **Encode your own name.** Take a letter from it that is not ASCII, find its code point (`python3 -c "print(hex(ord('ż')))"`), and do the five steps on paper. Then check: `printf '\xc5\xbc' | xxd -p`, with your own bytes.
2. **Read a real file's first character.** `head -c 4 somefile.txt | xxd -b` on anything you have — a CSV that came out wrong, a downloaded page, a log. Count the leading `1`s of the first byte and say how long the first character is before you decode anything.
3. **Count the characters in a file with no decoder.** The byte classes are enough: every byte in `80`–`BF` is a continuation, so *bytes minus continuations* is the number of characters. On one of your own files —

    ```bash
    f=yourfile; b=$(xxd -p "$f" | tr -d '\n' | grep -o -E '..' | wc -l | sed 's/^ *//'); c=$(xxd -p "$f" | tr -d '\n' | grep -o -E '..' | grep -c -E '^[89ab]'); echo "$b bytes, $c continuations, $((b - c)) characters"
    ```

    Then check it against a decoder: `python3 -c "d=open('yourfile','rb').read(); print(len(d), len(d.decode()))"`. The two numbers should match, and the `[89ab]` in that pipeline is `80`–`BF` written as a first hex digit.
4. **Cut one of your own files in the middle.** `tail -c +N yourfile | head -c 20 | xxd`, choosing an `N` that lands inside a multi-byte character — `iconv -f UTF-8 -t UTF-8` on that tail will exit 1, because it starts on a continuation byte. Now find the first byte that is *not* in `80`–`BF`, call its offset `M`, and run the validator again from there: `tail -c +M yourfile | iconv -f UTF-8 -t UTF-8 >/dev/null; echo $?`. That is the resync, done by hand on a file you own.
5. **Ask your own language the two questions.** Whatever you write in daily, find the two lengths — bytes and code points — for one non-ASCII string. If the language gives you only one number, you have just learned which one it thinks a character is.

## Practice

**Four sequences, and one that is not a character.** Before you run anything, write down the UTF-8 bytes for these four code points using the five steps above:

```text
U+00E9    U+017C    U+20AC    U+1F600
```

Then the one that matters: put `U+D800` through the same arithmetic. It is a three-byte number, the template takes it without complaint, and you will get an answer. Say what the answer is — and then say why it is not UTF-8.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:utf8_by_hand_kata_sh -->
*Verified output of [`utf8_by_hand_kata_sh.sh`](examples/utf8_by_hand_kata_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE FOUR SEQUENCES

   Pad the number to the payload width, cut at the slot boundaries, put
   the markers in front. Every line below is bash arithmetic -- the only
   thing an encoder is asked is the last column, and only for the fifth.

   U+00E9
      padded to 11 slots   00011101001
      the bytes            11000011 10101001
      in hex               c3a9   and it shows as  é
   U+017C
      padded to 11 slots   00101111100
      the bytes            11000101 10111100
      in hex               c5bc   and it shows as  ż
   U+20AC
      padded to 16 slots   0010000010101100
      the bytes            11100010 10000010 10101100
      in hex               e282ac   and it shows as  €
   U+1F600
      padded to 21 slots   000011111011000000000
      the bytes            11110000 10011111 10011000 10000000
      in hex               f09f9880   and it shows as  😀

   C3 A9   C5 BC   E2 82 AC   F0 9F 98 80
   Two, two, three, four -- and the byte count came from where the number
   sits on the number line, not from the alphabet the letter belongs to.

AND THE FIFTH, WHICH IS THE POINT OF THE KATA

   U+D800 goes through the same arithmetic without complaint:
      padded to 16 slots   1101100000000000
      the bytes            11101101 10100000 10000000
      in hex               eda080

      iconv says           exit 1   refused

   The templates are a recipe and a rule, and here they part company. The
   recipe produces ED A0 80; the rule -- Table 3-7's ED row, whose second
   byte stops at 9F instead of BF -- forbids it. U+D800 is a surrogate:
   one half of the pair UTF-16 uses to reach above U+FFFF, and not a
   character at all, so no UTF-8 sequence is allowed to mean it.

   That cap is the 2,048-number hole the lesson's exhaustion walks past:
   0x110000 - 2048 = 1112064, and every one of those has bytes while
   these 2,048 do not. If your pencil answered ED A0 80, the arithmetic
   was right and the answer is still no.
```
<!-- /output -->

</details>

## See also

- [Validation is a boundary](../validation_is_a_boundary/README.md) — the same templates read as a check, and what is left of that check downstream
- [Overlong sequences](../overlong_sequences/README.md) — the padded second spellings the templates allow and the rule forbids, and the 2001 worm that came of it
- [UTF-16 and surrogates](../utf16_and_surrogates/README.md) — where the 2,048-number hole and the `U+10FFFF` ceiling come from
- [Why UTF-8 won](../../09_History/why_utf8_won/README.md) — the six properties this mechanism buys, and the bill it pays for them
- [Unicode code points](../../02_Characters/unicode_code_points/README.md) — the numbers this page turns into bytes
- [An encoding is four layers](../the_encoding_model/README.md) — where the templates above sit in the standard's own stack, and why `UTF-16` and `UTF-16LE` name different layers
- [Mojibake](../mojibake/README.md) — what a hex dump looks like when the bytes were right and the table was wrong
- [The table has a version](../../02_Characters/the_table_has_a_version/README.md) — which Unicode facts go stale, and why none of this page's do
- [Table 3-7, *Well-Formed UTF-8 Byte Sequences* ↗](https://www.unicode.org/versions/latest/core-spec/chapter-3/) — the standard's own statement of the rule, four pages into chapter 3
- [RFC 3629 ↗](https://www.rfc-editor.org/rfc/rfc3629) — UTF-8 in nine pages, including the 2003 cap at `U+10FFFF`
