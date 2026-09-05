# A BOM in a CSV

**Level:** 101 → 201 · for anyone who has opened a CSV from Excel

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Excel writes `EF BB BF` at the start of a UTF-8 CSV, so the first column of the first row is named `\ufeffID` and every lookup on `'ID'` fails; `encoding='utf-8-sig'` on the way in is the whole fix, and on the way out it is what makes Excel read your UTF-8 correctly.

## What the finished page has to answer

- Seeing it: `xxd file.csv | head -1` and the three bytes before the first letter
- The failing lookup: `row['ID']` raising `KeyError` while `print(row.keys())` shows a key that looks exactly like `ID`
- `utf-8-sig` on read: strips a BOM if present, harmless if not — so it is the safe default for any CSV of unknown origin
- `utf-8-sig` on write: why Excel (and only Excel) needs the BOM to guess UTF-8 rather than the local code page
- SAP: the inbound file with a BOM and the first field that never matches — the same bug, wearing a different error message

## The example it will run

Python: write a CSV with `utf-8-sig`, dump it, read it back with `utf-8` (the failing key) and `utf-8-sig` (the fix).

## See also

- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md)
- [Opening a file](../../04_Python/opening_a_file/README.md)
