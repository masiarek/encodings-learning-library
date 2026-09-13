#!/usr/bin/env python3
"""PE: three magics, an optional header whose own magic decides its width,
and a section with two addresses.

Builds a PE32 and a PE32+ around the same one-section image and parses
both, then maps an RVA to a file offset through the section table.

Run:  python3 pe_py.py
"""

import struct

PE32, PE32PLUS = 0x10B, 0x20B
MACHINE = {0x14C: "I386", 0x8664: "AMD64", 0xAA64: "ARM64", 0x1C0: "ARM"}

# (name, PE32 letter, PE32+ letter) -- the optional header up to the directories.
OPTIONAL = [
    ("Magic", "H", "H"), ("MajorLinkerVersion", "B", "B"), ("MinorLinkerVersion", "B", "B"),
    ("SizeOfCode", "I", "I"), ("SizeOfInitializedData", "I", "I"), ("SizeOfUninitializedData", "I", "I"),
    ("AddressOfEntryPoint", "I", "I"), ("BaseOfCode", "I", "I"), ("BaseOfData", "I", None),
    ("ImageBase", "I", "Q"), ("SectionAlignment", "I", "I"), ("FileAlignment", "I", "I"),
    ("MajorOperatingSystemVersion", "H", "H"), ("MinorOperatingSystemVersion", "H", "H"),
    ("MajorImageVersion", "H", "H"), ("MinorImageVersion", "H", "H"),
    ("MajorSubsystemVersion", "H", "H"), ("MinorSubsystemVersion", "H", "H"),
    ("Win32VersionValue", "I", "I"), ("SizeOfImage", "I", "I"), ("SizeOfHeaders", "I", "I"),
    ("CheckSum", "I", "I"), ("Subsystem", "H", "H"), ("DllCharacteristics", "H", "H"),
    ("SizeOfStackReserve", "I", "Q"), ("SizeOfStackCommit", "I", "Q"),
    ("SizeOfHeapReserve", "I", "Q"), ("SizeOfHeapCommit", "I", "Q"),
    ("LoaderFlags", "I", "I"), ("NumberOfRvaAndSizes", "I", "I"),
]


def optional_layout(magic):
    col = 0 if magic == PE32 else 1
    return [(name, f[col]) for name, *f in OPTIONAL if f[col] is not None]


def build(magic, machine):
    layout = optional_layout(magic)
    values = dict(Magic=magic, MajorLinkerVersion=14, MinorLinkerVersion=0, SizeOfCode=0x200,
                  SizeOfInitializedData=0, SizeOfUninitializedData=0, AddressOfEntryPoint=0x1000,
                  BaseOfCode=0x1000, BaseOfData=0x2000, ImageBase=0x140000000 if magic == PE32PLUS else 0x400000,
                  SectionAlignment=0x1000, FileAlignment=0x200, MajorOperatingSystemVersion=6,
                  MinorOperatingSystemVersion=0, MajorImageVersion=0, MinorImageVersion=0,
                  MajorSubsystemVersion=6, MinorSubsystemVersion=0, Win32VersionValue=0,
                  SizeOfImage=0x2000, SizeOfHeaders=0x400, CheckSum=0, Subsystem=3, DllCharacteristics=0x8160,
                  SizeOfStackReserve=0x100000, SizeOfStackCommit=0x1000, SizeOfHeapReserve=0x100000,
                  SizeOfHeapCommit=0x1000, LoaderFlags=0, NumberOfRvaAndSizes=16)
    fmt = "<" + "".join(letter for _, letter in layout)
    optional = struct.pack(fmt, *(values[name] for name, _ in layout)) + bytes(16 * 8)
    stub = b"MZ" + bytes(0x3C - 2) + struct.pack("<I", 0x80)
    stub = stub.ljust(0x80, b"\x00")
    coff = struct.pack("<HHIIIHH", machine, 1, 0, 0, 0, len(optional), 0x22)
    text = struct.pack("<8sIIIIIIHHI", b".text", 0x100, 0x1000, 0x200, 0x400, 0, 0, 0, 0, 0x60000020)
    return (stub + b"PE\x00\x00" + coff + optional + text).ljust(0x400, b"\x00") + bytes(0x200)


def parse_optional(data, at):
    (magic,) = struct.unpack_from("<H", data, at)
    layout = optional_layout(magic)
    fmt = "<" + "".join(letter for _, letter in layout)
    return dict(zip((name for name, _ in layout), struct.unpack_from(fmt, data, at))), struct.calcsize(fmt)


def rva_to_offset(sections, rva):
    for name, vsize, vaddr, rawsize, rawptr in sections:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            return rawptr + (rva - vaddr), name
    return None, None


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "THREE MAGICS, AND WHERE EACH ONE IS FOUND")
    pe = build(PE32PLUS, 0x8664)
    (lfanew,) = struct.unpack_from("<I", pe, 0x3C)
    (optmagic,) = struct.unpack_from("<H", pe, lfanew + 24)
    print(f"   offset 0        {pe[:2].hex(' ')}         'MZ'      the DOS header, present in every PE")
    print(f"   offset 0x3c     {pe[0x3C:0x40].hex(' ')}   e_lfanew  = {lfanew:#x}: where the PE header starts")
    print(f"   offset {lfanew:#x}     {pe[lfanew:lfanew + 4].hex(' ')}   'PE\\0\\0'  the signature")
    print(f"   offset {lfanew:#x}+4   {pe[lfanew + 4:lfanew + 24].hex(' ')}   the COFF file header, 20 bytes")
    print(f"   offset {lfanew:#x}+24  {pe[lfanew + 24:lfanew + 26].hex(' ')}         {optmagic:#x}: the optional header's own magic")
    print()
    print("   Three signatures, and only the first is at a fixed place. The")
    print("   second is wherever a 32-bit little-endian field says, and the third")
    print("   is a number, not text: 0x10b means PE32 and 0x20b means PE32+.")
    print()

    section(2, "THE OPTIONAL HEADER'S MAGIC DECIDES ITS OWN WIDTH")
    for magic, machine in ((PE32, 0x14C), (PE32PLUS, 0x8664)):
        data = build(magic, machine)
        (lfanew,) = struct.unpack_from("<I", data, 0x3C)
        (m, nsec, _, _, _, optsize, chars) = struct.unpack_from("<HHIIIHH", data, lfanew + 4)
        fields, fixed = parse_optional(data, lfanew + 24)
        print(f"   {'PE32' if magic == PE32 else 'PE32+':<6} machine {m:#06x} {MACHINE[m]:<6} SizeOfOptionalHeader {optsize:<4} = {fixed} fixed + 16 directories x 8")
        print(f"          ImageBase {fields['ImageBase']:#x}   SizeOfStackReserve {fields['SizeOfStackReserve']:#x}"
              f"   {'has BaseOfData' if 'BaseOfData' in fields else 'no BaseOfData'}")
    print()
    print("   Same fields, two sizes: 224 and 240. PE32+ drops BaseOfData and")
    print("   widens ImageBase and the four Size...Reserve/Commit fields from 4")
    print("   bytes to 8, so every field after ImageBase sits at a different")
    print("   offset in the two layouts. The width is the optional header's own")
    print("   magic, not the machine type, which is a separate field 22 bytes")
    print("   earlier: two fields, two facts.")
    print()

    section(3, "A SECTION HAS AN ADDRESS IN THE FILE AND ANOTHER IN MEMORY")
    (lfanew,) = struct.unpack_from("<I", pe, 0x3C)
    (_, nsec, _, _, _, optsize, _) = struct.unpack_from("<HHIIIHH", pe, lfanew + 4)
    table = lfanew + 24 + optsize
    sections = []
    for i in range(nsec):
        name, vsize, vaddr, rawsize, rawptr = struct.unpack_from("<8sIIII", pe, table + 40 * i)[:5]
        short = name.rstrip(b"\x00").decode()
        sections.append((short, vsize, vaddr, rawsize, rawptr))
        print(f"   {short:<8} VirtualAddress {vaddr:#06x}  VirtualSize {vsize:#05x}"
              f"   PointerToRawData {rawptr:#06x}  SizeOfRawData {rawsize:#05x}")
    print()
    for rva in (0x1000, 0x1010, 0x2000):
        off, name = rva_to_offset(sections, rva)
        print(f"   RVA {rva:#06x}  ->  " + (f"file offset {off:#06x} in {name}" if off is not None else "no section: not in the file at all"))
    print()
    print("   AddressOfEntryPoint is an RVA, an offset from ImageBase once the")
    print("   image is mapped. The bytes for it are at a different offset in")
    print("   the file, because sections are 0x200-aligned on disk and 0x1000-")
    print("   aligned in memory. The section table is the conversion, and an")
    print("   RVA in a gap between sections is a number with no bytes behind it.")
    print()

    section(4, "THE NAME FIELD IS EIGHT BYTES AND NO TERMINATOR")
    for raw in (b".text\x00\x00\x00", b".rdata\x00\x00", b".textbss"):
        print(f"   {raw.hex(' ')}   {raw!r:<14} -> {raw.rstrip(b'\x00').decode()!r}")
    print()
    print("   Eight bytes exactly: a shorter name is NUL-padded and an eight-byte")
    print("   name has no NUL at all, so strlen() on it runs into the next field.")
    print("   COFF's escape for longer names, /offset, is on the COFF page.")


if __name__ == "__main__":
    main()
