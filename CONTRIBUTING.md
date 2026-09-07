# Conventions

House rules for writing a page here. Readers browsing lessons do not need this file; it is for whoever is about to add one.

## The shape of a lesson

```
02_Characters/
  a_character_is_a_number/
    README.md                              the lesson
    examples/
      a_character_is_a_number_py.py        the Python program
      a_character_is_a_number_py.out       its recorded output
      a_character_is_a_number_rs.rs        the Rust program
      a_character_is_a_number_rs.out
      a_character_is_a_number_sh.sh        the shell script
      a_character_is_a_number_sh.out
      a_character_is_a_number_c.c          (optional) the C view, where one helps
```

One idea per folder. The folder name is the idea, in `lower_snake_case`, and it becomes a permanent URL — so name it for what it teaches, not for where it currently sits in the reading order.

A lesson does not need all three languages. It needs the ones that show something the others cannot: Python for the shortest statement, the shell for the bytes on a real pipe, Rust for the type holding the line. A lesson with one example is fine; a lesson with three that say the same thing is padding.

## The page

Open with the title, then two lines that let a reader decide in five seconds whether this is their page:

```markdown
# Hex is a shorthand

**Level:** 101 · for anyone starting from zero

**One line:** Hexadecimal is not a different kind of number. It is binary written four bits at a time, so one byte is always exactly two hex digits.
```

`**Level:**` is `101` / `201` / `301` / `reference`, then `·`, then who it is for. The one-line summary states the *claim*, not the topic — "hex is bits four at a time" is a one-liner; "an introduction to hexadecimal" is a table-of-contents entry.

Then, in this order: the mechanism in prose, the generated blocks per language (`## In Python`, `## In the terminal`, `## In Rust`), the bridge, `## Try it`, `## Practice` if the page has a kata, `## See also`.

Do not hard-wrap paragraphs. Write each paragraph as one long line and let the editor soft-wrap; Markdown collapses single newlines anyway.

## Output is generated, never typed

Mark the spot and let the tool fill it:

```markdown
<!-- output:a_character_is_a_number_py -->
<!-- /output -->
```

`tools/run_examples.py` runs the program and pastes what it actually printed, with a provenance line above the fence. Inside the markers is generated; outside is yours. The stem is bare — no path, no extension — so stems must be unique repo-wide *across languages*, which is what the `_py` / `_rs` / `_sh` suffix is for. The tool refuses a duplicate.

There is a second kind, `<!-- source:stem -->`, which pastes the program itself. Use it when the code *is* the lesson — a ten-line `xxd` in Python, a shell script whose commands are the content — and a hand-copied fence could silently drift from the file CI runs.

```bash
python3 tools/run_examples.py                 # verify + refill
python3 tools/run_examples.py --update --only X   # record X's output as its answer key
python3 tools/run_examples.py --check         # write nothing, fail on drift (CI)
```

**Always pass `--only` with `--update`.** A bare `--update` re-records every key in the repo, including one somebody else is midway through editing. And read what it recorded before committing: `--update` accepts whatever the program printed, so it will happily enshrine a bug. The recorded key proves the page shows what the program printed; it cannot know the program is right.

**A recorded key cannot hold a carriage return.** The key is read back through Python's universal newlines, so a `\r\n` in the `.out` file arrives as `\n` and is compared against a program's stdout, which was not translated — the two can never match, and the gate reports drift with a diff that looks empty because the difference is invisible. The example most likely to hit it is the one most likely to be written: anything about CRLF. Print the CR through `cat -vet` (`^M$`) or `xxd` instead, which is what the page wants anyway, since the whole reason that byte needs showing is that nothing draws it.

## The programs

**Python: stdlib only.** A reader must be able to run any page with the `python3` already on their machine, and CI has no install step to prove it.

**Rust: bare `rustc --edition 2024`.** No Cargo, no crates. A lesson about something a crate does (`unicode-segmentation`, say) hand-rolls the narrow case in std and says plainly what the crate adds.

**C: `cc -std=c11 -Wall -Wextra`**, no libraries beyond libc, and only on a page where the C view sharpens the point — it is an aside, not a fourth track. `cc` is clang on macOS and gcc on Ubuntu; both compile in CI, so a warning from either is printed as a note and worth fixing.

**Shell: `bash`, and only tools both macOS and Ubuntu ship** — `xxd`, `od`, `hexdump`, `cat`, `file`, `wc`, `printf`, `iconv`, `tr`, `sed`, `grep`, `find`, `sort`, `uniq`, `cut`. On Ubuntu `xxd`, `hexdump` and `file` are separate packages, which the examples workflow installs if the runner image ever stops shipping them. CI runs every example on both, which is the only check that catches a BSD/GNU difference. **Twenty-eight found so far.** The first seven: **`od -a` names bytes above 127 differently on the two platforms, and no layout helper can fix it** — GNU masks the high bit off and names the remainder (`c3` becomes `C`), BSD asks `isprint()` in the current locale and emits the raw byte when the answer is yes, so the row is both platform- and locale-dependent; record `-tx1` and never `-a`, as [Inspecting a file](06_Terminal/inspecting_a_file/README.md) sets out. Then: `od` pads its lines on macOS and not on Linux (pipe through the `tidy` helper the existing scripts define); `printf '\x..'` is bash, not POSIX (so the scripts run under `bash`, and a page that wants portability shows the octal form); **`cat -A` does not exist on macOS** (`cat -vet` is the portable spelling of the same three flags, and its output is identical on both); and `iconv -c` **repairs differently** — on invalid input macOS iconv stops at the first bad byte while GNU iconv skips it and keeps going, so the same command writes two different files. Plain `iconv -f X -t X` used as a yes/no validator agrees on both, exit status and all, which is what [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) records. And `iconv -t UTF-16` **with no `BE` or `LE` picks the byte order itself** — big-endian on macOS, little-endian on GNU — so the same command writes two different files and there is no key that matches both; name the order explicitly (`UTF-16BE` / `UTF-16LE`), as [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) does. And **`tr` does not agree about whether the locale applies at all** — BSD `tr` under a UTF-8 locale uppercases `é` to `É`, GNU `tr` is byte-oriented and has never handled multi-byte characters, so it leaves the same bytes untouched; there is no key that matches both, and [Locale and `LC_CTYPE`](06_Terminal/locale_and_lc_ctype/README.md) states it in a dated table rather than running it.

Four more came out of [11_Tools](11_Tools/README.md) on 2026-09-06 — unsurprising, since that chapter is about the tools whose job is *not* bytes, and those are the ones nobody standardised carefully. The first is the worst failure shape in this repo.

8. **BSD `grep` in a UTF-8 locale DROPS a line it cannot decode, and exits 0.** Three lines, all containing `line`, the middle one holding two invalid bytes: GNU grep 3.11 finds three, BSD grep finds two and says nothing at all about the third — no warning, no diagnostic, no status. GNU gives the same answer in both locales. So never record a `grep` run over invalid bytes, and in prose tell readers to search a file of unknown encoding under `LC_ALL=C`, where grep is a pure byte matcher and skips nothing. Measured on [`grep` on text that is not ASCII](11_Tools/grep/README.md).
9. **The "binary file" notice has two wordings on two different streams** — BSD prints `Binary file f matches` on **stdout**, GNU 3.11 prints `grep: f: binary file matches` on **stderr**. Redirecting a search therefore writes a junk line into the output file on one platform and produces a silently empty file on the other, exit 0 both times. `grep -a` is identical on both and is what an example should use.
10. **`uniq -c` pads its count to different widths**, the same trap as `wc -c`. Strip it (`sed 's/^ *//'`) before recording.
11. **The filesystem, not only the tools.** macOS APFS is *normalization-insensitive*, so creating `żółw` in NFC and again in NFD leaves **one** file where Linux leaves two — and APFS **refuses a filename that is not valid UTF-8** (`Errno 92`), where Linux takes any bytes but `NUL` and `/`. An example that creates filenames may use only one spelling, and cannot test the invalid case at all. Measured on [`find`, and filenames that are bytes](11_Tools/find/README.md).

And a twelfth, from the tool that is otherwise the *most* portable thing in this list:

12. **`hexdump -c` changes notation with the locale on BSD and not on GNU.** Under `LC_ALL=C` both print octal (`303 251` for an `é`); under a UTF-8 locale macOS switches to `M-x` meta notation for the bytes whose low seven bits happen to be printable — `e2` becomes `M-b`, while `82` stays `303`-style octal in the same row — and util-linux keeps printing octal. It is the `od -a` masking trick again, one tool along. Nothing else in `hexdump` differs: the default view, `-C`, `-x`, `-b`, `-o`, `-d` and any `-e` format are byte-identical on both platforms in both locales, down to the trailing spaces on a short last line, because util-linux's hexdump descends directly from the BSD one. So **`hexdump -C` is the dump to record and to paste into a bug report**, and `-c` is the one to leave out. Measured on [`hexdump` is a format engine wearing six presets](11_Tools/hexdump/README.md).

**And one that is not a BSD/GNU split but costs the same.** `xxd` is a single implementation — it ships with vim, so both runners are executing the same program — and it still produced two different answers on 2026-09-07: **`xxd -e` pads its short final group by one space more in xxd 2023-10-25 (`ubuntu:24.04`) than in 2025-11-26 (macOS)**. Every other flag in [`xxd` is the dump you can put back](11_Tools/xxd/README.md) is byte-identical on both. Nothing about the platform predicts this; the *version* does, and neither `python3` nor `rustc` nor the vim on a runner is pinned here. So the rule that already applies to anything read out of the Unicode table applies to tool output too: **if a column's width is the only thing carrying your claim, it is not a claim an answer key can hold.** Put it in a dated fence naming both versions, as that page does.

13. **`printf '\u20ac'` gives three different answers on three configurations, and only one of them is a euro sign.** The escape that names a *code point* is the least portable thing in this list, because it depends on the bash version AND the locale: bash 5.2 under `C.UTF-8` writes `e2 82 ac`; bash 5.2 under `LC_ALL=C` cannot represent the character and hands the escape back with the hex **uppercased** (`\u20AC`); and macOS still ships bash 3.2, which predates `printf`'s `\u` entirely and hands it back untouched (`\u20ac`). Six bytes either way and not the same six, so there is no key that matches both runners — record the *shape* (six bytes, not three) and put the bytes in a dated table. `\xHH` and `\NNN` name bytes, ask nothing of the locale, and are identical everywhere. Measured on [Writing a code point](02_Characters/writing_a_code_point/README.md).

14. **`base64` disagrees with itself in five places, and one of them is silent.** The BSD build wraps nothing by default and the GNU build wraps at 76, so `base64 file > out` writes a *different file* on the two platforms; the flag that sets the width is `-b` on macOS and `-w` on GNU; `-D` decodes on macOS and is an error on GNU; and `-i` means **input file** on macOS and **ignore garbage** on GNU — the same letter, two unrelated jobs, neither of which errors. The silent one is the last: given a payload with a space in the middle, macOS decodes straight through and exits 0 while GNU emits partial output, says `invalid input` and exits 1. Newlines inside a payload are accepted by both (MIME wrapped at 76, so every decoder skips them) and a short payload encodes identically, which is the only part an example may record. Measured on [Binary to text](03_Encodings/binary_to_text/README.md).

15. **`xargs -a filelist` is a GNU extension, and BSD `xargs` rejects it outright** — `xargs: invalid option -- a`, exit 1, so a sweep written with it runs nothing on a Mac. The portable spelling is the redirect, `xargs < filelist cmd`, which both accept. Worth knowing beside it, because they fail the same way: `grep -l PAT $(cat filelist)` puts every path in **argv** and blows past `ARG_MAX` somewhere in the low tens of thousands of files, at which point the shell fails the command before `grep` starts — no matches and nothing that reads as an error. Build the list, then pipe it through `xargs`. Measured on [The encoding man pages nobody opens](13_Documentation/the_encoding_man_pages/README.md).

16. **`errno` after a failed `strtol` belongs to the C library, not to the standard — and it is the first on this list that lives in a C library function rather than a command-line tool or the filesystem.** On a string it cannot convert at all (`"zz"`, `""`), macOS sets `errno` to `EINVAL` and glibc leaves it at `0`; both are conforming, because C leaves errno implementation-defined when no conversion is performed. `ERANGE` on overflow **is** promised and both agree, so that one may be recorded. The portable test for *nothing was converted* is the pointer — `endptr == input` — and a C example may print that comparison and must never print `errno` or `strerror` for the no-conversion case (the message text differs too: *Result too large* against *Numerical result out of range*). Same genre as the CPython error wording that came off a key on 2026-09-06. Measured on [Hex: a number, or a picture of bytes](01_Bits_and_Bytes/hex_number_or_bytes/README.md).

17. **`diff`'s "binary" verdict reaches the whole file on BSD and the first block on GNU.** Both call a file binary when they meet a NUL byte, and print `Binary files a and b differ` instead of the change — but a NUL 200 kB into an otherwise textual file makes macOS say exactly that while GNU prints an ordinary line diff; the boundary measured between 4 KB and 8 KB on diffutils 3.10. One log file with a stray NUL near the end therefore gets two different reports, both exit 1, neither of them wrong. An example may only put its NUL near the front, where the two agree. Measured on [`diff` compares lines, `cmp` compares bytes](11_Tools/diff_and_cmp/README.md).

18. **`cmp`'s two diagnostics differ and its main line does not.** `cmp -l` pads the offset column to a fixed width on BSD and not at all on GNU — the `wc -c` / `uniq -c` trap one tool along, so strip it with `sed 's/^ *//'` before recording — and the early-EOF notice is `cmp: EOF on f` on BSD against `cmp: EOF on f after byte 3` on GNU. Both of those go to **stderr**, which is why only the padding can reach a key at all. What is byte-identical on both, and so recordable: the `f g differ: char 4, line 1` line — the word `char` is POSIX's own format string and both print it while counting **bytes** — the two octal value columns of `-l`, and every exit status. Measured on the same page.

Three more came out of [`od` reads types, not bytes](11_Tools/od/README.md) on 2026-09-07 — all inside `od`'s own flags, which is unsurprising for the tool whose padding was already number two on this list.

19. **The offset column is a different WIDTH under `-A x`.** BSD prints seven hex digits, GNU six; under `-A d` and `-A o` they agree at seven. So the radix you most want for an offset is the one where the column moves.
20. **The `z` type suffix is GNU-only.** `od -A x -t x1z` adds a `>text<` column and makes GNU `od` very nearly `hexdump -C`; BSD `od` stops with *"z: unrecognised format character"*. A script using it does not run on a Mac.
21. **`-t f` formats the same float differently.** BSD prints `-2.303804e+02` where GNU prints `-230.38042`, with different precision in the exponent forms too. Same value, and nothing comparing the two as text will agree.

Between those and the padding, an `od` example can only be recorded through a helper that re-spaces its fields — which the `od` page's script does, in a section of its own rather than quietly.

**And two more from [File type is four questions](06_Terminal/file_type_is_four_questions/README.md) on 2026-09-07, and neither is a BSD/GNU split — both are `file(1)` and `cc` being the *same* project at different versions, the genre the `xxd -e` note above already warned about.**

22. **`file`'s English wording is version-dependent; its MIME output is not.** One non-executable file holding `#!/bin/sh`, three builds, two answers: file-5.41 (macOS 26) says `POSIX shell script text executable, ASCII text`, while file-5.44 (Debian 12) and file-5.45 (Ubuntu 24.04) both say `POSIX shell script, ASCII text executable` — the word `executable` moved from one noun to the other upstream between 5.41 and 5.44, so macOS is simply behind rather than different. Checked across the same nine files, **`--mime-type` and `--mime-encoding` were byte-identical on every one**, `inode/x-empty`, `inode/directory` and `inode/fifo` included. So an example may record the MIME forms freely and must never record the default prose; a script that greps the English is depending on a release note. (The rule already had a cousin: `06_Terminal/file_guesses` was written as a stub *because* of this, and had guessed the reason correctly before anyone measured it.)
23. **There is no spelling of the POSIX feature-test macro that gets `mkdtemp` under `-std=c11` on both platforms.** Compiled exactly as this repo compiles C, with no macro, glibc hides `mkdtemp` and gcc warns `implicit declaration`; add `-D_POSIX_C_SOURCE=200809L` and gcc goes clean but **clang now errors**, because macOS gates the same function behind its own `_DARWIN_C_SOURCE` and reads the POSIX macro as a request to *restrict* the namespace. `-D_XOPEN_SOURCE=700` fails the same way round. Two combinations do satisfy both (`_DARWIN_C_SOURCE` + `_POSIX_C_SOURCE`, and `_DEFAULT_SOURCE` + `_POSIX_C_SOURCE`), but the second works on macOS for no reason anyone here could explain, which is not a thing to build an answer key on. **The fix is to not need the function:** `mkdir()` plus `getpid()` and `snprintf()` builds a scratch directory with no feature macro anywhere, and compiles clean on both. Worth knowing generally — everything else that example calls (`fork`, `execve`, `waitpid`, `chdir`, `chmod`, `unlink`, `rmdir`) is exposed by default on both, so `mkdtemp` is the odd one out rather than the start of a pattern.

**And three more, from the four tools nobody documents** — [`split`, `paste`, `look` and `tee`](11_Tools/look_paste_tee_split/README.md), measured 2026-09-07. All three are BSD/GNU splits, which is what the count above went up by.

24. **`paste -d` is multi-byte aware on BSD in a UTF-8 locale and has never been on GNU.** `-d` takes a *list* of delimiters and cycles through it, and GNU reads that list a byte at a time in every locale, so `paste -d 'é' a b c` puts `c3` after the first column and `a9` after the second — in `LC_ALL=C` **and** in `C.UTF-8`. BSD does the same under `LC_ALL=C` and treats `é` as one delimiter under a UTF-8 locale. Exactly the `tr` split one tool along, with the same conclusion: the C-locale answer is the one both give, so record that, and tell readers to use a single-byte delimiter.

25. **`split`'s useful flags do not overlap, and the one that does rounds the other way.** `-C` — a byte budget cut at a line boundary, the flag that would make `split` safe on text — is **GNU-only**; BSD answers `illegal option`. `-p PATTERN` is **BSD-only**; GNU answers `invalid option` and offers `csplit`, which both ship. And `-n N`, which both accept, divides the remainder to opposite ends: 17 bytes into 2 pieces is 8+9 on BSD and 9+8 on GNU, which on a file with a two-byte character at that offset is the difference between a piece that is still text and one that is not. The portable pair is `-l` and `csplit`.

26. **`look` is not installed on a plain Ubuntu at all**, so no example may call it — `apt-get install bsdextrautils` brings util-linux's. The two implementations also disagree on the case this library cares about: given a file sorted in a *collation* order rather than byte order, BSD `look` reports nothing (exit 1) where util-linux `look` finds the line. They agree on a genuinely unsorted file — nothing found, exit 1, for words that are plainly in it, which is the silent-false-negative shape `grep` already owns.

And a twenty-seventh, which is neither a tool nor a filesystem but a **shell's exit status** — the first on this list a page could have recorded without running anything that differs.

27. **A failed shebang exits 126 on Apple's `/bin/bash` and 127 nearly everywhere else.** Give a script a CRLF first line, so the interpreter path the kernel reads ends in a CR: `execve` returns `ENOENT` on both platforms, and the shell turns that into a status. Apple's `/bin/bash` says **126** (*found, but not executable*); bash **3.2.57 under Linux** — byte for byte the same version — says **127** (*not found*), as do 4.4.23 and 5.2.37, and so do macOS's own `zsh` 5.9, `fish` and `dash`. Not the bash version, then, and not simply the platform: that one build. What *is* identical everywhere is the part worth teaching, and it is the sharper finding anyway — a script whose shebang the kernel never found at all (a BOM in front of it, or no `#!`) exits **`0`**, because the shell catches the `ENOEXEC` and runs the file itself. Record the zeros, derive a word for the nonzero case, and put the numbers in a dated fence. Measured on [The first two bytes](06_Terminal/the_first_two_bytes/README.md).

The shells' error *text* for that same file is worse, and falls under the diagnostics rule above: three shells give three sentences, and bash 5.2 on Ubuntu has dropped the interpreter path from the message entirely — so the `^M`, the one character that explains the failure, is not shown to the reader most likely to meet it.

28. **The two spellings of `sed -i` are mutually exclusive, so there is no in-place edit that runs everywhere except `-i.bak`.** BSD `sed` takes the backup suffix as a **separate argument**; GNU and busybox take it as an **optional attached** one. So bare `sed -i 's/a/b/' f` works on GNU 4.9 and busybox and fails on BSD with exit 1 — its error, `sed: 1: "f.txt`, is the giveaway that it has swallowed the *script* as its suffix and is now parsing the filename as the script — while `sed -i '' 's/a/b/' f` works on BSD and fails on GNU (exit 2) and busybox (exit 1), which read the `''` as the script and the script as a filename. Only `sed -i.bak` runs on all three, and it leaves a `.bak` on all three. Measured on BSD sed (Darwin 25.6), GNU sed 4.9 (ubuntu:24.04) and busybox sed (alpine:3.20). **What makes this one worth knowing rather than just avoiding is that it fails loudly:** both wrong spellings exit nonzero *and leave the file byte-for-byte unchanged* — no half-edit, no truncation. On a list where the recurring shape is a silent wrong answer, this is the counter-example, and it is why a build script that checks its exit status is safe here in a way it is not with `grep` or `base64`. (Found by the crlf_vs_lf session; reproduced here on all three implementations before recording.)

**A note on the count, because the next person to find a composite will reason their way to inflating it.** The number claims *distinct measured splits*, so a finding that is two existing rules composed does not earn a new one — it earns a cross-reference. The case that set this: the shebang error message differs across shells *and* drops the interpreter path in bash 5.2, which is finding 27 plus the diagnostics rule above, and adding it as a 28th would have made the count mean less rather than more.

**Deterministic.** No clocks, no randomness, no network, no reading the filesystem. Every example runs under a fixed environment (`LC_ALL=C`, `PYTHONUTF8=1`) so the key does not depend on who ran it; a lesson whose subject *is* the locale sets its own inside the script, on purpose and in view. **And nothing read out of the Unicode table may become a key.** Neither `python3` nor `rustc` is pinned here, and both runners upgrade on their own schedule — on the machine this rule was written, `python3` was answering from Unicode 16.0 and `rustc` from 17.0, in the same repository. A *name* is safe (Unicode guarantees it never changes) and arithmetic over the number line is safe; a count of assigned code points, or whether some recent character is assigned at all, is a fact about the runner and will break on one of the two. [The table has a version](02_Characters/the_table_has_a_version/README.md) works through which is which, and its two programs are written to print questions where the answer would have been a version.

**Prose inside an example is not checked by anything, and it is where wrong claims hide.** The answer key proves the program printed what the page shows; it cannot know whether a *sentence* the program prints is true. So an explanatory line in a `print` needs the same evidence as a number, and it is the easiest place in the repo to assert something plausible and unverified. **Four instances on 2026-09-07, across two pages and two sessions**, and they take three different shapes — which is why this is a rule rather than a checklist item about one mistake.

- **Inverted.** The trailing-newline Rust example asserted stdout "is line-buffered when it is a terminal": Rust wraps stdout in a `LineWriter` *unconditionally*, and it is C and Python that switch to block buffering off a tty. The claim named the right subject and got the direction backwards.
- **Overclaimed.** The CRLF example inherited the convention from "every protocol written in the 1980s" — `every` is unearnable, and HTTP, which the same page names in the same breath, is a decade later.
- **Self-contradictory, inside one key.** The same CRLF Python example said bytes are what you get from "a socket, a zipfile, a subprocess with `text=False`, and a database column", while **section 6 of that same program** correctly said those paths translate nothing. A `TEXT` column hands you `str` (sqlite3, measured); the other three do hand you `bytes`. So the accurate sentence sat eighty lines below the wrong one, in one recorded key, both inside the same fence and both looking equally verified.
- **Survived by luck.** The first-two-bytes example asserted what `file(1)` calls its four scripts. True — and it survived the file-5.41/5.45 wording split *only because it counted rather than quoting*. One notch more specific and it would have been a red CI run.

That third shape is the argument in miniature: **the numbers in a generated block are evidence and the prose beside them is assertion, and they sit inside the same fence looking identical.** All four had been read many times.

**And the audit is worth running even when nothing is false**, because it finds a second thing: a claim that is *correct but inferred*, standing in for evidence that was one command away. The file-type page argued that `file(1)` runs its test classes in order and stops at the first hit — reasoning backwards from the answers, since an empty file reports `inode/x-empty`. True, and `strace` settles it outright and more strongly than the inference could: on an empty file `file` issues `newfstatat` and **no `openat` at all**, so stage two does not lose the race, it never runs (measured on ubuntu:24.04, and the same trace shows the `openat` appearing for a non-empty file). A false sentence is the worse defect; an unevidenced one is the commoner, and the same pass over your own printed prose is what turns up either. When a claim in a print statement is doing teaching work, measure it, and if the measurement is platform- or version-dependent put it in a dated fence on the page rather than in the key.

**And an interpreter's diagnostic TEXT is not a property of your data.** Same rule as the paragraph above, one layer out, and it broke CI twice on 2026-09-06/07. `os.stat('a\x00b')` raises ValueError with two different sentences on macOS and Linux; `bytes.fromhex('123')` raises ValueError with two different sentences on CPython 3.13 and 3.14. The second is the instructive one, because it is a **version** split rather than a platform split — running the example on both runners would not have caught it if the two happened to ship the same Python. So print the exception **class**, and say in the program's own words why the call refused; if the wording is the point, put it on the page in a dated fence naming the builds it came from.

**Written to be read aloud.** Numbered sections, aligned columns, prose in the print statements. A reader should understand the output without the page and the page without the output.

**A snippet in the prose puts its output in a trailing comment**, on the line that prints it, so the whole thing survives a copy-paste into a file:

```python
format(65, '08b')   # '01000001'
```

**Never open a page with code that does not run.** The first block on a page is the one that gets pasted. Lead with the working thing; put a refusal or an error further down, as a comment inside a valid snippet or as a `text` fence nobody can paste into a program by accident.

## Bridges

Every lesson has a section **If you are coming from Python or ABAP**. Those are the two languages this library's reader already thinks in, and a bridge to a language you already speak is the fastest teaching on the page — take the words it needs. Say what transfers *and* what the new language enforces that the old one left to habit; a bridge that hides a real difference costs more than it saves.

The ABAP half is prose. CI cannot run ABAP, so every page says so in the bridge: *(Not machine-checked — CI cannot run ABAP.)* Keep ABAP claims to things you would bet on — type widths, `xstring` vs `string`, the `cl_abap_codepage` and `cl_abap_char_utilities` names — and never quote an SAP code-page number without saying it should be verified against the system.

## Try it, and Practice

**`## Try it` closes a lesson.** Three to five numbered prompts, each one something the reader runs against *their own* files — the CSV that came out wrong, the filename `find` cannot see, a script they already have. 68 of the library's 71 finished lesson pages end with one; the three that do not are a survey ([`worth_installing`](11_Tools/worth_installing/README.md)), a resource page ([`anki`](14_Resources/anki/README.md)), and a page that is already an exercise end to end ([`tribit`](08_Build_Your_Own/tribit/README.md)). Treat it as required unless your page is one of those shapes.

**`## Practice` is optional, and it is a different thing.** It holds a **kata**: predict the answer, then run it, then check. It goes after `## Try it` and before `## See also`.

The test for which section a prompt belongs in is whether **you can print the answer**:

- *"Run `file` on the worst CSV you have, then `head -c 3 | xxd`"* has no answer — the answer is on the reader's disk. `## Try it`.
- *"Write down the hex of these six writes before you run any of them"* has exactly one answer, and it is the same on every machine. `## Practice`.

Both failure modes are quiet. A kata with no checkable answer is a chore the reader abandons; a *Try it* with an answer printed under it is a claim about a file nobody here has seen.

**Fold the answer, and put `markdown="1"` on the tag:**

```markdown
<details markdown="1">
<summary><strong>Answers</strong></summary>

**The six writes.** `68 65 6c 6c 6f` is `hello` …

</details>
```

That attribute is load-bearing and its absence is invisible from the author's chair. `md_in_html` is enabled, so **without** `markdown="1"` the body ships as literal Markdown — asterisks and backticks drawn on the published page — while GitHub renders the same block correctly either way and `mkdocs build --strict` passes, because it is not a link error. Measured 2026-09-07: the library's first kata shipped exactly like that, and the only surface showing the bug was the site. Do not reach for a `???` Material admonition instead; that one prints as literal text on GitHub, which is the mirror of the same problem.

**An answer has to have been run**, like every other claim here. Where it is a program's output, prefer a generated block over typing it — an `examples/<stem>_kata_sh.sh` beside the lesson's own example, pasted in with `<!-- output: -->` — so a solution cannot rot into one that no longer prints what the page says. The sibling [Rust library ↗](https://github.com/masiarek/rust-learning-library) requires this and gates it with a `check_katas.py`; here there is **one kata, no index and no gate**, so nothing checks that a folded answer is true. Until one of those exists, the discipline is yours, and the honest move on a kata whose answer you typed is to run it once more before you commit.

**A kata lives on the page for the topic it teaches**, never in a folder of its own and never with a number in its heading. Folders are permanent URLs and a sequence is the thing that gets reordered — the same reasoning as [Nav order](#nav-order) below. If this library ever collects enough of them to need a reading sequence, it goes in a `KATAS.md` table, which costs nothing to reshuffle; at one kata it would be a file with a row in it.

**A stub gets neither section.** It has no example behind it, so a *Try it* would point at nothing and a folded answer would be a guess with a disclosure triangle over it.

## The cast

**Demonstrate with a character from [CAST.md](CAST.md).** Nine characters, seven invisibles and six strings, each earning its place by a property no other member has — `é` for mojibake, `ż` for what a Latin-1 table cannot hold, `€` for Windows-1252, `😀` for the BMP boundary, `ß` for case mapping that changes length, `café` against `café` for normalization.

The reason is compounding rather than tidiness: a reader who has already met `é` knows it is `C3 A9`, one byte in Latin-1, and `Ã©` when the two are confused, so your page can spend its words on its own subject. When the measurement was taken, 90 of the library's 156 distinct non-ASCII characters appeared once or twice in the whole repo — that tail is what the cast replaces.

If no cast member has the property your page needs, use what you need, say in a line why, and add a row to CAST.md if it will be wanted again. Its byte columns are generated from a program, so a new row goes in that program too.

**A string you call *decomposed* has to be decomposed** — machine-checked (`python3 tools/check_decomposed_literals.py`). `café` and `café` are the same picture, so nothing but a program can tell them apart, and the odds run one way: **you cannot type a decomposed string**. Keyboard, editor and clipboard all hand you the composed spelling, so a hand-written "decomposed" example is composed unless somebody deliberately pasted the mark. When the check was written, all three of the library's hand-authored decomposed literals were composed, each sitting under counts (6 bytes, 5 code points) its own string does not produce. Paste the real spelling — `python3 -c "import unicodedata as u; print(u.normalize('NFD', 'café'))"` — or write the mark out (`U+0301`, `\u{301}`, `65 cc 81`), which is the better answer inside a fence where a bare mark is invisible to the author too. Generated blocks are exempt: their numbers come from the program that printed them.

## Stubs

A **stub** is a lesson page with no example behind it yet: an H1, a `**Level:**`, the notice, a `**One line:**`, and the questions the finished page has to answer. It exists so the plan has a shape and every page has its permanent URL before the prose does. Every stub carries this notice directly under its `**Level:**` line:

```markdown
> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.
```

A stub must not have an `<!-- output: -->` block — there is nothing to fill it from. It graduates by gaining an `examples/` program and losing the notice; update its row in the chapter README and in [ROADMAP.md](ROADMAP.md) when it does.

## Links

- Link a folder by naming its `README.md` — `[label](some_folder/README.md)`, never `[label](some_folder/)`.
- A repo path in backticks should be a link, not bare code text: backticks in the label, a real relative path in the href.
- **A link that leaves the library ends its label with ` ↗`**; an internal link never does. `python3 tools/check_link_style.py --fix` adds and removes them; CI runs it without `--fix`.
- **A passing `link style` does not mean your links resolve.** `check_link_style.py` checks the ` ↗` convention and the shapes above; it is `mkdocs --strict` that fails on a link whose *target does not exist*. Measured 2026-09-07: a `[label](./this_file_does_not_exist.md)` planted in a page passes `link style` and fails `mkdocs --strict` with *"the target … is not found among documentation files"*. Two different checks over the same syntax, and the one that answers "is this link real" is the slow one at the end — so a green `link style` on its own is not a reason to skip the full run.
- Where the sibling Rust library already teaches something — `u8`, hexadecimal, `char`, the anatomy of a `String` — link to it and do not repeat it. Its pages publish at `https://masiarek.github.io/rust-learning-library/<folder>/index.html`; a folder README is `index.html`, never `README.html`.

## Nav order

Sidebar reading order lives in `NAV_ORDER` in `mkdocs_hooks.py`, keyed by folder path. **Never set order by renaming files to `01_`, `02_`** — a filename is a permanent URL. Unlisted pages sort alphabetically at the bottom, so adding a page needs no edit there; a new chapter does.

**Reading order has two renderings, and only one of them is the sidebar.** The other is the prev/next arrows at the foot of every page, and they are computed at a different time: MkDocs sets `previous_page` / `next_page` inside `get_navigation()`, which runs **before** any hook, so a hook that only sorts `nav.items` fixes the sidebar and leaves the arrows in MkDocs' default alphabetical order. That is what happened here — for 13 chapters the published `11_Tools` page offered *"awk"* as the page after it while the sidebar said *"grep"* — and nothing caught it, because each half is internally consistent and the two are only comparable side by side. `on_nav` now re-chains the arrows after sorting, and `tools/check_nav_chain.py` asserts the two agree — forward, backward, and in `nav.pages` — walking the nav itself rather than reusing the hook's helper. If you change `on_nav`, run that gate; it fails loudly when the re-chain goes missing, and `--selftest` proves it still bites.

The same gate checks that `NAV_ORDER` and `LABEL_OVERRIDES` **name things that exist**, because a name the hook cannot match is a silent no-op: the page drops to the alphabetical tail and nothing is printed. That fires two ways. A rename left the entry behind — update it. Or the entry is simply **ahead of its page**, which in a shared checkout is the common one: `git add mkdocs_hooks.py` takes whatever a colleague has left in the file, including a row for a folder they have not committed yet. Commit the row and its folder together. Note that `mkdocs build --strict` passes in that state — a stale nav name is not a broken link — so this gate is the only thing that catches it.

## If someone else is working here too

**Give each concurrent worker its own worktree.** Everything in the next two sections is a *mitigation* for sharing one; a worktree is the prevention, and it is one command:

```bash
git worktree add -b <topic> /tmp/wt-<topic> origin/master
```

A shared checkout means one working tree, one index and one `HEAD`, and its failures are quiet rather than loud. Observed here on 2026-09-07, with three workers in this repo for an afternoon: a whole lesson directory deleted from the tree with the deletion unstaged; a committed paragraph reverted inside a file that still read correctly, visible only as `0 2` in `git diff --numstat`; a push that carried another worker's commit; and a false green in a gate written that same day to catch exactly this. **None of them was caught by a gate** — each was caught by somebody re-running a claim. The gates check what the code does; nothing checks what a shared tree did to your files while you were not looking.

**And it repairs a gate mode rather than only avoiding damage.** A worktree has its **own index** — `.git/worktrees/<name>/index`, not `.git/index` — so a colleague's `git add` cannot enter your staged tree. Verified 2026-09-07: staging a file inside a worktree leaves the main checkout's `git diff --cached` empty, and the two `git write-tree` hashes differ. That removes the whole hazard behind `--staged`, whose only footgun in a shared checkout is that the index it writes out is everyone's. From a worktree the index holds nothing but your work, so `--staged` is simply the right tool for *"what will my next commit contain"* again.

What a worktree does *not* fix, so read the rest of this file anyway: the shared **index files** — `CONTRIBUTING.md`, `ROADMAP.md`, `mkdocs_hooks.py`, a chapter `README.md` — still collide. But from a worktree they collide as a **merge conflict git shows you**, rather than as an edit made against a stale copy that silently drops someone's committed rows. Land the work with a rebase onto `origin/master`, and remove the worktree when you are done.

## Before you commit

```bash
python3 tools/check_all.py              # every gate, in CI's order
python3 tools/check_all.py --staged     # the tree your next commit would make
python3 tools/check_all.py --committed  # the same, against what CI will check out
```

That runs the five commands CI runs — `run_examples.py --check`, `check_link_style.py`, `check_decomposed_literals.py` (with its `--selftest` first), `check_nav_chain.py`, and `uv run --group docs mkdocs build --strict` — and you can still run any of them alone. `--strict` fails on a broken internal link, which is the failure most likely to reach the published site unnoticed. The examples job also runs on macOS in CI; a shell example that passes here and fails there is a BSD/GNU difference, not a flake.

**Two reasons to use the runner rather than the five commands.**

The first is that these gates print a line per example, so the natural way to run one by hand is to pipe it — and **a pipeline's exit status is the last command's**, so `run_examples.py --check | tail -1` reports success no matter what the gate said. A red gate then scrolls past under a green-looking summary line. `set -o pipefail` fixes it — in bash and in zsh — if you remember it every time. What does **not** fix it is the idiom most people reach for next: `${PIPESTATUS[0]}` is bash's spelling, and under zsh it expands to the empty string rather than erroring, so `echo "exit=${PIPESTATUS[0]}"` prints `exit=` and reads like a stumble instead of a wrong answer (zsh's own array is lowercase and 1-indexed, `${pipestatus[1]}`). That is the same failure one level down, so prefer `set -o pipefail` or a plain redirect over any array lookup — and `check_all.py` does not pipe at all: it keeps each status and prints a failing gate's output only when there is one.

The second is `--committed`, which extracts `git archive HEAD` into a temporary directory and runs the gates there. That is what CI checks out, and it differs from your working directory in **both** directions. An untracked file makes your tree red where CI is green — somebody else's half-built lesson in a shared checkout does this constantly. And an untracked file that a *committed* page links to makes CI red where your tree is green, because `--strict` resolves the link against a tree where the target exists. Only the second one reddens the build for everybody, and only `--committed` can see it coming.

And `--staged`, which is the one to run in the *minute before* you commit. `--committed` archives HEAD, so it cannot see the index at all — it is green and says nothing about the commit you are about to make. `--staged` writes the index out with `git write-tree` (which reads the index and moves no ref, so it is safe while others are working) and gates that tree. In a checkout several sessions share, that gap is where the damage happens: `git add` on a shared file takes a colleague's in-flight lines with it, and the resulting tree can fail a gate that both your working directory and HEAD pass. Observed twice on 2026-09-07 — once against the author of the gate that caught it.

And `--mine`, which is the only mode that isolates **your uncommitted work** while somebody else is mid-edit:

```bash
python3 tools/check_all.py --mine 06_Terminal/my_lesson CONTRIBUTING.md
```

It extracts HEAD and copies in only the paths you name, so what it gates is HEAD plus your work and nothing else. Each of the other three is green or red for reasons that need not be yours: the bare working-tree run reads colleagues' unstaged edits, `--staged` writes out the **shared index** so their `git add` enters your verdict, and `--committed` cannot see uncommitted work at all. **You must name the paths**, and that is deliberate — inferring them from `git status` reproduces the very bug the mode exists to dodge, since on 2026-09-07 a half-applied rename left one session's tree showing six deletions and an addition that belonged to *another* session. A named path that is gone from your tree is treated as a deletion and removed, because deleting a file is work too.

The division of labour between the four: **`--mine` before you commit**, **`--committed` after you commit**, the bare run when you are the only session working — and `--staged` only in the narrow case below.

**`--staged`'s condition is not about your working tree, and an earlier version of this paragraph got that wrong.** The hazard is a *colleague's* `git add`, so your own tree's cleanliness is beside the point. Measured in a scratch repo: with a peer's `peer.txt` staged and my `mine.txt` dirty but unstaged, `git write-tree` produced a tree containing **their** staged content and **not** my dirty file. The testable condition is therefore one command about the index, not a feeling about your directory:

```bash
git diff --cached --name-only     # must list only your own paths
```

And even then it describes a commit you are probably not making. **`git commit -- <paths>` builds a *temporary* index**, so a pathspec commit — the house habit here, precisely because the checkout is shared — ignores whatever else is staged. Same scratch repo: the pathspec commit contained my file and left the peer's staged work uncommitted, while `--staged` had just gated a tree containing it. So `--staged` answers exactly one question, and it is narrower than "it sees the index": *you are about to run a bare `git commit` or `git commit -a`, and this is what that will contain.* Any other time, `--mine`.

`python3 tools/check_all.py --selftest` proves the runner still reports a failure, in the same spirit as `check_decomposed_literals.py --selftest` — and then proves `--mine` assembles the right tree, by building a scratch repo in which a colleague has edited *and staged* a file you did not name, and asserting that their bytes do not reach the gated tree. That second half is the one that distinguishes `--mine` from the modes that already existed, so it is the one that had to be tested.

## Before you push

**`git push origin master` resolves the branch at PUSH time, not at commit time.** In a checkout several sessions commit into, that is a time-of-check/time-of-use race: a colleague committing in the window between your `git commit` and your `git push` moves the local `master` your push is about to read, so you send their commit along with yours — a commit you have not read and whose gates you have not run. `HEAD:master` has exactly the same problem, and so does a guard, because a guard checks a state the push then re-reads.

Observed 2026-09-07, and the guard is the instructive part. A session committed `d511962`, guarded the push with `[ "$(git rev-parse origin/master)" = "$(git rev-parse HEAD~1)" ]` — which passed, correctly, for the commit it had just made — and then ran `git push origin HEAD:master`. Another session committed `186de1f` onto the shared `master` eight seconds **later** — after the guard had run and before the push did. Both went. The direction matters, because it is the only one the story can have: `186de1f`'s parent *is* `d511962`, and had it landed first the guard would have compared `origin/master` against it and failed. The window a guard cannot cover is the one **after** it. The push output read `73b3ceb..186de1f`, naming a SHA that session had never seen, and the two commits then had to be disentangled across three sessions' messages because the shipped work looked like the pusher's.

**Push the literal commit you verified:**

```bash
sha=$(git rev-parse HEAD); git push origin "$sha:master"
```

That refspec names one commit rather than a branch to be re-read, so nothing made after it can ride along. Verified: pushing an *older* SHA is rejected as `non-fast-forward` rather than quietly sending whatever `master` now points at, which is the proof the refspec is not resolved a second time.

**And it is self-verifying, which is the other half of the `-q` rule.** The literal form echoes your own SHA back on the left of the arrow, where the branch form can only ever say `master`:

```text
git push origin "$sha:master"   b3bf422..a7a9ab3  a7a9ab39e589355f85ee2d07a68af3d0c1e0a036 -> master
git push origin master          b3bf422..a7a9ab3  master -> master
```

So the SHA you typed is the SHA it prints, and a mismatch needs no comparison by hand. `master -> master` cannot tell you what it sent under any circumstances, which is why `-q` costs more with the branch form than with the refspec.

**Getting it wrong fails safe.** "Push a specific SHA" sounds like the dangerous option and is the opposite: if a colleague landed first, the literal push is **rejected** as `non-fast-forward` rather than rewinding their work. The failure mode is a refusal, not a loss.

**A rejection is normal here, so do the three steps as one command.** With several sessions committing, `origin/master` moves between your `git fetch` and your `git push` often enough that a rejection is routine rather than exceptional — observed twice in a row on 2026-09-07, once in the seconds between rebasing and pushing. Rebase and retry; the window is what you are shrinking:

```bash
git fetch --quiet && git rebase --quiet origin/master && git push origin "$(git rev-parse HEAD):master"
```

**And confirm it landed before you clean anything up.** The mistake that produced this paragraph: a worktree removed and its branch deleted after a rejection, on the assumption the push had gone — which orphaned the commit until it was recovered by SHA from the object database. Removing a worktree deletes the only checkout of that work, and `git branch -D` deletes the only ref to it. Confirm first:

```bash
git fetch --quiet
git merge-base --is-ancestor "$sha" origin/master; echo "landed=$?"   # 0 = yes, 1 = no
```

**Fetch first, and compare against `origin/master`, not against `git ls-remote`.** That check has *three* exit codes and only two of them are answers: `0` landed, `1` not landed, and **`128` could not tell you** — `fatal: Not a valid commit name` — which is what you get when the remote tip is an object you have not fetched. In this repo that is the *likely* case, because a colleague has usually pushed since. A naive `if ! git merge-base …` reads 128 as "not landed" — **a check that errored and a check that answered *no* look identical**, which is finding 15's shape (`grep -l PAT $(cat filelist)` past `ARG_MAX`: "no matches and nothing that reads as an error") in a different tool. Fetching first makes `origin/master` a local ref, and 128 cannot arise. The general form is worth carrying: **when a check can fail to run, test its status against the specific code that means *no*, never against empty output or a bare `if !`.**

**What a refspec cannot do is separate an ANCESTOR**, and the line above is deliberately narrow — *nothing made after it* can ride along, not *nothing at all*. If a colleague committed **before** you and you committed on top, their commit is in your history by definition and no refspec on earth excludes it. That case is not hypothetical and not rare: it was live while this very paragraph was being written, with `a7a9ab3` sitting committed-but-unpushed on the shared `master`, so any commit made on top of it could only ship by shipping it too. It then resolved on its own, because that commit's author pushed first — which is the ordinary outcome and the reason the ancestor case is so easy to never notice. Had they been a minute slower it would have travelled under someone else's push, exactly as `186de1f` did. So the closing line below is not a backstop for this section, it is the **only** check that covers the ancestor case at all — read what you are about to carry, and gate what actually landed.

**Reconstructing one of these afterwards: use parentage, not the clock.** `git rev-parse <sha>^` is the only authoritative answer to which of two commits landed first — `186de1f`'s parent being `d511962` is what settled the case above. If you do reach for a timestamp, ask for the **committer** date (`%cd`): `git log --date=…` prints the **author** date (`%ad`) by default, and that is the one that moves under `--amend` and rebase. Measured here on 2026-09-07: across 60 parent/child pairs there were **zero** committer-date inversions and exactly **one** author-date inversion — a rebased commit showing `author=09:29:52` against `committer=09:31:50`. So the clocks in this repo are not scrambled by concurrency, and a reader who goes looking for that will not find it; the single thing that misleads is `%ad` after history editing.

**And do not use `git push -q`.** The ref-update range it suppresses — `73b3ceb..186de1f` — is the only thing that tells you a SHA you did not create just went out under your name. Read it, and if it does not start at the commit you expected, work out what you shipped before doing anything else.

**And `ahead 1` is not evidence that anything is unpushed.** `git status -sb` compares your branch against `refs/remotes/origin/master`, which is a *cache* updated only by `git fetch` — so in a checkout where somebody else may have pushed, "ahead" often means "you have not fetched". Ask the remote instead: `git ls-remote origin master` contacts it and caches nothing, and `git merge-base --is-ancestor <sha> $(git ls-remote origin master | cut -f1)` answers "did my commit really land". Observed 2026-09-07, as a false alarm between two sessions: one warned the other that a commit was sitting unpushed and would ride out under the next person's push, and it had been on origin for several minutes. Same shape as the rest of this section — a number that looked authoritative because the tooling handed it to you.

**And "I fetched" is not evidence that you fetched.** The other half of the same false alarm: the session that raised it *had* run `git fetch` immediately beforehand — as `git fetch --quiet 2>/dev/null`, with the error channel discarded and the exit status never read. A fetch that fails exits **128** and, spelled that way, prints nothing at all, so a stale tracking ref and a fresh one are indistinguishable in the transcript. Never discard `git fetch`'s stderr, or check `$?` if you do. This is the same rule the top of `check_all.py` argues for gates — **a command that fails silently is worse than one that fails loudly, and redirecting its output is how you build the first out of the second.**

Afterwards, `check_all.py --committed` gates whatever actually landed rather than what you meant to send, which is the backstop for all of this.
