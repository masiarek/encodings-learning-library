# Locale and `LC_CTYPE`

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** The locale is the terminal's default encoding, `LC_CTYPE` is the variable that sets it, and `wc -m`, `tr`, `sort`, and Python's default `open()` all change behaviour with it — this machine, measured on 2026-09-05, was running with `LC_CTYPE=C`.

## What the finished page has to answer

- `locale`: reading the current settings, and what `C`, `POSIX`, `C.UTF-8` and `en_US.UTF-8` each promise
- `wc -c` vs `wc -m` on `café`: bytes vs characters, and how `-m` answers 5 under `LC_ALL=C` and 4 under a UTF-8 locale
- `LC_ALL` overrides everything, `LANG` is the fallback, and the precedence between them
- Why `tools/run_examples.py` pins `LC_ALL=C` for every example in this library, and what it would cost not to
- Python: `locale.getpreferredencoding()` and `sys.stdout.encoding` follow the locale — unless UTF-8 mode is on, which it is by default from 3.15

## The example it will run

Shell: the same `wc -m` and `tr` under `LC_ALL=C` and under `LC_ALL=en_US.UTF-8`, side by side. (Only if both locales exist on every CI runner; otherwise the UTF-8 half is prose.)

One worked instance is already measured: `od -a` on macOS asks `isprint()` in the current locale, so the same command on the same file prints a different row under `LC_ALL=C` than under a UTF-8 locale — and `wc -m` counts bytes in the C locale and characters in a UTF-8 one. Both are in [Inspecting a file with `od`](../inspecting_a_file/README.md).

## See also

- [Inspecting a file with `od`](../inspecting_a_file/README.md) — two tools whose output changes with `LC_CTYPE`

- [Opening a file](../../04_Python/opening_a_file/README.md)
- [`printf` writes bytes](../printf_writes_bytes/README.md)
