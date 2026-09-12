#!/usr/bin/env python3
"""The Hex Operations dialog, as one Python function.

010 Editor's manual writes each operation in C notation, "assuming that X[i]
represents each value in the file to be modified". hexop() below is that
sentence made runnable: cut the bytes into values of the type Treat Data As
names, in the byte order the Endian toggle names, apply one formula to each
value, and write it back where it came from. Every program in 15_Hex starts
with the same function.

It makes one assumption the manual does not state: an integer result that
does not fit its type keeps its low bits.

Run:  python3 the_dialog_py.py
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
    """C's integer division, which rounds toward zero."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def add(value, operand):
    return value + operand


def assign(value, operand):
    return operand


def values(data, treat, endian="little"):
    code = ("<" if endian == "little" else ">") + TREAT_AS[treat]
    return [value for (value,) in struct.iter_unpack(code, data)]


CUTS = (
    ("Unsigned Byte", "little", "Unsigned Byte"),
    ("Unsigned Short", "little", "Unsigned Short, little"),
    ("Unsigned Short", "big", "Unsigned Short, big"),
    ("Unsigned Int", "little", "Unsigned Int, little"),
)


def main():
    section(1, "TREAT DATA AS DECIDES WHAT ONE VALUE IS")
    data = bytes.fromhex("01 00 02 00")
    print("   Four bytes, cut four ways. The file does not say which cut is")
    print("   meant; the dropdown and the Endian toggle do.")
    print()
    print(f"     the bytes                  {show(data)}")
    for treat, endian, label in CUTS:
        listed = ", ".join(str(v) for v in values(data, treat, endian))
        print(f"     {label:<26} X = {listed}")
    print()

    section(2, "SO ONE OPERATION HAS MORE THAN ONE ANSWER")
    pair = data[:2]
    print(f"   Add 1 to the first two of those bytes, {show(pair)}, three ways:")
    print()
    for treat, endian, label in CUTS[:3]:
        print(f"     {label:<26} {show(hexop(pair, treat, add, 1, endian))}")
    print()
    print("   As bytes, each one gets its own 1. As one little-endian Short the")
    print("   1 lands on the first byte, and as a big-endian Short on the second.")
    print()

    section(3, "SIGNED OR UNSIGNED CHANGES SOME FORMULAS AND NOT OTHERS")
    print("   F0 is 240 as an Unsigned Byte and -16 as a Signed Byte:")
    print()
    print(f"     {'operation':<20} {'Unsigned Byte':<15} Signed Byte")
    rows = (
        ("Add 1", add, 1),
        ("Multiply 2", lambda x, k: x * k, 2),
        ("Divide 2", c_div, 2),
        ("Set Minimum 16", max, 16),
    )
    for name, formula, operand in rows:
        unsigned = show(hexop(b"\xf0", "Unsigned Byte", formula, operand))
        signed = show(hexop(b"\xf0", "Signed Byte", formula, operand))
        print(f"     {name:<20} {unsigned:<15} {signed}")
    print()
    print("   Addition and multiplication keep the same low bits either way.")
    print("   Division and comparison have to know the number, and the number")
    print("   is what the dropdown changed.")
    print()

    section(4, "OPERAND STEP ADDS TO THE OPERAND AFTER EACH VALUE")
    print("   Assign 0 with Operand Step 1 counts up, one value at a time:")
    print()
    print(f"     Unsigned Byte,  8 bytes    {show(hexop(bytes(8), 'Unsigned Byte', assign, 0, step=1))}")
    print(f"     Unsigned Short, 8 bytes    {show(hexop(bytes(8), 'Unsigned Short', assign, 0, step=1))}")
    print()

    section(5, "SKIP BYTES LEAVES A GAP AFTER EACH VALUE")
    records = struct.pack("<i4si4s", 1, b"Ada ", 2, b"Bob ")
    after = hexop(records, "Signed Int", add, 1, skip=4)
    print("   Two records, each a Signed Int id and then a four-byte name. Add 1")
    print("   with Skip Bytes 4 changes every id and no name:")
    print()
    print(f"     before  {show(records)}")
    print(f"     after   {show(after)}")
    print()
    for label, blob in (("before", records), ("after", after)):
        first, name1, second, name2 = struct.unpack("<i4si4s", blob)
        print(f"     {label:<6}  ids {first} and {second}, names {name1!r} and {name2!r}")
    print()

    section(6, "RANGE: A SELECTION IS A SLICE")
    whole = bytes(6)
    start, size = 2, 2
    selected = (whole[:start]
                + hexop(whole[start:start + size], "Unsigned Byte", add, 1)
                + whole[start + size:])
    print("   With Selection set, the bytes outside it are not values at all.")
    print("   Add 1 to six zero bytes, then to two of them selected at offset 2:")
    print()
    print(f"     Entire File   {show(hexop(whole, 'Unsigned Byte', add, 1))}")
    print(f"     Selection     {show(selected)}")


if __name__ == "__main__":
    main()
