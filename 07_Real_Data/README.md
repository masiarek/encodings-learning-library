# 07_Real_Data — the six ways it goes wrong at work

**Level:** 201 · for SAP and interface work

Everything before this chapter is mechanism. This chapter is the six shapes the mechanism takes when a file crosses an interface: a code page named by number, mojibake that can or cannot be reversed, a BOM at the top of a CSV, a field measured in bytes, the 32 bytes where two tables disagree, and the second byte at the end of every Windows line. Each page reproduces the damage in Python so it can be checked, and says what the ABAP side is doing in prose.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [SAP code pages](sap_code_pages/README.md) | What are 1100, 1160, 4110 and 4103, and how do I reproduce an interface's mojibake outside SAP? | stub |
| 2 | [Mojibake round trip](mojibake_round_trip/README.md) | When can damaged text be repaired, and when is the data gone? | stub |
| 3 | [A BOM in a CSV](bom_in_a_csv/README.md) | Why is my first column named `﻿ID`? | stub |
| 4 | [Fixed-width byte fields](fixed_width_byte_fields/README.md) | Why does a 10-byte field hold five Polish letters, and how do I truncate without cutting one in half? | stub |
| 5 | [Windows-1252 vs Latin-1](windows_1252_vs_latin1/README.md) | Why is the text almost right except for `€` and the quotes? | stub |
| 6 | [CRLF vs LF](crlf_vs_lf/README.md) | Where do the `^M`s come from? | stub |

*(ABAP claims on these pages are prose — CI cannot run ABAP — and the Python reproduction beside each one is the checked half.)*
