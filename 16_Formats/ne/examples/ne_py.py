#!/usr/bin/env python3
"""NE: a 16-bit executable reached through the MZ header, with segment
offsets in sectors whose size is a shift count, and names stored as
Pascal strings -- a length byte, the bytes, an ordinal, no terminator.

Run:  python3 ne_py.py
"""

import struct

NE_MAGIC = 0x454E
EXETYPE = {1: "OS/2", 2: "Windows", 3: "European DOS 4.x", 4: "Windows/386", 5: "BOSS"}
INFO = "<HBBHHIBBHHHIIHHHHHHHHIHHHBBHHHH"     # the information block, 64 bytes, as Ghidra's InformationBlock reads it
INFO_NAMES = ["ne_magic", "ne_ver", "ne_rev", "ne_enttab", "ne_cbenttab", "ne_crc", "ne_flags_prog", "ne_flags_app",
              "ne_autodata", "ne_heap", "ne_stack", "ne_csip", "ne_sssp", "ne_cseg", "ne_cmod", "ne_cbnrestab",
              "ne_segtab", "ne_rsrctab", "ne_restab", "ne_modtab", "ne_imptab", "ne_nrestab", "ne_cmovent",
              "ne_align", "ne_cres", "ne_exetyp", "ne_flagsothers", "ne_pretthunks", "ne_psegrefbytes",
              "ne_swaparea", "ne_expver"]


def pascal(name, ordinal):
    b = name.encode("ascii")
    return bytes([len(b)]) + b + struct.pack("<H", ordinal)


def build():
    align = 4                                          # sector = 16 bytes
    ne_at = 0x80
    segments = [(0x10, 0x0100, 0x0D00, 0x0100), (0x30, 0x0020, 0x0C41, 0x0020)]   # (sector, length, flags, minalloc)
    segtab = b"".join(struct.pack("<HHHH", *s) for s in segments)
    restab = pascal("HELLO", 0) + pascal("WinMain", 1) + pascal("SayCaf", 2) + b"\x00"
    segtab_off = 64
    restab_off = segtab_off + len(segtab)
    values = dict(ne_magic=NE_MAGIC, ne_ver=5, ne_rev=1, ne_enttab=0, ne_cbenttab=0, ne_crc=0, ne_flags_prog=0,
                  ne_flags_app=0, ne_autodata=2, ne_heap=0x400, ne_stack=0x1000, ne_csip=0x00010000, ne_sssp=0x00020000,
                  ne_cseg=len(segments), ne_cmod=0, ne_cbnrestab=0, ne_segtab=segtab_off, ne_rsrctab=restab_off,
                  ne_restab=restab_off, ne_modtab=restab_off + len(restab), ne_imptab=restab_off + len(restab),
                  ne_nrestab=0, ne_cmovent=0, ne_align=align, ne_cres=0, ne_exetyp=2, ne_flagsothers=0,
                  ne_pretthunks=0, ne_psegrefbytes=0, ne_swaparea=0, ne_expver=0x030A)
    info = struct.pack(INFO, *(values[n] for n in INFO_NAMES))
    mz = b"MZ" + struct.pack("<H", 0x80) + struct.pack("<H", 1) + bytes(0x3C - 6) + struct.pack("<I", ne_at)
    mz = mz.ljust(ne_at, b"\x00")
    body = (info + segtab + restab).ljust(0x80, b"\x00")          # 0x80..0x100
    code = b"\xb8\x00\x4c\xcd\x21".ljust(0x200, b"\x90")        # 0x100..0x300: segment 1, sector 0x10
    data = ("caf" + chr(0xE9)).encode("cp1252").ljust(0x20, b"\x00")   # 0x300: segment 2, sector 0x30
    return mz + body + code + data


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    exe = build()

    section(1, "MZ FIRST, THEN e_lfanew, THEN NE")
    (lfanew,) = struct.unpack_from("<I", exe, 0x3C)
    (magic,) = struct.unpack_from("<H", exe, lfanew)
    print(f"   offset 0      {exe[:2]!r}")
    print(f"   offset 0x3c   {exe[0x3C:0x40].hex(' ')}   e_lfanew = {lfanew:#x}")
    print(f"   offset {lfanew:#x}   {exe[lfanew:lfanew + 2].hex(' ')}         {exe[lfanew:lfanew + 2]!r} = {magic:#06x}, IMAGE_NE_SIGNATURE")
    print()
    print("   The same door PE walks through, ten years earlier: a DOS header,")
    print("   a 32-bit offset at 0x3c, and a two-letter signature there.")
    print()

    section(2, "THE INFORMATION BLOCK IS 64 BYTES")
    values = dict(zip(INFO_NAMES, struct.unpack_from(INFO, exe, lfanew)))
    for n in ("ne_ver", "ne_rev", "ne_cseg", "ne_segtab", "ne_restab", "ne_align", "ne_exetyp", "ne_expver"):
        if n == "ne_align":
            extra = f"a shift count: one sector is 1 << {values[n]} = {1 << values[n]} bytes"
        elif n == "ne_exetyp":
            extra = EXETYPE[values[n]]
        elif n == "ne_expver":
            extra = f"expected Windows {values[n] >> 8}.{values[n] & 0xFF}"
        elif n == "ne_segtab":
            extra = "offset of the segment table, from the NE header"
        elif n == "ne_restab":
            extra = "offset of the resident-name table"
        else:
            extra = ""
        print(f"   {n:<14} {values[n]:#06x}  {values[n]:>6}   {extra}")
    print()

    section(3, "SEGMENT OFFSETS ARE IN SECTORS, AND THE SECTOR SIZE IS IN THE HEADER")
    shift = values["ne_align"]
    for i in range(values["ne_cseg"]):
        sector, length, flags, minalloc = struct.unpack_from("<HHHH", exe, lfanew + values["ne_segtab"] + 8 * i)
        file_off = sector << shift
        kind = "DATA" if flags & 1 else "CODE"
        print(f"   segment {i + 1}   sector {sector:#06x}  length {length:#06x}  flags {flags:#06x} {kind}   file offset {sector} << {shift} = {file_off:#x}   {exe[file_off:file_off + 5].hex(' ')}")
    print()
    print("   A 16-bit sector number times a sector size reaches 1 MB with a")
    print("   shift of 4 and 32 MB with a shift of 9, out of a 16-bit field. The")
    print("   unit is in the file, unlike MZ's pages, but it is a power of two")
    print("   written as its exponent, which is a third way to write a number.")
    print()

    section(4, "A NAME IS A LENGTH BYTE, THE BYTES, AND AN ORDINAL")
    pos = lfanew + values["ne_restab"]
    first = True
    while exe[pos]:
        n = exe[pos]
        name = exe[pos + 1:pos + 1 + n]
        (ordinal,) = struct.unpack_from("<H", exe, pos + 1 + n)
        role = "the module name (ordinal 0)" if first else f"an exported name, ordinal {ordinal}"
        print(f"   {exe[pos:pos + 3 + n].hex(' '):<32} len {n}  {name.decode('ascii')!r:<10} {role}")
        pos += 3 + n
        first = False
    print(f"   {exe[pos:pos + 1].hex():<32} a zero length ends the table")
    print()
    print("   No NUL after the name: the length byte is the delimiter, so a name")
    print("   may hold any byte and can be at most 255 long. The first entry is")
    print("   the module's own name, and each one carries an ordinal -- which is")
    print("   the number an import can use instead of the name.")
    print()

    section(5, "THE DATA SEGMENT IS BYTES IN THE CODE PAGE OF 1990")
    sector, length, *_ = struct.unpack_from("<HHHH", exe, lfanew + values["ne_segtab"] + 8)
    raw = exe[sector << shift:(sector << shift) + 5].rstrip(b"\x00")
    try:
        raw.decode("utf-8")
        utf8 = "valid"
    except UnicodeDecodeError:
        utf8 = "not valid"
    print(f"   bytes {raw.hex(' ')}   cp1252 {raw.decode('cp1252')!r}   as UTF-8: {utf8}")
    print()
    print("   A Windows 3.x program's strings are single-byte, in whatever ANSI")
    print("   code page the machine ran, and nothing in the NE header records")
    print("   which. 'e9' is é in cp1252 and an error in UTF-8.")


if __name__ == "__main__":
    main()
