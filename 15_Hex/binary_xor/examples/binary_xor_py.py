#!/usr/bin/env python3
"""Binary Xor: X[i] ^= Operand, as 010 Editor's Hex Operations dialog documents it.

Xor flips every bit the operand has. Flip the same bits twice and they are
back where they started, which is the whole of its usefulness and the whole
of its weakness.

Run:  python3 binary_xor_py.py
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


def binary_xor(value, operand):
    return value ^ operand


def utf8_or_not(data):
    try:
        return repr(data.decode("utf-8"))
    except UnicodeDecodeError:
        return "not UTF-8"


def main():
    section(1, "XOR 20 SWAPS THE CASE OF ASCII LETTERS")
    print("   Bit 5 is set in a lowercase ASCII letter and clear in a capital, so")
    print("   flipping it swaps them:")
    print()
    for word in ("Cafe", "Café"):
        data = word.encode()
        out = hexop(data, "Unsigned Byte", binary_xor, 0x20)
        print(f"     {word!r:<7} {show(data):<16} -> {show(out):<16} {utf8_or_not(out)}")
    print()
    print("   On é the flip also lands on the lead byte: C3 becomes E3, which")
    print("   starts a three-byte character, and only one byte follows it.")
    print()

    section(2, "XOR TWICE GIVES THE FILE BACK")
    pairs = all((v ^ k) ^ k == v for v in range(256) for k in range(256))
    cafe = "café".encode()
    twice = hexop(hexop(cafe, "Unsigned Byte", binary_xor, 0x20), "Unsigned Byte", binary_xor, 0x20)
    print(f"     every byte, every operand, 65,536 pairs   {pairs}")
    print(f"     café through Xor 20 twice                 {twice.decode('utf-8')!r}")
    print()
    print("   Even the invalid UTF-8 in the middle comes back, because no bit was")
    print("   ever lost -- only flipped.")
    print()

    section(3, "A ONE-BYTE KEY IS NOT A SECRET")
    key = 0x5A
    hidden = hexop(cafe, "Unsigned Byte", binary_xor, key)
    print(f"   café, Xor 0x{key:02X}: {show(hidden)}")
    print()
    cancels = all(hidden[i] ^ hidden[j] == cafe[i] ^ cafe[j] for i in range(5) for j in range(5))
    rows = (
        ("hidden[0] ^ ord('c')", f"0x{hidden[0] ^ ord('c'):02X}", "the key, from one known letter"),
        ("hidden[i] ^ hidden[j] == café[i] ^ café[j]", str(cancels), "the key cancels out"),
    )
    for expression, value, note in rows:
        print(f"     {expression:<44} {value:<6} {note}")
    print()
    print("   Anyone who can guess one byte of the original has the key, and")
    print("   anyone who has two hidden bytes has their Xor without it.")
    print()

    section(4, "OPERAND STEP GIVES EVERY BYTE ITS OWN KEY")
    same = b"aaaa"
    fixed = hexop(same, "Unsigned Byte", binary_xor, key)
    stepped = hexop(same, "Unsigned Byte", binary_xor, key, step=1)
    back = hexop(stepped, "Unsigned Byte", binary_xor, key, step=1)
    print(f"   {same!r}, Xor 0x{key:02X}:")
    print()
    print(f"     Operand Step 0           {show(fixed)}   four equal bytes for four equal letters")
    print(f"     Operand Step 1           {show(stepped)}   no two alike")
    print(f"     Step 1 again, same key   {back!r}")
    print()
    print("   The key now changes with the position, so repeated letters stop")
    print("   showing. It is still a key anyone can recover the same way.")
    print()

    section(5, "A WIDER KEY LANDS WHERE THE ENDIAN TOGGLE PUTS IT")
    print("   Xor 0x1234 as Unsigned Short over four zero bytes writes the key")
    print("   itself, in the order the toggle names:")
    print()
    for endian in ("little", "big"):
        print(f"     {endian:<7} {show(hexop(bytes(4), 'Unsigned Short', binary_xor, 0x1234, endian))}")


if __name__ == "__main__":
    main()
