#!/usr/bin/env python3
"""The typical words: what other people's encoding examples are made of.

Tutorials, test suites and bug reports keep reaching for the same few dozen
words, and each one is there for a single property. This program measures
the property, so the page can say what a word is FOR rather than only that
it is famous.

Everything printed is arithmetic over UTF-8 and UTF-16, a normalization
(which Unicode's stability policy freezes for every character already
assigned), a character name (frozen likewise), or a codec table Python has
shipped unchanged for years -- which is why it may be an answer key. The one
count several of these words are best known for, grapheme clusters, is
deliberately NOT printed: the rules that produce it have a version, and the
page puts that measurement in a dated fence instead.

Run:  python3 typical_words_py.py
"""

import encodings.aliases
import unicodedata as ud

BAR = "-" * 72

APOSTROPHE = chr(0x2019)  # RIGHT SINGLE QUOTATION MARK, the curly one
FACEPALM = "".join(map(chr, (0x1F926, 0x1F3FC, 0x200D, 0x2642, 0xFE0F)))
FAMILY = "".join(map(chr, (0x1F468, 0x200D, 0x1F469, 0x200D, 0x1F467)))

# The words, grouped as the page groups them. A star marks a member of this
# library's own cast (CAST.md); everything else is here because somebody
# else's example uses it.
GROUPS = [
    ("accented Latin", [
        ("café", "*"), ("naïve", ""), ("résumé", ""), ("Iñtërnâtiônàlizætiøn", ""),
    ]),
    ("Central Europe", [
        ("żółw", "*"), ("Łódź", "*"), ("zażółć gęślą jaźń", "*"),
        ("Árvíztűrő tükörfúrógép", ""), ("Příliš žluťoučký kůň úpěl ďábelské ódy", ""),
    ]),
    ("case and normalization", [
        ("Straße", ""), ("İstanbul", ""), ("ΟΔΥΣΣΕΥΣ", ""), ("Ångström", ""),
        ("Nguyễn", ""), ("한국어", ""),
    ]),
    ("other scripts", [
        ("Привет", ""), ("Ελληνικά", ""), ("日本語", "*"), ("文字化け", ""), ("नमस्ते", ""),
    ]),
    ("above U+FFFF", [
        ("😀", "*"), ("💩", ""), ("𝄞", ""), (FACEPALM, ""), (FAMILY, "*"),
    ]),
]

# Ten legacy tables: the Western pair, the Central European pair, Turkish,
# Greek, the two Cyrillic rivals, and one double-byte table each for Japanese
# and Korean.
TABLES = [
    ("8859-1", "latin_1"), ("1252", "cp1252"), ("8859-2", "iso8859_2"), ("1250", "cp1250"),
    ("1254", "cp1254"), ("1253", "cp1253"), ("KOI8-R", "koi8_r"), ("1251", "cp1251"),
    ("SJIS", "shift_jis"), ("EUC-KR", "euc_kr"),
]

# The letters each language adds to ASCII -- for Russian, its whole alphabet.
ALPHABETS = {
    "Polish": "ąćęłńóśźż",
    "Czech": "áčďéěíňóřšťúůýž",
    "Hungarian": "áéíóöőúüű",
    "German": "äöüß",
    "Turkish": "çğıöşü",
    "Russian": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
}

# The pangrams: the first is this library's own; the rest are lines of
# Markus Kuhn's quickbrown.txt, apart from the Czech one, which that file lacks.
SENTENCES = [
    ("Polish", "zażółć gęślą jaźń"),
    ("Polish", "Pchnąć w tę łódź jeża lub ośm skrzyń fig"),
    ("Czech", "Příliš žluťoučký kůň úpěl ďábelské ódy"),
    ("Hungarian", "Árvíztűrő tükörfúrógép"),
    ("German", "Zwölf Boxkämpfer jagten Eva quer über den Sylter Deich"),
    ("Turkish", "Pijamalı hasta, yağız şoföre çabucak güvendi."),
    ("Russian", "Съешь же ещё этих мягких французских булок да выпей чаю"),
]


def head(n, title):
    print(f"{n}. {title}")
    print(BAR)


def fits(word, codec):
    """Can this table hold every character of the word?

    LookupError covers the names in Python's alias table that are not text
    encodings at all (base64, rot13) or not available on this platform (mbcs).
    """
    try:
        word.encode(codec)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def misread(word, write, read):
    """Write with one table and read with another: the whole of mojibake."""
    return word.encode(write).decode(read, errors="replace")


def utf16_units(s):
    return len(s.encode("utf-16-le")) // 2


def strip_marks(s):
    """The folk recipe for 'remove the accents': decompose, drop the marks."""
    return "".join(c for c in ud.normalize("NFD", s) if not ud.combining(c))


def cps(s):
    return " ".join(f"{ord(c):04X}" for c in s)


def main():
    head(1, "THE WORDS, AND FOUR RULERS THAT NEED NO TABLE")
    print(f"   {'chars':>5} {'NFD':>4} {'UTF-8':>6} {'UTF-16':>7}      word")
    for title, rows in GROUPS:
        print(f"   -- {title}")
        for word, star in rows:
            print(f"   {len(word):>5} {len(ud.normalize('NFD', word)):>4} "
                  f"{len(word.encode()):>6} {utf16_units(word):>7}  {star:1}   {word}")
    print()
    print("   'chars' counts code points as typed; 'NFD' counts them again with")
    print("   every accent taken off as a mark of its own; 'UTF-8' is bytes;")
    print("   'UTF-16' is the units Java, JavaScript and ABAP call characters.")
    print("   A star marks a member of this library's own cast, in CAST.md.")
    print()

    head(2, "WHICH LEGACY TABLE CAN HOLD EACH WORD")
    print("   " + " ".join(f"{label:>6}" for label, _ in TABLES) + "   word")
    homeless = []
    for _, rows in GROUPS:
        for word, _ in rows:
            marks = [fits(word, codec) for _, codec in TABLES]
            if not any(marks):
                homeless.append(word)
            print("   " + " ".join(f"{'yes' if m else '.':>6}" for m in marks) + f"   {word}")
    print()
    print(f"   {len(homeless)} of the words fit none of the ten:")
    print("      " + "  ".join(homeless))
    print()
    catalogue = sorted(set(encodings.aliases.aliases.values()))
    writers = [name for name in catalogue if fits("नमस्ते", name)]
    print("   Nor does a table built for Devanagari turn up anywhere else. Of every")
    print("   codec named in Python's alias table, these can write 'नमस्ते' at all:")
    print("      " + "  ".join(writers))
    print("   The UTFs, and GB18030 -- the Chinese national standard, which maps")
    print("   the whole of Unicode rather than one script.")
    print()
    print("   Vietnamese has a Windows table of its own, 1258, and it does not")
    print("   fill the gap so much as move it -- 'Nguyễn' fits in neither")
    print("   normal form:")
    nfc = "Nguyễn"
    nfd = ud.normalize("NFD", nfc)
    half = "Nguy" + chr(0xEA) + chr(0x303) + "n"
    for label, form in (("NFC", nfc), ("NFD", nfd), ("neither", half)):
        try:
            out = form.encode("cp1258").hex(" ").upper()
        except UnicodeEncodeError as e:
            out = f"refuses U+{ord(form[e.start]):04X}"
        print(f"      {label:<8} {cps(form):<40} {out}")
    print("   1258 carries the five Vietnamese tone marks as combining characters")
    print("   and the vowel shapes as precomposed letters, so it wants the")
    print("   e-circumflex composed and the tilde written after it -- a spelling")
    print("   that no normalization form produces.")
    print()

    head(3, "THE MOJIBAKE EACH ONE IS FAMOUS FOR")
    misreads = [
        ("café", "utf-8", "cp1252"),
        ("café", "latin-1", "utf-8"),
        ("don" + APOSTROPHE + "t", "utf-8", "cp1252"),
        ("żółw", "utf-8", "cp1250"),
        ("Łódź", "cp1250", "iso8859_2"),
        ("Łódź", "iso8859_2", "cp1250"),
        ("Árvíztűrő", "iso8859_2", "latin-1"),
        ("Привет", "koi8_r", "cp1251"),
        ("Привет", "cp1251", "koi8_r"),
        ("文字化け", "utf-8", "shift_jis"),
    ]
    print(f"   {'written as':<11} {'read as':<11} the word, and what the reader gets")
    for word, write, read in misreads:
        print(f"   {write:<11} {read:<11} {word!r:<14} -> {misread(word, write, read)!r}")
    twice = misread(misread("café", "utf-8", "cp1252"), "utf-8", "cp1252")
    print(f"   {'utf-8':<11} {'cp1252':<11} {'café'!r:<14} -> {twice!r}   (misread twice)")
    print()
    koi = "Привет".encode("koi8_r")
    seven = bytes(b & 0x7F for b in koi)
    print(f"   'Привет' in KOI8-R           {koi.hex(' ').upper()}")
    print(f"   every top bit cleared        {seven.hex(' ').upper()}   {seven.decode('ascii')!r}")
    print("   Clear the eighth bit of every byte and KOI8-R text is still")
    print("   readable: Latin letters, with the case turned over.")
    print()

    head(4, "ABOVE U+FFFF: ONE CHARACTER, TWO UTF-16 UNITS")
    for c in ("😀", "💩", "𝄞"):
        units = c.encode("utf-16-be")
        print(f"   U+{ord(c):05X}   UTF-8 {c.encode().hex(' ').upper():<12}  UTF-16 "
              f"{units[:2].hex().upper()} {units[2:].hex().upper()}   {ud.name(c)}")
    print()
    for label, seq in (("the facepalm", FACEPALM), ("the family", FAMILY)):
        print(f"   {label}: {len(seq)} code points, {len(seq.encode())} UTF-8 bytes, "
              f"{utf16_units(seq)} UTF-16 units, one emoji to a reader")
        for c in seq:
            print(f"      {'U+%04X' % ord(c):<8} {ud.name(c)}")
    print()

    head(5, "WHOLE SENTENCES: DOES THE PANGRAM COVER THE ALPHABET?")
    print("   of the letters the language adds to ASCII (for Russian, of all 33)")
    for lang, s in SENTENCES:
        want = set(ALPHABETS[lang])
        have = set(s.lower()) & want
        missing = " ".join(sorted(want - have)) or "none"
        print(f"   {lang:<10} {len(have):>2} of {len(want):<2}  missing {missing:<6} {s}")
    print()

    head(6, "STRIP THE MARKS: THE FOLK WAY TO ASCII")
    for word in ("café", "naïve", "Nguyễn", "Příliš žluťoučký kůň úpěl ďábelské ódy",
                 "Árvíztűrő tükörfúrógép", "Straße", "żółw", "Łódź", "Iñtërnâtiônàlizætiøn"):
        out = strip_marks(word)
        left = " ".join(dict.fromkeys(c for c in out if ord(c) > 127))
        verdict = "ASCII" if out.isascii() else f"keeps {left}"
        print(f"   {verdict:<12} {out}")
    print()
    print("   Decompose, drop the combining marks, keep the rest. It works on")
    print("   every letter whose accent Unicode writes as a separate mark, and")
    print("   on nothing else: ß, ł, æ and ø have no decomposition at all, so")
    print("   they come through untouched -- and so does every search, sort or")
    print("   username check built on this recipe.")


if __name__ == "__main__":
    main()
