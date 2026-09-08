#!/usr/bin/env python3
"""Wrapping text is not splitting on spaces, and `textwrap` only knows spaces.

Japanese and Thai are written without spaces between words. So the question
`where may this line break` cannot be answered by looking for a space -- and
the two languages do not even answer it the same way:

    Japanese  a RULE decides, from the classes of the two adjacent characters
    Thai      a DICTIONARY decides, because the rule is `between two words`

This program hand-rolls enough of UAX #14 to break the Japanese string
correctly, and then shows that the same machinery cannot touch the Thai one.

Run:  python3 where_a_line_may_break_py.py
"""

# ----------------------------------------------------------------------
# The line-break classes, WRITTEN DOWN HERE rather than looked up.
#
# `unicodedata` does not expose the UAX #14 property at all -- see section 5 --
# so there is nothing to look it up in. Transcribing the handful of classes
# this page needs is also what keeps the answer key honest: a table in this
# file is the same on every machine, and the runner's Unicode version is not.
# ----------------------------------------------------------------------
OP = "「『（［"          # Open Punctuation   -- never break AFTER one
CL = "」』）］。、"        # Close Punctuation  -- never break BEFORE one
EX = "！？"              # Exclamation        -- never break BEFORE one
# Nonstarter -- never break BEFORE one. UAX #14 calls the prolonged sound mark
# and the small kana `CJ`, and resolves CJ to NS only in STRICT mode; see the
# note at the end of section 5.
NS = "ー々ぁぃぅぇぉっゃゅょァィゥェォッャュョ"

JA = "日本語は「スペース」を使いません。"
TH = "ภาษาไทย"   # two words, no space: ภาษา (language) + ไทย (Thai)


def klass(c: str) -> str:
    """The one-line class of a character, for the four classes this page uses."""
    if c in OP:
        return "OP"
    if c in CL:
        return "CL"
    if c in EX:
        return "EX"
    if c in NS:
        return "NS"
    return "ID"  # Ideographic: kanji and ordinary kana, which may break freely


def may_break_between(left: str, right: str) -> bool:
    """UAX #14, the three rules that matter for ordinary Japanese prose."""
    if klass(right) in ("CL", "EX", "NS"):
        return False        # LB13/LB21: nothing may START a line with these
    if klass(left) == "OP":
        return False        # LB14: an opening bracket keeps the next character
    return True             # LB31: otherwise, between two ideographs, break


def break_points(text: str) -> list[int]:
    return [i for i in range(1, len(text)) if may_break_between(text[i - 1], text[i])]


def wrap_by_rule(text: str, width: int) -> list[str]:
    """Greedy wrap that only breaks where the rules allow."""
    allowed = set(break_points(text))
    lines, start = [], 0
    while start < len(text):
        if len(text) - start <= width:
            lines.append(text[start:])
            break
        cut = next((i for i in range(start + width, start, -1) if i in allowed), None)
        if cut is None:                       # no legal break: overrun rather than lie
            cut = min(start + width, len(text))
        lines.append(text[start:cut])
        start = cut
    return lines


def show(lines: list[str], indent: str = "     ") -> None:
    for n, line in enumerate(lines, 1):
        print(f"{indent}{n}  |{line}|")


def rule(title: str) -> None:
    print(title)
    print("-" * 72)


def main() -> None:
    import textwrap

    # ------------------------------------------------------------------
    rule("1. THE STRING, AND WHY `SPLIT ON WHITESPACE` HAS NOTHING TO WORK WITH")
    print(f"   {JA}")
    print(f"   {len(JA)} characters, {len(JA.encode())} bytes, and:")
    print(f"     JA.split()      -> {JA.split()}")
    print(f"     ' ' in JA       -> {' ' in JA}")
    print()
    print("   One 'word' as far as every whitespace-based tool is concerned.")
    print("   It is an ordinary sentence: `Japanese does not use spaces.`")
    print()

    # ------------------------------------------------------------------
    rule("2. WHAT textwrap DOES WITH IT")
    print("   textwrap.wrap(text, 8):")
    show(textwrap.wrap(JA, 8))
    print()
    print("   Look at the last line. It is a full stop, alone, at the start of")
    print("   a line. In Japanese typesetting that is the first rule anyone")
    print("   learns -- kinsoku shori, `forbidden-character handling` -- and it")
    print("   is forbidden in every style guide, every word processor and every")
    print("   browser. `textwrap` is not broken; it was asked a question about")
    print("   spaces and answered it.")
    print()

    # ------------------------------------------------------------------
    rule("3. THE SAME STRING, BROKEN BY RULE")
    print("   Three rules, and the class of the two adjacent characters decides:")
    print()
    print("     never break BEFORE  CL (closing bracket, 。 、)  EX (！？)  NS (ー, small kana)")
    print("     never break AFTER   OP (opening bracket)")
    print("     otherwise, between two ideographs, break freely")
    print()
    print("   Every position in the sentence, and the verdict:")
    print()
    print(f"   {'pos':>3}  {'left':<6} {'right':<6} {'classes':<10} break?")
    for i in range(1, len(JA)):
        left, right = JA[i - 1], JA[i]
        ok = may_break_between(left, right)
        pair = f"{klass(left)}-{klass(right)}"
        print(f"   {i:>3}  {left:<6} {right:<6} {pair:<10} {'yes' if ok else 'NO'}")
    print()
    print("   wrap_by_rule(text, 8):")
    show(wrap_by_rule(JA, 8))
    print()
    print("   The full stop stayed with its sentence, and the closing bracket")
    print("   stayed with the word it closes. Nothing here consulted a space,")
    print("   a dictionary or a font -- only which of five classes each of two")
    print("   neighbouring characters is in.")
    print()

    # ------------------------------------------------------------------
    rule("4. AND NOW THAI, WHERE THE RULE DOES NOT EXIST")
    print(f"   {TH}   -- {len(TH)} characters, {len(TH.encode())} bytes, no space")
    print("   It is two words: ภาษา (language) + ไทย (Thai). The only correct")
    print("   break is between them, at position 4.")
    print()
    print("   Every position, through the same machinery as section 3:")
    print()
    print(f"   {'pos':>3}  {'left':<6} {'right':<6} {'classes':<10} break?")
    for i in range(1, len(TH)):
        left, right = TH[i - 1], TH[i]
        pair = f"{klass(left)}-{klass(right)}"
        print(f"   {i:>3}  {left:<6} {right:<6} {pair:<10} "
              f"{'yes' if may_break_between(left, right) else 'NO'}")
    print()
    print("   Six positions, six yeses. The rules cannot see the one answer that")
    print("   matters, because in Thai the boundary is not a fact about two")
    print("   adjacent characters -- it is a fact about the vocabulary. UAX #14")
    print("   says so itself: it puts Thai in class SA, `Complex Context")
    print("   Dependent`, and hands the problem to a lexical analyser.")
    print()
    print("   textwrap on the same string, at four widths:")
    for w in (3, 4, 5, 6):
        print(f"     width {w}  ->  {textwrap.wrap(TH, w)}")
    print()
    print("   Width 4 is CORRECT. It is also luck: it is the only width whose")
    print("   greedy cut happens to land on the boundary, and the three either")
    print("   side of it split a word down the middle. A wrapper that is right")
    print("   at one width and wrong at the next is not a wrapper that knows")
    print("   anything -- which is the most useful thing on this page, because")
    print("   testing at one width would have shown a pass.")
    print()

    # ------------------------------------------------------------------
    rule("5. WHAT THE STANDARD LIBRARY HAS, AND WHAT IT DOES NOT")
    import unicodedata
    props = sorted(n for n in dir(unicodedata) if not n.startswith("_"))
    linebreak = [n for n in props if "line" in n.lower() or "break" in n.lower()]
    print(f"   properties `unicodedata` exposes that concern line breaking: {len(linebreak)}")
    print()
    print("   It has category, combining class, decomposition, bidirectional,")
    print("   east_asian_width and normalize. It does not have Line_Break, so")
    print("   there is nothing in the standard library to look a class up in --")
    print("   which is why the table at the top of this file is a table at the")
    print("   top of this file.")
    print()
    print("   Two more things that were NOT done here, deliberately:")
    print()
    print("     * Nothing measured a COLUMN. This program's `width` counts")
    print("       characters, and a real wrapper counts columns or pixels --")
    print("       every one of the CJK characters above is two columns wide.")
    print("       Measuring that means reading east_asian_width, which is a")
    print("       fact about the machine, and this page keeps such facts out")
    print("       of its answer key.")
    print("     * Nothing here is the whole of UAX #14. It defines dozens of")
    print("       classes and thirty-odd numbered rules; this is four classes")
    print("       and three rules, chosen to be exactly enough for one sentence.")
    print("       It is a demonstration of the mechanism, not an implementation")
    print("       of the annex.")
    print()
    print("   And one place where even this small table took a side. The")
    print("   prolonged sound mark ー and the small kana are class CJ,")
    print("   `Conditional Japanese Starter`, which UAX #14 resolves to NS in")
    print("   STRICT mode and to ID in NORMAL and LOOSE mode. The table above")
    print("   picked strict. Under the loose reading, position 7 becomes a legal")
    print("   break and this sentence wraps differently -- so `where may this")
    print("   line break` does not have one answer even after you have the")
    print("   annex, and CSS exposes the choice as `line-break: strict | normal")
    print("   | loose` precisely because publishers disagree about it.")


if __name__ == "__main__":
    main()
