#!/usr/bin/env python3
"""The Python-specific half of the checklist, with the traps shown failing.

Nothing here is about Unicode theory — that is the rest of the library. This is
about the six places where Python's own defaults, or Python's own vocabulary,
are where the mistake actually happens.

Everything runs in memory (io.BytesIO stands in for a file) so the example is
deterministic on any machine.

Run:  python3 python_text_in_practice_py.py
"""

import io
import json
import os
import re
import sys
import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "str AND bytes DO NOT MIX, AND THAT IS THE FEATURE")
t, b = "Łódź", "Łódź".encode("utf-8")
print(f"   str    {t!r:12} len {len(t)}   type {type(t).__name__}")
print(f"   bytes  {b!r:22} len {len(b)}   type {type(b).__name__}")
for expr, fn in [
    ('"a" + b"b"', lambda: "a" + b"b"),
    ('"Ł" in b"\\xc5\\x81"', lambda: "Ł" in b"\xc5\x81"),
    ('b"x".decode()', lambda: b"x".decode()),
]:
    try:
        print(f"   {expr:22} -> {fn()!r}")
    except TypeError as e:
        print(f"   {expr:22} -> TypeError: {e}")
print("   Python 2 would have guessed here, and guessed with ASCII. Python 3")
print("   refuses, which turns a wrong answer in production into a TypeError")
print("   on your machine. Every '.encode()' you add is you saying where the")
print("   boundary of your program is.")

# ------------------------------------------------------------------ 2
head(2, "open(): FOUR ARGUMENTS THAT SHOULD BE HABIT")
raw = "id,city\r\n1,Łódź\r\n".encode("utf-8")
handle = io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8", newline="")
print(f"   on disk               {raw!r}")
print(f"   encoding='utf-8'      {handle.read()!r}")
handle = io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8")
print(f"   newline= left default {handle.read()!r}   <- \\r\\n became \\n")
print("     open(p, encoding='utf-8')   name the encoding even when it is the")
print("                                 default; it says which side of the")
print("                                 boundary the file is on")
print("     newline=''                  for csv, ALWAYS — the csv module does")
print("                                 its own line handling and doubles up")
print("                                 otherwise")
print("     errors='strict'             the default; change it deliberately")
print("     'rb' / 'wb'                 when it is not text: images, zips, and")
print("                                 anything you will hash or checksum")

# ------------------------------------------------------------------ 3
head(3, "TWO SWITCHES THAT TURN THE WHOLE CLASS OF BUG INTO A WARNING")
print(f"   sys.flags.utf8_mode             = {sys.flags.utf8_mode}")
print("       set by -X utf8 or PYTHONUTF8; with neither, a C or POSIX locale")
print("       switches it on by itself (PEP 540)")
print(f"   sys.flags.warn_default_encoding = {sys.flags.warn_default_encoding}")
print("       set by -X warn_default_encoding or PYTHONWARNDEFAULTENCODING=1")
print("   In this page's recorded run the first flag is 1 because of the")
print("   locale: the library records every example under LC_ALL=C, and runs")
print("   it with python3 -I, which ignores every PYTHON* variable — so the")
print("   PYTHONUTF8=1 the runner also sets is ignored with the rest.")
print()
print("   UTF-8 mode stops Python asking the locale wherever it picks an")
print("   encoding for you — open(), the standard streams, filenames — and")
print("   PEP 686 makes it the DEFAULT in Python 3.15, which is the single")
print("   biggest change to this subject in fifteen years.")
print()
print("   The second flag is the one to run your test suite under today:")
print("   -X warn_default_encoding turns every open() that did not name an")
print("   encoding into an EncodingWarning, pointing at the line. That is a")
print("   whole codebase audited in one run, and it is PEP 597, since 3.10.")

# ------------------------------------------------------------------ 4
head(4, "FILENAMES ARE NOT TEXT, AND PYTHON HANDS YOU THE ESCAPE HATCH")
weird = b"report-caf\xe9.csv"                       # a Latin-1 name on a Unix disk
name = os.fsdecode(weird)
print(f"   bytes on disk       {weird!r}")
print(f"   os.fsdecode(...)    {name!r}")
print(f"   os.fsencode(back)   {os.fsencode(name)!r}")
print(f"   round-trips exactly {os.fsencode(name) == weird}")
print("   A Unix filename is any bytes but NUL and '/', so it need not be UTF-8")
print("   at all. os.listdir() gives you str with the undecodable bytes parked")
print("   in surrogates, and os.fsencode puts them back — which is why you can")
print("   rename a file you cannot print. Never .encode('utf-8') a filename by")
print("   hand; that is the call that raises on somebody else's disk.")

# ------------------------------------------------------------------ 5
head(5, "bytes HAS TEXT-LOOKING METHODS. THEY ARE ASCII-ONLY, ON PURPOSE.")
strasse = "straße"
print(f"   'straße'.upper()          -> {strasse.upper()!r}   <- one letter became two")
print(f"   'straße'.encode().upper() -> {strasse.encode().upper()!r}")
print("                                  ^ the ß bytes came through untouched:")
print("                                    bytes.upper() only knows a-z.")
print()
# Computed outside the f-strings: before 3.12 an f-string's {expression}
# may not contain a backslash, and both patterns need one.
words_str = re.findall(r"\w+", "Łódź ok")
words_bytes = re.findall(rb"\w+", "Łódź ok".encode())
print(f"   re.findall(r'\\w+', 'Łódź ok')          -> {words_str}")
print(f"   re.findall(rb'\\w+', b'...') on bytes   -> {words_bytes}")
print("   Same pattern, two answers: \\w means 'Unicode word character' against")
print("   str and 'ASCII word character' against bytes. A bytes object has no")
print("   idea which table made it, so ASCII is the only thing it can assume —")
print("   and that is the right call, not a limitation.")

# ------------------------------------------------------------------ 6
head(6, "THE unicodedata TOOLKIT, WHICH IS ALREADY INSTALLED")
for ch in ["ź", "́", "😀"]:
    print(f"   {ch!r:10} category {unicodedata.category(ch):3}  "
          f"combining {unicodedata.combining(ch):3}  {unicodedata.name(ch)}")
print(f"   lookup('YEN SIGN')          -> {unicodedata.lookup('YEN SIGN')!r}")
print(f"   normalize('NFKC', 'ﬁ')      -> {unicodedata.normalize('NFKC', 'ﬁ')!r}"
      f"   <- the ligature becomes two letters")
print(f"   normalize('NFKC', '１２３')  -> {unicodedata.normalize('NFKC', '１２３')!r}"
      f"   <- fullwidth digits become ASCII")
print("   NFKC is the aggressive one: it folds compatibility forms together, so")
print("   it is right for a search index or a username check and wrong for text")
print("   you will store and hand back. NFC is the safe default for storage.")
print()
print(f"   And the export side, one flag: json.dumps(ensure_ascii=False) ->"
      f" {json.dumps({'c': 'Łódź'}, ensure_ascii=False)}")
