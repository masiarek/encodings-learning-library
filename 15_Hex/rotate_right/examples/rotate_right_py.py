#!/usr/bin/env python3
"""Rotate Right, as 010 Editor's Hex Operations dialog documents it.

"Similar to Shift Right except that bytes shifted off of X[i] will be added
to the left side of X[i]." The bit that leaves the bottom becomes the top
bit -- which, in a signed value, is the sign.

Run:  python3 rotate_right_py.py
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


def rotate(bits, direction):
    """The formula for a value of `bits` bits, rotated left or right."""
    mask = (1 << bits) - 1

    def formula(value, count):
        value &= mask
        count %= bits
        if direction == "right":
            count = (bits - count) % bits
        return (value << count | value >> (bits - count)) & mask
    return formula


def main():
    section(1, "THE BIT THAT FALLS OFF THE BOTTOM LANDS ON TOP")
    out = hexop(b"\x01", "Unsigned Byte", rotate(8, "right"), 1)
    (as_unsigned,) = struct.unpack("B", out)
    (as_signed,) = struct.unpack("b", out)
    print(f"     01 rotated right by 1   {out.hex()}   {out[0]:08b}")
    print()
    print(f"   Read back, that is {as_unsigned} as an Unsigned Byte and {as_signed} as a Signed")
    print("   one. The only 1 in the byte became the sign bit, and a value that")
    print("   was +1 is now the most negative the type can hold, without any")
    print("   arithmetic having happened.")
    print()

    section(2, "ROTATE RIGHT N IS ROTATE LEFT BY THE WIDTH MINUS N")
    bytes_agree = all(
        hexop(bytes([v]), "Unsigned Byte", rotate(8, "right"), n)
        == hexop(bytes([v]), "Unsigned Byte", rotate(8, "left"), 8 - n)
        for v in range(256) for n in range(8)
    )
    shorts_agree = all(
        hexop(v.to_bytes(2, "big"), "Unsigned Short", rotate(16, "right"), n)
        == hexop(v.to_bytes(2, "big"), "Unsigned Short", rotate(16, "left"), 16 - n)
        for v in range(65536) for n in (1, 4, 8, 12)
    )
    print(f"     all 256 bytes, every count 0-7                  {bytes_agree}")
    print(f"     all 65,536 Unsigned Shorts, counts 1, 4, 8, 12  {shorts_agree}")
    print()
    print("   So a dialog needs only one of the two. Rotate Right 4 on a byte is")
    print("   Rotate Left 4, the swap of its hex digits, from the other side.")
    print()

    section(3, "ON A SHORT THE ENDIAN TOGGLE CANNOT CHANGE A ROTATION, ON AN INT IT CAN")
    # The same arithmetic hexop does, on plain integers: it runs a million times.
    short_same = True
    for v in range(65536):
        little, big = (v >> 8) | (v & 0xFF) << 8, v
        for n in range(16):
            r_little = (little >> n | little << (16 - n)) & 0xFFFF
            r_big = (big >> n | big << (16 - n)) & 0xFFFF
            if r_little.to_bytes(2, "little") != r_big.to_bytes(2, "big"):
                short_same = False
    print(f"     every Unsigned Short, every count 0-15, little == big   {short_same}")
    data = bytes.fromhex("12 34 56 78")
    int_right = rotate(32, "right")
    little = hexop(data, "Unsigned Int", int_right, 8, "little")
    big = hexop(data, "Unsigned Int", int_right, 8, "big")
    print(f"     {show(data)} as an Unsigned Int, Rotate Right 8:")
    print(f"       little   {show(little)}")
    print(f"       big      {show(big)}")
    print()
    print("   Reading a Short the other way round swaps its two bytes, and that is")
    print("   itself a rotation by 8. Rotations of the same width can be done in")
    print("   either order, so the toggle cannot change the result. Reversing four")
    print("   bytes is not a rotation of 32 bits, so on an Int it can.")


if __name__ == "__main__":
    main()
