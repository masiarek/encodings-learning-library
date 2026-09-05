#!/usr/bin/env python3
"""Why one character has exactly one legal spelling in UTF-8.

Takes the closing brace from Bob Steagall's slide, pads it into the two-,
three- and four-byte templates, and asks Python about each one. Then writes
the decoder everybody writes by hand -- the one missing the shortest-form
check -- and walks a byte filter straight past with it.
"""


def spell(cp: int, nbytes: int) -> bytes:
    """Write cp into exactly nbytes using the UTF-8 templates. Legal or not."""
    if nbytes == 1:
        return bytes([cp])
    lead_marker = {2: 0b110, 3: 0b1110, 4: 0b11110}[nbytes]
    lead_payload = {2: 5, 3: 4, 4: 3}[nbytes]
    bits = format(cp, "0%db" % (lead_payload + 6 * (nbytes - 1)))
    out = [(lead_marker << lead_payload) | int(bits[:lead_payload], 2)]
    for i in range(nbytes - 1):
        chunk = bits[lead_payload + 6 * i : lead_payload + 6 * (i + 1)]
        out.append(0b10000000 | int(chunk, 2))
    return bytes(out)


def as_bits(bs: bytes) -> str:
    return " ".join(format(b, "08b") for b in bs)


def as_hex(bs: bytes) -> str:
    return " ".join(format(b, "02X") for b in bs)


BRACE = 0x7D
FORMS = [spell(BRACE, n) for n in (1, 2, 3, 4)]

print("1. ONE CHARACTER, FOUR SPELLINGS")
print("   The closing brace }  is U+007D, binary 0111 1101 -- seven payload bits.")
print("   Every template below carries those same seven bits. Only the padding grows.")
for n, form in zip((1, 2, 3, 4), FORMS):
    print(f"   {n} byte{'s' if n > 1 else ' '}:  {as_hex(form):<12}  {as_bits(form)}")
print("   The two-byte row is the slide's 0xC1 0xBD; the three-byte row is 0xE0 0x81 0xBD.")

print()
print("2. WHAT PYTHON SAYS ABOUT EACH")
for form in FORMS:
    try:
        print(f"   {as_hex(form):<12} -> {form.decode('utf-8')!r}")
    except UnicodeDecodeError as e:
        print(f"   {as_hex(form):<12} -> UnicodeDecodeError: {e.reason}, "
              f"bytes {e.start}..{e.end}")
print("   Only the shortest spelling is UTF-8. The other three are ill-formed --")
print("   not because the bits are wrong, but because a second spelling is not allowed.")
print("   Note WHERE each one dies: 0xC1 can only ever start an overlong form, so it is")
print("   refused as a start byte with no second byte read. 0xE0 and 0xF0 are legal start")
print("   bytes, so those two survive one byte longer and die on the byte after.")

print()
print("3. THE DECODER EVERYBODY WRITES BY HAND")


def naive_decode(bs: bytes) -> str:
    """Textbook UTF-8, straight off the template table. No shortest-form check."""
    i, out = 0, []
    while i < len(bs):
        b = bs[i]
        if b < 0x80:
            length, cp = 1, b
        elif b >> 5 == 0b110:
            length, cp = 2, b & 0b11111
        elif b >> 4 == 0b1110:
            length, cp = 3, b & 0b1111
        else:
            length, cp = 4, b & 0b111
        for k in range(1, length):
            cp = (cp << 6) | (bs[i + k] & 0b111111)
        out.append(chr(cp))
        i += length
    return "".join(out)


for form in FORMS:
    print(f"   naive_decode({as_hex(form)})".ljust(33) + f" = {naive_decode(form)!r}")
print("   Every bit handled correctly, every template read right -- and it takes all four.")
print("   That is the bug. It is not a typo -- it is the check nobody thought to add.")

print()
print("4. WALKING A FILTER PAST THE GATE")
payload = b"name" + spell(BRACE, 2) + b"drop"
literal = b"name" + spell(BRACE, 1) + b"drop"


def blocked(raw: bytes) -> bool:
    """A filter that scans BYTES for the forbidden character."""
    return b"}" in raw


for label, raw in (("plain  }", literal), ("overlong", payload)):
    verdict = "BLOCKED" if blocked(raw) else "allowed"
    print(f"   {label}  {as_hex(raw):<30} filter says: {verdict}")
print(f"   ...and then the sloppy decoder runs: {naive_decode(payload)!r}")
print("   The filter looked at bytes, the decoder produced characters, and the two")
print("   disagreed about what the input said. That gap is the whole attack.")
print("   RFC 3629 section 10 tells this story with '/' and a 2001 web-server worm.")

print()
print("5. THIRTEEN BYTES THAT CANNOT APPEAR IN UTF-8 AT ALL")
used = set()
for cp in range(0x110000):
    if 0xD800 <= cp <= 0xDFFF:
        continue
    used.update(chr(cp).encode("utf-8"))
never = sorted(set(range(256)) - used)
print(f"   {' '.join(format(b, '02X') for b in never)}")
print(f"   {len(never)} of 256, found by encoding every code point Unicode has and")
print("   collecting the bytes that never came out.")
print("   0xC0 and 0xC1 are missing because the only code points they could lead are")
print("   ones that fit in a single byte -- so they are overlong by construction.")
print("   0xF5 and up are missing because they lead past U+10FFFF, the top of Unicode.")
