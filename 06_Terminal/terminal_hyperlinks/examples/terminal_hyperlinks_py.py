#!/usr/bin/env python3
"""What an OSC 8 hyperlink is made of, and what belongs in the URI inside it.

The tool measured on this page is `rg`, which neither CI runner has. What CAN be
checked is the standard it is being measured against: the OSC 8 rule about which
bytes may appear, and `urllib.parse.quote`'s answer for the same filenames. Each
section states a rule and applies it to the names rg was measured on.

The honest limit is this library's usual one for a tool page: this tests the
spec, not the implementation. That is why the session on the page is dated.
"""

import unicodedata
import urllib.parse

# The names rg was measured on. NFD is spelled with an escape because the two
# forms are the same picture and a typed literal is always the composed one.
NFC_NAME = "caf\u00e9.txt"   # c a f + U+00E9 LATIN SMALL LETTER E WITH ACUTE
NFD_NAME = "cafe\u0301.txt"  # c a f e + U+0301 COMBINING ACUTE ACCENT
assert unicodedata.normalize("NFD", NFC_NAME) == NFD_NAME

OSC8_OPEN = b"\x1b]8;;"      # ESC ] 8 ; ;
ST = b"\x1b\\"               # ESC \  -- the standard string terminator


def show(label: str, value: object) -> None:
    print(f"   {label:<40} {value}")


print("RULE 1. THE LINK IS AN ESCAPE SEQUENCE WRAPPED AROUND THE TEXT")
link = OSC8_OPEN + b"file://HOST/tmp/ok.txt" + ST + b"ok.txt" + OSC8_OPEN + ST
show("the opener, as bytes", OSC8_OPEN.hex(" "))
show("the terminator (ST), as bytes", ST.hex(" "))
show("whole link, bytes on the wire", len(link))
show("what the terminal draws", len("ok.txt"))
print("   Six characters of visible text inside forty-odd bytes of sequence, and")
print("   ESC is a C0 control -- so every byte that makes the link clickable is")
print("   invisible by design. Pipe the output anywhere and the difference shows")
print("   up as length: `wc -c` counts the sequence, your eyes do not.")

print()
print("RULE 2. THE SPEC SAYS 32-126. THE FILENAME DOES NOT ASK PERMISSION")
for label, name in [("ascii", "ok.txt"), ("space", "with space.txt"), ("NFC", NFC_NAME)]:
    raw = name.encode("utf-8")
    outside = [b for b in raw if b < 32 or b > 126]
    show(f"{label}: bytes outside 32-126", outside or "none")
    show(f"{label}: urllib quote() gives", urllib.parse.quote(name))
print("   The middle row is the one everyone gets right -- a space is 0x20, inside")
print("   the range, and still reserved, so every implementation escapes it. The")
print("   third row is the one to look at: 0xc3 0xa9 are outside the range, the")
print("   OSC 8 spec says such bytes 'must be URI-encoded' and that the behaviour")
print("   is undefined otherwise, and Python's quote() duly writes %C3%A9.")
print("   Measured on the page: rg writes the raw bytes.")

print()
print("RULE 3. TWO SPELLINGS OF ONE NAME ARE TWO DIFFERENT URIs")
show("NFC quoted", urllib.parse.quote(NFC_NAME))
show("NFD quoted", urllib.parse.quote(NFD_NAME))
show("same string?", NFC_NAME == NFD_NAME)
show("same after NFC normalisation?", unicodedata.normalize("NFC", NFD_NAME) == NFC_NAME)
print("   Both draw as café.txt. On Linux they are two files and two URIs; on a")
print("   Mac the filesystem folds them together, so the second name cannot exist")
print("   beside the first. A URI is a byte sequence and has no opinion about")
print("   normalisation -- whatever the filesystem handed over is what gets linked.")

print()
print("RULE 4. A COLUMN IS A NUMBER, AND THE UNIT IS NOT WRITTEN DOWN")
LINE = "café X here"
show("the line", repr(LINE))
show("'here' at character (1-based)", LINE.index("here") + 1)
show("'here' at byte (1-based)", LINE.encode("utf-8").index(b"here") + 1)
show("difference", LINE.encode("utf-8").index(b"here") - LINE.index("here"))
print("   Eight and nine. rg's --column counts bytes and says so in its own docs,")
print("   and the vscode hyperlink alias puts that number into the URI as")
print("   {column}. Nothing in the URI records which unit it is, so an editor that")
print("   counts characters lands one position early -- once per non-ASCII")
print("   character to the left of the match, silently, on the line it just")
print("   opened for you.")
