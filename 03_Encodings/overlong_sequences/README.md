# Overlong sequences

**Level:** 301 · deep dive

**One line:** A code point has exactly one legal UTF-8 spelling, and the padded longer spellings — which carry the identical payload bits and decode to the identical character — are ill-formed anyway, because the moment one character has two byte strings, every check that reads bytes and every step that reads characters can be made to disagree.

## The slide this page started from

Bob Steagall's CppCon 2018 talk [Fast Conversion From UTF-8 with C++, DFAs, and SSE Intrinsics ↗](https://www.youtube.com/watch?v=5FQ87-Ecb-A) follows its *Valid Sequence Example* — the slide [Validation is a boundary](../validation_is_a_boundary/README.md) starts from — with one called *Overlong Sequence Example*. It takes the same closing brace and writes it out twice more:

```text
    }   U+007D   0111 1101

1:  0111.1101                            Valid ASCII leading byte
2:  1100.0001 1011.1101                  Invalid sequence 0xC1 0xBD
3:  1110.0000 1000.0001 1011.1101        Invalid sequence 0xE0 0x81 0xBD
```

The highlighted bits on that slide are the payload, and the point of the highlighting is that **the payload never changes**. `111 1101` is in row 1, in row 2 and in row 3. What grows is the padding: the two-byte template has eleven payload slots for a seven-bit number, so four of them are filled with leading zeros, and the three-byte template pads with nine. Nothing is corrupted. Every one of those rows decodes, by the templates alone, to 125.

The slide stops at three. The pattern does not — there is a fourth:

| Bytes | Hex | Binary | UTF-8? |
|---|---|---|---|
| 1 | `7D` | `01111101` | **yes** — the only legal spelling |
| 2 | `C1 BD` | `11000001 10111101` | no — overlong |
| 3 | `E0 81 BD` | `11100000 10000001 10111101` | no — overlong |
| 4 | `F0 80 81 BD` | `11110000 10000000 10000001 10111101` | no — overlong |

Every character in Unicode has this fan of extra spellings: the shortest one, and then one for every longer template that still has room. ASCII has three spare spellings each, a three-byte character has one, and the four-byte characters at the top have none — which is why the pattern stops at four and not at five.

## Why a second spelling is forbidden

The bits are right, so the rule is not about correctness. It is about **uniqueness**, and the reason is a shape rather than an incident: real systems check bytes in one place and interpret characters in another. A blocklist, a path comparison, a WAF rule, a `grep` in a log pipeline — these read bytes. A template engine, a filesystem, a shell, a JSON parser — these read characters. Give a character two byte strings and you can hand the first stage a byte string it does not recognise and the second stage a character it will act on.

[RFC 3629 ↗](https://www.rfc-editor.org/rfc/rfc3629#section-10) says exactly this, and unusually for an encoding spec it spends a whole section on it. Its example is `/`: a parser guarding against `2F 2E 2E 2F` (`/../`) never sees it in `2F C0 AE 2E 2F`, and a lenient decoder downstream turns that back into `/../`. The RFC notes this was used by a widespread web-server worm in 2001 — the IIS directory-traversal hole, [CVE-2000-0884 ↗](https://www.cve.org/CVERecord?id=CVE-2000-0884), whose payloads are still recognisable in old logs as `%c0%af`.

So the rule is **reject**, never *canonicalise and continue*. Silently shortening an overlong to its legal form would preserve the character and destroy the evidence: the sender said something they were not allowed to say, and a program that quietly fixes it forwards an attack as though it were text. Rejection is what makes "these bytes are UTF-8" a fact the next stage can build on.

The rule was not always this firm. Unicode's [Corrigendum #1 ↗](https://www.unicode.org/versions/corrigendum1.html), issued in 2001 in response to exactly these attacks, tightened the conformance clause so that non-shortest forms are *ill-formed* — before it, a decoder could take them and still call itself conformant. RFC 3629 restated it in 2003. If you meet a decoder that accepts `C0 80`, it is not being clever; it is twenty-five years out of date.

## Boundary conditions: three holes, not one

Steagall's next slide is *Boundary Conditions*, and it is the one worth copying into your own notes, because it lists everything that can make a byte sequence ill-formed while still matching the templates perfectly:

- **the top of Unicode** — `U+10FFFF`, seventeen planes of 2¹⁶ code points. Anything above it is not a code point at all.
- **the surrogate range** — `U+D800`–`U+DFFF`, high `U+D800`–`U+DBFF` and low `U+DC00`–`U+DFFF`. These exist only as UTF-16 machinery and are not characters, so UTF-8 must not encode them.
- **overlong sequences** — this page. Stated as three lead-byte facts:
  - 2-byte: leading `C0` or `C1`
  - 3-byte: leading `E0` followed by a second byte ≤ `9F`
  - 4-byte: leading `F0` followed by a second byte ≤ `8F`

Those three numbers look arbitrary until you notice they are not conventions at all — they are arithmetic, and [the C example](#the-c-view) below derives all three by brute force in a dozen lines. Each template has a floor, the smallest code point it is *allowed* to carry: `0x80` for two bytes, `0x800` for three, `0x10000` for four. Walk the second byte upward and the boundary is simply the first value that clears the floor. For two bytes that is `C2` (so `C0` and `C1` lead nothing legal, ever); for three bytes it is `A0`; for four it is `90`.

## Finding the transitions

Steagall's third slide walks the code point space in order and marks the bands that fall out. The result is [the Unicode Standard's Table 3-7 ↗](https://www.unicode.org/versions/latest/core-spec/chapter-3/), *Well-Formed UTF-8 Byte Sequences*, which is the table every real decoder is compiled from — and which is why a UTF-8 decoder is a small state machine and not a shift-and-mask:

| Code points | Byte 1 | Byte 2 | Byte 3 | Byte 4 |
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

The four bold cells are the whole story. Three of them (`E0`, `F0`, and the `C2` floor in row two) exclude overlongs; the fourth (`ED` capped at `9F`) excludes the surrogates; and `F4` capped at `8F` is the top of Unicode. Every other second byte is the full `80`–`BF`.

Read the other way, the table's gaps are the yellow bands on the slide:

| The excluded band | What it would have encoded | Why it is out |
|---|---|---|
| `C0 80` … `C1 BF` | `U+0000`–`U+007F` | overlong — one byte already says all of these |
| `E0 80 80` … `E0 9F BF` | `U+0000`–`U+07FF` | overlong |
| `ED A0 80` … `ED BF BF` | `U+D800`–`U+DFFF` | surrogates — not characters |
| `F0 80 80 80` … `F0 8F BF BF` | `U+0000`–`U+FFFF` | overlong |
| `F4 90 80 80` and up | `U+110000` and beyond | past the top of Unicode |

That table is not quoted from memory. Every row above was checked by expanding it: 1,112,064 byte sequences, which is `0x110000` minus the 2,048 surrogates, each decoded and each landing inside the code point range its row claims — no gaps, no overlaps, nothing rejected.

## Thirteen bytes that can never appear

A useful thing falls out of the table, and it is the fastest overlong smell-test there is. Encode every code point Unicode has and collect the byte values that come out; thirteen of the 256 never do:

```text
C0 C1 F5 F6 F7 F8 F9 FA FB FC FD FE FF
```

`C0` and `C1` are missing because the only code points they could lead are ones that fit in a single byte — they are overlong *by construction*, with no second byte needed to know it. `F5` and up are missing because they lead past `U+10FFFF`. So if a hex dump of something claiming to be UTF-8 contains a `C0` or a `C1` anywhere, you already know: either it is not UTF-8, or somebody padded a character on purpose.

## In Python

<!-- output:overlong_sequences_py -->
*Verified output of [`overlong_sequences_py.py`](examples/overlong_sequences_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE CHARACTER, FOUR SPELLINGS
   The closing brace }  is U+007D, binary 0111 1101 -- seven payload bits.
   Every template below carries those same seven bits. Only the padding grows.
   1 byte :  7D            01111101
   2 bytes:  C1 BD         11000001 10111101
   3 bytes:  E0 81 BD      11100000 10000001 10111101
   4 bytes:  F0 80 81 BD   11110000 10000000 10000001 10111101
   The two-byte row is the slide's 0xC1 0xBD; the three-byte row is 0xE0 0x81 0xBD.

2. WHAT PYTHON SAYS ABOUT EACH
   7D           -> '}'
   C1 BD        -> UnicodeDecodeError: invalid start byte, bytes 0..1
   E0 81 BD     -> UnicodeDecodeError: invalid continuation byte, bytes 0..1
   F0 80 81 BD  -> UnicodeDecodeError: invalid continuation byte, bytes 0..1
   Only the shortest spelling is UTF-8. The other three are ill-formed --
   not because the bits are wrong, but because a second spelling is not allowed.
   Note WHERE each one dies: 0xC1 can only ever start an overlong form, so it is
   refused as a start byte with no second byte read. 0xE0 and 0xF0 are legal start
   bytes, so those two survive one byte longer and die on the byte after.

3. THE DECODER EVERYBODY WRITES BY HAND
   naive_decode(7D)               = '}'
   naive_decode(C1 BD)            = '}'
   naive_decode(E0 81 BD)         = '}'
   naive_decode(F0 80 81 BD)      = '}'
   Every bit handled correctly, every template read right -- and it takes all four.
   That is the bug. It is not a typo -- it is the check nobody thought to add.

4. WALKING A FILTER PAST THE GATE
   plain  }  6E 61 6D 65 7D 64 72 6F 70     filter says: BLOCKED
   overlong  6E 61 6D 65 C1 BD 64 72 6F 70  filter says: allowed
   ...and then the sloppy decoder runs: 'name}drop'
   The filter looked at bytes, the decoder produced characters, and the two
   disagreed about what the input said. That gap is the whole attack.
   RFC 3629 section 10 tells this story with '/' and a 2001 web-server worm.

5. THIRTEEN BYTES THAT CANNOT APPEAR IN UTF-8 AT ALL
   C0 C1 F5 F6 F7 F8 F9 FA FB FC FD FE FF
   13 of 256, found by encoding every code point Unicode has and
   collecting the bytes that never came out.
   0xC0 and 0xC1 are missing because the only code points they could lead are
   ones that fit in a single byte -- so they are overlong by construction.
   0xF5 and up are missing because they lead past U+10FFFF, the top of Unicode.
```
<!-- /output -->

Section 3 is the one to sit with. That decoder is not a strawman — it is what you get by implementing the template table faithfully and stopping when the bits come out right, and it is what most people write the first time. Section 4 is the same program's version of the RFC's story, with the slide's brace instead of a slash: the filter reads bytes and reports nothing to see, the decoder reads characters and produces the thing the filter existed to remove.

## In the terminal

<!-- output:overlong_sequences_sh -->
*Verified output of [`overlong_sequences_sh.sh`](examples/overlong_sequences_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE CLOSING BRACE, SPELLED FOUR WAYS

   $ printf '\x7d' | xxd -p
     7d
   $ printf '\xc1\xbd' | xxd -p
     c1bd
   $ printf '\xe0\x81\xbd' | xxd -p
     e081bd
   $ printf '\xf0\x80\x81\xbd' | xxd -p
     f08081bd
   All four carry the same seven payload bits. Only the first is UTF-8.

2. iconv TAKES ONLY THE SHORTEST ONE

   \x7d                 exit 0   the brace, as UTF-8
   \xc1\xbd             exit 1   overlong, 2 bytes
   \xe0\x81\xbd         exit 1   overlong, 3 bytes
   \xf0\x80\x81\xbd     exit 1   overlong, 4 bytes
   Same on macOS and on Linux. Unlike the U+10FFFF cap, the shortest-form rule
   predates RFC 3629, so every iconv built in the last twenty years enforces it.

3. A BYTE FILTER DOES NOT SEE THE BRACE IT IS LOOKING FOR

   plain     6e616d657d64726f70      9 bytes in,  8 out  -> filter removed 1
   overlong  6e616d65c1bd64726f70   10 bytes in, 10 out  -> filter removed 0
   `tr -d '}'` is a byte filter and the overlong brace contains no 0x7D byte,
   so it passes through untouched. Any later stage that decodes leniently gets
   back the character the filter was put there to remove.

4. SO THE ORDER OF THE PIPELINE IS THE SECURITY PROPERTY

   wrong:   cat input | tr -d '}' | do_something        # filter, then hope
   right:   iconv -f UTF-8 -t UTF-8 < input | tr -d '}' | do_something

   Validate at the top of the pipe and every stage below it is looking at bytes
   that have exactly one reading. Filter first and you are guarding a spelling,
   not a character - and there are three other spellings.
```
<!-- /output -->

The shell is where this stops being theoretical, because a pipeline is *made* of stages that read bytes. `tr`, `grep`, `sed` and `cut` are byte filters; whatever consumes their output usually is not. Section 4 is the practical rule, and it is one word long: **first**. Validate at the top of the pipe and every stage below is looking at bytes with exactly one reading.

Worth noting what section 2 does *not* say. The sibling page records that `iconv` accepts sequences above `U+10FFFF` on both platforms, because it is checking the older 31-bit UTF-8 that RFC 3629 capped in 2003. The shortest-form rule is older than that cap and universally implemented, so on overlongs `iconv` agrees with Python and Rust exactly. "Valid UTF-8" is still not one question — but this is one of the parts everybody answers the same way.

## In Rust

<!-- output:overlong_sequences_rs -->
*Verified output of [`overlong_sequences_rs.rs`](examples/overlong_sequences_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. from_utf8 ON EACH SPELLING
   7D           Ok("}")
   C1 BD        Err(valid_up_to: 0, error_len: Some(1))
   E0 81 BD     Err(valid_up_to: 0, error_len: Some(1))
   F0 80 81 BD  Err(valid_up_to: 0, error_len: Some(1))
   valid_up_to is how many bytes were text before the trouble -- zero here,
   because the trouble is the first byte of the sequence. error_len is how
   many bytes to skip: Some(1) means one bad byte, then look again.

2. THE SAME BYTES, MADE SAFE INSTEAD OF REFUSED
   7D           -> "}"   (0 replacement chars)
   C1 BD        -> "��"   (2 replacement chars)
   E0 81 BD     -> "���"   (3 replacement chars)
   F0 80 81 BD  -> "����"   (4 replacement chars)
   Lossy conversion never invents the brace. It marks the damage and moves on,
   one U+FFFD per byte that could not begin or continue a real sequence.

3. THE CHARACTER WAS NEVER THE PROBLEM
   char::from_u32(0x7D)      = Some('}')
   '}' encodes as             7D
   char::from_u32(0xD800)    = None   (a surrogate is not a character)
   char::MAX                 = U+10FFFF
   U+007D is a perfectly good code point with a perfectly good encoding.
   What Rust refused was a second, longer way of writing the same one.

4. WHERE THE GUARANTEE IS HANDED BACK
   from_utf8_unchecked(7D) = "}"   -- sound: the bytes really are UTF-8
   The same call on C1 BD would be undefined behaviour, and this program
   does not make it: every later &str method is allowed to assume the
   invariant, so a false promise is not a wrong answer, it is no answer.
   Write that line with the bytes in view and rustc refuses to compile it --
   see the page for the error. `unsafe` moves the check to you; it does not
   remove it, and here the compiler checks your homework anyway.
```
<!-- /output -->

Rust does not check for overlongs so much as make them unrepresentable: `&str` is *defined* as well-formed UTF-8, so the question is settled at construction and never asked again. Section 2 shows the lossy alternative — one `U+FFFD` per byte that could neither begin nor continue a real sequence, which is why the four-byte overlong produces four of them and never produces a brace.

Section 4 has the detail worth keeping. `from_utf8_unchecked` is the door out, and writing it with the bad bytes in view does not compile — `rustc` has a deny-by-default lint for exactly this:

```text
error: calls to `std::str::from_utf8_unchecked` with an invalid literal are undefined behavior
   |
   = note: `#[deny(invalid_from_utf8_unchecked)]` on by default
```

`unsafe` moves the obligation to you; it does not delete it. And in the one case where the compiler can still see the bytes, it checks your homework anyway.

## The C view

<!-- output:overlong_sequences_c -->
*Verified output of [`overlong_sequences_c.c`](examples/overlong_sequences_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE DECODER WITH NOTHING BUT THE TEMPLATES
   1 byte  -> U+007D  '}'
   2 bytes -> U+007D  '}'
   3 bytes -> U+007D  '}'
   4 bytes -> U+007D  '}'
   Four different byte strings, one character. C will not stop you:
   there is no str type here, only a pointer, and no library ran a check.

2. WHERE THE BOUNDARY FALLS, BY ARITHMETIC
   For each template, walk the second byte upward and ask the only
   question that matters: is this code point already spellable shorter?
   2 bytes: lead 0xC2 0x80 is the first that reaches U+0080
            so 0xC0 and 0xC1 lead nothing legal, ever.
   3 bytes: 0xE0 0xA0 ... is the first that reaches U+0800
            so after 0xE0, a second byte below 0xA0 is overlong.
   4 bytes: 0xF0 0x90 ... is the first that reaches U+10000
            so after 0xF0, a second byte below 0x90 is overlong.

3. THE FIX, IN THREE COMPARISONS
   if (b0 == 0xC0 || b0 == 0xC1)                 return REJECT;
   if (b0 == 0xE0 && b1 <  0xA0)                 return REJECT;
   if (b0 == 0xF0 && b1 <  0x90)                 return REJECT;
   1 byte  U+007D  accept
   2 bytes U+007D  REJECT
   3 bytes U+007D  REJECT
   4 bytes U+007D  REJECT
   Three lines. That is the entire cost of the rule, and leaving them
   out is what a decade of directory-traversal advisories was about.
```
<!-- /output -->

C is where this bug actually shipped, and the reason is in section 1: there is no `str` type, only a pointer, and nothing in the standard library has an opinion about UTF-8. The decoder is yours, so the check is yours to leave out.

Section 2 is the part worth doing once by hand. The boundary bytes `C2`, `A0` and `90` are not values to memorise — they are the answer to *what is the smallest second byte that reaches this template's floor*, and asking the machine that question gets the same three numbers Steagall's slide lists. Section 3 is the fix: three comparisons. That is the entire runtime cost of the shortest-form rule, and omitting them is what a decade of directory-traversal advisories was about.

## The overlongs that are on purpose

Two widely-deployed formats break this rule deliberately, which is why data arriving from them can be labelled UTF-8 and still fail a UTF-8 validator:

**Java's Modified UTF-8** encodes `U+0000` as the overlong `C0 80`, precisely so a NUL never appears as a zero byte inside a string — convenient when the surrounding C code is NUL-terminated. It is what [`DataInput.readUTF` / `DataOutput.writeUTF` ↗](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/DataInput.html) read and write, what string constants use inside a `.class` file ([JVM spec §4.4.7 ↗](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html#jvms-4.4.7)), and what JNI hands to native code. It also encodes characters above `U+FFFF` as a surrogate *pair*, each surrogate given its own three bytes — which is the second violation, and it has its own name: **CESU-8** ([UTR #26 ↗](https://www.unicode.org/reports/tr26/)). Neither is UTF-8, and the specs say so.

**WTF-8** ([the spec ↗](https://simonsapin.github.io/wtf-8/)) extends UTF-8 to hold unpaired surrogates, so that Windows filenames and other UTF-16 data that is not well-formed can round-trip through a byte string. It is deliberately never used for interchange — Rust uses it internally for `OsString` on Windows and does not let it out.

The lesson is the same in all three cases and it is the one to carry to real data: **"UTF-8" on a label is a claim about a producer, not a property of the bytes.** Validate anyway. A `C0 80` in the middle of what a Java system called UTF-8 is not corruption and not an attack — it is a different format with the same name, and knowing which of the three you are holding is the difference between a two-line fix and an afternoon.

## If you are coming from Python or ABAP

**Python.** You have already met the two halves of this page without them being named. `bytes.decode('utf-8')` implements the whole table above, which is why `b'\xc1\xbd'.decode()` raises rather than returning `'}'`, and why the reason strings differ between the spellings — `C1` fails as an *invalid start byte* with no second byte read, while `E0 81` and `F0 80` fail one byte later as an *invalid continuation byte*, which is the table's second-byte column talking. The gap Python leaves open is the same one this page is about, one level up: a `str` can hold `chr(0xD800)`, so the check on the way *out* is not redundant. If you are reading Java data, the codec you want is not `utf-8` — Python has no built-in for Modified UTF-8, and the usual move is `data.replace(b'\xc0\x80', b'\x00').decode('utf-8')` after checking that is really what you have.

**ABAP.** `cl_abap_codepage=>convert_from( )` is your decoding boundary and it raises `cx_sy_conversion_codepage` on ill-formed input, so an overlong arriving in an `xstring` fails there rather than downstream — the same place Python's `decode` fails. Two things to hold onto. A Unicode ABAP system stores `string` in a fixed-width UTF-16 form internally, so overlongs are strictly a property of the *bytes* at the boundary, never of a `string` you already hold; by the time you can see the character, the question is gone. And the boundary is usually a file or an interface rather than a call — `OPEN DATASET … IN LEGACY BINARY MODE` hands you an `xstring` nobody has validated, which is exactly the C situation with different syntax. Verify the code page against your own system rather than trusting a number from a document. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 03_Encodings/overlong_sequences/examples
python3 overlong_sequences_py.py
bash overlong_sequences_sh.sh
rustc --edition 2024 overlong_sequences_rs.rs -o /tmp/ol && /tmp/ol
cc -std=c11 -Wall -Wextra overlong_sequences_c.c -o /tmp/olc && /tmp/olc
```

**The euro, answered.** [Validation is a boundary](../validation_is_a_boundary/README.md) ends by asking what `F0 82 82 AC` is — four bytes that decode by the templates to `U+20AC`, whose real encoding is the three bytes `E2 82 AC`. It is row four of the excluded-band table above: lead byte `F0` with a second byte of `82`, which is below `90`, so it is an overlong and the second of the three comparisons in the C example rejects it. Check it: `printf '\xf0\x82\x82\xac' | iconv -f UTF-8 -t UTF-8; echo $?`

**Then one without the machine.** The Python example prints thirteen bytes that can never appear in UTF-8. Nine of them are `F5`–`FF`. Work out why the list does not also contain `F4` — and then why it does not contain `E0` or `F0`, which are the lead bytes of two of the excluded bands. (The answer to both is in the Table 3-7 rows above, and it is the same answer.)

**And one on real data.** Take any file you did not write and look for the smell test: `xxd file | grep -i -E 'c0|c1' | head`. Most hits will be the low nibble of some other byte, so confirm the ones that look like lead bytes with `iconv -f UTF-8 -t UTF-8 < file > /dev/null; echo $?`.

## See also

- [Validation is a boundary](../validation_is_a_boundary/README.md) — *where* the check runs, in four languages, and what is left of it afterwards
- [UTF-8 by hand](../utf8_by_hand/README.md) — the templates this page pads, with a pencil
- [UTF-16 and surrogates](../utf16_and_surrogates/README.md) — the second hole in the table, and why UTF-8 has to forbid it
- [Why UTF-8 won](../../09_History/why_utf8_won/README.md) — self-synchronisation and the other properties the shortest-form rule protects
- [Mojibake](../mojibake/README.md) — the failure where the bytes are valid and the table was still wrong
- [RFC 3629, section 10: Security Considerations ↗](https://www.rfc-editor.org/rfc/rfc3629#section-10) — one page, and the whole argument for rejecting rather than repairing
