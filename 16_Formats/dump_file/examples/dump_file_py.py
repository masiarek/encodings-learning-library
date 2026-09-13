#!/usr/bin/env python3
"""Dump File Loader: four crash-dump formats told apart by one little-endian
integer at offset 0, three of them binary and one a text file; then a
minidump's header, directory, and a module name stored as a byte length
followed by UTF-16.

Run:  python3 dump_file_py.py
"""

import struct

# The four constants Ghidra's DumpFileLoader switches on, from its source at 12.1.3.
GHIDRA = {"Minidump": 0x504D444D, "Pagedump": 0x45474150, "Userdump": 0x52455355, "Apport": 0x626F7250}
MINIDUMP_VERSION = 0xA793
ARCH = {0: "x86", 5: "ARM", 9: "AMD64", 12: "ARM64"}
STREAMS = {3: "ThreadList", 4: "ModuleList", 5: "MemoryList", 7: "SystemInfo", 9: "Memory64List"}


def spell(n):
    return struct.pack("<I", n).decode("ascii")


def minidump_string(s):
    u = s.encode("utf-16-le")
    return struct.pack("<I", len(u)) + u + b"\x00\x00"


def build():
    header_size, dir_entry = 32, 12
    streams = []
    # SystemInfo: architecture, level, revision, processors, product type, then versions.
    sysinfo = struct.pack("<HHHBBIIII", 9, 6, 0x3F03, 8, 1, 10, 0, 22631, 2) + bytes(24)
    streams.append((7, sysinfo))
    # ModuleList: a count, then one 108-byte MINIDUMP_MODULE whose ModuleNameRva points at a string.
    name_rva_placeholder = 0
    module = struct.pack("<QIIII", 0x7FF600000000, 0x20000, 0, 0, name_rva_placeholder) + bytes(108 - 24)
    streams.append((4, struct.pack("<I", 1) + module))
    names = [minidump_string("café.dll"), minidump_string("\U0001F600.dll")]
    # Lay everything out: header, directory, streams, then the strings.
    rva = header_size + dir_entry * len(streams)
    directory, body, placed = b"", b"", []
    for stream_type, data in streams:
        placed.append(rva)
        directory += struct.pack("<III", stream_type, len(data), rva)
        rva += len(data)
    names_rva = rva
    body = b"".join(data for _, data in streams)
    body = bytearray(body)
    # Patch the module's ModuleNameRva (offset 4 + 24 - 4 inside the ModuleList stream).
    module_at = placed[1] - placed[0] + 4
    struct.pack_into("<I", body, module_at + 20, names_rva)
    header = struct.pack("<4sIIIIIQ", b"MDMP", MINIDUMP_VERSION | (0x1234 << 16), len(streams), header_size, 0, 0, 0)
    return header + directory + bytes(body) + b"".join(names)


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "FOUR SIGNATURES, READ AS ONE LITTLE-ENDIAN INTEGER")
    for name, const in GHIDRA.items():
        b = struct.pack("<I", const)
        print(f"   {name:<9} constant {const:#010x}   bytes {b.hex(' ')}   spells {spell(const)!r}")
    print()
    print("   Ghidra reads a 32-bit little-endian integer at offset 0 and switches")
    print("   on it. Three are the first four bytes of a binary header -- MDMP,")
    print("   PAGE (then DUMP or DU64), USER (then DUMP). The fourth is the first")
    print("   four letters of 'ProblemType:', the first line of an Ubuntu apport")
    print("   crash report, which is a text file recognised as if it were binary.")
    print()
    for hexes, note in (("50 41 47 45 44 55 4d 50", "PAGEDUMP, a 32-bit kernel dump"), ("50 41 47 45 44 55 36 34", "PAGEDU64, a 64-bit one"),
                        ("ef bb bf 50 72 6f 62 6c", "a BOM in front of ProblemType")):
        (first,) = struct.unpack_from("<I", bytes.fromhex(hexes), 0)
        (second,) = struct.unpack_from("<I", bytes.fromhex(hexes), 4)
        hit = next((k for k, v in GHIDRA.items() if v == first), "no loader")
        print(f"   {hexes}   first int {first:#010x} -> {hit:<10} second int {second:#010x} spells {spell(second)!r:<8} {note}")
    print()
    print("   The BOM row is the text file's hazard: three invisible bytes and")
    print("   the integer compare misses. And the second word of a kernel dump")
    print("   is DUMP, 0x504d5544, or DU64, 0x34365544 -- Ghidra's source holds")
    print(f"   0x504d5444 for both, which spells {spell(0x504D5444)!r}; a comment says DUMP.")
    print()

    section(2, "THE MINIDUMP HEADER IS 32 BYTES, THEN A DIRECTORY")
    dump = build()
    sig, version, nstreams, dir_rva, checksum, stamp, flags = struct.unpack_from("<4sIIIIIQ", dump, 0)
    print(f"   {dump[:32].hex(' ')}")
    print()
    print(f"   Signature   {sig!r}")
    print(f"   Version     {version:#010x}   low word {version & 0xFFFF:#06x} = MINIDUMP_VERSION; high word {version >> 16:#06x} is the writer's")
    print(f"   Streams     {nstreams} at RVA {dir_rva}   Flags {flags:#x}")
    print()
    for i in range(nstreams):
        stream_type, size, rva = struct.unpack_from("<III", dump, dir_rva + 12 * i)
        print(f"   directory[{i}]   type {stream_type:<2} {STREAMS.get(stream_type, '?'):<12} {size:>4} bytes at RVA {rva}")
    print()
    print("   An RVA here is a plain file offset -- the dump is not mapped -- and")
    print("   every stream is found through the directory, never by position.")
    print()

    section(3, "THE ARCHITECTURE IS A 16-BIT NUMBER IN THE SYSTEMINFO STREAM")
    for i in range(nstreams):
        stream_type, size, rva = struct.unpack_from("<III", dump, dir_rva + 12 * i)
        if stream_type == 7:
            arch, level, rev, ncpu, ptype, major, minor, build_no = struct.unpack_from("<HHHBBIII", dump, rva)
            print(f"   ProcessorArchitecture {arch} = {ARCH[arch]}   level {level}  revision {rev:#x}  {ncpu} processors   Windows {major}.{minor} build {build_no}")
    print()
    print("   This is the field Ghidra's Minidump.getMachineType() returns, as a")
    print("   decimal string, to pick a language: 0 x86, 5 ARM, 9 AMD64, 12 ARM64.")
    print()

    section(4, "A MINIDUMP_STRING IS A BYTE LENGTH, THEN UTF-16LE, THEN A NUL")
    for i in range(nstreams):
        stream_type, size, rva = struct.unpack_from("<III", dump, dir_rva + 12 * i)
        if stream_type == 4:
            (count,) = struct.unpack_from("<I", dump, rva)
            base, image_size, _, _, name_rva = struct.unpack_from("<QIIII", dump, rva + 4)
            print(f"   {count} module   base {base:#x}   size {image_size:#x}   ModuleNameRva {name_rva}")
            for _ in range(2):
                (length,) = struct.unpack_from("<I", dump, name_rva)
                raw = dump[name_rva + 4:name_rva + 4 + length]
                text = raw.decode("utf-16-le")
                print(f"   at {name_rva}: Length {length:>2} bytes   {raw.hex(' ')}")
                print(f"           -> {text!r}  ({len(text)} code points, {len(raw) // 2} UTF-16 units)")
                name_rva += 4 + length + 2
    print()
    print("   Length counts BYTES of UTF-16, excluding the terminator: café.dll")
    print("   is 8 characters and 16 bytes, and the emoji name is 5 code points,")
    print("   6 units, 12 bytes. Three numbers for one name, and the field holds")
    print("   the one a C++ wchar_t buffer needs.")


if __name__ == "__main__":
    main()
