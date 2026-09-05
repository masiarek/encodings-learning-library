#!/usr/bin/env python3
"""Hex is binary written four bits at a time.

Run:  python3 hex_is_a_shorthand_py.py
"""


def main() -> None:
    print("1. ONE HEX DIGIT IS EXACTLY FOUR BITS (a 'nibble')")
    print("   bits   hex   decimal")
    for n in range(16):
        print(f"   {n:04b}   {n:X}     {n:>2}")
    print()

    print("2. SO A BYTE IS EXACTLY TWO HEX DIGITS, ALWAYS")
    for n in (65, 200, 255, 0, 15, 16):
        b = format(n, "08b")
        print(f"   {n:>3} = {b[:4]} {b[4:]} = {n:02X}   (left nibble {int(b[:4], 2):X}, right nibble {int(b[4:], 2):X})")
    print("   Compare decimal: 65 / 200 / 255 have no visible relation to their bits.")
    print()

    print("3. THE SPELLINGS PYTHON GIVES YOU")
    print(f"   hex(65)              -> {hex(65)!r}     (0x prefix, lowercase, no padding)")
    print(f"   format(65, '02x')    -> {format(65, '02x')!r}       (two digits, no prefix)")
    print(f"   format(5, '02x')     -> {format(5, '02x')!r}       (padding matters: '5' would not be a byte)")
    print(f"   f'{{65:#04x}}'         -> '{65:#04x}'     (# adds the prefix, 04 counts the prefix)")
    print(f"   int('41', 16)        -> {int('41', 16)}         (text -> number, base 16)")
    print(f"   0x41                 -> {0x41}         (a hex literal in source)")
    print(f"   bytes.fromhex('41')  -> {bytes.fromhex('41')!r}       (text -> the byte itself)")
    print(f"   b'A'.hex()           -> {b'A'.hex()!r}       (the byte -> text)")
    print()

    print("4. THE TRAP: THE TEXT '41' IS NOT THE BYTE 0x41")
    as_text = "41".encode()
    print(f"   '41'.encode()        -> {as_text!r}   which is the bytes {as_text.hex(' ')}")
    print("   Two characters, '4' and '1', are two bytes: 0x34 and 0x31.")
    print(f"   bytes.fromhex('41')  -> {bytes.fromhex('41')!r}    one byte, value 0x41 = 65 = 'A'")
    print("   A hex dump SHOWS you '41'; the file CONTAINS one byte. Never confuse the picture with the thing.")
    print()

    print("5. WHY 0xFF IS THE NUMBER EVERYONE REMEMBERS")
    print(f"   0xFF = {0xFF} = {0xFF:08b} = every switch on = the biggest byte")
    print(f"   0x100 = {0x100} = {0x100:b} = the first number that needs a second byte")


if __name__ == "__main__":
    main()
