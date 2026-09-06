# `char` is four bytes

**Level:** 101 → 201 · for anyone learning Rust

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A `char` is one Unicode scalar value stored in four bytes, while the same character inside a `String` takes one to four — so `chars().count()` and `len()` disagree, and neither of them counts what a person calls a character.

## What the finished page has to answer

- `size_of::<char>()` is 4; `'é'.len_utf8()` is 2; `"é".len()` is 2; `'é' as u32` is 233 — four numbers, one character
- `chars()`, `bytes()`, `char_indices()`: three walks over the same string, and what each yields for `café`
- Why `char` cannot hold a surrogate, and what `char::from_u32(0xD800)` returns
- `'\u{1F600}'`: writing a code point in source, and `.escape_unicode()` for reading one back
- The Rust library's [Meet the `char` ↗](https://masiarek.github.io/rust-learning-library/14_Strings/meet_the_char/index.html) covers the type and [Why a `char` is 32 bits wide ↗](https://masiarek.github.io/rust-learning-library/14_Strings/why_char_is_32_bits/index.html) covers the width — U+10FFFF needs 21 bits, rounded up to an addressable 32; this page connects both to chapter 2's code points and chapter 3's bytes

## The example it will run

Rust: the four numbers for `A`, `é`, `€`, `😀`; then the three walks over `café`.

## See also

- [Unicode code points](../../02_Characters/unicode_code_points/README.md)
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md)
