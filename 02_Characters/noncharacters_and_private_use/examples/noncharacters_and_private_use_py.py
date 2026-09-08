#!/usr/bin/env python3
"""Two kinds of permanently reserved code point, and the difference between
"reserved" and "invalid".

Nothing below is typed from the standard's prose. Both sets are GENERATED from
the rules that define them, and both are then cross-examined -- the private-use
set against this interpreter's own table, the noncharacter set against every
UTF codec in the stdlib. A number copied out of a FAQ is the kind of number
that gets copied wrong.

No noncharacter and no private-use character is ever printed as itself. They
are shown as escapes with the name of the range they came from, because a raw
one in a page renders as a box, or as nothing, or as whatever the reader's
font privately decided.
"""

import json
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET

RULE = "-" * 72
PLANES = 17  # plane 0 (the BMP) plus 16 supplementary planes


def is_noncharacter(cp: int) -> bool:
    """The standard's two rules, and nothing else."""
    return (cp & 0xFFFF) in (0xFFFE, 0xFFFF) or 0xFDD0 <= cp <= 0xFDEF


# The three ranges the standard designates Private_Use, written as ranges
# rather than as a total -- the total is derived below and then checked.
PUA_RANGES = [
    (0xE000, 0xF8FF, "Private Use Area (BMP)"),
    (0xF0000, 0xFFFFD, "Supplementary Private Use Area-A (plane 15)"),
    (0x100000, 0x10FFFD, "Supplementary Private Use Area-B (plane 16)"),
]

NONCHARS = [cp for cp in range(0x110000) if is_noncharacter(cp)]
PRIVATE = [cp for lo, hi, _ in PUA_RANGES for cp in range(lo, hi + 1)]

print("1. THE SET, GENERATED RATHER THAN QUOTED")
print(RULE)
arabic = [cp for cp in NONCHARS if 0xFDD0 <= cp <= 0xFDEF]
plane_ends = [cp for cp in NONCHARS if (cp & 0xFFFF) in (0xFFFE, 0xFFFF)]
print("   U+FDD0..U+FDEF, one block in the middle of the BMP     %3d" % len(arabic))
print("   the last two code points of each of %d planes          %3d" % (PLANES, len(plane_ends)))
print("                                                         ----")
print("   noncharacters, total                                   %3d" % len(NONCHARS))
print()
print("   first four   %s" % "  ".join("U+%04X" % cp for cp in NONCHARS[:4]))
print("   last four    %s" % "  ".join("U+%04X" % cp for cp in NONCHARS[-4:]))
print()
print("   That 66 may go in an answer key, which almost nothing read out of")
print("   the Unicode table may. The set of noncharacters is formally")
print("   IMMUTABLE -- a stability policy, not a fact about this release --")
print("   so the number is arithmetic over a rule that cannot change, rather")
print("   than a lookup a September might move.")
print()

print("2. RESERVED IS NOT INVALID: EVERY UTF ENCODES ALL 66")
print(RULE)
for enc in ("utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be", "utf-7"):
    failed = 0
    for cp in NONCHARS:
        try:
            if chr(cp).encode(enc).decode(enc) != chr(cp):
                failed += 1
        except UnicodeError:
            failed += 1
    print("   %-10s  encodes and decodes back all %d:  %s" % (enc, len(NONCHARS), failed == 0))
print()
print("   Not one refusal, and not one loss. To an encoder a noncharacter is")
print("   an ordinary code point -- three UTF-8 bytes for the BMP ones, four")
print("   for the rest:")
for cp in (0xFDD0, 0xFFFE, 0xFFFF, 0x1FFFE, 0x10FFFF):
    b = chr(cp).encode("utf-8")
    print("      U+%-8X %-12s %d bytes" % (cp, b.hex(" "), len(b)))
print()
print("   The contrast is the whole point. THESE two are refused, and neither")
print("   refusal has anything to do with being reserved:")
for cp, why in ((0xD800, "a surrogate: not a scalar value, so no UTF carries it"),
                (0x110000, "not a code point at all -- past U+10FFFF")):
    try:
        chr(cp).encode("utf-8")
        verdict = "encoded?!"
    except (UnicodeEncodeError, ValueError) as exc:
        verdict = type(exc).__name__
    print("      U+%-8X %-20s %s" % (cp, verdict, why))
print()
print("   So of everything a reader files under 'not really a character',")
print("   the encoder objects to exactly one class, and the noncharacters")
print("   are not it. A conformant decoder may not reject them either: the")
print("   standard requires the value to be preserved, not sanitised.")
print()

print("3. WHICH IS WHY THE BOM CAN PROVE ANYTHING")
print(RULE)
le = chr(0xFEFF).encode("utf-16-le")
misread = ord(le.decode("utf-16-be"))
print("   U+FEFF written little-endian      %s" % le.hex(" "))
print("   those same bytes read big-endian  U+%04X" % misread)
print("   ...and U+%04X is a noncharacter:  %s" % (misread, is_noncharacter(misread)))
print()
print("   A reader that decodes U+FFFE has not found a rare character. It has")
print("   found a value guaranteed never to mean anything, so it knows for")
print("   certain the byte order is backwards. The reservation is what turns")
print("   a convention into a proof.")
print()

print("4. THE OTHER RESERVATION: PRIVATE USE")
print(RULE)
for lo, hi, label in PUA_RANGES:
    print("   U+%-6X..U+%-7X %7d   %s" % (lo, hi, hi - lo + 1, label))
print("   %-19s %7d   total" % ("", len(PRIVATE)))
print()
from_table = [cp for cp in range(0x110000) if unicodedata.category(chr(cp)) == "Co"]
print("   code points this interpreter's table calls Co (Private_Use):  %d" % len(from_table))
print("   the same set as the three ranges above:                       %s" % (from_table == PRIVATE))
print()
print("   Two independent sources, one answer: the ranges above are written")
print("   from the standard, the Co set is read out of unicodedata. They")
print("   agree exactly, so neither is a typo -- and were a release ever to")
print("   move a boundary, that line would flip to False rather than go")
print("   unnoticed.")
print()
print("   Note where the supplementary areas STOP. Plane 15 ends at U+FFFFD,")
print("   not U+FFFFF, because the last two of every plane are already spoken")
print("   for. The two reservations do not overlap by a single code point.")
print()

print("5. WHAT NEITHER OF THEM HAS -- AND THE ONE DIFFERENCE THE TABLE SEES")
print(RULE)
print("   code point  cat  name()                  alpha  print  what it is")
for cp, what in [
    (0x0041, "an ordinary letter"),
    (0xE000, "private use -- yours by agreement"),
    (0xF8FF, "private use -- Apple's logo, on Apple's machines"),
    (0x100000, "private use, plane 16"),
    (0xFDD0, "noncharacter -- nobody's, ever"),
    (0xFFFE, "noncharacter -- the BOM's mirror"),
    (0x0378, "unassigned -- may become a letter one day"),
]:
    ch = chr(cp)
    try:
        name = unicodedata.name(ch)
    except ValueError:
        name = "ValueError"
    print("   U+%-9s %-4s %-23s %-6s %-6s %s" % (
        "%04X" % cp, unicodedata.category(ch), name,
        ch.isalpha(), ch.isprintable(), what))
print()
print("   Read the category column. Private use is Co and says so. A")
print("   noncharacter is Cn -- and so is U+0378, which is merely unassigned")
print("   and could be a letter in some future release. The table cannot tell")
print("   those two apart, because Cn means UNASSIGNED and a noncharacter is,")
print("   permanently, unassigned.")
print()
print("   And there is no API for it. unicodedata exports %d public names and"
      % len([n for n in dir(unicodedata) if not n.startswith("_")]))
print("   not one of them answers 'is this a noncharacter'. The property is in")
print("   the UCD -- Noncharacter_Code_Point -- and the standard library does")
print("   not expose it. Which is why section 1 generates the set from the two")
print("   rules: not for elegance, but because nothing here will tell you.")
print()

print("6. WHAT HAPPENS WHEN ONE REACHES SOMETHING REAL")
print(RULE)
nc, pua = chr(0xFFFE), chr(0xE000)

print("   JSON")
print("      json.dumps(U+FFFE)                    %s" % json.dumps(nc))
print("      json.dumps(U+E000)                    %s" % json.dumps(pua))
print("      round trips through loads:            %s" % (json.loads(json.dumps(nc)) == nc))
print("      ensure_ascii=False writes the bytes:  %s"
      % json.dumps(nc, ensure_ascii=False).encode("utf-8").hex(" "))
print("      No objection anywhere. \\uFFFE is a well-formed escape and the")
print("      three raw bytes are well-formed UTF-8, so both spellings survive.")
print()

print("   XML -- where the write and the read disagree, inside one module")
el = ET.Element("a")
el.text = nc
written = ET.tostring(el, encoding="unicode")
print("      ET.tostring on U+FFFE                 %s" % written.replace(nc, "\\ufffe"))
try:
    ET.fromstring(written)
    read_back = "parsed"
except ET.ParseError as exc:
    read_back = "ParseError: %s" % str(exc).split(":")[0]
print("      ET.fromstring of what it just wrote   %s" % read_back)
print()
accepted = refused = 0
for cp in NONCHARS:
    try:
        ET.fromstring("<a>&#x%X;</a>" % cp)
        accepted += 1
    except ET.ParseError:
        refused += 1
pua_ok = sum(1 for cp in (0xE000, 0xF8FF, 0xF0000, 0x10FFFD)
             if ET.fromstring("<a>&#x%X;</a>" % cp).text == chr(cp))
print("      of the 66 noncharacters, XML 1.0 accepts       %2d" % accepted)
print("                                     and refuses     %2d" % refused)
print("      the two it refuses                             %s" % " ".join(
    "U+%04X" % cp for cp in NONCHARS if cp in (0xFFFE, 0xFFFF)))
print("      of four private-use code points sampled, XML accepts %d" % pua_ok)
print()
print("      So 'noncharacter' and 'what XML forbids' are two different sets")
print("      that overlap in exactly two places. XML 1.0's Char production")
print("      excludes U+FFFE and U+FFFF and says nothing about the other 64.")
print("      A numeric character reference does not help either: &#xFFFE; is")
print("      refused as well -- the same shape as XML refusing to carry")
print("      U+0001 even when escaped.")
print()

print("   SQLite -- a database in the standard library")
con = sqlite3.connect(":memory:")
con.execute("create table t (x text)")
con.executemany("insert into t values (?)", [(nc,), (pua,)])
rows = [r[0] for r in con.execute("select x from t order by rowid")]
print("      stored and read back unchanged:       %s" % (rows == [nc, pua]))
print("      SQL length() of each:                 %s"
      % [r[0] for r in con.execute("select length(x) from t order by rowid")])
print("      No complaint. TEXT is UTF-8, these are UTF-8, and the engine has")
print("      no opinion about what the code points were supposed to mean.")
print()

print("   Sorting and word breaking -- the quiet one")
words = ["apple", "zebra", pua * 2, nc * 2, "\N{LATIN SMALL LETTER E WITH ACUTE}clair",
         "\N{GRINNING FACE}"]
order = sorted(words)
print("      of %d strings sorted, the two reserved ones land at %s"
      % (len(words), [order.index(w) + 1 for w in (pua * 2, nc * 2)]))
print("      'a\\ue000b'.split()          ->  %d piece(s)" % len(("a" + pua + "b").split()))
print("      'a\\ue000b'.isidentifier()   ->  %s" % ("a" + pua + "b").isidentifier())
print("      'a\\ue000b'.isprintable()    ->  %s" % ("a" + pua + "b").isprintable())
print("      Default sort is code point order, so a private-use string lands")
print("      after every Latin letter and ahead of the emoji -- an order")
print("      nobody chose. There is no collation weight to consult and no")
print("      word-break class to honour, because the standard declines to")
print("      have an opinion about what you decided these mean.")
print()

print("7. THE TWO RESERVATIONS, SIDE BY SIDE")
print(RULE)
ROWS = [
    ("how many", "%d" % len(NONCHARS), "%d" % len(PRIVATE)),
    ("General_Category", "Cn (unassigned)", "Co (private use)"),
    ("has a name", "no", "no"),
    ("well-formed in every UTF", "yes", "yes"),
    ("will ever be assigned", "no, and guaranteed so", "no, that is the point"),
    ("meaning", "none, permanently", "whatever you agreed"),
    ("safe to interchange", "no -- that is the deal", "only inside the agreement"),
    ("what it is for", "your program's internals", "your font, your protocol"),
]
print("   %-26s %-24s %s" % ("", "noncharacter", "private use"))
for label, a, b in ROWS:
    print("   %-26s %-24s %s" % (label, a, b))
print()
print("   One sentence apart: private use is YOURS TO DEFINE, a noncharacter")
print("   is NOBODY'S, EVER. Both are useless for interchange, and useful for")
print("   exactly that reason -- a value you can be certain did not arrive")
print("   from outside is the only kind of sentinel that cannot be forged.")
