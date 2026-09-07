#!/usr/bin/env python3
"""Where the spaces go in a dump, and what choosing a width claims.

Run:  python3 grouping_is_a_choice_py.py
"""


def bits(data: bytes) -> str:
    """The whole input as one run of binary digits, no separators anywhere."""
    return "".join(f"{b:08b}" for b in data)


def group(data: bytes, width: int, base: int = 2) -> str:
    """Cut the BIT stream into width-bit pieces. The last piece may be short."""
    stream = bits(data)
    pieces = [stream[i : i + width] for i in range(0, len(stream), width)]
    if base == 2:
        return " ".join(pieces)
    return " ".join(f"{int(p, 2):0{-(-len(p) // 4)}x}" for p in pieces)


WIDTHS = [
    (4, "a hex digit (a nibble)"),
    (5, "a Base32 character"),
    (6, "a Base64 character"),
    (8, "a byte"),
    (16, "a UTF-16 code unit"),
    (24, "Base64's quantum, or an RGB pixel"),
    (32, "a UTF-32 code unit"),
]


def main() -> None:
    word = "café".encode("utf-8")

    print("1. THE SPACES ARE NOT IN THE FILE")
    print(f"   {word!r} is {len(word)} bytes = {len(word) * 8} bits, and that never changes.")
    print(f"   ungrouped   {bits(word)}")
    print(f"   as hex      {group(word, 8, base=16)}")
    print("   Same file. The separators below are all this program's opinion.")
    print()

    print("2. THE WIDTH YOU PICK IS A CLAIM ABOUT THE UNIT")
    for width, what in WIDTHS:
        shown = group(word, width, base=16 if width % 4 == 0 else 2)
        print(f"   {width:>2} bits = {what:<33} {shown}")
    print("   A width that is not a multiple of 4 has no whole number of hex digits,")
    print("   so those two rows had to be shown in binary. That is not a preference.")
    print()

    print("3. THE GROUPS ARE CUT FROM BITS, NOT FROM BYTES")
    stream = bits(word)
    print(f"   bytes    {' '.join(f'{b:08b}' for b in word)}")
    print(f"   5 bits   {group(word, 5)}")
    print(f"   The second 5-bit group is {stream[5:10]}: the last {len(stream[5:8])} bits of "
          f"{word[0]:#04x} ({stream[5:8]})")
    print(f"   followed by the first {len(stream[8:10])} bits of {word[1]:#04x} ({stream[8:10]}).")
    print("   It belongs to two bytes and to no character at all.")
    print()

    print("4. NOTHING IS PADDED: A SHORT LAST GROUP IS JUST SHORT")
    for width in (16, 24, 32):
        pieces = [len(p) for p in group(word, width).split(" ")]
        print(f"   {width:>2} bits: {len(pieces)} groups, sizes {pieces} -> last one holds "
              f"{pieces[-1]} bits")
    print("   Base64 does the opposite: it pads the last quantum to 24 bits and writes")
    print("   '=' to say how much it added, because there the groups are the encoding.")
    print("   Here they are only the view, so the tail is left ragged.")
    print()

    print("5. ALIGNMENT IS NOT UNDERSTANDING")
    print("   Grouping by 4 bytes will sometimes put a 4-byte character in one group.")
    print("   That is arithmetic about its offset, not knowledge of UTF-8.")
    emoji = "😀".encode("utf-8")
    for pad in range(8):
        data = b"~" * pad + emoji
        start = pad
        contained = start % 4 == 0
        print(f"   offset {start} ({start} % 4 = {start % 4}): {group(data, 32, base=16):<28} "
              f"{'the whole character in one group' if contained else 'split across two groups'}")
    print("   One character earlier in the file and the picture changes. The tool never knew.")
    print()

    print("6. IN PYTHON THE SIGN IS THE DIRECTION")
    print(f"   word.hex(' ', -2)  {word.hex(' ', -2):<20} pairs from the LEFT, short group last")
    print(f"   word.hex(' ',  2)  {word.hex(' ', 2):<20} pairs from the RIGHT, short group first")
    print("   Positive counts back from the end, which is right for a number and wrong")
    print("   for a stream. A hex dump reads left to right, so it wants the negative.")


if __name__ == "__main__":
    main()
