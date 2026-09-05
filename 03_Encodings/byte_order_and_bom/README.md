# Byte order and the BOM

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A number wider than one byte has to be written in *some* order, and the byte order mark is a code point, `U+FEFF`, put first so the reader can tell which — in UTF-8 it is `EF BB BF`, and it is the reason a CSV's first column is called `\ufeffID`.

## What the finished page has to answer

- Little-endian and big-endian with `int.to_bytes(4, 'little')` and `'big'`, and why the network and the x86 chip disagree
- `FF FE` vs `FE FF` at the top of a UTF-16 file: the same code point, mirror-imaged, so the reader learns the order from it
- Why UTF-8 has no byte-order problem and still gets a BOM — Windows Notepad and Excel write one anyway
- `utf-8-sig` in Python: strips it on read, writes it on write; and why Excel needs it to open UTF-8 correctly
- What a BOM breaks: a shell script's `#!`, a JSON parser, a `grep` for `^ID`, a SAP inbound file

## The example it will run

Python: `to_bytes` both orders; encode `'ID'` as `utf-16`, `utf-16-le`, `utf-8-sig` and dump each; shell: `xxd` on a file Excel would write.

## See also

- [UTF-16 and surrogates](../utf16_and_surrogates/README.md)
- [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md)
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md)
