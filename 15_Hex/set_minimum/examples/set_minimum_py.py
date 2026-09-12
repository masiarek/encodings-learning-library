#!/usr/bin/env python3
"""Set Minimum, as 010 Editor's Hex Operations dialog documents it.

"If X[i] is less than the Operand, X[i] is set to the Operand." The operand
is a floor, and whether a byte is below it depends on whether the byte is
read as signed.

Run:  python3 set_minimum_py.py
"""

import struct
import unicodedata

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


def set_minimum(value, operand):
    return operand if value < operand else value


def runs(values):
    """[0, 1, 2, 5] -> '00-02, 05'."""
    parts, start = [], None
    for i, v in enumerate(values):
        if start is None:
            start = v
        if i + 1 == len(values) or values[i + 1] != v + 1:
            parts.append(f"{start:02x}" if start == v else f"{start:02x}-{v:02x}")
            start = None
    return ", ".join(parts)


def main():
    section(1, "SET MINIMUM 20 ON A LINE OF TEXT")
    line = "A\tB\r\ncafé".encode()
    print("   A, a tab, B, CR, LF, then café. Set Minimum 0x20 raises every value")
    print("   below a space to a space:")
    print()
    print(f"     the bytes       {show(line)}")
    for treat in ("Unsigned Byte", "Signed Byte"):
        out = hexop(line, treat, set_minimum, 0x20)
        print(f"     {treat:<15} {show(out)}   {out.decode('utf-8', errors='replace')!r}")
    print()
    print("   As Unsigned Byte the tab, the CR and the LF became spaces, and café")
    print("   came through. As Signed Byte, C3 and A9 are -61 and -87, both below")
    print("   32, so the é became two spaces as well.")
    print()

    section(2, "HOW MANY BYTE VALUES IT CHANGES")
    for treat in ("Unsigned Byte", "Signed Byte"):
        changed = [v for v in range(256) if hexop(bytes([v]), treat, set_minimum, 0x20)[0] != v]
        print(f"     {treat:<15} {len(changed):>3} of 256   {runs(changed)}")
    print()
    print("   The C0 control characters are 00-1F under both settings. Signed")
    print("   Byte adds every byte from 80 up -- which is every byte UTF-8 uses")
    print("   for anything outside ASCII.")
    print()

    section(3, "THE NAME IS THE FLOOR, NOT THE FUNCTION")
    print("   Set Minimum does not take a minimum. It sets one, which in Python is")
    print("   max():")
    print()
    for value in (0x10, 0x20, 0x41):
        out = hexop(bytes([value]), "Unsigned Byte", set_minimum, 0x20)[0]
        print(f"     Set Minimum 20 on {value:02x} -> {out:02x}      max(0x{value:02x}, 0x20) -> {max(value, 0x20):02x}")
    print()

    section(4, "ON UTF-16, THE WIDTH DECIDES WHAT A CONTROL CHARACTER IS")
    text = "A\tB".encode("utf-16-le")
    print(f"   A, tab, B in UTF-16LE is {show(text)}. Set Minimum 0x20:")
    print()
    for treat in ("Unsigned Short", "Unsigned Byte"):
        out = hexop(text, treat, set_minimum, 0x20)
        print(f"     {treat:<15} {show(out)}   .decode('utf-16-le') -> {out.decode('utf-16-le')!r}")
    wrecked = hexop(text, "Unsigned Byte", set_minimum, 0x20).decode("utf-16-le")
    print()
    print("   As a Short, only the tab was below 0x20. As a Byte, so was every 00")
    print("   that UTF-16 puts beside an ASCII letter, and three new characters")
    print("   arrived:")
    print()
    for char in wrecked:
        print(f"     U+{ord(char):04X}  {unicodedata.name(char)}")


if __name__ == "__main__":
    main()
