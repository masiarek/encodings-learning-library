#!/usr/bin/env python3
"""MAP: an MSVC linker map is text in columns, and the loader keeps two
of the four -- the name, and the Rva+Base column parsed as hexadecimal
with no prefix -- and ignores the segment:offset column entirely.

Run:  python3 program_mapfile_py.py
"""

import re

MAP = """ hello

 Timestamp is 5f3c2a1e (Tue Aug 18 12:00:30 2020)

 Preferred load address is 0000000140000000

 Start         Length     Name                   Class
 0001:00000000 00001000H .text                   CODE
 0002:00000000 00000200H .rdata                  DATA

  Address         Publics by Value              Rva+Base               Lib:Object

 0000:00000000       __ImageBase                0000000140000000     <linker-defined>
 0001:00000040       main                       0000000140001040 f   hello.obj
 0001:000000c0       café_string                00000001400010c0     hello.obj
 0002:00000010       ?greeting@@3PEBDEB         0000000140002010     hello.obj

 entry point at        0001:00000040

 Static symbols

 0001:00000200       helper                     0000000140001200 f   hello.obj
"""


def ghidra_parse(text):
    """MapLoader.parseMapFile and parseMapSymbol, as 12.1.3 has them."""
    symbols, lines = [], text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line.startswith(";"):
            continue
        if "Publics by Value" in line or line.startswith("Static symbols"):
            added = False
            while i < len(lines):
                line = lines[i].strip()
                i += 1
                if line.startswith(";"):
                    continue
                if line:
                    parts = re.split(r"\s+", line, maxsplit=3)
                    if len(parts) < 3:
                        continue
                    try:
                        symbols.append((parts[1], int(parts[2], 16)))
                        added = True
                    except ValueError:
                        pass
                elif added:
                    break
    return symbols


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "THE LOADER KEEPS THE SECOND AND THIRD COLUMNS")
    for name, addr in ghidra_parse(MAP):
        print(f"   {name:<22} {addr:#018x}")
    print()
    print("   Each symbol line is split on whitespace into at most four parts:")
    print("   parts[0] is the segment:offset, ignored; parts[1] the name;")
    print("   parts[2] the Rva+Base column, parsed as hexadecimal; parts[3] the")
    print("   rest, ignored. A line with fewer than three parts is skipped, and")
    print("   the section ends at the first blank line after a symbol was added.")
    print()

    section(2, "THE ADDRESS COLUMN IS HEX WITH NO PREFIX")
    col = "0000000140001040"
    print(f"   {col!r}")
    print(f"   int(col, 16)   {int(col, 16):#x}   what the loader does: Long.parseLong(s, 16)")
    print(f"   int(col)       {int(col):,}   what a reader who did not know the base would get")
    print()
    for spelled in ("140001040", "0x140001040", "140001040h"):
        try:
            v = int(spelled, 16)
            note = "Python accepts a 0x prefix in base 16; Java's parseLong does not" if spelled.startswith("0x") else ""
            print(f"   int({spelled!r}, 16)   {v:#x}   {note}")
        except ValueError:
            print(f"   int({spelled!r}, 16)   ValueError   -- and NumberFormatException in Java: the line is logged and skipped")
    print()
    print("   Sixteen digits and no 0x: the base is in the linker's documentation")
    print("   and nowhere in the file. And the one prefix a reader might add is")
    print("   a parser differential between the two languages on this page.")
    print()

    section(3, "THE COLUMN THE LOADER IGNORES SAYS THE SAME THING")
    base = int(re.search(r"Preferred load address is ([0-9A-Fa-f]+)", MAP).group(1), 16)
    starts = {}
    for m in re.finditer(r"^ (\d{4}):([0-9A-Fa-f]{8}) ([0-9A-Fa-f]{8})H (\S+)", MAP, re.M):
        starts[int(m.group(1), 16)] = (m.group(4), int(m.group(2), 16))
    print(f"   preferred load address {base:#x}   sections {starts}")
    print()
    for m in re.finditer(r"^ (\d{4}):([0-9A-Fa-f]{8})\s+(\S+)\s+([0-9A-Fa-f]{16})", MAP, re.M):
        seg, off, name, rva_base = int(m.group(1), 16), int(m.group(2), 16), m.group(3), int(m.group(4), 16)
        if seg == 0:
            continue
        computed = base + 0x1000 * seg + off        # sections are page-aligned here, so segment n begins at n * 0x1000
        print(f"   {seg:04x}:{off:08x}  {name:<22} computed {computed:#x}   column {rva_base:#x}   {'agree' if computed == rva_base else 'DIFFER'}")
    print()
    print("   segment:offset plus the section's start plus the load address is")
    print("   the Rva+Base column, so the column is redundant and the loader")
    print("   reads the one that needs no arithmetic. It does mean that a map")
    print("   file with the wrong preferred load address is wrong in the column")
    print("   Ghidra trusts and right in the one it ignores.")
    print()

    section(4, "WHERE THE SECTION ENDS")
    split = MAP.replace("       caf", "\n       caf", 1)    # a blank line inside the Publics section
    print(f"   as written             {len(ghidra_parse(MAP))} symbols")
    print(f"   blank line after main  {len(ghidra_parse(split))} symbols   -- the loop stops at the first blank line once it has added one")
    print()
    print("   'Static symbols' opens a second section that is parsed the same")
    print("   way, so symbols after it are found; a stray blank line inside")
    print("   the first section loses everything after it, silently.")


if __name__ == "__main__":
    main()
