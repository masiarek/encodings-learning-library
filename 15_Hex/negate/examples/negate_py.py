#!/usr/bin/env python3
"""Negate: X[i] = -X[i], as 010 Editor's Hex Operations dialog documents it.

Negate takes no operand. On an integer it is two's complement, which is why
it writes the same bytes signed or unsigned; on a float it is one bit.

Run:  python3 negate_py.py
"""

import struct

# The dialog's Treat Data As list, top to bottom, as struct's letter for each.
TREAT_AS = {
    "Signed Byte": "b", "Unsigned Byte": "B",
    "Signed Short": "h", "Unsigned Short": "H",
    "Signed Int": "i", "Unsigned Int": "I",
    "Signed Int64": "q", "Unsigned Int64": "Q",
    "Float": "f", "Double": "d",
}


def hexop(data, treat, formula, operand=0, endian="little", step=0, skip=0):
    """X[i] = formula(X[i], operand) for every value, written back in place."""
    letter = TREAT_AS[treat]
    code = ("<" if endian == "little" else ">") + letter
    width = struct.calcsize(code)
    out = bytearray(data)
    pos = 0
    while pos + width <= len(out):
        (x,) = struct.unpack_from(code, out, pos)
        y = formula(x, operand)
        if letter not in "fd":  # an integer result keeps its low bits
            y &= (1 << 8 * width) - 1
            if letter.islower() and y >> (8 * width - 1):
                y -= 1 << 8 * width
        struct.pack_into(code, out, pos, y)
        operand += step
        pos += width + skip
    return bytes(out)


def show(data):
    return data.hex(" ")


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def negate(value, operand):
    return -value


def invert(value, operand):
    return ~value


def add(value, operand):
    return value + operand


def main():
    section(1, "NEGATE IS INVERT, THEN ADD ONE")
    data = bytes.fromhex("00 01 7f 80 81 ff")
    inverted = hexop(data, "Unsigned Byte", invert)
    print("   As Unsigned Byte, and the two steps that make it:")
    print()
    print(f"     the bytes        {show(data)}")
    print(f"     Binary Invert    {show(inverted)}")
    print(f"     ...then Add 1    {show(hexop(inverted, 'Unsigned Byte', add, 1))}")
    print(f"     Negate           {show(hexop(data, 'Unsigned Byte', negate))}")
    agree = all(
        hexop(bytes([v]), "Unsigned Byte", negate)
        == hexop(hexop(bytes([v]), "Unsigned Byte", invert), "Unsigned Byte", add, 1)
        for v in range(256)
    )
    print()
    print(f"   The same for all 256 bytes: {agree}")
    print()

    section(2, "SIGNED OR UNSIGNED, THE SAME BYTES")
    print("   Negate 01 writes FF either way. The two settings only disagree")
    print("   about what FF is:")
    print()
    for value in (0x01, 0x10, 0x80):
        out = hexop(bytes([value]), "Unsigned Byte", negate)
        (as_unsigned,) = struct.unpack("B", out)
        (as_signed,) = struct.unpack("b", out)
        print(f"     Negate {value:02x} -> {out.hex()}   as Unsigned Byte {as_unsigned:>3}, as Signed Byte {as_signed:>4}")
    same = all(hexop(bytes([v]), "Unsigned Byte", negate) == hexop(bytes([v]), "Signed Byte", negate)
               for v in range(256))
    print()
    print(f"   All 256 bytes, both settings, the same byte written: {same}")
    print("   An Unsigned Byte has no negative numbers, so -1 wraps to 255 --")
    print("   the same wrap as 0 - 1.")
    print()

    section(3, "TWO VALUES ARE THEIR OWN NEGATIVE")
    fixed = bytes(v for v in range(256) if hexop(bytes([v]), "Signed Byte", negate)[0] == v)
    print(f"     bytes Negate leaves alone   {show(fixed)}")
    print()
    print("   00 is zero. 80 is -128, and +128 does not fit in a Signed Byte, so")
    print("   the most negative value is its own negative. Every signed width has")
    print("   one:")
    print()
    for treat in ("Signed Short", "Signed Int"):
        code = "<" + TREAT_AS[treat]
        smallest = struct.pack(code, -(1 << (8 * struct.calcsize(code) - 1)))
        out = hexop(smallest, treat, negate)
        print(f"     {treat:<13} {show(smallest):<12} -> {show(out):<12} unchanged: {out == smallest}")
    print()

    section(4, "NEGATE TWICE GIVES THE FILE BACK")
    twice = all(
        hexop(hexop(v.to_bytes(2, "little"), "Signed Short", negate), "Signed Short", negate)
        == v.to_bytes(2, "little")
        for v in range(65536)
    )
    print(f"     all 65,536 Signed Shorts   {twice}")
    print()

    section(5, "ON A FLOAT, NEGATE CHANGES ONE BIT")
    for number in (1.0, 0.0):
        before = struct.pack("<f", number)
        after = hexop(before, "Float", negate)
        (read,) = struct.unpack("<f", after)
        print(f"     {number!r:<4} {show(before)} -> {show(after)}   reads back {read!r}")
    zero, minus_zero = struct.pack("<f", 0.0), struct.pack("<f", -0.0)
    print()
    print(f"     -0.0 == 0.0 as numbers   {-0.0 == 0.0}")
    print(f"     ...and as bytes          {minus_zero == zero}")
    print()
    print("   A float keeps its sign in a bit of its own, the top bit of the last")
    print("   byte here, so there is no carry and no wrap -- and zero has two")
    print("   spellings that compare equal and are not the same file.")


if __name__ == "__main__":
    main()
