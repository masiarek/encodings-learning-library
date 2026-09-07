# 11_Tools — the toolbox for character data

**Level:** 201 · for anyone with a terminal

Chapters 1 to 10 are about what text *is*. This chapter is about the programs you already run over it every day — `grep`, `find`, `sort`, `tr` — plus the handful worth installing. None of them is *about* encodings. Every one of them has already made an encoding decision on your behalf before it printed its first line, and not one of them tells you which.

That is the chapter in a sentence, and it is why these pages exist separately from [06_Terminal](../06_Terminal/README.md). Chapter 6 is the tools whose *job* is bytes — `xxd`, `od`, `iconv`, `file` — shown inside a workflow: one file, five questions, which column is the file and which is a guess. This chapter is the tools whose job is something else entirely, and which turn out to have an opinion about your text anyway.

The three dump tools — [`hexdump`](hexdump/README.md), [`xxd`](xxd/README.md) and [`od`](od/README.md) — are the deliberate exceptions, and they are here rather than in chapter 6 because the question they answer is a *tool-choice* question: which one to type, what each decided before it printed a line, which you can paste into a bug report and expect the reader to see what you saw, which will give you the file back afterwards, and which will simply be there when nothing else is. That is this chapter's job. Chapter 6 still owns the workflow.

[Typing a character you cannot type](typing_a_character/README.md) is the other way round from the rest of the chapter, and belongs here for the same reason: it is a tool-choice question. The compose key, Vim's digraphs, `uni print` and a macOS keyboard layout are four tools for one job, each with its own table and its own idea of what a character is called — and the chapter's first question, *bytes or characters*, has a twin here: *whose table*.

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
| 4 | [`--pre` and `-z` — decompress, then decode](decompress_then_decode/README.md) | Why does `rg -z` find nothing in a file `file` calls gzip? | written |
| 5 | [`find`, and filenames that are bytes](find/README.md) | Why does `cat` open the file that `find -name` cannot see? | written |
| 6 | [`xargs` splits on the wrong things](xargs/README.md) | Why does one apostrophe stop my `find` pipeline? | written |
| 7 | [`sed` matches patterns, not bytes](sed/README.md) | Why does `sed` get right what `tr` gets wrong? | written |
| 8 | [`awk` is three programs](awk/README.md) | Whose `awk` is this, and why does it disagree with itself? | written |
| 9 | [`cut` counts what it is told to count](cut/README.md) | `-b` or `-c`? And why does the same command differ per machine? | written |
| 10 | [`tr` and `sort` work a byte at a time](tr_and_sort/README.md) | Why did deleting `é` damage a different word? | written |
| 11 | [`diff` compares lines, `cmp` compares bytes](diff_and_cmp/README.md) | Why does `diff` say the line changed when both sides look identical? | written, 2026-09-07 |
| 12 | [`split`, `paste`, `look` and `tee`](look_paste_tee_split/README.md) | Why is the piece my splitter wrote not valid UTF-8 any more? | written, 2026-09-07 |
| 13 | [`hexdump` is a format engine wearing six presets](hexdump/README.md) | Why is my dump showing the bytes in the wrong order? | written |
| 14 | [`xxd` is the dump you can put back](xxd/README.md) | Which column of a dump is the file, and how do I get the file back? | written |
| 15 | [`od` reads types, not bytes](od/README.md) | Nothing else is installed. What are the two flags that make `od` honest? | written, 2026-09-07 |
| 16 | [`uni` — the character's name](uni/README.md) | What *is* this character, not just how is it stored? | written |
| 17 | [Typing a character you cannot type](typing_a_character/README.md) | There is no `ż` on my keyboard — how do I produce one? | written, 2026-09-07 |
| 18 | [The five worth installing](worth_installing/README.md) | What do `hexyl`, `uchardet`, `recode`, `dos2unix` and GNU coreutils add? | written |

## The whole toolkit, one row each

If you came looking for *the list* — every command you are likely to run over text, and what each one quietly decided before it printed — this is it. Nothing here needs installing on macOS or Ubuntu.

**A bold tool has a page in this chapter and its last column was measured.** A link that is *not* bold means the tool has no page of its own, so it goes to wherever this library does show it — a lesson in another chapter that runs it, or the page for the tool it is a flag of. And a name with **no link at all** has no page anywhere here: its last column links the *concept* instead, and names the question worth asking rather than a verdict, which is the honest state of the evidence. `rev` and `strings` are the two exceptions, [measured below](#two-of-the-unbolded-rows-measured). The three questions at the top of this page are how you settle one for yourself in about a minute.

### Search and match

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| **[`grep`](grep/README.md)** | search | a character is whatever the **locale** says; invalid bytes are handled two different ways by the two greps, and one of them [drops the line and exits 0](grep/README.md) |
| **[`rg`](ripgrep/README.md)** | search, recursively, fast | never asks the locale; [reads the BOM](ripgrep/README.md) and otherwise searches raw bytes. `--column` counts **bytes** and says so |
| **[`rg -P`](pcre2/README.md)** | the other regex engine | a second Unicode implementation with its own `\p{…}` and its own [silent failure](pcre2/README.md); absent from a Mac entirely |
| **[`find`](find/README.md)** | walk a directory | filenames are **bytes**, and `-name` is a byte comparison — even where [the filesystem disagrees](find/README.md) |
| **[`look`](look_paste_tee_split/README.md)**, [`fgrep`](grep/README.md) | fixed-string search | `fgrep` is `grep -F`; the locale questions are grep's, unchanged. `look` adds one of its own — it binary-searches a file it requires to be **sorted**, misses silently when it is not, and [whose order that is](../07_Real_Data/sorting_and_collation/README.md) is a locale question |

### Slice, reshape, join

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| **[`cut`](cut/README.md)** | slice columns | `-b` is honest; `-c` means characters on one platform and bytes on the other |
| **[`sed`](sed/README.md)** | edit with patterns | a **sequence**, not a byte set — which is why it repairs what `tr` breaks |
| **[`awk`](awk/README.md)** | fields and arithmetic | three implementations, two of them called `awk`, and they do not agree; `substr()` is `cut -c` with no `-b` to escape to |
| [`head`](../07_Real_Data/bom_in_a_csv/README.md), [`tail`](../06_Terminal/trailing_newline/README.md) | first or last part | `-n` counts **newlines** and `-c` counts **bytes**; neither decodes, so neither can fail — but `-c` will cut a character in half |
| **[`paste`](look_paste_tee_split/README.md)**, `join`, `comm` | put files side by side, or match them up | delimiters and field boundaries are bytes — `-d` takes a **list** of them and reads it a byte at a time, so one multi-byte delimiter becomes two; [`join` and `comm`](tr_and_sort/README.md) additionally require both inputs sorted **in the same collation** as they compare, which is [a locale question](../07_Real_Data/sorting_and_collation/README.md) |
| **[`split`, `csplit`](look_paste_tee_split/README.md)** | cut a file into pieces | `split -b` is bytes and will [land mid-character](../07_Real_Data/fixed_width_byte_fields/README.md), so a piece on its own is not text; `-l` is lines and will not |
| `rev` | reverse each line | the **locale** decides whether it reverses characters or bytes — and reversing bytes takes a multi-byte character apart. [Measured below](#two-of-the-unbolded-rows-measured) |
| `fold`, `fmt`, `expand`, `column`, `nl`, `pr` | wrap, align, number, paginate | every one of them has a notion of *width*, and width is the [character-vs-byte question](cut/README.md) wearing a different hat. Ask before trusting a column |

### Transform

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| **[`tr`](tr_and_sort/README.md)** | substitute or delete | **bytes only**, always — which is why [it damages the word next door](tr_and_sort/README.md) |
| [`iconv`](../06_Terminal/iconv/README.md) | change encoding | the only tool here whose *whole job* is the encoding — so it is the one you have to tell, and `-c` [repairs differently on the two platforms](../CONTRIBUTING.md) |
| [`dos2unix`](worth_installing/README.md) | line endings | [CRLF](../07_Real_Data/crlf_vs_lf/README.md) only; it has a report mode that changes nothing, which is the one to run first |
| [`recode`](worth_installing/README.md) | change encoding, bigger table set | **refuses** an untranslatable character and leaves the file intact; `-f` converts and silently deletes it |

### Order, count, compare

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| **[`sort`](tr_and_sort/README.md)** | order lines | the **locale** picks the order, and byte order is not alphabetical order — [three locales, three alphabets](../07_Real_Data/sorting_and_collation/README.md) |
| [`uniq`](tr_and_sort/README.md) | collapse adjacent equals | byte equality, and only *adjacent* — so it inherits whatever order `sort` chose. `-c` [pads its count to different widths per platform](../CONTRIBUTING.md) |
| [`wc`](../06_Terminal/inspecting_a_file/README.md) | count | `-c` bytes, `-m` characters, `-l` [newlines](../06_Terminal/trailing_newline/README.md) — three questions, three answers, and `-m` needs the locale to mean anything |
| **[`diff`, `cmp`](diff_and_cmp/README.md)** | compare | `cmp` compares bytes and reports the first differing byte — in a message that calls it a `char`; `diff` compares lines as bytes, so two files that differ only in [normalization](../04_Python/normalization/README.md) or [line ending](../07_Real_Data/crlf_vs_lf/README.md) differ on **every line** |

### Look at the bytes

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| **[`hexdump`](hexdump/README.md)** | dump | six presets on one format engine; the default reads **16-bit numbers** and swaps your pairs. `-C`'s text column is ASCII and nothing else, which is what makes it safe |
| **[`xxd`](xxd/README.md)** | dump, and undump | honest default, and the only one of the four that goes **backwards** — `xxd -r` reads the hex column, seeks to the offsets, and [ignores the text column entirely](xxd/README.md) |
| **[`od`](od/README.md)** | dump, POSIX | the only one guaranteed present — and its interface is a **C type**, so its default is octal words at octal offsets, `-a` [invents names for bytes it cannot draw](../06_Terminal/inspecting_a_file/README.md), and [no two machines lay its columns out alike](od/README.md) |
| [`file`](../06_Terminal/file_guesses/README.md) | guess what this is | reads the first bytes and guesses; `--mime-encoding` distinguishes valid UTF-8 from not, and little else |
| [`cat -vet`](../06_Terminal/inspecting_a_file/README.md#why-plain-cat-is-not-a-way-to-look-at-a-file) | show the invisibles | ASCII-only respelling: `M-x` for a high byte, `$` for a newline, `^I` for a tab. `cat -A` [does not exist on macOS](../CONTRIBUTING.md) |
| `strings` | pull the text out of a binary | **ASCII by default**, in runs of four or more — so a word containing an accent is split, and a short fragment is dropped entirely. [Measured below](#two-of-the-unbolded-rows-measured) |
| [`hexyl`](worth_installing/README.md) | dump, in colour | colour by byte category, which is the one column no other dump has |
| [`uchardet`](worth_installing/README.md) | guess the *encoding* | a real detector where `file` only tells valid-UTF-8 from not — it narrows the field, it does not settle it |
| **[`uni`](uni/README.md)** | name the character | the character's **name**, and search *by* name — the column no dump tool has |

### Feed other commands

| Tool | Its actual job | Its opinion about your text |
|---|---|---|
| **[`xargs`](xargs/README.md)** | turn a list into a command line | splits on spaces *and* quotes, and batches by **bytes** — so the encoding decides how many times your command runs |
| [`find -exec`](find/README.md), **[`tee`](look_paste_tee_split/README.md)** | run per file, or fork a stream | both pass bytes through untouched — `tee` is this chapter's **control**, the one tool with no opinion at all; `find -exec … +` is the escape from most of [`xargs`'s problems](xargs/README.md) |
| **[`rg --pre`, `rg -z`](decompress_then_decode/README.md)** | one stage before the decode | a container is not an encoding, and [`-z` is a list of binaries, not a capability](decompress_then_decode/README.md) |

### Two of the unbolded rows, measured

The two above that would otherwise be pure assertion, since both surprised the author:

```text title="Measured 2026-09-06 — macOS 26.6, cafe.txt = 'café bar' in UTF-8, 10 bytes. Verbatim; not machine-checked, because no answer key can match both platforms."
$ LC_ALL=C rev cafe.txt | hexdump -C
00000000  72 61 62 20 a9 c3 66 61  63 0a                    |rab ..fac.|
0000000a
$ LC_ALL=en_US.UTF-8 rev cafe.txt | hexdump -C
00000000  72 61 62 20 c3 a9 66 61  63 0a                    |rab ..fac.|
0000000a
$ strings cafe.txt | hexdump -C
00000000  20 62 61 72 0a                                    | bar.|
00000005
```

The first two runs differ in one byte pair: `a9 c3` against `c3 a9`. The C-locale line is no longer UTF-8 at all — the `é` was taken apart and put back the wrong way round — while the text column of both dumps says `rab ..fac.`, which is [exactly the column that cannot tell you](hexdump/README.md). `rev` is the counter-example to this chapter's own advice. Everywhere else, `LC_ALL=C` is the escape hatch — it turns a decoding tool into a byte tool and stops it failing on input it cannot read. For `rev` it is the *cause*: in the C locale there are no characters to reverse, only bytes, and a two-byte `é` comes back as two bytes in the wrong order. `LC_ALL=C` is right for **searching and matching**, where you want no interpretation. It is wrong for anything that **rearranges** what it read.

`strings` is the other shape of the same problem: it is not wrong about the encoding, it never had one. Its default is runs of four or more printable ASCII bytes, so `café` becomes `caf` (three — dropped) plus a byte it will not print. `strings -e S` takes single-byte 8-bit encodings and `-e l` little-endian 16-bit, which is how you get the text out of a UTF-16 file it otherwise reports as empty.

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
