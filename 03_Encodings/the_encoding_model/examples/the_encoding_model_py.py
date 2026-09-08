#!/usr/bin/env python3
"""Four layers between a character and a byte, and where each one is visible.

UTR #17 splits "an encoding" into four mappings stacked on each other -- a
repertoire, a set of numbers, a set of code units, a run of bytes -- plus two
concepts beside the stack. Every layer is observable from Python, and the two
that share a name are the two that cost people days.

Nothing here is random and nothing is read out of a Unicode table except the
normalization in section 1, which is what that section is about.

Run:  python3 the_encoding_model_py.py
"""

import base64
import json
import sys
import unicodedata

RULE = "-" * 72

# The Unicode Standard's seven character encoding schemes (UTR #17, section 6),
# each with the encoding FORM it serialises and whether the standard calls the
# scheme simple or compound. A compound scheme is an optional BOM followed by a
# simple one -- which is the whole of the difference this file is about.
SCHEMES = [
    ("utf-8", "UTF-8", "simple"),
    ("utf-16", "UTF-16", "compound"),
    ("utf-16be", "UTF-16", "simple"),
    ("utf-16le", "UTF-16", "simple"),
    ("utf-32", "UTF-32", "compound"),
    ("utf-32be", "UTF-32", "simple"),
    ("utf-32le", "UTF-32", "simple"),
]

UNIT_WIDTH = {"UTF-8": 1, "UTF-16": 2, "UTF-32": 4}


def say(title):
    print(f"\n{title}\n{RULE}")


def hexs(raw):
    return " ".join(f"{b:02x}" for b in raw)


def units(text, form):
    """The code units of `text` in `form`, as numbers -- no byte order."""
    width = UNIT_WIDTH[form]
    raw = text.encode({"UTF-8": "utf-8", "UTF-16": "utf-16be", "UTF-32": "utf-32be"}[form])
    return [int.from_bytes(raw[i:i + width], "big") for i in range(0, len(raw), width)]


print("Layer by layer, on one character and one word.")
print(f"Section 5 depends on the machine: this one is {sys.byteorder}-endian.")

# ---------------------------------------------------------------- 1. ACR
say("1. ABSTRACT CHARACTER REPERTOIRE -- what counts as one character")
print("""
   The first decision is not a number. It is whether an accented letter
   is a character in its own right, or a letter plus a mark that is also
   a character. Unicode answered BOTH, which is why one word has two
   spellings that no screen can tell apart:
""")
for name in ("NFC", "NFD"):
    word = unicodedata.normalize(name, "café")
    points = " ".join(f"U+{ord(c):04X}" for c in word)
    print(f"   {name}  {len(word)} code points   {points}")
print("""
   Same word, same repertoire, two sequences. Everything below this line
   is downstream of that choice: a layer cannot fix an ambiguity the
   layer above it introduced, which is why normalization is its own
   subject and not an encoding setting.
""")

# ---------------------------------------------------------------- 2. CCS
say("2. CODED CHARACTER SET -- characters to numbers")
print()
for ch in ("A", "é", "ż", "\U0001F600"):
    label = f"U+{ord(ch):04X}"
    print(f"   {label:9}{unicodedata.name(ch):36}{ch}")
total = 0x110000
surrogates = 0xE000 - 0xD800
print(f"""
   The numbers live in a codespace, and Unicode's is fixed forever at
   U+0000..U+10FFFF -- {total:,} positions. {surrogates:,} of them are surrogates,
   which are code points that are permanently not characters, so the
   set a character can be assigned to is {total - surrogates:,} values wide.

   Note what has NOT been decided yet: nothing here says how many bits
   U+1F600 takes. It is a number. Numbers do not have widths.
""")

# ---------------------------------------------------------------- 3. CEF
say("3. CHARACTER ENCODING FORM -- numbers to code units")
print("\n   One code point, three forms, three unit counts:\n")
emoji = "\U0001F600"
for form in ("UTF-8", "UTF-16", "UTF-32"):
    got = units(emoji, form)
    width = UNIT_WIDTH[form] * 2
    shown = " ".join(f"{u:0{width}X}" for u in got)
    plural = "unit " if len(got) == 1 else "units"
    print(f"   {form:7} {len(got)} {plural} of {UNIT_WIDTH[form] * 8:2} bits   {shown}")
print("""
   D83D DE00 is the surrogate PAIR, and it is a fact about the form,
   not about any file: those are two 16-bit numbers, and a number has
   no first byte. This is the layer Java's `char`, JavaScript's
   `.length` and ABAP's string length all count.
""")

# ---------------------------------------------------------------- 4. CES
say("4. CHARACTER ENCODING SCHEME -- code units to bytes")
print("\n   The Unicode Standard has exactly seven. Here is 'A' under each:\n")
print(f"   {'scheme':10} {'form':7} {'kind':9} {'bytes':24} n")
for codec, form, kind in SCHEMES:
    raw = "A".encode(codec)
    print(f"   {codec:10} {form:7} {kind:9} {hexs(raw):24} {len(raw)}")
print("""
   Sort that by the last column and the model falls out of it. The two
   longer rows are exactly the two the standard calls COMPOUND, and the
   extra bytes are the byte order mark -- so `utf-16` is not `utf-16le`
   with a default, it is a different scheme that begins by writing down
   which of the other two it is about to be.

   Three names appear in both of the first two columns. UTR #17 says so
   in as many words: used without qualification, UTF-8, UTF-16 and
   UTF-32 are ambiguous between the form and the scheme.
""")

# ------------------------------------------------- 5. where it bites
say("5. THE ONE PLACE THE AMBIGUITY IS NOT HARMLESS")
probe = b"\x41\x00"
print(f"""
   Two bytes, {hexs(probe)}, with no mark in front of them. They are
   well formed under both orders, so nothing here is an error:
""")
for codec in ("utf-16", "utf-16le", "utf-16be"):
    out = probe.decode(codec)
    print(f"   .decode({codec!r:10}) -> {out!r:8} U+{ord(out):04X}   {unicodedata.name(out)}")
print("""
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
""")

# ---------------------------------------------------------------- 6. TES
say("6. TRANSFER ENCODING SYNTAX -- and why it is outside the model")
text = "Hi"
print(f"\n   base64 of {text!r}, once per scheme:\n")
for codec in ("utf-8", "utf-16le", "utf-16be"):
    raw = text.encode(codec)
    print(f"   {codec:9} {hexs(raw):14} -> {base64.b64encode(raw).decode()}")
print(f"""
   One text, three payloads, three base64 strings. base64 never saw a
   character; it transformed the bytes layer 4 handed it. That is why
   UTR #17 keeps it OUTSIDE the four levels -- it works the same on a
   PNG -- and why "we base64 the field" is not a complete statement
   until the scheme is named.

   And one that reaches back up the stack instead:

   json.dumps({text!r})          ->  {json.dumps(text)}
   json.dumps('\\U0001F600')  ->  {json.dumps(emoji)}

   Those escapes are not bytes and not code points: {json.dumps(emoji)[1:-1]}
   is the surrogate pair from section 3. JSON's escape syntax names
   UTF-16 CODE UNITS, so a format whose bytes are UTF-8 spells one
   character with two escapes borrowed from a form it does not use.
""")
