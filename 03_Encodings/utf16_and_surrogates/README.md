# UTF-16 and surrogates

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** UTF-16 writes most code points as one 16-bit unit and everything above `U+FFFF` as a *surrogate pair* of two units — which is why Windows, Java, JavaScript and SAP all report an emoji's length as 2.

## What the finished page has to answer

- Code unit vs code point: the distinction UTF-8 lets you ignore and UTF-16 does not
- The surrogate ranges `D800–DBFF` and `DC00–DFFF`, and the arithmetic that turns `U+1F600` into `D83D DE00`
- Why those 2,048 code points are reserved and can never be characters — and why Rust's `char` refuses them
- UCS-2: the 1990s belief that 65,536 would be enough, and the systems still living with it
- UTF-32: one unit per code point, four bytes each, simple and almost never on disk
- SAP: a Unicode system's `string` is UTF-16 internally, so `strlen( )` counts units — an emoji is 2, a Polish letter is 1

## The example it will run

Python: `.encode('utf-16-be')` for the same four characters as the UTF-8 page, and the pair arithmetic in ten lines; Rust: `encode_utf16().count()` vs `chars().count()`.

## See also

- [UTF-8 by hand](../utf8_by_hand/README.md)
- [Byte order and the BOM](../byte_order_and_bom/README.md)
