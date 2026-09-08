#!/usr/bin/env python3
"""UTF-8 by hand: the four templates, five characters, and the table by exhaustion.

Nothing here calls .encode('utf-8') to GET an answer. The encoder below is the
pencil method written out -- choose the template, shift the payload bits into
its slots -- and CPython's codec appears only as the second opinion every
answer is checked against, which is the honest role for a library on a page
about doing the thing yourself.

Section 5 is the claim this page rests on. Table 3-7 of the Unicode standard is
normally quoted; here every scalar value Unicode can hold is encoded and placed
in the row whose code point range contains it, all 1,112,064 of them, and the
bytes are checked against that row's byte columns. That is arithmetic over the
number line, so unlike a character's name or a count of assigned code points it
does not depend on which Unicode version this machine's Python was built
against -- and it cannot go stale.
"""

# ---------------------------------------------------------------- the templates
#
# width, the lead byte's marker bits, how many payload bits fit, and the code
# point range that is REQUIRED to use this width (the shortest-form rule).
TEMPLATES = [
    (1, "0",     7,  0x0000,  0x007F),
    (2, "110",   11, 0x0080,  0x07FF),
    (3, "1110",  16, 0x0800,  0xFFFF),
    (4, "11110", 21, 0x10000, 0x10FFFF),
]

# Table 3-7, "Well-Formed UTF-8 Byte Sequences". Nine rows: a code point range,
# then one inclusive byte range per position. Typed out once, checked in full.
TABLE_3_7 = [
    (0x0000,   0x007F,   [(0x00, 0x7F)]),
    (0x0080,   0x07FF,   [(0xC2, 0xDF), (0x80, 0xBF)]),
    (0x0800,   0x0FFF,   [(0xE0, 0xE0), (0xA0, 0xBF), (0x80, 0xBF)]),
    (0x1000,   0xCFFF,   [(0xE1, 0xEC), (0x80, 0xBF), (0x80, 0xBF)]),
    (0xD000,   0xD7FF,   [(0xED, 0xED), (0x80, 0x9F), (0x80, 0xBF)]),
    (0xE000,   0xFFFF,   [(0xEE, 0xEF), (0x80, 0xBF), (0x80, 0xBF)]),
    (0x10000,  0x3FFFF,  [(0xF0, 0xF0), (0x90, 0xBF), (0x80, 0xBF), (0x80, 0xBF)]),
    (0x40000,  0xFFFFF,  [(0xF1, 0xF3), (0x80, 0xBF), (0x80, 0xBF), (0x80, 0xBF)]),
    (0x100000, 0x10FFFF, [(0xF4, 0xF4), (0x80, 0x8F), (0x80, 0xBF), (0x80, 0xBF)]),
]

SURROGATES = range(0xD800, 0xE000)      # 2,048 numbers that are not characters
LEAD_MARKER = {1: 0x00, 2: 0xC0, 3: 0xE0, 4: 0xF0}
LEAD_PAYLOAD_MASK = {1: 0x7F, 2: 0x1F, 3: 0x0F, 4: 0x07}


def width_for(cp: int) -> int:
    """The pencil rule: the narrowest template whose payload slots hold the number."""
    for width, _marker, payload_bits, _lo, _hi in TEMPLATES:
        if cp < (1 << payload_bits):
            return width
    raise ValueError(f"U+{cp:04X} is above U+10FFFF")


def encode_by_hand(cp: int) -> bytes:
    """Shift the payload bits into the template's slots. No codec involved."""
    width = width_for(cp)
    if width == 1:
        return bytes([cp])
    tail = [0x80 | ((cp >> (6 * i)) & 0x3F) for i in range(width - 2, -1, -1)]
    return bytes([LEAD_MARKER[width] | (cp >> (6 * (width - 1)))] + tail)


def decode_by_hand(raw: bytes) -> int:
    """Read the lead byte's marker for the width, strip every marker, concatenate."""
    lead = raw[0]
    width = 1 if lead < 0x80 else 2 if lead < 0xE0 else 3 if lead < 0xF0 else 4
    cp = lead & LEAD_PAYLOAD_MASK[width]
    for byte in raw[1:width]:
        cp = (cp << 6) | (byte & 0x3F)
    return cp


def payload_pieces(cp: int, width: int) -> list[str]:
    """The payload bits, cut at the template's slot boundaries."""
    padded = format(cp, f"0{TEMPLATES[width - 1][2]}b")
    if width == 1:
        return [padded]
    head = len(padded) - 6 * (width - 1)
    return [padded[:head]] + [padded[head + 6 * i: head + 6 * (i + 1)]
                              for i in range(width - 1)]


def hexes(raw: bytes) -> str:
    return " ".join(f"{b:02X}" for b in raw)


def bits(raw: bytes) -> str:
    return " ".join(f"{b:08b}" for b in raw)


def cp_label(cp: int) -> str:
    return f"U+{cp:04X}"


# ------------------------------------------------------------------ section 1
print("1. THE FOUR TEMPLATES")
print("   An x is a payload bit. Every other bit is a marker, and it announces")
print("   one of two things: how long this character is, or that this byte is")
print("   the continuation of one.")
print()
print("   bytes  template                              payload  code points")
for width, marker, payload_bits, lo, hi in TEMPLATES:
    shape = " ".join([marker + "x" * (8 - len(marker))] + ["10xxxxxx"] * (width - 1))
    print(f"   {width}      {shape:<38}{payload_bits:>2} bits  "
          f"{cp_label(lo)} - {cp_label(hi)}")
print()
print("   Two rules do all the work. A byte starting 0 is a whole character by")
print("   itself, so all 128 ASCII bytes mean in UTF-8 exactly what they meant")
print("   in ASCII. And a byte starting 10 is never a lead byte, only ever the")
print("   continuation of one -- which is what makes a UTF-8 stream readable")
print("   from any position, and is why the shell example can cut one in half")
print("   and still find its footing.")
print()

# ------------------------------------------------------------------ section 2
CAST = [
    ("A",           0x0041, "ASCII: one byte, and the byte is unchanged"),
    ("é",      0x00E9, "the number fits in a byte; the character needs two"),
    ("ż",      0x017C, "Polish: past U+00FF, so no 8-bit table can hold it"),
    ("€",      0x20AC, "three bytes -- 16 slots for a 14-bit number"),
    ("\U0001F600",  0x1F600, "above U+FFFF: the four-byte row, 17 bits in 21 slots"),
]

print("2. FIVE CHARACTERS, DONE WITH A PENCIL")
print("   Write the number in binary. Pad it to the payload width of the")
print("   narrowest template that fits. Cut it at the slot boundaries. Put the")
print("   markers back in front. Read off the hex.")
for char, cp, why in CAST:
    width = width_for(cp)
    payload_bits = TEMPLATES[width - 1][2]
    raw = encode_by_hand(cp)
    agrees = "agrees" if raw == char.encode("utf-8") else "DISAGREES"
    print()
    print(f"   {char}   {cp_label(cp)}   {why}")
    rows = [
        ("the number in binary", format(cp, "b")),
        (f"padded to {payload_bits} payload slots", format(cp, f"0{payload_bits}b")),
        ("cut at the slot boundaries", " ".join(payload_pieces(cp, width))),
        ("markers put back in front", bits(raw)),
        ("the bytes", hexes(raw)),
        ("CPython's own codec", f"{hexes(char.encode('utf-8'))}   {agrees}"),
    ]
    for label, value in rows:
        print(f"      {label:<28}{value}")
print()
print("   The second character is the one to sit with. U+00E9 is 233, which fits")
print("   in a byte with room to spare -- and it still takes two bytes, because")
print("   the one-byte template has seven payload slots and 233 needs eight.")
print("   'Does the number fit in a byte' is not the question UTF-8 asks.")
print()

# ------------------------------------------------------------------ section 3
print("3. WHERE THE THRESHOLDS COME FROM")
print("   0x80, 0x800 and 0x10000 are not conventions to memorise. Each is two")
print("   raised to a template's payload width: the first number that template")
print("   can no longer hold, which is where the next one starts.")
print()
for width, _marker, payload_bits, lo, hi in TEMPLATES:
    noun = "byte " if width == 1 else "bytes"
    print(f"   {payload_bits:>2} payload slots reach {cp_label((1 << payload_bits) - 1):<9}"
          f"-> {width} {noun} covers {cp_label(lo)} - {cp_label(hi)}")
print()
above = 0x1FFFFF - 0x10FFFF
print(f"   Only the last row stops early. Its 21 slots reach U+1FFFFF, and UTF-8")
print(f"   stops at U+10FFFF, so {above} of the numbers it could express name")
print("   nothing. That ceiling is not this table's -- it is the largest number")
print("   UTF-16 can reach, and the arithmetic says so exactly:")
print(f"      0x10000 + 2**20 - 1 = 0x{0x10000 + (1 << 20) - 1:X}"
      f"   (a surrogate pair carries 20 bits)")
print()

# ------------------------------------------------------------------ section 4
print("4. DECODING IS THE SAME TABLE READ BACKWARDS")
print("   Count the leading 1s of the first byte: none means one byte, two means")
print("   two, three means three, four means four. Strip every marker, join what")
print("   is left, and that is the number.")
print()
for _char, cp, _why in CAST:
    raw = encode_by_hand(cp)
    joined = "".join(payload_pieces(cp, len(raw)))
    back = decode_by_hand(raw)
    print(f"   {hexes(raw):<13} payload {joined:<22} = {cp_label(back):<8}"
          f" {'ok' if back == cp else 'WRONG'}")
print()
print("   The width came out of the first byte alone. Nothing had to be counted")
print("   ahead, and nothing had to be remembered from earlier in the stream.")
print()

# ------------------------------------------------------------------ section 5
print("5. TABLE 3-7, CHECKED BY EXHAUSTION -- THE CODE POINT SIDE")
print("   Every scalar value Unicode can hold, encoded by the pencil method in")
print("   section 2, placed in the one row whose code point range contains it,")
print("   then checked byte by byte against that row's byte columns.")
print()
print("   code points            the row's byte columns                   scalars")
grand_total = 0
for lo, hi, cols in TABLE_3_7:
    checked = 0
    for cp in range(lo, hi + 1):
        if cp in SURROGATES:
            continue
        raw = encode_by_hand(cp)
        assert len(raw) == len(cols), f"U+{cp:04X}: {len(raw)} bytes in a {len(cols)}-byte row"
        for byte, (blo, bhi) in zip(raw, cols):
            assert blo <= byte <= bhi, f"U+{cp:04X} -> {hexes(raw)} outside its row"
        assert raw == chr(cp).encode("utf-8"), f"U+{cp:04X}: CPython disagrees"
        checked += 1
    grand_total += checked
    span = f"{cp_label(lo)} - {cp_label(hi)}"
    print(f"   {span:<22} {' '.join(f'{a:02X}-{z:02X}' for a, z in cols):<40}"
          f"{checked:>7}")
print()
print(f"   {grand_total} scalar values, every one encoding to bytes that lie")
print("   inside the row claiming it. None fell outside all nine rows, none")
print("   matched two, and CPython's codec agreed on every answer.")
print()

# ------------------------------------------------------------------ section 6
print("6. THE HOLE IN THE MIDDLE IS THE SURROGATES")
print("   Rows five and six are neighbours in the table and their code point")
print("   ranges are not neighbours. Nothing was left out: the gap is what the")
print("   ED row's second byte, capped at 9F where every other row reaches BF,")
print("   is for.")
print()
print(f"   row 5 (ED 80-9F ..) ends at    {cp_label(0xD7FF)}")
print(f"   row 6 (EE-EF ..) begins at     {cp_label(0xE000)}")
print(f"   the gap                        U+D800 - U+DFFF")
print(f"                                  {len(SURROGATES)} numbers that are not characters")
print()
print(f"   0x110000 - {len(SURROGATES)} = {0x110000 - len(SURROGATES)}, which is the total in section 5.")
print("   Two ways of counting one set: subtract the hole from the ceiling, or")
print("   add up nine rows of a byte table. They have to agree, and they do.")
print()

# ------------------------------------------------------------------ section 7
print("7. WHAT A CHARACTER COSTS, AND WHY BYTES >= CHARACTERS ALWAYS")
print("   A template row is a range of code points, so the byte cost of a letter")
print("   is settled by where its script sits on the number line. The library's")
print("   whole cast, sorted into the four rows:")
print()
CAST_CHARS = sorted([("A", 0x0041), ("~", 0x007E), ("é", 0x00E9), ("ß", 0x00DF),
                     ("ż", 0x017C), ("ಠ", 0x0CA0), ("€", 0x20AC),
                     ("日", 0x65E5), ("\U0001F600", 0x1F600)], key=lambda m: m[1])
for width, _marker, _bits, lo, hi in TEMPLATES:
    members = [f"{c} {cp_label(cp)}" for c, cp in CAST_CHARS if width_for(cp) == width]
    noun = "byte " if width == 1 else "bytes"
    span = f"{cp_label(lo)} - {cp_label(hi)}"
    print(f"   {width} {noun}  {span:<20}{'  '.join(members)}")
print()
print("   And the cast's strings, measured rather than described:")
print()
print("   code points   bytes   what costs what")
for text, note in [
    ("Hello, World!", "ASCII only: the two rulers agree"),
    ("café", "one two-byte letter"),
    ("żółw", "Polish: three of four letters cost two"),
    ("日本語", "CJK: three bytes each"),
    ("\U0001F600", "one emoji, and the widest row there is"),
]:
    raw = text.encode("utf-8")
    print(f"   {len(text):>11}   {len(raw):>5}   {note:<38} {text}")
print()
print("   len(bytes) >= len(str), always, and never the other way, because the")
print("   narrowest template is one byte wide. The two are equal exactly when")
print("   every character is ASCII -- which is the whole compatibility story in")
print("   one sentence, and the reason an ASCII file is already a UTF-8 file.")
