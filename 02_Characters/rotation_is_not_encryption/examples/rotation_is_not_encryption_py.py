#!/usr/bin/env python3
"""ROT13: arithmetic on the ASCII layout, filed under encodings, with no key.

Run:  python3 rotation_is_not_encryption_py.py
"""

import codecs
import encodings.rot_13  # noqa: F401  -- imported to show WHERE Python keeps it
import unicodedata


def rotate_letters(text: str, n: int) -> str:
    """Rotate A-Z and a-z by n. Everything else is left alone."""
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - ord("a") + n) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - ord("A") + n) % 26 + ord("A")))
        else:
            out.append(ch)
    return "".join(out)


def rotate_printable(text: str, n: int) -> str:
    """Rotate the 94 printable ASCII characters, 0x21..0x7E, by n."""
    return "".join(
        chr((ord(c) - 0x21 + n) % 94 + 0x21) if 0x21 <= ord(c) <= 0x7E else c for c in text
    )


def rotate_digits(text: str, n: int) -> str:
    return "".join(chr((ord(c) - ord("0") + n) % 10 + ord("0")) if c.isdigit() else c for c in text)


def main() -> None:
    plain = "abcdefghijklmnopqrstuvwxyz"

    print("1. A SUBSTITUTION CIPHER IS A LOOKUP TABLE. ROTATION IS ONE FORMULA FOR IT.")
    print(f"   plaintext alphabet   {plain}")
    print(f"   ciphertext alphabet  {rotate_letters(plain, 13)}   <- ROT13, built by (x + 13) % 26")
    print(f"   ciphertext alphabet  {rotate_letters(plain, 3)}   <- shift 3, the Caesar of the books")
    print("   The table IS the key. Rotation just means you can write the table as one sum.")
    print()

    print("2. ROT13 IS ITS OWN INVERSE, BECAUSE 13 + 13 = 26")
    once = rotate_letters("Hello, World!", 13)
    twice = rotate_letters(once, 13)
    print(f"   'Hello, World!' -> {once!r} -> {twice!r}")
    print("   One function both ways. Nothing in the program knows which direction it is going.")
    print()

    print("3. THE ROTATION IS ARITHMETIC ON THE ASCII LAYOUT, SO THE LAYOUT PICKS THE NUMBER")
    print(f"   A..Z        is {ord('Z') - ord('A') + 1} contiguous code points, half of it is 13   -> ROT13")
    print(f"   0..9        is {ord('9') - ord('0') + 1} contiguous code points, half of it is  5   -> ROT5")
    print(f"   0x21..0x7E  is {0x7E - 0x21 + 1} contiguous code points, half of it is 47   -> ROT47")
    print(f"   ROT5  on '2026-09-07'    -> {rotate_digits('2026-09-07', 5)}")
    print(f"   ROT47 on 'Hello, World!' -> {rotate_printable('Hello, World!', 47)}")
    print(f"   ROT47 twice              -> {rotate_printable(rotate_printable('Hello, World!', 47), 47)}")
    print("   ROT18 is just ROT13 for the letters and ROT5 for the digits, done at once.")
    print("   Each of those numbers is half the size of a RANGE IN THE TABLE. Nothing else.")
    print()

    print("4. THERE IS NO KEY. THE WHOLE KEYSPACE OF A ROTATION FITS ON THIS SCREEN.")
    secret = rotate_letters("attack at dawn", 13)
    print(f"   ciphertext: {secret!r}")
    for n in range(26):
        mark = "  <- the plaintext, and you found it by reading" if n == 13 else ""
        print(f"   shift {n:>2}: {rotate_letters(secret, n)}{mark}")
    print("   25 wrong lines and one right one, and no computer was needed to pick it.")
    print("   For ROT13 it is worse than that: the shift is published, so the keyspace is 1.")
    print()

    print("5. PYTHON FILES ROT13 UNDER encodings/ -- AND encode() STILL REFUSES IT")
    print(f"   the module is  {encodings.rot_13.__name__}   (package: {encodings.rot_13.__package__})")
    print(f"   the registry knows it as  {codecs.lookup('rot13').name!r}")
    try:
        "abc".encode("rot13")
    except Exception as exc:
        print(f"   'abc'.encode('rot13')  raises  {type(exc).__name__}")
    print(f"   codecs.encode('abc', 'rot13')  ->  {codecs.encode('abc', 'rot13')!r}")
    print("   Both facts are right. It lives with the encodings because it is a rewriting")
    print("   with a published rule; encode() rejects it because encode() means str -> bytes,")
    print("   and this is str -> str. A cipher that fits in the encodings package is not")
    print("   protecting anything.")
    print()

    print("6. INSIDE ASCII THE BYTE COUNT CANNOT MOVE. OUTSIDE IT, IT DOES.")
    for label, text in [
        ("plain      ", "hello"),
        ("ROT13      ", rotate_letters("hello", 13)),
        ("ROT47      ", rotate_printable("hello", 47)),
        ("+0x2000    ", "".join(chr(ord(c) + 0x2000) for c in "hello")),
    ]:
        b = text.encode("utf-8")
        print(f"   {label} {len(text)} characters   {len(b):>2} UTF-8 bytes")
    print("   Rotating inside a 7-bit range is free: every result is still one byte.")
    print("   Rotate the code point instead and the same five characters cost fifteen bytes.")
    print()

    print("7. AND ROTATING THE CODE POINT LANDS WHEREVER THE ARITHMETIC SAYS")
    landed = chr(ord("h") + 0x2000)
    print(f"   'h' is U+{ord('h'):04X}.  U+{ord('h'):04X} + 0x2000 = U+{ord(landed):04X}")
    print(f"   U+{ord(landed):04X} is {unicodedata.name(landed)}")
    print("   That is not a letter. It is an invisible bidirectional formatting character,")
    print("   and it changes how everything after it is DISPLAYED.")
    print()
    print("   Worse, some destinations are not characters at all:")
    hole = chr(0xD800)
    print(f"   chr(0xD800) is a str of length {len(hole)} ...")
    try:
        hole.encode("utf-8")
    except Exception as exc:
        print(f"   ... and encoding it raises {type(exc).__name__}: U+D800 is a surrogate,")
    print("   permanently reserved, and no UTF-8 file may contain one.")
    print("   So a rotation over the whole table cannot be a sum. It needs a list of which")
    print("   code points it is allowed to produce -- which is the opposite of a one-line rule.")


if __name__ == "__main__":
    main()
