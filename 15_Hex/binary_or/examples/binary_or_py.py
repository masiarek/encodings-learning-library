#!/usr/bin/env python3
"""Binary Or: X[i] |= Operand, as 010 Editor's Hex Operations dialog documents it.

Or sets every bit the operand has and never clears one, which makes it the
mask for adding a bit -- and, since two inputs can reach the same output,
the one operation here whose damage cannot be reversed by another.

Run:  python3 binary_or_py.py
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


def binary_or(value, operand):
    return value | operand


def utf8_or_not(data):
    try:
        return repr(data.decode("utf-8"))
    except UnicodeDecodeError:
        return "not UTF-8"


def main():
    section(1, "OR 20 LOWERCASES ASCII LETTERS, AND A FEW THINGS BESIDES")
    line = b"HI [42]@"
    out = hexop(line, "Unsigned Byte", binary_or, 0x20)
    print("   Bit 5 is the difference between an ASCII capital and its lowercase")
    print("   letter. Set it everywhere:")
    print()
    print(f"     {line!r} -> {out!r}")
    print()
    print("   The space and the digits live in 20-3F, where that bit is already")
    print("   set, so they are untouched -- unlike Subtract 20, which takes 0x20")
    print("   from every byte whether it has the bit or not. [ ] and @ live in")
    print("   40-5F with the capitals, and became { } and `.")
    print()

    section(2, "ON UTF-8, IT BREAKS EVERY TWO-BYTE CHARACTER")
    word = "CAFÉ".encode()
    lowered = hexop(word, "Unsigned Byte", binary_or, 0x20)
    print(f"     before   {show(word)}   {utf8_or_not(word)}")
    print(f"     after    {show(lowered)}   {utf8_or_not(lowered)}")
    leads = range(0xC2, 0xE0)
    moved = [v for v in leads if v | 0x20 != v]
    print()
    print(f"   Two-byte lead bytes, C2-DF, that Or 20 changes: {len(moved)} of {len(leads)},")
    print(f"   every one into E2-FF: {all(0xE2 <= v | 0x20 <= 0xFF for v in moved)}")
    print()
    print("   A lead byte from E0 up announces a character of three bytes or more,")
    print("   so C3 | 20 = E3 tells a decoder to expect two continuation bytes,")
    print("   and the É had only one.")
    print()

    section(3, "OR NEVER CLEARS A BIT, SO IT CANNOT BE UNDONE")
    outputs = {hexop(bytes([v]), "Unsigned Byte", binary_or, 0x20)[0] for v in range(256)}
    print(f"     different bytes Or 20 can write   {len(outputs)} of 256")
    print(f"     41 and 61 both become             {hexop(b'A', 'Unsigned Byte', binary_or, 0x20).hex()}"
          f" and {hexop(b'a', 'Unsigned Byte', binary_or, 0x20).hex()}")
    print()
    print("   Once two bytes have been merged into one, no operation can tell")
    print("   which one it was. And and Or both lose information this way; Xor and")
    print("   Invert never do.")
    print()

    section(4, "OR 80 MOVES EVERY BYTE INTO THE TOP HALF")
    text = b"Hi!"
    high = hexop(text, "Unsigned Byte", binary_or, 0x80)
    print(f"   {text!r} is {show(text)}. Or 0x80:")
    print()
    print(f"     {show(high)}   as Latin-1 {high.decode('latin-1')!r}, and {utf8_or_not(high)}")
    print()
    print("   Every ASCII character lands exactly 0x80 higher, in the half of the")
    print("   byte range where each code page keeps its own letters -- which is")
    print("   why text that has been through Or 80 reads as accented garbage in")
    print("   one table and as nothing at all in UTF-8.")


if __name__ == "__main__":
    main()
