#!/usr/bin/env python3
"""open(path) with no encoding= is a bet, and this file shows what it bets on.

THE ENVIRONMENT IS THE SUBJECT, so this program sets its own rather than
reading the one it was started in. Every answer about a default comes from a
CHILD interpreter whose variables are set on the line above it and printed
beside the result. That is not decoration: this library runs every example
under LC_ALL=C, and a C locale switches on UTF-8 Mode (PEP 540), which is
precisely what stops open()'s default from being the locale's. Asked about
itself, this program would report the opposite of what the page claims -- and
would record a passing answer key while doing it.

The runner sets PYTHONUTF8=1 as well, and that is NOT what switches the mode
on: it starts Python with -I, which implies -E, and -E ignores every PYTHON*
variable. Section 0 prints both halves of that.

Nothing below prints the locale's encoding by NAME. The C locale is called
'US-ASCII' on macOS and 'ANSI_X3.4-1968' on glibc, so the name is a fact about
the runner; codecs.lookup() canonicalises both to 'ascii', which is a fact
about the encoding. The two raw spellings are on the page, in a dated fence.

Run:  python3 opening_a_file_py.py
"""

import os
import subprocess
import sys
import tempfile
import unicodedata

RULE = "-" * 72

# A UTF-8 file and a Windows-1252 file, holding the same four characters.
TEXT = "café\n"                      # c a f U+00E9
UTF8_BYTES = TEXT.encode("utf-8")         # 63 61 66 c3 a9 0a
CP1252_BYTES = TEXT.encode("cp1252")      # 63 61 66 e9    0a


def child(code, args=(), **env):
    """Run `code` in a fresh interpreter whose environment we state exactly.

    Every PYTHON* variable is dropped first, so the harness that started THIS
    process cannot reach the child -- a child started without -I would obey
    the runner's PYTHONUTF8=1, which this process is ignoring. LC_ALL/LANG are
    pinned to C so the answer does not depend on the machine either. No -I
    unless a caller passes it, because isolated mode implies -E and -E would
    ignore the very variables this lesson is about; section 0 passes it once,
    to show exactly that."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    e.update({"LC_ALL": "C", "LANG": "C"})
    e.update(env)
    proc = subprocess.run([sys.executable, *args, "-c", code],
                          env=e, capture_output=True, text=True)
    return (proc.stdout + proc.stderr).strip()


def cps(s):
    """A string as its code points -- the only unambiguous way to quote one."""
    return " ".join("U+%04X" % ord(c) for c in s)


def hexs(b):
    return " ".join("%02x" % x for x in b)


print("0. THIS PROGRAM'S OWN ENVIRONMENT IS RIGGED")
print(RULE)
print("   The library runs every example under LC_ALL=C and LANG=C so that")
print("   answer keys do not depend on whose machine recorded them. For this")
print("   page that is a problem, because it leaves this interpreter in UTF-8")
print("   Mode -- the switch that stops open() asking the locale at all:")
print()
print("     %-38s %s" % ("sys.flags.utf8_mode:", sys.flags.utf8_mode))
print()
print("   The runner also sets PYTHONUTF8=1, and that is NOT why:")
print()
print("     %-38s %s" % ("PYTHONUTF8 in os.environ:",
                         os.environ.get("PYTHONUTF8", "(unset)")))
print("     %-38s %s" % ("sys.flags.isolated (-I):", sys.flags.isolated))
print("     %-38s %s" % ("sys.flags.ignore_environment (-E):",
                         sys.flags.ignore_environment))
print()
print("   The runner starts Python with -I, which implies -E, and -E ignores")
print("   every PYTHON* variable -- this one included. UTF-8 Mode is on for")
print("   the reason section 1's bottom row shows: the locale is C, and")
print("   PEP 540 turns a C locale into UTF-8 Mode by itself. Two children,")
print("   both under LC_ALL=C and both told PYTHONUTF8=0, settle which:")
print()
mode_probe = "import sys; print(sys.flags.utf8_mode)"
for label, args, note in (("python3 -I", ("-I",), "the variable is ignored"),
                          ("python3", (), "without -I, it is obeyed")):
    print("     %-12s utf8_mode %s   %s"
          % (label, child(mode_probe, args=args, PYTHONUTF8="0"), note))
print()
print("   So nothing below asks THIS interpreter what open() would do. Each")
print("   answer comes from a child whose environment is printed with it, and")
print("   none of those children gets -I: they have to hear their variables.")
print()

print("1. WHAT open() BETS ON")
print(RULE)
probe = (
    "import locale, sys, codecs, io\n"
    "enc = locale.getpreferredencoding(False)\n"
    "print('%-10s %-9s %-11s %s' % ("
    "  sys.flags.utf8_mode,"
    "  codecs.lookup(enc).name,"
    "  codecs.lookup(sys.stdout.encoding).name,"
    "  io.text_encoding(None)))\n"
)
print("     %-16s %-10s %-9s %-11s %s"
      % ("child env", "utf8_mode", "open()", "print()", "io.text_encoding"))
for label, env in (("PYTHONUTF8=1", {"PYTHONUTF8": "1"}),
                   ("PYTHONUTF8=0", {"PYTHONUTF8": "0"}),
                   ("(unset)", {})):
    print("     %-16s %s" % (label, child(probe, **env)))
print()
print("   Three things in that table.")
print()
print("   The middle row is the honest default: under a C locale with UTF-8")
print("   Mode off, open() decodes as ASCII -- so any byte over 127 ends the")
print("   program. Somebody has to switch the mode off to get it, though. A")
print("   container, a cron job or a systemd unit that sets nothing behaves")
print("   like the bottom row, not this one.")
print()
print("   The bottom row turned UTF-8 Mode on WITHOUT being asked. PEP 540")
print("   reads a C locale as a machine describing its own configuration")
print("   rather than its data, and overrides it. The locale page works")
print("   through that; the point here is only that the default has to be")
print("   asked about rather than assumed.")
print()
print("   The print() column is the same bet made on the way OUT. A script")
print("   that prints an e-acute happily in your terminal raises")
print("   UnicodeEncodeError in the middle row and in neither of the others")
print("   -- so not under a bare cron job, whose empty environment gets the")
print("   bottom row's answer. Nothing about the program changes from row to")
print("   row; only the environment it was started in.")
print()
print("   io.text_encoding(None) answers 'locale' rather than a name. That")
print("   string IS the encoding argument that means 'go and ask' -- it is")
print("   what open() uses when you pass nothing.")
print()

with tempfile.TemporaryDirectory() as tmp:
    utf8_path = os.path.join(tmp, "utf8.txt")
    cp1252_path = os.path.join(tmp, "cp1252.txt")
    with open(utf8_path, "wb") as fh:
        fh.write(UTF8_BYTES)
    with open(cp1252_path, "wb") as fh:
        fh.write(CP1252_BYTES)

    print("2. ONE FILE, FOUR READINGS")
    print(RULE)
    print("   A file holding the four characters c-a-f-e-acute, written UTF-8:")
    print()
    print("     bytes on disk    %s" % hexs(UTF8_BYTES))
    print()
    print("   Read with an encoding named explicitly, four ways. Only the")
    print("   first is right, and only the second says so:")
    print()
    print("     %-9s %-19s %s" % ("encoding", "result", "code points"))
    for enc in ("utf-8", "ascii", "cp1252", "latin-1"):
        try:
            with open(utf8_path, encoding=enc) as fh:
                got = fh.read().rstrip("\n")
            print("     %-9s %-19s %s" % (enc, ascii(got).strip("'"), cps(got)))
        except UnicodeDecodeError as exc:
            print("     %-9s %-19s byte %d is not ASCII"
                  % (enc, type(exc).__name__, exc.start))
    print()
    print("   And the reading that refuses to bet at all:")
    print()
    with open(utf8_path, "rb") as fh:
        raw = fh.read()
    print("     %-9s %-19s %s" % ("'rb'", "bytes", hexs(raw)))
    print()
    print("   The ASCII row is the safe failure: it stops. The cp1252 and")
    print("   latin-1 rows are the dangerous ones -- five characters where the")
    print("   file has four, no error, no exit status, and the corruption")
    print("   travels onward into whatever you write next.")
    print()

    print("3. THE FLIP PEP 686 CAUSES, AND WHY IT IS QUIET")
    print(RULE)
    print("   PEP 686 makes UTF-8 Mode the default, so open()'s guess stops")
    print("   depending on the machine. Most code this silently FIXES. The")
    print("   case it silently breaks needs bytes that decode cleanly under")
    print("   both the old default and the new one -- and there are two of")
    print("   them right here:")
    print()
    print("     bytes on disk    %s" % hexs(UTF8_BYTES))
    print()
    print("     %-22s %-19s %s" % ("read as", "result", "code points"))
    for enc in ("cp1252", "utf-8"):
        with open(utf8_path, encoding=enc) as fh:
            got = fh.read().rstrip("\n")
        label = "cp1252 (a Windows box)" if enc == "cp1252" else "utf-8 (after PEP 686)"
        print("     %-22s %-19s %s" % (label, ascii(got).strip("'"), cps(got)))
    print()
    print("   No exception on either line. Same file, same call, two answers,")
    print("   and the only thing that changed was a default. That pair --")
    print("   C3 A9 read as two Latin-1 letters -- is the mojibake this")
    print("   library keeps meeting; here it is arriving as an UPGRADE.")
    print()
    print("   The other direction is louder and so matters less. A genuine")
    print("   Windows-1252 file:")
    print()
    print("     bytes on disk    %s" % hexs(CP1252_BYTES))
    for enc in ("cp1252", "utf-8"):
        try:
            with open(cp1252_path, encoding=enc) as fh:
                got = fh.read().rstrip("\n")
            print("     %-22s %-19s %s"
                  % ("read as " + enc, ascii(got).strip("'"), cps(got)))
        except UnicodeDecodeError as exc:
            print("     %-22s %-19s byte %d cannot start a sequence"
                  % ("read as " + enc, type(exc).__name__, exc.start))
    print()
    print("   That one you find on the first run. It is the quiet row above")
    print("   that reaches production.")
    print()

    print("4. FINDING THESE CALLS IN CODE YOU ALREADY HAVE")
    print(RULE)
    print("   PEP 597 added a warning for exactly this, and it is off by")
    print("   default. Turn it on and every open() that did not say an")
    print("   encoding reports itself:")
    print()
    warn_code = (
        "import warnings, sys\n"
        "with warnings.catch_warnings(record=True) as caught:\n"
        "    warnings.simplefilter('always')\n"
        "    open(%r).close()\n"
        "    open(%r, encoding='utf-8').close()\n"
        "print('warnings raised:', len(caught))\n"
        "for w in caught:\n"
        "    print('%%s from line %%d' %% (w.category.__name__, w.lineno))\n"
    ) % (utf8_path, utf8_path)
    print("     python3 -X warn_default_encoding  (or PYTHONWARNDEFAULTENCODING=1)")
    for line in child(warn_code, args=("-X", "warn_default_encoding"),
                      PYTHONUTF8="0").splitlines():
        print("       " + line)
    print()
    print("     without the flag:")
    for line in child(warn_code, PYTHONUTF8="0").splitlines():
        print("       " + line)
    print()
    print("   One call warned and one did not, and the difference between them")
    print("   is the whole lesson: the second one said encoding='utf-8'.")
    print()
    print("   Only the warning's CLASS is printed above. Its wording is")
    print("   CPython's and may be reworded in any release, which is not")
    print("   something this library puts in an answer key.")
    print()
    print("   If you WRITE functions that take an encoding argument, there is")
    print("   a matching call for the other side of the boundary:")
    print()
    print("     def load(path, encoding=None):")
    print("         encoding = io.text_encoding(encoding)   # <- one line")
    print("         return open(path, encoding=encoding).read()")
    print()
    print("   io.text_encoding() returns 'locale' or 'utf-8' as appropriate")
    print("   AND blames the caller's line rather than yours, so the warning")
    print("   points at the code that has to change.")
    print()

    print("5. TEXT MODE ALSO REWRITES YOUR LINE ENDINGS")
    print(RULE)
    print("   Encoding is not the only thing open() decides. In text mode it")
    print("   translates line endings on the way in, which is a second silent")
    print("   difference between the file and the string:")
    print()
    crlf_path = os.path.join(tmp, "crlf.txt")
    with open(crlf_path, "wb") as fh:
        fh.write(b"a\r\nb\n")
    print("     bytes on disk               %s" % hexs(b"a\r\nb\n"))
    with open(crlf_path, encoding="utf-8") as fh:
        print("     open(..., encoding='utf-8') %s" % ascii(fh.read()))
    with open(crlf_path, encoding="utf-8", newline="") as fh:
        print("     ... plus newline=''         %s" % ascii(fh.read()))
    with open(crlf_path, "rb") as fh:
        print("     open(..., 'rb')             %s" % ascii(fh.read()))
    print()
    print("   The default is usually what you want for reading prose and is")
    print("   wrong for the csv module, which does its own line handling and")
    print("   documents newline='' as required -- a quoted field is allowed to")
    print("   contain a bare CR or LF, and translating it corrupts the record.")
    print()

    print("6. AND open() DOES NOT NORMALISE")
    print(RULE)
    print("   Decoding settles which characters the bytes name. It does not")
    print("   settle which SPELLING of a character was written, and the")
    print("   e-acute has two:")
    print()
    composed = unicodedata.normalize("NFC", "café")
    decomposed = unicodedata.normalize("NFD", "café")
    nfc_path = os.path.join(tmp, "nfc.txt")
    nfd_path = os.path.join(tmp, "nfd.txt")
    for path, s in ((nfc_path, composed), (nfd_path, decomposed)):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(s)
    print("     %-8s %-6s %-22s %s" % ("form", "chars", "bytes on disk", "code points"))
    for label, path in (("NFC", nfc_path), ("NFD", nfd_path)):
        with open(path, "rb") as fh:
            b = fh.read()
        with open(path, encoding="utf-8") as fh:
            s = fh.read()
        print("     %-8s %-6d %-22s %s" % (label, len(s), hexs(b), cps(s)))
    print()
    with open(nfc_path, encoding="utf-8") as f1, open(nfd_path, encoding="utf-8") as f2:
        a, b = f1.read(), f2.read()
    print("     %-40s %s" % ("the two strings compare equal:", a == b))
    print("     %-40s %s" % ("...after unicodedata.normalize('NFC'):",
                             unicodedata.normalize("NFC", a)
                             == unicodedata.normalize("NFC", b)))
    print()
    print("   Both files are valid UTF-8, both were read with the correct")
    print("   encoding, both print the same word, and they are not the same")
    print("   string. encoding= was never the question here -- which is worth")
    print("   knowing before you spend an afternoon on it.")
    print()

print("7. THE RULE")
print(RULE)
print("     open(path, encoding='utf-8')   says what it means, everywhere")
print("     open(path, 'rb')               refuses to guess; decide later")
print("     open(path)                     asks a machine you have not met")
print()
print("   Pass encoding=, and nothing on this page can reach your program.")
