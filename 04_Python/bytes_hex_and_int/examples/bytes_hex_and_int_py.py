#!/usr/bin/env python3
"""Four conversions, and the one argument that used to be compulsory.

Chapter 1 established that the same run of hex digits is two different objects
-- a NUMBER, where width is nothing and a leading zero is noise, and a BYTE
STRING, where width IS the data and a leading zero is a NUL. This file is the
Python door onto that: bytes.hex and bytes.fromhex move between bytes and
their picture, int.from_bytes and int.to_bytes move between bytes and a
number, and struct does all four at once against a template.

The PNG header at the end is built here rather than read off disk -- the CRC
is computed, not asserted -- so nothing in this program depends on a file
existing or on which machine ran it.

Run:  python3 bytes_hex_and_int_py.py
"""

import struct
import zlib

RULE = "-" * 72
W = 40

# From the cast: e-acute is C3 A9 in UTF-8. Two bytes, so it has a byte order.
EACUTE = "é".encode("utf-8")

print("1. BYTES AND THEIR PICTURE")
print(RULE)
print("   bytes.hex() and bytes.fromhex() are inverses, and neither one is a")
print("   number: they move between some bytes and a written-down picture of")
print("   the same bytes, digit for digit, in order.")
print()
print("     %-*s %s" % (W, "EACUTE = 'e-acute'.encode('utf-8')", EACUTE))
print("     %-*s %r" % (W, "EACUTE.hex()", EACUTE.hex()))
print("     %-*s %s" % (W, "bytes.fromhex('c3a9') == EACUTE",
                        bytes.fromhex("c3a9") == EACUTE))
print()
print("   The separator argument groups the picture without changing it, and")
print("   the SIGN of the group width is the direction: positive counts from")
print("   the RIGHT, negative from the left. On an odd number of bytes that")
print("   decides where the short group lands, which the grouping page works")
print("   through in full:")
print()
five = bytes.fromhex("0001e240ff")
for args, why in (((" ",), "one byte at a time"),
                  ((" ", 2), "short group first"),
                  ((" ", -2), "short group last")):
    shown = ", ".join(repr(a) for a in args)
    print("     %-20s %-16s %s" % ("b.hex(%s)" % shown, five.hex(*args), why))
print()
print("   Same five bytes every time. Only the spaces moved, and the spaces")
print("   are not in the data.")
print()

print("2. BYTES AND A NUMBER")
print(RULE)
print("   int.from_bytes() reads bytes as one integer, and the byte order is")
print("   the whole question. Two bytes, two readings:")
print()
print("     %-*s %d" % (W, "int.from_bytes(EACUTE, 'big')",
                        int.from_bytes(EACUTE, "big")))
print("     %-*s %d" % (W, "int.from_bytes(EACUTE, 'little')",
                        int.from_bytes(EACUTE, "little")))
print()
print("   Neither is right. They are answers to different questions, and the")
print("   bytes do not say which one you meant -- that is what a format spec")
print("   is for.")
print()
print("   Going back the other way, the LENGTH is the other half of the same")
print("   point. One number, four widths:")
print()
n = 123456
for size in (3, 4, 8):
    print("     %-*s %s" % (W, "(%d).to_bytes(%d, 'big')" % (n, size),
                            n.to_bytes(size, "big").hex(" ")))
try:
    n.to_bytes(2, "big")
except OverflowError as exc:
    print("     %-*s %s" % (W, "(%d).to_bytes(2, 'big')" % n, type(exc).__name__))
print()
print("   The leading zeros are not decoration. As a NUMBER 123456 has no")
print("   width; as a field in a file it has exactly the width the format")
print("   says, and the zeros are bytes that must be written.")
print()

print("3. THE ARGUMENT THAT STOPPED BEING COMPULSORY")
print(RULE)
print("   For nine years byteorder had no default. You could not call")
print("   int.from_bytes without answering the question, which is the kind of")
print("   API that prevents a bug rather than documenting one.")
print()
print("   Python 3.11 gave it one, and the default is 'big':")
print()
no_arg = int.from_bytes(EACUTE)
print("     %-*s %d" % (W, "int.from_bytes(EACUTE)", no_arg))
print("     %-*s %s" % (W, "...same as 'big':", no_arg == int.from_bytes(EACUTE, "big")))
print("     %-*s %s" % (W, "...same as 'little':",
                        no_arg == int.from_bytes(EACUTE, "little")))
print("     %-*s %s" % (W, "(255).to_bytes()", (255).to_bytes().hex()))
print()
print("   On Python 3.10 and earlier the first line is a TypeError. So the")
print("   guard is gone, the question is not, and it is now yours to")
print("   remember: write the byte order down even where the default would")
print("   have done, because the reader of your code cannot tell a deliberate")
print("   big-endian from a forgotten argument.")
print()

print("4. NEGATIVE NUMBERS ARE ONE MORE ARGUMENT")
print(RULE)
print("   signed=True is two's complement, spelled as a keyword:")
print()
print("     %-*s %s" % (W, "(-1).to_bytes(4, 'big', signed=True)",
                        (-1).to_bytes(4, "big", signed=True).hex(" ")))
print("     %-*s %s" % (W, "(-2).to_bytes(4, 'big', signed=True)",
                        (-2).to_bytes(4, "big", signed=True).hex(" ")))
print("     %-*s %s" % (W, "(1).to_bytes(4, 'big', signed=True)",
                        (1).to_bytes(4, "big", signed=True).hex(" ")))
print()
ff = bytes.fromhex("ffffffff")
print("   And the same four bytes read both ways -- which is why a format")
print("   spec has to say signed or unsigned, and why getting it wrong gives")
print("   you a number instead of an error:")
print()
print("     %-*s %d" % (W, "int.from_bytes(ff, 'big')",
                        int.from_bytes(ff, "big")))
print("     %-*s %d" % (W, "int.from_bytes(ff, 'big', signed=True)",
                        int.from_bytes(ff, "big", signed=True)))
print()
try:
    (-1).to_bytes(4, "big")
except OverflowError as exc:
    print("     %-*s %s" % (W, "(-1).to_bytes(4, 'big')", type(exc).__name__))
print("     Unsigned refuses a negative, which is the one place the")
print("     conversion does check up on you.")
print()

print("5. struct IS THE SAME FOUR WITH A TEMPLATE")
print(RULE)
print("   The first character of a struct format is the byte order, and it is")
print("   the first thing to read in any format string you meet:")
print()
value = 0x0001E240
print("     %-*s %s" % (W, "hex(value)", hex(value)))
print()
print("     %-8s %-26s %s" % ("format", "packed bytes", "meaning"))
for fmt, why in (("<I", "little-endian, 4 bytes"),
                 (">I", "big-endian, 4 bytes"),
                 ("<H", "little-endian, 2 bytes"),
                 (">Q", "big-endian, 8 bytes")):
    try:
        shown = struct.pack(fmt, value).hex(" ")
    except struct.error:
        shown = "struct.error"
        why = "the value does not fit"
    print("     %-8s %-26s %s" % (fmt, shown, why))
print()
print("     %-*s %s" % (W, "struct.calcsize('<I')", struct.calcsize("<I")))
print("     %-*s %s" % (W, "struct.calcsize('<HH')", struct.calcsize("<HH")))
print("     %-*s %s" % (W, "struct.unpack('>I', pack('>I', v))",
                        struct.unpack(">I", struct.pack(">I", value))[0] == value))
print()
print("   Leave the byte-order character off and you get NATIVE order plus")
print("   native alignment padding, which is a different size on a different")
print("   machine. In a file format that is always a bug:")
print()
print("     %-*s %d" % (W, "struct.calcsize('=HI')  (no padding)",
                        struct.calcsize("=HI")))
print("     %-*s %d" % (W, "struct.calcsize('HI')   (native, padded)",
                        struct.calcsize("HI")))
print("     %-*s %d" % (W, "struct.calcsize('<HI')  (explicit)",
                        struct.calcsize("<HI")))
print()
print("   The middle row is two bytes of padding you did not ask for and")
print("   cannot see. Which order 'native' means is sys.byteorder, and it is")
print("   a fact about the machine rather than about your data -- which is")
print("   why it is named here rather than printed: an answer key that")
print("   recorded it would be recording the runner.")
print()

print("6. A REAL HEADER, BUILT AND THEN READ BACK")
print(RULE)
print("   The first 16 bytes of a PNG. Everything below is computed here --")
print("   the length, the CRC -- so it is a real header rather than a quoted")
print("   one:")
print()
signature = b"\x89PNG\r\n\x1a\n"
ihdr_body = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
chunk = (struct.pack(">I", len(ihdr_body)) + b"IHDR" + ihdr_body
         + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_body)))
png = signature + chunk

print("     %s" % png[:8].hex(" "))
print("     %s" % png[8:16].hex(" "))
print()
print("   Field by field:")
print()
print("     %-14s %-26s %s" % ("bytes", "field", "value"))
print("     %-14s %-26s %s" % (signature.hex(" ")[:11] + "..", "PNG signature", "8 bytes, fixed"))
print("     %-14s %-26s %d" % (png[8:12].hex(" "), "chunk length (>I)",
                               struct.unpack(">I", png[8:12])[0]))
print("     %-14s %-26s %s" % (png[12:16].hex(" "), "chunk type (4 ASCII)",
                               png[12:16].decode("ascii")))
w, h, depth, colour, comp, filt, inter = struct.unpack(">IIBBBBB", png[16:29])
print("     %-14s %-26s %d" % (png[16:20].hex(" "), "width (>I)", w))
print("     %-14s %-26s %d" % (png[20:24].hex(" "), "height (>I)", h))
print("     %-14s %-26s %d" % (png[24:25].hex(" "), "bit depth (B)", depth))
print("     %-14s %-26s %d" % (png[25:26].hex(" "), "colour type (B)", colour))
print("     %-14s %-26s %s" % (png[29:33].hex(" "), "CRC-32 of type+body",
                               "checks: %s" % (
                                   struct.unpack(">I", png[29:33])[0]
                                   == zlib.crc32(png[12:29]))))
print()
print("   PNG is big-endian throughout, which is why every length above is")
print("   '>I'. Read it as '<I' and the 13-byte header announces itself as")
print("   %d bytes:" % struct.unpack("<I", png[8:12])[0])
print()
print("     %-*s %d" % (W, "struct.unpack('>I', png[8:12])",
                        struct.unpack(">I", png[8:12])[0]))
print("     %-*s %d" % (W, "struct.unpack('<I', png[8:12])",
                        struct.unpack("<I", png[8:12])[0]))
print()

print("7. AND THE SIGNATURE IS AN ENCODING TEST")
print(RULE)
print("   Those first eight bytes are not a magic number somebody liked. Six")
print("   of the eight are there to catch a file that was TRANSFORMED in")
print("   transit, and two of them are this library's subject exactly:")
print()
reasons = [
    ("high bit set: dies if the path is 7-bit clean", 1),
    ("P", 1), ("N", 1), ("G", 1),
    ("CR: gone if LF was translated to CRLF", 1),
    ("LF: gone if CRLF was translated to LF", 1),
    ("DOS end-of-file, so TYPE stops here", 1),
    ("LF again, catching the reverse translation", 1),
]
i = 0
for why, n in reasons:
    print("     %-8s %s" % (signature[i:i + n].hex(), why))
    i += n
print()
print("   A PNG that went through an FTP client in text mode arrives with its")
print("   CR/LF pair rewritten and fails on byte five, before any decoder has")
print("   to guess what went wrong. That is a file format defending itself")
print("   against the line-ending problem -- the same one that turns a CSV")
print("   into a column of blank rows.")
