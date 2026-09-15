#!/usr/bin/env python3
"""Only one of these is a dot.

A parser compares numbers, not pictures. U+002E FULL STOP is the character
every syntax means by '.', and each character below is drawn like it and is a
different number with different bytes. Then three readers in the standard
library are asked the same question -- is this a dot? -- and they give three
different answers, because each of them is really asking something else.

What may be recorded, and why: a character NAME never changes; UTF-8 is
arithmetic; a decomposition mapping is frozen by Unicode's normalization
stability policy, so NFC and NFKC of an assigned character cannot move; and
the idna codec normalizes with unicodedata.ucd_3_2_0, a table frozen in 2002.

Run:  python3 the_full_stop_and_its_lookalikes_py.py
"""

import ipaddress
import unicodedata

BAR = "-" * 72

# U+002E first, then nine characters a font draws like it. Written as numbers
# on purpose: a look-alike pasted into source code is this page's own bug.
CODE_POINTS = [
    0x002E,  # FULL STOP -- the keyboard's, and every syntax's
    0x2024,  # ONE DOT LEADER
    0x2026,  # HORIZONTAL ELLIPSIS -- what autocorrect makes of three dots
    0xFF0E,  # FULLWIDTH FULL STOP -- CJK input methods
    0x3002,  # IDEOGRAPHIC FULL STOP -- Chinese and Japanese prose
    0xFF61,  # HALFWIDTH IDEOGRAPHIC FULL STOP
    0x00B7,  # MIDDLE DOT -- Catalan writes l, middle dot, l
    0x0387,  # GREEK ANO TELEIA -- the Greek semicolon
    0x22C5,  # DOT OPERATOR -- the dot product
    0x2022,  # BULLET -- a list pasted out of a document
]
CHARS = [chr(n) for n in CODE_POINTS]
LOOKALIKES = CHARS[1:]


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def ucp(s):
    """'U+2024' for one character, 'U+002E x3' for a run of one, else a list."""
    if len(s) > 1 and len(set(s)) == 1:
        return f"U+{ord(s[0]):04X} x{len(s)}"
    return " ".join(f"U+{ord(c):04X}" for c in s)


def changed(before, after):
    return "same" if after == before else ucp(after)


def pieces(n):
    return f"{n} piece" if n == 1 else f"{n} pieces"


def names(chars):
    return "  ".join(ucp(c) for c in chars) or "(none)"


# ------------------------------------------------------------------ 1
head(1, "ONE DOT, AND NINE CHARACTERS DRAWN LIKE IT")
print(f"   {'code point':<11} {'name':<32} {'UTF-8':<9} in a word")
for c in CHARS:
    print(f"   U+{ord(c):04X}      {unicodedata.name(c):<32} "
          f"{c.encode().hex(' '):<9} a{c}b")

holding = [c for c in LOOKALIKES if 0x2E in c.encode()]
print(f"\n   look-alikes whose UTF-8 holds the byte 2e    "
      f"{len(holding)} of {len(LOOKALIKES)}")
print("""
   Every one of them is two or three bytes, and none of those bytes is
   2e. A multi-byte UTF-8 sequence is built only from bytes 80 and up, so
   a program scanning for the dot's byte cannot find a look-alike, and
   cannot cut one in half either. The Rust example checks that claim
   against every scalar value there is.""")

# ------------------------------------------------------------------ 2
head(2, "WHAT UNICODE DECLARED ABOUT EACH ONE")
print(f"   {'code point':<11} {'decomposition':<24} {'NFC':<8} NFKC")
for c in CHARS:
    decomp = unicodedata.decomposition(c) or "(none)"
    print(f"   U+{ord(c):04X}      {decomp:<24} "
          f"{changed(c, unicodedata.normalize('NFC', c)):<8} "
          f"{changed(c, unicodedata.normalize('NFKC', c))}")

to_dot = [c for c in LOOKALIKES
          if set(unicodedata.normalize("NFKC", c)) == {"."}]
nfc_moved = [c for c in CHARS if unicodedata.normalize("NFC", c) != c]
print(f"""
   NFKC turns into full stops     {names(to_dot)}
   NFC changes at all             {names(nfc_moved)}

   A decomposition in angle brackets is a COMPATIBILITY mapping: Unicode
   saying this is the other character in different clothes, a leader dot
   or a wide one, and NFKC applies it. The ideographic full stop has no
   mapping at all. It ends sentences too, but it is a different
   punctuation mark, so NFKC leaves it -- and folds its halfwidth form onto
   IT, not onto '.'. A bare mapping with no brackets is CANONICAL, and
   even NFC, the form usually called safe, applies it: GREEK ANO TELEIA
   becomes MIDDLE DOT, which is still not a dot.""")

# ------------------------------------------------------------------ 3
head(3, "THREE READERS, THREE ANSWERS")
print(f"   {'code point':<11} {'split on dot':<16} {'NFKC is dots':<13} "
      f".encode('idna')")
split_dot, idna_dot = [], []
for c in CHARS:
    word = "a" + c + "b"
    n = len(word.split("."))
    folded = set(unicodedata.normalize("NFKC", c)) == {"."}
    idna = word.encode("idna")
    if n > 1:
        split_dot.append(c)
    if b"." in idna:
        idna_dot.append(c)
    print(f"   U+{ord(c):04X}      {pieces(n):<16} {str(folded):<13} {idna!r}")

print(f"""
   str.split('.') finds a dot in        {names(split_dot)}
   NFKC makes a dot of                  {names(['.'] + to_dot)}
   .encode('idna') writes a 2e for      {names(idna_dot)}

   Three readers, three questions. split() compares code points, and
   exactly one code point is 2E. NFKC asks what Unicode declared, which
   is section 2. The idna codec holds a LIST: RFC 3490 section 3.1 names
   four characters that must be recognised as the dots between labels,
   U+002E U+3002 U+FF0E U+FF61, and every other row that comes out with
   a 2e got it from the NFKC that nameprep runs inside each label.""")

# ------------------------------------------------------------------ 4
head(4, "THE ORDER OF THE READERS DECIDES")
ip = "127" + "\N{IDEOGRAPHIC FULL STOP}" + "0.0.1"
as_idna = ip.encode("idna")


def refuses(func, arg):
    try:
        return repr(func(arg))
    except (ValueError, UnicodeError) as exc:
        return type(exc).__name__


print(f"   s = '127' + IDEOGRAPHIC FULL STOP + '0.0.1'")
print(f"   s.split('.')                          {ip.split('.')}")
print(f"   ipaddress.ip_address(s)               "
      f"{refuses(ipaddress.ip_address, ip)}")
print(f"   s.encode('idna')                      {as_idna!r}")
print(f"   ipaddress.ip_address(that, decoded)   "
      f"{ipaddress.ip_address(as_idna.decode('ascii'))}")

three = "a...b"
ellipsis = "a" + "\N{HORIZONTAL ELLIPSIS}" + "b"
print(f"\n   {'a...b'!r}.encode('idna')                "
      f"{refuses(lambda s: s.encode('idna'), three)}")
print(f"   ('a' + ELLIPSIS + 'b').encode('idna') "
      f"{refuses(lambda s: s.encode('idna'), ellipsis)}")
print("""
   The same string is not an IP address before the idna codec and is one
   after it. And the codec itself decides what a dot is twice: it splits
   the name into labels on its four dots FIRST, and runs NFKC inside each
   label AFTER. So three real full stops trip its empty-label check, and
   an ellipsis walks past that check and comes out as the same three
   bytes. Whatever validates a name has to run after the last step that
   can turn something into a dot.""")

# ------------------------------------------------------------------ 5
head(5, "A DOT THAT BELONGS TO A LETTER")
cap = "\N{LATIN CAPITAL LETTER I WITH DOT ABOVE}"
low = cap.lower()
print(f"   '{cap}'   U+{ord(cap):04X}   {unicodedata.name(cap)}")
rows = [
    (f"'{cap}'.lower()", f"{low!r}  {len(low)} code points: {ucp(low)}"),
    ("the second one", unicodedata.name(low[1])),
    ("its UTF-8", low.encode().hex(" ")),
    (".split('.')", pieces(len(low.split(".")))),
    ("NFKC", changed(low, unicodedata.normalize("NFKC", low))),
    (f"'{cap}'.lower() == 'i'", str(low == "i")),
]
for label, value in rows:
    print(f"   {label:<24}  {value}")
print("""
   Lowercasing the Turkish capital without Turkish rules keeps its dot as
   a combining mark on an ordinary i. Nothing on this page reads that
   mark as punctuation, and nothing removes it either.""")
