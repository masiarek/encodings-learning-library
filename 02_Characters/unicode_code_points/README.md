# Unicode code points

**Level:** 101 → 201 · for anyone starting from zero

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Unicode assigns every character a number called a code point, written `U+XXXX` — and a code point is a *number*, not a byte. How it becomes bytes is the next chapter's question, and keeping the two apart is most of the subject.

## What the finished page has to answer

- 1,114,112 slots, 17 planes, and the Basic Multilingual Plane where almost everything you type lives
- `U+00E9` and `0xE9` are the same number and different things: one is a code point, the other a byte under one particular table
- The first 256 code points *are* Latin-1 — which is why Latin-1 decoding never fails, and why that is a trap
- `ord` and `chr` are code-point functions; `unicodedata.name('é')` is how you ask what a number is
- Where Polish lives (`U+0104` Ą … `U+017C` ż), where the euro lives (`U+20AC`), where emoji live (above `U+FFFF`, which is why UTF-16 needs pairs)
- Rust's `char` is exactly one code point in the scalar range — surrogates excluded — and `'\u{1F600}'` is how you write one

## The example it will run

Python: walk a string printing code point, `U+` form, and `unicodedata.name`; Rust: the same with `char::escape_unicode`.

## See also

- [Code pages](../code_pages/README.md)
- [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md)
- [A code point is not a character](../a_code_point_is_not_a_character/README.md)
