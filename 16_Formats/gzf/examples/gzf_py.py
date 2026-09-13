#!/usr/bin/env python3
"""GZF: the same packed-file container as a GDT with 'Program' in its
content-type field, and an item name written by Java's writeUTF -- a
16-bit count of modified-UTF-8 bytes.

Run:  python3 gzf_py.py
"""

import struct
import zlib

MAGIC_NUMBER = 0x2E30212634E92C20
TC_BLOCKDATA, TC_BLOCKDATALONG = 0x77, 0x7A


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


def write_utf(s):
    b = mutf8(s)
    if len(b) > 65535:
        raise ValueError("UTFDataFormatException: encoded string too long")
    return struct.pack(">H", len(b)) + b


def block_header(n):
    """ObjectOutputStream writes a 1-byte length up to 255 and a 4-byte one above."""
    return bytes([TC_BLOCKDATA, n]) if n <= 255 else bytes([TC_BLOCKDATALONG]) + struct.pack(">I", n)


def pack(item_name, content_type, payload):
    block = struct.pack(">QI", MAGIC_NUMBER, 1) + write_utf(item_name) + write_utf(content_type)
    block += struct.pack(">iq", 0, len(payload))
    stream = b"\xac\xed\x00\x05" + block_header(len(block)) + block
    deflated = zlib.compress(payload)[2:-4]
    local = struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0x0808, 8, 0, 0x21, 0, 0, 0, 11, 0) + b"FOLDER_ITEM"
    return stream + local + deflated + struct.pack("<IIII", 0x08074B50, zlib.crc32(payload), len(deflated), len(payload))


def magic_offset(data):
    return 6 if data[4] == TC_BLOCKDATA else 9


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "THE CONTAINER, WITH 'Program' IN THE TYPE FIELD")
    gzf = pack("hello.bin", "Program", b"/01,4),*" + bytes(4088))
    print(f"   {gzf[:16].hex(' ')}")
    print(f"   {gzf[16:32].hex(' ')}")
    print(f"   {gzf[32:50].hex(' ')}")
    pos = 18
    (n,) = struct.unpack_from(">H", gzf, pos)
    item = gzf[pos + 2:pos + 2 + n]
    pos += 2 + n
    (n,) = struct.unpack_from(">H", gzf, pos)
    ctype = gzf[pos + 2:pos + 2 + n]
    print()
    print(f"   block length {gzf[5]}   item {item!r}   content type {ctype!r}")
    print()
    print("   Byte for byte the GDT layout: the same magic at 6, and the type")
    print("   string is what says whether the ZIP holds a program, a data type")
    print("   archive or a trace. The GZF loader reads the extension and the")
    print("   magic, and finds out which it has when it unpacks.")
    print()

    section(2, "writeUTF COUNTS BYTES OF MODIFIED UTF-8")
    for name in ("hello.bin", "caf" + chr(0xE9) + ".bin", "a" + chr(0) + "b", chr(0x1F600) + ".bin"):
        w = write_utf(name)
        print(f"   {name!r:<14} {len(name):>2} chars   count {w[:2].hex(' ')} = {len(w) - 2:>2} bytes   {w[2:].hex(' ')}")
    print()
    print("   The item name is a Java String written by DataOutput.writeUTF: two")
    print("   bytes of count, then modified UTF-8, the encoding of the Java class")
    print("   file and of DEX. A NUL costs two bytes and an emoji six, and the")
    print("   count is of those bytes -- the third format here that carries it.")
    print()

    section(3, "THE COUNT IS 16 BITS, AND SO IS THE NAME'S CEILING")
    for n in (65535, 65536):
        try:
            write_utf("A" * n)
            print(f"   {n} ASCII characters   writes")
        except ValueError as e:
            print(f"   {n} ASCII characters   refused: {e}")
    print(f"   32768 {chr(0xE9)}'s               refused: {len(mutf8(chr(0xE9) * 32768))} encoded bytes")
    print()
    print("   Java throws UTFDataFormatException past 65,535 encoded bytes, so")
    print("   the longest program name a GZF can carry depends on its letters.")
    print()

    section(4, "A LONG NAME MOVES THE MAGIC")
    for name in ("hello.bin", "x" * 200, "x" * 230):
        data = pack(name, "Program", bytes(16))
        block_len = len(data) and (data[5] if data[4] == TC_BLOCKDATA else struct.unpack_from(">I", data, 5)[0])
        print(f"   name of {len(name):>3} chars   block {block_len:>3} bytes   header byte {data[4]:#04x} {'TC_BLOCKDATA    ' if data[4] == TC_BLOCKDATA else 'TC_BLOCKDATALONG'}   magic at offset {magic_offset(data)}")
    print()
    print("   ObjectOutputStream writes a block's length in one byte up to 255")
    print("   and in four above that, with a different tag. Ghidra's isPackedFile")
    print("   reads eight bytes at offset 6 unconditionally, so -- computed here,")
    print("   not tried on Ghidra -- a name long enough to push the block past")
    print("   255 bytes leaves the magic at offset 9, where the check never looks.")


if __name__ == "__main__":
    main()
