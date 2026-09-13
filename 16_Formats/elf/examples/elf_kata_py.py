#!/usr/bin/env python3
"""Kata: four e_ident prefixes, and what each one commits the reader to."""

import struct

CASES = [
    ("7f 45 4c 46 02 01", "Linux x86-64, the usual"),
    ("7f 45 4c 46 01 02", "a 32-bit big-endian target, PowerPC or MIPS"),
    ("7f 45 4c 46 02 02", "64-bit big-endian: s390x, or SPARC64"),
    ("7f 45 4c 46 01 01", "32-bit little-endian: i386, ARM"),
]
FMT32 = "HHIIIIIHHHHHH"
FMT64 = "HHIQQQIHHHHHH"


def main():
    print("   ident (first 6)      class   data     header   struct format")
    print()
    for hexes, note in CASES:
        b = bytes.fromhex(hexes)
        cls = "64-bit" if b[4] == 2 else "32-bit"
        data = "little" if b[5] == 1 else "big"
        fmt = ("<" if b[5] == 1 else ">") + (FMT64 if b[4] == 2 else FMT32)
        size = 16 + struct.calcsize(fmt)
        print(f"   {hexes:<20} {cls:<7} {data:<8} {size:>3} bytes  {fmt!r:<20} {note}")
    print()
    print("   The answer is two bytes long. Byte 4 picks the widths and so the")
    print("   header size, 52 or 64; byte 5 picks the byte order and so the first")
    print("   character of the format string. Nothing after byte 5 is readable")
    print("   until both have been read, and nothing before it is multi-byte.")
    print()
    print("   THE TRAP: e_ehsize is in the header too, as a 16-bit number -- so a")
    print("   reader that wants the header size from e_ehsize has to know the byte")
    print("   order to read it, and it is the ident that says. 0x0040 read the")
    print(f"   wrong way round is {struct.unpack('<H', struct.pack('>H', 0x40))[0]}, which is not a header size anyone has.")


if __name__ == "__main__":
    main()
