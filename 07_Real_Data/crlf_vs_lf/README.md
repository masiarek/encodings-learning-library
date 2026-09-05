# CRLF vs LF

**Level:** 101 · for anyone starting from zero

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A line ends with `0A` on Unix and `0D 0A` on Windows, and the stray `0D` is the `^M` in vim, the phantom column in a CSV, the `\r` on the end of every string you read, and the git warning about line endings.

## What the finished page has to answer

- `od -c` on a two-line file made each way: the whole lesson is in the dump
- Where the two bytes come from: a teletype's *carriage return* and *line feed* were two motions, and DOS kept both
- `dos2unix`, `tr -d '\r'`, `sed 's/\r$//'`: three ways to strip, and why `tr` is the one that is always installed
- Python: universal newlines on read turn both into `\n`; on write the default follows the OS; `csv` wants `newline=''` so it can write `\r\n` itself
- git: `core.autocrlf`, `.gitattributes`, and the `LF will be replaced by CRLF` warning decoded
- SAP: `cl_abap_char_utilities=>cr_lf` vs `=>newline`, and the download that grows a `#` at every line end when displayed in the wrong place

## The example it will run

Shell + Python: make both files with `printf`, dump them, strip one, and read both with Python's universal newlines.

## See also

- [Control characters](../../02_Characters/control_characters/README.md)
- [Opening a file](../../04_Python/opening_a_file/README.md)
