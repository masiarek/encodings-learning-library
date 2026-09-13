#!/usr/bin/env python3
"""Raw Binary: the loader that accepts every file and asks the reader for
everything a header would have said -- and why a base address is not a
detail.

Run:  python3 raw_binary_py.py
"""

import struct

BASE = 0x08000000


def build():
    """Four pointers, then the four strings they point at, laid out for one base."""
    strings = ["café".encode() + b"\x00", b"hello\x00", b"\xc5\xbc\x00", b"ok\x00"]
    table = bytearray()
    offset = 16
    for s in strings:
        table += struct.pack("<I", BASE + offset)
        offset += len(s)
    return bytes(table) + b"".join(strings)


def read_string(blob, base, pointer):
    off = pointer - base
    if not 0 <= off < len(blob):
        return None
    end = blob.find(b"\x00", off)
    return blob[off:end if end >= 0 else len(blob)]


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "FOUR BYTES, AND WHAT EACH READING MAKES OF THEM")
    b = bytes.fromhex("00 00 80 3f")
    for fmt, label in (("<I", "u32 little"), (">I", "u32 big"), ("<i", "i32 little"), ("<f", "f32 little"),
                       (">f", "f32 big"), ("<HH", "two u16 little"), (">HH", "two u16 big"), ("4B", "four bytes")):
        v = struct.unpack(fmt, b)
        print(f"   {label:<16} {fmt!r:<7} {v[0] if len(v) == 1 else v}")
    print()
    print("   00 00 80 3f is 1.0 as a little-endian float and 32,831 as a big-")
    print("   endian one; 1,065,353,216 or 32,831 as an integer. Every other")
    print("   loader here has a header that picks one row. Raw Binary has a")
    print("   dropdown, and the reader picks.")
    print()

    section(2, "A POINTER IS A POINTER UNDER ONE BASE")
    blob = build()
    print(f"   {len(blob)} bytes: a table of four 32-bit little-endian values, then four strings")
    print(f"   {blob[:16].hex(' ')}")
    print(f"   {blob[16:].hex(' ')}")
    print()
    pointers = struct.unpack("<4I", blob[:16])
    for base in (BASE, 0, BASE + 0x100, BASE - 4):
        got = []
        for p in pointers:
            s = read_string(blob, base, p)
            got.append("out of range" if s is None else repr(s.decode("utf-8", "replace")))
        print(f"   base {base:#010x}   {', '.join(got)}")
    print()
    print("   The same 16 bytes of table read four ways. Under the base the file")
    print("   was built for, every value lands on a string. Under base 0 they")
    print("   point 128 MB past the end; four bytes lower, each lands four bytes")
    print("   into its string. The file does not say which base is right, and")
    print("   the loader has no way to tell a pointer from a number.")
    print()

    section(3, "THE DIALOG'S FIELDS ARE A SLICE AND A PLACEMENT")
    for file_offset, length, base in ((0, len(blob), BASE), (16, 20, BASE + 16), (16, 5, 0x1000)):
        piece = blob[file_offset:file_offset + length]
        print(f"   File Offset {file_offset:<3} Length {length:<3} Base Address {base:#010x}   -> {len(piece)} bytes at {base:#x}..{base + len(piece) - 1:#x}   {piece[:8].hex(' ')}{' ...' if len(piece) > 8 else ''}")
    print()
    print("   File Offset and Length cut the file; Base Address says where the")
    print("   cut goes; Block Name and Overlay name the result. Nothing is")
    print("   parsed, so nothing can be wrong, and nothing can be checked.")
    print()

    section(4, "WHAT EVERY OTHER FORMAT HERE WOULD HAVE SAID")
    rows = [("which end", "ELF byte 5, a Mach-O magic, PE by decree", "the language's, chosen from a list"),
            ("how wide", "ELF byte 4, the PE optional magic", "the language's"),
            ("where it loads", "e_entry, ImageBase, a mapping table", "Base Address, typed in"),
            ("what it is", "a magic number", "nothing: every file qualifies")]
    print(f"   {'question':<16} {'a header answers with':<42} Raw Binary answers with")
    for q, h, r in rows:
        print(f"   {q:<16} {h:<42} {r}")
    print()
    print("   Ghidra's BinaryLoader is an UNTARGETED_LOADER: it appears in the")
    print("   list for any file, last, with no opinion. It is the only loader")
    print("   whose acceptance test is empty, and the only one that cannot be")
    print("   wrong about a file, because it claims nothing about it.")


if __name__ == "__main__":
    main()
