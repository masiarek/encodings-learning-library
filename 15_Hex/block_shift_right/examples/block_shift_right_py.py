#!/usr/bin/env python3
"""Block Shift Right, as 010 Editor's Hex Operations dialog documents it.

"Similar to Shift Right except data is treated as one long block." The bits
that pass the bottom of one value enter the value after it, and only the last
value's low bits leave the range.

Run:  python3 block_shift_right_py.py
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


def block_shift(data, count, direction, fill="zeros"):
    """The bytes, in order, as one number; fill says what enters at the top."""
    bits = 8 * len(data)
    block = int.from_bytes(data, "big")
    if direction == "left":
        block = (block << count) & ((1 << bits) - 1)
    else:
        top = block >> (bits - 1) if fill == "sign" else 0
        block >>= count
        if top:
            block |= ((1 << count) - 1) << (bits - count)
    return block.to_bytes(len(data), "big")


def utf8_or_not(data):
    try:
        return repr(data.decode("utf-8"))
    except UnicodeDecodeError:
        return "not UTF-8"


def main():
    section(1, "THE SAME LONG NUMBER, MOVED THE OTHER WAY")
    data = bytes.fromhex("12 34 56")
    print(f"   {show(data)} as Unsigned Byte, shifted right by 4:")
    print()
    print(f"     Shift Right 4         {show(hexop(data, 'Unsigned Byte', lambda x, k: x >> k, 4))}   each byte on its own")
    print(f"     Block Shift Right 4   {show(block_shift(data, 4, 'right'))}   the three bytes as one number")
    print()

    section(2, "BLOCK SHIFT RIGHT 8 INSERTS A ZERO BYTE AND DROPS THE LAST ONE")
    cafe = "café".encode()
    moved = block_shift(cafe, 8, "right")
    print(f"     {show(data):<19} -> {show(block_shift(data, 8, 'right'))}")
    print(f"     {show(cafe):<19} -> {show(moved)}   café, now {utf8_or_not(moved)}")
    print()
    print("   The range keeps its size, so inserting a byte at the front pushes one")
    print("   out at the back. In café the byte pushed out was half of the é, and")
    print("   the byte pushed in is a NUL.")
    print()

    section(3, "RIGHT 4, THEN LEFT 4, LOSES THE LAST DIGIT")
    there = block_shift(data, 4, "right")
    back = block_shift(there, 4, "left")
    print(f"     {show(data)}   Block Shift Right 4 -> {show(there)}")
    print(f"     {show(there)}   Block Shift Left 4  -> {show(back)}")
    print()

    section(4, "WHAT ENTERS AT THE TOP OF A SIGNED RANGE")
    signed = bytes.fromhex("f0 00")
    print(f"   {show(signed)}, Block Shift Right 4. Its first bit is 1, which as a Signed")
    print("   type is a minus sign. Two candidates for what comes in:")
    print()
    print(f"     zeros, as this program does          {show(block_shift(signed, 4, 'right'))}")
    print(f"     copies of the sign bit, as >> does   {show(block_shift(signed, 4, 'right', fill='sign'))}")
    print()
    print("   The manual says only that Block Shift Right is similar to Shift")
    print("   Right, and Shift Right itself leaves the signed case to the")
    print("   implementation. Neither row has been measured against the dialog.")


if __name__ == "__main__":
    main()
