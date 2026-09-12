#!/usr/bin/env python3
"""Rotate Left, as 010 Editor's Hex Operations dialog documents it.

"Similar to Shift Left except that bytes shifted off of X[i] will be added
to the right side of X[i]." Nothing leaves the value, so nothing is lost.

Run:  python3 rotate_left_py.py
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


def rotate_left(bits):
    """The formula for a value of `bits` bits: the bits that leave the top come in at the bottom."""
    mask = (1 << bits) - 1

    def formula(value, count):
        value &= mask
        count %= bits
        return (value << count | value >> (bits - count)) & mask
    return formula


BYTE = rotate_left(8)
SHORT = rotate_left(16)


def main():
    section(1, "THE BIT THAT FALLS OFF COMES BACK")
    print("   81 is 1000 0001. Shift and rotate it left by 1:")
    print()
    shifted = hexop(b"\x81", "Unsigned Byte", lambda x, k: x << k, 1)[0]
    rotated = hexop(b"\x81", "Unsigned Byte", BYTE, 1)[0]
    print(f"     Shift Left 1    {shifted:02x}   {shifted:08b}")
    print(f"     Rotate Left 1   {rotated:02x}   {rotated:08b}")
    print()

    section(2, "ROTATE LEFT 4 SWAPS A BYTE'S TWO HEX DIGITS")
    e_acute = "é".encode()
    print(f"     é   {show(e_acute)} -> {show(hexop(e_acute, 'Unsigned Byte', BYTE, 4))}")
    swaps = all(hexop(bytes([v]), "Unsigned Byte", BYTE, 4)[0] == ((v & 0x0F) << 4 | v >> 4)
                for v in range(256))
    print(f"     the same as swapping the digits, all 256 bytes   {swaps}")
    print()
    print("   Four is half of eight, so the top digit comes round to the bottom")
    print("   and the bottom digit is pushed up to the top.")
    print()

    section(3, "NOTHING IS LOST")
    eight_ones = all(_rotate_n(bytes([v]), 8) == bytes([v]) for v in range(256))
    outputs = {hexop(bytes([v]), "Unsigned Byte", BYTE, 1)[0] for v in range(256)}
    undone = all(
        hexop(hexop(bytes([v]), "Unsigned Byte", BYTE, 3), "Unsigned Byte", BYTE, 5) == bytes([v])
        for v in range(256)
    )
    print(f"     Rotate Left 1, eight times, gives every byte back   {eight_ones}")
    print(f"     different bytes Rotate Left 1 can write             {len(outputs)} of 256")
    print(f"     Rotate Left 3, then Rotate Left 5, is no change     {undone}")
    print()
    print("   Every byte in, a different byte out, and all 256 of them reachable:")
    print("   a rotation only reorders bits, so it can always be turned back.")
    print()

    section(4, "ROTATE LEFT 8 ON AN UNSIGNED SHORT IS SWAP BYTES")
    same = all(
        hexop(v.to_bytes(2, "big"), "Unsigned Short", SHORT, 8) == v.to_bytes(2, "little")
        for v in range(65536)
    )
    print(f"     all 65,536 Unsigned Shorts   {same}")
    print()
    print("   Half of sixteen is eight, and a byte is eight bits: rotating a Short")
    print("   by half its width trades its two bytes.")
    print()

    section(5, "SIGNED OR UNSIGNED, THE SAME BITS")
    signed_same = all(
        hexop(bytes([v]), "Unsigned Byte", BYTE, k) == hexop(bytes([v]), "Signed Byte", BYTE, k)
        for v in range(256) for k in range(8)
    )
    print(f"     all 256 bytes, counts 0-7   {signed_same}")
    print()
    print("   A rotation moves bits and never looks at what they mean. The number")
    print("   read back can change sign -- 40 rotated left by 1 is 80, which is")
    print("   +64 becoming -128 -- but the bytes do not depend on the dropdown.")


def _rotate_n(data, times):
    for _ in range(times):
        data = hexop(data, "Unsigned Byte", BYTE, 1)
    return data


if __name__ == "__main__":
    main()
