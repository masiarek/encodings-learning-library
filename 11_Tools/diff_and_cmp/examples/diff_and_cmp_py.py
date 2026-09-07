#!/usr/bin/env python3
"""The same two comparisons in Python, where "the same" is a decision you write
down rather than one the tool made before you arrived.

The shell example shows diff and cmp answering a question about bytes. Python
has both answers in the standard library — filecmp is cmp, difflib is diff — and
one answer neither shell tool has: open() translates line endings on the way in,
so the CRLF pair that diff reports as two changed lines arrives as one string.
Which of the three questions you asked is visible in the code, which is the
whole argument for doing it here.
"""

import difflib
import filecmp
import tempfile
import unicodedata
from pathlib import Path

NFC = "caf\u00e9\n"      # café, composed:   63 61 66 c3 a9 0a
NFD = "cafe\u0301\n"     # café, decomposed: 63 61 66 65 cc 81 0a
#     the mark is written as an escape on purpose: a combining acute pasted into
#     a source file is invisible to whoever edits it next, and to the reviewer.


def show(label: str, value: object) -> None:
    print(f"   {label:<40} {value}")


print("1. ONE WORD, TWO SPELLINGS, AND len() CAN SEE IT")
show("NFC on screen", NFC.strip())
show("NFD on screen", NFD.strip())
show("len(NFC), len(NFD)", (len(NFC.strip()), len(NFD.strip())))
show("NFC.encode('utf-8').hex()", NFC.strip().encode("utf-8").hex())
show("NFD.encode('utf-8').hex()", NFD.strip().encode("utf-8").hex())
show("NFC == NFD", NFC == NFD)
show("after NFC normalization", unicodedata.normalize("NFC", NFC) == unicodedata.normalize("NFC", NFD))
print("   Four characters against five, printed identically. == on str is not a")
print("   byte comparison — it compares code points — and it still says False,")
print("   because these are genuinely different code points. Only naming a")
print("   normal form makes the question answerable, and NFC is a CHOICE: it")
print("   says composed spellings win. diff has no way to express that choice.")

with tempfile.TemporaryDirectory() as d:
    tmp = Path(d)
    nfc, nfd = tmp / "nfc.txt", tmp / "nfd.txt"
    dos, unix = tmp / "dos.txt", tmp / "unix.txt"
    nfc.write_text(NFC, encoding="utf-8")
    nfd.write_text(NFD, encoding="utf-8")
    dos.write_bytes(b"one\r\ntwo\r\n")
    unix.write_bytes(b"one\ntwo\n")

    print()
    print("2. filecmp IS cmp, difflib IS diff")
    show("filecmp.cmp(shallow=False)", filecmp.cmp(nfc, nfd, shallow=False))
    print("   That is cmp -s: byte for byte, no decode, one boolean. shallow=True")
    print("   is the default and compares os.stat() — size and mtime — which is a")
    print("   different question wearing the same name.")
    lines = list(difflib.unified_diff(
        [NFC], [NFD], fromfile="nfc.txt", tofile="nfd.txt", lineterm=""))
    for line in lines:
        print(f"   {line.rstrip()}")
    print("   difflib prints the same unreadable change diff prints, for the same")
    print("   reason: it was handed two sequences and asked which differ. It")
    print("   compares characters rather than bytes, and on this pair that does")
    print("   not help — a decode is not a normalization.")

    print()
    print("3. THE ONE ANSWER THE SHELL TOOLS CANNOT GIVE: UNIVERSAL NEWLINES")
    show("open(dos).read() == open(unix).read()",
         dos.read_text(encoding="utf-8") == unix.read_text(encoding="utf-8"))
    with open(dos, encoding="utf-8", newline="") as f1, open(unix, encoding="utf-8", newline="") as f2:
        show("...with newline='' (no translation)", f1.read() == f2.read())
    show("...as bytes", dos.read_bytes() == unix.read_bytes())
    print("   True, False, False — one pair of files, three answers, and the")
    print("   difference is which door you opened them through. Python's default")
    print("   text mode translates CRLF to \\n on the way in, so the difference")
    print("   diff reports on every line of these two files is gone before your")
    print("   code sees it. That is a convenience with a cost: a program that")
    print("   reads text this way cannot tell you the file was ever a DOS file.")

    print()
    print("4. WRITE THE POLICY DOWN, THEN COMPARE")
    def same_text(a: Path, b: Path, *, form: str = "NFC", fold: bool = False) -> bool:
        """Equal as TEXT under a stated policy: decode, translate newlines,
        normalize, optionally case-fold. Every one of those is a decision."""
        def read(p: Path) -> str:
            s = unicodedata.normalize(form, p.read_text(encoding="utf-8"))
            return s.casefold() if fold else s
        return read(a) == read(b)

    show("same_text(nfc, nfd)", same_text(nfc, nfd))
    show("same_text(dos, unix)", same_text(dos, unix))
    show("filecmp.cmp(dos, unix, shallow=False)", filecmp.cmp(dos, unix, shallow=False))
    show("'CAFÉ'.casefold() == 'café'.casefold()", "CAFÉ".casefold() == "café".casefold())
    print("   Four lines that a shell one-liner cannot say. The last one is worth")
    print("   holding against diff -i, which folds ASCII case and leaves É alone:")
    print("   casefold() is Unicode's own case mapping, so it folds É to é — and")
    print("   ß to ss, which is why it is casefold() and not lower().")
    print("   Nothing here is more CORRECT than cmp. It is more SPECIFIC: the")
    print("   policy is four keyword arguments in one function instead of a")
    print("   default nobody chose.")
