# Slicing by byte

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `&s[0..2]` is a *byte* range, and it panics at run time if either end lands inside a multibyte character — the one string operation Rust cannot check at compile time, and the reason `get(0..2)` exists.

## What the finished page has to answer

- `&"café"[0..4]` panics: `byte index 4 is not a char boundary` — read the message, then find the boundaries with `char_indices()`
- `is_char_boundary(i)`: the question the panic is asking, available to ask first
- `s.get(0..4)` returns `Option<&str>` — the checked version, the same shape as `checked_add`
- Truncating a `String` to fit a byte budget without cutting a character — the fixed-width-field problem, solved properly
- The Rust library's [String slices ↗](https://masiarek.github.io/rust-learning-library/14_Strings/string_slices/index.html) covers slices as views; this page is only about where the cut may fall

## The example it will run

Rust: every byte index of `café` tested with `is_char_boundary`, the panic caught with `catch_unwind` so the page can show its message, and a `truncate_to_bytes` that never panics.

## See also

- [`String` is bytes that promise UTF-8](../string_is_bytes_that_promise_utf8/README.md)
- [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md)
