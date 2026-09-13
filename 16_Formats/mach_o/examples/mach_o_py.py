#!/usr/bin/env python3
"""Mach-O: the magic is written in the file's own byte order, and a fat
binary wraps little-endian slices in a big-endian header.

Builds a 64-bit x86-64 header with one segment, wraps it with an arm64 twin
in a fat header, and reads everything back the way a loader has to.

Run:  python3 mach_o_py.py
"""

import struct

MH_MAGIC, MH_MAGIC_64 = 0xFEEDFACE, 0xFEEDFACF
MH_CIGAM, MH_CIGAM_64 = 0xCEFAEDFE, 0xCFFAEDFE
FAT_MAGIC = 0xCAFEBABE
CPU_ARCH_ABI64 = 0x01000000
CPU_TYPE_X86, CPU_TYPE_ARM = 7, 12
CPU_TYPE_X86_64 = CPU_ARCH_ABI64 | CPU_TYPE_X86   # 0x01000007
CPU_TYPE_ARM64 = CPU_ARCH_ABI64 | CPU_TYPE_ARM    # 0x0100000c
MH_EXECUTE = 2
LC_SEGMENT_64 = 0x19
LC_LOAD_DYLINKER = 0xE

MAGICS = {MH_MAGIC: "MH_MAGIC     32-bit, this reader's order",
          MH_MAGIC_64: "MH_MAGIC_64  64-bit, this reader's order",
          MH_CIGAM: "MH_CIGAM     32-bit, the other order",
          MH_CIGAM_64: "MH_CIGAM_64  64-bit, the other order"}


def segment_64(name, vmaddr, vmsize, fileoff, filesize):
    segname = name.encode("ascii").ljust(16, b"\x00")
    return struct.pack("<II16sQQQQIIII", LC_SEGMENT_64, 72, segname, vmaddr, vmsize,
                       fileoff, filesize, 5, 5, 0, 0)


def load_dylinker(path):
    body = path.encode("ascii") + b"\x00"
    size = 12 + len(body)
    size += (-size) % 8                       # load commands are 8-byte aligned in a 64-bit file
    return struct.pack("<III", LC_LOAD_DYLINKER, size, 12) + body.ljust(size - 12, b"\x00")


def macho_64(cputype, cpusubtype, order="<"):
    cmds = segment_64("__TEXT", 0x100000000, 0x4000, 0, 0x4000) + load_dylinker("/usr/lib/dyld")
    header = struct.pack(order + "IiiIIIII", MH_MAGIC_64, cputype, cpusubtype, MH_EXECUTE,
                         2, len(cmds), 0x00200085, 0)
    return header + cmds


def fat(slices):
    """slices: list of (cputype, cpusubtype, bytes). Every field big-endian."""
    align = 12                                 # 2**12: each slice starts on a 4 KiB boundary
    out = struct.pack(">II", FAT_MAGIC, len(slices))
    offset = 4096
    archs, bodies = b"", b""
    for cputype, cpusubtype, body in slices:
        archs += struct.pack(">iiIII", cputype, cpusubtype, offset, len(body), align)
        bodies += body.ljust(4096, b"\x00")
        offset += 4096
    out += archs
    return out.ljust(4096, b"\x00") + bodies


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "ONE MAGIC, TWO SPELLINGS, FOUR CONSTANTS")
    for label, order in (("written on x86 (little)", "<"), ("written on PowerPC (big)", ">")):
        b = struct.pack(order + "I", MH_MAGIC_64)
        (as_le,) = struct.unpack("<I", b)
        print(f"   {label:<26} {b.hex(' ')}   read LE {as_le:#010x}   {MAGICS[as_le]}")
    print()
    print("   The value is 0xfeedfacf in both files. A reader that always reads")
    print("   little-endian sees it forwards on one and backwards on the other,")
    print("   and 'backwards' has a name: CIGAM. Ghidra reads the four bytes LE")
    print("   and accepts all four constants, so the spelling IS the byte order.")
    print()

    section(2, "A 64-BIT HEADER IS 32 BYTES, THEN THE LOAD COMMANDS")
    x86 = macho_64(CPU_TYPE_X86_64, 3)
    fields = struct.unpack_from("<IiiIIIII", x86, 0)
    names = ("magic", "cputype", "cpusubtype", "filetype", "ncmds", "sizeofcmds", "flags", "reserved")
    print(f"   bytes 0..32   {x86[:16].hex(' ')}")
    print(f"                 {x86[16:32].hex(' ')}")
    print()
    for name, value in zip(names, fields):
        extra = ""
        if name == "cputype":
            extra = f"   CPU_ARCH_ABI64 | 7: the high byte says 64-bit, the low byte says x86"
        if name == "filetype":
            extra = "   MH_EXECUTE"
        print(f"   {name:<12} {value:#010x}  {value:>10}{extra}")
    print()
    cmd, cmdsize, segname = struct.unpack_from("<II16s", x86, 32)
    print(f"   load command 1   cmd {cmd:#x} LC_SEGMENT_64   cmdsize {cmdsize}")
    print(f"   segname          {segname.hex(' ')}")
    stripped = segname.rstrip(b"\x00").decode()
    print(f"                    {segname!r}  -> {stripped!r}")
    print("   Sixteen bytes, NUL-padded, never NUL-terminated if the name is 16")
    print("   long: strip the padding, do not read to a NUL.")
    cmd, cmdsize, name_off = struct.unpack_from("<III", x86, 32 + 72)
    path_start = 32 + 72 + name_off
    path = x86[path_start:x86.index(b"\x00", path_start)]
    print(f"   load command 2   cmd {cmd:#x} LC_LOAD_DYLINKER   cmdsize {cmdsize}   name offset {name_off}")
    print(f"   the path         {path.decode()!r}, NUL-terminated at {name_off} bytes into the command")
    print()

    section(3, "A FAT HEADER IS BIG-ENDIAN, WHATEVER IS INSIDE IT")
    arm = macho_64(CPU_TYPE_ARM64, 0)
    universal = fat([(CPU_TYPE_X86_64, 3, x86), (CPU_TYPE_ARM64, 0, arm)])
    magic, nfat = struct.unpack_from(">II", universal, 0)
    print(f"   bytes 0..8      {universal[:8].hex(' ')}   magic {magic:#x}   nfat_arch {nfat}")
    print()
    print(f"   {'slice':<6} {'cputype':<12} {'subtype':<8} {'offset':<8} {'size':<6} {'align':<6} first bytes of the slice")
    for i in range(nfat):
        cputype, sub, off, size, align = struct.unpack_from(">iiIII", universal, 8 + 20 * i)
        head = universal[off:off + 4]
        print(f"   {i:<6} {cputype:#010x}   {sub:<8} {off:<8} {size:<6} 2^{align:<3} {head.hex(' ')}")
    print()
    print("   Two byte orders in one file: the fat header and its arch table are")
    print("   big-endian on every machine, and each slice inside is a whole")
    print("   Mach-O in its own order -- here cf fa ed fe, little-endian, twice.")
    print()

    section(4, "CAFEBABE IS ALSO A JAVA CLASS, AND OFFSET 4 SETTLES IT")
    java = bytes.fromhex("ca fe ba be 00 00 00 45")
    for label, b in (("this fat binary", universal[:8]), ("a Java 25 class file", java)):
        (n,) = struct.unpack_from(">I", b, 4)
        print(f"   {label:<22} {b.hex(' ')}   u32 at 4 = {n:<4} {'a slice count' if n <= 30 else 'a class version'}")
    print()
    print("   file(1)'s rule is exactly that comparison: greater than 30 is Java.")
    print("   The two formats never agreed to share; the number was Java's first.")
    print()

    section(5, "THE SAME HEADER READ THE WRONG WAY")
    (m_be,) = struct.unpack_from(">I", x86, 0)
    (cpu_be,) = struct.unpack_from(">i", x86, 4)
    print(f"   magic as big-endian     {m_be:#010x}   {MAGICS.get(m_be, 'not Mach-O')}")
    print(f"   cputype as big-endian   {cpu_be:#010x}   {cpu_be:>12}")
    print()
    print("   The magic tells a reader it has the order wrong; the cputype does")
    print("   not, it is simply a different number. Read the magic first.")


if __name__ == "__main__":
    main()
