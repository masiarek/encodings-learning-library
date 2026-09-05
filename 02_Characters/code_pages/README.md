# Code pages

**Level:** 101 → 201 · for anyone starting from zero

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Every code page agrees with ASCII on the first 128 numbers and disagrees with every other code page on the second 128 — so a byte above `0x7F` means nothing until you know which table it was written under.

## What the finished page has to answer

- Latin-1 (ISO-8859-1): the one table where byte value and Unicode code point are the same number, 0..255
- Windows-1252: Latin-1 with 32 of its slots reassigned (`0x80` is €, `0x93`/`0x94` are the smart quotes) — the source of most "almost right" text
- Latin-2 (ISO-8859-2) and Windows-1250: where `ą ę ł ś ż` lived before UTF-8, and why a Polish file from 2005 is unreadable under Latin-1
- CP437: the DOS table, box-drawing characters and all; CP850; the mainframe's EBCDIC, which does not even agree on `A`
- The demonstration: one byte, `0xE9`, decoded under six tables, giving six different characters — and `0x41` giving `A` under all of them
- How SAP names these tables by number (1100, 1160, 1401 …) — the full table is in [SAP code pages](../../07_Real_Data/sap_code_pages/README.md)

## The example it will run

Python: `bytes([0xE9]).decode(cp)` across `latin-1`, `cp1252`, `iso8859_2`, `cp437`, `cp1250`, `koi8_r`; shell: `iconv` between two of them.

## See also

- [A character is a number](../a_character_is_a_number/README.md)
- [Unicode code points](../unicode_code_points/README.md)
- [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md)
