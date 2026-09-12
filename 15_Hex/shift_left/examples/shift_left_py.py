#!/usr/bin/env python3
"""Shift Left: X[i] <<= Operand, as 010 Editor's Hex Operations dialog documents it.

Every bit of the value moves toward its top by the operand, zeros come in
at the bottom, and whatever passes the top of the value is gone.

Run:  python3 shift_left_py.py
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


def shift_left(value, operand):
    return value << operand


def main():
    section(1, "THE TOP BIT FALLS OFF")
    print("   81 is 1000 0001. Shift Left, as Unsigned Byte:")
    print()
    for count in (1, 4, 7):
        out = hexop(b"\x81", "Unsigned Byte", shift_left, count)[0]
        print(f"     81 << {count}   {out:02x}   {out:08b}")
    print()
    print("   The low 1 walks up one place per count. The high 1 went past the top")
    print("   on the first step and nothing remembers it.")
    print()

    section(2, "SHIFT LEFT 1 IS MULTIPLY 2, AND ADDING THE VALUE TO ITSELF")
    doubles = all(
        hexop(bytes([v]), "Unsigned Byte", shift_left, 1)
        == hexop(bytes([v]), "Unsigned Byte", lambda x, k: x * 2)
        == hexop(bytes([v]), "Unsigned Byte", lambda x, k: x + x)
        for v in range(256)
    )
    signed_same = all(
        hexop(bytes([v]), "Unsigned Byte", shift_left, k) == hexop(bytes([v]), "Signed Byte", shift_left, k)
        for v in range(256) for k in range(8)
    )
    print(f"     all 256 bytes, the three agree                         {doubles}")
    print(f"     Signed and Unsigned write the same, counts 0-7         {signed_same}")
    print()

    section(3, "ON A LITTLE-ENDIAN SHORT THE BITS CROSS RIGHTWARD ON SCREEN")
    print("   0x1234 << 4 is 0x2340 whichever way the bytes are stored:")
    print()
    for endian, data in (("big", bytes.fromhex("12 34")), ("little", bytes.fromhex("34 12"))):
        out = hexop(data, "Unsigned Short", shift_left, 4, endian)
        print(f"     Unsigned Short, {endian:<6}  {show(data)} -> {show(out)}")
    print()
    print("   In the big-endian row the digits moved left, the way they would on")
    print("   paper. In the little-endian row the high byte is the second one, so")
    print("   the 3 that left the first byte arrived in the second.")
    print()

    section(4, "A SHIFT BY THE WIDTH OR MORE")
    for count in (7, 8, 9):
        out = hexop(b"\x81", "Unsigned Byte", shift_left, count)
        print(f"     81 << {count}   {out.hex()}")
    print()
    print("   This program keeps the low eight bits of the true result, so from 8")
    print("   on every bit has gone. That is Python's arithmetic, not a rule: C")
    print("   leaves a shift by the width or more undefined, Rust's wrapping_shl")
    print("   takes the count modulo the width, and the manual does not say what")
    print("   the dialog does.")


if __name__ == "__main__":
    main()
