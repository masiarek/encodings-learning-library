#!/usr/bin/env python3
"""Six properties UTF-8 has and its rivals do not — each one run, not asserted.

UTF-8 did not win because a committee picked it. It won because of six design
decisions, and this program is one demonstration per decision, with the rival
of the day next to it. The seventh section is what it costs, because a fair
comparison has to include the bill.

Run:  python3 why_utf8_won_py.py
"""

import unicodedata

BAR = "-" * 72
MIXED = "id,Łódź,日本語,😀,ok"


def pad(s, width):
    """Left-justify by terminal columns: CJK and emoji are two columns wide."""
    cols = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, width - cols)


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "AN ASCII FILE IS ALREADY A UTF-8 FILE")
plain = "id,name,city"
print(f"   {plain!r}")
print(f"     as ascii : {plain.encode('ascii').hex(' ')}")
print(f"     as utf-8 : {plain.encode('utf_8').hex(' ')}")
print(f"     identical: {plain.encode('ascii') == plain.encode('utf_8')}")
print(f"     as utf-16: {plain.encode('utf_16_be').hex(' ')}")
print("   Every file, tool and protocol that already spoke ASCII kept working")
print("   on the day UTF-8 arrived. Nothing else on this page could say that,")
print("   and that alone is most of the reason it won.")

# ------------------------------------------------------------------ 2
head(2, "NO FRAGMENT OF A CHARACTER CAN EVER LOOK LIKE ASCII")
data = MIXED.encode("utf_8")
low = [b for b in data if b < 0x80]
print(f"   {MIXED!r}")
print(f"     utf-8 : {len(data)} bytes, {len(low)} of them below 0x80")
ascii_chars = "".join(c for c in MIXED if ord(c) < 0x80)
print(f"     those bytes, as characters : {''.join(chr(b) for b in low)!r}")
print(f"     the ASCII characters of the text : {ascii_chars!r}")
print(f"     the same, in the same order: {''.join(chr(b) for b in low) == ascii_chars}")
print("   In UTF-8 a byte below 0x80 is ALWAYS a whole ASCII character, never")
print("   half of something else. So splitting on ',' or '/' cannot go wrong.")
print()
print("   The rival could not promise that. In Shift-JIS the second byte of a")
print("   two-byte character may be any of 0x40..0xFC — which includes ASCII:")
for pair in [b"\x83\x5c", b"\x93\x5c"]:
    print(f"     {pair.hex(' ')} is {pair.decode('shift_jis')!r}, "
          f"and its second byte is {chr(pair[1])!r}")
print("   A path splitter looking for a backslash found one INSIDE a character.")
print("   That is the '5C problem', and it broke Japanese Windows for years.")

# ------------------------------------------------------------------ 3
head(3, "SELF-SYNCHRONISING: YOU CAN START READING ANYWHERE")
print("   Every byte says what it is, from its top bits alone:")
print("     0xxxxxxx  a whole ASCII character")
print("     110xxxxx  start of a 2-byte character   1110xxxx  start of 3")
print("     11110xxx  start of a 4-byte character   10xxxxxx  a CONTINUATION")
print()
word = "Łódź"
b = word.encode("utf_8")
print(f"   {word!r} -> {b.hex(' ')}")
for i, byte in enumerate(b):
    ones = f"{byte:08b}".find("0")          # leading 1s = length of the character
    kind = ("ascii" if byte < 0x80 else
            "continuation" if byte >> 6 == 0b10 else
            f"start of a {ones}-byte character")
    print(f"     byte {i}  0x{byte:02X}  {byte:08b}  {kind}")
print()
print("   So a reader dropped into the middle can find the next character by")
print("   skipping continuation bytes — at most 3 of them:")
for cut in range(len(b)):
    tail = b[cut:]
    skipped = 0
    while skipped < len(tail) and tail[skipped] >> 6 == 0b10:
        skipped += 1
    print(f"     start at byte {cut}: skip {skipped}, then read {tail[skipped:].decode()!r}")
print("   Shift-JIS and EUC-JP cannot be entered in the middle at all: you")
print("   must read from the start of the file to know which byte is which.")
print("   (UTF-16 can, but only once you know where the 2-byte boundaries are,")
print("   and a byte stream does not tell you that either.)")

# ------------------------------------------------------------------ 4
head(4, "SELF-VALIDATING: A WRONG-TABLE FILE CAN BE DETECTED")
latin1_bytes = "café au lait".encode("latin_1")
print(f"   A Latin-1 file : {latin1_bytes.hex(' ')}")
try:
    latin1_bytes.decode("utf_8")
except UnicodeDecodeError as e:
    print(f"     read as utf-8   -> UnicodeDecodeError: {e.reason} at byte {e.start}")
print(f"     read as latin-1 -> {latin1_bytes.decode('latin_1')!r}")
print()
print("   Now the other direction, which is the important one:")
utf8_bytes = "café au lait".encode("utf_8")
print(f"   A UTF-8 file   : {utf8_bytes.hex(' ')}")
print(f"     read as latin-1 -> {utf8_bytes.decode('latin_1')!r}  (no error!)")
print("   Latin-1 maps all 256 bytes, so it can NEVER report a problem. It")
print("   accepts every file and quietly returns the wrong text — which is")
print("   exactly why mojibake was silent for twenty years. UTF-8's structure")
print("   makes most wrong guesses fail loudly, on the first bad byte.")

# ------------------------------------------------------------------ 5
head(5, "NO BYTE ORDER, SO NO BOM AND NO VARIANTS")
s = "Hi"
for enc in ["utf_8", "utf_16_le", "utf_16_be", "utf_16", "utf_32_le", "utf_32"]:
    print(f"   {s!r} in {enc:10} -> {s.encode(enc).hex(' ')}")
print("   UTF-8 has one spelling. UTF-16 and UTF-32 have two each, so they")
print("   need a Byte Order Mark to say which — a magic prefix that then")
print("   leaks into CSV headers, JSON parsers and shell scripts forever.")

# ------------------------------------------------------------------ 6
head(6, "SORTING BY BYTES == SORTING BY CODE POINT")
sample = ["A", "z", "é", "！", "\U00010000", "😀"]


def by(enc):
    return " ".join(f"U+{ord(c):04X}" for c in sorted(sample, key=lambda c: c.encode(enc)))


print(f"   by code point : {' '.join(f'U+{ord(c):04X}' for c in sorted(sample))}")
print(f"   by utf-8 bytes: {by('utf_8')}")
print(f"   by utf-16 byte: {by('utf_16_be')}")
print("   UTF-8's byte order and Unicode's numbering agree, so a sort, a")
print("   binary search or a B-tree index over raw bytes is already correct.")
print("   UTF-16 gets it wrong: surrogates start at D800, so every character")
print("   above U+FFFF sorts BEFORE the ones from E000 to FFFF.")

# ------------------------------------------------------------------ 7
head(7, "WHAT IT COSTS, STATED HONESTLY")
for text, label in [("hello world", "ASCII"), ("Łódź", "Polish"), ("日本語です", "Japanese")]:
    u8, u16 = len(text.encode("utf_8")), len(text.encode("utf_16_le"))
    print(f"   {label:9} {pad(repr(text), 14)} utf-8 {u8:3}   utf-16 {u16:3}   "
          f"{'utf-8 wins' if u8 < u16 else 'utf-16 wins' if u16 < u8 else 'tie'}")
print("   UTF-8 charges 3 bytes for a CJK character where UTF-16 and the old")
print("   Japanese tables charged 2 — a 50% bill on exactly the text that")
print("   needed the most storage. That is a real cost, it was argued about")
print("   loudly, and it lost to the six properties above.")
