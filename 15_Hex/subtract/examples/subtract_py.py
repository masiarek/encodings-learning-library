#!/usr/bin/env python3
"""Subtract: X[i] -= Operand, as 010 Editor's Hex Operations dialog documents it.

Subtraction wraps below zero the way Add wraps above the top, and a borrow
stops at the edge of a value the way a carry does.

Run:  python3 subtract_py.py
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


def subtract(value, operand):
    return value - operand


def add(value, operand):
    return value + operand


def main():
    section(1, "THE SAME BYTES, THREE DIFFERENCES")
    pair = bytes.fromhex("08 01")
    print(f"   Subtract 0x10 from {show(pair)}:")
    print()
    for treat, endian, label, why in (
        ("Unsigned Byte", "little", "Unsigned Byte", "each byte borrows from nowhere"),
        ("Unsigned Short", "little", "Unsigned Short, little", "0108-10 is 00F8"),
        ("Unsigned Short", "big", "Unsigned Short, big", "0801-10 is 07F1"),
    ):
        print(f"     {label:<24} {show(hexop(pair, treat, subtract, 0x10, endian))}   {why}")
    print()

    section(2, "ZERO MINUS ONE IS EVERY BIT SET, IN EVERY TYPE")
    print("   Subtract 1 from zero bytes, then read the result back as the same")
    print("   type:")
    print()
    for treat in ("Unsigned Byte", "Signed Byte", "Unsigned Short", "Signed Int", "Unsigned Int64"):
        letter = TREAT_AS[treat]
        out = hexop(bytes(struct.calcsize(letter)), treat, subtract, 1)
        (value,) = struct.unpack("<" + letter, out)
        print(f"     {treat:<16} {show(out):<25} {value}")
    print()
    print("   The bytes are the same in each signed and unsigned pair. The")
    print("   number is not, and the file only ever holds the bytes.")
    print()

    section(3, "SUBTRACT 1 IS ADD FF")
    bytes_agree = all(
        hexop(bytes([v]), "Unsigned Byte", subtract, 1) == hexop(bytes([v]), "Unsigned Byte", add, 0xFF)
        for v in range(256)
    )
    shorts_agree = all(
        hexop(v.to_bytes(2, "little"), "Unsigned Short", subtract, 1)
        == hexop(v.to_bytes(2, "little"), "Unsigned Short", add, 0xFFFF)
        for v in range(65536)
    )
    print("   Wrapping makes subtraction a special case of addition, which is why")
    print("   a dialog could offer only one of them:")
    print()
    print(f"     Subtract 1 == Add 0xFF,   all 256 Unsigned Bytes        {bytes_agree}")
    print(f"     Subtract 1 == Add 0xFFFF, all 65,536 Unsigned Shorts    {shorts_agree}")
    print()

    section(4, "SUBTRACT 20 ON A LINE OF TEXT")
    line = "café 42".encode()
    out = hexop(line, "Unsigned Byte", subtract, 0x20)
    print("   Lowercase ASCII sits exactly 0x20 above uppercase, so Subtract 0x20")
    print("   as Unsigned Byte uppercases letters -- and does the same arithmetic")
    print("   to every other byte:")
    print()
    print(f"     before  {show(line)}   {line.decode('utf-8')!r}")
    print(f"     after   {show(out)}   {out.decode('utf-8', errors='replace')!r}")
    print()
    print("   The letters came out right. The space became NUL, the digits became")
    print("   control characters, and C3 A9 became A3 89 -- a continuation byte")
    print("   where a lead byte has to be, so the é is two replacement characters.")


if __name__ == "__main__":
    main()
