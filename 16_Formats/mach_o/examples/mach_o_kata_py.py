#!/usr/bin/env python3
"""Kata: five four-byte openings, and what each one is."""

import struct

CASES = [
    ("cf fa ed fe 07 00 00 01", "a 64-bit Mach-O written little-endian: x86-64 or arm64"),
    ("fe ed fa ce 00 00 00 12", "a 32-bit Mach-O written big-endian: PowerPC"),
    ("ca fe ba be 00 00 00 02", "a fat binary with two slices"),
    ("ca fe ba be 00 00 00 41", "a Java class file, major version 65 = Java 21"),
    ("ce fa ed fe 0c 00 00 00", "a 32-bit Mach-O written little-endian: armv7"),
]
NAMES = {0xFEEDFACE: "MH_MAGIC", 0xFEEDFACF: "MH_MAGIC_64", 0xCEFAEDFE: "MH_CIGAM", 0xCFFAEDFE: "MH_CIGAM_64"}


def main():
    print("   bytes                      read LE       verdict")
    print()
    for hexes, answer in CASES:
        b = bytes.fromhex(hexes)
        (le,) = struct.unpack_from("<I", b, 0)
        (be4,) = struct.unpack_from(">I", b, 4)
        if le in NAMES:
            name = NAMES[le]
            width = "64-bit" if name.endswith("64") else "32-bit"
            order = "little-endian" if name.startswith("MH_MAGIC") else "big-endian"
            verdict = f"{name:<12} {width}, written {order}"
        elif le == 0xBEBAFECA:
            verdict = f"cafebabe     u32 at 4 is {be4}: " + ("a fat binary" if be4 <= 30 else "a Java class")
        else:
            verdict = "not Mach-O"
        print(f"   {hexes:<26} {le:#010x}    {verdict}")
        print(f"   {'':<26} {'':<12}    {answer}")
        print()
    print("   Read LE and look the number up: four values are Mach-O and the")
    print("   spelling gives the order. 0xbebafeca is cafebabe backwards, which is")
    print("   the fat magic seen by a little-endian reader -- and then the next")
    print("   four bytes, always big-endian, say whether Java or a fat header.")


if __name__ == "__main__":
    main()
