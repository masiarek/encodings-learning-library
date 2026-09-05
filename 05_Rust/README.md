# 05_Rust — the same boundary, enforced by the compiler

**Level:** 101 → 201 · for anyone learning Rust

Rust's `String` is a `Vec<u8>` with one promise attached — the bytes are valid UTF-8 — and everything that feels strange about Rust strings is that promise being kept. These pages connect the type to chapters 2 and 3; the sibling Rust learning library's [Strings chapter ↗](https://masiarek.github.io/rust-learning-library/14_Strings/index.html) owns the memory, ownership and API stories — twelve lessons, plus a reference page for each of the 125 `str` and `String` methods, mapped in [STRINGS.md ↗](https://masiarek.github.io/rust-learning-library/STRINGS.html) — and is linked from every page here rather than repeated. Read in that direction it is a Rust section that happens to be about text; read in this one it is the same bytes, from the encoding's side.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [`String` is bytes that promise UTF-8](string_is_bytes_that_promise_utf8/README.md) | What is a `String`, under the hood, and why does `s[0]` not compile? | stub |
| 2 | [`char` is four bytes](char_is_four_bytes/README.md) | Why do `len()`, `chars().count()` and `size_of::<char>()` all disagree? | stub |
| 3 | [From UTF-8, and lossy](from_utf8_and_lossy/README.md) | What do the three ways of turning bytes into a `String` each promise? | stub |
| 4 | [Slicing by byte](slicing_by_byte/README.md) | Why can `&s[0..2]` panic, and what do I call instead? | stub |
