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
