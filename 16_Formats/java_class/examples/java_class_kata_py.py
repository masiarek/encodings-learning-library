#!/usr/bin/env python3
"""Kata: five strings, and the length field javac writes for each."""


def mutf8(s):
    out = bytearray()
    for ch in s:
        c = ord(ch)
        if c == 0:
            out += b"\xc0\x80"
        elif c < 0x80:
            out.append(c)
        elif c < 0x800:
            out += bytes([0xC0 | c >> 6, 0x80 | c & 0x3F])
        elif c < 0x10000:
            out += bytes([0xE0 | c >> 12, 0x80 | c >> 6 & 0x3F, 0x80 | c & 0x3F])
        else:
            c -= 0x10000
            for unit in (0xD800 | c >> 10, 0xDC00 | c & 0x3FF):
                out += bytes([0xE0 | unit >> 12, 0x80 | unit >> 6 & 0x3F, 0x80 | unit & 0x3F])
    return bytes(out)


def main():
    print(f"   {'string':<12} {'chars':>5} {'UTF-16':>6} {'UTF-8':>5} {'MUTF-8':>6}   the two length bytes")
    print()
    for s in ("A", "caf\u00e9", "\u0141\u00f3d\u017a", "a\x00b", "\U0001F600"):
        m = mutf8(s)
        print(f"   {s!r:<12} {len(s):>5} {len(s.encode('utf-16-le')) // 2:>6} {len(s.encode('utf-8')):>5} {len(m):>6}   {len(m).to_bytes(2, 'big').hex(' ')}")
    print()
    print("   The field is the last column, big-endian. It equals the UTF-8 length")
    print("   for three of the five and differs for the two the encoding exists")
    print("   to change: the NUL costs one byte more, the emoji two. It never")
    print("   equals the character count except for pure ASCII, and it equals")
    print("   the UTF-16 count for nothing here but 'A'.")


if __name__ == "__main__":
    main()
