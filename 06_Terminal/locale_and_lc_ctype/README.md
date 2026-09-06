# Locale and `LC_CTYPE`

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** The locale is the terminal's default encoding, `LC_CTYPE` is the variable that sets it, and `wc -m`, `tr`, `sort`, and Python's default `open()` all change behaviour with it — this machine, measured on 2026-09-05, was running with `LC_CTYPE=C`.

## What the finished page has to answer

- `locale`: reading the current settings, and what `C`, `POSIX`, `C.UTF-8` and `en_US.UTF-8` each promise
- `wc -c` vs `wc -m` on `café`: bytes vs characters, and how `-m` answers 5 under `LC_ALL=C` and 4 under a UTF-8 locale
- `LC_ALL` overrides everything, `LANG` is the fallback, and the precedence between them
- The two layers a "terminal encoding" setting can mean, and which one a program can actually see — see below
- Why `tools/run_examples.py` pins `LC_ALL=C` for every example in this library, and what it would cost not to
- Python: `locale.getpreferredencoding()` and `sys.stdout.encoding` follow the locale — except that UTF-8 mode turns *itself* on under the C locale, which it has done since 3.7 and which is not the same thing as the 3.15 default

## The terminal's own settings are not the locale

Apple's help page for this — *Display high-bit characters in Terminal on Mac* — walks you through three checkboxes, and it is worth reading once for what they are, as long as you notice that they belong to **two different layers** and only one of them is visible to a program.

- **"Text encoding"** (Profiles ▸ Advanced ▸ International) is Terminal decoding the bytes a program writes *to* it, and encoding what you type. That is a display decision, made by the emulator, about bytes it did not produce. `wc` cannot see it. Neither can `python3`, nor any example in this library.
- **"Set locale environment variables on startup"** sits in the same panel and is a completely different mechanism: it puts `LANG` / `LC_*` into the environment of the shell Terminal launches — derived from your **Region** in System Settings, not from the encoding menu above it. *This* is the one every program reads, and the only one this page is about.
- **"Escape non-ASCII input with Control-V"** (Advanced ▸ Input) touches the input path only — a literal-next prefix for line editors that needed one before a high byte.

Set the first without the second and you get a terminal decoding, correctly, bytes the program was never told to produce. That is the failure the page's title is really about, and it is why the fix for mojibake is almost never the encoding menu.

**Measured 2026-09-06, before trusting any of the three:** the `Basic` profile carries no encoding, locale, or escape key at all — not in `defaults read com.apple.Terminal`, and not in the shipped `Basic.terminal` inside the app bundle — so all three sit at built-in defaults and **cannot be read back from a script**. Terminal.app 2.15, macOS 26.6.2. An audit of these settings has to read the GUI, which is worth knowing before promising to check them across a fleet.

## The example it will run

Shell: `wc -m` and `tr` under `LC_ALL=C` and under `LC_ALL=en_US.UTF-8`, side by side.

**That second locale is no longer needed to make the point** (measured 2026-09-06, and it removes the recording problem this section used to describe). On one file holding `café\n`, under `LC_ALL=C`, with `PYTHONUTF8` unset:

```text title="Measured 2026-09-06 — abridged session, macOS 26.6 / Python 3.14.2, reproduced on python:3.12-slim"
  wc -m  :        6        <- obeys the locale: US-ASCII, so it counts bytes
  len()  : 5               <- Python decoded UTF-8 anyway

  sys.flags.utf8_mode         1          with PYTHONUTF8 unset
  locale.getencoding()        US-ASCII   the locale, reported honestly
  sys.stdout.encoding         utf-8      what Python actually does
```

Two tools, one file, one environment, two correct answers — because **Python turns UTF-8 mode on by itself when the locale is `C` or `POSIX`** (PEP 540), while `wc` simply obeys what it was given. The `locale.getencoding()` / `sys.stdout.encoding` pair is what makes the override visible instead of mysterious. Every CI runner has the C locale, so this half is recordable as it stands; the `en_US.UTF-8` half still has to be checked against `locale -a` on each runner before it is promised.

One worked instance is already measured elsewhere: `od -a` on macOS asks `isprint()` in the current locale, so the same command on the same file prints a different row under `LC_ALL=C` than under a UTF-8 locale — and `wc -m` counts bytes in the C locale and characters in a UTF-8 one. Both are in [Inspecting a file](../inspecting_a_file/README.md).

## See also

- [Inspecting a file](../inspecting_a_file/README.md) — two tools whose output changes with `LC_CTYPE`

- [Opening a file](../../04_Python/opening_a_file/README.md)
- [`printf` writes bytes](../printf_writes_bytes/README.md)
