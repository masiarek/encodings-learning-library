# 05_Rust — the same boundary, enforced by the compiler

**Level:** 101 → 201 · for anyone learning Rust

Rust's `String` is a `Vec<u8>` with one promise attached — the bytes are valid UTF-8 — and everything that feels strange about Rust strings is that promise being kept. These pages connect the type to chapters 2 and 3; the sibling [Rust learning library ↗](https://masiarek.github.io/rust-learning-library/STRINGS.html) owns the memory, ownership and API stories, and is linked from every page here rather than repeated.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [`String` is bytes that promise UTF-8](string_is_bytes_that_promise_utf8/README.md) | What is a `String`, under the hood, and why does `s[0]` not compile? | stub |
| 2 | [`char` is four bytes](char_is_four_bytes/README.md) | Why do `len()`, `chars().count()` and `size_of::<char>()` all disagree? | stub |
| 3 | [From UTF-8, and lossy](from_utf8_and_lossy/README.md) | What do the three ways of turning bytes into a `String` each promise? | stub |
| 4 | [Slicing by byte](slicing_by_byte/README.md) | Why can `&s[0..2]` panic, and what do I call instead? | stub |
