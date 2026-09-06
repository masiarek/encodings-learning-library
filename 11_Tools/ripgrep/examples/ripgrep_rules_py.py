#!/usr/bin/env python3
"""The four rules ripgrep follows, applied by hand in the standard library.

`rg` is not on either CI runner — it ships with no operating system — so no
answer key on this page can be recorded from the tool itself. What CAN be
checked is the rules it implements, because they are short and none of them is
exotic. Each section below states a rule, applies it to the same file rg was
measured on, and prints the answer rg gave.

If one of these ever stops agreeing with the tool, the page is wrong and this
program will not notice — that is the honest limit of doing it this way, and it
is why the real outputs on the page are dated and name their machines.
"""

import re

RAW_UTF16 = b"\xff\xfe" + "café\n".encode("utf-16-le")
RAW_UTF32 = b"\xff\xfe\x00\x00" + "café\n".encode("utf-32-le")
RAW_UTF8 = "café\n".encode("utf-8")
RAW_LATIN1 = "café latin1\n".encode("latin-1")
RAW_NUL = b"hello\x00world\nhello again\n"
RAW_INVALID = b"good line\nbad \xff\xfe line\nlast line\n"

# The marks rg's default (-E auto) actually tests for. Three, not five: the man
# page says detection "only applies to files that begin with a UTF-8 or UTF-16
# byte-order mark (BOM). No other automatic detection is performed."
RG_BOMS = [
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
]

# The two it does not test — and the first of them BEGINS with the whole of
# UTF-16LE's mark, which is why leaving it off the list is not a no-op.
UNTESTED = [
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
]


def sniff(raw: bytes) -> str | None:
    """Rule 1: a byte-order mark names the encoding, and rg believes it."""
    for mark, codec in RG_BOMS:
        if raw.startswith(mark):
            return codec
    return None


def decode_like_rg(raw: bytes) -> str:
    """Sniff, consume the mark, decode. No mark means assume UTF-8."""
    codec = sniff(raw)
    if codec is None:
        return raw.decode("utf-8", "replace")
    if codec == "utf-8-sig":
        return raw.decode(codec)  # this codec eats its own mark
    return raw[2:].decode(codec)  # rg does not put the mark in the output


def show(label: str, value: object) -> None:
    print(f"   {label:<38} {value}")


print("RULE 1. A BOM NAMES THE ENCODING, AND IS ACTED ON")
for name, raw in [
    ("utf-16le + BOM", RAW_UTF16),
    ("utf-8, no BOM", RAW_UTF8),
    ("utf-32le + BOM", RAW_UTF32),
]:
    codec = sniff(raw)
    text = decode_like_rg(raw)
    show(f"{name}: sniffed", codec or "(nothing — assume UTF-8)")
    show(f"{name}: 'caf' in the BYTES", b"caf" in raw)
    show(f"{name}: 'caf' after decoding", "caf" in text)
print("   The first file answers False then True: the word is present and the")
print("   bytes do not contain it. That gap is the whole difference between")
print("   grep and rg on this file — rg looks at the first two bytes, decodes,")
print("   and searches the text. grep searches the bytes and finds nothing.")
print("   The third file answers False TWICE, and that is not a typo. rg tests")
print("   three marks, not five:", ", ".join(c for _, c in RG_BOMS) + ".")
show("marks rg does not test", ", ".join(c for _, c in UNTESTED))
show("utf-32le + BOM: what it decoded to", repr(text))
print("   UTF-32LE's mark ff fe 00 00 STARTS with UTF-16LE's ff fe, so a sniffer")
print("   that does not test the four-byte form calls the file UTF-16 and welds a")
print("   NUL to every letter. rg is such a sniffer, and the NULs then make it")
print("   call the file binary — measured on the page above, both machines.")

print()
print("RULE 2. NO BOM: SEARCH THE RAW BYTES, AND A UNICODE CLASS SKIPS")
print("         WHAT IT CANNOT DECODE")
show("latin-1 bytes", RAW_LATIN1.hex())
byte_mode = len(re.findall(rb"[^\n]", RAW_LATIN1))
lax = RAW_LATIN1.decode("utf-8", "surrogateescape")
char_mode = sum(1 for ch in lax if ch != "\n" and not "\udc80" <= ch <= "\udcff")
show("bytes that are not a newline", byte_mode)
show("of those, decodable characters", char_mode)
show("b'caf' present in the raw bytes", b"caf" in RAW_LATIN1)
show("the e9 became U+FFFD?", "\ufffd" in lax)
print("   Eleven and ten. The e9 is a byte that no character class can match,")
print("   because there is no character there to match — and it did NOT become")
print("   U+FFFD, which is the mistake to avoid: nothing decoded it, nothing")
print("   replaced it, it is simply skipped by anything Unicode-aware and seen")
print("   by anything byte-oriented. Those are rg's two modes: '.' matches ten,")
print("   and '(?-u).' or --no-unicode matches eleven.")
print("   So 'caf' matches (three ASCII bytes, present as bytes) and 'caf.' does")
print("   not (the fourth position is not a character). Naming the encoding is")
print("   the only real fix; rg spells it -E latin1, and then it re-encodes what")
print("   it prints, so the match comes back out of the pipe as UTF-8.")

print()
print("RULE 3. A NUL MEANS BINARY — AND SAY WHERE IT WAS")
offset = RAW_NUL.find(b"\x00")
show("first NUL at offset", offset)
show("lines containing 'hello'", sum(
    b"hello" in ln for ln in RAW_NUL.split(b"\n")))
print("   Both greps and rg agree that one NUL reclassifies the file. They")
print("   differ in what they tell you: the two greps name the file, rg names")
print("   the file AND the offset — 'found \"\\0\" byte around offset 5' — which")
print("   is the difference between a refusal and a diagnosis. You now know")
print("   where to look, and xxd -s 0 -l 16 will show you.")

print()
print("RULE 4. INVALID BYTES DO NOT REMOVE A LINE")
kept = RAW_INVALID.decode("utf-8", "surrogateescape").splitlines()
show("lines in the file", len(RAW_INVALID.splitlines()))
show("lines after decoding the bad bytes", len(kept))
show("lines containing 'line'", sum("line" in ln for ln in kept))
print("   Three, three, three. Whatever you do with the two bad bytes — keep")
print("   them, replace them, refuse to look at them — the LINE is still there")
print("   and is still searched. That is the rule rg follows and the rule BSD")
print("   grep does not: measured on the grep page, the same file loses a line")
print("   in a UTF-8 locale and grep still exits 0. A line is a run of bytes")
print("   between newlines, and no decoding question changes where they are.")
