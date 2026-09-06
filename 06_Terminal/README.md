# 06_Terminal — seeing and making bytes without a language

**Level:** 101 → 201 · for anyone with a terminal

`xxd` and `od` were taught in chapter 1 because nothing later works without them. This chapter is the rest of the toolbox: putting known bytes on a pipe, the last byte of a text file and everything that depends on it, reading a dump's *other* columns without being lied to, re-encoding a file, the locale that silently sets every tool's default, and the tool that guesses.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [`printf` writes bytes](printf_writes_bytes/README.md) | How do I put exactly the bytes I mean in front of `xxd`? | stub |
| 2 | [The trailing newline](trailing_newline/README.md) | Why did `cat` print nothing for a file that is not empty? | written |
| 3 | [A character and its bytes on one line](character_and_its_bytes/README.md) | How do I see the letter and its hex at the same time? | written |
| 4 | [Inspecting a file](inspecting_a_file/README.md) | Which column of a dump is the file, and which ones are the tool guessing? | written |
| 5 | [`iconv`](iconv/README.md) | How do I re-encode a file, and what does its refusal mean? | stub |
| 6 | [Locale and `LC_CTYPE`](locale_and_lc_ctype/README.md) | What is the terminal's default encoding, and which tools change with it? | written |
| 7 | [`file` guesses](file_guesses/README.md) | Why is `file`'s answer an inference, and when is it sure? | stub |
