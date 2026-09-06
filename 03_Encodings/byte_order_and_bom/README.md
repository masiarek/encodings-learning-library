# Byte order and the BOM

**Level:** 201 · working knowledge

**One line:** A value wider than one byte has to be written in *some* order, and the byte order mark is one code point — `U+FEFF` — placed first so the reader can work the order out; UTF-8 has no order to resolve, gets the mark anyway as a *signature*, and those three bytes `EF BB BF` are why a CSV's first column is called `﻿ID`.

## Two different problems, one mark

The mark does two jobs and they are not equally necessary, which is the source of most of the confusion about it.

The first job is real. UTF-16 stores every character as a 16-bit number, and a 16-bit number has two possible layouts in memory — most significant byte first (**big-endian**, what the internet standards chose, which is why it is called network byte order) or least significant first (**little-endian**, what x86 and ARM actually run). A file of UTF-16 is therefore ambiguous, and *undetectably* so: both layouts are well-formed, so a reader handed one and told nothing does not get an error, it gets the wrong text. Putting `U+FEFF` at the front fixes that, because the mark is itself a two-byte value and is written in the file's own order — `FE FF` one way, `FF FE` the other. The reader learns the order by reading.

The second job is a repurposing. UTF-8 is a stream of individual bytes; a three-byte character has exactly one spelling and there is no end to put first, so there is no order to resolve and nothing for a byte order mark to do. But the same code point encoded as UTF-8 is the three bytes `EF BB BF`, and people started writing those at the front of files as a **signature** — a flag meaning *"read me as UTF-8"* for a reader that would otherwise fall back to a local code page and [guess wrong](../mojibake/README.md). That is a different problem (which rulebook?) than the one the mark was invented for (which end?), solved by reusing the same three bytes. Python names the distinction honestly: the codec is `utf-8-sig`, **sig for signature**.

## Why the mirror image is proof, not convention

This is the part usually left out, and it is the reason the scheme works at all.

If the mark were an ordinary character, a reader seeing the reversed bytes would face a second ambiguity: is this a little-endian mark, or a big-endian file that happens to begin with some other letter? `U+FFFE` — the mirror image of `U+FEFF` — is a **permanent noncharacter**. Unicode reserves it and guarantees it will never be assigned to anything, precisely so that it can serve as this signal. A reader that decodes `FFFE` has not found a rare character; it has found a value that cannot legitimately exist, and it knows for certain the order is backwards. Section 2 of the Python run below decodes the little-endian bytes as big-endian on purpose and asks Unicode for the resulting character's name; there is no name, because there is deliberately nothing there.

## Which name you type decides whether there is a mark

Everything above is about the *file*. This is about the one line of code that produces it — which is where a mark is most often added by accident, because in Python the decision is not a flag, an argument or a setting. It is the codec's **name**. Anthony Sottile's [what is a BOM (byte-order-marker) ↗](https://youtu.be/OrtNMystCgM) is eleven minutes of exactly this at the REPL: one character through `utf-16le` and `utf-16be`, and then the same character through a bare `utf-32`, where the byte count jumps and the extra bytes are the mark.

| you encode with | what comes out |
|---|---|
| `utf-16le` · `utf-16be` · `utf-32le` · `utf-32be` | the payload, and nothing else |
| `utf-16` · `utf-32` | **a mark**, then the payload — in whichever order the machine running your code happens to use |
| `utf-8` | the payload |
| `utf-8-sig` | **`EF BB BF`**, then the payload |

The logic is consistent once you see it. A suffix is a promise you have already made, so there is nothing left to announce and no mark is written. A bare `utf-16` is you declining to choose, so the codec chooses for you — and then has to say which way it went. `'😀'.encode('utf-16')` is six bytes where `'😀'.encode('utf-16le')` is four, and `''.encode('utf-16')` is two bytes for the empty string: the mark is a header, not text.

The same name decides the other direction, and that is the half that bites. **The unsuffixed codec eats a leading mark; the suffixed one hands it back as a character** — you told it the order, so it has no reason to think the first two bytes are anything but content. That is the `utf-8` / `utf-8-sig` asymmetry below, one encoding up, and it is where an invisible `U+FEFF` welded to the first field of a header comes from.

Reading a file that has **no** mark with the unsuffixed `utf-16` is worse than either, because it always works. Python falls back to the byte order of the machine doing the reading: right whenever writer and reader happen to agree, wrong when they do not, and in both cases a decode that *succeeds*. That is the original problem the mark exists to solve, reintroduced as a default.

Nothing about this is Python's alone. `iconv` has the identical rule — `-t UTF-16` writes a mark and picks an order, `-t UTF-16LE` writes neither — which is why the note under the shell run below is a consequence rather than a quirk of one tool. Rust has no unsuffixed form to reach for: `encode_utf16()` stops at code *units* and makes you name `to_le_bytes` or `to_be_bytes` yourself, and nothing in `std` will emit a mark on your behalf.

### Two smaller traps in the same line of code

**`FF FE` is not enough to identify a file.** The UTF-32LE mark is `FF FE 00 00` — the UTF-16LE mark entire, plus two NULs. A sniffer that tests the two-byte form first therefore calls every little-endian UTF-32 file UTF-16, and gets no error for it: `'A~'` comes back as `'\x00A\x00~\x00'`, the right letters with a NUL welded to each one. It then survives `.strip()`, fails every comparison, and looks like a database problem. Test the four-byte mark before the two-byte one.

**The name has to survive the alias table.** `'utf16-le'` raises `LookupError: unknown encoding: utf16-le` while `'utf-16le'` is fine — and the difference is not the hyphen, because `'UTF 16 LE'` works too. Python collapses every run of non-alphanumeric characters into a single underscore and looks the result up in `encodings.aliases`, which holds `utf_16le` and `utf_16_le` and has never held `utf16_le`: in `utf16-le` there is nothing between `utf` and `16` to collapse. Two spellings that look equally reasonable, and only one of them exists.

## What the three bytes cost

To a reader expecting a signature, the mark is invisible. To every other reader it is simply the first three bytes of the file — and the whole difficulty is that this is nearly always silent:

| Reader | What happens |
|---|---|
| a JSON parser | raises — and Python's even names the fix in the message |
| a `^`-anchored match, `grep '^id'` | quietly matches nothing; the line starts with `EF`, not `i` |
| an exact key or header comparison | `'﻿id' == 'id'` is simply `False` |
| `.strip()` / `.trim()` | does nothing: `U+FEFF` is named ZERO WIDTH NO-BREAK SPACE but is **not** in Unicode's `White_Space` property |
| a shebang, `#!/usr/bin/env python3` | the kernel reads offset 0, does not find `#!`, and will not run the script |
| concatenation — `cat`, a log shipper, a multipart upload | the second file's signature lands in the *middle*, where it is not a signature at all |

Only the first of those complains. The rest return `None`, or `False`, or a count of zero, and the header that looks identical on screen goes on not matching.

## The decision, in one question

**Who reads this file?**

- **A program, by exact bytes** — JSON, a config, a shell script, a diff, a build input: write plain `utf-8`. Everything here reads from offset 0 and the mark is content.
- **A guessing GUI** — Excel, Notepad: write `utf-8-sig`. Excel has no other way to know, and falls back to the local code page when there is no flag. That is the whole of [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md).
- **Both** — write plain, and make the *reader* forgiving with `utf-8-sig`.

The question is answerable rather than a matter of taste: grep for who opens the file before changing what you write into it.

## In Python

<!-- output:byte_order_and_bom_py -->
*Verified output of [`byte_order_and_bom_py.py`](examples/byte_order_and_bom_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A NUMBER WIDER THAN A BYTE HAS TWO SPELLINGS
------------------------------------------------------------------------
   the number                258   = 0x00000102
   .to_bytes(4, 'big')       00 00 01 02   most significant end first
   .to_bytes(4, 'little')    02 01 00 00   least significant end first

   Same number, same four bytes, opposite order. Both are correct and
   neither is detectable from the bytes alone: 00 00 01 02 read the
   other way round is 33,619,968, and nothing in the file objects.
   Big-endian is the order the internet standards chose, which is why
   it is called network byte order; x86 and ARM run little-endian, so
   every packet header crossing a socket is being swapped.

   A single byte has no order. This whole question only exists for
   values stored in more than one byte -- which is what UTF-16 makes
   every character, and what UTF-8 makes none of.

2. THE MARK: ONE CODE POINT, WRITTEN IN THE FILE'S OWN ORDER
------------------------------------------------------------------------
   U+FEFF is ZERO WIDTH NO-BREAK SPACE
   as utf-16-be   fe ff
   as utf-16-le   ff fe

   The reader does not have to be told the order; it reads the mark and
   deduces it. Both of these decode to the same two letters:
     fe ff 00 49 00 44    .decode('utf-16') -> 'ID'
     ff fe 49 00 44 00    .decode('utf-16') -> 'ID'

   And here is why the trick is sound rather than merely conventional.
   Read the little-endian bytes as if they were big-endian:
     b'\xff\xfeI\x00D\x00'.decode('utf-16-be') -> '\ufffe䤀䐀'
     first code point: U+FFFE, no name -- a PERMANENT NONCHARACTER

   U+FFFE is reserved forever and can never be assigned. So the mirror
   image of the mark is not some other letter that might legitimately
   open a file -- it is a value guaranteed never to mean anything, and
   a reader that sees it knows for certain it has the order backwards.

3. THE CODEC NAME DECIDES WHETHER A MARK IS WRITTEN
------------------------------------------------------------------------
   one code point, U+1F600, written seven ways:
     utf-8     4 bytes   f0 9f 98 80
     utf-16be  4 bytes   d8 3d de 00
     utf-16le  4 bytes   3d d8 00 de
     utf-32be  4 bytes   00 01 f6 00
     utf-32le  4 bytes   00 f6 01 00
     utf-16    6 bytes   starts with codecs.BOM_UTF16: True
     utf-32    8 bytes   starts with codecs.BOM_UTF32: True

   The bytes of those last two are not printed, on purpose: the mark
   is followed by whichever order THIS machine runs, so the answer
   depends on who ran the script and a recorded key must not. What
   holds everywhere is the shape --
     the rest of the utf-16 form is one of the two suffixed forms: True
     the rest of the utf-32 form is one of the two suffixed forms: True

   So the rule is the name, and that is the whole of it:
     WITH a suffix (utf-16le, utf-32be) -- you have already said which
       order, there is nothing left to announce, and no mark is added
     WITHOUT one (utf-16, utf-32) -- the codec picks an order for you
       and writes a mark at the front to say which one it picked

   The mark is a header, not text, and it is written even when there
   is no text at all:
     len(''.encode('utf-16le')) = 0
     len(''.encode('utf-16'))   = 2
     len(''.encode('utf-32le')) = 0
     len(''.encode('utf-32'))   = 4

4. AND THE NAME HAS TO SURVIVE THE ALIAS TABLE
------------------------------------------------------------------------
   'utf-16le'   -> codecs.lookup(..).name = 'utf-16-le'
   'utf-16-le'  -> codecs.lookup(..).name = 'utf-16-le'
   'utf_16_le'  -> codecs.lookup(..).name = 'utf-16-le'
   'UTF 16 LE'  -> codecs.lookup(..).name = 'utf-16-le'
   'utf16-le'   -> LookupError: unknown encoding: utf16-le
   'utf16le'    -> LookupError: unknown encoding: utf16le

   Four spellings work and two do not, and the difference is not the
   hyphen -- 'UTF 16 LE' is fine. Python turns every run of
   non-alphanumeric characters into a single underscore and looks the
   result up in encodings.aliases, so 'utf-16le', 'utf 16le' and
   'utf_16_le' all arrive as a name that table knows. 'utf16-le' has
   nothing at all between 'utf' and '16', so it normalises to a name
   the table has never contained. Two spellings that look equally
   reasonable, and only one of them exists.

5. READING BACK: THE SAME NAME DECIDES WHO EATS THE MARK
------------------------------------------------------------------------
   a little-endian file with a mark   ff fe 3d d8 00 de
     .decode('utf-16')     -> '😀'
     .decode('utf-16le')   -> '\ufeff😀'

   The unsuffixed codec consumes the mark; the suffixed one hands it
   back as a character, because you told it the order and it has no
   reason to think the first two bytes are anything but text. That is
   the utf-8-sig asymmetry of section 8, one encoding up -- and it is
   where an invisible U+FEFF welded to your first field comes from.

   The other way round is worse, and cannot be shown here for the
   same reason as section 3: a file with NO mark, decoded by the
   unsuffixed 'utf-16', is read in this machine's order. Right half
   the time, silently wrong the other half, and the half you get
   depends on the hardware -- which is the exact bug the mark was
   invented to prevent, reintroduced by a codec default.

6. FF FE IS NOT ENOUGH TO IDENTIFY A FILE
------------------------------------------------------------------------
   codecs.BOM_UTF16_LE   ff fe
   codecs.BOM_UTF32_LE   ff fe 00 00   <- the line above, plus two NULs
   a UTF-32LE file       ff fe 00 00 41 00 00 00 7e 00 00 00
     .decode('utf-32')   -> 'A~'
     .decode('utf-16')   -> '\x00A\x00~\x00'

   No exception. A sniffer that tests the two-byte mark first calls
   every little-endian UTF-32 file UTF-16, and what it hands back is
   the right letters with a NUL welded to each one -- which then
   survives a strip(), fails every comparison, and looks like a
   database problem. Test the four-byte mark before the two-byte one.

7. UTF-8 HAS NO BYTE ORDER, AND GETS THE MARK ANYWAY
------------------------------------------------------------------------
   the same code point as UTF-8   ef bb bf
   codecs.BOM_UTF8                b'\xef\xbb\xbf'

   UTF-8 is a stream of single bytes; a three-byte character has one
   spelling and there is no end to put first. So EF BB BF resolves
   nothing. It was repurposed as a SIGNATURE: a flag at the front
   meaning 'read me as UTF-8', for a reader that would otherwise fall
   back to a local code page and guess wrong. Python spells that codec
   'utf-8-sig' -- sig for signature, not for byte order.

   plain UTF-8     69 64 2c 6e 61 6d 65 0a
   with signature  ef bb bf 69 64 2c 6e 61 6d 65 0a

   Same file. Three bytes of difference, and they are content.

8. utf-8-sig: FORGIVING ON THE WAY IN, LOUD ON THE WAY OUT
------------------------------------------------------------------------
   ef bb bf 69 64 as utf-8: '\ufeffid'   as utf-8-sig: 'id'
   69 64          as utf-8: 'id'         as utf-8-sig: 'id'

   That asymmetry is the whole rule. Reading with utf-8-sig strips a
   signature if there is one and does nothing at all if there is not,
   so it is the safe reader for a file of unknown origin. Writing with
   it always adds one -- so write plain 'utf-8' unless you have decided
   on purpose that the consumer needs the flag.

9. WHAT THE THREE BYTES BREAK
------------------------------------------------------------------------
   Invisible to a reader that expects it. To everyone else it is just
   the first three bytes of the file:

   a ^-anchored match   re.match('^id', '\ufeffid') -> None
   a JSON parser        JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig): line 1 column 1 (char 0)
   a shebang            ef bb bf 23 21 2f ...   the kernel looks at offset 0 and does not find '#!'
   an exact key match   '\ufeffid' == 'id' -> False
   a strip()            '\ufeffid'   -- U+FEFF.isspace() is False, so strip() leaves it
   concatenation        ef bb bf 61 0a ef bb bf 62 0a
                        a signature in the MIDDLE of a file is not a
                        signature, it is garbage on line 2

   Only the JSON parser complains, and it is the only one that names
   the fix in its own error message. The rest fail silently: the match
   returns None, the comparison returns False, the strip does nothing,
   and a header that looks identical on screen goes on not matching.

10. THE DECISION, IN ONE QUESTION
------------------------------------------------------------------------
   Who reads this file?

     a program, by exact bytes    -> plain 'utf-8'. A parser, a config,
       (JSON, a shell script,        a shebang and a diff all read from
        a diff, a build)             offset 0 and the mark is content.

     a guessing GUI               -> 'utf-8-sig'. Excel has no other
       (Excel, Notepad)             way to know, and guesses the local
                                    code page when there is no flag.

     both                         -> write plain, and make the reader
                                    forgiving with 'utf-8-sig'.

   The question is answerable: grep for who opens the file before you
   change what you write into it.
```
<!-- /output -->

## In the terminal

One command is missing from the script below on purpose, and its absence is the codec-name rule above, in a second tool. `iconv -t UTF-16` — with no `BE` or `LE` — does add a mark, and **it picks the order itself: big-endian on macOS, little-endian on GNU.** The same command on two machines writes two different files, so there is no single answer key for it, and there is no way to know which you got except to look at the bytes. Everything below is pinned to `UTF-16BE` or `UTF-16LE` and is byte-identical on both platforms.

<!-- output:byte_order_and_bom_sh -->
*Verified output of [`byte_order_and_bom_sh.sh`](examples/byte_order_and_bom_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SAME TWO LETTERS, BOTH WAYS ROUND
------------------------------------------------------------------------

   as UTF-16BE (most significant byte first):
     00000000: 0049 0044                                .I.D

   as UTF-16LE (least significant byte first):
     00000000: 4900 4400                                I.D.

   Two files, same text, no byte in common in the same place. A
   reader handed either one and told nothing has to guess -- and the
   guess is not detectable, because both are well-formed UTF-16.

2. THE MARK, PUT IN FRONT BY HAND
------------------------------------------------------------------------

   with a big-endian mark:
     00000000: feff 0049 0044                           ...I.D

   with a little-endian mark:
     00000000: fffe 4900 4400                           ..I.D.

   Now nobody is guessing. The first two bytes are the same code
   point written in the file's own order, so a reader learns the
   order by reading. FE FF and FF FE are the whole protocol.

3. UTF-8 HAS NO ORDER, AND STILL COLLECTS THREE BYTES
------------------------------------------------------------------------

   plain UTF-8:
     00000000: 6964 2c6e 616d 650a                      id,name.

   the same, with the UTF-8 signature:
     00000000: efbb bf69 642c 6e61 6d65 0a              ...id,name.

   first three bytes: efbbbf
   EF BB BF is U+FEFF encoded as UTF-8. It resolves no byte order --
   UTF-8 has none -- it is a flag saying "this file is UTF-8", for a
   reader that would otherwise fall back to a local code page.

4. TO ANYTHING ANCHORED AT THE START, IT IS CONTENT
------------------------------------------------------------------------

   grep -c "^id" on the clean file      : 1
   grep -c "^id" on the signed file     : 0

   Same visible text, and the second one matches nothing. The line
   does not start with i; it starts with EF. Nothing errors, nothing
   warns, the count is just zero -- which is the failure mode that
   costs an afternoon.

5. AND TWO SIGNED FILES DO NOT CONCATENATE
------------------------------------------------------------------------

     00000000: efbb bf61 0aef bbbf 620a                 ...a....b.

   The second mark is now in the middle of the file, where it is not
   a signature at all -- just an invisible character glued to the "b".
   Anything that joins files (cat, a log shipper, a multipart upload)
   turns a signature into a data bug on every part after the first.

6. TAKING IT OFF, PORTABLY
------------------------------------------------------------------------

   sed on line 1 only  : 69642c6e616d650a
   tail -c +4          : 69642c6e616d650a
   ..the same on a file that never had one:
   sed on line 1 only  : 69642c6e616d650a
   tail -c +4          : 6e616d650a

   Use the sed. Both strip a real mark, and both are identical on
   BSD and GNU -- but `tail -c +4` removes three bytes whether or not
   they were the mark, so on a clean file it eats the first three
   characters -- "id," is gone and the header now begins "name". The
   sed is conditional, which is what `utf-8-sig` is in Python.
```
<!-- /output -->

## In Rust

Rust splits the byte order into two method names, so a program that serialises a number has already said which end it meant — there is no default to get wrong quietly. On the reading side it shows the other half of this page, and shows it more starkly than Python does: `String::from_utf8` accepts `EF BB BF` happily, because a signature **is** valid UTF-8, and then nothing in std ever takes it off. There is no `utf-8-sig` in the standard library. The strip is yours to write, and `trim()` will not do it for you.

<!-- output:byte_order_and_bom_rs -->
*Verified output of [`byte_order_and_bom_rs.rs`](examples/byte_order_and_bom_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE ORDER IS A METHOD NAME, NOT A DEFAULT
------------------------------------------------------------------------
   let n: u32 = 258;
     n.to_be_bytes()  = [00, 00, 01, 02]   big-endian, network order
     n.to_le_bytes()  = [02, 01, 00, 00]   little-endian
     n.to_ne_bytes()  = whichever this machine uses -- not printed here,
                        because a recorded answer key must not depend
                        on the machine that produced it

   Three methods, three names. Nothing is implicit, so a program
   that writes a number to a socket or a file has already said
   which end it meant. `to_ne_bytes` is the one to be suspicious
   of: it is correct for a memory dump and wrong for a format.

2. READING BACK, WITH THE ORDER SUPPLIED BY THE READER
------------------------------------------------------------------------
   the four bytes            [00, 00, 01, 02]
     u32::from_be_bytes(..)  = 258
     u32::from_le_bytes(..)  = 33619968

   Same bytes, two answers, both valid. This is the problem the
   byte order mark exists to solve for text: put one known code
   point at the front and the reader can work the order out
   instead of being told it out of band.

3. AND THERE IS NO UNSUFFIXED OPTION TO GET WRONG
------------------------------------------------------------------------
   let face = "\u{1F600}";
     face.encode_utf16()       [d83d, de00]   2 units -- a surrogate pair
     ..each unit to_le_bytes   [3d, d8, 00, de]
     ..each unit to_be_bytes   [d8, 3d, de, 00]
     bytes either way          4, and no mark before either

   `encode_utf16` stops at code UNITS and hands the byte question
   straight back, so what Python spells as a codec name is a
   method name here -- and there is no third method that picks an
   order for you and writes a mark to announce it. Nothing in std
   emits a BOM at all: if a consumer needs one you write those
   bytes yourself, which is also why you cannot emit one by
   accident and wonder later where it came from.

4. A SIGNATURE IS VALID UTF-8, SO NOTHING REJECTS IT
------------------------------------------------------------------------
   bytes                     [ef, bb, bf, 69, 64]
   String::from_utf8(..)     Ok("\u{feff}id")
     s.len()                 5   <- bytes, and three of them are the mark
     s.chars().count()       3   <- one invisible char, then i, then d
     s == "id"               false

   The comparison is the bug, and it is silent. `from_utf8`
   cannot help: the mark is a legitimate code point and the bytes
   are well formed. Validity was never the question.

5. trim() WILL NOT REMOVE IT
------------------------------------------------------------------------
   first char                '\u{feff}'
     first.is_whitespace()   false
     s.trim() == "id"        false

   U+FEFF is named ZERO WIDTH NO-BREAK SPACE and is not in
   Unicode's White_Space property, so `trim` -- which is defined
   in terms of that property -- steps straight over it. A field
   that was trimmed and still does not match is this.

6. SO YOU WRITE THE STRIP, AND IT IS ONE LINE
------------------------------------------------------------------------
   s.strip_prefix('\u{feff}')  Some("id")
   ..unwrap_or(&s) on a clean string leaves it alone:
     "id" -> "id"

   That is Python's `utf-8-sig` in one method call, and having to
   type it is the honest version: std does not hide a codec that
   silently edits your input. The cost is that you must remember
   to do it at every boundary where a file of unknown origin
   arrives -- which is the same place you already chose a codec.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** Two rules cover it. **Read with `utf-8-sig`, write with `utf-8`** — the `-sig` codec strips a mark if there is one and does nothing if there is not, so it is the safe reader for a file of unknown origin, while writing with it always adds one. And when you find a mark already inside a `str`, remember that `.strip()` will not remove it: use `s.lstrip('﻿')` or `s.removeprefix('﻿')`, or better, fix the decode that let it in. `codecs.BOM_UTF8` is the bytes and `codecs.BOM_UTF16_LE` / `_BE` are the two-byte forms, which is tidier than typing the hex.

**ABAP.** There is no `utf-8-sig`. `OPEN DATASET … IN TEXT MODE ENCODING UTF-8` reads the mark as data, so an inbound file from a Windows or Excel producer arrives with `EF BB BF` welded to the first field of the header record — and the symptom is an interface whose first column never matches while every other column is fine, which reads like a mapping bug and is not one. Strip it at the boundary, on the first record only. `cl_abap_char_utilities` is where the byte-order-mark constants live on most releases; check what your system actually offers rather than trusting a name from a document, and see [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) for the wider habit. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 03_Encodings/byte_order_and_bom/examples
python3 byte_order_and_bom_py.py
bash byte_order_and_bom_sh.sh
rustc --edition 2024 byte_order_and_bom_rs.rs -o /tmp/bom && /tmp/bom
```

Without the machine: a colleague reports that a shell script you wrote "does nothing" on their laptop — no output, no error. They opened it in an editor that helpfully saved it as "UTF-8 with BOM". Say what the kernel did, and why nothing in the script itself could have told you.

## See also

- [UTF-16 and surrogates](../utf16_and_surrogates/README.md) — the encoding this mark was actually invented for
- [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md) — the same three bytes, met by everybody, in the place they do the most damage
- [Encode and decode are verbs](../encode_and_decode_are_verbs/README.md) — the two operations a signature is trying to disambiguate
- [Mojibake](../mojibake/README.md) — what happens when there is no signature and the guess is wrong
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — `to_bytes` and `from_bytes` in more detail
- [Why UTF-8 won](../../09_History/why_utf8_won/README.md) — property 5: no byte order, and no variants
- [UTF-8 everywhere](../../10_Best_Practices/utf8_everywhere/README.md) — where the read/write asymmetry belongs in a program
