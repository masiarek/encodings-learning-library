#!/usr/bin/env python3
"""Binary or text: one set of bytes, several readers, and who decides.

The bytes are c0 ff ee. Nothing in them says "binary" or "text", so every
reader brings its own test. This program asks three codecs and git's rule in
memory, works out why UTF-8 in particular refuses, and then shows that a
filename is not an input to any of it. The disk-level tools - file, grep,
iconv - are in the shell example; the Finder, which does read the name, is on
the page.

What is printed is a codec's output, an exception CLASS, or arithmetic -
never an exception's message, which is CPython's wording and moves between
versions.

Run:  python3 binary_or_text_py.py
"""

import os
import tempfile

DATA = bytes.fromhex("c0 ff ee")
REPLACEMENT = chr(0xFFFD)


def hexed(bs: bytes) -> str:
    return " ".join(f"{b:02x}" for b in bs)


def points(s: str) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in s)


print("1. ONE SET OF BYTES, SIX READINGS")
print(f"   the bytes              {hexed(DATA)}")
try:
    DATA.decode("utf-8")
except UnicodeDecodeError as e:
    print(f"   utf-8, strict          {type(e).__name__} at byte {e.start}")
replaced = DATA.decode("utf-8", errors="replace")
print(f"   utf-8, replace         {replaced.count(REPLACEMENT)} of {len(replaced)} characters are U+FFFD")
for codec in ("latin-1", "cp1252", "mac_roman"):
    text = DATA.decode(codec)
    print(f"   {codec:<22} {text}   {points(text)}")
has_nul = b"\x00" in DATA[:8000]
print(f"   git's rule             {'binary' if has_nul else 'text'} - is there a NUL in the first 8000 bytes?")
print("   Strict UTF-8 refuses at the first byte. 'replace' keeps going and")
print("   keeps nothing. The three 8-bit tables each find three characters")
print("   and disagree about which. git's rule never decodes anything at all.")
print("   Latin-1 maps all 256 byte values to characters, so under Latin-1")
print("   no file can fail to decode - which is exactly why it cannot tell you")
print("   that a file is binary.")

print()
print("2. WHY UTF-8 SAYS NO - A DIFFERENT REASON FOR EACH BYTE")
print("   byte  bits      leading 1s  verdict")
for i, b in enumerate(DATA):
    lead = 0
    while lead < 8 and b & (0x80 >> lead):
        lead += 1
    if lead == 0:
        verdict = "ASCII - valid on its own"
    elif lead == 1:
        verdict = "a continuation byte - it cannot start a sequence"
    elif lead > 4:
        verdict = "never valid - no sequence starts with more than four 1s"
    elif lead == 2 and (b & 0x1F) < 2:
        top = ((b & 0x1F) << 6) | 0x3F
        verdict = f"overlong - it could only spell U+0000..U+{top:04X}"
    else:
        need, have, j = lead - 1, 0, i + 1
        while j < len(DATA) and have < need and DATA[j] & 0xC0 == 0x80:
            have, j = have + 1, j + 1
        if have == need:
            verdict = f"starts a {lead}-byte sequence, complete"
        elif j == len(DATA):
            verdict = f"truncated - needs {need} continuation bytes, the file ends"
        else:
            verdict = f"broken - needs {need} continuation bytes, byte {j} is not one"
    print(f"   {b:02x}    {b:08b}  {lead:<10}  {verdict}")
print("   Three bytes, three different failures, and 'replace' puts one U+FFFD")
print("   in place of each - the three that section 1 counted. A random byte")
print("   string almost never gets past these rules, which is what makes 'not")
print("   UTF-8' such a strong hint. It is still a hint about one encoding.")

print()
print("3. THE NAME IS A LABEL - THE MODE IS THE DECLARATION")
with tempfile.TemporaryDirectory() as tmp:
    paths = [os.path.join(tmp, n) for n in ("output.bin", "output.txt", "output.dat", "output")]
    for p in paths:
        with open(p, "wb") as f:
            f.write(DATA)
    back = []
    for p in paths:
        with open(p, "rb") as f:
            back.append(f.read())
    print(f"   written under 4 names with 'wb', read back with 'rb': all identical? {all(x == DATA for x in back)}")

    txt = paths[1]                                  # output.txt, the name that most sounds like text
    scratch = os.path.join(tmp, "scratch.txt")

    def read_binary():
        with open(txt, "rb") as f:
            return f.read()

    def read_utf8():
        with open(txt, encoding="utf-8") as f:
            return f.read()

    def read_latin1():
        with open(txt, encoding="latin-1") as f:
            return f.read()

    def write_bytes_in_text_mode():
        with open(scratch, "w", encoding="utf-8") as f:
            f.write(DATA)

    def write_str_in_binary_mode():
        with open(scratch, "wb") as f:
            f.write(DATA.decode("latin-1"))

    for label, call in [
        ("open('output.txt', 'rb').read()", read_binary),
        ("open('output.txt', encoding='utf-8')", read_utf8),
        ("open('output.txt', encoding='latin-1')", read_latin1),
        ("open(..., 'w').write(<bytes>)", write_bytes_in_text_mode),
        ("open(..., 'wb').write(<str>)", write_str_in_binary_mode),
    ]:
        try:
            print(f"   {label:<40} -> {call()!r}")
        except Exception as e:                      # the class is the point, not CPython's sentence
            print(f"   {label:<40} -> {type(e).__name__}")
print("   The file is called output.txt and Python did not care: 'rb' handed")
print("   back bytes, utf-8 refused, latin-1 found three letters, and each")
print("   write failed on a TYPE, never on a name. Every line would read the")
print("   same for output.bin. The b in the mode is what makes a file binary")
print("   to Python; the extension is a note for the next person to read it.")

print()
print("4. A .hex FILE IS USUALLY TEXT THAT DESCRIBES BYTES")


def intel_hex_record(rtype: int, address: int, data: bytes) -> str:
    body = bytes([len(data), address >> 8, address & 0xFF, rtype]) + data
    return ":" + body.hex().upper() + f"{-sum(body) & 0xFF:02X}"


records = [intel_hex_record(0x00, 0x0000, DATA), intel_hex_record(0x01, 0x0000, b"")]
for r, what in zip(records, ["count, address, type 00 (data), the data, checksum", "type 01: end of file"]):
    print(f"   {r:<20} {what}")
hexfile = ("\n".join(records) + "\n").encode("ascii")
try:
    hexfile.decode("utf-8")
    valid = True
except UnicodeDecodeError:
    valid = False
print(f"   {len(hexfile)} bytes, highest byte 0x{max(hexfile):02x}, valid UTF-8: {valid}")
print("   That is Intel HEX, the format most .hex files hold. The same three")
print("   bytes of data, spelled as ASCII with an address and a checksum - so")
print("   every reader in section 1 would call this file text.")
