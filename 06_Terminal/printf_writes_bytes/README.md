# `printf` writes bytes

**Level:** 101 · for anyone with a terminal

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `printf '\xC3\xA9'` puts exactly two bytes on the pipe, while `echo` may or may not add a newline, interpret escapes, or both depending on the shell — so `printf` is the tool for putting *known* bytes in front of `xxd`.

## What the finished page has to answer

- `\xNN` (hex, bash) vs `\NNN` (octal, POSIX): why a script that must run under `sh` uses octal
- `echo -e`, `echo -n`, and the `echo` that prints `-n` literally: the portability mess in one table
- `$'\xC3\xA9'`: bash's ANSI-C quoting, and `%b` for escapes in an argument rather than the format
- `xxd -r -p`: the other direction, from a hex string to bytes, and the `printf | xxd` / `xxd -r` round trip
- Putting a byte the terminal cannot display on the screen, and what the terminal does with it

## The example it will run

Shell: the same two bytes produced five ways, each piped to `xxd` to prove they are identical.

## See also

- [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md)
- [`iconv`](../iconv/README.md)
