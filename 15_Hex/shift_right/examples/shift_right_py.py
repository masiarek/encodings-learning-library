#!/usr/bin/env python3
"""Shift Right: X[i] >>= Operand, as 010 Editor's Hex Operations dialog documents it.

Every bit moves toward the bottom of the value and falls off the end. The
page's question is what comes in at the top -- and for a signed value C
lets each compiler choose.

Run:  python3 shift_right_py.py
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


def shift_right(value, operand):
    """Python's >>, which copies the sign bit into a negative value."""
    return value >> operand


def shift_right_zeros(value, operand):
    """The other rule for a signed value: shift the bit pattern, zeros in."""
    return (value & 0xFF) >> operand


def c_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def main():
    section(1, "WHAT COMES IN AT THE TOP")
    data = bytes.fromhex("f0 81 7f")
    print(f"   Shift Right {show(data)} by 1 and by 4:")
    print()
    rows = (
        ("Unsigned Byte", "Unsigned Byte", shift_right),
        ("Signed Byte, sign copied in", "Signed Byte", shift_right),
        ("Signed Byte, zeros in", "Signed Byte", shift_right_zeros),
    )
    for label, treat, formula in rows:
        by_1 = show(hexop(data, treat, formula, 1))
        by_4 = show(hexop(data, treat, formula, 4))
        print(f"     {label:<30} >> 1  {by_1}    >> 4  {by_4}")
    print()
    print("   An Unsigned Byte always takes zeros. For a Signed Byte, C says a")
    print("   negative value's >> is implementation-defined; every compiler this")
    print("   library runs copies the sign bit, which is the second row, and the")
    print("   manual does not say which rule the dialog follows. 7F is positive,")
    print("   and all three rows agree on it.")
    print()

    section(2, "SHIFT RIGHT 4 AND AND 0F SPLIT A BYTE INTO ITS HEX DIGITS")
    e_acute = "é".encode()
    high = hexop(e_acute, "Unsigned Byte", shift_right, 4)
    low = hexop(e_acute, "Unsigned Byte", lambda x, k: x & k, 0x0F)
    print(f"     é               {show(e_acute)}")
    print(f"     Shift Right 4   {show(high)}   the left digits")
    print(f"     Binary And 0F   {show(low)}   the right digits")
    print()

    section(3, "SHIFT RIGHT 1 IS NOT DIVIDE 2 ON A NEGATIVE VALUE")
    mismatched = [v for v in range(-128, 128) if (v >> 1) != c_div(v, 2)]
    print("   Copying the sign bit rounds toward minus infinity; C's division")
    print("   rounds toward zero:")
    print()
    for label, value in (
        ("Signed Bytes where they differ", f"{len(mismatched)} of 256"),
        ("every one of them negative and odd", all(v < 0 and v % 2 for v in mismatched)),
        ("-7 >> 1, and -7 / 2", f"{-7 >> 1} and {c_div(-7, 2)}"),
    ):
        print(f"     {label:<36} {value}")
    print()

    section(4, "SHIFT RIGHT 8 MOVES A SHORT'S HIGH BYTE DOWN")
    print("   0x1234 >> 8 is 0x0012, stored both ways:")
    print()
    for endian, pair in (("big", bytes.fromhex("12 34")), ("little", bytes.fromhex("34 12"))):
        out = hexop(pair, "Unsigned Short", shift_right, 8, endian)
        print(f"     Unsigned Short, {endian:<6}  {show(pair)} -> {show(out)}")


if __name__ == "__main__":
    main()
