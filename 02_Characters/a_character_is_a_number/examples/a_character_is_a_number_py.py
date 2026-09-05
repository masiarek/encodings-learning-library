#!/usr/bin/env python3
"""ASCII: 128 numbers, each assigned a character by agreement.

Run:  python3 a_character_is_a_number_py.py
"""

CONTROL_NAMES = {0: "NUL", 7: "BEL", 8: "BS", 9: "TAB", 10: "LF", 13: "CR", 27: "ESC", 127: "DEL"}


def main() -> None:
    print("1. THE AGREEMENT: ord() looks a character up, chr() looks a number up")
    for ch in "A", "a", "0", " ", "~":
        n = ord(ch)
        print(f"   {ch!r:<4} ord -> {n:>3}   hex {n:02X}   bits {n:08b}   chr({n}) -> {chr(n)!r}")
    print()

    print("2. THE TABLE HAS A LAYOUT, AND IT IS NOT AN ACCIDENT")
    print("   digits start at 0x30:  ", " ".join(f"{c}={ord(c):02X}" for c in "0123456789"))
    print("   uppercase at 0x41:     ", " ".join(f"{c}={ord(c):02X}" for c in "ABCDEF"), "...")
    print("   lowercase at 0x61:     ", " ".join(f"{c}={ord(c):02X}" for c in "abcdef"), "...")
    print(f"   'a' - 'A' = {ord('a') - ord('A')} = 0x20 = 0010 0000: one bit apart, bit 5")
    print()

    print("3. TWO TRICKS THE LAYOUT MAKES POSSIBLE")
    print(f"   digit value  : ord('7') - ord('0') = {ord('7') - ord('0')}")
    print(f"   flip case    : chr(ord('a') ^ 0x20) = {chr(ord('a') ^ 0x20)!r},  chr(ord('Q') ^ 0x20) = {chr(ord('Q') ^ 0x20)!r}")
    print(f"   force lower  : chr(ord('Q') | 0x20) = {chr(ord('Q') | 0x20)!r}   force upper: chr(ord('q') & ~0x20) = {chr(ord('q') & ~0x20)!r}")
    print()

    print("4. THE FIRST 32 ARE NOT LETTERS: control characters, from teletype days")
    for n, name in CONTROL_NAMES.items():
        print(f"   {n:>3}  0x{n:02X}  {name:<4} {chr(n)!r}")
    print("   TAB, LF and CR are the three you will meet every week; NUL ends a C string.")
    print()

    print("5. ALL 128 FIT IN SEVEN BITS, SO THE TOP BIT OF EVERY ASCII BYTE IS 0")
    for ch in "A", "z", "~", "\x7f":
        print(f"   {ch!r:<6} {ord(ch):08b}")
    print("   The 128 patterns with the top bit SET are unclaimed by ASCII.")
    print("   Everyone claimed them differently. That is the next lesson.")
    print()

    print("6. THE WHOLE PRINTABLE TABLE, 32..126")
    for row in range(32, 127, 16):
        cells = [f"{n:>3}={chr(n)}" for n in range(row, min(row + 16, 127))]
        print("   " + " ".join(cells))


if __name__ == "__main__":
    main()
