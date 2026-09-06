# `iconv`

**Level:** 101 → 201 · for anyone with a terminal

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `iconv -f FROM -t TO` re-encodes bytes from one table to another, and its refusal — `illegal input sequence at position N` — is the terminal's `UnicodeDecodeError`.

## What the finished page has to answer

- `iconv -l`: the tables your machine knows, and the aliases (`LATIN1`, `ISO-8859-1`, `ISO8859-1`) that name the same one
- Latin-1 to UTF-8 on a real file, dumped before and after: the one-byte `E9` becoming `C3 A9`
- `//TRANSLIT` and `//IGNORE`: the `errors=` policies, spelled as a suffix on the target
- What `iconv` cannot do: detect. It converts what you tell it from what you tell it, and a wrong `-f` produces clean mojibake without complaint
- GNU vs macOS `iconv`: the same interface, different table lists, different `//TRANSLIT` results — why this page's example sticks to the tables both have

## The example it will run

Shell: a Latin-1 file made with `printf`, converted to UTF-8 and to CP1252, each step dumped with `xxd`; one deliberate failure.

Already demonstrated elsewhere, so this page should link rather than repeat it: the UTF-8 → UTF-16 round trip, the byte order `iconv` picks when you do not name one, and the size arithmetic are in [Inspecting a file with `od`](../inspecting_a_file/README.md). What is left for this page is `iconv`'s own behaviour — `-l`, the alias lists, `//TRANSLIT` and `//IGNORE`, and what its refusal means.

## See also

- [Inspecting a file with `od`](../inspecting_a_file/README.md) — `iconv` to UTF-16, dumped before and after
- [Code pages](../../02_Characters/code_pages/README.md)
- [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md)
