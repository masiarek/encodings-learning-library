#!/usr/bin/env python3
"""OMF: a stream of records, each a type byte, a 16-bit length and a
checksum that makes the record sum to zero -- unless it is zero, which
means 'not computed' and is accepted -- with every name a length-prefixed
string and the low bit of the type saying whether fields are 16 or 32
bits wide.

Run:  python3 omf_py.py
"""

import struct

TYPES = {0x80: "THEADR", 0x82: "LHEADR", 0x88: "COMENT", 0x8A: "MODEND", 0x8C: "EXTDEF", 0x90: "PUBDEF",
         0x96: "LNAMES", 0x98: "SEGDEF", 0x9A: "GRPDEF", 0x9C: "FIXUPP", 0xA0: "LEDATA", 0xA2: "LIDATA"}


def omf_string(s):
    b = s.encode("ascii")
    return bytes([len(b)]) + b


def record(rectype, body, checksum=True):
    length = len(body) + 1                                   # the checksum byte is counted in the length
    head = bytes([rectype]) + struct.pack("<H", length) + body
    cs = (-sum(head)) & 0xFF if checksum else 0
    return head + bytes([cs])


def parse(data):
    pos, out = 0, []
    while pos < len(data):
        rectype = data[pos]
        (length,) = struct.unpack_from("<H", data, pos + 1)
        rec = data[pos:pos + 3 + length]
        body, cs = rec[3:-1], rec[-1]
        valid = cs == 0 or (sum(rec) & 0xFF) == 0
        out.append((rectype, length, body, cs, valid))
        pos += 3 + length
    return out


def read_strings(body):
    names, pos = [], 0
    while pos < len(body):
        n = body[pos]
        names.append(body[pos + 1:pos + 1 + n].decode("ascii"))
        pos += 1 + n
    return names


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    theadr = record(0x80, omf_string("cafe.c"))
    lnames = record(0x96, omf_string("") + omf_string("_TEXT") + omf_string("CODE"))
    segdef16 = record(0x98, bytes([0x48]) + struct.pack("<H", 0x0100) + bytes([2, 3, 1]))          # attributes, 16-bit length, name/class/overlay indexes
    segdef32 = record(0x99, bytes([0x48]) + struct.pack("<I", 0x00010000) + bytes([2, 3, 1]))      # the same with the low bit set: a 32-bit length
    ledata = record(0xA0, bytes([1]) + struct.pack("<H", 0) + "café".encode())
    modend = record(0x8A, bytes([0]))
    module = theadr + lnames + segdef16 + ledata + modend

    section(1, "A RECORD IS A TYPE, A LENGTH, A BODY AND A CHECKSUM")
    print(f"   {theadr.hex(' ')}")
    print()
    print(f"   type     {theadr[0]:#04x}  THEADR")
    print(f"   length   {theadr[1:3].hex(' ')}       = {struct.unpack_from('<H', theadr, 1)[0]}, little-endian, counting the checksum")
    print(f"   body     {theadr[3:-1].hex(' ')}   a length byte, then the name")
    print(f"   checksum {theadr[-1]:#04x}  sum of every byte of the record mod 256 = {sum(theadr) & 0xFF}")
    print()
    print("   The same three fields Framing a format asks for -- type, length,")
    print("   check -- with Intel's checksum rule from Intel HEX: the whole record,")
    print("   type and length included, sums to zero. This is Intel's 1981 8086")
    print("   object format, and the 8086's byte order: little-endian throughout.")
    print()

    section(2, "THE MODULE, RECORD BY RECORD")
    for rectype, length, body, cs, valid in parse(module):
        name = TYPES.get(rectype & 0xFE, "?")
        text = read_strings(body) if rectype in (0x80, 0x96) else body.hex(" ")
        print(f"   {rectype:#04x} {name:<7} length {length:>3}   checksum {cs:#04x} {'ok ' if valid else 'BAD'}   {text}")
    print()
    print("   THEADR names the module, LNAMES lists every name any later record")
    print("   will refer to by index, SEGDEF defines a segment by those indexes,")
    print("   LEDATA carries bytes for it, MODEND ends the module. No offsets:")
    print("   every record is found by walking from the one before.")
    print()

    section(3, "EVERY STRING HAS A LENGTH BYTE")
    body = lnames[3:-1]
    print(f"   LNAMES body   {body.hex(' ')}")
    pos, i = 0, 1
    while pos < len(body):
        n = body[pos]
        print(f"   name {i}   length {n}   {body[pos + 1:pos + 1 + n]!r}")
        pos += 1 + n
        i += 1
    print()
    print("   No terminator anywhere: the first name is the empty string, one")
    print("   byte long, which is what index 1 in a SEGDEF means by 'no name'.")
    print("   A name can be 255 bytes at most and may hold any byte, including")
    print("   a NUL, which a C string could not. Ghidra's OmfUtils.readString")
    print("   is exactly 'read a byte, read that many'.")
    print()

    section(4, "THE LOW BIT OF THE TYPE IS THE WIDTH OF THE FIELDS")
    for rec in (segdef16, segdef32):
        rectype, length, body, cs, valid = parse(rec)[0]
        wide = rectype & 1
        fmt = "<I" if wide else "<H"
        (seglen,) = struct.unpack_from(fmt, body, 1)
        print(f"   {rec.hex(' '):<40} type {rectype:#04x} = SEGDEF{'32' if wide else '  '}   segment length {seglen:#x} in {4 if wide else 2} bytes")
    print()
    print("   0x98 and 0x99 are one record type; the low bit says whether its")
    print("   numeric fields are 16 or 32 bits, and Ghidra masks it off before")
    print("   looking the type up. The 8086 format grew 32-bit fields for the")
    print("   386 by spending one bit that was always zero.")
    print()

    section(5, "A CHECKSUM OF ZERO MEANS 'NOT COMPUTED', AND IS ACCEPTED")
    lazy = record(0x80, omf_string("cafe.c"), checksum=False)
    damaged = bytearray(theadr)
    damaged[5] ^= 0x20
    for label, rec in (("as written", theadr), ("checksum byte set to 0", lazy), ("one byte of the name changed", bytes(damaged))):
        _, _, _, cs, valid = parse(rec)[0]
        print(f"   {label:<30} checksum {cs:#04x}   sum {sum(rec) & 0xFF:#04x}   {'valid' if valid else 'INVALID'}")
    print()
    print("   'Some compilers just set this to zero', says the comment in Ghidra's")
    print("   OmfRecord.validCheckSum, and so a zero passes. A check that can be")
    print("   switched off by the writer is a check the reader cannot rely on --")
    print("   and a record damaged in a way that happens to leave the byte at")
    print("   zero is, to this reader, a record nobody checked.")
    print()

    section(6, "HOW GHIDRA RECOGNISES A MODULE")
    for label, head in (("a THEADR", theadr), ("an LHEADR", record(0x82, omf_string("lib"))), ("a THEADR with the wrong length", theadr[:1] + b"\x09\x00" + theadr[3:]),
                        ("an LNAMES first", lnames)):
        t = head[0] & 0xFE
        (length,) = struct.unpack_from("<H", head, 1)
        ok = t in (0x80, 0x82) and length == head[3] + 2
        print(f"   {label:<32} type {head[0]:#04x}  length {length:>2}  name length {head[3]}   {'OMF' if ok else 'not OMF'}")
    print()
    print("   OmfFileHeader.checkMagicNumber: the first record must be THEADR")
    print("   or LHEADR, and its length must be the name's length plus two --")
    print("   the name byte and the checksum. There is no magic; the first")
    print("   record's arithmetic is the signature.")


if __name__ == "__main__":
    main()
