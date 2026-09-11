#!/usr/bin/env python3
"""The five rules, each one shown working and shown failing.

The rules are language-independent — they are about where the boundary of your
program is — but Python is the shortest place to demonstrate them, because it
draws the text/bytes line as a type you can print.

Run:  python3 utf8_everywhere_py.py
"""

import codecs
import io
import json
import locale
import sys
import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "THE SANDWICH: DECODE AT THE EDGE, WORK IN TEXT, ENCODE AT THE EDGE")
wire = b"name,city\r\n\xc5\x81\xc3\xb3d\xc5\xba,PL\r\n"      # what arrived
text = wire.decode("utf-8")                                   # decode ONCE, here
rows = [line.split(",") for line in text.splitlines() if line]
out = "\n".join(";".join(r) for r in rows).encode("utf-8")    # encode ONCE, here
print(f"   in   (bytes) {wire!r}")
print(f"   work (str)   {rows!r}")
print(f"   out  (bytes) {out!r}")
print("   Bytes at the two ends, text in the middle, and NOTHING in the middle")
print("   that has to know what an encoding is. Every encoding bug you will")
print("   ever have is a program that let bytes leak into the filling.")

# ------------------------------------------------------------------ 2
head(2, "THE ENCODING IS NOT A GUESS — IT COMES FROM THE PROTOCOL")


def canonical(name):
    """codecs.lookup()'s spelling. The C locale's encoding is 'US-ASCII' on
    macOS and 'ANSI_X3.4-1968' on glibc, and both of those are 'ascii'."""
    return codecs.lookup(name).name


# A TextIOWrapper given no encoding= is the object open() builds in text mode,
# and it makes open()'s choice — over bytes in memory, so no file is touched.
choices = [
    ("sys.flags.utf8_mode", sys.flags.utf8_mode, ""),
    ("locale.getencoding()", canonical(locale.getencoding()),
     "<- what the locale says"),
    ("locale.getpreferredencoding(False)",
     canonical(locale.getpreferredencoding(False)), "<- open()'s default"),
    ("io.TextIOWrapper(buf).encoding",
     canonical(io.TextIOWrapper(io.BytesIO()).encoding), "<- open()'s own choice"),
]
for label, value, note in choices:
    print(f"   {label:34} = {value!s:6}  {note}".rstrip())
print("   (The last line builds the object open() returns, over bytes in")
print("   memory. Names are canonical, from codecs.lookup(): under LC_ALL=C")
print("   macOS calls the locale's encoding 'US-ASCII' and Linux calls it")
print("   'ANSI_X3.4-1968' — even the fallback's NAME is machine-dependent.)")
print()
print("   open() with no encoding= follows getpreferredencoding(False), not")
print("   getencoding(): UTF-8 while UTF-8 Mode is on, the locale's encoding")
print("   when it is off. This page's recorded run has the mode on without")
print("   anyone asking: the run is pinned to LC_ALL=C, and PEP 540 switches")
print("   UTF-8 Mode on under a C locale, which is why the locale and open()")
print("   disagree there. With the mode off, a C locale gets you ASCII, which")
print("   raises on the first byte over 127, and a western Windows box gets")
print("   you 'cp1252' — which is how the same script reads a file correctly")
print("   on one machine and silently wrongly on another.")
print()
print("   So: open(path, encoding='utf-8'), always, even when it is the default.")
print("   Python 3.15 makes UTF-8 the default (PEP 686) and the argument STILL")
print("   belongs in the call, because it documents which side of the boundary")
print("   the file is on. The encoding comes from the HTTP header, the database")
print("   connection, the interface spec — never from the bytes themselves.")

# ------------------------------------------------------------------ 3
head(3, "errors= IS A POLICY DECISION. MAKE IT ON PURPOSE.")
dirty = "Sales: café".encode("latin-1")          # someone else's file
print(f"   the bytes: {dirty!r}")
for policy in ["strict", "replace", "ignore", "backslashreplace", "surrogateescape"]:
    try:
        print(f"     errors={policy:17} -> {dirty.decode('utf-8', policy)!r}")
    except UnicodeDecodeError as e:
        print(f"     errors={policy:17} -> UnicodeDecodeError at byte {e.start}")
print()
round_trip = dirty.decode("utf-8", "surrogateescape").encode("utf-8", "surrogateescape")
print(f"   Only ONE of them can be undone: surrogateescape round-trips.")
print(f"     decode then encode == the original bytes: {round_trip == dirty}")
print("   Use strict for data you own, surrogateescape when you must carry")
print("   somebody else's bytes through unharmed, replace only for a log line")
print("   a human will read. Never ignore: it deletes evidence silently.")

# ------------------------------------------------------------------ 4
head(4, "COMPARE AFTER NORMALIZING, NOT BEFORE")
composed = "łódź"                   # ł ó d ź
decomposed = unicodedata.normalize("NFD", composed)
print(f"   composed   {composed!r}  {len(composed)} code points  {composed.encode().hex(' ')}")
print(f"   decomposed {decomposed!r}  {len(decomposed)} code points  {decomposed.encode().hex(' ')}")
print(f"   composed == decomposed                : {composed == decomposed}")
print(f"   NFC(composed) == NFC(decomposed)      : "
      f"{unicodedata.normalize('NFC', composed) == unicodedata.normalize('NFC', decomposed)}")
print("   Same word, same screen, different bytes — a macOS filename and a")
print("   Linux one, or a form field and a database row. Normalize to NFC on")
print("   the way IN and compare after that; do not normalize at compare time")
print("   in one place and forget in the other.")
print()
print("   Caseless comparison is casefold(), not lower():")
for w in ["Straße", "İstanbul"]:
    print(f"     {w!r:12} lower {w.lower()!r:13} casefold {w.casefold()!r:13} "
          f"upper {w.upper()!r}")
print("   Note the lengths change. 'ß'.upper() is two letters, so a case")
print("   conversion is not a per-character operation and never was.")

# ------------------------------------------------------------------ 5
head(5, "'LENGTH' HAS THREE ANSWERS. SAY WHICH ONE YOU MEANT.")
def pad(s, width):
    """Left-justify by terminal columns: CJK and emoji are two columns wide."""
    cols = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, width - cols)


samples = [
    ("Łódź", "Łódź", 4),
    ("café", "café", 4),
    ("café (NFD)", unicodedata.normalize("NFD", "café"), 4),
    ("👨\u200d👩\u200d👧", "👨\u200d👩\u200d👧", 1),
]
print(f"   {'text':14} {'bytes':>6} {'code points':>12} {'graphemes':>10}")
for label, text, graphemes in samples:
    print(f"   {pad(label, 14)} {len(text.encode('utf-8')):6} {len(text):12} {graphemes:10}")
print("   (the last column is counted BY EYE — Python's standard library has no")
print("    grapheme segmenter, which is the point of the paragraph below)")
print("   The bytes column is what a VARCHAR(n) and a fixed-width field count.")
print("   The code-point column is what len() gives you. The last column needs")
print("   grapheme-cluster segmentation, which is a library in every language")
print("   including this one. Three different questions — pick one deliberately.")

# ------------------------------------------------------------------ 6
head(6, "TWO DEFAULTS WORTH CHANGING ON THE WAY OUT")
data = {"city": "Łódź"}
print(f"   json.dumps(...)                     -> {json.dumps(data)}")
print(f"   json.dumps(..., ensure_ascii=False) -> {json.dumps(data, ensure_ascii=False)}")
print("   Both are valid JSON and both survive the trip. The first is ASCII-safe")
print("   escaping from an era when the channel might not be 8-bit clean; today")
print("   it mostly makes payloads bigger and logs unreadable. JSON is UTF-8 by")
print("   RFC 8259, so ensure_ascii=False is the honest default now.")
print()
print("   And the BOM: read Excel's CSVs with encoding='utf-8-sig', which eats a")
print("   leading BOM if there is one; write with 'utf-8' so you never add one.")
bom_csv = "\ufeffid,city\n1,Łódź\n".encode("utf-8")
print(f"     first bytes from Excel : {bom_csv[:6].hex(' ')}")
print(f"     read as utf-8          : {bom_csv.decode('utf-8').split(',')[0]!r}  <- BOM stuck to the header")
print(f"     read as utf-8-sig      : {bom_csv.decode('utf-8-sig').split(',')[0]!r}")
