#!/usr/bin/env python3
"""COFF: a header with no magic, section names with a decimal escape written
in ASCII, and symbol names that take one of two shapes.

Builds a one-section object with two symbols and a string table, then
reads it back the way Ghidra's CoffFileHeader, CoffSectionHeader and
CoffSymbol do.

Run:  python3 coff_py.py
"""

import struct

MACHINES = {0x14C: "I386", 0x1C0: "ARM", 0x8664: "AMD64", 0xAA64: "ARM64", 0x1F0: "POWERPC", 0x5064: "RISCV64"}
HEADER = "<HHIIIHH"          # f_magic f_nscns f_timdat f_symptr f_nsyms f_opthdr f_flags
SECTION = "<8sIIIIIIHHI"     # name vsize vaddr rawsize rawptr relocptr lineptr nreloc nline flags
SYMBOL = "<8sIhHBB"          # name value scnum type sclass numaux  (18 bytes)


def build():
    strings = b"\x00\x00\x00\x00" + b".text.startup\x00" + b"a_much_longer_symbol_name\x00"
    strings = struct.pack("<I", len(strings)) + strings[4:]
    sections = [struct.pack(SECTION, b"/4", 0, 0, 3, 0, 0, 0, 0, 0, 0x60000020)]
    symbols = [
        struct.pack(SYMBOL, b"main", 0, 1, 0x20, 2, 0),
        struct.pack("<II", 0, 18) + struct.pack("<IhHBB", 0x10, 1, 0, 3, 0),
    ]
    header = struct.pack(HEADER, 0x14C, len(sections), 0, 20 + 40 * len(sections) + 3, len(symbols), 0, 0)
    text = b"\xc3\x00\x00"
    return header + b"".join(sections) + text + b"".join(symbols) + strings


def c_string(data, at):
    return data[at:data.index(b"\x00", at)].decode("ascii")


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    obj = build()

    section(1, "THE FIRST TWO BYTES ARE A MACHINE TYPE, NOT A SIGNATURE")
    (f_magic,) = struct.unpack_from("<H", obj, 0)
    print(f"   bytes 0..2   {obj[:2].hex(' ')}   read LE {f_magic:#06x}   {MACHINES.get(f_magic, '?')}")
    print()
    for hexes in ("4c 01", "64 86", "64 aa", "00 00", "7f 45"):
        (m,) = struct.unpack("<H", bytes.fromhex(hexes))
        if m in MACHINES:
            verdict = "a machine the table knows: " + MACHINES[m]
        elif m == 0:
            verdict = "IMAGE_FILE_MACHINE_UNKNOWN: defined, and refused by a guard"
        else:
            verdict = "not in the table: not COFF"
        print(f"   {hexes}   {m:#06x}   {verdict}")
    print()
    print("   There is no magic number. A file is COFF if its first 16-bit word")
    print("   is a machine type the reader has heard of -- Ghidra's isValid() is")
    print("   that lookup, plus one guard: 0x0000 is IMAGE_FILE_MACHINE_UNKNOWN,")
    print("   which is 'defined', so a file that starts with 64 zero bytes is")
    print("   refused by hand. Every other format in this chapter says its name;")
    print("   this one says which CPU, and the reader infers the rest.")
    print()

    section(2, "THE HEADER IS 20 BYTES")
    names = ("f_magic", "f_nscns", "f_timdat", "f_symptr", "f_nsyms", "f_opthdr", "f_flags")
    values = struct.unpack_from(HEADER, obj, 0)
    print(f"   {obj[:20].hex(' ')}")
    print()
    for n, v in zip(names, values):
        print(f"   {n:<10} {v:#010x}  {v:>6}")
    print()
    print("   f_symptr is the file offset of the symbol table, f_nsyms how many")
    print("   18-byte entries it has, and the string table starts right after")
    print("   the last one. f_opthdr is 0 in an object; in a PE it is 224 or 240.")
    print()

    section(3, "A SECTION NAME IS EIGHT BYTES, OR A DECIMAL OFFSET IN ASCII")
    (_, nscns, _, symptr, nsyms, _, _) = values
    strtab = symptr + 18 * nsyms
    (strsize,) = struct.unpack_from("<I", obj, strtab)
    raw = struct.unpack_from(SECTION, obj, 20)[0]
    print(f"   name bytes   {raw.hex(' ')}   {raw!r}")
    if raw.startswith(b"/"):
        offset = int(raw.rstrip(b"\x00")[1:])
        print(f"   starts with '/', so the rest is a DECIMAL number in ASCII: {offset}")
        print(f"   string table at {strtab}, offset {offset} there -> {c_string(obj, strtab + offset)!r}")
    print()
    print("   Eight bytes hold '.text' and not '.text.startup', so a long name is")
    print("   stored in the string table and the name field holds its offset --")
    print("   as text, in base 10, in a header where every other number is")
    print("   binary. '/4' is the two ASCII bytes 2f 34, and int('4') is the read.")
    print()

    section(4, "A SYMBOL NAME HAS TWO SHAPES")
    for i in range(nsyms):
        at = symptr + 18 * i
        (first,) = struct.unpack_from("<I", obj, at)
        if first == 0:
            (offset,) = struct.unpack_from("<I", obj, at + 4)
            name = c_string(obj, strtab + offset)
            shape = f"zeroes then offset {offset}"
        else:
            name = struct.unpack_from("<8s", obj, at)[0].rstrip(b"\x00").decode("ascii")
            shape = "eight bytes in place"
        value, scnum, typ, sclass, numaux = struct.unpack_from("<IhHBB", obj, at + 8)
        print(f"   symbol {i}   {obj[at:at + 8].hex(' ')}   {shape:<24} -> {name!r}")
        print(f"             value {value:#x}  section {scnum}  type {typ:#x}  class {sclass}  aux {numaux}")
    print()
    print("   The first four bytes decide: zero means 'the next four are an")
    print("   offset', anything else means 'these eight are the name'. A name")
    print("   cannot start with a NUL, so the two shapes cannot collide -- but")
    print("   a name of exactly eight characters has no terminator at all.")
    print()

    section(5, "THE STRING TABLE'S FIRST FOUR BYTES ARE ITS OWN SIZE")
    print(f"   at {strtab}:  {obj[strtab:strtab + 4].hex(' ')}   size {strsize}, counting these four bytes")
    print(f"   contents   {obj[strtab + 4:strtab + strsize]!r}")
    print()
    print("   So the smallest string table is 04 00 00 00, and offset 4 is the")
    print("   first string. Both escapes above -- '/4' and the symbol's offset --")
    print("   point at this table, and both count from its size field.")


if __name__ == "__main__":
    main()
