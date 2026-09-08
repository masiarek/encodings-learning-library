#!/usr/bin/env python3
"""Answers for the bytes/hex/int kata.

Every number below is computed from the six bytes, never typed in.

Run:  python3 bytes_hex_and_int_kata_py.py
"""

import struct

RAW = bytes.fromhex("0000000d4948")
HEAD, TAIL = RAW[:4], RAW[4:]

print("SIX BYTES")
print("   %-38s %s" % ("the bytes", RAW.hex(" ")))
print("   %-38s %r" % ("RAW.hex()", RAW.hex()))
print("   %-38s %s" % ("bytes.fromhex(RAW.hex()) == RAW",
                       bytes.fromhex(RAW.hex()) == RAW))
print()
print("   The round trip is exact because neither call is arithmetic.")
print("   fromhex() also skips ASCII spaces, so a dump pasted straight out")
print("   of xxd goes back in:")
print("   %-38s %s" % ("bytes.fromhex('00 00 00 0d') == HEAD",
                       bytes.fromhex("00 00 00 0d") == HEAD))
print()

print("THE FIRST FOUR AS A NUMBER")
print("   %-38s %d" % ("int.from_bytes(HEAD, 'big')",
                       int.from_bytes(HEAD, "big")))
print("   %-38s %d" % ("int.from_bytes(HEAD, 'little')",
                       int.from_bytes(HEAD, "little")))
print()
print("   %-38s %d" % ("struct.unpack('>I', HEAD)[0]", struct.unpack(">I", HEAD)[0]))
print("   %-38s %d" % ("struct.unpack('<I', HEAD)[0]", struct.unpack("<I", HEAD)[0]))
print("   %-38s %s" % ("'>I' agrees with 'big':",
                       struct.unpack(">I", HEAD)[0] == int.from_bytes(HEAD, "big")))
print("   %-38s %s" % ("the smaller answer is:",
                       ">I / big" if struct.unpack(">I", HEAD)[0]
                       < struct.unpack("<I", HEAD)[0] else "<I / little"))
print()
print("   Big-endian reads the significant byte first, so three leading")
print("   zeros mean a small number. Little-endian reads them last, where")
print("   they are the TOP three bytes -- so the same four bytes become")
print("   thirteen or two hundred and eighteen million, and nothing about")
print("   the bytes prefers either reading.")
print()

print("THE LAST TWO AS TEXT")
print("   %-38s %r" % ("TAIL", TAIL))
print("   %-38s %r" % ("TAIL.decode('ascii')", TAIL.decode("ascii")))
print("   %-38s %s" % ("...and as a number, 'big':", int.from_bytes(TAIL, "big")))
print()
print("   Both readings are available and only one is intended. These six")
print("   bytes are the start of a PNG's IHDR chunk: a big-endian length")
print("   followed by a four-byte ASCII type, of which we have two letters.")
print("   A length field and a name field, side by side, distinguishable")
print("   only by a spec.")
print()

print("FOUR BYTES THAT ARE TWO NUMBERS")
FF = bytes.fromhex("ffffffff")
print("   %-38s %d" % ("int.from_bytes(FF, 'big')", int.from_bytes(FF, "big")))
print("   %-38s %d" % ("int.from_bytes(FF, 'big', signed=True)",
                       int.from_bytes(FF, "big", signed=True)))
print("   %-38s %s" % ("both round-trip to the same bytes:",
                       (int.from_bytes(FF, "big").to_bytes(4, "big") == FF)
                       and (int.from_bytes(FF, "big", signed=True)
                            .to_bytes(4, "big", signed=True) == FF)))
print()
print("   A format spec has to state THREE things before four bytes are one")
print("   number: the width, the byte order, and whether it is signed.")
print("   Miss any one and the bytes still decode -- to a different value,")
print("   with no error and no clue. The signed case is the meanest of the")
print("   three, because the two answers agree for every value below 2^31")
print("   and diverge only once the top bit is set: a counter that has been")
print("   correct for years starts reporting -1 the day it crosses over.")
print()
print("   %-38s %s" % ("2147483647 both ways agree:",
                       int.from_bytes((2147483647).to_bytes(4, "big"), "big")
                       == int.from_bytes((2147483647).to_bytes(4, "big"),
                                         "big", signed=True)))
print("   %-38s %s" % ("2147483648 both ways agree:",
                       int.from_bytes((2147483648).to_bytes(4, "big"), "big")
                       == int.from_bytes((2147483648).to_bytes(4, "big"),
                                         "big", signed=True)))
