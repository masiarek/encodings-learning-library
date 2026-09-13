#!/usr/bin/env python3
"""GDT: Ghidra's packed-file container -- a Java serialization stream carrying
a 44-byte block, then a ZIP with one entry and no central directory.

Builds one the way ItemSerializer.outputItem does, then reads it back three
ways: by hand, with zipfile (which refuses), and with raw zlib (which works).

Run:  python3 gdt_py.py
"""

import io
import struct
import zipfile
import zlib

STREAM_MAGIC = b"\xac\xed"        # java.io.ObjectStreamConstants.STREAM_MAGIC
STREAM_VERSION = b"\x00\x05"
TC_BLOCKDATA = 0x77
MAGIC_NUMBER = 0x2E30212634E92C20  # ItemSerializer.MAGIC_NUMBER
FORMAT_VERSION = 1


def write_utf(s):
    """java.io.DataOutput.writeUTF: a 16-bit byte count, then modified UTF-8."""
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
    return struct.pack(">H", len(out)) + bytes(out)


def pack(item_name, content_type, file_type, payload):
    block = struct.pack(">QI", MAGIC_NUMBER, FORMAT_VERSION) + write_utf(item_name) + write_utf(content_type)
    block += struct.pack(">iq", file_type, len(payload))
    stream = STREAM_MAGIC + STREAM_VERSION + bytes([TC_BLOCKDATA, len(block)]) + block
    deflated = zlib.compress(payload)[2:-4]                       # raw deflate: no zlib header, no adler trailer
    local = struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0x0808, 8, 0, 0x21, 0, 0, 0, len(b"FOLDER_ITEM"), 0) + b"FOLDER_ITEM"
    descriptor = struct.pack("<IIII", 0x08074B50, zlib.crc32(payload), len(deflated), len(payload))
    return stream + local + deflated + descriptor


def is_packed_file(data):
    """ItemSerializer.isPackedFile: skip 6, read 8 bytes big-endian, compare."""
    return struct.unpack_from(">Q", data, 6)[0] == MAGIC_NUMBER


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    payload = b"/01,4),*" + bytes(4088)         # the shape of what a real archive holds: a buffer file, 4 KiB here
    gdt = pack("DTArchive", "Archive", 0, payload)

    section(1, "A JAVA SERIALIZATION STREAM, THEN ONE BLOCK OF DATA")
    print(f"   {gdt[:16].hex(' ')}")
    print(f"   {gdt[16:32].hex(' ')}")
    print(f"   {gdt[32:50].hex(' ')}")
    print()
    print(f"   bytes 0..4   {gdt[:4].hex(' ')}   STREAM_MAGIC ac ed, STREAM_VERSION 5: ObjectOutputStream's header")
    print(f"   byte 4       {gdt[4]:#04x}          TC_BLOCKDATA: a block of primitive data follows")
    print(f"   byte 5       {gdt[5]:#04x} = {gdt[5]}     its length in bytes")
    pos = 6
    magic, version = struct.unpack_from(">QI", gdt, pos)
    pos += 12
    (n,) = struct.unpack_from(">H", gdt, pos)
    item = gdt[pos + 2:pos + 2 + n]
    pos += 2 + n
    (n,) = struct.unpack_from(">H", gdt, pos)
    ctype = gdt[pos + 2:pos + 2 + n]
    pos += 2 + n
    file_type, length = struct.unpack_from(">iq", gdt, pos)
    pos += 12
    print(f"   bytes 6..14  {gdt[6:14].hex(' ')}   MAGIC_NUMBER {magic:#x}, big-endian")
    print(f"   then         FORMAT_VERSION {version}")
    print(f"                writeUTF item name     {item!r}   ({len(item)} bytes, after a 2-byte count)")
    print(f"                writeUTF content type  {ctype!r}")
    print(f"                fileType {file_type}   length {length} = the payload's size before compression")
    print(f"   block ends at {pos} = 6 + {gdt[5]}")
    print()
    print("   writeLong, writeInt, writeUTF: Java's DataOutput, big-endian, with")
    print("   writeUTF counting bytes of modified UTF-8 in a 16-bit field. The")
    print("   whole 44 bytes travel as one serialization block.")
    print()

    section(2, "THEN A ZIP WITH ONE ENTRY AND NO CENTRAL DIRECTORY")
    sig, ver, flags, method, _, _, crc, csize, usize, nlen, xlen = struct.unpack_from("<IHHHHHIIIHH", gdt, pos)
    name = gdt[pos + 30:pos + 30 + nlen]
    print(f"   at {pos}: local header {sig:#010x}   flags {flags:#06x}   method {method} (deflate)   entry {name!r}")
    print(f"   crc {crc:#x}  sizes {csize}/{usize}: all zero, because flag bit 3 says a data descriptor follows the data")
    print(f"   PK\\1\\2 (central directory) present: {b'PK' + bytes([1, 2]) in gdt}   PK\\5\\6 (end record) present: {b'PK' + bytes([5, 6]) in gdt}")
    print(f"   last 16 bytes  {gdt[-16:].hex(' ')}   the descriptor: PK\\7\\8, crc, compressed size, size")
    print()
    print("   ItemSerializer calls closeEntry() and flush() on a ZipOutputStream")
    print("   and never finish(): the central directory is never written. A")
    print("   stream reader that walks local headers does not need one; an")
    print("   archive reader that starts from the end cannot find anything.")
    print()

    section(3, "WHO CAN OPEN IT")
    print(f"   isPackedFile (8 bytes at offset 6 == magic)   {is_packed_file(gdt)}")
    try:
        zipfile.ZipFile(io.BytesIO(gdt[pos:]))
        print("   zipfile.ZipFile on the ZIP part               opened")
    except zipfile.BadZipFile as e:
        print(f"   zipfile.ZipFile on the ZIP part               refused: {type(e).__name__}")
    start = pos + 30 + nlen + xlen
    inflater = zlib.decompressobj(-15)
    out = inflater.decompress(gdt[start:])
    dsig, dcrc, dcs, dus = struct.unpack_from("<IIII", inflater.unused_data, 0)
    print(f"   zlib, raw deflate from byte {start}             {len(out)} bytes out; descriptor crc matches: {zlib.crc32(out) == dcrc}; size matches: {dus == length}")
    print(f"   the payload begins                            {out[:8]!r}")
    print()
    print("   Same bytes, three verdicts. The Java stream reader Ghidra uses")
    print("   reads entries in order and is satisfied; unzip and zipfile look")
    print("   for the end record first and give up; zlib does not know what a")
    print("   ZIP is and inflates what it is pointed at.")
    print()

    section(4, "WHAT A REAL ONE HOLDS")
    for name_, ctype_, length_ in (("DTArchive", "Archive", 0xCAC000), ("Archive", "Archive", 0x74000)):
        head = pack(name_, ctype_, 0, bytes(16))[:6 + 1]
        print(f"   item {name_!r:<12} content type {ctype_!r}   block length {head[5]}   length field {length_:#x} = {length_:,} bytes unpacked")
    print()
    print("   The sixteen .gdt files Ghidra 12.1.3 ships all open ac ed 00 05 77")
    print("   and then 2c or 2a -- 44 or 42 -- because 'DTArchive' is two bytes")
    print("   longer than 'Archive'. The block length is the only byte that")
    print("   varies before the magic, and the magic is what the loader reads.")


if __name__ == "__main__":
    main()
