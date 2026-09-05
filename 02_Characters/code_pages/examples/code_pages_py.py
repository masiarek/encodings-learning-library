#!/usr/bin/env python3
"""Seven 256-entry tables, one shared bottom half, and 128 slots everyone claimed.

A code page is ASCII plus a second opinion. The first 128 entries are the 1963
agreement and every table below keeps them; the second 128 were unclaimed, and
everybody filled them differently. This program measures the disagreement
rather than describing it -- including the part that is usually left out, which
is how much the tables partly AGREE, because that is what lets a wrong table go
unnoticed until the third page of a report.

Run:  python3 code_pages_py.py
"""

import unicodedata

BAR = "-" * 72

# Seven tables a European or American file might plausibly be written in.
TABLES = ["latin_1", "cp1252", "iso8859_2", "cp1250", "cp437", "cp850", "koi8_r"]
SHORT = {"latin_1": "latin1", "cp1252": "1252", "iso8859_2": "8859-2",
         "cp1250": "1250", "cp437": "437", "cp850": "850", "koi8_r": "koi8"}
TOP = range(0x80, 0x100)


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def dec(b, table):
    """One byte under one table, or None where the table defines nothing."""
    try:
        return bytes([b]).decode(table)
    except UnicodeDecodeError:
        return None


def show(ch):
    if ch is None:
        return "<undefined>"
    return f"{ch!r} U+{ord(ch):04X} {unicodedata.name(ch, '?')}"


# ------------------------------------------------------------------ 1
head(1, "THE HALF EVERYBODY AGREES ON")
same = [b for b in range(0x20, 0x7F) if len({dec(b, t) for t in TABLES}) == 1]
print(f"   printable ASCII, 0x20-0x7E: {len(same)} of {0x7F - 0x20} bytes decode")
print(f"   identically under all {len(TABLES)} tables.")
print()
for b in (0x41, 0x37, 0x2C):
    print(f"     {b:#04x} -> {dec(b, 'latin_1')!r} under every one of them")
print()
print("   That is the entire reason these files were interchangeable at all.")
print("   Source code, CSV delimiters, HTTP headers and English prose live")
print("   down here, which is why the problem stayed invisible in the")
print("   English-speaking world for a decade.")

# ------------------------------------------------------------------ 2
head(2, "ONE BYTE, ABOVE THE LINE")
for b in (0xE9, 0xB9):
    meanings = {dec(b, t) for t in TABLES}
    print(f"   {b:#04x} -- {len(meanings)} different characters:")
    for t in TABLES:
        print(f"     {SHORT[t]:<8} {show(dec(b, t))}")
    print()
print("   Not one byte. Not a corrupted byte. The same byte, and the question")
print("   'what character is this?' has no answer until somebody names a table.")

# ------------------------------------------------------------------ 3
head(3, "HOW MUCH THE TABLES AGREE -- WHICH IS THE PART THAT HURTS")
print(f"   of the {len(TOP)} bytes 0x80-0xFF, how many decode to the SAME character:")
print()
print("            " + "".join(f"{SHORT[t]:>8}" for t in TABLES))
for a in TABLES:
    cells = "".join(
        f"{sum(1 for b in TOP if dec(b, a) is not None and dec(b, a) == dec(b, x)):>8}"
        for x in TABLES
    )
    print(f"   {SHORT[a]:<9}{cells}")
print()
print("   Read the off-diagonal numbers. Latin-1 and Latin-2 agree on 71 of")
print("   128 -- so a Polish file read as Latin-1 comes out mostly right, with")
print("   a handful of wrong letters, which reads as a typo rather than a bug.")
print("   The DOS and Cyrillic tables agree with the ISO family on ZERO, and")
print("   that is the easy case: it is obviously garbage and gets fixed.")

# ------------------------------------------------------------------ 4
head(4, "LATIN-1 IS THE ONE THAT IS AN IDENTITY")
identity = all(dec(b, "latin_1") == chr(b) for b in range(256))
print(f"   for every byte 0-255, latin_1 decodes it to code point b: {identity}")
print(f"     {0xE9:#04x} -> U+{ord(dec(0xE9, 'latin_1')):04X}")
print(f"     {0xFF:#04x} -> U+{ord(dec(0xFF, 'latin_1')):04X}")
print()
defined = {t: sum(1 for b in range(256) if dec(b, t) is not None) for t in TABLES}
for t in TABLES:
    print(f"     {SHORT[t]:<8} defines {defined[t]:>3} of 256 byte values")
print()
print("   Latin-1's first 256 code points ARE Unicode's first 256 -- not a")
print("   coincidence, it is where Unicode took them from. Two consequences:")
print("   decoding under Latin-1 can never fail, and Latin-1 is therefore the")
print("   only lossless way to carry unknown bytes through a text type.")

# ------------------------------------------------------------------ 5
head(5, "A POLISH FILE FROM 2005")
word = "Łódź"
for t in ("latin_1", "cp1250", "iso8859_2"):
    try:
        print(f"   {word!r}.encode({t:<10}) = {word.encode(t).hex(' ')}")
    except UnicodeEncodeError as e:
        print(f"   {word!r}.encode({t:<10}) raises: {e.object[e.start]!r} is not in this table")
print()
print("   Two tables can both write it, and they do not write it the same way.")
for written in ("cp1250", "iso8859_2"):
    data = word.encode(written)
    print(f"     written {written:<10} {data.hex(' ')}")
    for t in ("cp1250", "iso8859_2", "latin_1", "cp437"):
        mark = "   <- correct" if t == written else ""
        print(f"       read as {t:<10} {data.decode(t)!r}{mark}")
print()
print("   The two Central European readings are the cruel ones: three letters")
print("   right and the fourth quietly wrong -- Ľ for ź, or a control character")
print("   that prints as nothing at all. Nobody files a bug for that. They")
print("   retype the word and move on, and the file goes on being wrong.")
print("   The cp437 reading is the lucky one: it is obviously broken.")

# ------------------------------------------------------------------ 6
head(6, "WHAT NONE OF THEM COULD DO")
reachable = {c for t in TABLES for b in range(256) if (c := dec(b, t)) is not None}
print(f"   reachable by ONE 8-bit table         {'256':>10}  at the absolute most")
print(f"   reachable by all {len(TABLES)} of them together {len(reachable):>10}")
print(f"   code points Unicode has room for     {1114112:>10,}")
print()
print("   And you may only pick one table per file. That is not an argument")
print("   about tidiness -- a Kraków office and an Athens office could not put")
print("   both addresses in one file, because there was no byte to write.")
