#!/usr/bin/env python3
"""The same four searches grep does, in Python, where the byte/character line is
a type and not a locale.

The shell example on this page runs in the C locale, so `.` there means one
byte. Python has no such setting: a `str` pattern searches characters, a `bytes`
pattern searches bytes, and you choose by which kind of object you hand it. That
is the whole difference, and it is why this file is on the page.
"""

import re

CAFE = "café"
LINES = ["plain ascii", "café here", "more ascii"]


def show(label: str, value: object) -> None:
    print(f"   {label:<34} {value}")


print("1. THE DOT: THE CHOICE IS A TYPE, NOT A LOCALE")
show("len('café')", len(CAFE))
show("len(b'caf\\xc3\\xa9')", len(CAFE.encode("utf-8")))
show("len(re.findall('.', 'café'))", len(re.findall(".", CAFE)))
show("len(re.findall(b'.', ...utf-8))", len(re.findall(b".", CAFE.encode("utf-8"))))
print("   Four and five, from one file, and nothing in between decided it for")
print("   you: the str pattern searched characters, the bytes pattern searched")
print("   bytes. grep makes the same choice from the locale, silently.")

print()
print("2. FINDING THE NON-ASCII LINES")
for n, line in enumerate(LINES, 1):
    hit = re.search(r"[^\x00-\x7f]", line)
    verdict = "NON-ASCII" if hit else "ascii only"
    print(f"   line {n}: {verdict:<11} {line}")
print("   The class is the same idea as the shell's [^ -~], written the way a")
print("   language with escapes lets you write it. grep's BSD build has no -P,")
print("   so it cannot take \\x escapes at all — hence the printable-range trick.")

print()
print("3. A NUL IS JUST A CHARACTER")
data = b"hello\x00world\nhello again\n"
text = data.decode("utf-8")
show("b'...' contains a NUL", b"\x00" in data)
show("lines matching 'hello'", sum("hello" in ln for ln in text.splitlines()))
show("Python refused to show them?", False)
print("   grep calls this file binary and prints a notice instead of the lines.")
print("   Python has no such rule — the NUL is character U+0000 and the search")
print("   works. A rule that protects a terminal from control bytes is not a")
print("   rule about what the text is.")

print()
print("4. UTF-16 — THE SEARCH THAT NEEDS A DECODE, NOT A BETTER PATTERN")
raw = "café\n".encode("utf-16-le")
raw_with_mark = b"\xff\xfe" + raw
show("the bytes", raw_with_mark.hex())
show("b'caf' in the bytes", b"caf" in raw_with_mark)
show("'caf' in decoded utf-16", "caf" in raw_with_mark.decode("utf-16"))
print("   The first answer is False and the second is True, for one file. This is")
print("   exactly grep's failure on the same file, and the fix is the same: name")
print("   the encoding and decode, then search. Note that decoding as 'utf-16'")
print("   with no LE/BE suffix consumed the mark; 'utf-16-le' would have handed")
print("   it back as a leading U+FEFF, which is the shell example's last section.")

print()
print("5. THE BYTES THAT ARE NOT VALID TEXT")
broken = b"good line\nbad \xff\xfe line\nlast line\n"
strict_failed = False
try:
    broken.decode("utf-8")
except UnicodeDecodeError as exc:
    strict_failed = True
    show("strict decode", f"UnicodeDecodeError at byte {exc.start}")
show("strict decode raised", strict_failed)
lax = broken.decode("utf-8", errors="surrogateescape")
show("surrogateescape: lines kept", len(lax.splitlines()))
show("...lines containing 'line'", sum("line" in ln for ln in lax.splitlines()))
show("re-encodes to the same bytes", lax.encode("utf-8", "surrogateescape") == broken)
print("   Three lines in, three lines out, and the file round-trips byte for")
print("   byte. Python's three answers to invalid input are: raise (strict),")
print("   replace (lose the bytes), or surrogateescape (keep them). One of the")
print("   two greps has a fourth answer — skip the line and say nothing — and")
print("   the page names which.")
