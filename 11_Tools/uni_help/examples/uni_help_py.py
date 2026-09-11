#!/usr/bin/env python3
"""The columns on uni's help screen that need no table, recomputed from the number.

`uni -h` lists every column uni can print. Some of them are arithmetic on the
code point, so any program on any machine gets the same answer and this one
can record it. The rest are rows in a table that somebody publishes and
revises -- the Unicode Character Database, X11's keysymdef.h, RFC 1345, the
WHATWG list of named references -- and a program can only ask its own copy.

Section 1 fills in the arithmetic columns for the help's own example, U+2713,
and for the cast's character above U+FFFF, U+1F600. Sections 2 to 4 are the
three places where the help's wording and the arithmetic part company, and
section 5 asks Python's copy of the table for the columns it has.

Run:  python3 uni_help_py.py
"""

import html.entities
import json
import unicodedata

BAR = "-" * 72
BS = chr(92)  # one backslash, built rather than typed
CHECK, GRIN = 0x2713, 0x1F600


def head(n, title):
    print(("" if n == 1 else "\n") + f"{n}. {title}\n{BAR}")


def utf16(cp, order):
    return chr(cp).encode("utf-16-" + order).hex(" ")


def arithmetic(cp):
    """Every column a pencil can fill in, spelled the way uni spells it."""
    ch = chr(cp)
    return [
        ("%(cpoint)", f"U+{cp:04X}"),
        ("%(hex)", f"{cp:x}"),
        ("%(dec)", str(cp)),
        ("%(oct)", f"{cp:o}"),
        ("%(bin)", f"{cp:b}"),
        ("%(utf8)", ch.encode("utf-8").hex(" ")),
        ("%(utf16le)", utf16(cp, "le")),
        ("%(utf16be)", utf16(cp, "be")),
        ("%(xml)", f"&#x{cp:x};"),
        ("%(json)", json.dumps(ch)[1:-1]),
        ("plane number", str(cp >> 16)),
    ]


head(1, "THE COLUMNS A PENCIL CAN FILL IN")
print("   " + "placeholder".ljust(15) + "U+2713, the help's".ljust(22) + "U+1F600, above U+FFFF")
for (name, a), (_, b) in zip(arithmetic(CHECK), arithmetic(GRIN)):
    print("   " + name.ljust(15) + a.ljust(22) + b)
print()
print("   Nothing above came out of a table. Every value is the one number")
print("   rewritten -- in another base, as UTF-8 or UTF-16 bytes, or as an")
print("   escape -- so no Unicode version and no machine can change it. The")
print("   last row is the plane's number, cp >> 16; the plane's NAME, which is")
print("   what %(plane) prints, has to come from a list of names.")


def bits(bs):
    return " ".join(f"{b:08b}" for b in bs)


head(2, "%(bin) IS A NUMERAL, AND A NUMERAL HAS NO BYTE ORDER")
big, little = CHECK.to_bytes(2, "big"), CHECK.to_bytes(2, "little")
print("   " + "U+2713 in base 2".ljust(30) + f"{CHECK:b}")
print("   " + "as two bytes, big-endian".ljust(30) + bits(big) + "   " + big.hex(" "))
print("   " + "as two bytes, little-endian".ljust(30) + bits(little) + "   " + little.hex(" "))
print()
print("   The first row is the ordinary numeral, most significant digit")
print("   first. Set beside the other two it is the big-endian bytes with the")
print("   leading zeros dropped, and nothing like the little-endian ones.")
print("   Byte order describes how a number's BYTES are laid out in memory or")
print("   on a wire; a numeral written on a screen has no bytes to order.")

head(3, "ABOVE U+FFFF, JSON SPENDS TWO ESCAPES AND XML SPENDS ONE")
v = GRIN - 0x10000
high, low = 0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF)
steps = [
    ("0x1f600 - 0x10000", f"0x{v:x}"),
    (f"0xd800 + (0x{v:x} >> 10)", f"0x{high:x}"),
    (f"0xdc00 + (0x{v:x} & 0x3ff)", f"0x{low:x}"),
    ("json.dumps(chr(0x1f600))", json.dumps(chr(GRIN))),
    ("the XML reference", f"&#x{GRIN:x};"),
]
for left, right in steps:
    print("   " + left.ljust(30) + "= " + right)
print()
print("   The XML reference names the code point, however many digits that")
print("   takes. JSON's " + BS + "u escape names one UTF-16 code unit -- four hex")
print("   digits, no more -- so a character above U+FFFF is written as its")
print("   surrogate pair: two escapes, and still nothing but arithmetic.")

head(4, "A BARE NUMBER IS HEX TO uni AND DECIMAL TO PYTHON")
for typed, digits, base in (("20", "20", 16), ("0d20", "20", 10)):
    cp = int(digits, base)
    try:
        name = unicodedata.name(chr(cp))
    except ValueError as e:
        name = f"(no Name: name() raises {type(e).__name__})"
    print("   " + f"uni print {typed}".ljust(17) + f"int('{digits}', {base}) = {cp}".ljust(20)
          + f"U+{cp:04X}  {name}")
print()
print("   Python's int() reads decimal unless told otherwise; uni reads hex")
print("   unless told otherwise (0d decimal, 0o octal, 0b binary). U+0014 is")
print("   a control character, and controls have no Name -- DEVICE CONTROL")
print("   FOUR is one of its aliases, which lookup() accepts even though")
print("   name() never returns it:")
alias = "DEVICE CONTROL FOUR"
print(f"   unicodedata.lookup({alias!r}) -> U+{ord(unicodedata.lookup(alias)):04X}")

head(5, "THE COLUMNS THAT NEED A TABLE, AND WHICH ONES PYTHON HAS")
ch = chr(CHECK)
refs = [k for k, v in html.entities.html5.items() if v == ch]
have = [
    ("%(name)", "unicodedata.name()", unicodedata.name(ch)),
    ("%(cat)", "unicodedata.category()", unicodedata.category(ch)),
    ("%(width)", "unicodedata.east_asian_width()", unicodedata.east_asian_width(ch)),
    ("%(html)", "html.entities.html5", "  ".join("&" + r for r in refs)),
]
for col, where, value in have:
    print("   " + col.ljust(12) + where.ljust(33) + value)
for col, func in (("%(block)", "block"), ("%(script)", "script"), ("%(unicode)", "age")):
    print("   " + col.ljust(12) + f"unicodedata.{func}()".ljust(33) + f"exists: {hasattr(unicodedata, func)}")
print("   %(aliases), %(refs)  NamesList.txt, which Python does not ship")
print("   %(keysym)            X11's keysymdef.h: not a Unicode table at all")
print("   %(digraph)           RFC 1345's mnemonics: not a Unicode table at all")
print()
print("   EAST_ASIAN_WIDTH: THE TABLE'S LETTERS, AND WHAT EACH ONE MEANS")
MEANS = {
    "A": "Ambiguous",
    "F": "Fullwidth",
    "H": "Halfwidth",
    "N": "Neutral -- never in an East Asian legacy set",
    "Na": "Narrow -- an East Asian narrow form",
    "W": "Wide",
}
for cp in (0x0041, CHECK, 0x00E9, 0x65E5):
    w = unicodedata.east_asian_width(chr(cp))
    print(f"   U+{cp:04X}  {w:<3} {MEANS[w]:<46}{chr(cp)}")
print()
print("   A is Na and CHECK MARK is N. The letters are hard to confuse; the")
print("   words Narrow and Neutral are not, which is why it is worth reading")
print("   the letter whenever a tool prints only the word.")
