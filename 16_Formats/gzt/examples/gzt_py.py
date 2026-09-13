#!/usr/bin/env python3
"""GZT: how Ghidra decides a file is one of its own -- the extension, and
eight bytes at offset 6 -- and everything that check does not look at.

Builds a packed file with 'Trace' as its content type, then damages it in
five ways and asks the same two questions of each copy.

Run:  python3 gzt_py.py
"""

import struct
import zlib

MAGIC_NUMBER = 0x2E30212634E92C20


def write_utf(s):
    b = s.encode("utf-8")           # the names here are ASCII, so UTF-8 and modified UTF-8 agree
    return struct.pack(">H", len(b)) + b


def pack(item_name, content_type, payload):
    block = struct.pack(">QI", MAGIC_NUMBER, 1) + write_utf(item_name) + write_utf(content_type)
    block += struct.pack(">iq", 0, len(payload))
    stream = b"\xac\xed\x00\x05" + bytes([0x77, len(block)]) + block
    deflated = zlib.compress(payload)[2:-4]
    local = struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0x0808, 8, 0, 0x21, 0, 0, 0, 11, 0) + b"FOLDER_ITEM"
    return stream + local + deflated + struct.pack("<IIII", 0x08074B50, zlib.crc32(payload), len(deflated), len(payload))


def is_packed_file(data):
    """ItemSerializer.isPackedFile: skip 6 bytes, read 8 as a big-endian long, compare."""
    return len(data) >= 14 and struct.unpack_from(">Q", data, 6)[0] == MAGIC_NUMBER


def gzt_loader_accepts(name, data):
    """GztLoader.isGztFile: the name must end in .gzt, then isPackedFile."""
    return name.lower().endswith(".gzt") and is_packed_file(data)


def content_type(data):
    pos = 18
    (n,) = struct.unpack_from(">H", data, pos)
    pos += 2 + n
    (n,) = struct.unpack_from(">H", data, pos)
    return data[pos + 2:pos + 2 + n].decode("ascii")


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    good = pack("session-1", "Trace", b"/01,4),*" + bytes(4088))

    section(1, "TWO QUESTIONS: THE NAME, THEN EIGHT BYTES AT OFFSET 6")
    print(f"   {good[:16].hex(' ')}")
    print(f"   offset 6..14   {good[6:14].hex(' ')}   == MAGIC_NUMBER {MAGIC_NUMBER:#x}")
    print(f"   content type   {content_type(good)!r}")
    print()
    for name in ("session-1.gzt", "session-1.GZT", "session-1.gzf", "session-1"):
        print(f"   {name:<16} accepted by the GZT loader: {gzt_loader_accepts(name, good)}")
    print()
    print("   The extension is compared case-insensitively and it is compared")
    print("   first: the bytes are not read at all for a file not named .gzt.")
    print("   The same bytes named .gzf go to the GZF loader, which asks the same")
    print("   two questions with its own extension and would then find 'Trace'")
    print("   where it expected a Program, and stop.")
    print()

    section(2, "WHAT THE EIGHT-BYTE CHECK DOES NOT LOOK AT")
    cases = [
        ("the real file", good),
        ("byte 5, the block length, set to 0xff", good[:5] + b"\xff" + good[6:]),
        ("bytes 0..4, the stream header, zeroed", bytes(4) + good[4:]),
        ("byte 4, the block tag, set to 0x7a", good[:4] + b"\x7a" + good[5:]),
        ("one byte of the magic changed", good[:6] + b"\x2f" + good[7:]),
        ("everything after byte 14 removed", good[:14]),
        ("the ZIP part removed", good[:50]),
    ]
    for label, data in cases:
        print(f"   {label:<42} isPackedFile {is_packed_file(data)}")
    print()
    print("   Six of seven pass. The check reads exactly eight bytes and nothing")
    print("   else, so the serialization header, the block length, the strings")
    print("   and the ZIP are all beyond it: a recognised file and a loadable")
    print("   file are different things, and the loader finds out which it has")
    print("   only when it hands the bytes to the database layer.")
    print()

    section(3, "THE MAGIC IS A NUMBER, AND ALSO EIGHT BYTES")
    m = struct.pack(">Q", MAGIC_NUMBER)
    print(f"   big-endian bytes   {m.hex(' ')}")
    print(f"   as text            {m.decode('latin-1')!r}")
    print(f"   read little-endian {struct.unpack('<Q', m)[0]:#x}")
    print()
    print("   0x2e30212634e92c20 is compared as a long through a big-endian")
    print("   converter, so the byte order is fixed in the reader, not the file.")
    print("   Seven of the eight bytes are printable ASCII and one, e9, is not:")
    print("   a magic chosen so that no text file starts this way at offset 6.")


if __name__ == "__main__":
    main()
