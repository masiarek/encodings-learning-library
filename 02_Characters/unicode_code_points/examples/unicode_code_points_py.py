#!/usr/bin/env python3
"""A code point is a number, and U+XXXX is that number written in hex.

The useful skill is not memorising code points, it is reading one as an
ADDRESS: a block, then a house number inside it. Blocks start at round hex
numbers, so `U+20AC` reads as "currency block, house AC" rather than as
a number to store. This program walks the neighbourhoods a European
reader actually meets, and ends with the three pieces of arithmetic that
turn four more code points from things-to-memorise into things-to-derive.

Every character here has been named the same thing for decades, so nothing
below depends on which Unicode version your Python was built against.

Run:  python3 unicode_code_points_py.py
"""

import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def name(cp):
    return unicodedata.name(chr(cp), "<no name: a control>")


head(1, "U+00E9 IS A NUMBER, WRITTEN IN HEX")
cp = 0xE9
print(f"   U+{cp:04X}   decimal {cp}   binary {cp:08b}")
print(f"   chr({cp}) = {chr(cp)!r}   ord({chr(cp)!r}) = {ord(chr(cp))}")
print(f"   name: {name(cp)}")
print()
print("   U+00E9 and 0xE9 are the same NUMBER and different things:")
print("   one is a code point, the other is a byte under one table.")
print("   Which bytes carry U+00E9 is chapter 3's question, not this one.")

head(2, "READ IT AS AN ADDRESS: BLOCK, THEN HOUSE NUMBER")
print(f"   {'block':<10}{'what lives there':<28}example")
for start, what, sample, label in [
    (0x0000,  "ASCII",                   0x0041,  "A"),
    (0x0080,  "Latin-1's high half",     0x00A0,  "NBSP, invisible"),
    (0x0100,  "Latin Extended-A",        0x0104,  "\u0104"),
    (0x0370,  "Greek",                   0x03A9,  "\u03a9"),
    (0x0400,  "Cyrillic",                0x042F,  "\u042f"),
    (0x2000,  "General Punctuation",     0x2014,  "\u2014 em dash"),
    (0x20A0,  "Currency Symbols",        0x20AC,  "\u20ac"),
    (0x3000,  "CJK Symbols/Punctuation", 0x3000,  "ideographic space"),
    (0x4E00,  "CJK Ideographs",          0x4E00,  "\u4e00"),
    (0x1F300, "Emoji",                   0x1F600, "\U0001f600"),
]:
    block = f"U+{start:04X}"
    here = f"U+{sample:04X}"
    print(f"   {block:<10}{what:<28}{here:<9}{label}")
print()
print("   You do not memorise U+20AC. You memorise that currency starts")
print("   at U+20A0, and read the AC as a house number on that street.")

head(3, "THE FIRST 256 CODE POINTS *ARE* LATIN-1 -- WHICH IS THE TRAP")
ok = sum(1 for b in range(256) if bytes([b]).decode("latin_1"))
print(f"   bytes 0x00-0xFF decoded as latin-1: {ok} of 256 succeed")
print(f"   0xE9 -> {bytes([0xE9]).decode('latin_1')!r}, and ord() of it is {0xE9}")
print()
print("   Latin-1 is the identity table: byte N is code point N. So it can")
print("   never raise on decode -- and a mis-tagged file therefore does not")
print("   fail, it just quietly reads as the wrong letters.")

head(4, "WHERE POLISH LIVES")
for ch in "ĄĆĘŁŃÓŚŹŻ":
    print(f"   {ch}  U+{ord(ch):04X}  {unicodedata.name(ch)}")
print()
print("   All but Ó are in Latin Extended-A (U+0100-U+017F), because the")
print("   Latin-1 block had no room left. Ó is at U+00D3, inside Latin-1,")
print("   which is why it alone survives a wrong-table read intact.")

head(5, "THREE PIECES OF ARITHMETIC, AND FOUR FEWER THINGS TO MEMORISE")
print("   (a) the whitespace run 9-A-B-C-D, in cursor-travel order")
for cp, what in [(0x09, "TAB  right a little"), (0x0A, "LF   down one line"),
                 (0x0B, "VT   down a block"),   (0x0C, "FF   down a page"),
                 (0x0D, "CR   back to column 0")]:
    print(f"       U+{cp:04X}  {what}")
print("       ...and ASCII whitespace is that run MINUS B, PLUS 0x20.")
print()
print("   (b) NBSP is SPACE with the top bit set")
print(f"       0x20 | 0x80 = 0x{0x20 | 0x80:02X}  -> {name(0x20 | 0x80)}")
print()
print("   (c) the same 0x20 is the case bit you already use")
print(f"       'A' is 0x{ord('A'):02X}, and 0x{ord('A'):02X} ^ 0x20 = "
      f"0x{ord('A') ^ 0x20:02X} = {chr(ord('A') ^ 0x20)!r}")

head(6, "SEVENTEEN PLANES, AND THE 2,048 SLOTS THAT ARE NOT CHARACTERS")
planes, per_plane = 17, 0x10000
surrogates = 0xDFFF - 0xD800 + 1
print(f"   {planes} planes x {per_plane:,} = {planes * per_plane:,} slots")
print(f"   minus {surrogates:,} surrogates (U+D800-U+DFFF) reserved for UTF-16")
print(f"   = {planes * per_plane - surrogates:,} usable scalar values")
print()
print("   Python will build a str from a surrogate; Rust's char will not.")
print(f"   chr(0xD800) is fine here: {chr(0xD800)!r}")
try:
    chr(0xD800).encode("utf-8")
except UnicodeEncodeError as e:
    print(f"   ...until you ask for its bytes: {type(e).__name__}")
