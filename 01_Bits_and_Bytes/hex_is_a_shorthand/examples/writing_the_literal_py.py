#!/usr/bin/env python3
"""Writing a number in source: the prefix names the base, and a leading zero does not.

Run:  python3 writing_the_literal_py.py
"""


def main() -> None:
    print("1. FOUR BASES, ONE NUMBER, IN SOURCE")
    print(f"   0b1100_0011  = {0b1100_0011}      binary, 8 digits, one per bit")
    print(f"   0o303        = {0o303}      octal, 3 digits")
    print(f"   195          = {195}      decimal, the only base with no prefix")
    print(f"   0xC3         = {0xC3}      hex, 2 digits -- the byte-shaped one")
    print("   Same value four ways. The prefix is not decoration; it is the only thing")
    print("   in the line that says which base the digits are in.")
    print()

    print("2. THE UNDERSCORE IS A COMMENT YOU CAN PUT INSIDE A NUMBER")
    print(f"   0b1100_0011  = {0b1100_0011}      grouped by nibble, so you can read the two hex digits off it")
    print(f"   0xC3_A9      = {0xC3_A9}    grouped by BYTE, which is the grouping that matters here")
    print(f"   1_000_000    = {1_000_000}  grouped by thousand, the habit you already have")
    print("   The parser drops them, so they cost nothing and change nothing. Since 3.6.")
    print(f"   int('1_000')         -> {int('1_000')}    -- and int() takes them too")
    print(f"   int('0b1010_1010', 0) -> {int('0b1010_1010', 0)}    -- base 0 means 'read the prefix'")
    print()

    print("3. A LEADING ZERO IS NOT A BASE. PYTHON 3 MADE SURE OF IT")
    print("   Writing 0755 in source is a SyntaxError -- refused on purpose, not by accident.")
    print("   (The message names the fix; it is not quoted here because CPython rewords it.)")
    try:
        compile("x = 0755", "<demo>", "exec")
        print("   ...but this interpreter accepted it, which it should not have")
    except SyntaxError:
        print("   compile('x = 0755') -> SyntaxError    confirmed on this interpreter")
    print()
    print("   And the same seven characters as a STRING, which is where it still bites:")
    print(f"   int('0755')          -> {int('0755')}     base 10 by default; the zero is just a zero")
    print(f"   int('0755', 8)       -> {int('0755', 8)}     you said the base, so the zero is padding")
    try:
        int("0755", 0)
    except ValueError:
        print("   int('0755', 0)       -> ValueError   base 0 reads a prefix, and '0' is not one")
    print(f"   int('0o755', 0)      -> {int('0o755', 0)}     the prefix, spelled the way Python spells it")
    print("   Three answers from one field of seven characters. If it came out of a config")
    print("   file or a form, the base is a decision somebody has to make in the open.")


if __name__ == "__main__":
    main()
