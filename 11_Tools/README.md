# 11_Tools — the toolbox for character data

**Level:** 201 · for anyone with a terminal

Chapters 1 to 10 are about what text *is*. This chapter is about the programs you already run over it every day — `grep`, `find`, `sort`, `tr` — plus the handful worth installing. None of them is *about* encodings. Every one of them has already made an encoding decision on your behalf before it printed its first line, and not one of them tells you which.

That is the chapter in a sentence, and it is why these pages exist separately from [06_Terminal](../06_Terminal/README.md). Chapter 6 is the tools whose *job* is bytes — `xxd`, `od`, `iconv`, `file`. This chapter is the tools whose job is something else entirely, and which turn out to have an opinion about your text anyway.

## The three questions

Ask these of any tool before you trust its answer about non-ASCII text. Each page here answers all three for one tool.

| | The question | Why it bites |
|---|---|---|
| 1 | Does it work in **bytes** or in **characters**? | `.` means one byte to `grep` in the C locale and one character to `grep` in a UTF-8 locale — [same file, two counts](grep/README.md) |
| 2 | **Who decided** — the locale, a flag, or the tool itself? | `grep` asks the locale; [`rg` asks the first bytes of the file](ripgrep/README.md) and never the locale; `find` asks nobody and compares bytes |
| 3 | What does it do when the text is **not valid**? | The three answers are refuse, guess, and *silently skip* — and [the third one has no exit code](grep/README.md) |
| 3b | …and when the **pattern** is not valid? | `rg` names the flag that would help; [`rg -P` matches nothing and says nothing](pcre2/README.md) |

## The pages

| # | Page | The question it answers | Status |
|---|---|---|---|
| 1 | [`grep` on text that is not ASCII](grep/README.md) | Why did my search miss a line that is plainly there? | written |
| 2 | [`ripgrep` — the Rust grep](ripgrep/README.md) | What does `rg` decide differently, and when does that matter? | written |
| 3 | [PCRE2 — the other regex engine](pcre2/README.md) | What does `rg -P` buy, and what does it cost? | written |
| 4 | [`find`, and filenames that are bytes](find/README.md) | Why does `cat` open the file that `find -name` cannot see? | written |
| 5 | [`xargs` splits on the wrong things](xargs/README.md) | Why does one apostrophe stop my `find` pipeline? | written |
| 6 | [`sed` matches patterns, not bytes](sed/README.md) | Why does `sed` get right what `tr` gets wrong? | written |
| 7 | [`awk` is three programs](awk/README.md) | Whose `awk` is this, and why does it disagree with itself? | written |
| 8 | [`cut` counts what it is told to count](cut/README.md) | `-b` or `-c`? And why does the same command differ per machine? | written |
| 9 | [`tr` and `sort` work a byte at a time](tr_and_sort/README.md) | Why did deleting `é` damage a different word? | written |
| 10 | [`uni` — the character's name](uni/README.md) | What *is* this character, not just how is it stored? | written |
| 11 | [The five worth installing](worth_installing/README.md) | What do `hexyl`, `uchardet`, `recode`, `dos2unix` and GNU coreutils add? | written |

## What you already have

Nothing on this list needs installing on either macOS or Ubuntu, and the pages above are about the second column, not the first.

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| `grep` | search | a character is whatever the **locale** says; invalid bytes are handled [two different ways by the two greps](grep/README.md); `-P` is GNU-only and [absent from a Mac entirely](pcre2/README.md) |
| `find` | walk a directory | filenames are **bytes**, and `-name` is a byte comparison — even where [the filesystem disagrees](find/README.md) |
| `sort` | order lines | the **locale** picks the order, and byte order is not alphabetical order |
| `tr` | substitute or delete | **bytes only**, always — which is why [it damages the word next door](tr_and_sort/README.md) |
| [`xargs`](xargs/README.md) | turn a list into a command line | splits on spaces *and* quotes, and batches by **bytes** — so the encoding decides how many times your command runs |
| [`sed`](sed/README.md) | edit with patterns | a **sequence**, not a byte set — which is why it repairs what `tr` breaks |
| [`awk`](awk/README.md) | fields and arithmetic | three implementations, two of them called `awk`, and they do not agree |
| [`cut`](cut/README.md) | slice columns | `-b` is honest; `-c` means characters on one platform and bytes on the other |
| `wc` | count | `-c` bytes, `-m` characters, `-l` [newlines](../06_Terminal/trailing_newline/README.md) — three questions, three answers |

## What each of them does with a byte that is not text

The sharpest way to tell these tools apart is to hand them a file they cannot decode. Three lines, all containing the word `line`, the middle one holding the invalid bytes `ff fe`:

| BSD tool, `LC_ALL=en_US.UTF-8` | lines out, of 3 | exit | said |
|---|---|---|---|
| [`grep -a line`](grep/README.md) | **2** | **0** | **nothing at all** |
| [`sed -n '/line/p'`](sed/README.md) | 1 | 1 | `RE error: illegal byte sequence` |
| [`awk '/line/'`](awk/README.md) | 1 | 2 | `towc: multibyte conversion failure`, naming record 2 |
| [`cut -c1-3`](cut/README.md) | 2 | 74 | `Illegal byte sequence` |
| `cut -b1-3` | **3** | 0 | — it never decodes, so it cannot fail this way |

Every one of those runs **3 of 3, exit 0, silently** under `LC_ALL=C`, and on Ubuntu the GNU versions run 3 of 3 in *either* locale. So the table is one platform's behaviour in one locale — but it is the platform and locale a Mac gives you by default.

Two things to take from it. **`grep` is the only one that says nothing and still exits 0**, which is why [its page](grep/README.md) calls that the worst failure shape in this library — the others hand you something a script can catch. And **the escape is the same for all of them**: work in bytes. `LC_ALL=C` for the whole pipeline, or `-b` where the tool offers it.

*(Measured 2026-09-06 on macOS 26.6 and ubuntu:24.04. Not machine-checked — no answer key can hold both platforms.)*

## What is worth installing

`uni` and `rg` earn their place immediately and have a page each; the rest are for a specific bad day and share [one page](worth_installing/README.md), which measures every one of them against the tool you already have.

| Install | What it adds |
|---|---|
| [`uni`](uni/README.md) | the character's **name**, and search *by* name — the column no dump tool has |
| [`rg`](ripgrep/README.md) | one implementation on every platform, no locale — and it reads a UTF-16 file, [as long as it has a BOM](ripgrep/README.md): three marks are tested and UTF-32 is not one of them |
| [`hexyl`](worth_installing/README.md) | `xxd` with colour by byte category |
| [`uchardet`](worth_installing/README.md) | a real encoding detector, where `file` only tells valid-UTF-8 from not |
| [`recode`](worth_installing/README.md) | `iconv` with a bigger table set and a syntax you can type |
| [`dos2unix`](worth_installing/README.md) | the [CRLF](../07_Real_Data/crlf_vs_lf/README.md) kit, with a report mode that changes nothing |
| [`coreutils`](worth_installing/README.md) | the **GNU** tools on a Mac, so you can run both sides of a BSD/GNU split yourself |

## A note on what is machine-checked here

Every other chapter's claims are backed by a program CI runs on Ubuntu *and* macOS. Every page here keeps that contract for what it can, and three of them — [`ripgrep`](ripgrep/README.md), [`uni`](uni/README.md) and [the five worth installing](worth_installing/README.md) — are about tools neither operating system ships, so CI has none of them and no answer key can be recorded from the tool itself. Those pages put the tool's real output in a fence that is **labelled and dated with the two machines it was measured on**, and keep a machine-checked example beside it doing the same job in the standard library — so the claim is still tested, just not by the tool it is about.

## See also

- [06_Terminal](../06_Terminal/README.md) — the tools whose job *is* bytes
- [10_Best_Practices](../10_Best_Practices/README.md) — what to do on Monday, once you can see the problem
- [RESOURCES.md](../RESOURCES.md) — the reading list, and the install table these pages expand
