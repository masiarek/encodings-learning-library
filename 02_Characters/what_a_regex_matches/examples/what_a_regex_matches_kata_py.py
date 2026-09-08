#!/usr/bin/env python3
"""Answer key: six expressions, and the requirement each one is about.

Every line is stdlib `re` on a `str` or on `bytes`, with no flags beyond the
ones written down. Nothing here depends on the Unicode version -- the six
characters involved were all assigned decades ago -- so a row that does not
match on your machine is a finding rather than a difference of setup.

Run:  python3 what_a_regex_matches_kata_py.py
"""

import re
import unicodedata as ud
import warnings

BAR = "-" * 72

NFC = "café"                # c a f e-acute
NFD = "café"          # c a f e + U+0301 COMBINING ACUTE ACCENT
HINDI = "हिन्दी"
DEVA = "१२३"
LS = "a\u2028b"                   # a + U+2028 LINE SEPARATOR + b

print("PART ONE -- SIX EXPRESSIONS")
print(BAR)
print()

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    amp = bool(re.fullmatch(r"[\w&&\d]", "&"))

rows = [
    ("1", r"len(re.findall(r'\w+', hindi))",
     len(re.findall(r"\w+", HINDI)),
     "RL1.2a", "one word, three matches: \\w has no Mark in it"),
    ("2", r"bool(re.fullmatch(rb'\d+', deva.encode()))",
     bool(re.fullmatch(rb"\d+", DEVA.encode())),
     "--", "a bytes pattern is ASCII-only; the str one answers True"),
    ("3", r"bool(re.search(composed, decomposed))",
     bool(re.search(NFC, NFD)),
     "RL2.1", "same picture, different code points, no match"),
    ("4", r"re.match(r'caf.', decomposed).group()",
     re.match(r"caf.", NFD).group(),
     "RL2.1", "the dot took the bare e and left the accent behind"),
    ("5", r"bool(re.fullmatch(r'[\w&&\d]', '&'))",
     amp,
     "RL1.3", "no set operators, so && is two more class members"),
    ("6", r"len(re.findall(r'.', 'a' + U+2028 + 'b'))",
     len(re.findall(r".", LS)),
     "RL1.6", "'.' means 'not U+000A', not 'not a line separator'"),
]
print(f"   {'#':<3}{'expression':<46}{'answer':<10}{'requirement'}")
for n, expr, answer, req, _why in rows:
    print(f"   {n:<3}{expr:<46}{str(answer)!s:<10}{req}")
print()
for n, _expr, _answer, _req, why in rows:
    print(f"   {n}. {why}")
print()
print("   Line 2 is the one with no RL number, and it is the one most likely")
print("   to be in your code: it is not a shortfall in the engine, it is the")
print("   OTHER engine. `re` on bytes is a deliberate ASCII matcher, because")
print("   a byte string carries no encoding for it to consult. The switch is")
print("   the argument's type, so it flips when a value moves from a decoded")
print("   string to a raw pipe, and no flag on the pattern will tell you.")
print()
print(f"   the same three characters through splitlines() {len(LS.splitlines())} lines")
print("   Line 6 next to that one is the whole of RL1.6: the same standard")
print("   library reads the same three characters as one line and as two.")
print()

print()
print("PART TWO -- WHICH OF THE SIX DOES NORMALIZATION FIX?")
print(BAR)
print()

def nfc(s):
    return ud.normalize("NFC", s)


fixed = [
    ("1", r"len(findall(r'\w+', hindi))",
     lambda t: len(re.findall(r"\w+", t)), HINDI),
    ("3", r"bool(search(composed, text))",
     lambda t: bool(re.search(NFC, t)), NFD),
    ("4", r"match(r'caf.', text).group()",
     lambda t: re.match(r"caf.", t).group(), NFD),
    ("6", r"len(findall(r'.', a + U+2028 + b))",
     lambda t: len(re.findall(r".", t)), LS),
]
print(f"   {'#':<3}{'expression':<38}{'as it stands':<15}"
      f"{'over NFC text':<15}{'moved?'}")
for n, expr, run, text in fixed:
    before, after = run(text), run(nfc(text))
    moved = "YES" if before != after else "no"
    print(f"   {n:<3}{expr:<38}{str(before):<15}{str(after):<15}{moved}")
print()
print("   Two of the four move and two do not, and the split is the lesson.")
print()
print("   3 and 4 are fixed outright, because RL2.1 is the requirement that")
print("   normalization IS the implementation of. The report says so: put the")
print("   text in a known form, write the pattern for that form, match code")
print("   point by code point. A system that does this conforms, provided it")
print("   documents that it does.")
print()
print("   1 and 6 do not move an inch, and no normalization form will move")
print("   them. NFC composes a base and a mark where a single character for")
print("   the pair exists; Devanagari vowel signs have no precomposed forms,")
print("   so the marks are still there and \\w still refuses them. U+2028 is")
print("   not a decomposition of anything. Normalization is a fix for one")
print("   named requirement, not a general repair for Unicode text.")
print()
print("   5 is not in the table because there is nothing to normalize: the")
print("   pattern is wrong about the ENGINE, not about the string. It is the")
print("   only one of the six that silently widens rather than narrows, and")
print("   the only one that would still be wrong on an empty file.")

assert ud.normalize("NFD", NFC) == NFD
