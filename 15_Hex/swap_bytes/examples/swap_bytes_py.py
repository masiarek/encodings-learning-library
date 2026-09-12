#!/usr/bin/env python3
"""Swap Bytes, as 010 Editor's Hex Operations dialog documents it.

"Swap the bytes of X[i]": reverse each value's bytes, which turns a
little-endian value into a big-endian one and back. It takes no operand,
and it is the operation the Endian toggle cannot change.

Run:  python3 swap_bytes_py.py
"""

import array
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


def swap_bytes(treat):
    """The formula for one integer type: reverse the value's bytes."""
    width = struct.calcsize(TREAT_AS[treat])
    mask = (1 << 8 * width) - 1
    return lambda x, k: int.from_bytes((x & mask).to_bytes(width, "little"), "big")


SHORT = swap_bytes("Unsigned Short")


def main():
    section(1, "UTF-16LE BECOMES UTF-16BE IN PLACE")
    text = b"\xff\xfe" + "é€".encode("utf-16-le")
    swapped = hexop(text, "Unsigned Short", SHORT)
    print("   é€ in UTF-16LE with its byte order mark, then Swap Bytes as")
    print("   Unsigned Short:")
    print()
    print(f"     before   {show(text)}   .decode('utf-16') -> {text.decode('utf-16')!r}")
    print(f"     after    {show(swapped)}   .decode('utf-16') -> {swapped.decode('utf-16')!r}")
    print(f"     after, without its first two bytes, as UTF-16BE        {swapped[2:].decode('utf-16-be')!r}")
    print()
    print("   The mark was swapped along with the text, FF FE to FE FF, so a")
    print("   reader that trusts the mark still gets é€. That is what the mark is")
    print("   for.")
    print()

    section(2, "THE ENDIAN TOGGLE CANNOT CHANGE IT")
    shorts = all(
        hexop(v.to_bytes(2, "big"), "Unsigned Short", SHORT, endian="little")
        == hexop(v.to_bytes(2, "big"), "Unsigned Short", SHORT, endian="big")
        for v in range(65536)
    )
    INT = swap_bytes("Unsigned Int")
    ints = all(
        hexop(v.to_bytes(4, "big"), "Unsigned Int", INT, endian="little")
        == hexop(v.to_bytes(4, "big"), "Unsigned Int", INT, endian="big")
        for v in range(0, 1 << 32, 65537)
    )
    print("   Little and Big wrote the same bytes:")
    print()
    print(f"     all 65,536 Unsigned Shorts                    {shorts}")
    print(f"     65,536 Unsigned Ints, every 65,537th value    {ints}")
    print()
    print("   Reading a value little-endian and writing it back big-endian is a")
    print("   reversal, and so is the other way round. Either way the bytes come")
    print("   out reversed, so the setting has nothing to decide.")
    print()

    section(3, "THE WIDTH CAN")
    data = bytes.fromhex("12 34 56 78")
    print(f"   Swap Bytes on {show(data)}:")
    print()
    for treat in ("Unsigned Short", "Unsigned Int"):
        print(f"     {treat:<15} {show(hexop(data, treat, swap_bytes(treat)))}")
    eight = bytes(range(1, 9))
    print(f"     Unsigned Int64  {show(eight)} -> {show(hexop(eight, 'Unsigned Int64', swap_bytes('Unsigned Int64')))}")
    print()

    section(4, "A RANGE THAT STARTS ONE BYTE LATE")
    late = text[:1] + hexop(text[1:5], "Unsigned Short", SHORT) + text[5:]
    print("   The same six bytes, with the selection starting at offset 1 and")
    print("   four bytes long. The pairs are the wrong pairs:")
    print()
    print(f"     {show(late)}   .decode('utf-16-le') -> {late.decode('utf-16-le')!r}")
    print()
    print("   Three code units, and none of them is the mark, é or €. Swap Bytes")
    print("   trusts the range to start on a value, and nothing in the bytes says")
    print("   where one starts.")
    print()

    section(5, "PYTHON SPELLS IT array.byteswap()")
    units = array.array("H", text)
    units.byteswap()
    print(f"     array('H', before).byteswap()   {show(units.tobytes())}")
    print(f"     == Swap Bytes as Unsigned Short  {units.tobytes() == swapped}")


if __name__ == "__main__":
    main()
