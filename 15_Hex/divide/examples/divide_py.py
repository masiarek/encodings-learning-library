#!/usr/bin/env python3
"""Divide: X[i] /= Operand, as 010 Editor's Hex Operations dialog documents it.

Divide is the first operation in the list where Signed and Unsigned write
different bytes, and the manual's C notation brings C's rounding with it.

Run:  python3 divide_py.py
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


def c_div(a, b):
    """C's integer division: the quotient rounded toward zero."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def main():
    section(1, "ONE DROPDOWN, TWO QUOTIENTS")
    data = bytes.fromhex("f0 80 ff 7f")
    print(f"   Divide {show(data)} by 2:")
    print()
    for treat in ("Unsigned Byte", "Signed Byte"):
        numbers = ", ".join(str(n) for n in struct.unpack(f"{len(data)}{TREAT_AS[treat]}", data))
        print(f"     {treat:<14} reads {numbers:<20} writes {show(hexop(data, treat, c_div, 2))}")
    differ = [v for v in range(256)
              if hexop(bytes([v]), "Unsigned Byte", c_div, 2) != hexop(bytes([v]), "Signed Byte", c_div, 2)]
    print()
    print(f"   Byte values that divide differently: {len(differ)} of 256,")
    print(f"   and they are exactly 80 to FF: {differ == list(range(0x80, 0x100))}")
    print()
    print("   Those are the bytes the two settings read as different numbers. The")
    print("   first four operations never had to know the number; Divide does.")
    print()

    section(2, "C ROUNDS TOWARD ZERO, AND PYTHON'S // ROUNDS DOWN")
    print("   The manual writes Divide as C's /=, and C drops the fraction, which")
    print("   rounds toward zero. Python's // rounds toward minus infinity. They")
    print("   agree until the quotient is negative:")
    print()
    print(f"     {'a / b':<9} {'C':>3} {'//':>4}   as a Signed Byte, C and //")
    for a, b in ((7, 2), (-7, 2), (7, -2), (-1, 2)):
        label = f"{a} / {b}"
        c_byte = struct.pack("b", c_div(a, b)).hex()
        floor_byte = struct.pack("b", a // b).hex()
        print(f"     {label:<9} {c_div(a, b):>3} {a // b:>4}   {c_byte} and {floor_byte}")
    print()

    section(3, "DIVIDE 2 IS NOT SHIFT RIGHT 1")
    mismatched = [v for v in range(-128, 128) if c_div(v, 2) != v >> 1]
    print("   Shift Right 1 on a negative Signed Byte copies the sign bit in -- on")
    print("   every compiler this library runs -- which rounds toward minus")
    print("   infinity, where Divide rounds toward zero:")
    print()
    print(f"     values where Divide 2 and Shift Right 1 differ   {len(mismatched)} of 256")
    print(f"     every one of them negative and odd               {all(v < 0 and v % 2 for v in mismatched)}")
    print(f"     -7, through Divide 2 and Shift Right 1           {c_div(-7, 2)} and {-7 >> 1}")
    print()

    section(4, "DIVIDE 0")
    try:
        hexop(b"\x10", "Unsigned Byte", c_div, 0)
        outcome = "no error"
    except ZeroDivisionError as exc:
        outcome = type(exc).__name__
    print("   There is no byte to write. This program's answer is Python's:")
    print()
    print(f"     Divide 0 on 10   {outcome}")
    print()
    print("   C leaves integer division by zero undefined, and the manual does not")
    print("   say what the dialog does instead.")
    print()

    section(5, "A FLOAT QUOTIENT IS ROUNDED TO ITS TYPE")
    print("   As Float or Double, Divide is floating-point division. 1 / 3:")
    print()
    for treat in ("Float", "Double"):
        code = "<" + TREAT_AS[treat]
        out = hexop(struct.pack(code, 1.0), treat, lambda x, k: x / k, 3)
        (read,) = struct.unpack(code, out)
        print(f"     {treat:<7} {show(out):<24} reads back {read!r}")
    print()
    print("   Neither is a third. Each is the nearest number its bits can hold,")
    print("   and a Float and a Double are nearest in different places.")


if __name__ == "__main__":
    main()
