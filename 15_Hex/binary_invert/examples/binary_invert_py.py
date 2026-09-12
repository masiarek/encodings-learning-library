#!/usr/bin/env python3
"""Binary Invert: X[i] = ~X[i], as 010 Editor's Hex Operations dialog documents it.

Invert flips every bit and takes no operand. It is the one operation in the
dialog that no setting can change -- not the type, the sign or the order.

Run:  python3 binary_invert_py.py
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


def invert(value, operand):
    return ~value


SETTINGS_2 = [(t, e) for t in ("Unsigned Byte", "Signed Byte", "Unsigned Short", "Signed Short")
              for e in ("little", "big")]
SETTINGS_4 = [(t, e) for t in ("Unsigned Byte", "Unsigned Short", "Unsigned Int", "Signed Int")
              for e in ("little", "big")]


def main():
    section(1, "INVERT FLIPS EVERY BIT")
    cafe = "café".encode()
    flipped = hexop(cafe, "Unsigned Byte", invert)
    print(f"     café         {show(cafe)}")
    print(f"     inverted     {show(flipped)}")
    print(f"     and again    {show(hexop(flipped, 'Unsigned Byte', invert))}")
    print()

    section(2, "INVERT IS XOR FF")
    agree = all(hexop(bytes([v]), "Unsigned Byte", invert)[0] == v ^ 0xFF for v in range(256))
    print(f"     all 256 bytes   {agree}")
    print()
    print("   Xor flips the bits the operand has, and FF has all of them.")
    print()

    section(3, "NO SETTING CAN CHANGE IT")
    twos = all(
        len({hexop(v.to_bytes(2, "big"), t, invert, endian=e) for t, e in SETTINGS_2}) == 1
        for v in range(65536)
    )
    fours = all(
        len({hexop(v.to_bytes(4, "big"), t, invert, endian=e) for t, e in SETTINGS_4}) == 1
        for v in range(0, 1 << 32, 65537)
    )
    print("   Every setting below wrote the same bytes, on every input tried:")
    print()
    print(f"     all 65,536 two-byte inputs; Byte and Short, signed and")
    print(f"     unsigned, little and big                                    {twos}")
    print(f"     65,536 four-byte inputs; Byte, Short and Int, both orders   {fours}")
    print()
    print("   Inverting a value inverts each of its bytes, whichever bytes they")
    print("   are and whatever they mean -- so there is nothing for the type, the")
    print("   sign or the byte order to decide. Every other operation in the list")
    print("   depends on at least one of them.")
    print()

    section(4, "INVERT, THEN ADD 1, IS NEGATE")
    negate = all(
        hexop(hexop(bytes([v]), "Unsigned Byte", invert), "Unsigned Byte", lambda x, k: x + 1)
        == hexop(bytes([v]), "Unsigned Byte", lambda x, k: -x)
        for v in range(256)
    )
    print(f"     all 256 bytes   {negate}")
    print()

    section(5, "READ AS SIGNED, ~X IS -X - 1")
    holds = all(~v == -v - 1 for v in range(-128, 128))
    print(f"     every Signed Byte   {holds}")
    for v in (0, 5, -128):
        out = hexop(struct.pack("b", v), "Signed Byte", invert)
        (read,) = struct.unpack("b", out)
        print(f"     {v:>4} -> {out.hex()} -> {read}")
    print()
    print("   So inverting a Signed Byte never overflows: the most negative value")
    print("   becomes the most positive, and the other way round.")


if __name__ == "__main__":
    main()
