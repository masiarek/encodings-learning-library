# SAP code pages

**Level:** 201 · for SAP work

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** SAP names encodings by number — 1100 is Latin-1, 1160 is Windows-1252, 1401 is Latin-2, 4110 is UTF-8, 4102 and 4103 are UTF-16 big- and little-endian — and a file interface that names the wrong one produces mojibake you can reproduce exactly in Python with the same tables.

## What the finished page has to answer

- The number table, with the Python codec name beside each row — and the standing rule: **verify any number against the system's own code-page table before relying on it**, because a wrong number here is a wrong interface
- `string` vs `xstring`: characters vs bytes, the same line as Python's `str` vs `bytes`; on a Unicode system a `string` is UTF-16 inside
- `cl_abap_codepage=>convert_to( )` / `convert_from( )`: `.encode()` and `.decode()` with a code-page argument
- `OPEN DATASET … IN TEXT MODE ENCODING UTF-8` vs `ENCODING NON-UNICODE` vs `IN BINARY MODE`: text mode, locale bet, and `'rb'`, respectively
- Reproducing an interface's mojibake in Python: the file written under 4110 and read under 1100, side by side with `.encode('utf-8').decode('latin-1')`
- *(ABAP claims are prose only — CI cannot run ABAP — and the Python reproduction is the checked half.)*

## The example it will run

Python: the code-page table as a dict of SAP number → codec, one string encoded under each, and the 1100-reads-4110 mojibake reproduced.

## See also

- [Code pages](../../02_Characters/code_pages/README.md)
- [Mojibake round trip](../mojibake_round_trip/README.md)
- [Windows-1252 vs Latin-1](../windows_1252_vs_latin1/README.md)
