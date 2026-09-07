# Rotation is not encryption

**Level:** 101 → 201 · for anyone starting from zero

**One line:** ROT13 is not encryption but arithmetic on the ASCII layout — the shift is published in its own name, so the keyspace has exactly one element. And the two things that make it feel elegant, that it is a single sum and that the byte count never moves, are facts about where ASCII put the letters: rotate past ASCII and you lose both.

## One shape, four names

A **substitution cipher** replaces each character with another one, using a table that is fixed for the whole message. That table is the entire method. Everything in the family below is the same shape with a different rule for filling it in:

```text
Plaintext:   abcdefghijklmnopqrstuvwxyz
Caesar (3):  defghijklmnopqrstuvwxyzabc     (x + 3)  mod 26
ROT13:       nopqrstuvwxyzabcdefghijklm     (x + 13) mod 26
Atbash:      zyxwvutsrqponmlkjihgfedcba     25 - x
Affine:      insxchmrwbglqvafkpuzejotyd     (5x + 8) mod 26
```

Rotation is the case where the table can be written as one sum, and that is why it is the one you meet in a shell one-liner. It is not a different *kind* of thing from the other three — the sum is a convenience for the person implementing it, not a property of the cipher.

## The layout picks the number

Why 13? Because there are 26 letters and 13 is half of them, so applying it twice returns the input. That is not a fact about cryptography; it is a fact about [where the committee put the letters](../a_character_is_a_number/README.md). Every member of the ROT family is named after half the size of a **contiguous range in the table**:

| Variant | The range it rotates | Size | Shift |
|---|---|---|---|
| ROT5 | `0`–`9`, `0x30`–`0x39` | 10 | 5 |
| ROT13 | `A`–`Z` and `a`–`z`, `0x41`–`0x5A` and `0x61`–`0x7A` | 26 | 13 |
| ROT18 | both of the above at once | — | 13 and 5 |
| ROT47 | every printable ASCII character, `0x21`–`0x7E` | 94 | 47 |

Change the table and the arithmetic changes with it. In [EBCDIC](../code_pages/README.md) the letters are **not** contiguous: in cp037 `a`–`i` is `0x81`–`0x89`, then `j` jumps to `0x91` and `s` to `0xA2`. Two gaps, so `(x + 13)` is not ROT13 there and there is no one-line spelling of it at all. The trick belongs to ASCII, not to text.

## There is no key

This is the part worth carrying away. A cipher's key is the thing you keep and your opponent does not have. ROT13's shift is **published in its name**, so its keyspace has exactly one element, and the "ciphertext" is readable by anyone who has met it once. It is not weak encryption. It is not encryption.

What it actually is, is a **convention**: a rewriting whose rule everyone knows, used on Usenet so that a punchline or a spoiler would not be readable by accident. The job is to stop your *eye*, and it does that job perfectly. This library already says the same sentence about a different rewriting, on [Binary to text](../../03_Encodings/binary_to_text/README.md): Base64 *"is not encryption, not obfuscation and not a checksum"*, and `aHVudGVyMg==` is `hunter2` to anybody who has ever seen the alphabet. ROT13 is that claim with a smaller alphabet.

Python agrees, in the most literal way available to it: **`rot_13` ships inside the `encodings` package**, next to `utf_8` and `latin_1`. Not in a crypto module — there isn't one in the standard library — but with the codecs. And the `encode` method still refuses it, because [encode means `str` → `bytes`](../../03_Encodings/encode_and_decode_are_verbs/README.md) and this is `str` → `str`. Both facts are in section 5 below, and together they are the answer to "which shelf does this go on".

## Rotate past ASCII and it stops being a rotation

The variant list usually ends with **ROT8000**, which rotates over a large slice of Unicode instead of the alphabet. It sounds like more of the same, and it is a different thing entirely, for two reasons this library is exactly the right place to see.

**The size changes.** Every ROT13 output byte is still one byte, because the result never leaves the 7-bit range. Rotate the *code point* by `0x2000` and each of five ASCII characters becomes three UTF-8 bytes — same five characters, fifteen bytes. A transformation that triples the size of its input is not rotating an alphabet; it is re-encoding.

**The number line has holes.** `h` is `U+0068`; add `0x2000` and you land on `U+2068`, which is not a letter at all but FIRST STRONG ISOLATE, an invisible [bidirectional formatting character](../logical_and_visual_order/README.md) that changes how everything after it is displayed — the same class of character the [Trojan Source](../../12_Adversarial/trojan_source/README.md) attack is built from. Some destinations are worse: `U+D800` is a [surrogate](../../03_Encodings/utf16_and_surrogates/README.md), permanently reserved, and no UTF-8 file may contain one. Rust will not even construct it. So a rotation over Unicode has to carry a **list of which code points it may produce**, and once you are carrying a list you have lost the one thing rotation had going for it.

## Where this page stops

The paragraph above the code fence at the top of this page — the Caesar, Atbash and affine alphabets — is as far as this library goes into ciphers, on purpose.

The line is not *how complicated the table is*; it is **whether there is a secret**. As long as the rule is published, a substitution table is a re-labelling of a character set, which is this library's subject and is why ROT13 lives here. The moment the shift is something you are trying not to reveal, the questions change to *how large is the keyspace*, *what does an attacker see*, and *how long does it take* — and none of those are answered by knowing anything about ASCII.

Section 4 of the Python example shows the shallow end of it: 26 shifts, printed in a column, and you read the plaintext off the screen. That is a ciphertext-only attack, and it is a *reading* exercise. A general substitution alphabet has 26! ≈ 4.03 × 10²⁶ possible tables, far too many to print, and it still falls in an afternoon — because letters are not equally common in English, so counting them recovers the table. **[Frequency analysis ↗](https://en.wikipedia.org/wiki/Frequency_analysis) is the real subject there, and it is a fact about language, not about encodings.** A page that explained it would be a cryptography page in an encodings library, so it is not here.

## In Python

<!-- output:rotation_is_not_encryption_py -->
*Verified output of [`rotation_is_not_encryption_py.py`](examples/rotation_is_not_encryption_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A SUBSTITUTION CIPHER IS A LOOKUP TABLE. ROTATION IS ONE FORMULA FOR IT.
   plaintext alphabet   abcdefghijklmnopqrstuvwxyz
   ciphertext alphabet  nopqrstuvwxyzabcdefghijklm   <- ROT13, built by (x + 13) % 26
   ciphertext alphabet  defghijklmnopqrstuvwxyzabc   <- shift 3, the Caesar of the books
   The table IS the key. Rotation just means you can write the table as one sum.

2. ROT13 IS ITS OWN INVERSE, BECAUSE 13 + 13 = 26
   'Hello, World!' -> 'Uryyb, Jbeyq!' -> 'Hello, World!'
   One function both ways. Nothing in the program knows which direction it is going.

3. THE ROTATION IS ARITHMETIC ON THE ASCII LAYOUT, SO THE LAYOUT PICKS THE NUMBER
   A..Z        is 26 contiguous code points, half of it is 13   -> ROT13
   0..9        is 10 contiguous code points, half of it is  5   -> ROT5
   0x21..0x7E  is 94 contiguous code points, half of it is 47   -> ROT47
   ROT5  on '2026-09-07'    -> 7571-54-52
   ROT47 on 'Hello, World!' -> w6==@[ (@C=5P
   ROT47 twice              -> Hello, World!
   ROT18 is just ROT13 for the letters and ROT5 for the digits, done at once.
   Each of those numbers is half the size of a RANGE IN THE TABLE. Nothing else.

4. THERE IS NO KEY. THE WHOLE KEYSPACE OF A ROTATION FITS ON THIS SCREEN.
   ciphertext: 'nggnpx ng qnja'
   shift  0: nggnpx ng qnja
   shift  1: ohhoqy oh rokb
   shift  2: piiprz pi splc
   shift  3: qjjqsa qj tqmd
   shift  4: rkkrtb rk urne
   shift  5: sllsuc sl vsof
   shift  6: tmmtvd tm wtpg
   shift  7: unnuwe un xuqh
   shift  8: voovxf vo yvri
   shift  9: wppwyg wp zwsj
   shift 10: xqqxzh xq axtk
   shift 11: yrryai yr byul
   shift 12: zsszbj zs czvm
   shift 13: attack at dawn  <- the plaintext, and you found it by reading
   shift 14: buubdl bu ebxo
   shift 15: cvvcem cv fcyp
   shift 16: dwwdfn dw gdzq
   shift 17: exxego ex hear
   shift 18: fyyfhp fy ifbs
   shift 19: gzzgiq gz jgct
   shift 20: haahjr ha khdu
   shift 21: ibbiks ib liev
   shift 22: jccjlt jc mjfw
   shift 23: kddkmu kd nkgx
   shift 24: leelnv le olhy
   shift 25: mffmow mf pmiz
   25 wrong lines and one right one, and no computer was needed to pick it.
   For ROT13 it is worse than that: the shift is published, so the keyspace is 1.

5. PYTHON FILES ROT13 UNDER encodings/ -- AND encode() STILL REFUSES IT
   the module is  encodings.rot_13   (package: encodings)
   the registry knows it as  'rot-13'
   'abc'.encode('rot13')  raises  LookupError
   codecs.encode('abc', 'rot13')  ->  'nop'
   Both facts are right. It lives with the encodings because it is a rewriting
   with a published rule; encode() rejects it because encode() means str -> bytes,
   and this is str -> str. A cipher that fits in the encodings package is not
   protecting anything.

6. INSIDE ASCII THE BYTE COUNT CANNOT MOVE. OUTSIDE IT, IT DOES.
   plain       5 characters    5 UTF-8 bytes
   ROT13       5 characters    5 UTF-8 bytes
   ROT47       5 characters    5 UTF-8 bytes
   +0x2000     5 characters   15 UTF-8 bytes
   Rotating inside a 7-bit range is free: every result is still one byte.
   Rotate the code point instead and the same five characters cost fifteen bytes.

7. AND ROTATING THE CODE POINT LANDS WHEREVER THE ARITHMETIC SAYS
   'h' is U+0068.  U+0068 + 0x2000 = U+2068
   U+2068 is FIRST STRONG ISOLATE
   That is not a letter. It is an invisible bidirectional formatting character,
   and it changes how everything after it is DISPLAYED.

   Worse, some destinations are not characters at all:
   chr(0xD800) is a str of length 1 ...
   ... and encoding it raises UnicodeEncodeError: U+D800 is a surrogate,
   permanently reserved, and no UTF-8 file may contain one.
   So a rotation over the whole table cannot be a sum. It needs a list of which
   code points it is allowed to produce -- which is the opposite of a one-line rule.
```
<!-- /output -->

Section 4 is the one to read slowly. Twenty-six lines, twenty-five of them wrong, and the right one is obvious at a glance without a dictionary or a program. Section 5 is the shelving question, settled by the standard library.

## In the terminal

<!-- output:rotation_is_not_encryption_sh -->
*Verified output of [`rotation_is_not_encryption_sh.sh`](examples/rotation_is_not_encryption_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ROT13 IS ONE tr. THE 'KEY' IS THE SECOND ARGUMENT, AND IT IS ON THE SCREEN.

$ echo 'Hello, World!' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
Uryyb, Jbeyq!

2. THE SAME COMMAND UNDOES IT -- 13 + 13 = 26

$ echo 'Hello, World!' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
Hello, World!

3. ROT47 IS ALSO ONE tr, OVER THE 94 PRINTABLE ASCII CHARACTERS

$ echo 'Hello, World!' | tr '!-~' 'P-~!-O'
w6==@[ (@C=5P

$ echo 'Hello, World!' | tr '!-~' 'P-~!-O' | tr '!-~' 'P-~!-O'
Hello, World!

4. NOTHING MOVED. SAME BYTE COUNT, SAME RANGE, ONE BYTE PER CHARACTER.

$ printf 'Hello' | wc -c | tr -d ' '
5

$ printf 'Hello' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | wc -c | tr -d ' '
5

$ printf 'Hello' | xxd
00000000: 4865 6c6c 6f                             Hello

$ printf 'Hello' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | xxd
00000000: 5572 7979 62                             Uryyb
   Every byte is still 0x21..0x7E. That is what makes it survive a mail gateway,
   and it is the same property that makes it useless as protection.

5. THE ROTATION CANNOT LEAVE THE RANGE IT WAS GIVEN

$ printf 'caf\xc3\xa9\n' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | xxd
00000000: 706e 73c3 a90a                           pns...
   The two bytes c3 a9 are outside A-Za-z, so tr passes them through untouched.
   In UTF-8 that is one character, e-acute -- and no shell rotation will ever touch it.
   To rotate THAT you need code points, not bytes. See the Python and Rust examples.
```
<!-- /output -->

`tr 'A-Za-z' 'N-ZA-Mn-za-m'` is the whole implementation, and the second argument *is* the substitution alphabet — written out, in the command, where anybody watching can read it. Section 5 is the shell's limit: `tr` works on bytes, so the two bytes of `é` are outside `A-Za-z` and pass through untouched. To rotate that character you have to be working in code points, which is what the other two examples do.

## In Rust

<!-- output:rotation_is_not_encryption_rs -->
*Verified output of [`rotation_is_not_encryption_rs.rs`](examples/rotation_is_not_encryption_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. WHILE THE TEXT IS ASCII, THE ROTATION IS ARITHMETIC ON u8
   b'h' = 104   b'h' + 13 = 117   as char = 'u'
   rot_ascii("Hello, World!", 13) = "Uryyb, Jbeyq!"
   Every byte stays inside 0x00..=0x7F, so the String is still valid UTF-8
   for free -- no check needed, because ASCII is a subset of UTF-8.

2. AND IT IS ITS OWN INVERSE
   "Uryyb, Jbeyq!" -> "Hello, World!"

3. WHAT A ROTATION COSTS IS A METHOD ON THE TYPE: char::len_utf8()
   U+0068  len_utf8 = 1  bytes = [68]
   U+0075  len_utf8 = 1  bytes = [75]
   U+2068  len_utf8 = 3  bytes = [e2, 81, a8]
   U+00E9  len_utf8 = 2  bytes = [c3, a9]
   U+1F600  len_utf8 = 4  bytes = [f0, 9f, 98, 80]
   'h' rotated by 13 is still one byte. 'h' rotated by 0x2000 is three.
   A ciphertext that is three times the size of the plaintext is not a
   rotation of the alphabet any more -- it is a re-encoding.

4. char::from_u32 RETURNS Option, SO THE TYPE REFUSES THE HOLES
   from_u32(0x0068) = Some(U+0068)  len_utf8 1
   from_u32(0x2068) = Some(U+2068)  len_utf8 3
   from_u32(0xD800) = None
   from_u32(0xDFFF) = None
   from_u32(0x10FFFF) = Some(U+10FFFF)  len_utf8 4
   from_u32(0x110000) = None
   Python's chr() hands back a lone surrogate and fails later, at encode time.
   Rust cannot build the value at all: there is no char for those numbers.

5. SO 'ROTATE THE WHOLE TABLE' CANNOT BE ONE SUM
   numbers in the code point range 0..0x110000 : 1114112
   of those, numbers that are a char           : 1112064
   numbers that are NOT                        : 2048
   The gap is U+D800..=U+DFFF, the surrogates, permanently reserved.
   Any rotation over Unicode has to carry a list of the code points it may
   produce and step over that hole -- and once you are carrying a table,
   the 'it is just a sum' selling point of ROT13 is gone.
```
<!-- /output -->

Rust splits the two halves of this page apart by type. While the text is ASCII the rotation is `u8` arithmetic and the result is valid UTF-8 for free. Once the destination is a code point, `char::from_u32` returns an `Option` — and `None` for all 2,048 surrogates — so the compiler makes you say what a rotation should do when it lands in the hole. Python lets `chr(0xD800)` succeed and fails later, at encode time, which is the same bug found one step further from its cause.

## If you are coming from Python or ABAP

**Python.** `codecs.encode(s, 'rot13')` is the built-in, and the surprise is where it lives: `encodings/rot_13.py`, registered under the name `rot-13`. It is reachable through `codecs.encode` and **not** through `str.encode`, which raises `LookupError` — the `encode` verb is reserved for codecs that produce `bytes`. If you want it as a pipeline stage, `codecs.encode` is the door; if you were reaching for it as protection, the standard library's own filing is telling you something.

**ABAP.** There is no ROT13, and the shell trick does not transfer either: `TRANSLATE … USING` takes character *pairs*, so a rotation is a 52-character literal you build once rather than a range expression. Write it as an offset over `sy-abcde` (`cl_abap_char_utilities` has no rotation helper) and remember that a `c` field is UTF-16 on any modern system, so "the byte after `A`" is not a meaningful step — you are moving over code units, not the ASCII table this page describes. For anything that actually needs to be unreadable, the platform answer is `cl_sec_sxml_writer` / SSF, never a substitution. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 02_Characters/rotation_is_not_encryption/examples
python3 rotation_is_not_encryption_py.py
bash rotation_is_not_encryption_sh.sh
rustc --edition 2024 rotation_is_not_encryption_rs.rs -o /tmp/rot && /tmp/rot
```

Without the machine: ROT13 applied twice returns the input — for which other shifts of a 26-letter alphabet is that true? Why does ROT47 use 47 and not 63? And if you rotated the printable ASCII range by 47 **twice** but changed the range to `0x20`–`0x7E` in between, what would come back?

## See also

- [A character is a number](../a_character_is_a_number/README.md) — the layout every number on this page comes from
- [Binary to text](../../03_Encodings/binary_to_text/README.md) — the same "this is not encryption" claim, about Base64
- [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md) — why `str.encode` refuses a `str` → `str` transform
- [Logical and visual order](../logical_and_visual_order/README.md) — what `U+2068` actually does
- [What you see is not what runs](../../12_Adversarial/trojan_source/README.md) — the same characters, chosen on purpose
- [Frequency analysis ↗](https://en.wikipedia.org/wiki/Frequency_analysis) — where the cryptography starts, and where this library stops
