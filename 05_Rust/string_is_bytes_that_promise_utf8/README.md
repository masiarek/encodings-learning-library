# `String` is bytes that promise UTF-8

**Level:** 101 → 201 · for anyone learning Rust

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A `String` is a `Vec<u8>` with one extra promise — the bytes are valid UTF-8 — and every strange rule about Rust strings is that promise being kept.

<img src="img/same_len_different_meaning.svg" width="840" alt="Three Rust strings drawn as bytes. noodles is seven ASCII bytes and seven characters. oodles borrows six of the same bytes. poodles is the three-character string U+0CA0 underscore U+0CA0, seven bytes because each Kannada character takes three. noodles and poodles both report len() == 7.">

Two of those strings report the same length and mean nothing like the same thing. That is the whole lesson: `len()` is a **byte** count, and it is the only count a `String` can hand you without decoding anything first — which is why [`chars().count()`](../char_is_four_bytes/README.md) is a separate, slower question.

The three variables are the example [*Programming Rust*, 2nd ed. ↗](https://openlibrary.org/isbn/9781492052593) uses to introduce `String`, `&str` and `str`; its own figure draws the *ownership* — stack frame, heap buffer, capacity, who borrows whom. This one is drawn for this library and asks the *encoding* question about the same three lines instead. Read them together: the memory story is [the sibling library's ↗](https://masiarek.github.io/rust-learning-library/14_Strings/anatomy_of_a_string/index.html), and the byte values here are the real UTF-8 encodings — `ಠ` is U+0CA0, `E0 B2 A0`.

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
