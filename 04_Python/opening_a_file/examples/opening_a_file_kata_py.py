#!/usr/bin/env python3
"""Answers for the opening-a-file kata.

Same discipline as the lesson. The container rows are not typed in: each one
is a CHILD interpreter started with exactly the environment named beside it --
every LC_*, LANG and PYTHON* variable removed first, so the runner that started
this program cannot reach it -- and asked what open() does with the file. That
is all a container is, as far as this question goes: the same Python, started
with a different environment. The laptop and Windows rows cannot be run from
here, so they name the encoding those machines would pick and decode the bytes
with it. No locale name is printed -- the C locale has two spellings -- and no
exception's wording either, only its class.

Run:  python3 opening_a_file_kata_py.py
"""

import os
import subprocess
import sys
import tempfile

RAW = bytes.fromhex("63 61 66 c3 a9 0a".replace(" ", ""))

# What a child reports when nothing names an encoding: its UTF-8 Mode flag, the
# encoding open() picked (canonicalised, because the C locale has two
# spellings), and what it read -- or the class of what it raised.
PROBE = """\
import codecs, os, sys
with open(os.devnull) as fh:
    enc = codecs.lookup(fh.encoding).name
try:
    with open(sys.argv[1]) as fh:
        got = ascii(fh.read().rstrip("\\n")).strip("'")
except UnicodeDecodeError as exc:
    got = type(exc).__name__
print(sys.flags.utf8_mode, enc, got)
"""


def cps(s):
    return " ".join("U+%04X" % ord(c) for c in s)


def container(path, **env):
    """Run PROBE as a container would: no locale, no PYTHON* -- then `env`."""
    e = {k: v for k, v in os.environ.items()
         if not (k.startswith(("LC_", "PYTHON")) or k in ("LANG", "LANGUAGE"))}
    e.update(env)
    out = subprocess.run([sys.executable, "-c", PROBE, path], env=e,
                         capture_output=True, text=True, check=True).stdout
    return out.split()          # [utf8_mode, encoding, what it read]


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
    for machine, default in (("laptop, UTF-8 locale", "utf-8"),):
        shown = ascii(RAW.decode(default).rstrip("\n")).strip("'")
        print("   %-22s %-9s %-13s %s" % (machine, default, shown, "it does not"))
    _, default, shown = container(path)
    print("   %-22s %-9s %-13s %s"
          % ("container, no locale", default, shown, "it does not -- rescued"))
    shown = ascii(RAW.decode("cp1252").rstrip("\n")).strip("'")
    print("   %-22s %-9s %-13s %s"
          % ("Windows, cp1252", "cp1252", shown, "silently, forever"))
    print()
    print("   Two right answers and one wrong one, and the exit status is 0 on")
    print("   all three: nothing here fails loudly. The container's row was not")
    print("   typed in. It is the first line of the table below -- a real child,")
    print("   started with no locale at all, the way a container's entrypoint or")
    print("   a cron job starts one -- and it is right by rescue, not by design.")
    print()

    print("THE LOUD FAILURE IS STILL THERE -- SOMEBODY HAS TO ASK FOR IT")
    print()
    print("     %-26s %-10s %-8s %s" % ("child env", "utf8_mode", "open()", "result"))
    for label, env in (("(no locale)", {}),
                       ("LC_ALL=C", {"LC_ALL": "C"}),
                       ("PYTHONUTF8=0", {"PYTHONUTF8": "0"}),
                       ("LC_ALL=C  PYTHONUTF8=0", {"LC_ALL": "C", "PYTHONUTF8": "0"})):
        mode, default, shown = container(path, **env)
        print("     %-26s %-10s %-8s %s" % (label, mode, default, shown))
    print()
    print("   It takes both. LC_ALL=C on its own is a C locale, which PEP 540")
    print("   turns into UTF-8 Mode. PYTHONUTF8=0 on its own leaves LC_ALL")
    print("   unset, so PEP 538 coerces the missing locale to C.UTF-8 first.")
    print("   Only together do they put open() back on ASCII -- and the same")
    print("   two variables do it to the laptop. They cannot do it to the")
    print("   Windows box: cp1252 has a letter for every byte in this file, so")
    print("   there is nothing for it to refuse.")
    print()

print("AND WHAT PEP 686 DOES TO EACH ROW")
print()
print("   laptop      no change -- it was already UTF-8 Mode in all but name")
print("   container   no change -- it has run in UTF-8 Mode since 3.7, and")
print("               PEP 686 makes every other machine do what it already did")
print("   Windows     CHANGED, silently: the same bytes now decode as UTF-8,")
print("               so the third row above turns into the first one.")
print("               Right answer, no announcement -- and for a file that")
print("               really was cp1252, the reverse: it starts raising.")
print()
print("   And the loud row stays loud. PEP 686 changes a default, and")
print("   PYTHONUTF8=0 is not a default -- it is somebody saying no.")
print()
print("   The pattern is the point. A default that becomes correct is still")
print("   a default that changed, and the code that was relying on the old")
print("   one gets no warning at all. Every row above is settled for good")
print("   by one keyword argument, today, on every Python.")
print()

print("THE ONE LINE")
print("   open(path, encoding='utf-8')   and PEP 686 cannot reach you either.")
