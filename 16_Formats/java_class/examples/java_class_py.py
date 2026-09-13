#!/usr/bin/env python3
"""Java class file: big-endian throughout, a constant pool counted from 1
in which two kinds of entry take two slots, and strings in modified
UTF-8 with a 16-bit byte count.

Builds a constant pool by hand, encodes the string javac was given on
this page, and compares the bytes with what javac 25 wrote.

Run:  python3 java_class_py.py
"""

import struct

MAJORS = {45: "1.1", 49: "5", 52: "8", 55: "11", 61: "17", 65: "21", 69: "25"}
TAGS = {1: "Utf8", 3: "Integer", 5: "Long", 6: "Double", 7: "Class", 8: "String", 10: "Methodref", 12: "NameAndType"}


def mutf8(s):
    out = bytearray()
    for ch in s:
        c = ord(ch)
        if c == 0:
            out += b"\xc0\x80"
        elif c < 0x80:
            out.append(c)
        elif c < 0x800:
            out += bytes([0xC0 | c >> 6, 0x80 | c & 0x3F])
        elif c < 0x10000:
            out += bytes([0xE0 | c >> 12, 0x80 | c >> 6 & 0x3F, 0x80 | c & 0x3F])
        else:
            c -= 0x10000
            for unit in (0xD800 | c >> 10, 0xDC00 | c & 0x3FF):
                out += bytes([0xE0 | unit >> 12, 0x80 | unit >> 6 & 0x3F, 0x80 | unit & 0x3F])
    return bytes(out)


def cp_utf8(s):
    b = mutf8(s)
    return struct.pack(">BH", 1, len(b)) + b


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "MAGIC, THEN MINOR, THEN MAJOR, ALL BIG-ENDIAN")
    head = bytes.fromhex("ca fe ba be 00 00 00 45")
    magic, minor, major = struct.unpack(">IHH", head)
    print(f"   {head.hex(' ')}   magic {magic:#x}   minor {minor}   major {major} = Java {MAJORS[major]}")
    print()
    for m in (45, 52, 61, 65, 69):
        print(f"   major {m}  Java {MAJORS[m]:<4}  bytes {struct.pack('>H', m).hex(' ')}")
    print()
    print("   The class file is big-endian from the first byte to the last, by")
    print("   specification; no field says so and no field could be read before")
    print("   deciding it. Read as little-endian the version is 0x4500 = 17664.")
    print()

    section(2, "A CONSTANT_Utf8 IS A 16-BIT BYTE COUNT AND MODIFIED UTF-8")
    s = "caf\u00e9\x00\U0001F600"
    entry = cp_utf8(s)
    javac = bytes.fromhex("01 00 0d 63 61 66 c3 a9 c0 80 ed a0 bd ed b8 80")
    print(f"   the string      {s!r}   {len(s)} code points, {len(s.encode('utf-8'))} bytes of UTF-8")
    print(f"   built here      {entry.hex(' ')}")
    print(f"   javac 25 wrote  {javac.hex(' ')}")
    print(f"   identical       {entry == javac}")
    print()
    print("   tag 01, length 00 0d = 13 bytes: café is five, the NUL is c0 80,")
    print("   and the emoji is two surrogates of three bytes each. The length")
    print("   counts bytes of MUTF-8, not characters and not UTF-16 units -- a")
    print("   third answer to 'how long is this string', beside DEX's and C's.")
    print()

    section(3, "THE POOL IS COUNTED FROM 1, AND TWO KINDS TAKE TWO SLOTS")
    pool = [cp_utf8("Hello"), struct.pack(">BH", 7, 1), struct.pack(">Bq", 5, 1), cp_utf8("x"), struct.pack(">BH", 8, 4)]
    slots = 1 + sum(2 if e[0] in (5, 6) else 1 for e in pool)
    data = struct.pack(">H", slots) + b"".join(pool)
    print(f"   constant_pool_count   {data[:2].hex(' ')} = {slots}   (entries + 1, and a Long counts twice)")
    print()
    pos, index = 2, 1
    while index < slots:
        tag = data[pos]
        if tag == 1:
            (n,) = struct.unpack_from(">H", data, pos + 1)
            desc, size = f"length {n}  {data[pos + 3:pos + 3 + n]!r}", 3 + n
        elif tag in (7, 8):
            (ref,) = struct.unpack_from(">H", data, pos + 1)
            desc, size = f"-> #{ref}", 3
        elif tag == 5:
            (v,) = struct.unpack_from(">q", data, pos + 1)
            desc, size = f"{v}", 9
        print(f"   #{index:<3} {TAGS[tag]:<11} {desc}")
        if tag in (5, 6):
            print(f"   #{index + 1:<3} {'(unusable)':<11} the second half of the Long: no entry may use this index")
            index += 1
        pos += size
        index += 1
    print()
    print("   #0 does not exist, and the count is one more than the last index.")
    print("   The JVM specification calls the two-slot rule 'a poor choice' in")
    print("   its own words, and keeps it, because every class file has it.")
    print()

    section(4, "THE LENGTH FIELD IS 16 BITS OF BYTES")
    for text, n in (("A", 65535), ("é", 32767), ("😀", 10922), ("日", 21845)):
        b = mutf8(text * n)
        print(f"   {text!r} x {n:<6} {len(b):>6} bytes   {'fits' if len(b) <= 65535 else 'does not fit'}")
    print()
    print("   65,535 is the ceiling in BYTES, so how many characters fit depends")
    print("   on which characters: 65,535 of A, 32,767 of é, 10,922 emoji. A")
    print("   string constant longer than that is a compile error, not a runtime")
    print("   one, and the limit is measured after encoding.")


if __name__ == "__main__":
    main()
