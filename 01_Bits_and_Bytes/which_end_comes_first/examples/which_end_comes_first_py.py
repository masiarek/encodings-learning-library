#!/usr/bin/env python3
"""Two readings of the same bytes, and the default that is nobody's machine.

Run:  python3 which_end_comes_first_py.py
"""

import struct
import sys

three = bytes.fromhex("2f7505")

print("1. ONE FILE, TWO NUMBERS")
print(f"   the bytes                      {three.hex(' ')}")
big = int.from_bytes(three, "big")
little = int.from_bytes(three, "little")
print(f"   int.from_bytes(b, 'big')       {big:>9}   0x{big:06x}")
print(f"   int.from_bytes(b, 'little')    {little:>9}   0x{little:06x}")
print("   Neither call is a misreading. The bytes are the same object both times;")
print("   the number is a thing the reader made, and the file never voted.")

print()
print("2. THIS MACHINE")
print(f"   sys.byteorder                  {sys.byteorder!r}")
print("   That is what the CPU does in memory. It is NOT what the bytes in a file")
print("   do, and -- the next section -- it is not what Python does when you")
print("   decline to choose.")

print()
print("3. THE DEFAULT IS 'big', AND IT IS NOT YOUR MACHINE'S ORDER")
print(f"   int.from_bytes(b)              {int.from_bytes(three)}")
print(f"   (65).to_bytes(2).hex()         {(65).to_bytes(2).hex(' ')}")
print("   Since Python 3.11 both arguments have defaults: to_bytes(length=1,")
print("   byteorder='big'). So the reflex call is not 'whatever this machine")
print("   does' -- it is big-endian on every machine, while sys.byteorder is")
print(f"   {sys.byteorder!r} here. The two disagree, silently, and the result is a")
print("   perfectly ordinary int either way.")
print("   Before 3.11 the argument was required, which is the version most advice")
print("   about this was written against.")

print()
print("4. struct: FIVE PREFIXES, AND ONLY TWO OF THEM NAME AN ORDER")
n = 0x2F7505
for prefix, what in [
    ("<", "little-endian, no padding"),
    (">", "big-endian, no padding"),
    ("!", "network order -- a synonym for >"),
    ("=", "this machine's order, no padding"),
    ("@", "this machine's order AND its alignment (the default)"),
]:
    packed = struct.pack(prefix + "I", n)
    print(f"   {prefix}I  {packed.hex(' '):<12} {what}")
print("   '!' and '>' produce the same bytes because network byte order IS")
print("   big-endian; the name is the only difference. '=' and '@' differ from")
print("   each other in padding, not in order, which is why a struct that looks")
print("   portable because it says '=' is still this machine's opinion.")
print(f"   struct.calcsize('@ci') = {struct.calcsize('@ci')}, struct.calcsize('=ci') = {struct.calcsize('=ci')}"
      "   <- the padding, not the order")

print()
print("5. THE FAILURE HAS NO EXCEPTION IN IT")
written = n.to_bytes(4, "little")
read_back = int.from_bytes(written, "big")
print(f"   wrote {n} little-endian   -> {written.hex(' ')}")
print(f"   read it back big-endian       -> {read_back}")
print(f"   {n} became {read_back}. No error, no warning, no clue:")
print("   every byte string is a valid number in both orders, so a mismatch")
print("   cannot raise. It can only be wrong. That is the whole reason a format")
print("   specification has to say which end, and why 'the field is four bytes'")
print("   is not a specification.")
