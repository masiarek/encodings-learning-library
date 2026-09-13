#!/usr/bin/env python3
"""Eight text jobs, and how far the standard library gets on each one.

This is the BASELINE for the lesson page. Everything below imports nothing
outside the standard library, so it runs on the Python 3.14 CI has and its
output is an answer key. The libraries the page is about are measured on the
page, in dated fences, because CI installs no package and never will.

Nothing here reads a Unicode property that a newer table could change: no
east_asian_width, no name() of a recently added character, no category(). The
two lookups it does make -- a canonical decomposition and a combining class --
are frozen by Unicode's stability policy for every character already assigned,
and name('e-acute') has been the same string since 1991.

Run:  python3 where_the_stdlib_stops_py.py
"""

import locale
import re
import unicodedata as ud

ZWJ = "\N{ZERO WIDTH JOINER}"
E_ACUTE = "e\N{COMBINING ACUTE ACCENT}"
FAMILY = "👨" + ZWJ + "👩" + ZWJ + "👧" + ZWJ + "👦"   # four people, three joiners


def decodes(b, codec):
    try:
        b.decode(codec)
        return True
    except UnicodeDecodeError:
        return False


def recipe(s, wrong, right="utf-8"):
    """The mojibake repair: re-encode under the table that misread the bytes."""
    try:
        return repr(s.encode(wrong).decode(right))
    except UnicodeError as e:
        return f"<{type(e).__name__}>"


def strip_marks(s):
    return "".join(c for c in ud.normalize("NFKD", s) if not ud.combining(c))


print("1. DETECTION -- the standard library can VALIDATE, and that is all it can do")
samples = [
    ("utf8.txt", "café 1€\n".encode("utf-8")),
    ("latin1.txt", "café\n".encode("latin-1")),
    ("cp1252.txt", "Preis… 100€\n".encode("cp1252")),
    ("latin2.txt", "Zażółć gęślą jaźń\n".encode("iso-8859-2")),
    ("cp1250.txt", "Zażółć gęślą jaźń\n".encode("cp1250")),
]
tables = ["utf-8", "cp1252", "iso-8859-2", "cp1250", "latin-1"]
print(f"   {'file':11} decodes without error under")
for name, b in samples:
    ok = [t for t in tables if decodes(b, t)]
    print(f"   {name:11} {', '.join(ok)}")
print("   Every 8-bit table accepts every byte it defines, so 'decodes' rules out")
print("   UTF-8 and nothing else. Which table is RIGHT is not a question the bytes")
print("   can answer; a detector guesses from letter statistics, and the page")
print("   measures two of them. For Polish the guess rests on six letters:")
differ = [c for c in "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ" if c.encode("iso-8859-2") != c.encode("cp1250")]
print(f"   {'letter':8} iso-8859-2  cp1250")
for c in differ:
    print(f"   {c:8} {c.encode('iso-8859-2').hex():11} {c.encode('cp1250').hex()}")
print(f"   {len(differ)} of the 18 Polish letters differ between the two tables. A text")
print("   that happens to use none of them is the same bytes in both, and no")
print("   detector can tell the tables apart, because there is nothing to tell.")
print()

print("2. REPAIR -- the recipe is one line, and it has two ways to fail")
cases = ["cafÃ©", "Ã\x81lvaro", "cafÃƒÂ©", "Za¿ó³æ gêœl¹ jaŸñ"]
print(f"   {'damaged':22} {'encode(cp1252).decode(utf-8)':30} encode(latin-1).decode(utf-8)")
for s in cases:
    print(f"   {s!r:22} {recipe(s, 'cp1252'):30} {recipe(s, 'latin-1')}")
print("   Row 2: 0x81 is one of cp1252's five unassigned bytes, so the cp1252 recipe")
print("   cannot even re-encode it; Latin-1 has all 256 and can.")
print("   Row 3: mojibake applied twice needs the recipe twice:")
twice = "cafÃƒÂ©".encode("cp1252").decode("utf-8").encode("cp1252").decode("utf-8")
print(f"      once {recipe('cafÃƒÂ©', 'cp1252')}   twice {twice!r}")
print("   Row 4 is not UTF-8 mojibake at all: it is cp1250 bytes read as cp1252, so")
print("   the second half of the recipe names the other table:")
print(f"      encode(cp1252).decode(cp1250) -> {recipe('Za¿ó³æ gêœl¹ jaŸñ', 'cp1252', 'cp1250')}")
print("   Knowing WHICH recipe is the whole job. ftfy automates the first kind only.")
print()

print("3. TRANSLITERATION -- NFKD then drop the marks, and the letters it leaves standing")
for w in ["Zażółć gęślą jaźń", "Straße", "Łódź", "Москва", "北京", "Ærøskøbing", "ﬁ", "½", "Þór"]:
    out = strip_marks(w)
    left = "".join(c for c in out if not c.isascii())
    print(f"   {w:18} -> {out:18} still not ASCII: {left or '-'}")
print("   ł has no decomposition (there is no COMBINING STROKE), and neither do ß, æ,")
print("   ø, þ, any Cyrillic letter or any Han character. ½ decomposes to 1 FRACTION")
print("   SLASH 2, which is not ASCII either. The recipe is a normalization, and")
print("   normalization was never about ASCII. A transliterator is a table of")
print("   opinions -- Straße -> Strasse, 北京 -> Bei Jing -- and the standard library")
print("   ships none.")
print()

print("4. WHAT A PERSON CALLS ONE CHARACTER -- nothing in the standard library counts it")
for label, s in [("e + acute", E_ACUTE), ("flag PL", "🇵🇱"), ("family", FAMILY), ("Devanagari kshi", "क्षि"), ("thumbs up + tone", "👍🏽")]:
    print(f"   {label:18} len = {len(s)}   re.findall('.') = {len(re.findall('.', s))}   a person sees 1")
try:
    re.compile(r"\X")
    print("   re.compile(r'\\X') compiled")
except re.error:
    print("   re.compile(r'\\X') -> raises: the grapheme escape does not exist in re")
print("   len() counts code points and so does '.'. UAX #29's boundary rules are in")
print("   the third-party regex module, uniseg and grapheme -- measured on the page --")
print("   and in nothing that ships with the interpreter.")
print()

print("5. COLUMNS -- f'{s:<8}' pads, and pads by the wrong ruler")
for s in ["café", "日本語", FAMILY, "🇵🇱"]:
    print(f"   |{s:<8}|  len = {len(s)}")
print("   The bars are meant to line up. Python padded each string to 8 CODE POINTS;")
print("   a terminal draws 日本語 six columns wide and the family two, and the standard")
print("   library has no function that returns either number. unicodedata has the raw")
print("   East_Asian_Width property; turning it into columns is a rule set the library")
print("   leaves to you, and the property is a table lookup, so its values stay out of")
print("   this key.")
print()

print("6. SORTING -- sorted() is code point order, and the C locale has no other")
words = ["zebra", "Zebra", "łódź", "lód", "Łukasiewicz", "Zawadzki", "żaba", "ćma", "cmentarz"]
locale.setlocale(locale.LC_COLLATE, "C")
print("   sorted()              ", " ".join(sorted(words)))
print("   key=str.casefold      ", " ".join(sorted(words, key=str.casefold)))
print("   key=locale.strxfrm, C ", " ".join(sorted(words, key=locale.strxfrm)))
print("   Three orders and none of them Polish: ł, ć, ż all land after z. strxfrm is")
print("   the standard library's only collation, it says whatever the machine's locale")
print("   files say, and under LC_ALL=C -- every container, every CI runner, this")
print("   program -- it says byte order. The page shows what a pure-Python UCA and")
print("   ICU make of the same words.")
print()

print("7. REGEX -- re knows Unicode, and has no property syntax")
tests = [(r"\w+", "Zażółć_gęślą"), (r"(?i)straße", "STRASSE"), (r"(?i)straße", "STRAẞE"), (r"\d+", "٣٤"), (r"\p{L}+", "żółw"), (r"\X", FAMILY)]
for pat, s in tests:
    try:
        res = "match" if re.fullmatch(pat, s) else "no match"
    except re.error:
        res = "raises -- no such escape"
    shown = "FAMILY" if s is FAMILY else repr(s)
    print(f"   re.fullmatch({pat!r:13}, {shown:16}) -> {res}")
print("   \\w and \\d are Unicode-aware; (?i) folds one character to one, so ß never")
print("   meets SS; and \\p{...} and \\X do not exist. That is the whole of the gap the")
print("   regex module fills, and the page measures it.")
print()

print("8. THE TABLE -- one Unicode version per interpreter, and nothing to update it")
print(f"   unicodedata.unidata_version has {len(ud.unidata_version.split('.'))} parts and is a property of THIS python3")
print(f"   name('é')      -> {ud.name('é')}")
print(f"   name(U+FFFE)   -> {'raises' if ud.name(chr(0xFFFE), None) is None else 'has a name'}   (a noncharacter: never assigned, by policy)")
print("   A character assigned AFTER this interpreter's table has no name here and")
print("   category Cn, however real it is. How many such characters one version step")
print("   adds is on the page, dated -- it is the one number this program must not")
print("   print, because next year's interpreter would print a different one.")
