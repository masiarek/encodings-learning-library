#!/usr/bin/env python3
"""Block Shift Left, as 010 Editor's Hex Operations dialog documents it.

"Similar to Shift Left except data is treated as one long block." The bits
that pass the top of one value do not fall off; they enter the value before
it, and only the first value's top bits leave the range.

Run:  python3 block_shift_left_py.py
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


def block_shift(data, count, direction, width=1, endian="little"):
    """The values, in order, each most significant bit first, as one number."""
    values = [int.from_bytes(data[i:i + width], endian) for i in range(0, len(data), width)]
    bits = 8 * width
    block = 0
    for value in values:
        block = block << bits | value
    total = bits * len(values)
    block = (block << count) & ((1 << total) - 1) if direction == "left" else block >> count
    out = b""
    for i in range(len(values)):
        value = (block >> bits * (len(values) - 1 - i)) & ((1 << bits) - 1)
        out += value.to_bytes(width, endian)
    return out


def main():
    section(1, "ONE LONG NUMBER INSTEAD OF MANY SHORT ONES")
    data = bytes.fromhex("12 34 56")
    print(f"   {show(data)} as Unsigned Byte, shifted left by 4:")
    print()
    print(f"     Shift Left 4         {show(hexop(data, 'Unsigned Byte', lambda x, k: x << k, 4))}   each byte on its own")
    print(f"     Block Shift Left 4   {show(block_shift(data, 4, 'left'))}   the three bytes as one number")
    print()
    print("   Shift Left lost the top digit of every byte. Block Shift Left lost")
    print("   only the first, and the others moved into the byte before theirs.")
    print()

    section(2, "BLOCK SHIFT LEFT 4 DELETES A HEX DIGIT")
    for count in (4, 8, 12):
        out = block_shift(data, count, "left")
        print(f"     Block Shift Left {count:<3} {data.hex()} -> {out.hex()}")
    print()
    print("   Four bits is one hex digit, so each 4 deletes the first digit of the")
    print("   range and appends a 0; eight deletes a whole byte. The range keeps")
    print("   its size, which a real delete would not.")
    print()

    section(3, "NOTHING COMES BACK")
    there = block_shift(data, 4, "left")
    back = block_shift(there, 4, "right")
    print(f"     {show(data)}   Block Shift Left 4  -> {show(there)}")
    print(f"     {show(there)}   Block Shift Right 4 -> {show(back)}")
    print()
    print("   The 1 that left the range is gone, and a 0 came in to replace it.")
    print("   A Rotate would have kept it.")
    print()

    section(4, "ON A LITTLE-ENDIAN SHORT, THE SENTENCE HAS TWO READINGS")
    print("   The manual says bytes shifted off X[i+1] are shifted onto X[i]. For")
    print("   one-byte values that settles everything. For wider ones there are two")
    print("   ways to lay the values end to end, and they agree only on big-endian:")
    print()
    for endian, pair in (("big", bytes.fromhex("12 34 56 78")), ("little", bytes.fromhex("34 12 78 56"))):
        by_value = block_shift(pair, 4, "left", width=2, endian=endian)
        by_file = block_shift(pair, 4, "left")
        print(f"     Unsigned Short, {endian:<6}  {show(pair)}")
        print(f"       the values in order, each high bit first   {show(by_value)}")
        print(f"       the file's bytes as they lie                {show(by_file)}")
    print()
    print("   The first reading follows the manual's X[i] wording, and it is the")
    print("   one this program's Block Shift uses. Which one the dialog uses on a")
    print("   little-endian Short has not been measured here.")


if __name__ == "__main__":
    main()
