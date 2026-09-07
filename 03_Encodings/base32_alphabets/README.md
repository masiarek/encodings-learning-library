# The alphabet is not the encoding

**Level:** 201 · for interface work

**One line:** A converter's Base32 menu offers four entries and prints four different strings for one input, but three of them differ by nothing except which thirty-two symbols were used — while the fourth, Crockford's, is a notation for **numbers**, zero-extends the opposite end, and gives a different answer for any input that is not a whole number of five-bit pieces.

## The menu that started this

A converter offers Base32 (RFC 3548, RFC 4648) · Base32hex (RFC 4648) · z-base-32 · Crockford's Base32 · Custom, and prints, for `The quick brown fox jumps over the lazy dog.`:

```text
AHM6A83HENMP6TS0C9S6YXVE41K6YY10D9TPTW3K41QQCSBJ41T6GS90DHGQMY90CHQPEBG
```

Seventy-one characters. Pick a different entry from the same menu and seventy-one different characters come back. Nothing on screen says whether those are four encodings or four spellings of one, and the answer decides whether "we base32 the field" is a complete statement in an interface agreement.

It is four spellings of one — with an exception that is the real subject of this page.

## Two questions, and only one of them is about bits

[Binary to text](../binary_to_text/README.md) is about the first question: **how wide a piece** the scheme cuts the bits into. Four bits is base16, five is base32, six is base64, and the width fixes the cost — a byte becomes 2, 1.6 or 1.33 characters and there is nothing to decide.

This page is about the second: **which thirty-two symbols stand for the pieces, and in what order.** At width five the family has four published answers, and unlike the width question this one is not arithmetic. Each of the four was chosen by someone thinking about a person reading a code off a screen and typing it somewhere else, and the differences between them are consequences of that, not of the bits.

## Three of the four are one `tr`

The same five-bit pieces, written four ways:

| | the symbols, in order | value 0 is | value 26 is |
|---|---|---|---|
| **RFC 4648** base32 | `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` | `A` | `2` |
| **base32hex** (RFC 4648 §7) | `0123456789ABCDEFGHIJKLMNOPQRSTUV` | `0` | `Q` |
| **Crockford's** | `0123456789ABCDEFGHJKMNPQRSTVWXYZ` | `0` | `R` |
| **z-base-32** | `ybndrfg8ejkmcpqxot1uwisza345h769` | `y` | `s` |

Thirty-two in, thirty-two out, one for one. So the conversion between any two of them is a **character substitution** and nothing more — a `str.translate` in Python, a single `tr` in a shell pipe — and it is exactly reversible, because no bit moved. That is the test for whether two schemes are really the same encoding: if a 32-character `tr` converts between them, they are.

It also says what *cannot* be done that way. Base32 to base64 is not a `tr`, at any price, because those two cut the bits into different-sized pieces; the only route across is to decode back to bytes and encode again. **The alphabet is a rename. The packing is the encoding.**

## The order of the symbols is a feature

Look again at the value-26 column. Standard base32 writes 0 as `A` and 26 as `2`, and in ASCII `2` sorts **before** `A` — so the moment a five-bit piece crosses 26, the order of the encoded text stops matching the order of the bytes.

base32hex writes 0–31 as `0`–`9` then `A`–`V`, which is already ascending in ASCII, and RFC 4648 says in [§7 ↗](https://www.rfc-editor.org/rfc/rfc4648#section-7) that this is the point of it: *"encoded data maintains its sort order when the encoded data is compared bit-wise"*.

Tested over all 65,536 two-byte strings, base32hex preserves the order and standard base32 does not, first failing here:

```text
00 33  ->  AAZQ====
00 34  ->  AA2A====      but 0x0033 < 0x0034
```

That is worth a database index, a sorted log, or a range query — and it is invisible on any comparison table that ranks these schemes by bits per character. DNSSEC's NSEC3 records are the standing example: [RFC 5155 ↗](https://www.rfc-editor.org/rfc/rfc5155) specifies *"the 'Base 32 Encoding with Extended Hex Alphabet' as specified in RFC4648"* and says why in the same document — *"this order is the same as the canonical DNS name order"* — so a resolver can walk the chain by comparing the text it already has.

**One caveat, and it is `sort`'s, not base32hex's.** RFC 4648's promise is about a **bit-wise** comparison. `sort` gives you that only in the C locale; in any other it applies the locale's collation, which is a different order and can put the same two strings the other way round. So the property survives a database index on a binary collation and a `LC_ALL=C sort`, and is not guaranteed by anything else — see [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md).

## Crockford's Base32 is a notation for numbers

Here the "just a rename" story stops being true, and the reason is in the first sentence of the [specification ↗](https://www.crockford.com/base32.html): *"Base 32 is a textual 32-symbol notation for expressing **numbers**"* — not byte strings. On a value that does not fill its last piece it says: *"zero-extend the number to make its bit-length a multiple of 5"*.

A number is zero-extended at the **high** end. RFC 4648 pads the **low** end of the last group. Same bits, opposite ends, so two bytes give two answers:

```text
b'Hi'  =  0x4869  =  0100100001101001

RFC 4648, pad the right    01001 00001 10100 10000    ->  91MG
Crockford, extend the left 00000 10010 00011 01001    ->  0J39
```

Both are honestly described as "Crockford's Base32 of those two bytes". A converter with an alphabet menu hands you the first, because it is renaming an RFC 4648 string it already had. [ULID ↗](https://github.com/ulid/spec), which says *"Crockford's Base32 is used"* for a 128-bit value in 26 characters, is built on the second.

The two readings agree exactly when there is nothing to extend — when the bit count is already a multiple of five, which for whole bytes means a **length divisible by 5**. The Python run checks that at every length from 1 to 15 (exhaustively at 1 and 2), and the pattern is clean: at a multiple of 5, every case agrees; otherwise the only string that agrees is the one made of zero bytes, where it makes no difference which end you extend.

So a three-byte value has no agreed Crockford spelling, and two libraries can both be right about it. If a format uses Crockford, it has to say which reading — and the honest way is to say what ULID says: a **number**, of a **declared width**.

**And a number has no leading zeros.** `00 00 41`, `00 41` and `41` are three different byte strings and one number, 65, so the number reading cannot round-trip a length. That is the other half of why ULID pins 26 characters: 26 × 5 = 130 bits for a 128-bit value, with the width declared rather than inferred.

## The letters that are missing

| | drops | the stated reason |
|---|---|---|
| Crockford's | `I` `L` `O` `U` | `I` and `L` read as `1`, `O` as `0`; `U` "to reduce the chance of accidental obscenity" |
| z-base-32 | `0` `l` `v` `2` | the same confusions, plus `v`/`u` and `2`/`z` |

z-base-32 then goes further and **permutes** what is left, so the symbols that turn up most often are the ones its author judged easiest to read, say and remember. Neither list is about bits. Both are about transcription by a human being, which is why these alphabets are the ones you find on recovery codes, licence keys and anything a support agent reads down a phone.

The standard alphabet made no such allowance, so its *decoders* have to. Python's has since the module was written:

```python
base64.b32decode("MNQX1===", casefold=True, map01=b"I")   # b'cat'
```

`map01` has to be *told* which letter a typed `1` meant, because in the standard alphabet `I` and `L` are both live symbols, worth 8 and 11, and the string does not say which was intended. Its default is `None` — the docs say *"For security purposes"* — so `0` and `1` are rejected outright unless you ask for the repair. A repair at the decoder is strictly weaker than an alphabet that cannot be mistyped.

And on base32hex the repair is not weaker but **impossible**, which is the clearest way to see that these are choices and not styles: `b32hexdecode` has no `map01` at all, because `0`, `1`, `I`, `L` and `O` are *all five* live symbols in the extended-hex alphabet, worth 0, 1, 18, 21 and 24. The alphabet that fixed the sorting problem re-introduced the transcription one.

**One caveat on z-base-32.** Its [specification ↗](https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt) is written over *bits*, not bytes: an encoder that knows the exact bit length may stop short of the byte boundary, which RFC 4648 has no equivalent for. Anything a tool prints for a byte string is its octet-mode reading, and in octet mode it is the plain rename it appears to be.

## The command is not there

`base64` is on every machine this library targets. `base32` is not, and neither is anything that speaks the other three alphabets.

| tool | macOS 26 | ubuntu:24.04 |
|---|---|---|
| `base64` | `/usr/bin/base64` (FreeBSD) | `/usr/bin/base64` (GNU coreutils) |
| `base32` | **absent** — no `/usr/bin/base32` | `/usr/bin/base32` (GNU coreutils) |
| `basenc` (does base32hex) | absent | present |
| anything for Crockford or z-base-32 | absent | absent |

*Measured 2026-09-07, extending the row [Binary to text](../binary_to_text/README.md) already records for the same two tools.* The part worth adding is **why it is easy to miss**: on the Mac the name `base32` resolved perfectly well — to Homebrew's GNU coreutils 9.11, shadowing an absence. A developer with coreutils installed cannot tell by typing the command, only by asking where it came from.

The failure is at least loud (`command not found`), unlike the five ways `base64` disagrees with itself across the two builds. But it is why the shell example below converts with `tr` over constants instead of calling an encoder — and `tr` is the better demonstration anyway, since a rename is exactly what it does.

## What this page does not cover

Two things that belong to the width question, not the alphabet question, and are worked through on [Binary to text](../binary_to_text/README.md): that **decode is many-to-one** — the unused bits of the last group are supposed to be zero but [RFC 4648 §3.5 ↗](https://www.rfc-editor.org/rfc/rfc4648#section-3.5) only says a decoder *"MAY chose to reject"* a string where they are not, so two different strings decode to the same bytes and comparing the encoded form is a bug; and that base58 and base62, which look like neighbours on a bits-per-character table, are big-integer division over the whole message rather than a re-cut, so they are not in this family at all. Crockford's number reading, above, is that same big-integer idea arriving inside a scheme that *is*.

## In Python

<!-- output:base32_alphabets_py -->
*Verified output of [`base32_alphabets_py.py`](examples/base32_alphabets_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SAME FORTY-FOUR BYTES, FOUR TIMES
------------------------------------------------------------------------
   the text           'The quick brown fox jumps over the lazy dog.'
   its bytes          44 = 352 bits, which is 70.4 five-bit pieces

   RFC 4648           KRUGKIDROVUWG2ZAMJZG653OEBTG66BANJ2W24DTEBXXMZLSEB2GQZJANRQXU6JAMRXWOLQ
   base32hex          AHK6A83HELKM6QP0C9P6UTRE41J6UU10D9QMQS3J41NNCPBI41Q6GP90DHGNKU90CHNMEBG
   Crockford          AHM6A83HENMP6TS0C9S6YXVE41K6YY10D9TPTW3K41QQCSBJ41T6GS90DHGQMY90CHQPEBG
   z-base-32          ktwgkedtqiwsg43ycj3g675qrbug66bypj4s4hdurbzzc3m1rb4go3jyptozw6jyctzsqmo

   Four strings of 71 characters, no two alike, one input. A dropdown
   that offers all four calls them all Base32, and a reader is left to
   assume they are four encodings. They are one encoding written in
   four alphabets, and the four differ in nothing else -- with one
   caveat and one outright exception, in sections 6 and 4.

   The caveat is z-base-32. Its specification is written over BITS,
   not bytes: an encoder that knows the exact bit length may stop
   short. The line above is its octet-mode reading, which is the one
   a tool handed a byte string can give -- and in octet mode it is
   exactly the rename it looks like.

   padded             KRUGKIDROVUWG2ZAMJZG653OEBTG66BANJ2W24DTEBXXMZLSEB2GQZJANRQXU6JAMRXWOLQ=   72 characters
   unpadded           KRUGKIDROVUWG2ZAMJZG653OEBTG66BANJ2W24DTEBXXMZLSEB2GQZJANRQXU6JAMRXWOLQ   71 characters

   RFC 4648 pads to a multiple of 8 characters; Crockford and z-base-32
   define no padding at all. So the '=' is a fifth difference, and the
   character count alone -- 71, not 72 -- tells you the padding is off.

2. THREE OF THE FOUR ARE ONE str.translate AWAY
------------------------------------------------------------------------
   RFC 4648 of b'cat'                 MNQXI
   .translate(RFC -> base32hex)       CDGN8
   .translate(RFC -> Crockford)       CDGQ8
   .translate(RFC -> z-base-32)       cpoze

   and straight back again            MNQXI   recovered: True

   A rename is invertible and loses nothing, because no bit moved. The
   bytes were cut into five-bit pieces once; each scheme then writes
   the SAME pieces with a different set of thirty-two symbols. That is
   why one `tr` in a shell pipe converts between them -- see the
   terminal section on the page.

3. THE ORDER OF THE THIRTY-TWO SYMBOLS IS A FEATURE, NOT A STYLE
------------------------------------------------------------------------
   RFC 4648 gives a reason for base32hex, and it is a property of the
   ordering alone: 'encoded data maintains its sort order when the
   encoded data is compared bit-wise' (section 7).

   Tested over every two-byte string -- all 65,536 of them:

   sorting the base32 text == sorting the bytes     False
   sorting the base32hex text == sorting the bytes  True

   the first place standard base32 gets it wrong:
     0033     -> AAZQ====
     0034     -> AA2A====      but 0033 < 0034

   The cause is ASCII, not base32. Standard base32 spells value 0 as
   'A' and value 26 as '2', and '2' sorts BEFORE 'A', so the text order
   and the byte order disagree the moment a value crosses 26.
   base32hex spells 0..31 as 0-9 then A-V, which is already ascending
   in ASCII, so the two orders can never disagree.

   That is worth a database index, and it is invisible on any table
   that lists these schemes by bits-per-character.

4. CROCKFORD'S BASE32 IS A NOTATION FOR NUMBERS
------------------------------------------------------------------------
   Its specification opens: 'Base 32 is a textual 32-symbol notation
   for expressing NUMBERS' -- not byte strings. And on a short value it
   says: 'zero-extend the number to make its bit-length a multiple of
   5'. A number is zero-extended at the HIGH end. RFC 4648 pads the
   LOW end of the last group. Same bits, opposite ends.

   the bytes                b'Hi'  =  4869  =  0100100001101001
   RFC 4648: pad the right  01001 00001 10100 10000   -> 91MG
   Crockford: extend left   00000 10010 00011 01001    -> 0J39

   Two strings. Both are 'Crockford's Base32 of these two bytes'. A
   converter that shows you an alphabet dropdown gives you the first;
   ULID, which specifies Crockford's Base32 for a 128-bit number,
   is built on the second.

   The two readings agree exactly when there is nothing to extend --
   when the bit count is already a multiple of 5, i.e. when the byte
   count is a multiple of 5. Checked, by length:

    bytes  % 5   tested   agreed   verdict
        1    1      256        1   only the all-zero string
        2    2    65536        1   only the all-zero string
        3    3      125        1   only the all-zero string
        4    4      625        1   only the all-zero string
        5    0     3125     3125   all of them
        6    1     5209        1   only the all-zero string
        7    2     4112        1   only the all-zero string
        8    3     4112        1   only the all-zero string
        9    4     4104        1   only the all-zero string
       10    0     4097     4097   all of them
       11    1     4097        1   only the all-zero string
       12    2     4097        1   only the all-zero string
       13    3     4097        1   only the all-zero string
       14    4     4097        1   only the all-zero string
       15    0     4097     4097   all of them

   Lengths 1 and 2 are exhaustive -- every one of the 256 and the
   65,536; the rest sweep a fixed five-byte symbol set. The pattern is
   not a sample artefact, it is the arithmetic above: a value that is
   not a whole number of five-bit pieces has no agreed spelling, and
   the one string that survives every length is the one made of
   zeros, where it makes no difference which end you extend.

5. AND A NUMBER HAS NO LEADING ZEROS
------------------------------------------------------------------------
   000041     chunks 00042    as a number 21
   0041       chunks 010G     as a number 21
   41         chunks 84       as a number 21

   Three different byte strings; one number, 65. The chunked reading
   keeps the length because it is encoding BYTES; the number reading
   cannot, because 065 and 65 are the same number. Any format that
   uses the number reading has to declare a width, and ULID does:

   ULID                   128 bits, canonically 26 characters
   26 x 5                 130 bits -- 2 more than the value has
   its two fields         48-bit time in 10 chars (50 bits), 80-bit random in 16 (80 bits)

   80 is a multiple of 5 and 48 is not, which is why only the
   timestamp half needs the zero-extension at all.

6. WHICH LETTERS ARE MISSING, AND WHAT A DECODER DOES ABOUT IT
------------------------------------------------------------------------
   Crockford    drops I L O U
   z-base-32    drops 0 2 l v

   Crockford's reasons are I and L looking like 1, O looking like 0,
   and U 'to reduce the chance of accidental obscenity'. z-base-32
   drops a different four (0, l, v, 2) and then PERMUTES the rest, so
   that the symbols a person meets most often are the ones easiest to
   read and say. Neither list is about bits. Both are about a human
   reading a code off a screen and typing it somewhere else.

   The standard alphabet made no such allowance, so its decoders have
   to. Python's has carried the repair since the module was written:

   b32encode(b'cat')                            MNQXI===
   lower case, casefold=True                    b'cat'
   someone typed 1 for I and 0 for O            MNQX1===
   b32decode(..., casefold=True, map01=b'I')    b'cat'

   map01 has to be told which letter the digit 1 meant, because in the
   standard alphabet both I and L are live symbols with different
   values -- the ambiguity Crockford's alphabet removes by not having
   them. A repair at the decoder is a strictly weaker fix than an
   alphabet that cannot be mistyped.
```
<!-- /output -->

## In the terminal

<!-- output:base32_alphabets_sh -->
*Verified output of [`base32_alphabets_sh.sh`](examples/base32_alphabets_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE COMMAND YOU CANNOT ASSUME IS THERE
------------------------------------------------------------------------

   macOS 26 ships /usr/bin/base64 -- the FreeBSD one -- and there is
   no /usr/bin/base32 beside it. On the machine this was measured the
   name `base32` resolved to Homebrew's GNU coreutils 9.11 instead.
   ubuntu:24.04 has both, out of the one coreutils package.

   So a pipeline that reaches for base32 runs on a developer's Mac and
   on CI and fails on a colleague's -- with `command not found`, which
   at least stops rather than guessing. base32hex, Crockford and
   z-base-32 have no command on either platform: GNU's `basenc` covers
   base32hex, and nothing at all covers the other two.

   That is why the rest of this script is tr.

2. A RENAME IS ONE tr
------------------------------------------------------------------------

   RFC 4648     KRUGKIDROVUWG2ZAMJZG653OEBTG66BANJ2W24DTEBXXMZLSEB2GQZJANRQXU6JAMRXWOLQ
   base32hex    AHK6A83HELKM6QP0C9P6UTRE41J6UU10D9QMQS3J41NNCPBI41Q6GP90DHGNKU90CHNMEBG
   Crockford    AHM6A83HENMP6TS0C9S6YXVE41K6YY10D9TPTW3K41QQCSBJ41T6GS90DHGQMY90CHQPEBG
   z-base-32    ktwgkedtqiwsg43ycj3g675qrbug66bypj4s4hdurbzzc3m1rb4go3jyptozw6jyctzsqmo

   and back     KRUGKIDROVUWG2ZAMJZG653OEBTG66BANJ2W24DTEBXXMZLSEB2GQZJANRQXU6JAMRXWOLQ

   Four names for one encoding. Each tr is 32 characters in and 32
   out, one for one, so no bit has moved and the round trip is exact.
   Compare that with converting base32 to base64, which cannot be a
   tr at all: those two cut the bits into different-sized pieces, so
   the only way across is to decode to bytes and encode again.

3. THE SAME FOUR VALUES, SORTED TWICE
------------------------------------------------------------------------

   bytes      base32       base32hex
   0011       AAIQ====     008G====
   0033       AAZQ====     00PG====
   0034       AA2A====     00Q0====
   00ff       AD7Q====     03VG====

   sorted as base32 text:     AA2A==== AAIQ==== AAZQ==== AD7Q====
   sorted as base32hex text:  008G==== 00PG==== 00Q0==== 03VG====

   Read the first list against the table: sorting the base32 text
   puts 0034 first and 0011 second, scrambling four values that were
   already in order. The base32hex list is still in byte order, and
   RFC 4648 section 7 says that is the whole reason base32hex exists.

   The '=' padding sorts too, which is a second reason a base32 string
   makes a poor sort key: it is shorter than the alphabet question and
   just as easy to miss.

4. WHAT tr CANNOT DO
------------------------------------------------------------------------

   a Crockford typo             AHM6A83HENMP6TS0
   the same, misread by eye     AHM6A83HENMP6TSO

   The last character is the letter O where the data had the digit 0.
   Crockford's alphabet has no O, so a decoder is entitled to repair
   it -- and tr can do exactly that, one substitution:

   tr 'IiLlOo' '111100'         AHM6A83HENMP6TS0

   That repair is only available because the alphabet left those
   letters out. Run the same tr over an RFC 4648 string and it
   destroys it: I, L and O are all live symbols there, standing for
   8, 11 and 14, and nothing in the string says which was meant.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** `base64.b32encode` / `b32decode` are RFC 4648, and `b32hexencode` / `b32hexdecode` (3.10 and later) are the sorting variant — note that the *decoders* take the alphabet as a different function, not as a flag, so switching alphabets is a call-site change and grep can find it. For Crockford or z-base-32 there is nothing in the stdlib; `str.translate(str.maketrans(RFC, OTHER))` over an RFC 4648 string is the whole implementation of the chunked reading, and a PyPI package is worth it only for the check symbol. Two habits: decode with `casefold=True` for anything a human typed, and if you reach for `map01`, write down in the same line *why* the digit is ambiguous — the argument reads like a formality and is not one.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* There is no base32 in the standard library the way `cl_http_utility=>encode_x_base64( )` gives you base64, so a base32 field on an interface means either an add-on or your own routine over `xstring`. If you write one, write it against RFC 4648 and say so in the interface agreement, because "base32" alone does not distinguish the four alphabets on this page — and if the partner says *Crockford*, ask whether their value is a **number** or a **byte string**, since that decides the answer for every length not divisible by five. The same discipline as a code page: the tool does not carry the agreement, the document does. See [SAP code pages](../../07_Real_Data/sap_code_pages/README.md).

## Try it

```bash
cd 03_Encodings/base32_alphabets/examples
python3 base32_alphabets_py.py
bash base32_alphabets_sh.sh
```

Without the machine: a partner's API returns an identifier as `AHM6A83HENMP6TS0`, their documentation says "Crockford Base32", and your decoder returns bytes that are one short of what their example shows. Say which two things could disagree here, which question you would put to the partner, and what you would ask them to add to the specification so the next implementer does not have to ask.

## See also

- [Binary to text](../binary_to_text/README.md) — the width question, the padding, and why decode is many-to-one
- [Escaping into ASCII](../escaping_into_ascii/README.md) — the other reason text gets encoded twice, and the one scheme of the four there that names its charset
- [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) — base16, where the pieces divide the byte evenly and none of this arises
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) — the tool that performs the rename, and why the sort-order promise needs `LC_ALL=C`
