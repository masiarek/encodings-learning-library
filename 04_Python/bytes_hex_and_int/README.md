# Bytes, hex and int

**Level:** 101 → 201 · for Python programmers

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Four conversions — `bytes.hex`, `bytes.fromhex`, `int.from_bytes`, `int.to_bytes` — are the whole toolkit for reading a binary format by hand, and `struct` is the same four with a template.

## What the finished page has to answer

- `int.to_bytes(4, 'big')` and `'little'`: the same 32-bit number, two byte orders, one hex dump each
- `signed=True`: two's complement in one argument, and what `-1` looks like as four bytes
- `struct.pack('<I', n)` / `unpack`: the template letters, and why `<` and `>` are the first thing to read in any format spec
- Base64: a *text* encoding of bytes, not a character encoding — six bits per character, and why a 3-byte group becomes 4
- A worked example: the first 16 bytes of a PNG file, decoded field by field

## The example it will run

Python: round-trip a number, a negative, and a PNG header through all four conversions and `struct`.

## See also

- [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md)
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md)
