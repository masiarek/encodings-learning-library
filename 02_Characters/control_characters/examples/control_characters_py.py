#!/usr/bin/env python3
"""The first 32 codes are commands to a teletype, not letters.

Run:  python3 control_characters_py.py
"""

import ctypes

NAMES = {0: "NUL", 7: "BEL", 8: "BS", 9: "TAB", 10: "LF", 11: "VT", 12: "FF", 13: "CR", 27: "ESC", 127: "DEL"}
MEANING = {
    0: "nothing — and the end of a C string",
    7: "ring the bell (a terminal still beeps)",
    8: "move back one column",
    9: "jump to the next tab stop",
    10: "line feed: move down one line  — the Unix line end",
    11: "vertical tab (nobody uses it)",
    12: "form feed: eject the page (printers still do)",
    13: "carriage return: back to column 0  — half of the Windows line end",
    27: "escape: the next bytes are a command to the terminal",
    127: "delete (punch every hole in the paper tape)",
}


def main() -> None:
    print("1. THE ONES YOU WILL MEET: code, hex, Python escape, caret, meaning")
    for code, name in NAMES.items():
        ch = chr(code)
        caret = "^?" if code == 127 else "^" + chr(code + 64)
        print(f"   {code:>3}  0x{code:02X}  {name:<4} {ch!r:<7} {caret:<3} {MEANING[code]}")
    print()

    print("2. THE CARET IS ARITHMETIC: Ctrl+letter clears bit 6, the way Shift clears bit 5")
    for letter in "IJM[":
        print(f"   Ctrl-{letter}  =  {ord(letter):#04x} & 0x1F  =  {ord(letter) & 0x1F:>2}  =  {NAMES[ord(letter) & 0x1F]}")
    print("   So ^M is CR, ^I is TAB, ^J is LF, ^[ is ESC — the caret names vim and od use.")
    print()

    print("3. THREE LINE ENDINGS, ONE FILE EACH")
    for label, text in (("Unix  LF", "one\ntwo\n"), ("Windows  CR LF", "one\r\ntwo\r\n"), ("Classic Mac  CR", "one\rtwo\r")):
        b = text.encode()
        print(f"   {label:<16} {b.hex(' '):<32} {len(b):>2} bytes  split('\\n') -> {text.split(chr(10))}")
    print("   Only LF counts as a line to split('\\n'); the CR stays glued to the word before it.")
    print()

    print("4. splitlines() KNOWS ALL OF THEM, AND MORE THAN YOU WANT")
    s = "a\nb\r\nc\rd\ve\ff\x1cg\x85h i"
    print(f"   {s!r}")
    print(f"   split('\\n')  -> {len(s.split(chr(10)))} pieces")
    print(f"   splitlines() -> {len(s.splitlines())} pieces: {s.splitlines()}")
    print("   VT, FF, FS, NEL and LINE SEPARATOR all count. A CSV with a stray \\x85 in a cell splits there.")
    print()

    print("5. NUL: PYTHON KEEPS IT, C STOPS AT IT")
    py = "ab\0cd"
    print(f"   len({py!r}) = {len(py)}   (Python: five characters, NUL is just a character)")
    libc = ctypes.CDLL(None)
    print(f"   libc strlen({py.encode()!r}) = {libc.strlen(py.encode())}   (C: the string ended at the NUL)")
    print("   Every C API you hand a Python string to sees the first half only. See the C example.")
    print()

    print("6. ESC IS STILL A LIVE PROTOCOL")
    red = "\x1b[31mred\x1b[0m"
    print(f"   {red!r}")
    print(f"   bytes: {red.encode().hex(' ')}")
    print("   ESC [ 31 m  =  'switch to red';  ESC [ 0 m  =  'reset'.  A terminal draws 3 letters; a file holds 12 bytes.")


if __name__ == "__main__":
    main()
