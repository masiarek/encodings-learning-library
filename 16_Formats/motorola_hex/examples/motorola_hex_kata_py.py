#!/usr/bin/env python3
"""Kata: four S-records, and which of the three checks each one fails."""

WIDTH = {"0": 2, "1": 2, "2": 3, "3": 4, "5": 2, "7": 4, "8": 3, "9": 2}


def srecord(rectype, address, data):
    body = address.to_bytes(WIDTH[str(rectype)], "big") + data
    body = bytes([len(body) + 1]) + body
    return f"S{rectype}" + (body + bytes([(~sum(body)) & 0xFF])).hex().upper()


def check(line):
    rectype = line[1]
    body = bytes.fromhex(line[2:])
    count, width = body[0], WIDTH[rectype]
    problems = []
    if count != len(body) - 1:
        problems.append(f"count says {count}, the record has {len(body) - 1} bytes after it")
    if (sum(body) & 0xFF) != 0xFF:
        problems.append(f"sums to {sum(body) & 0xFF:#04x}, not 0xff")
    address = int.from_bytes(body[1:1 + width], "big")
    return rectype, address, body[1 + width:-1], problems


def main():
    good = srecord(1, 0x0100, "café".encode())
    retyped = "S2" + good[2:]
    damaged = good[:12] + "67" + good[14:]
    end = srecord(9, 0, b"")
    for line in (good, retyped, damaged, end):
        rectype, address, data, problems = check(line)
        print(f"   {line:<24} S{rectype}  address {address:#08x}  data {data.hex(' ')}")
        print(f"   {'':<24} {'ok' if not problems else '; '.join(problems)}")
        print()
    print("   Line 1 is café at 0x0100 and correct. Line 2 is the same characters")
    print("   with the type letter changed to 2: nothing else moved, but a 24-bit")
    print("   address takes one more byte, so the first data byte 63 has become")
    print("   the third address byte, the address reads 0x010063, and the count")
    print("   still says 8 -- which is right, so only the sum can object, and")
    print("   it cannot either: the bytes are the same bytes. A wrong type letter")
    print("   is invisible to both checks. Line 3 has one data byte changed, 66")
    print("   to 67, and the sum moves by one: caught. Line 4 is a correct S9")
    print("   with a start address of zero.")


if __name__ == "__main__":
    main()
