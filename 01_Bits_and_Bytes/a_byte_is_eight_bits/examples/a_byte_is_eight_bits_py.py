#!/usr/bin/env python3
"""A byte is eight switches. What they mean is whatever the reader agreed on.

Run:  python3 a_byte_is_eight_bits_py.py
"""


def bits(n: int) -> str:
    """The eight bits of a byte, in groups of four so the eye can count them."""
    b = format(n, "08b")
    return b[:4] + " " + b[4:]


def main() -> None:
    print("1. EIGHT SWITCHES, EACH WORTH A POWER OF TWO")
    places = [128, 64, 32, 16, 8, 4, 2, 1]
    print("   place value :  " + "  ".join(f"{p:>3}" for p in places))
    for n in (0, 1, 2, 65, 127, 128, 200, 255):
        on = [int(c) for c in format(n, "08b")]
        row = "  ".join(f"{c:>3}" for c in on)
        terms = " + ".join(str(p) for p, c in zip(places, on) if c) or "0"
        print(f"   {n:>3}         :  {row}    = {terms}")
    print()

    print("2. HOW MANY PATTERNS EIGHT SWITCHES CAN MAKE")
    print(f"   2 ** 8 = {2 ** 8}, so one byte holds 0..255 and nothing else.")
    print(f"   256 needs a ninth bit: {format(256, 'b')}  ({len(format(256, 'b'))} digits)")
    print()

    print("3. TWO WAYS TO WRITE THE SAME NUMBER")
    print(f"   format(65, '08b')      -> {format(65, '08b')!r}   (number -> its eight bits)")
    print(f"   int('01000001', 2)     -> {int('01000001', 2)}            (eight bits -> number)")
    print(f"   0b0100_0001            -> {0b0100_0001}            (a binary literal in source)")
    print()

    print("4. THE SAME BYTE, THREE READINGS")
    b = bytes([65])
    print(f"   as a number    : {b[0]}")
    print(f"   as bits        : {bits(b[0])}")
    print(f"   as ASCII text  : {b!r}   (Python shows the byte 65 as the letter A)")
    print("   Nothing in the byte says which reading is right. The program does.")
    print()

    print("5. DECIMAL -> BINARY BY HAND, FOR 200")
    n = 200
    out = ""
    for p in places:
        if n >= p:
            out += "1"
            print(f"   {n:>3} >= {p:<3} -> write 1, subtract, {n - p:>3} left")
            n -= p
        else:
            out += "0"
            print(f"   {n:>3} <  {p:<3} -> write 0")
    print(f"   result: {out[:4]} {out[4:]}  == format(200, '08b') -> {format(200, '08b') == out}")


if __name__ == "__main__":
    main()
