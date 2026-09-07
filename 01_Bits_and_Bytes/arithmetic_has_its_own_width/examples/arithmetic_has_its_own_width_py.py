#!/usr/bin/env python3
"""A byte is eight bits wide. In Python, the arithmetic over it is not any width at all.

Run:  python3 arithmetic_has_its_own_width_py.py
"""


def main() -> None:
    print("1. THERE IS NO WIDTH TO OVERFLOW")
    c = 255
    print(f"   c                     = {c:<6} 1111 1111, the largest value a byte holds")
    print(f"   c << 2                = {c << 2:<6} and Python simply keeps the ninth and tenth bits")
    print(f"   (c << 2) has          = {(c << 2).bit_length():<6} bits, so it no longer fits in a byte")
    print(f"   (1 << 1000) has       = {(1 << 1000).bit_length():<6} bits, and that is not an error either")
    print("   An int here is as wide as its value needs. Nothing wraps, because there")
    print("   is no edge to wrap at -- the memory is the only limit.")
    print()

    print("2. SO THE BYTE ANSWER HAS TO BE ASKED FOR BY NAME")
    print(f"   (c << 2) & 0xFF       = {(c << 2) & 0xFF:<6} mask to eight bits by hand")
    print(f"   ((c << 2) & 0xFF)     = {((c << 2) & 0xFF):#010b}")
    print(f"   int.to_bytes(1, ...)  = {(252).to_bytes(1, 'big')!r}   the width named in the call")
    print("   Both spellings say `eight bits` out loud. In a language where the type")
    print("   carries the width, that sentence is in the declaration instead -- and in C")
    print("   it is in neither, which is why the C aside on this page exists.")
    print()

    print("3. SIGNEDNESS IS AN ARGUMENT, NOT A PROPERTY OF THE BYTES")
    raw = bytes([0b10011100])
    print(f"   the byte              = {raw!r}  ->  {raw[0]:08b}")
    print(f"   from_bytes(signed=False) = {int.from_bytes(raw, 'big', signed=False)}")
    print(f"   from_bytes(signed=True)  = {int.from_bytes(raw, 'big', signed=True)}")
    print("   One byte, two numbers, and the byte does not know which you meant. The")
    print("   keyword is where the reading lives; nothing about the storage decides it.")
    print()

    print("4. >> AND // AGREE HERE, AND IN C THEY DO NOT")
    for x in (-5, -8, 5):
        print(f"   x = {x:<3} x >> 3 = {x >> 3:<3} x // 8 = {x // 8:<3} x % 8 = {x % 8:<3} int(x / 8) = {int(x / 8)}")
    shift_vs_floor = sum(1 for x in range(-8, 0) if (x >> 3) != (x // 8))
    shift_vs_trunc = sum(1 for x in range(-8, 0) if (x >> 3) != int(x / 8))
    print(f"   Counted over -8..-1: `>>` and `//` differ on {shift_vs_floor} of 8 values, because both")
    print(f"   round toward minus infinity. `>>` and C's truncating division differ on {shift_vs_trunc}.")
    print("   Python's `%` follows its `//`, so it is never negative for a positive")
    print("   divisor -- which is the half of this that most often surprises a C reader.")
    print()

    print("5. THE ONE PLACE PYTHON DOES INSIST ON A WIDTH")
    for value in (255, 256, -1):
        try:
            out = repr((value).to_bytes(1, "big"))
        except OverflowError as exc:
            out = f"raises {type(exc).__name__}"
        print(f"   ({value}).to_bytes(1, 'big') -> {out}")
    print("   The width is not in the int; it is in the request to become bytes. That")
    print("   is the boundary this whole chapter is about, and it is the only place a")
    print("   Python program is made to say how many bits it meant.")


if __name__ == "__main__":
    main()
