#!/usr/bin/env python3
"""Assign: X[i] = Operand, as 010 Editor's Hex Operations dialog documents it.

The simplest formula in the dialog, and the one whose bytes depend most on
the settings beside it: one operand fills one whole value, so Treat Data As
decides how many bytes each copy takes and Endian decides their order.

Run:  python3 assign_py.py
"""

import codecs
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


def assign(value, operand):
    return operand


def main():
    section(1, "ONE OPERAND, FOUR PATTERNS")
    print("   Assign 0x41 over the same eight zero bytes, four ways. The formula")
    print("   is the same every time; how many bytes one copy fills, and in which")
    print("   order, is not.")
    print()
    blank = bytes(8)
    for treat, endian, label in (
        ("Unsigned Byte", "little", "Unsigned Byte"),
        ("Unsigned Short", "little", "Unsigned Short, little"),
        ("Unsigned Short", "big", "Unsigned Short, big"),
        ("Unsigned Int", "little", "Unsigned Int, little"),
    ):
        print(f"     {label:<24} {show(hexop(blank, treat, assign, 0x41, endian))}")
    print()
    as_short = hexop(blank, "Unsigned Short", assign, 0x41, "little")
    print("   The second row is 'A' and a NUL, four times -- which is what")
    print("   UTF-16LE writes for AAAA:")
    print()
    print(f"     .decode('utf-16-le')                {as_short.decode('utf-16-le')!r}")
    print(f"     == 'AAAA'.encode('utf-16-le')       {'AAAA'.encode('utf-16-le') == as_short}")
    print()

    section(2, "ASSIGN FEFF TO ONE SHORT AND YOU HAVE WRITTEN A BOM")
    print("   U+FEFF, the byte order mark, is a 16-bit value. Assign it to the")
    print("   first Unsigned Short of a file and the Endian toggle picks which of")
    print("   the two marks you wrote:")
    print()
    for endian, constant in (("little", "BOM_UTF16_LE"), ("big", "BOM_UTF16_BE")):
        mark = hexop(bytes(2), "Unsigned Short", assign, 0xFEFF, endian)
        print(f"     {endian:<7} {show(mark)}   == codecs.{constant}: {mark == getattr(codecs, constant)}")
    print()

    section(3, "OPERAND STEP BUILDS THE TABLE EVERY CODE PAGE IS DRAWN ON")
    table = hexop(bytes(256), "Unsigned Byte", assign, 0, step=1)
    print("   Assign 0 with Operand Step 1 over 256 bytes writes every byte value")
    print("   once, in order:")
    print()
    print(f"     the first eight   {show(table[:8])}")
    print(f"     the last eight    {show(table[-8:])}")
    print(f"     == bytes(range(256)): {table == bytes(range(256))}")
    print()
    print("   Decode that file one byte at a time and count what each table calls")
    print("   a character:")
    print()
    for codec in ("latin-1", "cp1252", "ascii", "utf-8"):
        refused = []
        for value in table:
            try:
                bytes([value]).decode(codec)
            except UnicodeDecodeError:
                refused.append(value)
        note = f"   refuses {show(bytes(refused))}" if 0 < len(refused) < 8 else ""
        print(f"     {codec:<8} {256 - len(refused):>3} of 256{note}")
    print()

    section(4, "THE TYPE DECIDES THE BYTES, NOT ONLY HOW MANY")
    print("   Type 1 into the Operand box. What reaches the file depends on the")
    print("   type it is written as:")
    print()
    for treat, endian in (("Unsigned Byte", "little"), ("Unsigned Int", "little"),
                          ("Unsigned Int", "big"), ("Float", "little"), ("Double", "little")):
        width = struct.calcsize(TREAT_AS[treat])
        label = treat if treat.endswith("Byte") else f"{treat}, {endian}"
        print(f"     {label:<22} {show(hexop(bytes(width), treat, assign, 1, endian))}")
    print()
    print("   A Float or a Double is not the integer in more bytes. It is the")
    print("   same number in a different notation, and none of its bytes is 01.")
    print()

    section(5, "OPERAND STEP ON A SHORT COUNTS IN CHARACTERS")
    letters = hexop(bytes(8), "Unsigned Short", assign, 0x41, step=1)
    print("   Assign 0x41 with Operand Step 1, as a little-endian Unsigned Short,")
    print("   over eight bytes:")
    print()
    print(f"     {show(letters)}   .decode('utf-16-le') -> {letters.decode('utf-16-le')!r}")


if __name__ == "__main__":
    main()
