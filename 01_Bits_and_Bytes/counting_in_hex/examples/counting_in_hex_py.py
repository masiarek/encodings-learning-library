#!/usr/bin/env python3
"""Counting in hex is the same odometer with sixteen digits on every wheel.

Run:  python3 counting_in_hex_py.py
"""


def trailing(s: str, ch: str) -> int:
    """How many copies of ch the string ends with -- the digits a +1 will reset."""
    n = 0
    for c in reversed(s):
        if c != ch:
            break
        n += 1
    return n


def odometer(lo: int, hi: int) -> None:
    """Print n and n+1 across a span, marking every wheel that rolled over."""
    for n in range(lo, hi):
        a, b = f"{n:X}", f"{n + 1:X}"
        reset = trailing(a, "F")
        note = f"   <- {reset} wheel{'s' if reset > 1 else ''} rolled over" if reset else ""
        print(f"   {a:>4} + 1 = {b:<4}   ({n:>3} + 1 = {n + 1:<3}){note}")


def main() -> None:
    print("1. SIXTEEN DIGITS. SIX OF THEM ARE DRAWN AS LETTERS")
    print("   value " + "".join(f"{n:>3}" for n in range(16)))
    print("   digit " + "".join(f"{n:>3X}" for n in range(16)))
    print("   A is not a letter here. It is the digit worth ten, the way 9 is the digit worth nine.")
    print("   Decimal ran out of symbols at 9 and had to start carrying. Hex has six more to spend first.")
    print()

    print("2. COUNTING. THE ONLY NEW RULE IS WHERE THE WHEEL ROLLS OVER")
    odometer(0x0D, 0x12)
    print("   ...")
    odometer(0x18, 0x1C)
    print("   ...")
    odometer(0x1E, 0x21)
    print("   19 + 1 is 1A, not 20: that column still has six symbols left in it.")
    print()

    print("3. THE SAME ODOMETER. THE ONLY DIFFERENCE IS WHICH SYMBOL IS LAST")
    print("   decimal, last symbol 9        hex, last symbol F")
    for zeros in range(1, 4):
        d = int("9" * zeros)
        h = int("F" * zeros, 16)
        print(f"   {d:>6} + 1 = {d + 1:<6}          {h:>6X} + 1 = {h + 1:<6X}   {zeros} wheel{'s' if zeros > 1 else ''} reset")
    print("   Both right-hand answers are written '100'. One of them is 100 and the other is 256.")
    print("   A carry stops at the first digit that is not the last symbol:")
    for n in (0x9F, 0x1F, 0xAFF):
        t = trailing(f"{n:X}", "F")
        print(f"   0x{n:<4X} + 1 = 0x{n + 1:<4X}   ({t} trailing F{'s' if t > 1 else ''} reset, then the digit to their left went up by one)")
    print()

    print("4. WHY THE WHEEL ROLLS AT F: EACH COLUMN IS WORTH SIXTEEN OF THE ONE ON ITS RIGHT")
    print("   column        ...   16^2 = 256   16^1 = 16   16^0 = 1")
    for n in (0x21, 0xFF, 0x100, 0x2A5):
        digits = f"{n:X}"
        wide = len(digits)
        terms = " + ".join(f"{int(d, 16)}x{16 ** (wide - 1 - i)}" for i, d in enumerate(digits))
        adds = " + ".join(str(int(d, 16) * 16 ** (wide - 1 - i)) for i, d in enumerate(digits))
        print(f"   0x{digits:<4} = {terms:<24} = {adds:<19} = {n}")
    print("   Nothing there is special to hex. Swap the 16 for a 10 and it is the arithmetic you already do,")
    print("   which is the whole claim of this page: you are not learning to count, only where the wheel rolls.")
    print()

    print("5. 'MOST SIGNIFICANT' MEANS 'THE COLUMN WORTH THE MOST'. NOTHING ELSE")
    n = 33
    print(f"   {n} = 0x{n:02X} = 0b{n:08b}")
    print("   " + " " * 25 + "   " + "symbol".center(6) + "   " + "its column is worth".rjust(19) + "   " + "it contributes".rjust(14))
    rows = [
        ("most significant digit", f"{n >> 4:X}", 16, (n >> 4) * 16),
        ("least significant digit", f"{n & 0xF:X}", 1, n & 0xF),
        ("most significant bit", f"{n >> 7}", 128, (n >> 7) * 128),
        ("least significant bit", f"{n & 1}", 1, n & 1),
    ]
    for label, sym, worth, contributes in rows:
        print(f"   {label:<25}   {sym:^6}   {worth:>19}   {contributes:>14}")
    print("   The most significant bit of 33 is 0, and it is still the most significant bit: significance is")
    print("   what the column is worth, not what happens to be sitting in it.")
    print()

    print("6. AND IT IS PLACE VALUE, NOT SCREEN POSITION")
    print(f"   0x{0x2A5:X} as a 2-byte number, written the two ways a file may store it:")
    print(f"   big-endian     {(0x2A5).to_bytes(2, 'big').hex(' ')}   most significant byte first  -- reads like the number")
    print(f"   little-endian  {(0x2A5).to_bytes(2, 'little').hex(' ')}   least significant byte first -- and 'a5' is the LEAST significant half")
    print("   Same number, same significance, opposite order on screen. In a hex dump the leftmost byte")
    print("   is not automatically the most significant one; that is a fact about the file, not about hex.")
    print()

    print("7. SO SAY IT OUT LOUD CAREFULLY")
    for base, prefix, spelling in ((2, "0b", f"{33:b}"), (8, "0o", f"{33:o}"), (10, "", f"{33:d}"), (16, "0x", f"{33:X}")):
        print(f"   base {base:<2}  {prefix + spelling:<10} thirty-three")
    print("   0x21 is 'two-one', or 'hex twenty-one'. Bare 'twenty-one' is a different number, and mis-saying it")
    print("   is how a conversion goes wrong out loud before it goes wrong on paper. The two characters '10'")
    print(f"   are {0b10} in base 2, {0o10} in base 8, {10} in base 10 and {0x10} in base 16 -- four numbers, one spelling.")


if __name__ == "__main__":
    main()
