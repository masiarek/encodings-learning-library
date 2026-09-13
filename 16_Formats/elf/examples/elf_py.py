#!/usr/bin/env python3
"""ELF: the sixteen-byte e_ident says how to read the rest of the header.

Two headers are built from the same seven field values -- one 64-bit
little-endian, one 32-bit big-endian -- and each is read back using nothing
but its own bytes 4 and 5. Then the section-name string table, which is
where a section's name actually lives.

Run:  python3 elf_py.py
"""

import struct

ELFCLASS32, ELFCLASS64 = 1, 2
ELFDATA2LSB, ELFDATA2MSB = 1, 2
ET = {1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}
EM = {3: "386", 0x28: "ARM", 0x3E: "X86_64", 0xB7: "AARCH64", 0xF3: "RISC-V"}

# The seven fields after e_ident that every ELF header has, in order, and the
# struct letter for each in the two classes. Only three change width.
FIELDS = [
    ("e_type", "H", "H"), ("e_machine", "H", "H"), ("e_version", "I", "I"),
    ("e_entry", "I", "Q"), ("e_phoff", "I", "Q"), ("e_shoff", "I", "Q"),
    ("e_flags", "I", "I"), ("e_ehsize", "H", "H"), ("e_phentsize", "H", "H"),
    ("e_phnum", "H", "H"), ("e_shentsize", "H", "H"), ("e_shnum", "H", "H"),
    ("e_shstrndx", "H", "H"),
]


def ident(elf_class, elf_data):
    return bytes([0x7F, ord("E"), ord("L"), ord("F"), elf_class, elf_data, 1, 0, 0]) + bytes(7)


def fmt_for(e_ident):
    """A struct format string built from two bytes of the file."""
    order = "<" if e_ident[5] == ELFDATA2LSB else ">"
    col = 2 if e_ident[4] == ELFCLASS64 else 1
    return order + "".join(f[col] for f in FIELDS)


def build(elf_class, elf_data, values):
    e_ident = ident(elf_class, elf_data)
    fmt = fmt_for(e_ident)
    ehsize = 16 + struct.calcsize(fmt)
    v = dict(values, e_ehsize=ehsize,
             e_phentsize=56 if elf_class == ELFCLASS64 else 32,
             e_shentsize=64 if elf_class == ELFCLASS64 else 40)
    return e_ident + struct.pack(fmt, *(v[f[0]] for f in FIELDS))


def parse(data):
    fmt = fmt_for(data[:16])
    return dict(zip((f[0] for f in FIELDS), struct.unpack_from(fmt, data, 16)))


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    values = dict(e_type=2, e_machine=0x3E, e_version=1, e_entry=0x401000,
                  e_phoff=0, e_shoff=0, e_flags=0, e_phnum=0, e_shnum=0, e_shstrndx=0)

    section(1, "THE FIRST SIXTEEN BYTES SAY HOW TO READ THE REST")
    for label, c, d in (("64-bit, little-endian", ELFCLASS64, ELFDATA2LSB),
                        ("32-bit, big-endian", ELFCLASS32, ELFDATA2MSB)):
        e = ident(c, d)
        print(f"   {label:<22} {e.hex(' ')}")
    print()
    print("   byte 0..3   7f 45 4c 46   a byte no text file starts with, then 'ELF'")
    print("   byte 4      EI_CLASS      1 = 32-bit offsets, 2 = 64-bit offsets")
    print("   byte 5      EI_DATA       1 = little-endian, 2 = big-endian")
    print("   byte 6      EI_VERSION    1, the only value there has ever been")
    print("   byte 7      EI_OSABI      0 = System V; 9..15 the pad")
    print()

    section(2, "THE SAME SEVEN FIELDS, 52 OR 64 BYTES")
    little64 = build(ELFCLASS64, ELFDATA2LSB, values)
    big32 = build(ELFCLASS32, ELFDATA2MSB, values)
    for label, data in (("64-bit LSB", little64), ("32-bit MSB", big32)):
        print(f"   {label}   {len(data)} bytes   format string {fmt_for(data)!r}")
        for i in range(16, len(data), 16):
            print(f"      {i:04x}  {data[i:i + 16].hex(' ')}")
    print()
    print("   e_entry, e_phoff and e_shoff are the three fields that grew from")
    print("   4 bytes to 8; everything else is the same width in both. 52 + 12")
    print("   is 64, and e_ehsize in each header says which it is.")
    print()

    section(3, "READ EACH ONE WITH ITS OWN IDENT")
    a, b = parse(little64), parse(big32)
    print(f"   {'field':<12} {'64-bit LSB':>12} {'32-bit MSB':>12}")
    for name, _, _ in FIELDS:
        av, bv = a[name], b[name]
        show = (lambda x: f"{x:#x}") if name in ("e_entry", "e_machine") else str
        print(f"   {name:<12} {show(av):>12} {show(bv):>12}")
    print()
    print(f"   e_type {a['e_type']} is {ET[a['e_type']]}, e_machine {a['e_machine']:#x} is {EM[a['e_machine']]},")
    print("   in both -- two layouts, one header, because the file said which")
    print("   layout it used before its first multi-byte field.")
    print()

    section(4, "READ THE BIG-ENDIAN ONE AS IF IT WERE LITTLE")
    wrong = dict(zip((f[0] for f in FIELDS), struct.unpack_from("<" + "".join(f[1] for f in FIELDS), big32, 16)))
    print(f"   e_type      {wrong['e_type']:<8} ({wrong['e_type']:#06x}, not in the table: 1..4)")
    print(f"   e_machine   {wrong['e_machine']:<8} ({wrong['e_machine']:#06x}, not x86-64)")
    print(f"   e_entry     {wrong['e_entry']:#010x}")
    print()
    print("   Nothing raised. Every wrong reading of a header is a number, which")
    print("   is why byte 5 exists: the alternative is guessing from plausibility.")
    print()

    section(5, "A SECTION'S NAME IS AN OFFSET INTO A STRING TABLE")
    shstrtab = b"\x00.text\x00.shstrtab\x00"
    names = {1: ".text", 7: ".shstrtab"}
    print(f"   .shstrtab bytes   {shstrtab.hex(' ')}")
    print(f"   as text           {shstrtab!r}")
    print()
    for sh_name in (1, 7):
        end = shstrtab.index(b"\x00", sh_name)
        got = shstrtab[sh_name:end].decode("ascii")
        print(f"   sh_name = {sh_name:<3} -> read to the next NUL -> {got!r:<12} {'ok' if got == names[sh_name] else 'WRONG'}")
    print()
    print("   A section header holds no name, only sh_name, an offset into the")
    print("   section that e_shstrndx points at. Names are NUL-terminated there,")
    print("   and offset 0 is an empty string on purpose: the unnamed section.")


if __name__ == "__main__":
    main()
