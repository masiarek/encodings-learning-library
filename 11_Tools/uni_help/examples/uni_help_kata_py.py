#!/usr/bin/env python3
"""Answer key: predict uni's row for the euro sign, then name the tables.

The row is arithmetic, so it is computed here. The second part is the
columns no arithmetic produces: Python has a copy of three of those tables
and they are asked; the other two are written in from the files they come
from. The last part is the one trap in how uni reads a number.

Run:  python3 uni_help_kata_py.py
"""

import html.entities
import unicodedata

EURO = 0x20AC
ch = chr(EURO)
utf8 = ch.encode("utf-8")
be = ch.encode("utf-16-be")

print("THE ROW, WITH A PENCIL")
print(f"   U+{EURO:04X} {EURO} {EURO:o} {EURO:b} {utf8.hex(' ')} {be.hex(' ')} &#x{EURO:x};")
print()
nibbles = [(EURO >> s) & 0xF for s in (12, 8, 4, 0)]
place = " + ".join(f"{d}*{16 ** p}" for d, p in zip(nibbles, (3, 2, 1, 0)))
groups = [f"{EURO >> 12:04b}", f"{(EURO >> 6) & 0x3F:06b}", f"{EURO & 0x3F:06b}"]
explain = [
    ("%(cpoint)", f"U+{EURO:04X}", "the number in hex, at least four digits"),
    ("%(dec)", str(EURO), place),
    ("%(oct)", f"{EURO:o}", "the same number in base 8"),
    ("%(bin)", f"{EURO:b}", " ".join(f"{d:04b}" for d in nibbles) + ", leading zeros dropped"),
    ("%(utf8)", utf8.hex(" "), f"1110 {groups[0]}  10 {groups[1]}  10 {groups[2]}"),
    ("%(utf16be)", be.hex(" "), "one 16-bit unit (it is below U+FFFF), high byte first"),
    ("%(xml)", f"&#x{EURO:x};", "the hex again, between &#x and ;"),
]
for col, value, why in explain:
    print("   " + col.ljust(12) + value.ljust(17) + why)

print()
print("THE COLUMNS NO PENCIL FILLS IN")
refs = [k for k, v in html.entities.html5.items() if v == ch]
tables = [
    ("%(name)", unicodedata.name(ch), "Unicode's Name property -- unicodedata.name()"),
    ("%(cat)", unicodedata.category(ch), "General_Category -- unicodedata.category()"),
    ("%(html)", "  ".join("&" + r for r in refs), "WHATWG's named references -- html.entities.html5"),
    # Not in Python. Copied from the files they come from: keysymdef.h has
    # XK_EuroSign 0x20ac, and =e is the digraph Vim and uni both add by hand,
    # because RFC 1345 has no euro sign.
    ("%(keysym)", "EuroSign", "X11's keysymdef.h"),
    ("%(digraph)", "=e", "RFC 1345 -- except that the RFC has no euro sign"),
]
for col, value, whose in tables:
    print("   " + col.ljust(12) + value.ljust(17) + whose)
print()
print("   Any two of these answer the question. Each is a row in somebody's")
print("   table, with an owner and an edition -- the first block has neither.")

print()
print("A BARE NUMBER IS HEX TO uni")
for typed, digits, base in (("100", "100", 16), ("0d100", "100", 10)):
    cp = int(digits, base)
    print("   " + f"uni print {typed}".ljust(18) + f"int('{digits}', {base}) = {cp}".ljust(22)
          + f"U+{cp:04X}  {chr(cp)}  {unicodedata.name(chr(cp))}")
print()
print("   The same three digits, two characters. The prefix is the only thing")
print("   that says which number you meant.")
