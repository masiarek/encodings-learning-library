# A code point is not a character

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** What a person calls one character can be several code points — `é` as `e` plus a combining acute, a flag emoji as two, a family emoji as seven — so "how many characters" has a fourth honest answer, grapheme clusters, and neither Python's nor Rust's standard library will give it to you.

## What the finished page has to answer

- Combining marks: `U+0065 U+0301` prints identically to `U+00E9` and compares unequal — the preview of [normalization](../../04_Python/normalization/README.md)
- Grapheme clusters: the unit a cursor moves over, defined by Unicode's segmentation rules, not by any language's `len`
- ZWJ sequences: how 👨‍👩‍👧‍👦 is seven code points, and what `len()` and `.chars().count()` each say about it
- The five answers to "how long": bytes, code units, code points, graphemes, and terminal columns — one table
- Why the standard libraries stop at code points, and what `unicode-segmentation` (Rust) and `regex` `\X` (Python, third-party) add
- The shortest way to get the number without any of them: **`rg -P -o '\X' | wc -l`**, which is [already installed and measured](../../11_Tools/pcre2/README.md) — 👨‍👩‍👧‍👦 is 26 bytes, 7 code points and 1 grapheme, and that page prints all three

## The example it will run

Python: the five counts for four strings; Rust: `len()` vs `chars().count()` on the same four, and a hand-rolled grapheme count for the combining-mark case only.

## See also

- [Unicode code points](../unicode_code_points/README.md)
- [Normalization](../../04_Python/normalization/README.md)
- [`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md)
- [PCRE2 — the other regex engine](../../11_Tools/pcre2/README.md) — the one tool in the toolbox that can count graphemes
