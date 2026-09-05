# Control characters

**Level:** 101 · for anyone starting from zero

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** The first 32 codes are commands, not letters, and three of them — TAB, LF and CR — decide how every text file is cut into lines and columns.

## What the finished page has to answer

- What `\t`, `\n`, `\r` and `\0` are as bytes, and what `od -c` and `cat -A` show for each
- Why a Windows file shows `^M` at every line end in vim, and doubles every line in a diff
- NUL: why a C string ends at it, why a Python `str` can hold it, and why a C API given one silently truncates
- ESC and the terminal colour sequences — a control character that is still a live protocol
- BEL, BS, FF: the ones you will only ever meet in a hex dump, and how to recognise them there

## The example it will run

Python + shell: print each control byte three ways; `printf` a file with mixed endings and dump it.

## See also

- [A character is a number](../a_character_is_a_number/README.md)
- [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md)
