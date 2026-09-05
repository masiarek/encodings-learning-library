#!/usr/bin/env python3
"""Tribit — a deliberately silly 3-bit text encoding, as an executable spec.

Run:  python3 tribit_reference_py.py

This file IS the specification's test oracle. Every table it prints is a test
vector a Rust implementation has to reproduce. Read the page beside it for the
rules in prose; read this for the rules as code.

Four layers, each one thing to implement:

  1. TRIBITSET   our own character set: 64 code points, chosen by us
  2. T3V         a variable-length encoding of a number into 3-bit units
  3. PACK        3-bit units into 8-bit bytes, inside a tiny container
  4. DISPLAY     the same bytes shown as units, bits, nibbles, hex, code points
"""

# --------------------------------------------------------------------------
# 1. TRIBITSET — the code points. A number for every character WE decided on.
# --------------------------------------------------------------------------
# Frequent letters get small numbers on purpose: in T3V, 0..3 cost one unit,
# 4..15 two, 16..63 three. That is the only design idea in this table.
LETTERS = "etaoinshrdlcumwfgypbvkjxqz"          # one common English frequency order
POLISH = "ąćęłńóśźżé"                           # nine Polish letters, and the é of café
PUNCT = ".,!?'-:;()\"€😀"                        # 13 signs; the last two are NOT one byte anywhere

TABLE: dict[int, str] = {0: " "}
TABLE.update({i + 1: c for i, c in enumerate(LETTERS)})         # 1..26
TABLE.update({27 + i: d for i, d in enumerate("0123456789")})   # 27..36
TABLE.update({37 + i: c for i, c in enumerate(POLISH)})         # 37..46
TABLE[47] = "\n"
TABLE.update({48 + i: c for i, c in enumerate(PUNCT)})          # 48..60
CAPS, RESERVED, ESC = 61, 62, 63                                 # three control code points
assert len(TABLE) == 61 and max(TABLE) == 60

CHAR_TO_CP = {c: cp for cp, c in TABLE.items()}


class TribitError(Exception):
    """Every refusal has a name. A Rust port turns these into an enum."""


def text_to_codepoints(text: str) -> list[int]:
    """Text -> Tribitset code points. Uppercase costs a CAPS first; anything
    outside the table costs an ESC followed by its Unicode scalar value."""
    out: list[int] = []
    for ch in text:
        if ch in CHAR_TO_CP:
            out.append(CHAR_TO_CP[ch])
        elif ch.isupper() and ch.lower() in CHAR_TO_CP and ch.lower().isalpha():
            out += [CAPS, CHAR_TO_CP[ch.lower()]]
        else:
            out += [ESC, ord(ch)]          # ord() is a UNICODE code point, up to 0x10FFFF
    return out


def codepoints_to_text(cps: list[int]) -> str:
    out: list[str] = []
    i = 0
    while i < len(cps):
        cp = cps[i]
        if cp == CAPS:
            if i + 1 >= len(cps):
                raise TribitError("CAPS at end of text")
            nxt = cps[i + 1]
            if nxt not in TABLE or not TABLE[nxt].isalpha():
                raise TribitError(f"CAPS before non-letter code point {nxt}")
            out.append(TABLE[nxt].upper())
            i += 2
        elif cp == ESC:
            if i + 1 >= len(cps):
                raise TribitError("ESC at end of text")
            u = cps[i + 1]
            if u > 0x10FFFF or 0xD800 <= u <= 0xDFFF:
                raise TribitError(f"ESC to invalid Unicode scalar {u:#x}")
            out.append(chr(u))
            i += 2
        elif cp == RESERVED:
            raise TribitError("reserved code point 62")
        elif cp in TABLE:
            out.append(TABLE[cp])
            i += 1
        else:
            raise TribitError(f"code point {cp} is not in Tribitset")
    return "".join(out)


# --------------------------------------------------------------------------
# 2. T3V — a number as 3-bit units: [more][2 payload bits], top bits first.
# --------------------------------------------------------------------------
def t3v_encode(n: int) -> list[int]:
    """0..3 -> 1 unit, 4..15 -> 2, 16..63 -> 3, ..., 0x10FFFF -> 11."""
    if n < 0:
        raise TribitError("negative")
    groups = []
    while True:
        groups.append(n & 0b11)
        n >>= 2
        if n == 0:
            break
    groups.reverse()                                   # most significant group first
    return [(0b100 | g) for g in groups[:-1]] + [groups[-1]]


def t3v_decode(units: list[int], at: int = 0) -> tuple[int, int]:
    """Decode one number starting at `at`; return (value, units consumed).
    Refuses a truncated sequence and an overlong one."""
    n, i = 0, at
    while True:
        if i >= len(units):
            raise TribitError(f"truncated T3V at unit {at}")
        u = units[i]
        if not 0 <= u <= 7:
            raise TribitError(f"unit {u} is not a tribit")
        if i == at and (u & 0b11) == 0 and (u & 0b100):
            raise TribitError(f"overlong T3V at unit {at}")   # a leading 100 adds nothing
        n = (n << 2) | (u & 0b11)
        i += 1
        if not (u & 0b100):
            return n, i - at


def units_encode(cps: list[int]) -> list[int]:
    return [u for cp in cps for u in t3v_encode(cp)]


def units_decode(units: list[int]) -> list[int]:
    out, i = [], 0
    while i < len(units):
        n, used = t3v_decode(units, i)
        out.append(n)
        i += used
    return out


# --------------------------------------------------------------------------
# 3. PACK — units into bytes, MSB first, inside a 3-byte-header container.
# --------------------------------------------------------------------------
MAGIC = b"T3"


def pack(units: list[int]) -> bytes:
    bits = "".join(f"{u:03b}" for u in units)
    pad = (-len(bits)) % 8
    bits += "0" * pad
    payload = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))
    return MAGIC + bytes([pad]) + payload


def unpack(data: bytes) -> list[int]:
    if data[:2] != MAGIC:
        raise TribitError(f"bad magic {data[:2]!r}")
    if len(data) < 3:
        raise TribitError("no pad byte")
    pad = data[2]
    if pad > 7:
        raise TribitError(f"pad count {pad} > 7")
    bits = "".join(f"{b:08b}" for b in data[3:])
    if pad:
        if not data[3:]:
            raise TribitError("pad count with no payload")
        if bits[-pad:] != "0" * pad:
            raise TribitError("pad bits are not zero")
        bits = bits[:-pad]
    if len(bits) % 3:
        raise TribitError(f"{len(bits)} payload bits is not a multiple of 3")
    return [int(bits[i : i + 3], 2) for i in range(0, len(bits), 3)]


def encode(text: str) -> bytes:
    return pack(units_encode(text_to_codepoints(text)))


def decode(data: bytes) -> str:
    return codepoints_to_text(units_decode(unpack(data)))


# --------------------------------------------------------------------------
# 4. DISPLAY — the same thing, several ways.
# --------------------------------------------------------------------------
def group(bits: str, n: int) -> str:
    return " ".join(bits[i : i + n] for i in range(0, len(bits), n))


def show(text: str) -> None:
    cps = text_to_codepoints(text)
    units = units_encode(cps)
    data = encode(text)
    bits = "".join(f"{u:03b}" for u in units)
    print(f"   text        {text!r}")
    print(f"   code points {cps}")
    print(f"   units (oct) {''.join(str(u) for u in units)}".rstrip())
    print(f"   bits by 3   {group(bits, 3)}".rstrip())
    print(f"   bits by 4   {group(bits, 4)}   <- nibbles: the seams no longer line up")
    print(f"   bits by 8   {group(bits, 8)}".rstrip())
    print(f"   packed      {data.hex(' ')}   (T3 magic, pad={data[2]}, then {len(data) - 3} bytes)")
    print(f"   round trip  {decode(data) == text}")
    u8, u16 = len(text.encode('utf-8')), len(text.encode('utf-16-be'))
    print(f"   payload bytes: Tribit {len(data) - 3}   UTF-8 {u8}   UTF-16 {u16}")


def main() -> None:
    print("1. THE TRIBITSET TABLE (our code points)")
    for cp in range(64):
        name = {CAPS: "CAPS  (next letter is uppercase)", RESERVED: "RESERVED (an encoder must refuse it)",
                ESC: "ESC   (next number is a Unicode scalar)"}.get(cp)
        shown = name if name else repr(TABLE[cp])
        cost = len(t3v_encode(cp))
        print(f"   {cp:>2}  {cp:06b}  {cost} unit{'s' if cost > 1 else ' '}  {shown}")
    print()

    print("2. T3V: ONE NUMBER AS UNITS   (unit = [more][2 bits], top group first)")
    for n in (0, 1, 3, 4, 5, 15, 16, 63, 64, 255, 256, 0xE9, 0x20AC, 0xFFFF, 0x10000, 0x1F600, 0x10FFFF):
        us = t3v_encode(n)
        print(f"   {n:>8} = {n:#8x}  ->  {''.join(str(u) for u in us):<11} ({len(us):>2} {'units' if len(us) > 1 else 'unit '})  {group(''.join(f'{u:03b}' for u in us), 3)}")
    print()

    print("3. T3V DECODER REFUSALS")
    for label, units in (("truncated", [5]), ("truncated", [5, 6]), ("overlong 0", [4, 0]),
                         ("overlong 1", [4, 1]), ("not a tribit", [8])):
        try:
            t3v_decode(units)
            print(f"   {label:<13} {units}  -> accepted (BUG)")
        except TribitError as e:
            print(f"   {label:<13} {units}  -> {e}")
    print("   (44 0 = 100 100 000 -> 0 is overlong too: the check is on the FIRST unit only,")
    print("    because a later 100 carries two real zero bits.)")
    print()

    print("4. TEXT, END TO END")
    for text in ("", "e", "a", "café", "Hello, World!", "Zażółć gęślą jaźń", "€", "😀", "é", "AB", "ü", "\t"):
        show(text)
        print()

    print("5. UNPACK REFUSALS")
    for label, data in (("bad magic", b"X3\x00"), ("pad > 7", b"T3\x08\x00"), ("pad, no payload", b"T3\x02"),
                        ("pad bits set", b"T3\x02\x03"), ("bits not /3", b"T3\x00\x00")):
        try:
            unpack(data)
            print(f"   {label:<16} {data.hex(' '):<14} -> accepted (BUG)")
        except TribitError as e:
            print(f"   {label:<16} {data.hex(' '):<14} -> {e}")
    print()

    print("6. CODE POINT REFUSALS")
    for label, cps in (("CAPS at end", [CAPS]), ("CAPS before digit", [CAPS, 27]), ("ESC at end", [ESC]),
                       ("ESC to surrogate", [ESC, 0xD800]), ("ESC past Unicode", [ESC, 0x110000]), ("reserved", [RESERVED])):
        try:
            codepoints_to_text(cps)
            print(f"   {label:<18} {cps}  -> accepted (BUG)")
        except TribitError as e:
            print(f"   {label:<18} {cps}  -> {e}")
    print()

    print("7. THE SAME TEXT UNDER THREE CODE-POINT ASSIGNMENTS, ONE ENCODING")
    print("   Tribit  = T3V over OUR code points;  T3U = T3V over UNICODE code points (no table)")
    print(f"   {'text':<20} {'Tribit':>7} {'T3U':>5} {'UTF-8':>6} {'UTF-16':>7}   (payload bytes)")
    for text in ("e", "the", "café", "Hello, World!", "Zażółć gęślą jaźń", "😀"):
        t3 = len(encode(text)) - 3
        t3u = len(pack([u for ch in text for u in t3v_encode(ord(ch))])) - 3
        print(f"   {text!r:<20} {t3:>7} {t3u:>5} {len(text.encode('utf-8')):>6} {len(text.encode('utf-16-be')):>7}")
    print("   Same encoding, different numbering: the table is where the bytes were saved or spent.")


if __name__ == "__main__":
    main()
