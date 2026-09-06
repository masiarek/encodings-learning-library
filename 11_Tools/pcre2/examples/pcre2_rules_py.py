#!/usr/bin/env python3
"""The four rules behind `rg -P`, applied by hand in the standard library.

`rg` is not on either CI runner, so no answer key on this page can be recorded
from the tool. What CAN be checked is the model: Python's `re` is a backtracking
engine, like PCRE2, and Python's `str`/`bytes` split is the same Unicode/byte
split both of ripgrep's engines make. Each section states a rule, applies it to
the same input rg was measured on, and prints the number rg printed.

The honest limit is the same as the ripgrep page's: this tests the model, not the
tool. That is why the session on the page is dated and names its machines.
"""

import re
import unicodedata

NFC = "café"  # c a f é          -- one code point for the accented letter
NFD = "café"  # c a f e + U+0301 -- the accent is its own code point


def show(label: str, value: object) -> None:
    print(f"   {label:<40} {value}")


def graphemes(s: str) -> int:
    """Count grapheme clusters -- COMBINING MARKS ONLY.

    A real implementation follows UAX #29 and also joins regional indicators,
    ZWJ sequences and Hangul jamo. This narrow rule is enough for the accent on
    this page and is stated as narrow rather than sold as general.
    """
    return sum(1 for ch in s if unicodedata.combining(ch) == 0)


print("RULE 1. FOUR ANSWERS TO 'HOW LONG IS café'")
for name, s in [("NFC  café", NFC), ("NFD  cafe+U+0301", NFD)]:
    show(f"{name}: UTF-8 bytes", len(s.encode("utf-8")))
    show(f"{name}: UTF-16 code units", len(s.encode("utf-16-le")) // 2)
    show(f"{name}: code points", len(s))
    show(f"{name}: grapheme clusters", graphemes(s))
show("NFC(NFD form) is the NFC form?", unicodedata.normalize("NFC", NFD) == NFC)
show("but the two literals compare equal?", NFC == NFD)
print("   The NFD row is why this page exists. Five code points, four graphemes,")
print("   and a regex quantifier has to mean one or the other. rg's default")
print("   engine counts code points, so '^.{5}$' matches and '^.{4}$' does not;")
print("   PCRE2's \\X counts grapheme clusters, so '^\\X{4}$' matches. Both are")
print("   right about different questions, and only one of them is the question")
print("   a person asking 'how many characters' means.")

print()
print("RULE 2. A BACKTRACKING ENGINE ACCEPTS PATTERNS AN AUTOMATON REFUSES")
show("lookbehind '(?<=caf)e' on NFD", bool(re.search(r"(?<=caf)e", NFD)))
show("backreference r'(\\w)\\1' on 'aa'", bool(re.search(r"(\w)\1", "aa")))
try:
    re.compile(r"\X")
    show("does Python's re have \\X?", "yes")
except re.error as exc:
    show("does Python's re have \\X?", f"no -- {exc.msg}")
print("   Python's re is backtracking, like PCRE2, so the first two work here and")
print("   in `rg -P`, and rg's default engine rejects both by design: it is a")
print("   finite automaton and guarantees linear time, which those features cost.")
print("   But the third line is the one to read twice. \\X is not something you")
print("   get for free by backtracking -- Python backtracks and does not have it.")
print("   It is a feature PCRE2 chose to implement, which is why 'rg -P' can")
print("   count graphemes and no other tool in this chapter can.")

print()
print("RULE 3. A PATTERN CAN COMPILE AND STILL NEVER MATCH")
TEXT = "a\nb\n"
pat = re.compile("a\nb")
show("pattern compiles?", True)
show("matches the whole text?", bool(pat.search(TEXT)))
show("matches any single LINE?", any(pat.search(line) for line in TEXT.splitlines()))
print("   Both greps and rg search a line at a time, and a line by definition has")
print("   no newline in it -- so a pattern containing one can never match, however")
print("   well it compiles. That is the whole of 'rg -P \"a\\nb\"' printing nothing.")
print("   rg's default engine refuses the pattern up front and says so in four")
print("   lines, naming the -U flag; PCRE2 compiles it and returns no match, which")
print("   is indistinguishable from the file not containing what you asked for.")
print("   --engine=auto inherits the silence, because 'the default engine could")
print("   not compile it' is exactly its rule for switching to PCRE2.")

print()
print("RULE 4. ON ENCODING QUESTIONS THE TWO ENGINES AGREE")
KELVIN = "K"  # KELVIN SIGN, not the letter K
show("U+212A is the letter K?", KELVIN == "K")
show("U+212A lowercases to 'k'?", KELVIN.lower() == "k")
show("'żółw' matches ^\\w+$ on str", bool(re.fullmatch(r"\w+", "żółw")))
show("...and on bytes (the --no-unicode model)", bool(re.fullmatch(rb"\w+", "żółw".encode())))
show("'٤٢' matches ^\\d+$ on str", bool(re.fullmatch(r"\d+", "٤٢")))
print("   Measured on the page: rg's two engines give the same answer to every one")
print("   of these -- same case folding, same Unicode \\w and \\d, same reduction to")
print("   ASCII under --no-unicode, and the same behaviour on a file of invalid")
print("   UTF-8. So -P is not a different opinion about your text. It is a")
print("   different set of questions you may ask about it, at a different price.")
