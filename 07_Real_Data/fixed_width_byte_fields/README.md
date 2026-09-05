# Fixed-width byte fields

**Level:** 201 → 301 · for interface work

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A fixed-width interface allocates *bytes*, not characters, so a 10-byte field holds ten ASCII letters or five Polish ones with room for nothing, and truncating on a byte boundary can cut a UTF-8 character in half.

## What the finished page has to answer

- Byte width vs character width: the same `LENGTH 10` meaning two different things on the two sides of an interface
- Padding: what the space character is under each encoding, and why a UTF-16 field padded with `0x20` is corrupt
- Cutting inside a sequence: what Python (`errors=`), Rust (`from_utf8` error), `iconv`, and SAP each do with the half a character left behind
- Truncating correctly: back up to the last character boundary — `is_char_boundary` in Rust, a loop over `char_indices` in either language
- ABAP: `c LENGTH 10` is ten *characters* — twenty bytes in UTF-16 — and the conversion to a byte-counted file format is where the width changes
- The mainframe aside: EBCDIC fixed-width records, where even `A` is a different byte

## The example it will run

Python + Rust: pack `'Zażółć'` into a 10-byte field, truncate naively (broken), truncate on a boundary (correct), and show both readers' reactions.

## See also

- [Slicing by byte](../../05_Rust/slicing_by_byte/README.md)
- [SAP code pages](../sap_code_pages/README.md)
