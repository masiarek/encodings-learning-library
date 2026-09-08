#!/usr/bin/env python3
"""Answers for the opening-a-file kata.

Same discipline as the lesson: the three-machine question is answered by
naming an encoding explicitly rather than by pretending to be a machine we are
not on, and no locale name is printed -- the C locale has two spellings.

Run:  python3 opening_a_file_kata_py.py
"""

import os
import tempfile

RAW = bytes.fromhex("63 61 66 c3 a9 0a".replace(" ", ""))


def cps(s):
    return " ".join("U+%04X" % ord(c) for c in s)


print("ONE FILE, FOUR READINGS")
print("   bytes on disk   %s" % " ".join("%02x" % b for b in RAW))
print()
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "kata.txt")
    with open(path, "wb") as fh:
        fh.write(RAW)

    print("   %-10s %-19s %-6s %s" % ("encoding", "result", "chars", "code points"))
    for enc in ("utf-8", "ascii", "cp1252"):
        try:
            with open(path, encoding=enc) as fh:
                got = fh.read().rstrip("\n")
            print("   %-10s %-19s %-6d %s"
                  % (enc, ascii(got).strip("'"), len(got), cps(got)))
        except UnicodeDecodeError as exc:
            print("   %-10s %-19s %-6s byte %d is over 127"
                  % (enc, type(exc).__name__, "-", exc.start))
    with open(path, "rb") as fh:
        raw = fh.read()
    print("   %-10s %-19s %-6d %s"
          % ("'rb'", "bytes", len(raw), " ".join("%02x" % b for b in raw)))

print()
print("   Only 'ascii' raises. utf-8 gives four characters, cp1252 gives")
print("   five, and the extra one is not an error -- C3 and A9 are both")
print("   perfectly good Windows-1252 letters. 'rb' gives six bytes and")
print("   no opinion, which is the only honest answer before you know")
print("   what wrote the file.")
print()

print("THE SAME SCRIPT ON THREE MACHINES, WITH NO encoding= ANYWHERE")
print()
print("   %-22s %-9s %-13s %s"
      % ("machine", "default", "result", "how it fails"))
ROWS = [
    ("laptop, UTF-8 locale", "utf-8", "it does not"),
    ("container, C locale", "ascii", "loudly, first run"),
    ("Windows, cp1252", "cp1252", "silently, forever"),
]
for machine, default, how in ROWS:
    try:
        shown = ascii(RAW.decode(default).rstrip("\n")).strip("'")
    except UnicodeDecodeError:
        shown = "raises"
    print("   %-22s %-9s %-13s %s" % (machine, default, shown, how))
print()
print("   One file. One script. Three answers, and the exit status is 0 on")
print("   two of them.")
print()

print("AND WHAT PEP 686 DOES TO EACH ROW")
print()
print("   laptop      no change -- it was already UTF-8 Mode in all but name")
print("   container   FIXED, silently: the crash stops, and nobody learns")
print("               that the machine was misconfigured")
print("   Windows     CHANGED, silently: the same bytes now decode as UTF-8,")
print("               so the third row above turns into the first one.")
print("               Right answer, no announcement -- and for a file that")
print("               really was cp1252, the reverse: it starts raising.")
print()
print("   The pattern is the point. A default that becomes correct is still")
print("   a default that changed, and the code that was relying on the old")
print("   one gets no warning at all. Both rows below the first are fixed")
print("   permanently by one keyword argument, today, on every Python.")
print()

print("THE ONE LINE")
print("   open(path, encoding='utf-8')   and PEP 686 cannot reach you either.")
