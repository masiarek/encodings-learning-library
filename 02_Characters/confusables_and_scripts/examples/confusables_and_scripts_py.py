#!/usr/bin/env python3
"""Characters that are drawn the same and are not the same.

Everything else in this chapter is about a character having a number. This is
about several characters having one PICTURE -- which is not a Unicode defect
but an unavoidable consequence of encoding every writing system at once, since
Latin, Greek and Cyrillic genuinely share letter shapes by descent.

Every value printed below is a code point or a character NAME, and Unicode
guarantees both of those never change. That is why this page may print them.

Run:  python3 confusables_and_scripts_py.py
"""

import unicodedata

BAR = "-" * 72
FORMS = ("NFC", "NFD", "NFKC", "NFKD")

# Nine pairs that render alike in most fonts. The left one is what you meant.
PAIRS = [
    ("a", "а"), ("o", "ο"), ("p", "р"),
    ("c", "с"), ("e", "е"), ("i", "і"),
    ("l", "ⅼ"), ("/", "∕"), ("-", "‐"),
]


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def script_of(ch):
    """The poor man's script property: the first word of the character's NAME.

    unicodedata has no script(), and a Name never changes -- so this is both
    the only stdlib answer and a recordable one.
    """
    try:
        return unicodedata.name(ch).split()[0]
    except ValueError:
        return "UNNAMED"


def scripts_in(s):
    """Scripts present, ignoring the characters every script shares."""
    shared = {"DIGIT", "FULL", "HYPHEN-MINUS", "SPACE", "LOW", "COMMERCIAL"}
    return sorted({script_of(c) for c in s} - shared)


# ------------------------------------------------------------------ 1
head(1, "ONE PICTURE, TWO CHARACTERS")
lat, cyr = "a", "а"
print(f"   {lat}   U+{ord(lat):04X}   {unicodedata.name(lat)}")
print(f"   {cyr}   U+{ord(cyr):04X}   {unicodedata.name(cyr)}")
print()
print(f"   they are equal                {lat == cyr}")
print(f"   their UTF-8 bytes             {lat.encode().hex(' ')}  vs  {cyr.encode().hex(' ')}")
print(f"   their lengths in bytes        {len(lat.encode())}  vs  {len(cyr.encode())}")
print()
print("   Nothing is broken here. Cyrillic and Latin both took the letter")
print("   from Greek, so the shapes are related by descent -- and a table")
print("   that encodes every writing system has to hold both.")

# ------------------------------------------------------------------ 2
head(2, "NORMALIZATION IS NOT THE FIX -- BUT READ THE EXCEPTION")
print(f"   {'look-alike':<15}{'name':<47}merges under")
for want, got in PAIRS:
    merges = [f for f in FORMS if unicodedata.normalize(f, got) == want]
    print(f"   U+{ord(got):04X} -> {want!r:<4} {unicodedata.name(got):<47}{', '.join(merges) or 'nothing'}")
print()
print("   Eight of the nine survive every normalization form there is, and")
print("   they are RIGHT to. Normalization reconciles two spellings of the")
print("   SAME character; Cyrillic er and Latin p are two different letters")
print("   that a font happens to draw alike, and merging them would corrupt")
print("   every Russian word ever written.")
print()
print("   The ninth is the instructive one. U+217C is a Roman numeral, and")
print("   Unicode itself declared it COMPATIBILITY-equivalent to the letter,")
print("   so NFKC folds it. That is the whole rule: normalization catches a")
print("   look-alike only where the standard already said the two are the")
print("   same character wearing different clothes. Visual similarity is a")
print("   fact about fonts, and no normalization form has ever claimed it.")

# ------------------------------------------------------------------ 3
head(3, "ONE LETTER, AND IT IS SOMEBODY ELSE'S DOMAIN")
for host in ("apple.com", "аpple.com"):
    print(f"   {host!r:<14} {' '.join('U+%04X' % ord(c) for c in host[:3])} ...")
    print(f"   {'':<14} .encode('idna') -> {host.encode('idna')!r}")
print()
print("   The second one is not a spelling of the first; it is a different")
print("   name, and punycode preserves the difference perfectly -- which is")
print("   exactly what an encoding should do. The `xn--` form is why your")
print("   browser shows it: having decided it cannot tell you the names are")
print("   different, it stops showing you the pretty one.")

# ------------------------------------------------------------------ 4
head(4, "THE STANDARD LIBRARY HAS NO script()")
print(f"   hasattr(unicodedata, 'script')   {hasattr(unicodedata, 'script')}")
print()
print("   Six properties are exposed and script is not among them. Ask the")
print("   ones that are, about the two letters from section 1:")
print()
print(f"   {'property':<20} {'latin a':<16} cyrillic a")
for prop in ("category", "bidirectional", "combining", "east_asian_width"):
    fn = getattr(unicodedata, prop)
    print(f"   {prop:<20} {str(fn(lat)):<16} {fn(cyr)}")
print(f"   {'decomposition':<20} {unicodedata.decomposition(lat) or '(none)':<16} {unicodedata.decomposition(cyr) or '(none)'}")
print()
print("   Four of the five cannot tell them apart, and the fifth is a red")
print("   herring worth spending three lines on, because it looks like a")
print("   hit:")
print()
for ch in ("a", "\u00e9", "\u017c", "\u0430"):
    print(f"      U+{ord(ch):04X}  east_asian_width {unicodedata.east_asian_width(ch):<3} {unicodedata.name(ch)}")
print()
print("   It splits LATIN against itself -- three Latin letters, three")
print("   different values -- because it answers `how many columns in a")
print("   CJK terminal`, not `which alphabet`. A property that separates")
print("   two characters is not thereby a script property.")
print()
print("   The only stdlib function that does separate them is name(),")
print("   whose FIRST WORD is a script by convention -- and because a Name")
print("   is a Unicode stability guarantee, that convention is safe to")
print("   build on and safe to record:")
print()
for ch in (lat, cyr, "ο", "0", "."):
    print(f"      U+{ord(ch):04X}  {script_of(ch):<10} from {unicodedata.name(ch)}")

# ------------------------------------------------------------------ 5
head(5, "A MIXED-SCRIPT DETECTOR, AND WHAT IT CATCHES")
for host in ("apple.com", "аpple.com", "paypal.com", "рaypal.com"):
    found = scripts_in(host)
    verdict = "MIXED -- refuse" if len(found) > 1 else "single script"
    print(f"   {host!r:<16} {str(found):<26} {verdict}")
print()
print("   Six lines of stdlib, and it catches the whole classic attack: a")
print("   name that is mostly Latin with one letter borrowed from another")
print("   alphabet cannot help but be mixed-script.")

# ------------------------------------------------------------------ 6
head(6, "AND THE ONE IT WAVES STRAIGHT THROUGH")
whole = "аррӏе"
print(f"   {whole!r}")
print(f"   rendered            {whole}.com")
print(f"   code points         {' '.join('U+%04X' % ord(c) for c in whole)}")
print(f"   scripts present     {scripts_in(whole)}")
print(f"   mixed?              {len(scripts_in(whole)) > 1}")
print(f"   punycode            {(whole + '.com').encode('idna')!r}")
print()
print("   Every letter is Cyrillic, so the string is perfectly consistent")
print("   and the detector above is satisfied. This is a WHOLE-SCRIPT")
print("   confusable, and no amount of internal consistency will find it --")
print("   the only thing wrong with the name is that it is not the one the")
print("   reader thinks they are reading.")
print()
print("   That is where the stdlib runs out and UTS #39 begins: a published")
print("   table of confusable sequences, plus restriction levels that ask")
print("   which scripts a USER expects rather than which the string uses.")
print("   And the last of those questions is not answerable inside a")
print("   library at all -- it is a policy a registry or a browser holds.")
