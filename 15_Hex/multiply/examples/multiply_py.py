#!/usr/bin/env python3
"""Multiply: X[i] *= Operand, as 010 Editor's Hex Operations dialog documents it.

A product is usually wider than either factor, so Multiply is the operation
that throws away the most: everything above the width of the value.

Run:  python3 multiply_py.py
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


def multiply(value, operand):
    return value * operand


def c_div(a, b):
    """C's integer division, which rounds toward zero."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def byte_op(value, formula, operand, treat="Unsigned Byte"):
    return hexop(bytes([value]), treat, formula, operand)[0]


def main():
    section(1, "THE PRODUCT KEEPS ITS LOW BITS")
    print("   F0 x 2 is 480 as an Unsigned Byte and -32 as a Signed one. Both")
    print("   answers end in the same eight bits:")
    print()
    for treat in ("Unsigned Byte", "Signed Byte"):
        print(f"     {treat:<14} {show(hexop(b'\xf0', treat, multiply, 2))}")
    same = sum(
        byte_op(v, multiply, k) == byte_op(v, multiply, k, "Signed Byte")
        for v in range(256) for k in range(128)
    )
    print()
    print(f"   Every byte, every operand 0-127: the same byte {same:,} times of {256 * 128:,}.")
    print()

    section(2, "MULTIPLY 2 IS SHIFT LEFT 1, AND IT LOSES THE TOP BIT")
    agree = all(byte_op(v, multiply, 2) == byte_op(v, lambda x, k: x << k, 1) for v in range(256))
    outputs = {byte_op(v, multiply, 2) for v in range(256)}
    print(f"     Multiply 2 == Shift Left 1, all 256 bytes          {agree}")
    print(f"     different bytes Multiply 2 can write               {len(outputs)} of 256")
    print(f"     00 x 2 and 80 x 2                                  "
          f"{byte_op(0x00, multiply, 2):02x} and {byte_op(0x80, multiply, 2):02x}")
    print()
    print("   Half the byte values can never come out of a Multiply 2, and every")
    print("   one that does came from two different inputs.")
    print()

    section(3, "MULTIPLY 3 IS UNDONE BY MULTIPLY 171, NOT BY DIVIDE 3")
    by_171 = [v for v in range(256) if byte_op(byte_op(v, multiply, 3), multiply, 171) == v]
    by_div = [v for v in range(256) if byte_op(byte_op(v, multiply, 3), c_div, 3) == v]
    never_wrapped = [v for v in range(256) if v * 3 < 256]
    print("   Multiply every byte by 3, then try to get the file back:")
    print()
    print(f"     then Multiply 171 (AB)   restores {len(by_171):>3} of 256")
    print(f"     then Divide 3            restores {len(by_div):>3} of 256, bytes {by_div[0]:02x}-{by_div[-1]:02x}")
    print(f"     ...which are the bytes whose product never wrapped: {by_div == never_wrapped}")
    print()
    print(f"   3 x 171 is {3 * 171}, which is 2 x 256 + {3 * 171 % 256}: within eight bits, 1. So")
    print("   Multiply 171 undoes Multiply 3 on every byte, and Divide 3 only on")
    print("   the ones that did not overflow.")
    print()
    undoable = [m for m in range(256) if any(m * n % 256 == 1 for n in range(256))]
    print(f"   Multipliers with a partner like 171: {len(undoable)} of 256, all of them odd:")
    print(f"   {all(m % 2 for m in undoable)}. An even multiplier clears the low bit and loses the top one.")
    print()

    section(4, "MULTIPLY 256 MOVES A WHOLE BYTE")
    print("   0x1234 x 256 is 0x123400, and a Short keeps 0x3400:")
    print()
    print(f"     Unsigned Short, little   34 12 -> {show(hexop(bytes.fromhex('34 12'), 'Unsigned Short', multiply, 256))}")
    print(f"     Unsigned Short, big      12 34 -> {show(hexop(bytes.fromhex('12 34'), 'Unsigned Short', multiply, 256, 'big'))}")
    print()
    print("   The same byte moved to the high end of the value both times. On")
    print("   screen, that is rightward in one row and leftward in the other.")
    print()

    section(5, "A FLOAT DOUBLES IN ITS EXPONENT")
    print("   As Float, Multiply 2 is floating-point multiplication. Nothing wraps")
    print("   and nothing is kept low; the exponent field goes up by one:")
    print()
    for number in (1.0, 3.0, 0.1):
        before = struct.pack("<f", number)
        after = hexop(before, "Float", multiply, 2)
        (read,) = struct.unpack("<f", after)
        print(f"     {number:<4} {show(before)} -> {show(after)}   reads back {read}")


if __name__ == "__main__":
    main()
