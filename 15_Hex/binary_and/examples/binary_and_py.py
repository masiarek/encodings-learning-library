#!/usr/bin/env python3
"""Binary And: X[i] &= Operand, as 010 Editor's Hex Operations dialog documents it.

A bit survives an And only if the operand has it too, so the operand is a
mask: each 1 keeps a bit of the file and each 0 clears one.

Run:  python3 binary_and_py.py
"""

import struct
import unicodedata

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


def binary_and(value, operand):
    return value & operand


def main():
    section(1, "AND 7F IS A SEVEN-BIT CHANNEL")
    cafe = "café".encode()
    stripped = hexop(cafe, "Unsigned Byte", binary_and, 0x7F)
    print("   Clear the top bit of every byte, the way a mail relay built for")
    print("   seven-bit ASCII once did:")
    print()
    print(f"     before   {show(cafe)}   {cafe.decode('utf-8')!r}")
    print(f"     after    {show(stripped)}   {stripped.decode('ascii')!r}")
    print()
    print("   C3 A9 lost the bit that marked them as part of a UTF-8 character and")
    print("   became C and ). Nothing in the result says a bit was ever there.")
    print()

    section(2, "AND DF UPPERCASES ASCII, AND SOMETIMES MORE")
    print("   A lowercase ASCII letter is its capital plus 0x20, and DF is every")
    print("   bit except that one. The same mask, over UTF-8:")
    print()
    print(f"     {'word':<6} {'And DF':<22} reads as")
    results = {}
    for word in ("café", "Łódź", "€"):
        out = hexop(word.encode(), "Unsigned Byte", binary_and, 0xDF)
        try:
            results[word] = out.decode("utf-8")
            shown = repr(results[word])
        except UnicodeDecodeError:
            shown = "not UTF-8"
        print(f"     {word:<6} {show(out):<22} {shown}")
    print()
    print("   The non-ASCII letters it changed, by name:")
    print()
    for word, out in results.items():
        for before, after in zip(word, out):
            if ord(before) > 0x7F and before != after:
                print(f"     U+{ord(before):04X} {unicodedata.name(before):<31} -> U+{ord(after):04X} {unicodedata.name(after)}")
    print()
    print("   é and É are 0x20 apart, and so are ó and Ó, and UTF-8 keeps that")
    print("   bit in the continuation byte -- so clearing it capitalised them. ź")
    print("   and its capital are not 0x20 apart, and clearing the same bit made a")
    print("   different letter. € lost a bit its lead byte needed.")
    print()

    section(3, "A WIDER MASK LANDS WHERE THE ENDIAN TOGGLE PUTS IT")
    data = bytes.fromhex("34 12")
    print("   And 0x00FF as Unsigned Short keeps the low byte of the value. Which")
    print("   byte of the file that is depends on the toggle:")
    print()
    for endian in ("little", "big"):
        print(f"     {endian:<7} {show(data)} -> {show(hexop(data, 'Unsigned Short', binary_and, 0x00FF, endian))}")
    print()

    section(4, "AND FF CHANGES NOTHING, AND AND 00 IS ASSIGN 0")
    keeps = all(hexop(bytes([v]), "Unsigned Byte", binary_and, 0xFF)[0] == v for v in range(256))
    zeroes = all(hexop(bytes([v]), "Unsigned Byte", binary_and, 0x00)[0] == 0 for v in range(256))
    signed_same = all(
        hexop(bytes([v]), "Unsigned Byte", binary_and, k) == hexop(bytes([v]), "Signed Byte", binary_and, k)
        for v in range(256) for k in range(128)
    )
    for label, value in (
        ("And FF leaves all 256 bytes alone", keeps),
        ("And 00 writes 00 over all 256", zeroes),
        ("Signed and Unsigned write the same, operands 0-127", signed_same),
    ):
        print(f"     {label:<52} {value}")
    print()
    print("   Every other operand is in between: one bit column kept or cleared")
    print("   per bit of the mask, and no carries, so the sign never enters into it.")


if __name__ == "__main__":
    main()
