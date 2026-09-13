#!/usr/bin/env python3
"""MZ: a header measured in pages and paragraphs, the size DOS computes from
it, and the two bytes that are two numbers.

The header values are the ones pip's t64.exe launcher carries in its DOS
stub, so the arithmetic here is the arithmetic DOS does on that file.

Run:  python3 mz_py.py
"""

import struct

FIELDS = ["e_magic", "e_cblp", "e_cp", "e_crlc", "e_cparhdr", "e_minalloc", "e_maxalloc",
          "e_ss", "e_sp", "e_csum", "e_ip", "e_cs", "e_lfarlc", "e_ovno"]
MEANING = {
    "e_magic": "'MZ'", "e_cblp": "bytes used in the LAST 512-byte page", "e_cp": "pages of 512 bytes in the file",
    "e_crlc": "relocation entries", "e_cparhdr": "header size, in 16-byte paragraphs",
    "e_minalloc": "extra paragraphs needed", "e_maxalloc": "extra paragraphs wanted",
    "e_ss": "initial SS, relative", "e_sp": "initial SP", "e_csum": "checksum, usually 0",
    "e_ip": "initial IP", "e_cs": "initial CS, relative", "e_lfarlc": "offset of the relocation table",
    "e_ovno": "overlay number",
}


def header(**kw):
    v = dict(e_magic=0x5A4D, e_cblp=0, e_cp=0, e_crlc=0, e_cparhdr=4, e_minalloc=0, e_maxalloc=0xFFFF,
             e_ss=0, e_sp=0xB8, e_csum=0, e_ip=0, e_cs=0, e_lfarlc=0x40, e_ovno=0)
    v.update(kw)
    return struct.pack("<14H", *(v[f] for f in FIELDS))


def sizes(h):
    v = dict(zip(FIELDS, struct.unpack("<14H", h[:28])))
    total = v["e_cp"] * 512 if v["e_cblp"] == 0 else (v["e_cp"] - 1) * 512 + v["e_cblp"]
    return v, total, v["e_cparhdr"] * 16


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "THE HEADER, IN UNITS THAT ARE NOT BYTES")
    h = header(e_cblp=144, e_cp=3)
    v, total, hdr = sizes(h)
    print(f"   {h.hex(' ')}")
    print()
    for f in FIELDS:
        print(f"   {f:<12} {v[f]:#06x}  {v[f]:>6}   {MEANING[f]}")
    print()
    print(f"   file size DOS computes   (e_cp - 1) * 512 + e_cblp = ({v['e_cp']} - 1) * 512 + {v['e_cblp']} = {total}")
    print(f"   header size              e_cparhdr * 16 = {v['e_cparhdr']} * 16 = {hdr}")
    print(f"   load module              bytes {hdr} .. {total}, {total - hdr} of them")
    print()
    print("   These are the numbers from the DOS stub of pip's t64.exe, a 108,032-")
    print("   byte PE32+ launcher. DOS reads 1,168 of those bytes and stops, and")
    print("   the stub inside that region is what prints the one sentence DOS")
    print("   users of it ever see. No field here can count higher than 65,535")
    print("   pages, which is 32 MB, and a 16-bit page count was plenty in 1981.")
    print()

    section(2, "e_cblp = 0 MEANS THE LAST PAGE IS FULL")
    for cblp, cp in ((144, 3), (0, 3), (1, 3), (512, 3)):
        _, total, _ = sizes(header(e_cblp=cblp, e_cp=cp))
        note = {0: "0 bytes used of the last page means all 512", 512: "512 is never written: it would be 0 with one more page"}.get(cblp, "")
        print(f"   e_cblp {cblp:>3}  e_cp {cp}   ->  {total:>5} bytes   {note}".rstrip())
    print()

    section(3, "THE RELOCATION TABLE IS PAIRS OF 16-BIT NUMBERS")
    relocs = [(0x0003, 0x0000), (0x0010, 0x0001)]
    table = b"".join(struct.pack("<HH", off, seg) for off, seg in relocs)
    h = header(e_cblp=144, e_cp=3, e_crlc=len(relocs))
    print(f"   e_lfarlc {0x40:#x}  e_crlc {len(relocs)}   table bytes {table.hex(' ')}")
    for i, (off, seg) in enumerate(relocs):
        print(f"   entry {i}   offset {off:#06x}  segment {seg:#06x}   linear {seg * 16 + off:#07x}: a word the loader adds the load segment to")
    print()
    print("   segment:offset, 16 bits each, and the linear address is 16 * seg +")
    print("   off, so one address has 4096 spellings. The table says where the")
    print("   segment halves of far pointers sit, so DOS can patch them for")
    print("   wherever the program was actually loaded.")
    print()

    section(4, "TWO BYTES, TWO NUMBERS")
    for b in (b"MZ", b"ZM"):
        (le,) = struct.unpack("<H", b)
        (be,) = struct.unpack(">H", b)
        print(f"   {b.hex(' ')}  {b!r}   little-endian {le:#06x}   big-endian {be:#06x}   Ghidra: {'MZ' if le == 0x5A4D else 'not MZ'}")
    print()
    print("   The constant Ghidra compares, IMAGE_DOS_SIGNATURE, is 0x5a4d: the")
    print("   letters M and Z read as a little-endian 16-bit number. The same")
    print("   two bytes are 0x4d5a to a big-endian reader, and a file that")
    print("   spells them ZM is 0x4d5a to this one. One picture, two numbers,")
    print("   and a signature test picks one of them.")
    print()

    section(5, "WHAT MAKES IT 'OLD-STYLE'")
    h = header(e_cblp=144, e_cp=3).ljust(0x40, b"\x00")
    (lfanew,) = struct.unpack_from("<I", h, 0x3C)
    print(f"   e_lfanew at 0x3c   {h[0x3C:0x40].hex(' ')}   = {lfanew}")
    print()
    print("   0x3c is inside the reserved words of the 1981 header. NE and PE")
    print("   put a 32-bit offset there, pointing past the DOS stub at their own")
    print("   header. Ghidra's MZ loader takes a file only when the signature")
    print("   is MZ AND no NE header AND no PE header is found through e_lfanew:")
    print("   it is the loader for what the other two decline.")


if __name__ == "__main__":
    main()
