# Inspecting a file with `od`

**Level:** 101 → 201 · for anyone with a terminal

**One line:** In a hex dump exactly one column is the file — the hex — and every other column is a tool answering a question you did not ask, in a dialect that changes with your locale and your operating system.

## The session

This is the whole job in nine commands: write a line of text, look at its size, look at its bytes, re-encode it, look again. It is worth reading before the explanation, because every surprise on this page is visible in it.

```text title="A terminal session on a Mac — the file is 'Käse: 1€'"
$ cat demo.txt
Käse: 1€
$ ls -l demo.txt
-rw-r--r--  1 dret  staff  12 Sep  5 15:16 demo.txt
$ od -at x1 demo.txt
0000000     K   ?   ?   s   e   :  sp   1   ?  82   ?  nl
           4b  c3  a4  73  65  3a  20  31  e2  82  ac  0a
0000014
$ iconv -f utf-8 -t utf-16 demo.txt > demo-16.txt
$ ls -l demo-16.txt
-rw-r--r--  1 dret  staff  20 Sep  5 15:18 demo-16.txt
$ od -at x1 demo-16.txt
0000000     ?   ? nul   K nul   ? nul   s nul   e nul   : nul  sp nul   1
           fe  ff  00  4b  00  e4  00  73  00  65  00  3a  00  20  00  31
0000020    sp   ? nul  nl
           20  ac  00  0a
0000024
```

Eight characters and a newline. `ls -l` says **12**, because `ls -l` has always counted bytes. `iconv` turns it into **20**. And the top row of each dump — the one that looks like it is showing you the text — contains four question marks, a stray `82`, and a byte of the `€` politely labelled `sp`.

No example on this page uses `ä` — only the quoted session above does — because the library has [a fixed cast](../../CAST.md) and `é` is already the two-byte character every reader here has met. `café: 1€` has the same shape as the line above — seven one-byte characters, one two-byte, one three-byte — and gives the same numbers: nine characters, twelve bytes, twenty after `iconv`.

## Four questions, and which tool answers which

| Question | Ask | Not |
|---|---|---|
| How many **bytes**? | `wc -c`, or the size column of `ls -l` | anything about characters |
| How many **characters**? | `wc -m` **in a UTF-8 locale** | `wc -m` in the C locale, which counts bytes and says so to nobody |
| What **are** the bytes? | `xxd`, `hexdump -C`, `od -An -tx1` | the named-character row (below) |
| What **encoding** is it? | nothing can tell you — [`file` guesses](../file_guesses/README.md), and a BOM is a hint | any of the above |

The first two are different questions, and the whole library is about the gap between them. The third is the only one with a single answer everywhere. The fourth has no answer at all: an encoding is an agreement about how to read bytes, and it is not stored in the file.

## The row that makes things up

`od -a` prints "named characters", and that row is the least trustworthy output on this page. Two implementations print it, and they disagree about every byte above 127.

**GNU `od`** (Linux) masks the high bit off and names whatever is left. `c3` becomes `0x43`, which is `C`. Not a guess about the text — arithmetic on the byte, and the answer is a letter that appears nowhere in the file.

**BSD `od`** (macOS) asks `isprint()` in your current locale. In a UTF-8 locale that question is answered over U+0080–U+00FF, so `c3` is `Ã`, `a4` is `¤`, `ac` is `¬` — all printable, so od writes **the raw byte**. Your terminal then tries to read that lone byte as UTF-8, fails, and draws `?`. The question marks in the session above were never od's output:

```text title="Measured on macOS 25.6, en_US.UTF-8, 2026-09-05 — not machine-checked; the whole point is that it varies"
$ od -a demo.txt | xxd | head -3
00000000: 3030 3030 3030 3020 2020 2063 2020 2061  0000000    c   a
00000010: 2020 2066 2020 20c3 2020 20a9 2020 203a     f   .   .   :
00000020: 2020 7370 2020 2031 2020 20e2 2020 3832    sp   1   .  82
```

There is the `c3`, sitting in od's own output stream between two runs of padding spaces. od emitted a byte; the terminal drew the `?`.

That also explains the one detail in the session that looks like a typo — why `82` shows a **hex number** while the bytes either side of it show `?`. U+0082 is a C1 **control** character, so `isprint()` says no, and od falls through to its last branch, which is the only honest one it has. Of the three bytes in `€` (`e2 82 ac`), exactly one is a control code point, so exactly one prints as a number. That is a fact about `isprint()` and a locale. It is not a fact about the file.

Set `LC_ALL=C` and the same command on the same file prints `c3 a9` and `e2 82 ac` as plain hex, with no `?` anywhere. Same file, same tool, same machine, different answer.

So this is the **fifth** BSD/GNU difference [this library records](../../CONTRIBUTING.md), and the first that is a difference of *content* rather than whitespace — the `tidy` helper the other shell examples pipe `od` through cannot rescue it, because there is no layout that makes `C` and `Ã` agree. No example here records `od -a` output. Reach for `od -An -tx1`, or `xxd`, or `hexdump -C`; use `od -c` when you want octal escapes, and set `LC_ALL=C` when you do, because in a UTF-8 locale macOS `od -c` decodes multi-byte characters and prints `**` for the continuation bytes.

## `iconv`: the same characters, different bytes

`iconv -f utf-8 -t utf-16` re-encodes. It does not change the text, and it changes almost everything about the file: 12 bytes become 20, a BOM appears at the front, and half of the new bytes are `00` — which is why UTF-16 text handed to anything expecting a C string looks like it ends after one character.

It also silently picks a byte order. On macOS the session above got `fe ff` — big-endian. The same command on GNU writes `ff fe`, little-endian, so the same file re-encoded on two machines gives two different files. Always name it: `-t UTF-16BE` or `-t UTF-16LE`. (The `BE`/`LE` forms also write **no** BOM, which is the other half of the size arithmetic: 18 bytes of text, plus 2 for the mark.) The mark itself, and why `fe ff` can be trusted as evidence, is [byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md); `iconv`'s own refusals and its `//TRANSLIT` suffix are [its page](../iconv/README.md).

One last look at the UTF-16 dump, because it is the sharpest thing in the session. The `€` became the single code unit `20 ac`, and `od` names that first byte **`sp`** — a space — because `0x20` *is* the code point of a space. `xxd` does the same thing more quietly: its text column shows an actual blank there. A byte-oriented tool cannot see characters, and in UTF-16 it does not even get the boundaries right by accident the way it does in ASCII.

## In the terminal

<!-- output:inspecting_a_file_sh -->
*Verified output of [`inspecting_a_file_sh.sh`](examples/inspecting_a_file_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE HONEST VIEW: three tools, one file, the same twelve bytes

$ printf 'caf\303\251: 1\342\202\254\n' | xxd
00000000: 6361 66c3 a93a 2031 e282 ac0a            caf..: 1....

$ printf 'caf\303\251: 1\342\202\254\n' | hexdump -C
00000000  63 61 66 c3 a9 3a 20 31  e2 82 ac 0a              |caf..: 1....|
0000000c

$ printf 'caf\303\251: 1\342\202\254\n' | od -An -tx1 | tidy
  63  61  66  c3  a9  3a  20  31  e2  82  ac  0a
   Nine characters, twelve bytes. Every tool agrees, because this column IS the file.

2. HOW BIG IS IT? wc -c counts bytes — the same number ls -l shows in its size column

$ printf 'caf\303\251: 1\342\202\254\n' | wc -c | tr -d ' '
12

3. HOW MANY CHARACTERS? wc -m, and the answer depends on the locale

$ printf 'caf\303\251: 1\342\202\254\n' | LC_ALL=C wc -m | tr -d ' '
12
   ^ in the C locale, 'character' means 'byte', so this is the wrong question answered 12

$ printf "$LINE" | LC_ALL=$UTF8 wc -m | tr -d " "
9
   ^ in a UTF-8 locale the same command decodes first and says 9. Same file, same tool.

4. od -c: the octal escape, for bytes it has no character for

$ printf 'caf\303\251\n' | od -An -tx1 -c | tidy
  63  61  66  c3  a9  0a
   c   a   f 303 251  \n
   c a f, then 303 251 for the é — two bytes, no character to draw for either.
   (od -a, the NAMED-character row, is the one column to distrust: it is
    locale-dependent on macOS and high-bit-stripped on GNU. See the page.)

5. iconv: the same nine characters, re-encoded to UTF-16 — name the byte order

$ printf 'caf\303\251: 1\342\202\254\n' | iconv -f UTF-8 -t UTF-16BE | xxd
00000000: 0063 0061 0066 00e9 003a 0020 0031 20ac  .c.a.f...:. .1 .
00000010: 000a                                     ..

$ printf 'caf\303\251: 1\342\202\254\n' | iconv -f UTF-8 -t UTF-16LE | xxd
00000000: 6300 6100 6600 e900 3a00 2000 3100 ac20  c.a.f...:. .1.. 
00000010: 0a00                                     ..
   Same characters, mirrored bytes. Ask for plain UTF-16 and the tool chooses
   for you — big-endian on macOS, little-endian on GNU — and adds a BOM.

6. THE 20-BYTE FILE, rebuilt portably: a BOM, then UTF-16BE

$ { printf '\376\377'; printf 'caf\303\251: 1\342\202\254\n' | iconv -f UTF-8 -t UTF-16BE; } | xxd
00000000: feff 0063 0061 0066 00e9 003a 0020 0031  ...c.a.f...:. .1
00000010: 20ac 000a                                 ...

$ { printf '\376\377'; printf 'caf\303\251: 1\342\202\254\n' | iconv -f UTF-8 -t UTF-16BE; } | wc -c | tr -d ' '
20
   12 bytes became 20: two for the BOM, two per character, for text that was
   mostly ASCII. Look at the € — its code unit is 20 ac, and xxd's text column
   shows a SPACE for that 20, because half a character still looks like a byte.
```
<!-- /output -->

## In Python

The two `od -a` rules are short enough to write out, and applying them as arithmetic makes the fiction reproducible — the same output on every machine, which the tools themselves cannot manage.

<!-- output:inspecting_a_file_py -->
*Verified output of [`inspecting_a_file_py.py`](examples/inspecting_a_file_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE LINE OF TEXT, TWO DIFFERENT COUNTS
   text        'café: 1€'
   characters  9 (with the newline)
   bytes       12  <- this is the number ls -l and wc -c report
   hex         63 61 66 c3 a9 3a 20 31 e2 82 ac 0a

2. WHERE EACH CHARACTER SITS IN THE BYTES
   'c'    U+0063  1 byte(s)  offset 0      63
   'a'    U+0061  1 byte(s)  offset 1      61
   'f'    U+0066  1 byte(s)  offset 2      66
   'é'    U+00E9  2 byte(s)  offset 3..4   c3 a9
   ':'    U+003A  1 byte(s)  offset 5      3a
   ' '    U+0020  1 byte(s)  offset 6      20
   '1'    U+0031  1 byte(s)  offset 7      31
   '€'    U+20AC  3 byte(s)  offset 8..10  e2 82 ac

3. THE NAMED-CHARACTER ROW, BY BOTH RULES
   byte  hex   GNU od -a   BSD od -a (UTF-8 locale)   what the byte really is
      0  63    c           c                        'c' (whole)
      1  61    a           a                        'a' (whole)
      2  66    f           f                        'f' (whole)
      3  c3    C           raw byte (terminal: ?)   'é' (byte 1 of 2)
      4  a9    )           raw byte (terminal: ?)   'é' (byte 2 of 2)
      5  3a    :           :                        ':' (whole)
      6  20    sp          sp                       ' ' (whole)
      7  31    1           1                        '1' (whole)
      8  e2    b           raw byte (terminal: ?)   '€' (byte 1 of 3)
      9  82    stx         hex number               '€' (byte 2 of 3)
     10  ac    ,           raw byte (terminal: ?)   '€' (byte 3 of 3)
     11  0a    nl          nl                       the newline

4. WHY ONE BYTE OF THE THREE-BYTE € PRINTS AS A NUMBER AND THE OTHERS DO NOT
   e2 -> U+00E2 printable  =>  BSD od prints the raw byte
   82 -> U+0082 a C1 CONTROL, not printable  =>  BSD od prints the hex number 82
   ac -> U+00AC printable  =>  BSD od prints the raw byte
   So in a dump of this file, exactly one of the three € bytes shows a number.
   That is a fact about isprint() and a locale. It is not a fact about the file.

5. THE SAME NINE CHARACTERS, RE-ENCODED (what iconv does)
   UTF-8              12 bytes  63 61 66 c3 a9 3a 20 31 e2 82 ac 0a
   UTF-16BE, no BOM   18 bytes  00 63 00 61 00 66 00 e9 00 3a 00 20 00 31 20 ac 00 0a
   UTF-16BE + BOM     20 bytes  fe ff 00 63 00 61 00 66 00 e9 00 3a 00 20 00 31 20 ac 00 0a
   UTF-16LE + BOM     20 bytes  ff fe 63 00 61 00 66 00 e9 00 3a 00 20 00 31 00 ac 20 0a 00
   Mostly-ASCII text costs MORE in UTF-16, and gains bytes that are 00.

6. WHEN UTF-16 IS THE SMALLER FILE (no newline; the text goes last, so nothing
   has to align after a wide glyph)
   8 chars   UTF-8 11 bytes   UTF-16 16 bytes   UTF-8 wins    'café: 1€'
   3 chars   UTF-8  9 bytes   UTF-16  6 bytes   UTF-16 wins   '日本語'
   Neither encoding is 'smaller'. It depends entirely on the text.
```
<!-- /output -->

## In Rust

<!-- output:inspecting_a_file_rs -->
*Verified output of [`inspecting_a_file_rs.rs`](examples/inspecting_a_file_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE TWO COUNTS A DUMP CANNOT TELL APART
   text                "café: 1€\n"
   text.len()          12  <- BYTES, the ls -l number
   chars().count()     9  <- characters
   as_bytes() in hex   63 61 66 c3 a9 3a 20 31 e2 82 ac 0a 

2. WHERE EVERY CHARACTER STARTS — the offsets a dump makes you count by hand
   offset  0  c   U+0063  1 byte(s)  63 
   offset  1  a   U+0061  1 byte(s)  61 
   offset  2  f   U+0066  1 byte(s)  66 
   offset  3  é   U+00E9  2 byte(s)  c3 a9 
   offset  5  :   U+003A  1 byte(s)  3a 
   offset  6      U+0020  1 byte(s)  20 
   offset  7  1   U+0031  1 byte(s)  31 
   offset  8  €   U+20AC  3 byte(s)  e2 82 ac 
   offset 11  \n  U+000A  1 byte(s)  0a 

3. THE BYTES A DUMP SHOWS THAT ARE NOT CHARACTERS
   byte 9 of this file is 0x82. On its own it is not a character at all:
   char::from_u32(0x82) = Some('\u{82}') (a C1 control), and as a UTF-8 fragment
   it is only ever the middle of the €. Rust will not hand it to you as text:
   text.get(9..10) = None   <- None: that range splits a character
   text.get(8..11) = Some("€")    <- Some: the whole €

4. RE-ENCODED TO UTF-16, THE WAY iconv WOULD
   9 code units for 9 characters
   big-endian bytes    fe ff 00 63 00 61 00 66 00 e9 00 3a 00 20 00 31 20 ac 00 0a 
   2 bytes of BOM + 18 = 20 bytes, where UTF-8 needed 12

5. THE € CODE UNIT, AND WHY A BYTE TOOL CALLS ITS FIRST HALF A SPACE
   '€' is U+20AC, so its UTF-16 code unit is 0x20AC
   written big-endian that is the two bytes 20 ac
   and 0x20 is also the code point of ' ' — so od -a names it "sp"
   and xxd's text column draws a space. Half a character still looks like a byte.
```
<!-- /output -->

`text.get(9..10)` returning `None` is the difference between a dump and a type. Byte 9 is the middle of the `€`; the dump will hand it to you in a column of its own and even give it a name, while `&str` refuses to produce a slice that starts inside a character. Full story in [slicing by byte](../../05_Rust/slicing_by_byte/README.md).

## If you are coming from Python or ABAP

**Python.** `len(data)` on `bytes` is `wc -c`; `len(text)` on `str` is `wc -m` in a UTF-8 locale. The trap has the same shape as the terminal's: `print(data)` shows you Python's `repr` of the bytes, with its own printable/escape rule (`b'caf\xc3\xa9'`), so what you are reading is a *rendering* and not the file. `data.hex(' ')` is the one column that is the file, and it is the one to paste into a bug report.

**ABAP.** `xstrlen( )` against `strlen( )` is exactly this page: bytes against characters, and the two differ the moment a non-ASCII character arrives from a file, an RFC or an IDoc. The debugger's `xstring` view is the hex column with no name row attached, which is the honest form. Convert deliberately with `cl_abap_codepage=>convert_to( source = text codepage = 'UTF-8' )` rather than assigning between a `string` and an `xstring` and hoping; and when a value looks wrong after a file read, look at the `xstring` before deciding whose fault it is — usually the bytes are fine and the reader applied the wrong agreement. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 06_Terminal/inspecting_a_file/examples
bash inspecting_a_file_sh.sh
python3 inspecting_a_file_py.py
rustc --edition 2024 inspecting_a_file_rs.rs -o /tmp/insp && /tmp/insp
```

Then run the row this page told you not to trust, twice, on a file of your own:

```bash
printf 'caf\303\251: 1\342\202\254\n' > /tmp/demo.txt
LC_ALL=C            od -a /tmp/demo.txt
LC_ALL=en_US.UTF-8  od -a /tmp/demo.txt
od -a /tmp/demo.txt | xxd | head -3
```

The first two print different rows for identical bytes. The third shows you what od actually wrote.

## See also

- [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) — the three columns, and the tools that print them
- [Locale and `LC_CTYPE`](../locale_and_lc_ctype/README.md) — the setting that changed the row
- [Control characters](../../02_Characters/control_characters/README.md) — what U+0082 is, and why nothing can draw it
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — the `fe ff` that `iconv` chose for you
- [`file` guesses](../file_guesses/README.md) — the tool that answers the fourth question, and how sure it is
