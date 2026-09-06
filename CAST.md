# The cast

**Level:** reference · house convention

**One line:** Nine characters, seven invisibles and six strings — the whole demonstration vocabulary of this library. Each one earns its place by a property no other member has, and a page reaching outside the list should be able to say which property it needed.

## Why a fixed cast

Counting the library's own files, ignoring prose punctuation:

```text
110 files, 156 distinct non-ASCII characters
 90 of those 156 appear once or twice in the entire library
```

That tail is the problem this page exists to stop. A reader who meets a new alphabet on every page has to learn the example before they can read the lesson, and a page that reaches for a fresh CJK character teaches nothing the last one did not. A fixed cast compounds instead: the second time you meet `é` you already know it is `C3 A9`, one byte in Latin-1, and `Ã©` when those two are confused — so the page can spend its words on what it is actually about.

Same reasoning as the sibling Rust library's rule on [naming things in an example ↗](https://github.com/masiarek/rust-learning-library/blob/master/CONTRIBUTING.md): a name the reader has already met costs nothing, and one they have to learn first is charged against the lesson.

## The core eight, and one specialist

Eight cover the axis that matters most here — how many bytes, and which 8-bit tables can hold it. The ninth is on a different axis and is listed separately for that reason.

| char | code point | UTF-8 | 8859-1 | 1252 | why it is in the cast |
|---|---|---|---|---|---|
| `A` | `U+0041` | `41` | `41` | `41` | the ASCII baseline — the same byte in every encoding this library discusses |
| `~` | `U+007E` | `7E` | `7E` | `7E` | the top of printable ASCII, one below `DEL` |
| `é` | `U+00E9` | `C3 A9` | `E9` | `E9` | the canonical [mojibake](03_Encodings/mojibake/README.md) case, and the composed half of the normalization pair |
| `ż` | `U+017C` | `C5 BC` | — | — | Polish: a two-byte letter no Latin-1 table can hold, so it forces the [code-page](02_Characters/code_pages/README.md) question |
| `€` | `U+20AC` | `E2 82 AC` | — | `80` | in Windows-1252 at `0x80`, absent from ISO-8859-1 — the sharpest single case for [why those two are not the same table](07_Real_Data/windows_1252_vs_latin1/README.md) |
| `日` | `U+65E5` | `E6 97 A5` | — | — | CJK: three bytes, and two columns wide on a terminal |
| `ಠ` | `U+0CA0` | `E0 B2 A0` | — | — | a script nobody here has a keyboard for, so it can only be written as an escape |
| `😀` | `U+1F600` | `F0 9F 98 80` | — | — | above `U+FFFF`: four UTF-8 bytes, and a [surrogate **pair**](03_Encodings/utf16_and_surrogates/README.md) in UTF-16 |
| `ß` | `U+00DF` | `C3 9F` | `DF` | `DF` | **the specialist:** uppercases to *two* letters, so case mapping can change a string's length |

`ż` and `ß` look like near-duplicates and are not: `ż` is about what a table cannot *hold*, `ß` about what a *transformation* does to length. Neither substitutes for the other.

## The invisibles

Everything above you can see. These are the ones that bite precisely because you cannot.

| code point | UTF-8 | name | why it is in the cast |
|---|---|---|---|
| `U+0000` | `00` | NUL | ends a C string; the byte no text format may contain |
| `U+000D` | `0D` | CR | the half of [CRLF](07_Real_Data/crlf_vs_lf/README.md) that Unix does not write |
| `U+000A` | `0A` | LF | the other half |
| `U+0301` | `CC 81` | COMBINING ACUTE | put it after `e` and you have a second `é` that compares unequal to the first |
| `U+00A0` | `C2 A0` | NO-BREAK SPACE | whitespace to Unicode, not to ASCII — so two `trim`s disagree about it |
| `U+FEFF` | `EF BB BF` | BOM | a [byte-order mark](03_Encodings/byte_order_and_bom/README.md) that marks no byte order in UTF-8, and gets written anyway |
| `U+FFFD` | `EF BF BD` | REPLACEMENT | what a lossy decode leaves where the bytes failed |

Two more are named but never *used*, because they cannot be: `U+D800`, a lone surrogate no encoder will accept, and `U+FFFE`, a permanent noncharacter — which is exactly what makes it usable as proof about byte order.

## The strings

| chars | UTF-8 | UTF-16 | cols | text | what it is for |
|---|---|---|---|---|---|
| 13 | 13 | 13 | 13 | `Hello, World!` | the baseline: every ruler agrees |
| 4 | 5 | 4 | 4 | `café` | the house string — one accent, so bytes and characters part company |
| 5 | 6 | 5 | 4 | `café` | its decomposed twin: identical on screen, unequal in memory |
| 4 | 7 | 4 | 4 | `żółw` | Polish: three of four letters cost two bytes |
| 3 | 9 | 3 | 6 | `日本語` | three characters, nine bytes, six columns |
| 5 | 18 | 8 | 6 | `👨‍👩‍👧` | one family: three people, two joiners, one grapheme — and four different answers |

**chars** counts code points; **UTF-16** counts 16-bit units, which is what Java, JavaScript and ABAP call a character; **cols** is the width a terminal gives it. No two of the four are the same question, which is why the family emoji is on the list.

Longer Polish text, when a page needs a sentence rather than a word: **`zażółć gęślą jaźń`** — a pangram for the diacritics, and the string to reach for when demonstrating a code page that has to hold all nine of them.

## The pair of bytes worth memorising

```text
'é' in UTF-8    C3 A9   (2 bytes)
'é' in Latin-1  E9      (1 byte)

C3 A9 read as Latin-1  ->  'Ã©'
```

That is mojibake in three lines, and `Ã©` is the shape to recognise in the wild. Every mojibake demonstration in the library starts from this pair rather than inventing its own.

## Which one for which lesson

| if the page is about… | reach for |
|---|---|
| UTF-8 widths | `A`, `é`, `日`, `😀` — one, two, three, four bytes |
| code pages, and what a table cannot hold | `é` (in Latin-1), `ż` (not), `€` (1252 only) |
| Windows-1252 against ISO-8859-1 | `€` at `0x80` |
| mojibake | `é` — its UTF-8 bytes `C3 A9` read as Latin-1, which prints `Ã©` |
| UTF-16, surrogates, and the BMP | `😀` |
| normalization | `café` against `café` — composed `U+00E9` against `e` + `U+0301`, identical on screen |
| grapheme clusters | `👨‍👩‍👧` |
| case mapping | `ß` |
| C strings and the NUL boundary | `U+0000` |
| line endings | `CR`, `LF` |
| whitespace rules | `U+00A0` |
| file preambles | `U+FEFF` |
| decode failure | `U+FFFD` |
| escape syntax, and text you cannot type | `ಠ` |
| terminal width | `日本語` |
| Polish text and diacritics | `żółw`, `zażółć gęślą jaźń` |

## Rules

1. **Reach for a cast member first.** If none of them has the property your page needs, that is a real finding — say so in a line, use what you need, and add a row here if it will be wanted again.
2. **Do not mint a new alphabet for flavour.** A page that could use `日` and picks a different ideograph has spent the reader's attention on nothing.
3. **Keep the strings intact.** `café`, `żółw`, `日本語` are fixed. A new lesson gets a new *point*, not a new spelling of an old one.
4. **A character has to earn its row on a property, not on looking interesting.** `ಠ` is here because nobody can type it, not because it is a funny eye.
5. **Every number on this page comes from [the program below](#the-verified-output).** If you add a row, add it there too — the byte columns are output, not annotation.

## What is deliberately not in the cast

- **Right-to-left scripts.** Bidi is a real subject and this library does not teach it; a Hebrew or Arabic sample would raise a question no page here answers.
- **A second CJK language.** `日本語` covers three-byte, double-width, and the Shift-JIS contrast. Korean or Chinese samples would add rows and no properties.
- **Historic and astral scripts beyond `😀`.** One character above `U+FFFF` is enough to make every point about the BMP boundary.
- **Anything chosen for shock value.** Zalgo text, 200-character grapheme clusters and the rest are memorable and teach nothing that `👨‍👩‍👧` does not.

## The verified output

<!-- source:the_cast_py -->
*[`the_cast_py.py`](examples/the_cast_py.py) in full — pasted here by `tools/run_examples.py` from the file CI runs.*

```python
#!/usr/bin/env python3
"""The house cast: the characters and strings this library demonstrates with.

Every number on CAST.md comes from this program, so the cast cannot drift away
from what the characters actually do.

Run:  python3 the_cast_py.py
"""

import unicodedata

CORE = [
    ("A", "the ASCII baseline -- the same byte in every encoding here"),
    ("~", "the top of printable ASCII, one below DEL"),
    ("é", "the canonical mojibake case, and the composed half of the pair"),
    ("ż", "Polish: a 2-byte letter Latin-1 cannot hold at all"),
    ("€", "in Windows-1252 at 0x80, absent from ISO-8859-1"),
    ("日", "CJK: 3 bytes, and two columns wide on a terminal"),
    ("ಠ", "a script no keyboard here has -- forces escape syntax"),
    ("😀", "above U+FFFF: 4 bytes, and a surrogate PAIR in UTF-16"),
]

# One specialist, on a different axis: not width, but what case mapping does.
SPECIALIST = ("ß", "uppercases to TWO letters, so case can change a string's length")

INVISIBLE = [
    ("\x00", "NUL", "ends a C string; the byte no text format may contain"),
    ("\r", "CR", "the half of CRLF that Unix does not write"),
    ("\n", "LF", "the other half"),
    ("́", "COMBINING ACUTE", "put it after 'e' and you get a second 'é'"),
    (" ", "NO-BREAK SPACE", "whitespace to Unicode, not to ASCII"),
    ("﻿", "BOM", "a byte-order mark that marks no byte order in UTF-8"),
    ("�", "REPLACEMENT", "what a lossy decode leaves where bytes failed"),
]

STRINGS = [
    ("Hello, World!", "the baseline: every ruler agrees"),
    ("café", "the house string -- one accent, so bytes and chars part"),
    ("café", "its twin: identical on screen, unequal in memory"),
    ("żółw", "Polish: three of four letters cost two bytes"),
    ("日本語", "three chars, nine bytes, six columns"),
    ("👨‍👩‍👧", "one family: three people, two joiners, one grapheme"),
]


def columns(s: str) -> int:
    """A terminal's width for this text: 2 for East Asian wide, 0 for a mark."""
    total = 0
    for c in s:
        if unicodedata.combining(c) or c in "\u200d\ufeff":
            continue
        total += 2 if unicodedata.east_asian_width(c) in "WF" else 1
    return total


def in_table(ch: str, enc: str) -> str:
    """What this character is in an 8-bit table -- or why it is not there."""
    try:
        return ch.encode(enc).hex().upper()
    except UnicodeEncodeError:
        return "--"


def main() -> None:
    print("1. THE CORE EIGHT -- one per UTF-8 width, one per boundary -- and a specialist")
    print(f"   {'code pt':<9} {'UTF-8':<12} {'8859-1':<7} {'1252':<5} {'char':<5} why it is in the cast")
    for ch, why in CORE:
        utf8 = " ".join(f"{b:02X}" for b in ch.encode())
        print(f"   U+{ord(ch):<7X} {utf8:<12} {in_table(ch, 'iso-8859-1'):<7} "
              f"{in_table(ch, 'cp1252'):<5} {ch!r:<5} {why}")
    ch, why = SPECIALIST
    utf8 = " ".join(f"{b:02X}" for b in ch.encode())
    print(f"   U+{ord(ch):<7X} {utf8:<12} {in_table(ch, 'iso-8859-1'):<7} "
          f"{in_table(ch, 'cp1252'):<5} {ch!r:<5} {why}")
    print()

    print("2. THE INVISIBLES -- you cannot see them, and every one of them bites")
    print(f"   {'code pt':<9} {'UTF-8':<12} {'name':<16} why it is in the cast")
    for ch, name, why in INVISIBLE:
        utf8 = " ".join(f"{b:02X}" for b in ch.encode())
        print(f"   U+{ord(ch):<7X} {utf8:<12} {name:<16} {why}")
    print()

    print("3. THE STRINGS -- four rulers over the same text")
    print(f"   {'chars':>5} {'UTF-8':>6} {'UTF-16':>7} {'cols':>5}   text")
    for s, why in STRINGS:
        utf16_units = len(s.encode("utf-16-le")) // 2
        print(f"   {len(s):>5} {len(s.encode()):>6} {utf16_units:>7} {columns(s):>5}   {s!r}")
        print(f"   {'':>5} {'':>6} {'':>7} {'':>5}   {why}")
    print("   'chars' counts code points; 'UTF-16' counts 16-bit units, which is")
    print("   what Java, JavaScript and ABAP call a character; 'cols' is the width")
    print("   a terminal gives it. No two of the four are the same question, and")
    print("   the family emoji answers all four differently.")
    print()

    print("4. THE ONE PAIR OF BYTES WORTH MEMORISING")
    utf8 = "é".encode()
    latin1 = "é".encode("iso-8859-1")
    print(f"   'é' in UTF-8    {utf8.hex(' ').upper()}   ({len(utf8)} bytes)")
    print(f"   'é' in Latin-1  {latin1.hex(' ').upper()}      ({len(latin1)} byte)")
    print(f"   UTF-8 bytes read as Latin-1  -> {utf8.decode('iso-8859-1')!r}")
    print(f"   ...and read as Windows-1252  -> {utf8.decode('cp1252')!r}")
    print("   That is mojibake in one line, and 'Ã©' is the shape to recognise.")
    print()

    print("5. THREE THINGS THE CAST IS HERE TO PROVE")
    try:
        "\ud800".encode()
    except UnicodeEncodeError as e:
        print(f"   chr(0xD800).encode() -> UnicodeEncodeError: {e.reason}")
    print("   A lone surrogate is not a character, so no encoding will take it.")
    composed, decomposed = "café", "café"
    print(f"   {composed!r} == {decomposed!r} -> {composed == decomposed}")
    print("   They render identically. Comparing text means normalising first.")
    beta = SPECIALIST[0]
    print(f"   {beta!r}.upper() -> {beta.upper()!r}: {len(beta)} char in, {len(beta.upper())} out")
    print("   Case mapping is not one character in, one character out -- which is")
    print("   why a fixed-size buffer around .upper() is a bug waiting for German.")


if __name__ == "__main__":
    main()
```
<!-- /source -->

<!-- output:the_cast_py -->
*Verified output of [`the_cast_py.py`](examples/the_cast_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE CORE EIGHT -- one per UTF-8 width, one per boundary -- and a specialist
   code pt   UTF-8        8859-1  1252  char  why it is in the cast
   U+41      41           41      41    'A'   the ASCII baseline -- the same byte in every encoding here
   U+7E      7E           7E      7E    '~'   the top of printable ASCII, one below DEL
   U+E9      C3 A9        E9      E9    'é'   the canonical mojibake case, and the composed half of the pair
   U+17C     C5 BC        --      --    'ż'   Polish: a 2-byte letter Latin-1 cannot hold at all
   U+20AC    E2 82 AC     --      80    '€'   in Windows-1252 at 0x80, absent from ISO-8859-1
   U+65E5    E6 97 A5     --      --    '日'   CJK: 3 bytes, and two columns wide on a terminal
   U+CA0     E0 B2 A0     --      --    'ಠ'   a script no keyboard here has -- forces escape syntax
   U+1F600   F0 9F 98 80  --      --    '😀'   above U+FFFF: 4 bytes, and a surrogate PAIR in UTF-16
   U+DF      C3 9F        DF      DF    'ß'   uppercases to TWO letters, so case can change a string's length

2. THE INVISIBLES -- you cannot see them, and every one of them bites
   code pt   UTF-8        name             why it is in the cast
   U+0       00           NUL              ends a C string; the byte no text format may contain
   U+D       0D           CR               the half of CRLF that Unix does not write
   U+A       0A           LF               the other half
   U+301     CC 81        COMBINING ACUTE  put it after 'e' and you get a second 'é'
   U+A0      C2 A0        NO-BREAK SPACE   whitespace to Unicode, not to ASCII
   U+FEFF    EF BB BF     BOM              a byte-order mark that marks no byte order in UTF-8
   U+FFFD    EF BF BD     REPLACEMENT      what a lossy decode leaves where bytes failed

3. THE STRINGS -- four rulers over the same text
   chars  UTF-8  UTF-16  cols   text
      13     13      13    13   'Hello, World!'
                                the baseline: every ruler agrees
       4      5       4     4   'café'
                                the house string -- one accent, so bytes and chars part
       5      6       5     4   'café'
                                its twin: identical on screen, unequal in memory
       4      7       4     4   'żółw'
                                Polish: three of four letters cost two bytes
       3      9       3     6   '日本語'
                                three chars, nine bytes, six columns
       5     18       8     6   '👨\u200d👩\u200d👧'
                                one family: three people, two joiners, one grapheme
   'chars' counts code points; 'UTF-16' counts 16-bit units, which is
   what Java, JavaScript and ABAP call a character; 'cols' is the width
   a terminal gives it. No two of the four are the same question, and
   the family emoji answers all four differently.

4. THE ONE PAIR OF BYTES WORTH MEMORISING
   'é' in UTF-8    C3 A9   (2 bytes)
   'é' in Latin-1  E9      (1 byte)
   UTF-8 bytes read as Latin-1  -> 'Ã©'
   ...and read as Windows-1252  -> 'Ã©'
   That is mojibake in one line, and 'Ã©' is the shape to recognise.

5. THREE THINGS THE CAST IS HERE TO PROVE
   chr(0xD800).encode() -> UnicodeEncodeError: surrogates not allowed
   A lone surrogate is not a character, so no encoding will take it.
   'café' == 'café' -> False
   They render identically. Comparing text means normalising first.
   'ß'.upper() -> 'SS': 1 char in, 2 out
   Case mapping is not one character in, one character out -- which is
   why a fixed-size buffer around .upper() is a bug waiting for German.
```
<!-- /output -->

## See also

- [GLOSSARY.md](GLOSSARY.md) — the terms, where this page is the characters
- [CONTRIBUTING.md](CONTRIBUTING.md) — the rest of the house conventions
- [Unicode code points](02_Characters/unicode_code_points/README.md) — where `U+10FFFF` comes from
- [Why a `char` is 32 bits wide ↗](https://masiarek.github.io/rust-learning-library/14_Strings/why_char_is_32_bits/index.html) — the sibling Rust library on why one character is four bytes as a value and one to four inside a string
