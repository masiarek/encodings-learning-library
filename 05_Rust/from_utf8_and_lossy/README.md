# From UTF-8, and lossy

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `String::from_utf8` returns a `Result` because bytes might not be text; `String::from_utf8_lossy` replaces what it cannot read with `U+FFFD`; and `from_utf8_unchecked` is you signing the promise yourself, with `unsafe` as the signature.

## What the finished page has to answer

- `Utf8Error::valid_up_to()` and `error_len()`: the error tells you exactly where the bytes stopped being text — the same information as Python's `position 3`
- `from_utf8_lossy` returns `Cow<str>`: borrowed when nothing was wrong, owned when it had to replace — and why that is the right type
- `OsString` / `OsStr`: the type for a filename that was never promised to be UTF-8, and `.to_string_lossy()` at the boundary
- Reading a file: `fs::read` gives `Vec<u8>` and `fs::read_to_string` gives `String` or an error — the same `'rb'` vs text-mode choice as Python's `open`
- The `unsafe` one: when it is legitimate (you just validated) and what happens when it is not (undefined behaviour, not a panic)

## The example it will run

Rust: the same bad byte sequence through `from_utf8` (print the error's fields), `from_utf8_lossy`, and a hand-rolled `backslashreplace`.

## See also

- [`String` is bytes that promise UTF-8](../string_is_bytes_that_promise_utf8/README.md)
- [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md)
