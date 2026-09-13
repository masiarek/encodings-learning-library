#!/usr/bin/env python3
"""Motorola Hex: S-records, beside the Intel HEX records that carry the
same bytes -- a type letter that is the address width, a count that
includes the checksum, and a one's complement where Intel takes a two's.

Run:  python3 motorola_hex_py.py
"""

TYPES = {0: ("header", 2), 1: ("data, 16-bit address", 2), 2: ("data, 24-bit address", 3), 3: ("data, 32-bit address", 4),
         5: ("count, 16-bit", 2), 6: ("count, 24-bit", 3), 7: ("start, 32-bit", 4), 8: ("start, 24-bit", 3), 9: ("start, 16-bit", 2)}


def srecord(rectype, address, data):
    width = TYPES[rectype][1]
    body = address.to_bytes(width, "big") + data
    count = len(body) + 1                                   # the checksum byte is counted
    body = bytes([count]) + body
    return f"S{rectype}" + (body + bytes([(~sum(body)) & 0xFF])).hex().upper()


def parse(line):
    rectype = int(line[1])
    body = bytes.fromhex(line[2:])
    count, width = body[0], TYPES[rectype][1]
    ok = (sum(body) & 0xFF) == 0xFF
    address = int.from_bytes(body[1:1 + width], "big")
    return rectype, count, address, body[1 + width:-1], body[-1], ok


def ihex(rectype, offset, data):
    body = bytes([len(data)]) + offset.to_bytes(2, "big") + bytes([rectype]) + data
    return ":" + (body + bytes([(-sum(body)) & 0xFF])).hex().upper()


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    cafe = "café".encode()

    section(1, "THE SAME FIVE BYTES, TWO FRAMES")
    s1, i0 = srecord(1, 0x0100, cafe), ihex(0, 0x0100, cafe)
    print(f"   Motorola   {s1}")
    print(f"   Intel      {i0}")
    print()
    rows = [("mark", "S1", ":"), ("count", "08 = address + data + checksum", "05 = data only"),
            ("address", "0100, width from the type letter", "0100, always 16-bit"),
            ("type", "in the letter", "00, a field of its own"), ("checksum", "one's complement", "two's complement")]
    print(f"   {'field':<10} {'Motorola':<34} Intel")
    for field, m, i in rows:
        print(f"   {field:<10} {m:<34} {i}")
    print()
    print("   Every field is a different number for the same payload, and the")
    print("   Intel line is one character longer because its type is a field")
    print("   where Motorola's is the second character of the mark.")
    print()

    section(2, "THE COUNT INCLUDES THE CHECKSUM, AND THE ADDRESS")
    for rectype in (1, 2, 3):
        line = srecord(rectype, 0x0100, cafe)
        _, count, address, data, cksum, ok = parse(line)
        print(f"   {line:<26} S{rectype}: address {TYPES[rectype][1]} bytes   count {count} = {TYPES[rectype][1]} + {len(data)} + 1")
    print()
    print("   Three records for the same bytes at the same address, and the")
    print("   count grows with the address width the type letter chose. Intel's")
    print("   count would be 05 for all three, because it counts only data.")
    print()

    section(3, "ONE'S COMPLEMENT: THE RECORD SUMS TO 0xFF, NOT TO 0")
    for label, line in (("Motorola", s1), ("Intel", i0)):
        body = bytes.fromhex(line[2:] if label == "Motorola" else line[1:])
        print(f"   {label:<10} bytes after the mark  {body.hex(' ')}   sum mod 256 = {sum(body) & 0xFF:#04x}")
    print()
    print("   Intel's checksum is the two's complement of the sum, so the whole")
    print("   record sums to 0x00; Motorola's is the one's complement, so it")
    print("   sums to 0xFF. A reader checks for a different constant, and a")
    print("   record from one format fed to the other's check always fails --")
    print("   which is the useful property, since the marks can be confused.")
    print()

    section(4, "A WHOLE FILE: HEADER, DATA, COUNT, START")
    lines = [srecord(0, 0, b"hello.s19"), srecord(3, 0x08000000, cafe), srecord(3, 0x08000010, b"\x00\x01\x02\x03"),
             srecord(5, 2, b""), srecord(7, 0x08000000, b"")]
    for line in lines:
        rectype, count, address, data, cksum, ok = parse(line)
        text = data.decode("ascii") if rectype == 0 else data.hex(" ")
        print(f"   {line:<30} S{rectype} {TYPES[rectype][0]:<22} {text:<14} {'ok' if ok else 'BAD'}")
    print()
    print("   S0's data field is text by convention -- the module name -- and")
    print("   Ghidra skips the line. S5 carries the number of S1/S2/S3 records")
    print("   as its address; Ghidra treats it as invalid and skips it too. S7,")
    print("   S8 and S9 end the file with a start address in their address")
    print("   field, one letter per width, matching S3, S2 and S1.")
    print()

    section(5, "WHAT A CHECKSUM DOES NOT NOTICE")
    good = srecord(1, 0x0100, b"\x41\x42")
    swapped = srecord(1, 0x0100, b"\x42\x41")
    print(f"   {good}   ok {parse(good)[5]}")
    print(f"   {swapped}   ok {parse(swapped)[5]}   -- the same two bytes, swapped: the same checksum")
    print()
    print("   Addition does not care about order, in either complement. A byte")
    print("   count and a sum catch a changed byte and a missing one; they do")
    print("   not catch two bytes exchanged, in this format or in Intel's.")


if __name__ == "__main__":
    main()
