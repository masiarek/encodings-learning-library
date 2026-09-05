# UTF-8 by hand

**Level:** 101 → 201 · the lesson this library is built around

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** UTF-8 writes a code point as one to four bytes: a lead byte whose top bits announce the count, then continuation bytes that all start with `10`. You can encode `é` to `C3 A9` with a pencil, and after this page a hex dump of any text is readable.

## What the finished page has to answer

- The four templates, one table: `0xxxxxxx` · `110xxxxx 10xxxxxx` · `1110xxxx 10xxxxxx 10xxxxxx` · `11110xxx` + three
- Done by hand: `é` U+00E9 → `C3 A9`; `€` U+20AC → `E2 82 AC`; `😀` U+1F600 → `F0 9F 98 80`; and `A` → `41`, unchanged — why ASCII files are already UTF-8
- Decoding by hand: read the lead byte, count the `1`s, strip the markers, concatenate the payload bits
- Self-synchronising: why you can start reading in the middle of a file and find the next character boundary within three bytes
- What *invalid* means: a lone continuation byte, an overlong `C0 80`, a surrogate, anything above U+10FFFF — the templates' own rules; *who checks them, and when*, is [Validation is a boundary](../validation_is_a_boundary/README.md)
- Why `len()` in bytes is always ≥ the number of code points, and by how much for Polish, Russian, Chinese and emoji text

## The example it will run

Python: an encoder written from the templates, checked against `.encode('utf-8')` on every code point; Rust: the decoder side, checked against `from_utf8`; shell: `printf` the bytes and `xxd -b` them.

## See also

- [Validation is a boundary](../validation_is_a_boundary/README.md) — the same templates, from the checker's side
- [Unicode code points](../../02_Characters/unicode_code_points/README.md)
- [UTF-16 and surrogates](../utf16_and_surrogates/README.md)
- [Mojibake](../mojibake/README.md)
