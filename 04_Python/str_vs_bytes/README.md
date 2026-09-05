# `str` vs `bytes`

**Level:** 101 · for Python programmers

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `str` is a sequence of code points and `bytes` is a sequence of numbers 0..255; they never mix, and `TypeError: can't concat str to bytes` is the boundary refusing to be crossed silently.

## What the finished page has to answer

- Indexing each: `'café'[3]` is `'é'`, `b'caf\xc3\xa9'[3]` is `195` — a character versus a number
- `len` on each, and why they differ by exactly the number of non-ASCII characters' extra bytes
- Literals: `'…'`, `b'…'`, and why `b'é'` is a syntax error
- `repr` of each: what Python shows you, and why `b'A'` is a display choice, not a fact about the byte
- `bytearray` and `memoryview`: the mutable and the zero-copy views of the same numbers
- One line of history: Python 2's `str` was bytes, and every `u''` prefix in old code is that scar

## The example it will run

Python: the same four strings as `str` and as `bytes`, indexed, sliced, measured, and concatenated with each other until the TypeError.

## See also

- [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md)
- [Encode, decode and errors](../encode_decode_and_errors/README.md)
