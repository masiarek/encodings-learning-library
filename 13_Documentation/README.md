# 13_Documentation — the manual on your own machine

**Level:** 201 · for anyone with a terminal

Every other chapter here teaches you something about text. This one teaches you where to *look it up* — starting from the observation that a stock Mac ships about forty pages of primary material on exactly this subject, under `/usr/share/man`, and almost nobody has opened one. There is a man page per character encoding. There is a one-screen page that names every multibyte function in libc and explains why `setlocale` changes what they all mean. There is a 1996 C API whose flag list is a complete taxonomy of escaping.

And there is a catch, which is the reason this is a chapter rather than a link: **the documentation on your machine is documentation of your machine.** It has a date on it, it is not uniformly maintained, and it describes flags that no longer exist while omitting flags that do. That is the same rule this library already applies to [the Unicode table](../02_Characters/the_table_has_a_version/README.md) — a value read out of the machine is a fact about the machine — one layer up, applied to prose.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [The encoding man pages nobody opens](the_encoding_man_pages/README.md) | What is already installed, and how do I sweep it for a term? | written |
| 2 | [A page has a date](a_page_has_a_date/README.md) | `man 5 utf8` says six bytes. Which year is it saying that from? | written |
| 3 | [What the page does not say](what_the_page_does_not_say/README.md) | The flag works and is documented nowhere. Now what? | written |

## The three questions

Ask these of any manual before you act on it — the same shape as [11_Tools](../11_Tools/README.md)' three questions about a tool.

| | The question | Why it bites |
|---|---|---|
| 1 | **When** was this written? | `man 5 utf8` is dated 2004 and cites a 1998 RFC that was replaced in 2003 — [and it is still right about `iconv`](a_page_has_a_date/README.md) |
| 2 | Does it describe **this machine**? | `mbcs` is a documented Python codec and a `LookupError` here; a stock `ubuntu:24.04` image ships **no man pages at all** |
| 3 | What is it **not** saying? | `iconv` accepts `//TRANSLIT`; [no man page on this Mac mentions it](what_the_page_does_not_say/README.md) |

## Why this chapter is short on answer keys

Nearly every fact in it is machine-dependent, so the pages hold **dated tables** naming the machine they ran on rather than recorded output — the convention [Locale and `LC_CTYPE`](../06_Terminal/locale_and_lc_ctype/README.md) established for the same reason. The three programs behind these pages were written to sidestep it entirely: they do arithmetic, build their own corpus, or ask a registry a question whose answer is a *name*. All three print byte-identical output on macOS 26.6 and `ubuntu:24.04`, which is what makes them keys at all.

## When to read it

Any time. It has no prerequisites beyond a terminal, and it pairs naturally with [11_Tools](../11_Tools/README.md) — that chapter tells you what each tool decided, this one tells you where the tool says so, and where it does not.

## See also

- [11_Tools](../11_Tools/README.md) — one page per tool, and the three questions to ask each one
- [06_Terminal](../06_Terminal/README.md) — the tools whose job *is* bytes, shown in a workflow
- [RESOURCES.md](../RESOURCES.md) — the documentation that is not on your machine: specs, books and talks
- [TOPICS.md](../TOPICS.md) — every term the subject touches, with the pages that cover each
