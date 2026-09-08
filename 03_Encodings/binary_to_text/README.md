# Binary to text

**Level:** 201 · for interface work

**One line:** Base64 does not encode text and has no charset — it re-cuts a run of *bits* into pieces small enough that every piece has a printable character to stand for it, and the only question that separates the whole family is how big a piece the scheme can cut.

## The channel will not carry your bytes, so stop sending bytes

There are places in a stack that accept only printable ASCII: an email body from before SMTP was eight-bit clean, a JSON string, a `<textarea>`, a QR code, a Usenet article, a PEM certificate, a database column somebody typed as `VARCHAR`. Handing one of those an arbitrary byte — a `0x00`, a `0x1B`, a lone `0xFF` — gets it dropped, rewritten, or interpreted as a command.

A **binary-to-text encoding** is the standard answer: rewrite the entire byte stream in an alphabet the channel is guaranteed to survive, and rewrite it back at the far end. [Base64 ↗](https://www.rfc-editor.org/rfc/rfc4648#section-4) is the one everybody meets, but the family is large and all of it is the same idea at different widths.

This is the neighbour of [escaping into ASCII](../escaping_into_ascii/README.md) and the two are easy to confuse. An **escape** works on text that is already text and rewrites only the characters the channel objects to — `%C5` here, `ż` there — leaving the rest legible. A **binary-to-text encoding** consumes the whole input, legible or not, and produces something unreadable in exchange for a guarantee: *every* byte survives. Use an escape when the payload is text and you want it to still look like text; use an encoding when the payload is a PNG.

## Three bytes in, four characters out

The mechanism is one sentence long. Twenty-four bits — three bytes — are re-cut into four groups of six, and each group is a number from 0 to 63 that indexes a 64-character alphabet. `2**6 == 64`, and there are comfortably more than 64 safe printable ASCII characters to spend, so the trick fits.

Here is `café`, five bytes of UTF-8, done by hand:

```text
quantum 1: 63 61 66
  01100011 01100001 01100110    the bytes in binary
  011000 110110 000101 100110   the same 24 bits, re-cut into sixes
      24     54      5     38   each six bits as a number, 0-63
       Y      2      F      m   ALPHABET[n]
```

Nothing in that looked at a character. It looked at bits. That is the whole encoder, and the [C view](#the-c-view) below is the same six lines with the shifts made explicit.

Two facts fall straight out of it. Four characters per three bytes is **4/3**, so base64 always costs exactly 33% more — the "75% efficiency" you will see quoted is the same number upside down, six bits carried for every eight sent. And the output length depends only on the *input length*, so a decoder can size its buffer before it reads anything.

## `=` is the length, written down

Five bytes is not a whole number of quanta. The last group is zero-filled to 24 bits, encoded, and then the characters that carry no real data are replaced by `=` — one `=` means the last quantum held two bytes, two means it held one. The padding is not a separator and carries nothing; it restates a length.

Which is why it is droppable when the length is known some other way. A [JWT ↗](https://www.rfc-editor.org/rfc/rfc7515#section-2) is three base64url fields split on `.`, so the boundaries are already visible and the spec tells you to strip it — and putting it back is the first line of every JWT library:

```python
s + "=" * (-len(s) % 4)   # b64decode wants a multiple of four
```

## Base64 has no charset, and this is the bug you will actually hit

Base64 encodes **bytes**. It was never told what text they were, it cannot tell you afterwards, and it does not care whether they were text at all.

So `café` has more than one base64 spelling, and both are perfectly valid:

| the bytes | base64 |
|---|---|
| `63 61 66 c3 a9` — UTF-8 | `Y2Fmw6k=` |
| `63 61 66 e9` — Latin-1 | `Y2Fm6Q==` |

An interface agreement that says *"the field is base64"* has not said enough, in exactly the way [percent-encoding](../escaping_into_ascii/README.md) does not say enough one layer down. The sentence that finishes it is *"base64 of the UTF-8 bytes"*. Without it, the receiver decodes to bytes and then has to guess — and the guess fails silently, because `63 61 66 e9` is not valid UTF-8 at all and `Y2Fm6Q==` looks exactly as respectable as the other one.

The corollary is a habit worth keeping: **decode, then validate.** Base64 decoding always succeeds on well-formed input, so it proves nothing about what came out. The [UTF-8 check is a separate step](../validation_is_a_boundary/README.md), and a pipeline that never takes it ships whatever it was handed.

## Two spellings, one payload

Base64 is **not canonical**: decode is many-to-one.

One byte needs 8 bits; two base64 characters carry 12. The four left over are defined to be zero and nothing in a normal decoder makes them be — so `QQ==`, `QR==`, `QS==` … `Qf==`, sixteen distinct strings, all decode to the single byte `0x41`. Python's `validate=True` does **not** help: it validates the alphabet, not the arithmetic, and returns `b'A'` for all sixteen.

That matters wherever base64 text is *compared* rather than decoded — a signature computed over the encoded form, a cache key, a deduplication table, an allow-list of known-good blobs. The rule is one line: **compare the bytes you decoded, never the string.** If you must know a string is canonical, re-encode what you decoded and require the two to match.

## The line the reference tables do not draw

Every scheme so far cut the bits into equal pieces, because the base was a power of two and a whole number of bits fits:

| scheme | bits per character | quantum | `café` |
|---|---|---|---|
| Base16 (hex) | 4 | 1 byte → 2 chars | `636166C3A9` |
| Base32 | 5 | 5 bytes → 8 chars | `MNQWNQ5J` |
| Base64 | 6 | 3 bytes → 4 chars | `Y2Fmw6k=` |
| Ascii85 | ~6.4 | 4 bytes → 5 chars | `@prueW;` |

Ascii85 is the interesting near-miss: 85 is not a power of two, but `85**5` just exceeds `256**4`, so four bytes still fit in five characters and the quantum survives.

**Base58, Base62 and Base36 have no quantum at all.** No group size works, so the encoder reads the entire input as one enormous integer and divides it down. That is not a slightly different efficiency — it is a different algorithm, with three consequences no percentage can express:

- **No streaming and no seeking.** You cannot start before the last byte arrives, cannot decode the front without the back, and cannot predict the output length.
- **Quadratic arithmetic.** Doubling the input roughly quadruples the work, which is why nobody base58s a file.
- **Leading zero bytes vanish.** `00 00 41` and `41` are the same integer, so they are the same base58 string. Base58Check patches this outside the maths, writing one `1` per leading zero byte.

And the reason to accept all that is never density — it is **people**. Base58 exists because it drops `0`, `O`, `I` and `l`, so a bitcoin address survives being read off a screen and typed back in; [Bech32 ↗](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki) goes further and adds a checksum that locates up to six mistyped characters. Those alphabets are chosen against human error, not against bandwidth.

So the question that actually sorts this family is: **does the base divide a power of two?** One side is a re-cutting of bits that runs in one pass; the other is arbitrary-precision division over the whole message, bought deliberately to make the result transcribable. Answer that first, and the alphabet is a detail.

## What it does not buy

Base64 is not encryption, not obfuscation and not a checksum. It is a public, reversible rewriting with no key and no error detection, and `aHVudGVyMg==` is `hunter2` to anyone who has ever seen the alphabet. If the reason for it is "so it is not readable in the log", the reason is wrong.

It is also worth doing in the right order: **compress, then encode.** gzip works on the bytes, and once they are base64 the repeats it hunts for have been smeared across a four-character period. Measured on the small CSV in the Python run — 5,075 bytes, zlib 1.2.12 on macOS and 1.3.1 on Linux, both giving the same answer on 2026-09-06 — gzip-then-base64 is 1,568 bytes and base64-then-gzip is 1,653, about 5% worse. The gap is not dramatic and on a badly-compressing payload it can vanish, so measure yours; the ordering is the part that generalises. (Those two byte counts are the output of whichever zlib the machine was built against, which is why they are written here and not in an answer key.)

## In Python

<!-- output:binary_to_text_py -->
*Verified output of [`binary_to_text_py.py`](examples/binary_to_text_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. TWENTY-FOUR BITS IN, FOUR CHARACTERS OUT
------------------------------------------------------------------------
   the text               'café'   4 characters
   its UTF-8 bytes        63 61 66 c3 a9   5 bytes

   quantum 1: 63 61 66
     01100011 01100001 01100110    the bytes in binary
     011000 110110 000101 100110   the same 24 bits, re-cut into sixes
         24     54      5     38   each six bits as a number, 0-63
          Y      2      F      m   ALPHABET[n], then padding

   quantum 2: c3 a9   (short)
     11000011 10101001 00000000    the bytes in binary
     110000 111010 100100 000000   the same 24 bits, re-cut into sixes
         48     58     36      0   each six bits as a number, 0-63
          w      6      k      =   ALPHABET[n], then padding

   by hand                Y2Fmw6k=
   base64.b64encode       Y2Fmw6k=
   the same string?       True

   Nothing above looked at a character. It looked at bits, in groups
   of six, because 2**6 == 64 and there are more than 64 printable
   ASCII characters to spend. That is the entire mechanism, and every
   other scheme in the family is the same trick at a different width.

2. SO BASE64 HAS NO CHARSET -- IT ENCODES BYTES
------------------------------------------------------------------------
   'café' as utf-8       63 61 66 c3 a9   -> Y2Fmw6k=
   'café' as iso-8859-1  63 61 66 e9      -> Y2Fm6Q==

   One word, two byte strings, two base64 strings, both perfectly
   valid and neither carrying the faintest hint of which is which.
   "base64 of this text" is not defined until somebody says which
   encoding made the bytes -- the same missing statement that makes
   percent-encoding guessable, one layer down.

   And it never fails. Encode anything, including bytes that are not
   text at all:
     c3 28 ff         -> wyj/      (not valid UTF-8, encodes fine)
     the same bytes .decode('utf-8') -> UnicodeDecodeError: invalid continuation byte

3. PADDING IS THE LENGTH, WRITTEN DOWN
------------------------------------------------------------------------
   bytes in  base64 out   chars  pads   4 * ceil(n/3)
          1  YQ==             4     2              4
          2  YWE=             4     1              4
          3  YWFh             4     0              4
          4  YWFhYQ==         8     2              8
          5  YWFhYWE=         8     1              8
          6  YWFhYWFh         8     0              8
          7  YWFhYWFhYQ==    12     2             12

   The output length depends only on the input length, so a decoder
   can size its buffer before reading a byte. The '=' is not a
   separator and carries no data: it says how many of the last
   quantum's bytes were real -- one '=' means two, two means one.

   Which is why the padding is droppable when the length is known
   another way. A JWT is three base64url fields split on '.', so the
   lengths are already there and RFC 7515 tells you to strip it:
     with padding         eyJhbGciOiJub25lIn0=
     as a JWT sends it    eyJhbGciOiJub25lIn0
   Python will not decode the stripped form -- b64decode wants a
   multiple of four -- so putting the padding back is the first line
   of every JWT library:
     b64decode(stripped)          -> binascii.Error: Incorrect padding
     s + '=' * (-len(s) % 4)      -> b'{"alg":"none"}'

4. TWO SPELLINGS, ONE PAYLOAD -- AND validate=True DOES NOT CARE
------------------------------------------------------------------------
   One byte, 0x41, needs 8 bits. Two base64 characters carry 12.
   The 4 bits left over are supposed to be zero, and nothing in the
   decoder makes them be:

   canonical      QQ==  -> b'A'
   also decodes   QR==  -> b'A'
   and so does    Qf==  -> b'A'
   distinct spellings of that one byte:   16

   validate=True sounds like the fix. It is not -- it validates the
   ALPHABET, not the arithmetic:
     b64decode('QR==', validate=True) -> b'A'
     b64decode('SGVs bG8=', validate=True) -> binascii.Error: Only base64 data is allowed
     b64decode('SGVs bG8=')                -> b'Hello'   (space skipped)

   So base64 is NOT canonical: decode is many-to-one. Any check that
   compares the TEXT -- a signature over the encoded form, a cache
   key, a deduplication table, an allow-list -- can be defeated by
   respelling it. Compare the bytes you decoded, never the string.
   The only way to know a string is canonical is to re-encode what
   you decoded and require the two to match:
     QQ== -> decode -> encode -> QQ==   canonical: True
     QR== -> decode -> encode -> QQ==   canonical: False

5. THE LINE THE TABLES DO NOT DRAW: DOES THE BASE DIVIDE A POWER OF TWO?
------------------------------------------------------------------------
   Every scheme so far cut the bits into equal pieces, because 64,
   32 and 16 are powers of two and a whole number of bits fits:

   scheme     bits/char   quantum              café ->
   Base16             4   1 byte  -> 2 chars   636166C3A9
   Base32             5   5 bytes -> 8 chars   MNQWNQ5J
   Base64             6   3 bytes -> 4 chars   Y2Fmw6k=
   Ascii85         ~6.4   4 bytes -> 5 chars   @prueW;

   Ascii85 is the odd one: 85 is not a power of two, but 85**5 just
   exceeds 256**4, so it still has a fixed quantum -- four bytes in,
   five characters out, a base-85 number per group.

   Base58 and Base62 have no quantum at all. There is no group size
   that works, so the encoder reads the WHOLE input as one enormous
   integer and divides it down. Three consequences follow, and none
   of them is an efficiency percentage:

   base58 of café             CDK2VUL
     (a) You cannot start until the last byte has arrived, and you
         cannot decode the front without the back: no streaming, no
         seeking, no fixed output length.
     (b) The arithmetic is quadratic. Doubling the input roughly
         quadruples the work, which is why nobody base58s a file.
     (c) A leading zero byte is not a digit, it is nothing:
         00 00 41   -> int 65   -> base58 '28'   (two leading zeros)
         41         -> int 65   -> base58 '28'   (no leading zeros)
         Base58Check patches this by hand, writing one '1' per
         leading zero byte -- a rule bolted on outside the maths.

   That is the split worth carrying: a power-of-two base is a
   re-cutting of bits and runs in one pass; anything else is
   arbitrary-precision division over the whole message. The two are
   not neighbours on a scale of efficiency. They are different
   algorithms, and the choice is made for humans -- Base58 drops
   '0OIl' so a person can copy an address off a screen.

6. WHAT IT COSTS, AND THE ORDER TO DO IT IN
------------------------------------------------------------------------
   the payload (a small CSV)         5075 bytes
   base64 of it                      6768 bytes   1.33x

   Four characters per three bytes is 4/3, so base64 costs 33% more
   and always exactly that -- the '75% efficiency' in the reference
   tables is the same number upside down (6 bits carried per 8 sent).
   That number is arithmetic on the length, which is why it is
   printed above and the next two are not.

   Now compress as well, both ways round:
     smaller                gzip, then base64
     the other one is       about 5% bigger
     both are under         40% of the raw payload

   The two byte counts themselves are deliberately not recorded
   here: they are the output of whichever zlib the machine was
   built against, so they belong in a dated line on the page and
   not in an answer key. The ORDER is the lesson, and it is stable.

   Compress first. gzip works on the bytes; once they are base64 the
   repeats it looks for have been smeared across a 4-character
   period and it recovers fewer of them. The gap is not enormous
   here, and on a payload that compresses badly it can vanish or
   invert -- so measure yours rather than quoting the rule.

   And the thing base64 does not buy, which is worth saying out
   loud because a decade of code review says otherwise:
     b64decode('aHVudGVyMg==') -> b'hunter2'
   It is not encryption, it is not obfuscation, and it is not a
   checksum. It is a public, reversible rewriting whose only job is
   to survive a channel that will not carry arbitrary bytes.
   crc32 of the payload, for contrast: 0x39a4b3a2 -- that one detects damage.
```
<!-- /output -->

## In the terminal

The `base64` command is one of the least portable tools in this library, which is a surprise given how simple its job is. Everything the script below *runs* is byte-identical on both platforms; everything in this table is not, measured 2026-09-06 on macOS 26.6.2 and GNU coreutils 9.7:

| | macOS (BSD) | GNU coreutils |
|---|---|---|
| default line wrapping | none — one long line | wraps at **76** |
| flag that sets the width | `-b N` | `-w N` |
| `-i` means | **input file** | **ignore garbage** |
| decode flags | `-d`, `-D`, `--decode` | `-d`, `--decode` (`-D` is an error) |
| a space inside the payload | decoded straight through, **exit 0** | partial output, `invalid input`, **exit 1** |
| `base32`, `basenc` | not in the base system | present |

Two of those rows are worth pausing on. The wrapping difference means `base64 file > out.txt` writes a **different file** on the two platforms, so it can never be an answer key and should never be diffed across machines. And the last-but-one row is the [`grep`](../../11_Tools/grep/README.md) failure shape again: the same damaged input is silently repaired by one build and correctly rejected by the other, so a script that "works" on a laptop can start rejecting production data on a Linux host — or, far worse, the other way round. Newlines *inside* the payload are fine everywhere; nothing else is.

<!-- output:binary_to_text_sh -->
*Verified output of [`binary_to_text_sh.sh`](examples/binary_to_text_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE ROUND TRIP
------------------------------------------------------------------------

   the text                 café
   base64                   Y2Fmw6k=
   base64 | --decode        café

   --decode is the spelling to use. -d works on both builds too;
   -D is macOS only and GNU rejects it outright, which is the good
   kind of incompatibility -- the script stops instead of guessing.

2. base64 IS THE HEX DUMP, RE-CUT
------------------------------------------------------------------------

   xxd -p     (4 bits/char) 636166c3a9
   base64     (6 bits/char) Y2Fmw6k=
   bytes in                 5
   hex chars out            10
   base64 chars out         8

   Same five bytes, two widths. Hex spends a character on every four
   bits and doubles the size; base64 spends one on every six and adds
   a third. Neither has looked at a character in the text -- xxd and
   base64 are both reading the same five bytes off the same pipe.

3. ONE WORD, TWO CHARSETS, TWO BASE64 STRINGS
------------------------------------------------------------------------

   as utf-8                 Y2Fmw6k=
   as iso-8859-1            Y2Fm6Q==

   Both are valid base64 of a word spelled the same way, and nothing
   in either string says which encoding produced the bytes. That is
   not a flaw in base64: base64 was never told. If an interface
   agreement says "the field is base64", it has not said enough.

4. NEWLINES INSIDE THE PAYLOAD ARE FINE -- ON BOTH BUILDS
------------------------------------------------------------------------

   Y2Fm\nw6k= --decode      café

   Line breaks are part of the deal: MIME wrapped base64 at 76
   characters and every decoder skips them. What is NOT portable is
   anything past that. A space in the middle of the payload is
   decoded straight through by the macOS build (exit 0) and rejected
   by GNU after partial output (exit 1); the default wrap width is
   none on macOS and 76 on GNU; the flag that sets it is -b on macOS
   and -w on GNU; and -i means "input file" on macOS and "ignore
   garbage" on GNU. See the table on the page.

5. DECODE, THEN VALIDATE -- TWO STEPS, NOT ONE
------------------------------------------------------------------------

   decoded bytes            636166c3a9
   valid UTF-8?             yes (iconv exit 0)
   and wyj/ ?               no (iconv exit 1)

   base64 --decode succeeded on both. It always does: c3 28 ff is a
   perfectly good run of bytes and base64 has no opinion about text.
   The question "is this UTF-8?" is asked by a second tool, after,
   and a pipeline that never asks it is a pipeline that ships
   whatever it was handed.
```
<!-- /output -->

## In Rust

<!-- output:binary_to_text_rs -->
*Verified output of [`binary_to_text_rs.rs`](examples/binary_to_text_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE OUTPUT IS A String, AND NOTHING CAN MAKE IT NOT BE
------------------------------------------------------------------------

   "café" as UTF-8            63 61 66 c3 a9 -> Y2Fmw6k=
   the same word in Latin-1   63 61 66 e9    -> Y2Fm6Q==
   not text at all            c3 28 ff       -> wyj/

   The third row is the one that matters. Those three bytes are
   not valid UTF-8 and never will be:
     String::from_utf8 -> Err(invalid utf-8 sequence of 1 bytes from index 0)
     encode(..)        -> "wyj/"   an infallible fn(&[u8]) -> String

   That signature IS the definition of a binary-to-text encoding.
   Anything that can hand back a `String` for every possible byte
   sequence, without a Result, is one; anything that can fail on
   some inputs is a text decoder wearing the wrong name.

2. THE INPUT IS &[u8], SO THERE IS NO CHARSET TO GET WRONG
------------------------------------------------------------------------

   "café".as_bytes()          63 61 66 c3 a9
   encode(that)               Y2Fmw6k=
   encode(Latin-1 bytes)      Y2Fm6Q==

   Rust makes the missing question visible at the call site: you
   cannot pass a `&str` to a function that wants `&[u8]` without
   writing `.as_bytes()`, which is the moment the encoding was
   chosen. In a language where the two are the same type, that
   moment does not appear in the source at all.

3. DECODING RETURNS Vec<u8>, BECAUSE THAT IS ALL IT KNOWS
------------------------------------------------------------------------

   Y2Fmw6k=   -> 63 61 66 c3 a9 valid UTF-8: "café"
   Y2Fm6Q==   -> 63 61 66 e9    not UTF-8: incomplete utf-8 byte sequence from index 3
   wyj/       -> c3 28 ff       not UTF-8: invalid utf-8 sequence of 1 bytes from index 0

   Three successful decodes, and only the first is UTF-8. The
   second is the SAME WORD in Latin-1 -- a base64 string a
   partner could hand you as `café`, decoding to bytes that
   are not valid text in the encoding you assumed. The third
   was never text at all. base64 could not tell you any of
   this, because base64 was never told; decode, then validate,
   the same two-step that any read from a file or socket is.

4. STRICT MEANS CHECKING THE BITS NOBODY CHECKS
------------------------------------------------------------------------

   QQ==     -> Ok(41)
   QR==     -> Err(non-canonical: the 16 unused bits are not zero)
   Qf==     -> Err(non-canonical: the 16 unused bits are not zero)
   QQ=      -> Err(length 3 is not a positive multiple of four)
   Q!==     -> Err('!' is not in the alphabet)

   QR== and Qf== are rejected HERE and accepted almost
   everywhere else -- Python, Go, Java and the shell tool all
   return 0x41 for them, because the bits the padding covers are
   read and discarded rather than checked. Sixteen spellings of
   one byte. The check that stops it is the four lines above.

   The rule that follows is short: compare decoded bytes, never
   the encoded string. A signature, a cache key or an allow-list
   over base64 TEXT is a comparison over a spelling, and the
   spelling is not unique.
```
<!-- /output -->

## The C view

<!-- output:binary_to_text_c -->
*Verified output of [`binary_to_text_c.c`](examples/binary_to_text_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE ACCUMULATOR, FOUR SHIFTS
------------------------------------------------------------------------

   the bytes      63 61 66 c3 a9   (5 bytes)

   group 1: 3 bytes
     v = 0x636166        the 24-bit accumulator
     (v >> 18) & 63 = 24 -> Y
     (v >> 12) & 63 = 54 -> 2
     (v >>  6) & 63 =  5 -> F
      v        & 63 = 38 -> m

   group 2: 2 bytes
     v = 0xc3a900        the 24-bit accumulator (zero-filled)
     (v >> 18) & 63 = 48 -> w
     (v >> 12) & 63 = 58 -> 6
     (v >>  6) & 63 = 36 -> k
      v        & 63 =  0 -> =   (dropped: '=' says so)

   encoded        Y2Fmw6k=

2. WHY THE SHIFTS ARE THE WHOLE STORY
------------------------------------------------------------------------

   There is no string type here, no encoding, no locale and no
   allocation. `unsigned char` in, ASCII out, and the only
   arithmetic is masking six bits at a time out of a number that
   was three bytes a moment ago.

   That is why base64 costs exactly 4/3: 5 bytes is 2 groups
   of 24 bits, and each group is spent on four characters whether
   it was full or not -- 8 characters out, 1 of them padding.

   Change 6 to 5 and the alphabet to 32 characters and this is
   Base32. Change it to 4 and 16 and it is a hex dump. The base
   is a parameter; the loop is the encoding.
```
<!-- /output -->

## The reference article, and what its table hides

The obvious place to look this up is Wikipedia's [Binary-to-text encoding ↗](https://en.wikipedia.org/wiki/Binary-to-text_encoding), and it is a poor place to learn it from. That is worth saying precisely rather than dismissively, because *why* it fails is itself the lesson.

It has carried an **original research** banner since April 2010 and a **more citations needed** banner since December 2012 — fourteen and sixteen years of notice that nobody has answered. Its centre of gravity is a sortable table of some twenty-five schemes whose widest column is *"Programming language implementations"*: a list of outbound links to third-party code, a good number of them now reachable only through the Internet Archive. That column is a directory, not an explanation, and it is the one the layout gives the most room to.

The column that does the damage is **"Efficiency"**. Sorting the family on one percentage puts Base58 (73.2%) tidily between Base56 and Base62, as though picking between them were a bandwidth trade — and buries the fact that Base16, Base32 and Base64 re-cut bits in one pass while Base58 and Base62 are big-integer division over the whole message. Those are not neighbours on a scale. A reader who sorts that column learns something false about the shape of the subject.

And the mechanism — three bytes, four characters, six bits at a time — appears in a single paragraph *below* the table, with no worked example anywhere on the page.

What the article gets right, and better than most sources, is the distinction this page opens with: an encoding consumes the whole input, an escape embeds inside text that is already text. That paragraph is worth keeping. For the rest, [RFC 4648 ↗](https://www.rfc-editor.org/rfc/rfc4648) is short, free, and definitive — it specifies Base16, Base32 and Base64 together, in that order, precisely because they are one idea at three widths.

## If you are coming from Python or ABAP

**Python.** `base64` is the module, and the three calls are `b64encode` / `b64decode` (which take and return **`bytes`**, so `.encode('utf-8')` on the way in and `.decode('utf-8')` on the way out — the two hops are where the charset gets named), `urlsafe_b64encode` / `urlsafe_b64decode` for the `-_` alphabet, and `b16`/`b32`/`b85`/`a85` for the rest of the family. Three habits: `validate=True` rejects stray characters but not non-canonical padding bits, so it is a smaller guarantee than it sounds; `binascii.Error: Incorrect padding` almost always means an unpadded JWT-style field, and the fix is the one-liner above, not a `try`/`except pass`; and for a hex dump reach for `bytes.hex()` / `bytes.fromhex()` rather than `b16encode`, which is the same encoding with an uppercase-only decoder. See [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md).

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* The trap is the same one the whole page is about, and ABAP puts it in the method names: `cl_http_utility=>encode_base64( )` takes a **`string`** and `encode_x_base64( )` takes an **`xstring`**. Only the second is the operation described here. The first has to turn your characters into bytes before it can encode them, using a code page you did not name at the call site — so the round trip through a system with a different setting is precisely the `Y2Fmw6k=` versus `Y2Fm6Q==` problem, arriving as a corrupted attachment rather than an error. Convert explicitly (`cl_abap_conv_codepage`, or `cl_abap_conv_out_ce` on older releases) to get an `xstring`, then encode that. `SCMS_BASE64_ENCODE_STR` and `SCMS_BASE64_DECODE_STR` are the function-module pair you will find in older code and they have the same distinction to make; check on your release what any of them do with a payload that is not text, and see [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) for whose job it is to name the encoding.

## Try it

```bash
cd 03_Encodings/binary_to_text/examples
python3 binary_to_text_py.py
bash binary_to_text_sh.sh
rustc --edition 2024 binary_to_text_rs.rs -o /tmp/btt && /tmp/btt
cc -std=c11 -Wall -Wextra binary_to_text_c.c -o /tmp/btt_c && /tmp/btt_c
```

Then, in one line each:

```bash
printf 'café' | base64                      # Y2Fmw6k=
printf 'café' | iconv -t ISO-8859-1 | base64 # Y2Fm6Q==  -- same word, different answer
echo 'QR==' | base64 --decode | xxd         # the byte 0x41, from a string that is not QQ==
```

Without the machine: a partner sends you a field they describe as "the customer name, base64". It decodes to five bytes ending `e9`. Say what has gone wrong, whose side it is on, and what one sentence you would add to the interface agreement so it cannot happen again.

## Practice

**Predict the lengths.** For the 5 bytes `b"cafe!"`, say how many characters base16, base32 and base64 each produce, and how many `=` characters appear — before running anything. The arithmetic is one question: how many bits does one symbol of each scheme carry?

Then say why base64 of these 5 bytes is 1.60x rather than the 1.333x everyone quotes, and at what input lengths it is exactly 4/3. Finish with the question that has no arithmetic in it: what charset does base64 use?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:binary_to_text_kata_py -->
*Verified output of [`binary_to_text_kata_py.py`](examples/binary_to_text_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
input   b'cafe!'   5 bytes = 40 bits

scheme         bits/symbol output              len  growth
base16 (hex)             4 6361666521           10   2.00x
base32                   5 MNQWMZJB              8   1.60x
base64                   6 Y2FmZSE=              8   1.60x
base85                ~6.4 V_{}xAp               7   1.40x

The growth is forced, not chosen: 8 bits of input have to be carried by
symbols worth 4, 5 or 6 bits, so the ratios are 8/4, 8/5 and 8/6 --
2x, 1.6x and 1.333x. Nothing is compressed and nothing is encrypted;
the bits are re-cut into smaller pieces.

Read the base64 row again, though: 1.60x, not 1.333x. Those ratios are
what you get on a WHOLE number of groups, and 5 bytes is not one --
base64's group is 3 bytes, so 5 bytes is two groups with the second one
mostly empty, and the padding is charged to the length. The ratio
arrives as the input grows:
       3 bytes ->     4 characters   1.333x
       5 bytes ->     8 characters   1.600x
      30 bytes ->    40 characters   1.333x
     300 bytes ->   400 characters   1.333x
    3000 bytes ->  4000 characters   1.333x
   Only the multiples of 3 sit exactly on 4/3. Everything else pays for
   a partial group, and on a short field that overhead is most of the
   difference between the schemes.

THE PADDING IS ARITHMETIC TOO
   1 byte(s) =  8 bits -> Yw==     2 '=' character(s)
   2 byte(s) = 16 bits -> Y2E=     1 '=' character(s)
   3 byte(s) = 24 bits -> Y2Fm     0 '=' character(s)
   base64's unit is 3 bytes (24 bits = four 6-bit symbols). An input
   that is not a multiple of 3 leaves a partial group, and '=' says how
   many bytes the last group really carried. It is a length statement,
   not data -- which is why some formats drop it and pass the length
   along some other way.

AND NONE OF IT IS ABOUT TEXT
   base64 of raw bytes: AP+A
   The input was not text and there was no charset anywhere. Base64
   takes bits. If you hand it a string you must encode that string
   first, and THAT step is where the charset lives -- which is why
   'base64 encoded' is never a complete description of a field.
```
<!-- /output -->

</details>

## See also

- [Escaping into ASCII](../escaping_into_ascii/README.md) — the other half of this pair: rewriting the characters a channel objects to, rather than all of them
- [Validation is a boundary](../validation_is_a_boundary/README.md) — the second step, after the decode that always succeeds
- [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) — Base16 under its usual name, and the first four-bit quantum you ever met
- [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) — what `xxd -p` was doing in the shell run
- [Mojibake](../mojibake/README.md) — what `Y2Fm6Q==` becomes when the receiver assumes UTF-8 and the sender meant Latin-1
- [Collisions by design](../../12_Adversarial/collisions_by_design/README.md) — the general shape of "two spellings, one payload"
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — where "base64 of the UTF-8 bytes" belongs in writing
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — `bytes.hex()` and the four conversions next door
