#!/usr/bin/env python3
"""Add: X[i] += Operand, as 010 Editor's Hex Operations dialog documents it.

Addition is where the width of a value first shows: a carry has to go
somewhere, and it can only go as far as the edge of the value it started in.

Run:  python3 add_py.py
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


def add(value, operand):
    return value + operand


def main():
    section(1, "THE SAME BYTES, THREE SUMS")
    pair = bytes.fromhex("f8 00")
    print(f"   Add 0x10 to {show(pair)}:")
    print()
    for treat, endian, label, why in (
        ("Unsigned Byte", "little", "Unsigned Byte", "F8+10 is 108, and a byte keeps 08"),
        ("Unsigned Short", "little", "Unsigned Short, little", "00F8+10 is 0108: the 1 carries"),
        ("Unsigned Short", "big", "Unsigned Short, big", "F800+10 is F810: nothing carries"),
    ):
        print(f"     {label:<24} {show(hexop(pair, treat, add, 0x10, endian))}   {why}")
    print()

    section(2, "THE CARRY NEVER REACHES THE NEXT VALUE")
    four = bytes.fromhex("f8 ff 00 00")
    print(f"   Add 0x10 to {show(four)}, little-endian, as two Shorts and as one Int:")
    print()
    print(f"     Unsigned Short   {show(hexop(four, 'Unsigned Short', add, 0x10))}   FFF8+10 keeps 0008; the next Short gets its own 10")
    print(f"     Unsigned Int     {show(hexop(four, 'Unsigned Int', add, 0x10))}   0000FFF8+10 is 00010008")
    print()
    print("   One setting, one byte apart, and the 1 that the Int kept in its")
    print("   third byte is simply gone from the Short.")
    print()

    section(3, "SIGNED OR UNSIGNED, THE SAME BYTES")
    same = sum(
        hexop(bytes([v]), "Unsigned Byte", add, k) == hexop(bytes([v]), "Signed Byte", add, k)
        for v in range(256) for k in range(128)
    )
    print("   Every byte value, every operand from 0 to 127, both settings:")
    print()
    print(f"     wrote the same byte    {same:,} of {256 * 128:,}")
    print()
    top = hexop(b"\x7f", "Unsigned Byte", add, 1)
    (as_unsigned,) = struct.unpack("B", top)
    (as_signed,) = struct.unpack("b", top)
    print(f"   7F + 1 is {show(top)} either way. Read back, that byte is {as_unsigned}")
    print(f"   as an Unsigned Byte and {as_signed} as a Signed one: the bytes agree,")
    print("   and only the number they are read as moved.")
    print()

    section(4, "ADD 13 TO café")
    cafe = "café".encode()
    print(f"   café in UTF-8 is {show(cafe)}. Add to every byte, as Unsigned Byte:")
    print()
    for k in (1, 13, 0x40):
        out = hexop(cafe, "Unsigned Byte", add, k)
        try:
            text = repr(out.decode("utf-8"))
        except UnicodeDecodeError:
            text = "not UTF-8"
        print(f"     + {k:<4}  {show(out):<16} {text}")
    print()
    print("   é is C3 A9: a lead byte from C2-DF and a continuation byte from")
    print("   80-BF. Add 1 or 13 and both stay inside their ranges, so the pair")
    print("   is still one character, just a different one. Add 64 and neither")
    print("   does.")
    print()

    section(5, "OPERAND STEP ADDS A DIFFERENT AMOUNT TO EACH VALUE")
    same_letter = b"AAAA"
    stepped = hexop(same_letter, "Unsigned Byte", add, 0, step=1)
    print("   Add 0 with Operand Step 1 adds 0 to the first value, 1 to the")
    print("   second, and so on:")
    print()
    print(f"     {same_letter!r} -> {stepped!r}")


if __name__ == "__main__":
    main()
