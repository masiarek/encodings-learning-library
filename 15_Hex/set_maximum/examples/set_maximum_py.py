#!/usr/bin/env python3
"""Set Maximum, as 010 Editor's Hex Operations dialog documents it.

"If X[i] is greater than the Operand, X[i] is set to the Operand." The
operand is a ceiling -- and a ceiling of 7F catches every UTF-8 byte above
ASCII, or none of them, depending on one dropdown.

Run:  python3 set_maximum_py.py
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


def set_maximum(value, operand):
    return operand if value > operand else value


def set_minimum(value, operand):
    return operand if value < operand else value


def main():
    section(1, "SET MAXIMUM 7F ON café")
    cafe = "café".encode()
    print(f"   café is {show(cafe)}. Set Maximum 0x7F:")
    print()
    for treat in ("Unsigned Byte", "Signed Byte"):
        out = hexop(cafe, treat, set_maximum, 0x7F)
        print(f"     {treat:<14} {show(out)}   {out.decode('utf-8', errors='replace')!r}")
    print()
    print("   As Unsigned Byte, C3 and A9 are 195 and 169, both above 127, and")
    print("   both became 7F -- DEL, twice. As Signed Byte they are -61 and -87,")
    print("   nowhere near the ceiling, and nothing changed.")
    print()

    section(2, "HOW MANY BYTE VALUES IT CHANGES")
    for treat in ("Unsigned Byte", "Signed Byte"):
        changed = sum(hexop(bytes([v]), treat, set_maximum, 0x7F)[0] != v for v in range(256))
        print(f"     {treat:<14} {changed:>3} of 256")
    print()
    print("   0x7F is the largest Signed Byte there is. A ceiling at the top of")
    print("   the type catches nothing.")
    print()

    section(3, "TWO SEVEN-BIT CLAMPS THAT DISAGREE")
    clamped = hexop(cafe, "Unsigned Byte", set_maximum, 0x7F)
    masked = hexop(cafe, "Unsigned Byte", lambda x, k: x & k, 0x7F)
    print("   Binary And 7F also forces every byte into 00-7F. It gets there by")
    print("   dropping the top bit instead of by capping the value:")
    print()
    print(f"     Set Maximum 7F   {show(clamped)}   {clamped.decode('ascii')!r}")
    print(f"     Binary And 7F    {show(masked)}   {masked.decode('ascii')!r}")
    disagree = sum(
        hexop(bytes([v]), "Unsigned Byte", set_maximum, 0x7F) != hexop(bytes([v]), "Unsigned Byte", lambda x, k: x & k, 0x7F)
        for v in range(256)
    )
    print()
    print(f"   Bytes the two write differently: {disagree} of 256 -- every byte from")
    print("   80 up except FF, whose low seven bits are already 7F.")
    print()

    section(4, "A FLOOR AND A CEILING MAKE A RANGE")
    text = b"Hi 42!"
    digits = hexop(hexop(text, "Unsigned Byte", set_minimum, 0x30), "Unsigned Byte", set_maximum, 0x39)
    other_order = hexop(hexop(text, "Unsigned Byte", set_maximum, 0x39), "Unsigned Byte", set_minimum, 0x30)
    print("   Set Minimum 0x30, then Set Maximum 0x39, pins every byte into the")
    print("   ASCII digits:")
    print()
    print(f"     {text!r} -> {digits!r}")
    same_order = all(
        hexop(hexop(bytes([v]), "Unsigned Byte", set_minimum, 0x30), "Unsigned Byte", set_maximum, 0x39)
        == hexop(hexop(bytes([v]), "Unsigned Byte", set_maximum, 0x39), "Unsigned Byte", set_minimum, 0x30)
        for v in range(256)
    )
    print(f"     the other order, {other_order!r}; the same for all 256 bytes: {same_order}")
    print()
    swapped_min_first = hexop(hexop(text, "Unsigned Byte", set_minimum, 0x39), "Unsigned Byte", set_maximum, 0x30)
    swapped_max_first = hexop(hexop(text, "Unsigned Byte", set_maximum, 0x30), "Unsigned Byte", set_minimum, 0x39)
    print("   Get the operands the wrong way round and the order starts to matter,")
    print("   because then there is no byte both limits allow -- the second")
    print("   operation wins:")
    print()
    print(f"     Set Minimum 39, then Set Maximum 30   {swapped_min_first!r}")
    print(f"     Set Maximum 30, then Set Minimum 39   {swapped_max_first!r}")


if __name__ == "__main__":
    main()
