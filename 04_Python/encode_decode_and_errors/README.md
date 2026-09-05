# Encode, decode and errors

**Level:** 101 → 201 · for Python programmers

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `.encode()` and `.decode()` each take a table name and an `errors` policy, and the policy is your decision about what to do with the bytes you cannot explain — `strict` raises, and every other choice loses something.

## What the finished page has to answer

- The anatomy of `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3` — every word of it is a clue
- `strict` / `replace` / `ignore` / `backslashreplace` / `surrogateescape` on the same bad input, side by side
- `surrogateescape`: how Python reads a filename it cannot decode and still writes it back byte-for-byte
- Codec names and aliases: `latin-1` = `iso-8859-1` = `latin1`; `cp1252` ≠ `latin-1`; `utf-8-sig`; `utf-16` with and without the suffix
- `bytes.decode` vs `str(b, 'utf-8')` vs `codecs.open`: three spellings, one operation

## The example it will run

Python: one bad byte sequence through all five policies, and one good string through six codec aliases.

## See also

- [`str` vs `bytes`](../str_vs_bytes/README.md)
- [Opening a file](../opening_a_file/README.md)
- [Mojibake](../../03_Encodings/mojibake/README.md)
