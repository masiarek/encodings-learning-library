# Opening a file

**Level:** 101 → 201 · for Python programmers

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `open(path)` with no `encoding=` is a bet on the machine's locale, and the only portable call is `open(path, encoding='utf-8')`; `'rb'` is how you refuse to bet at all.

## What the finished page has to answer

- `locale.getpreferredencoding(False)`: what the bet is on your machine, and how it differs on a colleague's Windows box
- UTF-8 mode (`PYTHONUTF8=1`, `-X utf8`) and PEP 686's plan to make it the default
- Text mode's newline translation: what `\r\n` becomes on read, and why `csv` insists on `newline=''`
- `sys.stdout.encoding`: why a script prints `é` fine in the terminal and crashes under `cron`
- Reading an unknown file: `'rb'`, look at the bytes, *then* decide — the habit this whole library teaches

## The example it will run

Python: write one file three ways and read it back four ways, printing the result and the bytes each time.

## See also

- [Encode, decode and errors](../encode_decode_and_errors/README.md)
- [Locale and LC_CTYPE](../../06_Terminal/locale_and_lc_ctype/README.md)
- [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md)
