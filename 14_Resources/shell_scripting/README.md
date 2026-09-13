# Shell scripting: the reading list

**Level:** reference · for anyone whose text pipeline is a script

**One line:** The shell is the language most of this library's examples are written in and the only one here with [no string type at all](../../11_Tools/sh/README.md), so the material that teaches it well is the material that teaches it as glue between byte-processing programs — and the two resources that matter most are a wiki and a linter, not books.

Every link on this page was fetched on **2026-09-13** (`GET`, following redirects). Two publishers refuse an automated request with 403 — O'Reilly, as [RESOURCES.md](../../RESOURCES.md) already notes, and gnu.org's manual pages — so their books link to Open Library and their manuals are named rather than linked; both open normally in a browser.

## Start with these three, in this order

| | What it gives you |
|---|---|
| [BashGuide ↗](https://mywiki.wooledge.org/BashGuide) — Maarten Billemont, on Greg Wooledge's wiki | The one tutorial that teaches **quoting first** and everything else after it, which is the right order for a language where an unquoted `$var` is [re-parsed into words and globs](../../11_Tools/sh/README.md) before any command sees it. Read it before any book below. |
| [BashPitfalls ↗](https://mywiki.wooledge.org/BashPitfalls) | Sixty-odd numbered mistakes, each with the wrong line, the right line, and why. Number 1 is `for f in $(ls *.mp3)`, and most of the list is the same mistake — treating a stream of bytes as a list of words — in different clothes. |
| [ShellCheck ↗](https://www.shellcheck.net/) — Vidar Holen | The linter. `brew install shellcheck` or `apt install shellcheck`, then run it on every script you own; every warning links to [a wiki page ↗](https://github.com/koalaman/shellcheck/wiki/Checks) that explains the failure it prevents. It catches the pitfalls above mechanically, and it knows which constructs are bash-only in a `#!/bin/sh` file. |

Then the [BashFAQ ↗](https://mywiki.wooledge.org/BashFAQ), which is the same wiki's answers to the questions people actually ask — *how do I read a file line by line*, *how do I handle filenames with spaces* — and its entry [105 ↗](https://mywiki.wooledge.org/BashFAQ/105), on why `set -e` does not do what you expect, which is the one to read before putting that line at the top of a script.

## Books

### The shell as a language for text

- **[Arnold Robbins & Nelson Beebe, *Classic Shell Scripting* (2005) ↗](https://openlibrary.org/isbn/9780596005955).** The closest match to this library's subject: the whole book is scripts that push text through `grep`, `sed`, `awk`, `sort`, `cut` and `tr`, with a chapter on POSIX portability and a running example that builds a spelling checker out of a pipeline. Written for POSIX `sh` rather than bash, which is why its scripts still run on a Mac's `/bin/sh` and Ubuntu's `dash` alike.
- **[Brian Kernighan & Rob Pike, *The Unix Programming Environment* (1984) ↗](https://openlibrary.org/isbn/9780139376818).** Where the idea comes from: chapters 3 to 5 are the shell, filters, and shell programming, and the argument that a program should read a stream and write a stream is made here first. Every command in it still exists; the only thing that has aged is `ed`.
- **[Dale Dougherty & Tim O'Reilly, *Unix Text Processing* (1987, free) ↗](https://www.oreilly.com/openbook/utp/).** The same idea applied to documents. Listed on [RESOURCES.md](../../RESOURCES.md#text-processing-the-next-subject-along) already; here because it is the book that treats the shell as a text tool and nothing else.
- **[Stephen Kochan & Patrick Wood, *Shell Programming in Unix, Linux and OS X*, 4th ed. (2016) ↗](https://openlibrary.org/isbn/9780134496009).** A textbook for POSIX shell, patient and thorough, and the one to give somebody who has never written a script. Its portability is the point: what it teaches runs under every `sh` on the two platforms this library measures.

### bash specifically

- **[Carl Albing & JP Vossen, *Bash Idioms* (2022) ↗](https://openlibrary.org/isbn/9781492094753).** Short, and the modern one: how to *read* the bash that other people wrote — `${var:-default}`, `[[ ]]` against `[ ]`, `mapfile`, arrays — with a chapter on the idioms that are traps. Read after BashGuide.
- **[Carl Albing & JP Vossen, *bash Cookbook*, 2nd ed. (2017) ↗](https://openlibrary.org/isbn/9781491975336).** The same authors, three hundred recipes. Reference rather than reading; the chapters on input parsing and on "avoiding common mistakes" are the ones that overlap this library.
- **[Cameron Newham, *Learning the bash Shell*, 3rd ed. (2005) ↗](https://openlibrary.org/isbn/9780596009656).** The classic O'Reilly tutorial. Dated in its examples and still correct in its explanations; if BashGuide is too terse, this is the same material told slowly.
- **[Chris Johnson & Jayant Varma, *Pro Bash Programming*, 2nd ed. (2015) ↗](https://openlibrary.org/isbn/9781484201220)** and **[Steve Parker, *Shell Scripting: Expert Recipes* (2011) ↗](https://openlibrary.org/isbn/9781118024485).** Two more of the same shape, listed because both are unusually careful about which constructs are bash and which are POSIX.

### The command line around the script

- **[William Shotts, *The Linux Command Line*, 2nd ed. (2019, free) ↗](https://linuxcommand.org/tlcl.php).** The gentlest start of anything on this page, and free as a PDF from the author. Part 4 is shell scripting; the three parts before it are the tools a script is made of.
- **[Daniel Barrett, *Efficient Linux at the Command Line* (2022) ↗](https://openlibrary.org/isbn/9781098113407).** Not about scripting but about the *pipeline* — building a command out of eleven small ones — which is what most scripts here are before they become scripts.
- **[Jeroen Janssens, *Data Science at the Command Line*, 2nd ed. (2021, free online) ↗](https://datascienceatthecommandline.com/).** Text pipelines over CSV and JSON, with the modern tools (`csvkit`, `jq`, `xsv`) beside the old ones. The book for the reader whose "text" is a data file.
- **[Dave Taylor & Brandon Perry, *Wicked Cool Shell Scripts*, 2nd ed. (2017) ↗](https://nostarch.com/wcss2).** A hundred and one finished scripts to read. Good for seeing what a whole one looks like; do not learn quoting from it.
- **[Brian Hogan, *Small, Sharp Software Tools* (2019) ↗](https://pragprog.com/titles/bhcldev/small-sharp-software-tools/)** and **[Shelley Powers et al., *Unix Power Tools*, 3rd ed. (2002) ↗](https://openlibrary.org/isbn/9780596003302).** One modern and one encyclopaedic tour of the tools themselves.

### sed and awk, which are half of every script

- **[Dale Dougherty & Arnold Robbins, *sed & awk*, 2nd ed. (1997) ↗](https://openlibrary.org/isbn/9781565922259)** and **[Aho, Kernighan & Weinberger, *The AWK Programming Language*, 2nd ed. (2024) ↗](https://awk.dev/)** — both on [RESOURCES.md](../../RESOURCES.md#text-processing-the-next-subject-along) with their reasons. **[Arnold Robbins, *Effective awk Programming*, 4th ed. (2015) ↗](https://openlibrary.org/isbn/9781491904619)** is the third: it is the GNU awk manual in print, and the one that says which of the [three awks](../../11_Tools/awk/README.md) each feature belongs to.
- **[Jeffrey Friedl, *Mastering Regular Expressions*, 3rd ed. (2006) ↗](https://openlibrary.org/isbn/9780596528126).** For the chapter on flavours alone: BRE, ERE and PCRE are three regex dialects, `grep`, `sed` and `awk` speak them in different mixtures, and that chapter is the map. Which is also why a `+` that works in `grep -E` does nothing in `sed` without `-E`.
- **[Bruce Barnett, *The Grymoire*: sed ↗](https://www.grymoire.com/Unix/Sed.html)** and **[sh ↗](https://www.grymoire.com/Unix/Sh.html).** Old, plain-HTML tutorials that explain the hold space and the parsing order better than most books. **[Peteris Krumins, *sed one-liners explained* ↗](https://catonmat.net/sed-one-liners-explained-part-one)** takes the famous one-liner file apart line by line.

## The references you will actually open

| | What it is |
|---|---|
| [POSIX.1-2024, Shell Command Language ↗](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html) | The specification. Section 2.2 is quoting and 2.6 is word expansion, in the order the shell performs them — the two pages that settle every "why did it split there" argument. What it promises is what runs under both `sh`s [this library measures](../../11_Tools/sh/README.md). |
| *GNU Bash Reference Manual* — `info bash`, or the copy on gnu.org | Everything bash adds to the specification above, and `help <builtin>` at the prompt for the same text one command at a time. |
| [explainshell ↗](https://explainshell.com/) | Paste a command line; it splits it into the flags of each program and quotes the man page for each. The fastest way to read a one-liner somebody else wrote. |
| [Rich Felker, *Rich's sh (POSIX shell) tricks* ↗](https://www.etalabs.net/sh_tricks.html) | One page by the author of musl on doing things portably in `sh` that people believe need bash — reading a line, handling arbitrary filenames, `printf` as the only safe `echo`. The portable spellings this library's [`printf` page](../../06_Terminal/printf_writes_bytes/README.md) reaches the same way. |
| [Google Shell Style Guide ↗](https://google.github.io/styleguide/shellguide.html) | A house style with reasons, and one opinion worth taking even if you take no other: a script that grows past a hundred lines should be rewritten in a language with a string type. |
| [Bash Hackers Wiki ↗](https://flokoe.github.io/bash-hackers-wiki/) | The other wiki: parameter expansion, the parser, and the `printf` builtin in more detail than the manual. This is a mirror; the original domain lapsed in 2023. |
| [The Bash Guide ↗](https://guide.bash.academy/) | Billemont's newer, unfinished rewrite of BashGuide. The finished chapters are the best introduction to how bash *parses* a line, which is the thing the pitfalls are made of. |
| [The Art of Command Line ↗](https://github.com/jlevy/the-art-of-command-line) | One long page of idioms, from basics to one-liners, with a section on macOS-only and Windows-only differences. |

## Courses, for somebody starting from nothing

- **[Software Carpentry, *The Unix Shell* ↗](https://swcarpentry.github.io/shell-novice/).** A half-day lesson with data files to practise on, written for scientists who have never opened a terminal. The right first hour.
- **[MIT, *The Missing Semester of Your CS Education* ↗](https://missing.csail.mit.edu/).** Two lectures on the shell and shell scripting, with exercises, and a lecture on the data-wrangling pipelines this library's tools chapter is about.
- **[Raimon Grau, *Shell Field Guide* ↗](https://raimonster.com/scripting-field-guide/).** A short free book of idioms and gotchas, organised as a field guide rather than a course.

## Tools that read your script

| Tool | What it finds |
|---|---|
| [ShellCheck ↗](https://www.shellcheck.net/) | Above. The one to install first. |
| [shfmt ↗](https://github.com/mvdan/sh) — Daniel Martí | A formatter and a parser for POSIX shell and bash; `shfmt -d` diffs your script against a canonical layout, and the parser behind it is what several editors use for shell syntax. |
| [checkbashisms ↗](https://manpages.debian.org/checkbashisms) — Debian devscripts | Reports bash-only constructs in a script that claims `#!/bin/sh`. That claim is not idle: `/bin/sh` is bash 3.2 on a Mac and `dash` on Ubuntu, and [The shell has no string type](../../11_Tools/sh/README.md) measures three things the two answer differently for the same script. |
| `bash -n script` | Parses without running. Catches an unclosed quote; catches nothing about what the quotes mean. |

## Read with care

- **[Mendel Cooper, *Advanced Bash-Scripting Guide* ↗](https://tldp.org/LDP/abs/html/).** The most-linked bash document on the web, and the one BashGuide was written in reaction to: it is encyclopaedic, and its examples teach the exact habits BashPitfalls lists — unquoted expansions, parsing `ls`, `echo` where `printf` was needed. Use it as an index of what exists, never as a model of how to write it.
- **Any list of "useful one-liners".** They assume GNU tools almost without exception, and the forty-three platform differences [CONTRIBUTING.md](../../CONTRIBUTING.md) has collected are the ways those one-liners fail on a Mac — `sed -i` without a suffix, `xargs -a`, `base64 -w`, `split -C`. Run each through the tool's page in [11_Tools](../../11_Tools/README.md) before trusting it on both platforms.

## Where this library already covers it

The shell's own behaviour with text is a lesson here rather than a resource, and the tools a script is made of have a page each:

- [The shell has no string type](../../11_Tools/sh/README.md) — a variable is bytes, `${#var}` is a locale question, and `sh` is two different programs on the two platforms
- [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) — the portable way to produce a byte, and why `echo` is not it
- [The first two bytes](../../06_Terminal/the_first_two_bytes/README.md) — what a BOM or a CR does to `#!`
- [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) — why a script's output differs from what you saw at the prompt
- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — the variable every tool in a pipeline consults separately
- [`xargs` splits on the wrong things](../../11_Tools/xargs/README.md), [`find`, and filenames that are bytes](../../11_Tools/find/README.md), [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md), [`sed` matches patterns, not bytes](../../11_Tools/sed/README.md), [`awk` is three programs](../../11_Tools/awk/README.md), [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) — the tools, one page each, with the encoding decision each makes measured on both platforms

## See also

- [RESOURCES.md](../../RESOURCES.md) — the main reading list, of which this page is the shell shelf
- [11_Tools](../../11_Tools/README.md) — the toolbox those scripts call, and the three questions to ask of any tool in it
- [06_Terminal](../../06_Terminal/README.md) — the tools whose job *is* bytes
