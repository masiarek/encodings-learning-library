#!/usr/bin/env python3
"""DEX: a header that names its own byte order, checksums itself twice, and
stores strings as a UTF-16 count followed by modified UTF-8.

Builds the smallest DEX this page needs -- a header, a string_ids table
and three strings -- and reads it back.

Run:  python3 dex_py.py
"""

import hashlib
import struct
import zlib

ENDIAN_CONSTANT = 0x12345678
REVERSE_ENDIAN_CONSTANT = 0x78563412
HEADER_SIZE = 0x70


def mutf8(s):
    """Modified UTF-8: NUL as c0 80, and anything above U+FFFF as two 3-byte surrogates."""
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


def uleb128(n):
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def string_data_item(s):
    return uleb128(len(s.encode("utf-16-le")) // 2) + mutf8(s) + b"\x00"


def build(strings, endian="<"):
    ids_off = HEADER_SIZE
    data_off = ids_off + 4 * len(strings)
    items, offsets, pos = b"", [], data_off
    for s in strings:
        offsets.append(pos)
        item = string_data_item(s)
        items += item
        pos += len(item)
    file_size = pos
    tail = struct.pack(endian + "I", HEADER_SIZE) + struct.pack(endian + "I", ENDIAN_CONSTANT)
    tail += struct.pack(endian + "3I", 0, 0, 0)                    # link_size link_off map_off
    tail += struct.pack(endian + "2I", len(strings), ids_off)       # string_ids
    tail += struct.pack(endian + "8I", *([0] * 8))                  # type proto field method ids
    tail += struct.pack(endian + "2I", 0, 0)                        # class_defs
    tail += struct.pack(endian + "2I", len(items), data_off)        # data
    body = struct.pack(endian + "I", file_size) + tail
    ids = b"".join(struct.pack(endian + "I", o) for o in offsets)
    rest = body + ids + items                                       # everything from offset 32
    signature = hashlib.sha1(rest).digest()
    checksum = zlib.adler32(signature + rest) & 0xFFFFFFFF
    return b"dex\n035\x00" + struct.pack(endian + "I", checksum) + signature + rest


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    strings = ["café", "\U0001F600", "a\x00b"]
    dex = build(strings)

    section(1, "THE HEADER NAMES ITS OWN BYTE ORDER")
    (tag_le,) = struct.unpack_from("<I", dex, 40)
    (tag_be,) = struct.unpack_from(">I", dex, 40)
    print(f"   magic        {dex[:8].hex(' ')}   {dex[:8]!r}")
    print(f"   endian_tag   {dex[40:44].hex(' ')}   read LE {tag_le:#010x}   read BE {tag_be:#010x}")
    print()
    print("   ENDIAN_CONSTANT is 0x12345678. A reader that gets 0x78563412 has")
    print("   read a big-endian file with a little-endian rule, and the spec")
    print("   names that value too, REVERSE_ENDIAN_CONSTANT -- the same trick as")
    print("   Mach-O's CIGAM, as a 32-bit field instead of the magic itself.")
    print()

    section(2, "TWO CHECKSUMS OVER TWO RANGES")
    (checksum,) = struct.unpack_from("<I", dex, 8)
    signature = dex[12:32]
    print(f"   checksum    at 8    {dex[8:12].hex(' ')}   adler32 of bytes 12..end   recomputed {zlib.adler32(dex[12:]) & 0xFFFFFFFF:#010x}  {'ok' if zlib.adler32(dex[12:]) & 0xFFFFFFFF == checksum else 'BAD'}")
    print(f"   signature   at 12   {signature.hex()[:24]}...   sha1 of bytes 32..end   {'ok' if hashlib.sha1(dex[32:]).digest() == signature else 'BAD'}")
    print()
    damaged = bytearray(dex)
    damaged[-2] ^= 1
    c_ok = zlib.adler32(bytes(damaged[12:])) & 0xFFFFFFFF == checksum
    s_ok = hashlib.sha1(bytes(damaged[32:])).digest() == signature
    print(f"   flip one bit in the last string      checksum {'ok' if c_ok else 'FAILS'}   signature {'ok' if s_ok else 'FAILS'}")
    damaged = bytearray(dex)
    damaged[4] = ord("9")
    c_ok = zlib.adler32(bytes(damaged[12:])) & 0xFFFFFFFF == checksum
    s_ok = hashlib.sha1(bytes(damaged[32:])).digest() == signature
    print(f"   change the version digit at byte 4   checksum {'ok' if c_ok else 'FAILS'}   signature {'ok' if s_ok else 'FAILS'}")
    print()
    print("   Each check covers everything after itself and nothing before: the")
    print("   magic and the version are inside neither, so 'dex\\n935' verifies.")
    print()

    section(3, "MODIFIED UTF-8 IS UTF-8 WITH TWO EXCEPTIONS")
    print(f"   {'string':<10} {'UTF-8':<28} {'MUTF-8':<28} note")
    for s, note in ((strings[0], "identical below U+10000, except NUL"), (strings[1], "one code point, two surrogates, six bytes"),
                    (strings[2], "NUL is c0 80, so no byte is zero")):
        u, m = s.encode("utf-8"), mutf8(s)
        print(f"   {s!r:<10} {u.hex(' '):<28} {m.hex(' '):<28} {note}")
    print()
    print("   c0 80 is an overlong sequence and a UTF-8 decoder must reject it;")
    print("   ed a0 bd is a surrogate and so must that. Modified UTF-8 wants both,")
    print("   for one reason: a string can then be NUL-terminated in C and hold")
    print("   any character. The Java class file uses the same encoding.")
    print()

    section(4, "A STRING IS A COUNT OF UTF-16 UNITS, THEN MUTF-8, THEN NUL")
    (n, ids_off) = struct.unpack_from("<2I", dex, 56)
    for i in range(n):
        (off,) = struct.unpack_from("<I", dex, ids_off + 4 * i)
        size, pos, shift = 0, off, 0
        while True:
            b = dex[pos]
            size |= (b & 0x7F) << shift
            pos += 1
            shift += 7
            if not b & 0x80:
                break
        payload = dex[pos:dex.index(b"\x00", pos)]
        print(f"   string_id[{i}] -> offset {off}   uleb128 {dex[off:pos].hex(' '):<5} = {size} UTF-16 units   {len(payload)} bytes of MUTF-8   {payload.hex(' ')}")
    print()
    print("   utf16_size is not a byte count and not a code-point count: café is")
    print("   4 and 5 bytes, the emoji is 2 and 6 bytes. And the terminator that")
    print("   ends the search is a real 00, which is why NUL inside is c0 80.")
    print()

    section(5, "ULEB128, THE LENGTH FIELD THAT GROWS")
    for v in (4, 127, 128, 300, 16384):
        print(f"   {v:>6}  ->  {uleb128(v).hex(' ')}")
    print()
    print("   Seven bits per byte, low bits first, top bit set on every byte but")
    print("   the last. 127 is one byte and 128 is two, which is the same shape")
    print("   as UTF-8 itself: the length of the length depends on the value.")


if __name__ == "__main__":
    main()
