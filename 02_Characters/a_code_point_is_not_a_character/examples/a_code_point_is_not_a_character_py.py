#!/usr/bin/env python3
"""Five rulers along one string, and the four this program is allowed to record.

Bytes, UTF-16 code units, code points, grapheme clusters, terminal columns.
Five questions, five different numbers, none of them wrong. len() answers the
third one in Python and the first one in Rust, and a person asking "how many
characters" almost always means the fourth.

The fifth ruler is here too, and it is the one this program does NOT read out
of the Unicode table -- section 5 says why, and does the reading separately so
you can see the difference.

Run:  python3 a_code_point_is_not_a_character_py.py
"""

import unicodedata as ud

# --------------------------------------------------------------------------
# THE LADDER. Five strings from the house cast, ordered so that each one adds
# exactly one new disagreement to the row above it. Every invisible code point
# is written as an escape: a combining mark and a joiner are invisible in an
# editor too, so a literal here would be a claim nobody could check by reading.
# --------------------------------------------------------------------------
LADDER = [
    ("A",             "A",                        "all five rulers agree"),
    ("cafe + U+0301", "cafe\u0301",               "a mark is its own code point"),
    ("nihongo",       "\u65e5\u672c\u8a9e",        "a wide character costs two columns"),
    ("grinning face", "\U0001f600",               "above U+FFFF: two UTF-16 units"),
    ("family",        "\U0001f468\u200d\U0001f469\u200d\U0001f467",
                                                  "one picture, five code points"),
]

ZWJ = 0x200D
COMBINING_DIACRITICAL_MARKS = range(0x0300, 0x0370)


# --------------------------------------------------------------------------
# RULERS 1-3. Arithmetic over the code point numbers, using rules that are
# frozen: UTF-8 spends 1/2/3/4 bytes on the four ranges it defines, UTF-16
# spends one unit inside the BMP and a surrogate pair above it, and a code
# point's number never changes. Nothing here asks the Unicode table anything,
# which is why these three may be recorded as an answer key.
# --------------------------------------------------------------------------
def utf8_bytes(s: str) -> int:
    return len(s.encode("utf-8"))


def utf16_units(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def code_points(s: str) -> int:
    return len(s)                      # Python's len() counts code points


# --------------------------------------------------------------------------
# RULER 4. A deliberately partial grapheme segmenter.
#
# UAX #29 defines the extended grapheme cluster with a list of numbered
# boundary rules. This implements two of them, over code point ranges written
# out here rather than looked up:
#
#   GB9   -- an Extend character joins the cluster before it. Approximated by
#            the Combining Diacritical Marks block, U+0300..U+036F, plus ZWJ,
#            which UAX #29 also classes as Extend.
#   GB11  -- and then ZWJ joins what comes AFTER it as well, which is the half
#            that makes a family emoji one cluster instead of five.
#
# Section 4 lists what that leaves out. The point of hand-rolling it is not
# that it is good; it is that you can read every rule it knows.
# --------------------------------------------------------------------------
def clusters(s: str) -> list[str]:
    out: list[str] = []
    join_next = False
    for ch in s:
        cp = ord(ch)
        extend = cp in COMBINING_DIACRITICAL_MARKS or cp == ZWJ
        if out and (join_next or extend):        # GB9 / GB11
            out[-1] += ch
        else:
            out.append(ch)
        join_next = cp == ZWJ                    # GB11, second half
    return out


def graphemes(s: str) -> int:
    return len(clusters(s))


# --------------------------------------------------------------------------
# RULER 5. Terminal columns -- and the number below is this program's
# assumption, not your interpreter's answer.
#
# A width class is a Unicode table property, so reading it here would make the
# recorded output a fact about whichever Python ran it. Worse, it would be a
# fact about the wrong program: the terminal drawing your text has its own
# width table, compiled into the terminal, at its own version. So this table
# is written out, and section 5 asks unicodedata separately and prints the
# comparison as a question rather than as a key.
# --------------------------------------------------------------------------
ASSUMED_WIDTH = [
    (range(0x0300, 0x0370), 0, "combining marks take no column of their own"),
    (range(0x200D, 0x200E), 0, "ZWJ is a joiner, not a glyph"),
    (range(0x4E00, 0xA000), 2, "CJK ideographs are drawn double-width"),
    (range(0x1F300, 0x1FB00), 2, "emoji are drawn double-width"),
]
DEFAULT_WIDTH = 1


def assumed_width(ch: str) -> int:
    for span, width, _ in ASSUMED_WIDTH:
        if ord(ch) in span:
            return width
    return DEFAULT_WIDTH


def columns(s: str) -> int:
    return sum(assumed_width(ch) for ch in s)


def main() -> None:
    print("1. FIVE RULERS, ONE STRING AT A TIME")
    print(f"   {'bytes':>5} {'u16':>4} {'chars':>5} {'graph':>5} {'cols':>4}   what it is")
    for label, s, why in LADDER:
        print(f"   {utf8_bytes(s):>5} {utf16_units(s):>4} {code_points(s):>5} "
              f"{graphemes(s):>5} {columns(s):>4}   {label} -- {why}")
    print()
    print("   bytes  what a file costs, and what Rust's .len() returns")
    print("   u16    16-bit units: Java, JavaScript and ABAP call these characters")
    print("   chars  code points: what Python's len() returns")
    print("   graph  grapheme clusters: what a cursor moves over, and what a")
    print("          person means by 'character'")
    print("   cols   how wide a terminal draws it -- see section 5")
    print()

    print("2. EACH ROW SPLITS ONE MORE COLUMN OFF THE OTHERS")
    print("   A               1 1 1 1 1   the case that teaches nothing, and the")
    print("                               reason every other row is surprising")
    print("   cafe + U+0301   bytes and code points part company, and so do code")
    print("                   points and graphemes: 5 code points, 4 graphemes,")
    print("                   and it prints as four letters")
    print("   nihongo         3 code points, 9 bytes, 6 columns -- the first row")
    print("                   where the terminal disagrees with everybody")
    print("   grinning face   1 code point and 2 UTF-16 units: the BMP boundary,")
    print("                   which is why a Java length() says 2")
    print("   family          every ruler gives a different answer")
    print()

    print("3. THE FAMILY, CODE POINT BY CODE POINT")
    family = LADDER[-1][1]
    for ch in family:
        print(f"   U+{ord(ch):<6X} {utf8_bytes(ch)} bytes  {utf16_units(ch)} u16   {ud.name(ch)}")
    print(f"   {len(family)} code points, {utf8_bytes(family)} bytes, "
          f"{utf16_units(family)} UTF-16 units, and {graphemes(family)} cluster.")
    print("   A name is the one question this program asks the Unicode table,")
    print("   and it is one of the few questions whose answer Unicode promises")
    print("   never to change. That is why this section quotes names, and why")
    print("   section 5 refuses to quote a width.")
    print()

    print("4. WHAT THIS SEGMENTER DOES NOT IMPLEMENT")
    for label, s, _ in LADDER:
        parts = " | ".join(clusters(s))
        print(f"   {label:<15} -> {len(clusters(s))} cluster(s): {parts}")
    print()
    print("   Two rules, GB9 and GB11, over ranges written into this file. A")
    print("   real UAX #29 implementation reads the Grapheme_Cluster_Break")
    print("   property for every code point instead, and it also handles:")
    print("     - CR LF as one cluster, and controls as their own")
    print("     - spacing marks, which this misses outside U+0300..U+036F")
    print("     - regional indicator pairs, so a flag is one cluster")
    print("     - emoji modifiers, so a skin tone joins the emoji before it")
    print("     - Indic conjunct clusters, the newest rule in the list")
    print("   Python has no grapheme segmenter in the standard library; the")
    print("   third-party 'regex' module spells one \\X. Rust's std has none")
    print("   either, and the unicode-segmentation crate is the usual answer.")
    print()

    print("5. THE FIFTH RULER IS NOT A FACT ABOUT THE STRING")
    print("   The 'cols' column above came from this table, written into this")
    print("   program on purpose:")
    for span, width, why in ASSUMED_WIDTH:
        last = span.stop - 1
        rng = (f"U+{span.start:04X}" if last == span.start
               else f"U+{span.start:04X}..U+{last:04X}")
        print(f"     {rng:<18} -> {width}   {why}")
    print(f"     {'everything else':<18} -> {DEFAULT_WIDTH}")
    print()
    print("   unicodedata.east_asian_width() would answer this too, and this")
    print("   program does not call it. A width class is read out of the")
    print("   Unicode table, so recording the answer would make this file a")
    print("   fact about whichever Python ran it -- and unlike a name, a width")
    print("   class is not one of the properties Unicode promises to freeze.")
    print("   The page prints what this machine's table says, in a fence with")
    print("   a date on it, which is where a measurement like that belongs.")
    print()
    print("   It would be the wrong program to ask in any case. The terminal")
    print("   drawing this text has its own width table, compiled into the")
    print("   terminal, at its own Unicode version -- so a width from Python")
    print("   is a guess about a different program on the same machine.")
    print()
    fam5 = LADDER[-1][1]
    joined = sum(DEFAULT_WIDTH if w == 0 else w
                 for w in (assumed_width(c) for c in fam5))
    print("   The family emoji has THREE defensible column counts, and that is")
    print("   the strongest evidence here that the fifth ruler measures the")
    print("   terminal rather than the string:")
    print(f"     {joined:>2}  every code point counted, joiners included")
    print(f"     {columns(fam5):>2}  the same sum, with the joiners given no width")
    print("      2  what a terminal that understands ZWJ draws: one glyph,")
    print("         the same width as any other emoji")
    print("   All three follow a defensible rule, and none of them is a")
    print("   property of the string. Your own terminal has already picked one")
    print("   of them to draw the table in section 1 -- look at whether the")
    print("   columns there line up, and you will know which.")
    print()

    print("6. SO WHAT DOES len() ANSWER?")
    fam = LADDER[-1][1]
    print(f"   Python   len(s)                 -> {len(fam):>2}   code points")
    print(f"   Python   len(s.encode())        -> {len(fam.encode()):>2}   UTF-8 bytes")
    print(f"   Rust     s.len()                -> {len(fam.encode()):>2}   UTF-8 bytes")
    print(f"   Rust     s.chars().count()      -> {len(fam):>2}   code points")
    print(f"   Java/JS  s.length               -> {utf16_units(fam):>2}   UTF-16 units")
    print(f"   a person 'how many characters'  -> {graphemes(fam):>2}   grapheme cluster")
    print()
    print("   Four of the six rows are the same question asked of different")
    print("   units, and the last one is the question everybody actually asked.")
    print("   No standard library on this page answers it.")


if __name__ == "__main__":
    main()
