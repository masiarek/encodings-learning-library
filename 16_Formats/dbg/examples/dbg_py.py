#!/usr/bin/env python3
"""DBG: a separate-debug header whose two-byte signature is two numbers, a
debug directory pointing at a CodeView record, and a GUID written in
three byte orders at once.

Run:  python3 dbg_py.py
"""

import struct
import uuid

HEADER = "<HHHHIIIIIIIIII"      # 48 bytes: IMAGE_SEPARATE_DEBUG_HEADER
SECTION = "<8sIIIIIIHHI"        # 40 bytes: IMAGE_SECTION_HEADER
DEBUG_DIR = "<IIHHIIII"         # 28 bytes: IMAGE_DEBUG_DIRECTORY
IMAGE_DEBUG_TYPE = {1: "COFF", 2: "CODEVIEW", 3: "FPO", 4: "MISC", 6: "FIXUP", 16: "REPRO"}


def build():
    guid = uuid.UUID("3f2504e0-4f89-11d3-9a0c-0305e82c3301")
    path = "C:\\build\\caf\u00e9.pdb".encode("utf-8") + b"\x00"
    rsds = b"RSDS" + guid.bytes_le + struct.pack("<I", 7) + path
    sections = struct.pack(SECTION, b".text", 0x1000, 0x1000, 0x1000, 0x400, 0, 0, 0, 0, 0x60000020)
    names = b"main\x00_start\x00"
    debug_dir_at = 48 + len(sections) + len(names)
    entry = struct.pack(DEBUG_DIR, 0, 0, 0, 0, 2, len(rsds), 0, debug_dir_at + 28)
    header = struct.pack(HEADER, 0x4944, 0, 0x14C, 0x102, 0, 0, 0x400000, 0x3000, 1, len(names), 28, 0x1000, 0, 0)
    return header + sections + names + entry + rsds


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    dbg = build()

    section(1, "THE SIGNATURE IS TWO BYTES, AND TWO NUMBERS")
    (le,) = struct.unpack_from("<H", dbg, 0)
    (be,) = struct.unpack_from(">H", dbg, 0)
    print(f"   bytes 0..2   {dbg[:2].hex(' ')}   {dbg[:2]!r}   little {le:#06x}   big {be:#06x}")
    print()
    print("   Microsoft's IMAGE_SEPARATE_DEBUG_SIGNATURE is 0x4944, the two")
    print("   letters read little-endian. Ghidra's SeparateDebugHeader keeps a")
    print("   second constant, 0x4449, named _MAC -- the same picture read the")
    print("   other way. Two names for one pair of bytes is the honest version.")
    print()

    section(2, "THE HEADER IS 48 BYTES OF 16- AND 32-BIT FIELDS")
    names = ("Signature", "Flags", "Machine", "Characteristics", "TimeDateStamp", "CheckSum", "ImageBase",
             "SizeOfImage", "NumberOfSections", "ExportedNamesSize", "DebugDirectorySize", "SectionAlignment",
             "Reserved[0]", "Reserved[1]")
    for n, v in zip(names, struct.unpack_from(HEADER, dbg, 0)):
        print(f"   {n:<20} {v:#010x}  {v:>8}")
    print()
    print("   Machine and Characteristics are the PE's own, copied here so the")
    print("   file can say which image it belongs to. Then NumberOfSections")
    print("   section headers, ExportedNamesSize bytes of NUL-terminated names,")
    print("   and DebugDirectorySize bytes of 28-byte directory entries.")
    print()

    section(3, "THE DEBUG DIRECTORY POINTS AT A CODEVIEW RECORD")
    (_, _, _, _, _, _, _, _, nsec, names_size, dir_size, _, _, _) = struct.unpack_from(HEADER, dbg, 0)
    at = 48 + 40 * nsec
    exported = dbg[at:at + names_size].split(b"\x00")[:-1]
    print(f"   exported names   {[n.decode('ascii') for n in exported]}")
    at += names_size
    for i in range(dir_size // 28):
        chars, stamp, major, minor, typ, size, addr, ptr = struct.unpack_from(DEBUG_DIR, dbg, at + 28 * i)
        print(f"   entry {i}   Type {typ} {IMAGE_DEBUG_TYPE[typ]:<9} SizeOfData {size}   PointerToRawData {ptr:#x}")
        record = dbg[ptr:ptr + size]
        print(f"             {record[:4]!r} {record[4:20].hex(' ')} age {struct.unpack_from('<I', record, 20)[0]}")
        path = record[24:record.index(b'\x00', 24)]
        print(f"             path bytes {path.hex(' ')}")
        print(f"             as UTF-8   {path.decode('utf-8')!r}")
        print(f"             as cp1252  {path.decode('cp1252')!r}")
    print()
    print("   RSDS is the PDB 7.0 record: signature, GUID, age, path. Nothing in")
    print("   it says which encoding the path is in -- the linker wrote whatever")
    print("   bytes it had, and 'c3 a9' is one character or two depending on")
    print("   the reader. A debugger that opens the wrong file is the bug.")
    print()

    section(4, "A GUID IS THREE BYTE ORDERS IN SIXTEEN BYTES")
    g = uuid.UUID("3f2504e0-4f89-11d3-9a0c-0305e82c3301")
    print(f"   as text        {{{str(g).upper()}}}")
    print(f"   .bytes         {g.bytes.hex(' ')}   the text, left to right")
    print(f"   .bytes_le      {g.bytes_le.hex(' ')}   what the file holds")
    print()
    print("   Data1 (4 bytes) and Data2, Data3 (2 each) are little-endian; the")
    print("   last eight are in text order. So the file's e0 04 25 3f 89 4f d3 11")
    print("   reads back as 3F2504E0-4F89-11D3 -- three fields reversed and one")
    print("   not, in one 16-byte value. Python spells the choice bytes_le.")


if __name__ == "__main__":
    main()
