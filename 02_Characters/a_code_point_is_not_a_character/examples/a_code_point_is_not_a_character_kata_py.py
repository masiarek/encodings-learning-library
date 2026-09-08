#!/usr/bin/env python3
"""Answers to the kata: five numbers for one Polish word, spelled two ways.

The word is 'żółw' -- turtle -- and the trap is in the second spelling. Three
of its four letters carry something above or through them, and only two of
them come apart.

Run:  python3 a_code_point_is_not_a_character_kata_py.py
"""

# Both spellings are written out as escapes rather than pasted. A decomposed
# string is the same picture as a composed one, so a literal here would be a
# claim no reader -- and no author -- could check by looking.
COMPOSED = "\u017c\u00f3\u0142w"          # ż ó ł w, one code point per letter
DECOMPOSED = "z\u0307o\u0301\u0142w"      # z +dot, o +acute, ł unchanged, w
FAMILY = "\U0001f468\u200d\U0001f469\u200d\U0001f467"

ZWJ = 0x200D
MARKS = range(0x0300, 0x0370)


def graphemes(s: str) -> int:
    """The page's two rules: a mark joins backwards, ZWJ joins both ways."""
    count = 0
    join_next = False
    for ch in s:
        cp = ord(ch)
        if count == 0 or not (join_next or cp in MARKS or cp == ZWJ):
            count += 1
        join_next = cp == ZWJ
    return count


def width(ch: str) -> int:
    cp = ord(ch)
    if cp in MARKS or cp == ZWJ:
        return 0
    if 0x4E00 <= cp <= 0x9FFF or 0x1F300 <= cp <= 0x1FAFF:
        return 2
    return 1


def five(s: str) -> tuple[int, int, int, int, int]:
    return (len(s.encode("utf-8")), len(s.encode("utf-16-le")) // 2, len(s),
            graphemes(s), sum(width(c) for c in s))


def main() -> None:
    print("1. THE FIVE NUMBERS, BOTH SPELLINGS")
    print(f"   {'bytes':>5} {'u16':>4} {'chars':>5} {'graph':>5} {'cols':>4}   spelling")
    for label, s in (("as you would type it", COMPOSED), ("decomposed", DECOMPOSED)):
        b, u, c, g, w = five(s)
        print(f"   {b:>5} {u:>4} {c:>5} {g:>5} {w:>4}   {label}")
    print()
    print("   Both spellings print the same four letters, and a reader cannot")
    print("   tell them apart on screen. Two of the five rulers noticed.")
    print()

    print("2. THE TRAP IS IN THE SECOND ROW: 6 CODE POINTS, NOT 8")
    rows = [
        ("U+017C", "z + U+0307", 2, "ż  the dot above comes off"),
        ("U+00F3", "o + U+0301", 2, "ó  the acute comes off"),
        ("U+0142", "U+0142", 1, "ł  the STROKE does not -- it is drawn through"),
        ("U+0077", "U+0077", 1, "w  nothing to take off"),
    ]
    print(f"   {'composed':<8} {'decomposed':<12} {'cps':>3}   why")
    for comp, dec, n, why in rows:
        print(f"   {comp:<8} {dec:<12} {n:>3}   {why}")
    print(f"   {'':<8} {'':<12} {sum(r[2] for r in rows):>3}   total")
    print()
    print("   Four letters, three of them decorated, and only two come apart.")
    print("   A stroke through a letter is part of the letter; a mark above it")
    print("   is a code point of its own. Nothing about looking at 'ł' tells")
    print("   you which kind it is -- you have to ask.")
    print()
    print("   The graph column did not move, and that is the whole lesson:")
    print("   'żółw' is four graphemes in both spellings, because a grapheme")
    print("   cluster is what a person calls a letter. Only the code point")
    print("   count changed, and code points are the ruler len() reaches for.")
    print()

    print("3. THE COLUMN COUNT HAS MORE THAN ONE RIGHT ANSWER")
    b, u, c, g, w = five(FAMILY)
    print(f"   the family emoji: {b} bytes, {u} u16, {c} code points, {g} grapheme")
    print("   and for columns, three defensible answers:")
    print("      8  every code point counted, joiners included")
    print(f"      {w}  the same sum, with the joiners given no width")
    print("      2  what a terminal that understands ZWJ draws")
    print("   If you wrote one number here and did not hedge, that is the")
    print("   answer this kata was looking for. The other four rulers are")
    print("   properties of the string; the fifth is a property of whatever")
    print("   is drawing it.")


if __name__ == "__main__":
    main()
