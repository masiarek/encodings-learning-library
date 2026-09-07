# Hex: a number, or a picture of bytes

**Level:** 201 · for anyone who has met a hex dump

**One line:** The same run of hex digits is two different objects — a **number**, where the width is nothing and leading zeros are noise, and a **byte string**, where the width *is* the data and a leading zero is a NUL byte — and almost every hex bug is one of them read as the other.

## Two readings, and the string does not say which

[Hex is a shorthand](../hex_is_a_shorthand/README.md) settles what a hex digit is: four bits, so a byte is always two digits. This page is about the question that comes next and is rarely asked out loud. Take four digits:

```text
0041
```

| read as | it is | leading zeros | width | byte order |
|---|---|---|---|---|
| a **number** | 65 | noise — `0041` and `41` are equal | none; a number has no length | meaningless |
| a **byte string** | `00 41`, two bytes | data — the first byte is NUL | fixed; this field is two bytes long | a real question, unanswered |

Both readings are correct. Nothing in the string chooses between them, and nothing ever will — the choice lives in the field the string came out of, which is why *"the field is hex"* is not a specification and *"the field is four hex digits, two bytes, big-endian"* is.

The distinction sounds pedantic until you watch it break something. `int(s, 16)` is the reflex when a string "looks like a number", and it is the right call for an offset, a length, a colour or an error code. Apply it to a three-byte identifier and the value is never wrong and the *length* is destroyed:

```python
int("0004a1", 16)                       # 1185 — correct, and now one byte shorter
format(int("0004a1", 16), "x")          # '4a1' — three digits: not a whole number of bytes
bytes.fromhex(format(int("0004a1", 16), "x"))   # ValueError, several layers downstream
```

Nothing raises until the last line. That is the shape of the bug.

## A number has no byte order

This is the part the number reading hides most completely. `0041` as a *number* is 65 on every machine ever built. As *bytes* it is 65 or 16,640, depending on a convention the digits do not record — which is why `int.to_bytes` in Python has no default for its second argument and `u32::to_be_bytes` / `to_le_bytes` in Rust are two different methods rather than one with a flag. See [byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md); the point here is only that the question comes into existence at the moment you cross from one reading to the other, and did not exist before.

## An odd number of digits: fine, fatal, or silently halved

Three tools, one malformed input, three different answers:

| | `123` |
|---|---|
| `int("123", 16)` | **291** — a number needs no even width |
| `bytes.fromhex("123")` | **ValueError** — not a whole number of bytes |
| `printf '123' \| xxd -r -p` | **`0x12`** — the trailing nibble is dropped, exit 0, no message |

Only the middle one tells you. An odd-length hex field is nearly always a *truncated* one — a log line cut at a column limit, a copy-paste that lost a character — so the error is the answer you want, and the silent halving is the one that ships. `xxd -r -p` behaves the same way on a non-hex character: it stops, keeps what it had, and exits 0. It is an excellent encoder of hex you produced and a poor validator of hex somebody sent you.

**And the ValueError's *message* is not quotable.** CPython reworded it in 3.14, so the sentence you get is a fact about which interpreter ran rather than about hex:

```text title="Measured 2026-09-07 — one line, five CPython builds"
3.10.7, 3.12.0, 3.12.14, 3.13.11   non-hexadecimal number found in fromhex() arg at position 3
3.14.7                             fromhex() arg must contain an even number of hexadecimal digits
```

The program below therefore prints the exception *class* and says in its own words why the call refused. This is the rule [The table has a version](../../02_Characters/the_table_has_a_version/README.md) sets out for Unicode lookups, reaching one layer further: an interpreter's diagnostic text is not a property of your data either.

## The parsers do not agree about what a hex digit is

Same string, four languages, and the disagreement is not at the margins:

| input | Python `int(s,16)` | Rust `from_str_radix` | C `strtol` | `bash $((16#s))` |
|---|---|---|---|---|
| `41` | 65 | `Ok(65)` | 65 | 65 |
| `0x41` | 65 | `Err` | **65** — the prefix is part of base 16 in C | 65 |
| `4_1` | 65 | `Err` | **4**, silently, with `_1` left over | error |
| ` 41 ` | 65 | `Err` | **65** — leading space skipped | 65 |
| `-41` | −65 | `Err` | **−65** — a *byte field* can arrive negative | −65 |
| `4G` | ValueError | `Err` | **4**, silently | error |
| `٤١` | **65** | `Err` | 0, nothing converted | error |
| *(empty)* | ValueError | `Err` | 0, nothing converted | 0 |

Two rows deserve their own sentence.

**C converts what it can and returns it.** `strtol` is not a validator; it is a longest-prefix parser that reports nothing. `4G` gives you 4, `41xyz` gives you 65, and the only record of the rest of the string is `endptr`. `zz` and the empty string both give you 0 — which is also what a correct parse of `"0"` gives you, so the return value alone cannot distinguish success from total failure. `end == input` is the portable test for *nothing was converted*; `errno` after a failed conversion is implementation-defined and macOS and glibc genuinely differ, so the [C view](#the-c-view) below prints the pointer comparison and never `errno` itself.

**`٤١` is two ARABIC-INDIC digits, and Python returns 65.** They are not ASCII and not in `0123456789abcdefABCDEF`; `int()` accepts any character carrying a Unicode decimal digit value, in every base. So a field "validated" by `int(s, 16)` succeeding will accept digits that your regex, your database and your partner's parser all reject — a [parser differential](../../12_Adversarial/parser_differentials/README.md) sitting inside a one-line type check. (Those two characters are not in this library's [cast](../../CAST.md); nothing in the cast has the property, which is exactly why they are here.)

The habit that falls out: **`int(s, 16)` succeeding is not a validation.** If the field has a fixed width, check the length and the character set yourself, then decode — in that order, because after decoding the evidence is gone.

## The two doors

| | reach for | when the field is |
|---|---|---|
| a quantity | `int(s,16)` · `f"{n:x}"` · `$((16#s))` · `from_str_radix` | a length, an offset, a colour, a bitmask, an error code |
| data | `bytes.fromhex(s)` · `b.hex()` · `xxd -r -p` · a loop you wrote | a hash, a key, a certificate, a packet, an SAP `x`/`xstring` |

Left column: leading zeros cosmetic, width free, order meaningless, and a ceiling set by a type the string never mentions. Right column: leading zeros load-bearing, width fixed, order agreed in writing, and no maximum at all.

Rust makes the asymmetry visible by omission — `u32::from_str_radix` is in `std` and there is no `Vec<u8>::from_hex` anywhere in it. The moment a hex string is data you write the loop, and writing it is what forces the three decisions a hex string cannot make about itself: odd length, whitespace, and expected width. Every hex crate in the ecosystem answers those three differently.

## In Python

<!-- output:hex_number_or_bytes_py -->
*Verified output of [`hex_number_or_bytes_py.py`](examples/hex_number_or_bytes_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE STRING, TWO OBJECTS
------------------------------------------------------------------------
   the string                 '0041'
   int(s, 16)                 65         a number: 65, and nothing else is claimed
   bytes.fromhex(s)           b'\x00A'   two bytes: 00 41
   len of each                -          a number has no length; the bytes have 2

   Both readings are correct and they are not the same object. Which
   one a hex string means is not in the string -- it is in the field
   it came out of, and that is what an interface agreement is for.

2. LEADING ZEROS ARE NOISE, OR THEY ARE A NUL BYTE
------------------------------------------------------------------------
   a        b        int(a)==int(b)   fromhex                     
   '41'     '0041'   True             b'A' vs b'\x00A'            
   'ff'     '00ff'   True             b'\xff' vs b'\x00\xff'      
   '0a'     '00000a' True             b'\n' vs b'\x00\x00\n'      

   As numbers every row is a pair of equals. As bytes, no row is:
   '0041' is a NUL followed by an 'A', and a NUL byte is the one that
   truncates a C string, ends a field, or fails a database insert.
   Padding a number is cosmetic; padding a byte string is editing it.

3. A NUMBER HAS NO BYTE ORDER. BYTES DO.
------------------------------------------------------------------------
   (0x41).to_bytes(2, 'big')          00 41
   (0x41).to_bytes(2, 'little')       41 00
   and back, big                      65
   and back, little                   16640

   `to_bytes` will not let you leave the question out -- the argument
   has no default, because there is no right answer. Note what that
   means about the string in section 1: '0041' as a NUMBER is 65 on
   every machine ever built, and as BYTES it is 65 or 16640 depending
   on a convention the digits do not record.

4. AN ODD NUMBER OF DIGITS: FINE, FATAL, OR SILENTLY HALVED
------------------------------------------------------------------------
   int(odd, 16)               291          a number needs no even width
   bytes.fromhex(odd)         ValueError   three digits is not a whole number of bytes
   xxd -r -p (shell run)      0x12         drops the trailing nibble, exit 0, no message

   Three tools, three different answers to one malformed input, and
   only the middle one tells you. An odd-length hex field is almost
   always a truncated one -- a log line cut at a column limit, a copy
   that missed a character -- so the answer you want is the ValueError.

   The message is not printed above on purpose. CPython reworded it in
   3.14, so it is a fact about which interpreter ran, not about hex --
   the page names both wordings with a date.

5. WHAT int(s, 16) WILL SWALLOW
------------------------------------------------------------------------
   input        int(s, 16)     bytes.fromhex(s)    
   '41'         65             b'A'                
   '0x41'       65             ValueError          
   '0X41'       65             ValueError          
   '4_1'        65             ValueError          
   ' 41 '       65             b'A'                
   '41\n'       65             b'A'                
   '+41'        65             ValueError          
   '-41'        -65            ValueError          
   '٤١'         65             ValueError          
   '4G'         ValueError     ValueError          
   ''           ValueError     b''                 

   The prefix, an underscore, surrounding whitespace, a newline and a
   sign all pass. So does the ninth row, which is worth naming:
     '٤'  U+0664  ARABIC-INDIC DIGIT FOUR
     '١'  U+0661  ARABIC-INDIC DIGIT ONE
   Two ARABIC-INDIC digits -- not in this library's cast, and here
   because nothing else has the property: they are not ASCII, they
   are not in '0123456789abcdefABCDEF', and int() takes them anyway.
   int() accepts any Unicode character with a decimal digit value, in
   every base, so a hex field validated by `int(s, 16)` accepts digits
   your regex, your database and your partner's parser will not.

   And the last two rows are the pair to keep straight:
     int('', 16)          ValueError   -- no digits is not a number
     bytes.fromhex('')    b''          -- no digits is an empty file

6. SO: TWO DOORS, AND THE FIELD DECIDES WHICH ONE
------------------------------------------------------------------------
   int(s, 16) / f'{n:x}'         when the field is a QUANTITY
     a length, an offset, a colour, a bitmask, an error code
     -- leading zeros cosmetic, width free, order meaningless

   bytes.fromhex(s) / b.hex()    when the field is DATA
     a hash, a key, a certificate, a packet, an x/xstring from SAP
     -- leading zeros load-bearing, width fixed, order agreed in writing

   a three-byte field       '0004a1'
   as data                  00 04 a1   3 bytes, which is what it is
   as a quantity            1185
   written back out         '4a1'   the leading zero byte is gone
   and read as data again   ValueError -- five digits, not a whole
                            number of bytes

   That is the whole failure in four lines. Nothing raised until the
   very end, the value was never wrong as a number, and what came
   back is a different length from what went in. Reach for int()
   because a string 'looked like a number' and this is the shape of
   the bug you get -- usually much further downstream than here.
```
<!-- /output -->

## In the terminal

<!-- output:hex_number_or_bytes_sh -->
*Verified output of [`hex_number_or_bytes_sh.sh`](examples/hex_number_or_bytes_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE NUMBER DOOR, AND THE BASE IT ASSUMES
------------------------------------------------------------------------

   printf '%d' 0x41             65
   printf '%d' 41               41
   $(( 16#41 ))                 65
   $(( 0x41 ))                  65

   Rows one and two are the same command on the same-looking input
   and they differ by a factor of about one and a half. Without the
   0x, 41 is forty-one -- correct, silent, and wrong if the field was
   hex. $(( 16#41 )) is the spelling that cannot be misread, because
   the base is written where the value is, not inferred from a prefix.

2. THE BYTE DOOR
------------------------------------------------------------------------

   printf 'A' | xxd -p          41
   printf '\x41' | xxd -p       41
   printf '0041' | xxd -r -p    0041
   how many bytes is that       2

   xxd -r -p is the shell's bytes.fromhex: hex text in, bytes out,
   two digits per byte, leading zeros kept because they are bytes.
   Compare $(( 16#0041 )), which is 65 -- the same digits, one byte
   shorter, because a number has no width to keep.

3. AND IT DROPS WHAT IT CANNOT USE, WITHOUT SAYING SO
------------------------------------------------------------------------

   '123'        -> 12         exit 0
   'c3zzA9'     -> c3         exit 0
   'c3 a9'      -> c3a9       exit 0

   Three malformed or unusual inputs, three quiet answers and three
   zero exits. The first is an odd number of digits and the trailing
   nibble is simply gone. The second stops at the first character
   that is not a hex digit and keeps whatever it had. The third is
   the benign one -- whitespace between bytes really is allowed, and
   is what xxd -p emits with a width flag.

   So xxd -r -p is a fine encoder of hex you produced and a poor
   validator of hex somebody sent you. Nothing in this pipeline can
   tell a short field from a complete one; check the length yourself,
   before decoding, where the answer is still knowable.

4. THE ROUND TRIP THAT IS SAFE
------------------------------------------------------------------------

   the word                     café
   xxd -p                       636166c3a9
   xxd -p | xxd -r -p           café
   bytes in / bytes out         5 / 5

   xxd -p and xxd -r -p are inverses on anything xxd -p produced,
   which is the only guarantee either of them offers. Everything in
   section 3 was hex that xxd -p had never written.
```
<!-- /output -->

## In Rust

<!-- output:hex_number_or_bytes_rs -->
*Verified output of [`hex_number_or_bytes_rs.rs`](examples/hex_number_or_bytes_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE NUMBER DOOR IS STRICT ABOUT SPELLING AND BLIND TO WIDTH
------------------------------------------------------------------------

   input      u32::from_str_radix(s, 16)
   "41"       Ok(65)
   "0x41"     Err(invalid digit found in string)
   "4_1"      Err(invalid digit found in string)
   " 41 "     Err(invalid digit found in string)
   "+41"      Ok(65)
   "-41"      Err(invalid digit found in string)
   "41\n"     Err(invalid digit found in string)
   "4G"       Err(invalid digit found in string)
   ""         Err(cannot parse integer from empty string)
   "00041"    Ok(65)

   Compare Python, which accepts the first seven of those. Rust
   takes digits and an optional `+`, and nothing else -- no
   prefix, no underscore, no whitespace, no newline. But look at
   the last row: "00041" parses happily to 65, because leading
   zeros are noise in a number and there is no width to violate.
   Strictness about SPELLING is not strictness about MEANING.

2. THE WIDTH IS IN THE TYPE, NOT IN THE STRING
------------------------------------------------------------------------

   u8  "ff"     -> Ok(255)
   u8  "100"    -> Err("number too large to fit in target type")
   u32 "100"    -> Ok(256)

   "100" is three hex digits and fits no byte, and only the type
   knows that. This is the width that a hex string does not
   carry, supplied by the one place in Rust that always has it.
   In a dynamically typed language nothing asks the question at
   all, which is why the same string quietly becomes an int.

3. THE BYTE DOOR, WHICH YOU HAVE TO WRITE
------------------------------------------------------------------------

   "0041"   as a number     65   as bytes 00 41 (2 bytes)
   "41"     as a number     65   as bytes 41 (1 byte)
   "123"    as a number    291   as bytes Err(3 digits is not a whole number of bytes)
   "c3a9"   as a number  50089   as bytes c3 a9 (2 bytes)
   "c3zz"   as a number      -   as bytes Err('z' is not a hex digit)
   ""       as a number      -   as bytes nothing at all (0 bytes)

   Read the first two rows together: as numbers they are the
   same value, as bytes they are different lengths, and the
   difference is a NUL byte. The third is the odd-length case --
   which is an error here, an error in Python, and a silent
   truncation in `xxd -r -p`. The last is empty, which is a
   legitimate zero-byte value and not a number at all.

4. WHY THE OMISSION IS THE ARGUMENT
------------------------------------------------------------------------

   std::primitive::u32::from_str_radix   exists
   std::vec::Vec::<u8>::from_hex         does not exist

   Every hex-to-bytes crate in the ecosystem re-implements the
   twenty lines above, and they differ from each other exactly
   where this page says they would: whether whitespace is
   skipped, whether an odd length is an error or is left-padded,
   whether the output length is checked against an expected one.
   Those are not implementation details. They are the questions
   a hex string cannot answer about itself, and somebody has to.
```
<!-- /output -->

## The C view

<!-- output:hex_number_or_bytes_c -->
*Verified output of [`hex_number_or_bytes_c.c`](examples/hex_number_or_bytes_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. IT CONVERTS WHAT IT CAN AND RETURNS IT
------------------------------------------------------------------------

   input                        strtol(.., 16)  consumed  left over
   41                                       65  2         (nothing)
   0x41                                     65  4         (nothing)
     41                                     65  4         (nothing)
   +41                                      65  3         (nothing)
   -41                                     -65  3         (nothing)
   4_1                                       4  1         _1
   4G                                        4  1         G
   41xyz                                    65  2         xyz
   zz                                        0  0         zz
                                             0  0         (nothing)
   FFFFFFFFFFFFFFFFFF      9223372036854775807  18        (nothing)

   Only the first column is a return value. Rows 6, 7 and 8 all
   succeeded as far as C is concerned -- 4, 4 and 65 -- and the
   only trace of the rest of the string is the pointer. Row 9 and
   row 10 return 0, which is also what a correct parse of "0"
   returns, so the value alone cannot tell you they failed.

2. AND IT ACCEPTS THREE THINGS A BYTE FIELD SHOULD NOT
------------------------------------------------------------------------

   "0x41"                 the prefix is part of base 16 in C, by the standard
   "  41"                 leading whitespace is skipped before anything else
   "-41"                  a sign is allowed, so a hex FIELD can arrive negative

   The third is the one that surprises people. A two-digit hex
   field is a byte, bytes have no sign, and strtol will hand you
   -65 for "-41" without a murmur -- into a long, which is signed,
   so the assignment to an unsigned char later is where it wraps.

3. THE CHECKS THAT ARE PORTABLE
------------------------------------------------------------------------

   input                  no digits    trailing     ERANGE
   41                     no           no           no
   0x41                   no           no           no
     41                   no           no           no
   +41                    no           no           no
   -41                    no           no           no
   4_1                    no           yes          no
   4G                     no           yes          no
   41xyz                  no           yes          no
   zz                     yes          no           no
                          yes          no           no
   FFFFFFFFFFFFFFFFFF     no           no           yes

   Three questions, three answers, and none of them is the return
   value. `end == input` is the only portable way to learn that
   nothing was converted, and ERANGE on overflow is the only errno
   the standard promises: after a failed conversion errno is
   implementation-defined, and macOS and glibc genuinely differ.
   This program therefore prints the pointer comparison and never
   errno itself -- the same discipline the rest of the library
   applies to any answer that belongs to the machine.

4. WHAT THE OVERFLOW ROW IS REALLY SAYING
------------------------------------------------------------------------

   LONG_MAX on this build is 9223372036854775807, 8 bytes wide.
   "FFFFFFFFFFFFFFFFFF" is 18 hex digits, so 9 bytes of data --
   perfectly ordinary as a field, and unrepresentable as a long.
   The number door has a ceiling and the byte door does not, which
   is the same distinction one more time: a hex string that is
   DATA has no maximum, and a hex string that is a QUANTITY is
   bounded by a type it never mentions.
```
<!-- /output -->

## The reference article, and who it is written for

Wikipedia's [Hexadecimal ↗](https://en.wikipedia.org/wiki/Hexadecimal) is worth a paragraph here, and the verdict is different from the one on [Binary to text](../../03_Encodings/binary_to_text/README.md). That article is neglected — two maintenance banners open since 2010 and 2012. This one is not: it is careful, well sourced, and carries no cleanup tags at all. It is simply **written for a different reader than the one who arrives**.

Measured on the article's own wikitext, 2026-09-07 — 65,635 bytes, by top-level section:

| section | share |
|---|---|
| Written representation | 30.7% |
| **Real numbers** — base-16 fractions, repeating expansions, irrationals, powers | **26.7%** |
| **Cultural history** — including the etymology of the name | **13.1%** |
| Conversion — by-hand methods | 9.1% |
| Verbal representation — how to say it aloud | 6.3% |
| **Base16** — hex as an encoding of bytes | **2.3%** |
| Elementary arithmetic | 0.8% |

Forty percent of it is base 16 as a *numeral system*: which rationals terminate in hex given that sixteen has one prime factor, tables of reciprocals, the expansion of irrationals. That is real mathematics, correctly presented, and nobody who opened the page because a hex dump was on screen needs any of it. Meanwhile hex-as-an-encoding — the thing in front of that reader — gets 2.3%, and even there the framing is the efficiency percentage that [the binary-to-text article](../../03_Encodings/binary_to_text/README.md) leans on too.

The consequence is the one this page exists for. **A number has no width, so an article about numbers cannot mention the distinction that causes hex bugs.** Nowhere in 65 kilobytes is there a sentence about a leading zero being a byte, an odd-length field being a truncation, or a parser accepting a sign in a byte column — not through carelessness, but because those facts do not exist in the subject it chose.

Two other sections are worth knowing about for what they are. *Alternative symbols* is a fine catalogue of machines that used other digits — the SWAC and Bendix G-15 wrote 10–15 as `u v w x y z`, the ORDVAC and ILLIAC I as `K S N J F L`, the LGP-30 as `F G J K Q W`. *Verbal representation* collects proposals for saying hex out loud, including a 1968 naming scheme (`ann`, `bet`, `chris`, `dot`, `ernest`, `frost`) and a Morse-style dit/dah convention. Both are genuine history and neither is advice: no working programmer has used any of them in fifty years, and the practical answer — read the digits out singly, and say "oh" for `0` only if everyone present already knows you mean zero — is not in the article at all.

So: not a bad article. A good article about the other hexadecimal.

## If you are coming from Python or ABAP

**Python.** The two doors are `int(s, 16)` / `format(n, '02x')` and `bytes.fromhex(s)` / `b.hex()`, and the habit worth forming is to know which one a field wants *before* you touch it. Three details from the run above: `bytes.fromhex` skips ASCII whitespace (so `'c3 a9'` and a hex dump pasted across lines both work) but nothing else; `bytes.fromhex('')` is `b''` while `int('', 16)` raises, which is correct in both cases — an empty field is a legitimate zero-byte value and not a number; and `int(s, 16)` accepts a great deal more than you think, so it is a conversion and never a check. See [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) for the four conversions together.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* ABAP is unusual in having chosen the *byte* reading as the default: `TYPE x` and `xstring` are written and displayed as hex, two digits per byte, always, and the leading zeros are simply part of the value — `DATA b TYPE x LENGTH 2 VALUE '0041'.` is two bytes and stays two bytes. The number door is the explicit one, and it is where the care is needed: converting an `x` field to an integer type goes through the platform's byte order, so a hex field that arrived from an interface should be read as bytes and only turned into a number when something genuinely needs its magnitude. `cl_abap_conv_codepage` and the `xstrlen( )` / `strlen( )` pair are the tools; the rule to carry over is the same as everywhere else on this page — decide which of the two objects the field is, in writing, before the first conversion.

## Try it

```bash
cd 01_Bits_and_Bytes/hex_number_or_bytes/examples
python3 hex_number_or_bytes_py.py
bash hex_number_or_bytes_sh.sh
rustc --edition 2024 hex_number_or_bytes_rs.rs -o /tmp/hnb && /tmp/hnb
cc -std=c11 -Wall -Wextra hex_number_or_bytes_c.c -o /tmp/hnb_c && /tmp/hnb_c
```

Three one-liners that make the point on their own:

```bash
printf '%d\n' 41                      # 41 — decimal, silently, if you forgot the 0x
printf '123' | xxd -r -p | xxd -p     # 12 — a nibble vanished, exit 0
python3 -c "print(int('٤١', 16))"     # 65 — from two Arabic-Indic digits
```

Without the machine: an interface sends you a 32-character field described as "the hash, in hex". One day it arrives with 31 characters. Say what each of the three tools above would do with it, which of them you want, and where in your program the check belongs.

## See also

- [Hex is a shorthand](../hex_is_a_shorthand/README.md) — one digit is four bits, and the spellings; the page this one continues
- [Reading a hex dump](../reading_a_hex_dump/README.md) — where you meet the byte reading sixteen at a time
- [Binary to text](../../03_Encodings/binary_to_text/README.md) — Base16 is the 4-bit member of that family, and the one whose quantum is a whole nibble
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — the question that appears the moment a number becomes bytes
- [Parser differentials](../../12_Adversarial/parser_differentials/README.md) — the general shape of two readers disagreeing about one string
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — why "it parsed" is not "it is valid"
- [`hexdump` is a format engine wearing six presets](../../11_Tools/hexdump/README.md) — the tool side of the byte reading
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — the four Python conversions, together
