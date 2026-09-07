#!/usr/bin/env python3
"""Python's answers to the four questions, asked of Python's own registry.

"Does this language handle Unicode" is four independent questions -- can it
CONVERT between encodings, what does it do at a byte it cannot explain, what
does it call one character, and can the type system stop you getting it wrong.
This program answers the first two for Python by measurement, and shows where
Python stops on the third.

Everything here is arithmetic or a question to `codecs`, the encoding registry
that ships with the interpreter. Nothing is read out of a Unicode table, so
nothing depends on which Unicode version this build was compiled against.

Run:  python3 what_your_language_gives_you_py.py
"""

import codecs
import unicodedata

# The encodings named by the WHATWG Encoding Standard -- the list every web
# browser implements. Taken once from https://encoding.spec.whatwg.org/
# encodings.json and pasted here, so this program needs no network.
WHATWG = (
    # The Encoding
    "UTF-8",
    # Legacy single-byte encodings
    "IBM866", "ISO-8859-2", "ISO-8859-3", "ISO-8859-4", "ISO-8859-5",
    "ISO-8859-6", "ISO-8859-7", "ISO-8859-8", "ISO-8859-8-I",
    "ISO-8859-10", "ISO-8859-13", "ISO-8859-14", "ISO-8859-15",
    "ISO-8859-16", "KOI8-R", "KOI8-U", "macintosh", "windows-874",
    "windows-1250", "windows-1251", "windows-1252", "windows-1253",
    "windows-1254", "windows-1255", "windows-1256", "windows-1257",
    "windows-1258", "x-mac-cyrillic",
    # Legacy multi-byte Chinese (simplified) encodings
    "GBK", "gb18030",
    # Legacy multi-byte Chinese (traditional) encodings
    "Big5",
    # Legacy multi-byte Japanese encodings
    "EUC-JP", "ISO-2022-JP", "Shift_JIS",
    # Legacy multi-byte Korean encodings
    "EUC-KR",
    # Legacy miscellaneous encodings
    "replacement", "UTF-16BE", "UTF-16LE", "x-user-defined",
)

HANDLERS = (
    "strict", "replace", "ignore", "backslashreplace",
    "xmlcharrefreplace", "namereplace", "surrogateescape", "surrogatepass",
)

RULE = "-" * 72


def say(title: str) -> None:
    print(f"\n{title}\n{RULE}")


def hexs(raw: bytes) -> str:
    return " ".join(f"{b:02x}" for b in raw)


say("1. QUESTION ONE: CAN IT CONVERT? AND CAN IT CONVERT BOTH WAYS?")

known = []
for name in WHATWG:
    try:
        codecs.lookup(name)
        known.append(name)
    except LookupError:
        pass

# A probe every one of these tables can represent, so a failure here is the
# codec refusing a direction, not the character being out of its range.
PROBE = "aA1"
read_only, write_only = [], []
for name in known:
    try:
        raw = PROBE.encode(name)
    except (UnicodeError, LookupError):
        read_only.append(name)      # a decoder with no encoder behind it
        continue
    try:
        if raw.decode(name) != PROBE:
            write_only.append(name)
    except (UnicodeError, LookupError):
        write_only.append(name)     # wrote bytes it cannot read back

print(f"   encodings the standard names                     {len(WHATWG)}")
print(f"   of the ones this registry resolves, how many it")
print(f"       will only READ, never write                  {len(read_only)}")
print(f"       will only WRITE, never read                  {len(write_only)}")
print("""
   Zero and zero, and that is the answer to question one. Python's
   codecs come in pairs; there is no table it will take in and not
   give back. A standard library that reads a table it cannot write
   is a real design and not an oversight -- see the page.

   How many of the forty it resolves at all is a different question,
   and not one an answer key may hold: it is a property of the alias
   table, which has a version. Spot checks, on names that resolve
   the same way on CPython 3.11 through 3.14:""")
for name in ("UTF-8", "windows-1250", "ISO-8859-2", "KOI8-R",
             "Shift_JIS", "Big5", "EUC-KR"):
    codec = codecs.lookup(name).name
    ok = PROBE.encode(name).decode(name) == PROBE
    print(f"       {name:14} -> Python calls it {codec:12} both ways: {ok}")

say("2. THE STAKE, IN ONE CHARACTER")

Z_DOT = "ż"  # a cast member: the Polish z-with-dot. See CAST.md.
print(f"   {Z_DOT}  U+017C  {unicodedata.name(Z_DOT)}\n")
for table in ("utf-8", "cp1250", "iso8859-2", "latin-1"):
    try:
        raw = Z_DOT.encode(table)
        print(f"   encode to {table:12} {hexs(raw):8}  and back: {raw.decode(table)!r}")
    except UnicodeEncodeError as exc:
        print(f"   encode to {table:12} {type(exc).__name__}  -- no byte here means it")
print("""
   One byte in windows-1250, one in ISO-8859-2, two in UTF-8, and no
   byte at all in Latin-1. A language that can only WRITE UTF-8 can
   still read all four -- and cannot send a file to a system that
   expects the first.""")

say("3. QUESTION TWO: WHAT HAPPENS AT A BYTE IT CANNOT EXPLAIN?")

# caf + 0xE9 + .txt -- a Latin-1 e-acute in a stream declared UTF-8.
BROKEN = b"caf\xe9.txt"
print(f"   the bytes {hexs(BROKEN)}, decoded as UTF-8 under each policy:\n")
for policy in ("replace", "ignore", "backslashreplace", "surrogateescape"):
    text = BROKEN.decode("utf-8", policy)
    print(f"   {policy:18} {text!r:22} round-trips: {text.encode('utf-8', policy) == BROKEN}")
print(f"   {'strict':18} {'UnicodeDecodeError':22} round-trips: n/a")
print("\n   registered under these names:")
for i in range(0, len(HANDLERS), 3):
    row = [n for n in HANDLERS[i:i + 3] if codecs.lookup_error(n)]
    print("      " + "  ".join(f"{n:18}" for n in row).rstrip())
print("""
   Only `surrogateescape` gives the byte back, and it is worth seeing
   how: 0xE9 becomes U+DCE9, a lone surrogate -- a code point that can
   never occur in real text, holding a byte until something encodes it
   again. PEP 383 is the reason a filename that is not valid UTF-8 can
   still be opened.""")

say("4. THE SAME TRICK, TWICE, INVENTED SEPARATELY")

BYTE = 0xE9
print(f"   a byte that is not valid UTF-8   0x{BYTE:02X}\n")
print(f"   {'Python, surrogateescape':26} {'0xDC00 + byte':22} "
      f"U+{0xDC00 + BYTE:04X}  lone surrogate")
print(f"   {'the web, x-user-defined':26} {'0xF780 + byte - 0x80':22} "
      f"U+{0xF780 + BYTE - 0x80:04X}  private use")
print("""
   Two standards, no shared authors, one idea: to carry a byte you
   cannot interpret through a string type, map it into a range of
   code points that means nothing else, and map it back on the way
   out. Python reserved lone surrogates for it; the browsers reserved
   a slice of the private use area. So `x-user-defined` is not really
   a character table at all: it is this escape hatch, wearing an
   encoding's name so that it can be asked for like one.""")

say("5. QUESTION THREE: WHAT DOES IT CALL ONE CHARACTER?")

CAFE_NFD = "caf" + "e\u0301"  # e + U+0301 COMBINING ACUTE ACCENT, spelled out
points = " ".join(f"U+{ord(ch):04X}" for ch in CAFE_NFD)
print(f"   the string renders as {CAFE_NFD}, and is {points}\n")
print(f"   UTF-8 bytes                              {len(CAFE_NFD.encode('utf-8'))}")
print(f"   len(), which counts code points          {len(CAFE_NFD)}")
print(f"   what a reader counts                     4")
print("""
   Python answers one of those three, and it is not the one a person
   means. Nothing in the standard library returns the third; neither
   does Rust's. Swift's `count` does, because Swift chose a different
   default unit -- which is the whole of question three, and the page
   has the table.""")
