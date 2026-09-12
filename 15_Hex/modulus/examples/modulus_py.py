#!/usr/bin/env python3
"""Modulus: X[i] = X[i] % Operand, as 010 Editor's Hex Operations dialog documents it.

The remainder is the easy half of division, except for its sign: the manual
writes it in C, and C and Python disagree about whose sign it takes.

Run:  python3 modulus_py.py
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


def c_mod(a, b):
    """C's %: the remainder that makes a == b * c_div(a, b) + remainder."""
    return a - b * c_div(a, b)


def main():
    section(1, "MODULUS 16 KEEPS THE LOW HEX DIGIT")
    cafe = "café".encode()
    print(f"   café is {show(cafe)}. Modulus 16, as Unsigned Byte:")
    print()
    print(f"     {show(hexop(cafe, 'Unsigned Byte', c_mod, 16))}")
    same = all(hexop(bytes([v]), "Unsigned Byte", c_mod, 16)[0] == v & 0x0F for v in range(256))
    print()
    print(f"   Modulus 16 == Binary And 0F, all 256 Unsigned Bytes: {same}")
    print("   Sixteen is a power of two, so the remainder is the low four bits,")
    print("   which is the right-hand hex digit.")
    print()

    section(2, "UNTIL THE BYTE IS SIGNED")
    pair = bytes.fromhex("c3 a9")
    numbers = struct.unpack("2b", pair)
    print(f"   {show(pair)} as Signed Byte is {numbers[0]} and {numbers[1]}. Modulus 16 by each language's rule:")
    print()
    c_values = ", ".join(str(c_mod(n, 16)) for n in numbers)
    py_values = ", ".join(str(n % 16) for n in numbers)
    print(f"     C's %        {show(hexop(pair, 'Signed Byte', c_mod, 16))}   {c_values}")
    print(f"     Python's %   {show(hexop(pair, 'Signed Byte', lambda x, k: x % k, 16))}   {py_values}")
    print()
    print("   The manual writes Modulus in C, so the first row is the rule it")
    print("   names, and the low hex digit is no longer what comes out.")
    print()

    section(3, "WHOSE SIGN THE REMAINDER TAKES")
    print(f"     {'a % b':<9} {'C':>3} {'Python':>7}")
    for a, b in ((7, 3), (-7, 3), (7, -3), (-7, -3)):
        label = f"{a} % {b}"
        print(f"     {label:<9} {c_mod(a, b):>3} {a % b:>7}")
    print()
    pairs = [(a, b) for a in range(-128, 128) for b in range(-128, 128) if b]
    c_holds = all(a == b * c_div(a, b) + c_mod(a, b) for a, b in pairs)
    py_holds = all(a == b * (a // b) + a % b for a, b in pairs)
    print("   C's remainder has the sign of a, Python's the sign of b. Neither is")
    print("   wrong: each is the one that fits its own division, over every pair")
    print("   of Signed Bytes:")
    print()
    print(f"     a == b * c_div(a, b) + c_mod(a, b)    {c_holds}")
    print(f"     a == b * (a // b) + a % b             {py_holds}")
    print()

    section(4, "MODULUS 0")
    try:
        hexop(b"\x10", "Unsigned Byte", c_mod, 0)
        outcome = "no error"
    except ZeroDivisionError as exc:
        outcome = type(exc).__name__
    print(f"     Modulus 0 on 10   {outcome}")
    print()
    print("   A remainder after dividing by zero is undefined in C as well, and")
    print("   the manual does not say what the dialog writes.")


if __name__ == "__main__":
    main()
