# An encoding is four layers

**Level:** 201 · for anyone who has met a BOM

**One line:** The Unicode standard splits "an encoding" into four mappings stacked on each other, and the reason to care is that `UTF-16` names two of those layers while `UTF-16LE` names only the bottom one — which is why the first writes two bytes you did not ask for and the second cannot.

## The word "encoding" is doing four jobs

Everywhere else in this chapter, *encoding* has meant one thing: the rule that turns a character into bytes. That is enough to fix mojibake and enough to read a hex dump, and it is the reason [encode and decode are verbs](../encode_and_decode_are_verbs/README.md) is the page that carries most of the weight.

It stops being enough at exactly one place — the moment somebody writes `UTF-16` and you have to know whether they mean the thing Java counts or the thing in the file. Those are two different layers, they have the same name, and no amount of care about verbs and tables will separate them.

[Unicode Technical Report #17 ↗](https://www.unicode.org/reports/tr17/) is the document that separates them. It defines **four levels**:

| # | Level | Maps | The question it answers |
|---|---|---|---|
| 1 | **ACR** — abstract character repertoire | — | Which characters exist at all, and what counts as *one* of them? |
| 2 | **CCS** — coded character set | characters → numbers | What number is this character? |
| 3 | **CEF** — character encoding form | numbers → **code units** | How many fixed-width pieces, and how wide? |
| 4 | **CES** — character encoding scheme | code units → **bytes** | Which byte of a multi-byte unit goes first? |

Read down that table and each row answers a question the row above it left open. Level 1 decides that `é` is a character — and *also* that a combining acute is a character, which is why one word has two spellings and why [normalization](../../04_Python/normalization/README.md) exists as a separate subject. Level 2 says `é` is `U+00E9`, a number with no width. Level 3 says UTF-16 writes that number as one 16-bit unit and UTF-8 as two 8-bit ones. Only level 4 asks which end of the 16-bit unit comes first.

**The layers are what let you say where a bug is.** Mojibake is a level-4 disagreement — the bytes were right and the table was wrong. A surrogate pair is a level-3 fact, so `"😀".length === 2` in JavaScript is not a bug in any file. `café` sorting apart from `café` is level 1, and no encoding setting will touch it.

## Three names live on two levels, and the standard says so

Here is the part that costs people days, stated by UTR #17 itself: used without qualification, `UTF-8`, `UTF-16` and `UTF-32` are ambiguous — each names an encoding *form* **and** an encoding *scheme*.

As **forms** they are code units in memory, and UTR #17 is explicit that at that level there is no byte orientation and a BOM is never used. As **schemes** they are bytes in a file, and there the byte order has to be decided. The `BE` and `LE` spellings exist only at level 4; there is no such thing as UTF-16LE code units.

The standard defines seven schemes, and sorts them into two kinds:

| Scheme | Serialises the form | Kind |
|---|---|---|
| `UTF-8` | UTF-8 | simple |
| `UTF-16` | UTF-16 | **compound** |
| `UTF-16BE` · `UTF-16LE` | UTF-16 | simple |
| `UTF-32` | UTF-32 | **compound** |
| `UTF-32BE` · `UTF-32LE` | UTF-32 | simple |

A **compound** scheme is an optional byte order mark followed by a simple one. That single word settles the question the [BOM page](../byte_order_and_bom/README.md) approaches from the other side: `utf-16` is not `utf-16le` with a default, it is a *different scheme* whose first act is to write down which of the other two it is about to be. The Python run below encodes `A` under all seven, and the two rows that come out longer are exactly the two the standard calls compound.

**UTF-8 is the reason nobody had to learn this.** Its code unit is one byte, so levels 3 and 4 collapse into each other and the form/scheme distinction has nothing to bite on. Every reader who met UTF-8 first — which is every reader — arrived at UTF-16 with a vocabulary that had never needed the difference.

## The one place the ambiguity is not harmless

Two bytes, `41 00`, with nothing in front of them, arriving under the plain tag `UTF-16`. They are well formed read either way: little-endian gives `A`, big-endian gives `䄀` (`U+4100`). Nothing errors, and no examination of the bytes can decide it.

The two authorities give different answers:

- The [Unicode FAQ ↗](https://www.unicode.org/faq/utf_bom.html) is one line — where a stream is known to be Unicode but not which endian, and there is no BOM, *"the text should be interpreted as big-endian"*.
- **CPython resolves an unmarked stream to the machine's own byte order.** In [`Objects/unicodeobject.c` ↗](https://github.com/python/cpython/blob/main/Objects/unicodeobject.c), when no BOM was found the decoder falls through to a `#if PY_LITTLE_ENDIAN` block that picks `utf-16-le` on a little-endian build and `utf-16-be` on a big-endian one.

So `b"\x41\x00".decode("utf-16")` is `'A'` on every machine you own and `'䄀'` on a big-endian build, and the standard's rule says the second is the right answer. Section 5 of the run below prints all three readings side by side.

**This is not a bug to file, and it is worth saying why.** Practically all unmarked UTF-16 in the wild came off a little-endian Windows box, so the native guess is right far more often than the standard's rule would be. Python is optimising for the data that exists. The reason to know it anyway is that it is invisible: there is no warning, no error, and on your machine no wrong answer — the divergence only shows up on hardware you will never test on, or on a file that came from it.

The practical rule is the one the FAQ gives in the same breath, and it is a rule about *layers*: if you have no BOM, do not tag the data `UTF-16`. Tag it `UTF-16BE` or `UTF-16LE` — name the scheme, not the form.

## The fifth thing, which is deliberately not a level

Base64, quoted-printable, uuencode: UTR #17 calls these a **transfer encoding syntax**, and gives the TES *"a separate status outside the character encoding model proper"*. It is a transform of the bytes level 4 produced, and it neither knows nor cares that they were text — which is exactly why the same machinery carries a PNG.

That is the answer to "is Base64 an encoding?" It is, but not of characters, and it sits on top of a stack that must already be complete. `base64(text)` is not a defined operation until the scheme is named: the shell run below base64s one `é` four times and gets four different strings.

**And one transform runs the other way.** JSON's `\uXXXX` escape names neither a byte nor a code point — it names a **UTF-16 code unit**, which is level 3. So `json.dumps("😀")` is `"😀"`: a surrogate pair, in a format whose bytes are UTF-8 by [RFC 8259 ↗](https://www.rfc-editor.org/rfc/rfc8259), borrowed from a form the file does not use. [Escaping into ASCII](../escaping_into_ascii/README.md) is the page about the family; this is what layer each member reaches for.

## The sixth concept: what a "charset" really is

There is one more thing in the model, and it is the one you actually type. A **character map (CM)** is a mapping straight from characters to bytes, bridging all four levels in one operation — and UTR #17 says character maps are what get [IANA charset ↗](https://www.iana.org/assignments/character-sets/character-sets.xhtml) identifiers. So the `charset=utf-8` in an HTTP header, the `encoding=` in an XML declaration and the `-f`/`-t` of `iconv` name character maps, not schemes.

Most of the time the two have the same name, which is why nothing goes wrong. It matters for the compound cases: `charset=UTF-16` is a complete instruction (read the mark, then the bytes) in a way that "the form UTF-16" never is.

## Where this comes from, and one word not to copy

The clearest prose version of the model outside the standard is Richard Gillam's *Unicode Demystified* (Addison-Wesley, 2002), chapter 2, in a section called *Character encoding terminology* — pages 30–31. It is worth reading: it walks the same stack, and it is better than UTR #17 at saying *why* each level had to be split out, with ISO 2022 and the East Asian encodings as the worked cases.

Three things to correct as you read it, all of them consequences of its age:

1. **It counts five levels, with the transfer encoding syntax as the fifth.** Current UTR #17 counts four and puts the TES outside them, for the reason Gillam's own text gives — he describes it as orthogonal to the other four in the sentence that introduces it, and then numbers it anyway.
2. **It says "encoding space" where the standard says "codespace".** The current report uses *codespace* throughout and never *encoding space*; take the standard's word, or a reader searching for it will find nothing.
3. **It lists compression — LZW, run-length encoding — as a kind of transfer encoding syntax.** UTR #17 says compression is usually handled *outside* the TES, by protocols such as gzip. That one is a real disagreement rather than a rewording.

There is also a small arithmetic slip worth noticing rather than sneering at: the book says a standard usually defines a stack of *all four of these transformations* and then names three — characters to code points, code points to code units, code units to bytes. Three is right. **Four levels have three gaps between them,** and a careful author writing a whole book on the subject still put the wrong number in the sentence — which is a fair measure of how easy this is to lose track of, and a good argument for the table at the top of this page.

## What this page does not cover

The mechanism of the byte order mark — why `U+FEFF`, why `U+FFFE` is a permanent noncharacter, and what `EF BB BF` is doing at the top of a CSV — is [Byte order and the BOM](../byte_order_and_bom/README.md). The surrogate arithmetic behind `D83D DE00` is [UTF-16 and surrogates](../utf16_and_surrogates/README.md). This page is only the vocabulary and the layer boundaries; both of those are what the boundaries are *for*.

## In Python

<!-- output:the_encoding_model_py -->
*Verified output of [`the_encoding_model_py.py`](examples/the_encoding_model_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
Layer by layer, on one character and one word.
Section 5 depends on the machine: this one is little-endian.

1. ABSTRACT CHARACTER REPERTOIRE -- what counts as one character
------------------------------------------------------------------------

   The first decision is not a number. It is whether an accented letter
   is a character in its own right, or a letter plus a mark that is also
   a character. Unicode answered BOTH, which is why one word has two
   spellings that no screen can tell apart:

   NFC  4 code points   U+0063 U+0061 U+0066 U+00E9
   NFD  5 code points   U+0063 U+0061 U+0066 U+0065 U+0301

   Same word, same repertoire, two sequences. Everything below this line
   is downstream of that choice: a layer cannot fix an ambiguity the
   layer above it introduced, which is why normalization is its own
   subject and not an encoding setting.


2. CODED CHARACTER SET -- characters to numbers
------------------------------------------------------------------------

   U+0041   LATIN CAPITAL LETTER A              A
   U+00E9   LATIN SMALL LETTER E WITH ACUTE     é
   U+017C   LATIN SMALL LETTER Z WITH DOT ABOVE ż
   U+1F600  GRINNING FACE                       😀

   The numbers live in a codespace, and Unicode's is fixed forever at
   U+0000..U+10FFFF -- 1,114,112 positions. 2,048 of them are surrogates,
   which are code points that are permanently not characters, so the
   set a character can be assigned to is 1,112,064 values wide.

   Note what has NOT been decided yet: nothing here says how many bits
   U+1F600 takes. It is a number. Numbers do not have widths.


3. CHARACTER ENCODING FORM -- numbers to code units
------------------------------------------------------------------------

   One code point, three forms, three unit counts:

   UTF-8   4 units of  8 bits   F0 9F 98 80
   UTF-16  2 units of 16 bits   D83D DE00
   UTF-32  1 unit  of 32 bits   0001F600

   D83D DE00 is the surrogate PAIR, and it is a fact about the form,
   not about any file: those are two 16-bit numbers, and a number has
   no first byte. This is the layer Java's `char`, JavaScript's
   `.length` and ABAP's string length all count.


4. CHARACTER ENCODING SCHEME -- code units to bytes
------------------------------------------------------------------------

   The Unicode Standard has exactly seven. Here is 'A' under each:

   scheme     form    kind      bytes                    n
   utf-8      UTF-8   simple    41                       1
   utf-16     UTF-16  compound  ff fe 41 00              4
   utf-16be   UTF-16  simple    00 41                    2
   utf-16le   UTF-16  simple    41 00                    2
   utf-32     UTF-32  compound  ff fe 00 00 41 00 00 00  8
   utf-32be   UTF-32  simple    00 00 00 41              4
   utf-32le   UTF-32  simple    41 00 00 00              4

   Sort that by the last column and the model falls out of it. The two
   longer rows are exactly the two the standard calls COMPOUND, and the
   extra bytes are the byte order mark -- so `utf-16` is not `utf-16le`
   with a default, it is a different scheme that begins by writing down
   which of the other two it is about to be.

   Three names appear in both of the first two columns. UTR #17 says so
   in as many words: used without qualification, UTF-8, UTF-16 and
   UTF-32 are ambiguous between the form and the scheme.


5. THE ONE PLACE THE AMBIGUITY IS NOT HARMLESS
------------------------------------------------------------------------

   Two bytes, 41 00, with no mark in front of them. They are
   well formed under both orders, so nothing here is an error:

   .decode('utf-16'  ) -> 'A'      U+0041   LATIN CAPITAL LETTER A
   .decode('utf-16le') -> 'A'      U+0041   LATIN CAPITAL LETTER A
   .decode('utf-16be') -> '䄀'      U+4100   CJK UNIFIED IDEOGRAPH-4100

   The Unicode FAQ's rule for text tagged UTF-16 with no BOM is one
   line: it should be interpreted as big-endian. Python's answer above
   is the little-endian one, because CPython resolves an unmarked
   stream to the machine's own order -- so this same program prints a
   different character on a big-endian build, and neither reading is
   detectable from the bytes.

   That is not a bug to file. Practically all unmarked UTF-16 in the
   wild came off a little-endian Windows box, so the native guess is
   right more often than the standard's rule. It is worth knowing only
   because you cannot see it happen.


6. TRANSFER ENCODING SYNTAX -- and why it is outside the model
------------------------------------------------------------------------

   base64 of 'Hi', once per scheme:

   utf-8     48 69          -> SGk=
   utf-16le  48 00 69 00    -> SABpAA==
   utf-16be  00 48 00 69    -> AEgAaQ==

   One text, three payloads, three base64 strings. base64 never saw a
   character; it transformed the bytes layer 4 handed it. That is why
   UTR #17 keeps it OUTSIDE the four levels -- it works the same on a
   PNG -- and why "we base64 the field" is not a complete statement
   until the scheme is named.

   And one that reaches back up the stack instead:

   json.dumps('Hi')          ->  "Hi"
   json.dumps('\U0001F600')  ->  "\ud83d\ude00"

   Those escapes are not bytes and not code points: \ud83d\ude00
   is the surrogate pair from section 3. JSON's escape syntax names
   UTF-16 CODE UNITS, so a format whose bytes are UTF-8 spells one
   character with two escapes borrowed from a form it does not use.
```
<!-- /output -->

## In the terminal

<!-- output:the_encoding_model_sh -->
*Verified output of [`the_encoding_model_sh.sh`](examples/the_encoding_model_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE CHARACTER, FOUR SCHEMES
------------------------------------------------------------------------

   UTF-8      2 bytes   c3a9
   UTF-16BE   2 bytes   00e9
   UTF-16LE   2 bytes   e900
   UTF-32BE   4 bytes   000000e9

   The UTF-16 pair is the same 16-bit number, 00E9, written down twice
   in opposite orders. Nothing about the character changed between
   those two rows -- only the serialisation did, which is what makes
   them two schemes of one encoding form.

2. THE SAME BYTES, HANDED TO A TRANSFER ENCODING
------------------------------------------------------------------------

   UTF-8     w6k=
   UTF-16BE  AOk=
   UTF-16LE  6QA=
   UTF-32BE  AAAA6Q==

   One character, four base64 strings. base64 is a transform of the
   bytes, so it inherits whatever the scheme decided and can say
   nothing about it: "the field is base64" names the wrapper and
   leaves the encoding unstated.

3. THE SPELLING THIS SCRIPT WILL NOT RUN
------------------------------------------------------------------------

   `iconv -t UTF-16`, with no BE or LE, is the compound scheme: it
   writes a byte order mark and then picks an order -- big-endian on
   macOS, little-endian on GNU. The same command therefore writes two
   different files on two machines, which is why every target above
   names its order. Same fact as the Python file's section 4, one
   tool along.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python hides level 3, and that is why the model reads as pedantry until you leave it.** A `str` is code points and a `bytes` is bytes; there is no object in between, and no codec can give you one — a codec ends at bytes by definition, so `'😀'.encode('utf-16le')` is the closest you can get and you have to divide by two yourself to recover the units. That is why `len('😀')` is `1` in Python and `2` in Java, JavaScript, C# and SAP: those four expose the UTF-16 *form* as their string type, and Python does not expose a form at all. Nothing is wrong in either language; they are reporting counts from different levels.

Python's codec table is level 4 throughout. It carries all seven of the standard's schemes and one extra, `utf-8-sig` — which is the UTF-8 scheme with a signature the standard treats as an optional mark rather than a scheme of its own.

**In ABAP the split is in the type system, and it is the sharpest version of it anywhere in this library.** A `string` holds characters and an `xstring` holds bytes; nothing implicit converts between them, and the conversion object is `cl_abap_conv` — so levels 1–3 live on one side of `cl_abap_conv` and level 4 on the other, enforced by the compiler. The internal form is UTF-16 on a Unicode system, which is the same reason a length in ABAP counts what Java counts. And the code page you name when you create the converter is a **character map** in UTR #17's sense, not a scheme — which is why a code-page number is enough to write a file and a form name never would be. *(Not machine-checked — CI cannot run ABAP; and verify any code-page number against the system rather than against a page.)*

## Try it

1. Take a UTF-16 file you have actually received — a SAP download, a Windows export, an old `.reg` — and run `head -c 2 file | xxd`. If it is `ff fe` or `fe ff`, the sender used the compound scheme; if it is anything else, they used a simple one and did not tell you which, and you are relying on a guess.
2. Ask whatever produced that file which of the seven schemes it wrote. Most tools will answer "UTF-16", which is the ambiguity in this page, live.
3. In your own codebase, `grep -rn "utf-16\|utf_16\|UTF-16"` and sort the hits into the ones that named a byte order and the ones that did not. Each of the second kind is a place relying on a default that two authorities disagree about.
4. Take the largest string in a language that counts UTF-16 units — a JavaScript `.length`, an ABAP `strlen` — and compare it against Python's `len()` on the same text. Every character above `U+FFFF` accounts for exactly one of the difference.

## Practice

**Seven numbers for one two-character string.**

The string is `ż😀` — `U+017C` and `U+1F600`. Write down all seven numbers before you run anything:

1. how many **code points**
2. how many **UTF-8 code units**
3. how many **UTF-16 code units**
4. how many **UTF-32 code units**
5. how many **bytes** under `utf-16le`
6. how many **bytes** under `utf-16`
7. how many **bytes** under `utf-8-sig`

Then the question the list is really asking: **which of those seven numbers changes on a big-endian machine?**

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:the_encoding_model_kata_py -->
*Verified output of [`the_encoding_model_kata_py.py`](examples/the_encoding_model_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
TEXT = 'ż😀'   (U+017C, U+1F600)

   code points           2   the CCS layer -- what Python's len() counts
   UTF-8 code units      6   2 for ż, 4 for the emoji
   UTF-16 code units     3   1 for ż, a surrogate PAIR for the emoji
   UTF-32 code units     2   one unit per code point, always
   bytes, utf-16le       6   3 units x 2 bytes, no mark
   bytes, utf-16         8   the compound scheme: the same 6, after a 2-byte mark
   bytes, utf-8-sig      9   6 + a 3-byte signature that marks nothing

   Row 5 against row 6 is the form/scheme boundary in two numbers, and
   rows 2, 3 and 4 are one code point counted three ways.

   The last question has no row because the answer is that nothing
   moves: on a big-endian machine every count above is unchanged. Byte
   ORDER is a property of the scheme, and a count is not an order --
   which is why utf-16be and utf-16le never differ in length.
```
<!-- /output -->

The trap is rows 5 and 6. They are the same three code units, serialised by two schemes of the same form, and the difference between them is the entire subject of this page.

</details>

## See also

- [Byte order and the BOM](../byte_order_and_bom/README.md) — the mark itself: why `U+FEFF`, why its mirror image is reserved, and what it does at the top of a CSV.
- [UTF-16 and surrogates](../utf16_and_surrogates/README.md) — where `D83D DE00` comes from, and the arithmetic that makes `U+10FFFF` the ceiling.
- [Encode and decode are verbs](../encode_and_decode_are_verbs/README.md) — the two operations these four levels are stacked between.
- [Binary to text](../binary_to_text/README.md) and [Escaping into ASCII](../escaping_into_ascii/README.md) — the transfer encodings, from the other end.
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) — level 1, and the five different lengths one string has.
- [Unicode Technical Report #17 ↗](https://www.unicode.org/reports/tr17/) — the model itself. Short, and the only normative source for any of this.
