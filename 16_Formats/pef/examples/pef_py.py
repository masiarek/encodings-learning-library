#!/usr/bin/env python3
"""PEF: a container that opens with twelve ASCII bytes, dates itself in
seconds since 1904, and stores initialised data as a tiny bytecode --
a 3-bit opcode and a 5-bit count per byte -- that the loader runs.

Run:  python3 pef_py.py
"""

import datetime
import struct

MAC_EPOCH = datetime.datetime(1904, 1, 1, tzinfo=datetime.timezone.utc)
UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
KIND = {0: "code", 1: "unpacked data", 2: "pattern-initialized data", 3: "constant", 4: "loader", 5: "debug",
        6: "executable data", 7: "exception", 8: "traceback"}
OPCODE = {0: "Zero", 1: "BlockCopy", 2: "RepeatedBlock", 3: "InterleaveRepeatBlockWithBlockCopy", 4: "InterleaveRepeatBlockWithZero"}


def container_header(arch, stamp, sections):
    return b"Joy!" + b"peff" + arch.encode("ascii") + struct.pack(">IIIIIHHI", 1, stamp, 0, 0, 0, sections, sections, 0)


def section_header(name_off, addr, total, unpacked, packed, offset, kind, share=1, align=2):
    return struct.pack(">iIIIIIBBBB", name_off, addr, total, unpacked, packed, offset, kind, share, align, 0)


def count_arg(n):
    """A count: 5 bits in the opcode byte when 1..31, else 0 there and a varint after."""
    if 1 <= n <= 31:
        return n, b""
    out, groups = bytearray(), []
    while True:
        groups.append(n & 0x7F)
        n >>= 7
        if not n:
            break
    for g in groups[:0:-1]:
        out.append(g | 0x80)
    out.append(groups[0])
    return 0, bytes(out)


def op(opcode, n, *payload):
    c, extra = count_arg(n)
    return bytes([opcode << 5 | c]) + extra + b"".join(payload)


def unpack_pattern(data):
    """The five opcodes of the pattern-initialized data format, as the loader runs them."""
    out, pos = bytearray(), 0

    def varint():
        nonlocal pos
        n = 0
        while True:
            b = data[pos]
            pos += 1
            n = n << 7 | b & 0x7F
            if not b & 0x80:
                return n

    def count():
        nonlocal pos
        c = data[pos - 1] & 0x1F
        return c if c else varint()

    while pos < len(data):
        opcode = data[pos] >> 5
        pos += 1
        n = count()
        if opcode == 0:
            out += bytes(n)
        elif opcode == 1:
            out += data[pos:pos + n]
            pos += n
        elif opcode == 2:
            reps = varint()
            out += data[pos:pos + n] * (reps + 1)
            pos += n
        else:
            raise ValueError(f"opcode {opcode} not handled here")
    return bytes(out)


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    stamp = 0xC2A43140                     # a classic Mac timestamp: seconds since 1904-01-01
    pattern = op(0, 4) + op(1, 5, ("caf" + chr(0xE9)).encode()) + op(2, 2, bytes([2]), b"\xab\xcd") + op(0, 49)
    sections = [section_header(-1, 0x10000000, 0x200, 0x200, 0x200, 0x64, 0), section_header(-1, 0x20000000, 64, 64, len(pattern), 0x264, 2)]
    header = container_header("pwpc", stamp, len(sections))

    section(1, "TWELVE ASCII BYTES, THEN A BIG-ENDIAN HEADER")
    print(f"   {header[:16].hex(' ')}   {header[:12]!r}")
    tag1, tag2, arch = header[:4], header[4:8], header[8:12]
    version, ts, olddef, oldimp, cur, nsec, ninst, _ = struct.unpack_from(">IIIIIHHI", header, 12)
    print(f"   tag1 {tag1!r}  tag2 {tag2!r}  architecture {arch!r}   formatVersion {version}   sections {nsec}, {ninst} instantiated")
    print()
    print("   Joy! and peff are the two tags Ghidra's ContainerHeader compares,")
    print("   and pwpc or m68k the architecture that picks the language. Every")
    print("   number after them is big-endian, as everything on a 68000 or a")
    print("   PowerPC Mac was, and nothing in the file says so.")
    print()

    section(2, "THE TIMESTAMP COUNTS FROM 1904")
    as_mac = MAC_EPOCH + datetime.timedelta(seconds=ts)
    as_unix = UNIX_EPOCH + datetime.timedelta(seconds=ts)
    print(f"   dateTimeStamp   {ts:#010x} = {ts:,} seconds")
    print(f"   from 1904-01-01 {as_mac:%Y-%m-%d %H:%M:%S}   the Mac OS epoch, which is what the field means")
    print(f"   from 1970-01-01 {as_unix:%Y-%m-%d %H:%M:%S}   the Unix epoch, which is what a C program assumes")
    print(f"   the two epochs differ by {int((UNIX_EPOCH - MAC_EPOCH).total_seconds()):,} seconds")
    print()
    print("   An unsigned 32-bit count from 1904 runs out in 2040; a signed one")
    print("   from 1970 runs out in 2038; Windows counts 100-ns ticks from 1601.")
    print("   The number is the same kind of thing as a byte order: a choice the")
    print("   file does not record and a reader has to already know.")
    print()

    section(3, "A SECTION HEADER IS 28 BYTES, AND ONE KIND IS A PROGRAM")
    for i, sh in enumerate(sections):
        name_off, addr, total, unpacked, packed, off, kind, share, align, _ = struct.unpack(">iIIIIIBBBB", sh)
        print(f"   section {i}   kind {kind} {KIND[kind]:<26} address {addr:#010x}   total {total:>4}  unpacked {unpacked:>4}  packed {packed:>3}  at {off:#x}   nameOffset {name_off}")
    print()
    print("   nameOffset -1 means no name. Kind 2 is the one this page is about:")
    print("   totalSize bytes in memory, unpackedSize of them initialised, and")
    print("   only packedSize bytes in the file, because the initial contents")
    print("   are stored as instructions for producing them.")
    print()

    section(4, "PATTERN-INITIALIZED DATA: A 3-BIT OPCODE AND A 5-BIT COUNT")
    print(f"   the packed bytes   {pattern.hex(' ')}")
    print()
    pos = 0
    while pos < len(pattern):
        b = pattern[pos]
        opcode, count, width = b >> 5, b & 0x1F, 1
        if count == 0:                                     # the count is a varint after the opcode byte
            while pattern[pos + width] & 0x80:
                width += 1
            width += 1
            count = 0
            for x in pattern[pos + 1:pos + width]:
                count = count << 7 | x & 0x1F | (x & 0x60)
        extra = 1 if opcode == 2 else 0                    # RepeatedBlock: a one-byte repeat count here
        payload = 0 if opcode == 0 else count
        chunk = pattern[pos:pos + width + extra + payload]
        note = "(count in a varint after the opcode byte)" if b & 0x1F == 0 else ("(then the repeat count, then the block)" if opcode == 2 else "")
        print(f"   {chunk.hex(' '):<24} opcode {opcode} {OPCODE[opcode]:<14} count {count:>3}   {note}".rstrip())
        pos += width + extra + payload
    out = unpack_pattern(pattern)
    print()
    print(f"   unpacked, {len(out)} bytes")
    for i in range(0, len(out), 16):
        print(f"      {i:02x}  {out[i:i + 16].hex(' ')}")
    print()
    print("   Each byte's top three bits are an instruction and the low five a")
    print("   count; a count of 0 means 'read a varint next', seven bits per byte")
    print("   with the high bit as the continuation flag. Five opcodes, and a")
    print("   loader that runs them is executing the data section's bytes to")
    print(f"   produce the data section -- {len(pattern)} bytes of file for {len(out)} bytes of memory.")


if __name__ == "__main__":
    main()
