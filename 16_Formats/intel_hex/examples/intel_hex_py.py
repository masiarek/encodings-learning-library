#!/usr/bin/env python3
"""Intel Hex: a 16-bit offset field, and the two extended-address records
that let it reach a 4 GB image -- so one data record lands at three
different addresses depending on what preceded it.

Framing a format (08_Build_Your_Own) took the record apart; this page
assembles records into a memory image, which is the loader's job.

Run:  python3 intel_hex_py.py
"""

import re

TYPES = {0: "Data", 1: "End of File", 2: "Extended Segment Address", 3: "Start Segment Address",
         4: "Extended Linear Address", 5: "Start Linear Address"}
GHIDRA_FIRST_LINE = re.compile(r"^[S:][0-9a-fA-F]+$")   # MotorolaHexLoader.isPossibleHexFile, shared by both loaders


def record(rectype, offset, data):
    body = bytes([len(data)]) + offset.to_bytes(2, "big") + bytes([rectype]) + data
    return ":" + (body + bytes([(-sum(body)) & 0xFF])).hex().upper()


def parse(line):
    body = bytes.fromhex(line[1:])
    assert sum(body) & 0xFF == 0, "checksum"
    n, offset, rectype = body[0], int.from_bytes(body[1:3], "big"), body[3]
    return rectype, offset, body[4:4 + n]


def load(lines):
    """A loader: walk the records, keep the current upper address, place the data."""
    memory, base, start = {}, 0, None
    for line in lines:
        rectype, offset, data = parse(line)
        if rectype == 0:
            for i, b in enumerate(data):
                memory[base + offset + i] = b
        elif rectype == 2:
            base = int.from_bytes(data, "big") << 4
        elif rectype == 4:
            base = int.from_bytes(data, "big") << 16
        elif rectype == 3:
            cs, ip = int.from_bytes(data[:2], "big"), int.from_bytes(data[2:], "big")
            start = ("CS:IP", cs, ip, cs * 16 + ip)
        elif rectype == 5:
            start = ("EIP", int.from_bytes(data, "big"))
        elif rectype == 1:
            break
    return memory, start


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    cafe = "café".encode()

    section(1, "THE OFFSET FIELD IS 16 BITS")
    line = record(0, 0xFFFC, cafe)
    rectype, offset, data = parse(line)
    print(f"   {line}")
    print(f"   type {rectype} {TYPES[rectype]}   offset {offset:#06x}   {len(data)} bytes {data.hex(' ')}")
    print()
    print("   Four hex digits of offset reach 65,535 and no further. A firmware")
    print("   image for anything with more than 64 KB of address space needs")
    print("   another record to say which 64 KB, and Intel gave it two.")
    print()

    section(2, "THE SAME DATA RECORD, THREE ADDRESSES")
    data_line = record(0, 0x0100, cafe)
    variants = [
        ("nothing before it", []),
        ("02: Extended Segment Address 0x1000  (x 16)", [record(2, 0, (0x1000).to_bytes(2, "big"))]),
        ("04: Extended Linear Address 0x0001   (<< 16)", [record(4, 0, (0x0001).to_bytes(2, "big"))]),
        ("04: Extended Linear Address 0x0800   (<< 16)", [record(4, 0, (0x0800).to_bytes(2, "big"))]),
    ]
    for label, prefix in variants:
        memory, _ = load(prefix + [data_line, record(1, 0, b"")])
        first = min(memory)
        print(f"   {label:<46} {data_line}   lands at {first:#010x}")
    print()
    print("   The data record is identical in all four files: 63 61 66 c3 a9 at")
    print("   offset 0x0100. What changed is the record before it, which the")
    print("   loader keeps as state. Type 02 shifts by 4 bits, the 8086's")
    print("   segment arithmetic; type 04 shifts by 16, and reaches 4 GB.")
    print()

    section(3, "A LOADER IS A LITTLE STATE MACHINE")
    image = [
        record(4, 0, (0x0800).to_bytes(2, "big")),
        record(0, 0x0000, cafe),
        record(0, 0x0010, b"\x00\x01\x02\x03"),
        record(4, 0, (0x0801).to_bytes(2, "big")),
        record(0, 0x0000, b"\xff\xfe"),
        record(5, 0, (0x08000010).to_bytes(4, "big")),
        record(1, 0, b""),
    ]
    for line in image:
        rectype, offset, data = parse(line)
        print(f"   {line:<28} {rectype}  {TYPES[rectype]:<24} {data.hex(' ')}")
    memory, start = load(image)
    print()
    ranges, run = [], None
    for addr in sorted(memory):
        if run and addr == run[1] + 1:
            run[1] = addr
        else:
            run = [addr, addr]
            ranges.append(run)
    for lo, hi in ranges:
        print(f"   {lo:#010x}..{hi:#010x}   {bytes(memory[a] for a in range(lo, hi + 1)).hex(' ')}")
    print(f"   start address   {start[0]} {start[1]:#010x}")
    print()
    print("   Three runs of bytes at three addresses, out of seven lines of")
    print("   text, and the file itself has no notion of a total size or an")
    print("   order: a loader could read the records in any sequence as long")
    print("   as each data record follows the extended-address record it needs.")
    print()

    section(4, "HOW GHIDRA DECIDES A FILE IS HEX")
    for first_line, note in ((image[0], "an Intel Hex record"), ("S00600004844521B", "a Motorola S-record"),
                             (":00000001FF  ", "trailing spaces"), (":0000000 1FF", "a space inside"), ("", "an empty file")):
        ok = bool(GHIDRA_FIRST_LINE.match(first_line))
        print(f"   {first_line!r:<22} {'possible hex file' if ok else 'not a hex file':<18} {note}")
    print()
    print("   One regular expression over the first non-blank line, shared by the")
    print("   Intel and Motorola loaders: a colon or an S, then hex digits to the")
    print("   end. Neither loader can tell the two formats apart at that point;")
    print("   the record mark is the only difference, and both offer every")
    print("   processor Ghidra has, because a hex file names none.")


if __name__ == "__main__":
    main()
