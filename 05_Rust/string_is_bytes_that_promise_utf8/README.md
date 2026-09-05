# `String` is bytes that promise UTF-8

**Level:** 101 → 201 · for anyone learning Rust

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A `String` is a `Vec<u8>` with one extra promise — the bytes are valid UTF-8 — and every strange rule about Rust strings is that promise being kept.

## What the finished page has to answer

- `as_bytes()`, `into_bytes()`, `String::from_utf8(vec)`: the promise made visible as three conversions, one of which returns `Result`
- `len()` counts bytes because the vector counts bytes; `s[0]` does not compile because a byte is not a character
- `&str` is to `String` what `&[u8]` is to `Vec<u8>`: a view, with the same promise attached
- `b"…"` literals are `&[u8; N]`, not `&str` — no promise, so no `.chars()`
- The sibling Rust library owns the memory story — [The anatomy of a `String` ↗](https://masiarek.github.io/rust-learning-library/14_Strings/anatomy_of_a_string/index.html) — and this page owns the *encoding* story; read that one for pointer/len/capacity

## The example it will run

Rust: `"café"` as `String`, `&str`, `&[u8]`; `len` on each; `from_utf8` on the bytes and on the same bytes with one flipped.

## See also

- [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md)
- [`char` is four bytes](../char_is_four_bytes/README.md)
- [From UTF-8, and lossy](../from_utf8_and_lossy/README.md)
