#!/usr/bin/env python3
"""A ten-line xxd, so the columns stop being magic.

Run:  python3 reading_a_hex_dump_py.py
"""


def dump(data: bytes, width: int = 16) -> str:
    """Offset | hex bytes | printable ASCII, the way xxd and hexdump lay it out."""
    lines = []
    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]
        hexes = " ".join(f"{b:02x}" for b in chunk)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{offset:08x}  {hexes:<{width * 3 - 1}}  |{text}|")
    return "\n".join(lines)


def main() -> None:
    print("1. THE SAME THREE COLUMNS, BUILT BY HAND")
    print(dump(b"Hi there\n"))
    print()

    print("2. OFFSETS ARE BYTE POSITIONS, IN HEX, SO LINE TWO STARTS AT 0x10 = 16")
    print(dump(b"The quick brown fox jumps over it\n"))
    print()

    print("3. WHAT 'PRINTABLE' MEANS: 32..126 get a character, everything else a dot")
    print(dump(b"tab\there\nnew line\x00null\x7fdel"))
    print()

    print("4. THE SHORTCUT: bytes.hex(' ') is the middle column on its own")
    word = "café".encode("utf-8")
    print(f"   {word!r}")
    print(f"   {word.hex(' ')}")
    print(f"   len('café') = {len('café')} characters, len(word) = {len(word)} bytes")
    print()

    print("5. HOW MANY BYTES IS THIS TEXT?  Count the hex pairs, or ask.")
    for s in ("Hi", "Hi there\n", "café", "naïve façade"):
        print(f"   {s!r:<16} {len(s.encode('utf-8')):>2} bytes   {s.encode('utf-8').hex(' ')}")


if __name__ == "__main__":
    main()
