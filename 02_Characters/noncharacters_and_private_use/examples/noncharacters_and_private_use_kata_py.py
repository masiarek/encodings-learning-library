#!/usr/bin/env python3
"""Answer key: five code points, and the one an encoder actually refuses.

Every claim here is either arithmetic (the shape of the number line) or a
stability guarantee (the noncharacter set is immutable, an assigned name never
changes). Nothing is read out of the version-dependent part of the table, so
this key is the same under any Python on any runner -- which is the rule
[the table has a version] sets and the reason the fifth row below is described
rather than looked up.
"""

import unicodedata
import xml.etree.ElementTree as ET

FIVE = [
    (0xFFFE, "noncharacter -- the last but one code point of the BMP"),
    (0xFDD0, "noncharacter -- first of the block of 32"),
    (0xE000, "private use -- first of the BMP area"),
    (0xD800, "surrogate -- a high surrogate, on its own"),
    (0x0378, "unassigned -- a gap that may be filled one day"),
]


def utf8(cp: int):
    """Encode, the way a conformant encoder would, and report the verdict."""
    try:
        return chr(cp).encode("utf-8").hex(" "), None
    except ValueError as exc:  # UnicodeEncodeError is a subclass
        return None, type(exc).__name__


print("THE QUESTION: WHICH DOES A UTF-8 ENCODER REFUSE?")
print("-" * 72)
print("   code point   UTF-8              verdict   what it is")
refused = 0
for cp, what in FIVE:
    hexed, err = utf8(cp)
    refused += err is not None
    print("   U+%-10s %-18s %-9s %s" % (
        "%04X" % cp, hexed or "--", "refused" if err else "encoded", what))
print()
print("   refused: %d of %d" % (refused, len(FIVE)))
print()
print("   ONE. Not four, and not three. The one refusal is U+D800, and it is")
print("   refused for a reason no reader guesses from the list: a surrogate is")
print("   not a Unicode SCALAR VALUE, so no UTF has a spelling for it. It is")
print("   plumbing that UTF-16 reserved for itself in 1996.")
print()
print("   Everything else on the list encodes. The two noncharacters encode,")
print("   the private-use character encodes, and so does the unassigned code")
print("   point that is not anything yet. Reserved is not invalid, and a")
print("   conformant DECODER must hand all four of them back to you unchanged")
print("   rather than filtering them out.")
print()

print("THE SECOND HALF: EVERY LAYER DRAWS ITS OWN LINE")
print("-" * 72)
print("   code point   encoder  name()      XML 1.0  General_Category")
for cp, _ in FIVE:
    hexed, err = utf8(cp)
    try:
        unicodedata.name(chr(cp))
        named = "yes"
    except ValueError:
        named = "ValueError"
    try:
        ET.fromstring("<a>&#x%X;</a>" % cp)
        xml = "carries"
    except ET.ParseError:
        xml = "refuses"
    print("   U+%-10s %-8s %-11s %-8s %s" % (
        "%04X" % cp, "refuses" if err else "encodes", named, xml,
        unicodedata.category(chr(cp))))
print()
print("   Four columns, four different answers about the same five values.")
print("   The encoder refuses one. XML refuses TWO, and the second one is the")
print("   interesting half: U+FFFE falls outside XML 1.0's Char production")
print("   while U+FDD0, equally and identically a noncharacter, does not.")
print("   unicodedata names none of the five. And the category column puts")
print("   the two noncharacters in the same box as the merely unassigned")
print("   U+0378, because Cn means unassigned and that is what they are.")
print()
print("   The lesson is not that one of these is right. It is that 'invalid'")
print("   is never a property of a code point on its own -- it is a property")
print("   of a code point AND the door it is standing at.")
print()

print("AND THE PART THE QUESTION DOES NOT ASK")
print("-" * 72)
print("   Encoding is not the same question as interchange. All four of the")
print("   encodable rows above go into a file happily. Only the first two")
print("   below are things you may legitimately SEND someone, and even the")
print("   first carries a warning:")
print()
print("      U+0378   unassigned   nothing forbids it, and it may become a")
print("                            real letter, at which point your data is")
print("                            retroactively about something")
print("      U+E000   private use  fine inside the agreement that defines it,")
print("                            and meaningless one hop outside")
print("      U+FDD0   noncharacter never. Reserved for internal use, and the")
print("      U+FFFE   noncharacter guarantee that they are never in the input")
print("                            is exactly what they are worth")
print()
print("   Which is why the answer to 'is this legal?' is one, and the answer")
print("   to 'may I put it in the export?' is a different number entirely.")
