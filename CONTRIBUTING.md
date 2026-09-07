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

Then, in this order: the mechanism in prose, the generated blocks per language (`## In Python`, `## In the terminal`, `## In Rust`), the bridge, `## Try it`, `## See also`.

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

## The programs

**Python: stdlib only.** A reader must be able to run any page with the `python3` already on their machine, and CI has no install step to prove it.

**Rust: bare `rustc --edition 2024`.** No Cargo, no crates. A lesson about something a crate does (`unicode-segmentation`, say) hand-rolls the narrow case in std and says plainly what the crate adds.

**C: `cc -std=c11 -Wall -Wextra`**, no libraries beyond libc, and only on a page where the C view sharpens the point — it is an aside, not a fourth track. `cc` is clang on macOS and gcc on Ubuntu; both compile in CI, so a warning from either is printed as a note and worth fixing.

**Shell: `bash`, and only tools both macOS and Ubuntu ship** — `xxd`, `od`, `hexdump`, `cat`, `file`, `wc`, `printf`, `iconv`, `tr`, `sed`, `grep`, `find`, `sort`, `uniq`, `cut`. On Ubuntu `xxd`, `hexdump` and `file` are separate packages, which the examples workflow installs if the runner image ever stops shipping them. CI runs every example on both, which is the only check that catches a BSD/GNU difference. **Sixteen found so far.** The first seven: **`od -a` names bytes above 127 differently on the two platforms, and no layout helper can fix it** — GNU masks the high bit off and names the remainder (`c3` becomes `C`), BSD asks `isprint()` in the current locale and emits the raw byte when the answer is yes, so the row is both platform- and locale-dependent; record `-tx1` and never `-a`, as [Inspecting a file](06_Terminal/inspecting_a_file/README.md) sets out. Then: `od` pads its lines on macOS and not on Linux (pipe through the `tidy` helper the existing scripts define); `printf '\x..'` is bash, not POSIX (so the scripts run under `bash`, and a page that wants portability shows the octal form); **`cat -A` does not exist on macOS** (`cat -vet` is the portable spelling of the same three flags, and its output is identical on both); and `iconv -c` **repairs differently** — on invalid input macOS iconv stops at the first bad byte while GNU iconv skips it and keeps going, so the same command writes two different files. Plain `iconv -f X -t X` used as a yes/no validator agrees on both, exit status and all, which is what [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) records. And `iconv -t UTF-16` **with no `BE` or `LE` picks the byte order itself** — big-endian on macOS, little-endian on GNU — so the same command writes two different files and there is no key that matches both; name the order explicitly (`UTF-16BE` / `UTF-16LE`), as [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) does. And **`tr` does not agree about whether the locale applies at all** — BSD `tr` under a UTF-8 locale uppercases `é` to `É`, GNU `tr` is byte-oriented and has never handled multi-byte characters, so it leaves the same bytes untouched; there is no key that matches both, and [Locale and `LC_CTYPE`](06_Terminal/locale_and_lc_ctype/README.md) states it in a dated table rather than running it.

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

**Deterministic.** No clocks, no randomness, no network, no reading the filesystem. Every example runs under a fixed environment (`LC_ALL=C`, `PYTHONUTF8=1`) so the key does not depend on who ran it; a lesson whose subject *is* the locale sets its own inside the script, on purpose and in view. **And nothing read out of the Unicode table may become a key.** Neither `python3` nor `rustc` is pinned here, and both runners upgrade on their own schedule — on the machine this rule was written, `python3` was answering from Unicode 16.0 and `rustc` from 17.0, in the same repository. A *name* is safe (Unicode guarantees it never changes) and arithmetic over the number line is safe; a count of assigned code points, or whether some recent character is assigned at all, is a fact about the runner and will break on one of the two. [The table has a version](02_Characters/the_table_has_a_version/README.md) works through which is which, and its two programs are written to print questions where the answer would have been a version.

**Written to be read aloud.** Numbered sections, aligned columns, prose in the print statements. A reader should understand the output without the page and the page without the output.

**A snippet in the prose puts its output in a trailing comment**, on the line that prints it, so the whole thing survives a copy-paste into a file:

```python
format(65, '08b')   # '01000001'
```

**Never open a page with code that does not run.** The first block on a page is the one that gets pasted. Lead with the working thing; put a refusal or an error further down, as a comment inside a valid snippet or as a `text` fence nobody can paste into a program by accident.

## Bridges

Every lesson has a section **If you are coming from Python or ABAP**. Those are the two languages this library's reader already thinks in, and a bridge to a language you already speak is the fastest teaching on the page — take the words it needs. Say what transfers *and* what the new language enforces that the old one left to habit; a bridge that hides a real difference costs more than it saves.

The ABAP half is prose. CI cannot run ABAP, so every page says so in the bridge: *(Not machine-checked — CI cannot run ABAP.)* Keep ABAP claims to things you would bet on — type widths, `xstring` vs `string`, the `cl_abap_codepage` and `cl_abap_char_utilities` names — and never quote an SAP code-page number without saying it should be verified against the system.

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
- Where the sibling Rust library already teaches something — `u8`, hexadecimal, `char`, the anatomy of a `String` — link to it and do not repeat it. Its pages publish at `https://masiarek.github.io/rust-learning-library/<folder>/index.html`; a folder README is `index.html`, never `README.html`.

## Nav order

Sidebar reading order lives in `NAV_ORDER` in `mkdocs_hooks.py`, keyed by folder path. **Never set order by renaming files to `01_`, `02_`** — a filename is a permanent URL. Unlisted pages sort alphabetically at the bottom, so adding a page needs no edit there; a new chapter does.

## Before you commit

```bash
python3 tools/check_all.py              # all four gates, in CI's order
python3 tools/check_all.py --committed  # the same, against what CI will check out
```

That runs the four commands CI runs — `run_examples.py --check`, `check_link_style.py`, `check_decomposed_literals.py` (with its `--selftest` first), and `uv run --group docs mkdocs build --strict` — and you can still run any of them alone. `--strict` fails on a broken internal link, which is the failure most likely to reach the published site unnoticed. The examples job also runs on macOS in CI; a shell example that passes here and fails there is a BSD/GNU difference, not a flake.

**Two reasons to use the runner rather than the four commands.**

The first is that these gates print a line per example, so the natural way to run one by hand is to pipe it — and **a pipeline's exit status is the last command's**, so `run_examples.py --check | tail -1` reports success no matter what the gate said. A red gate then scrolls past under a green-looking summary line. `set -o pipefail` fixes it — in bash and in zsh — if you remember it every time. What does **not** fix it is the idiom most people reach for next: `${PIPESTATUS[0]}` is bash's spelling, and under zsh it expands to the empty string rather than erroring, so `echo "exit=${PIPESTATUS[0]}"` prints `exit=` and reads like a stumble instead of a wrong answer (zsh's own array is lowercase and 1-indexed, `${pipestatus[1]}`). That is the same failure one level down, so prefer `set -o pipefail` or a plain redirect over any array lookup — and `check_all.py` does not pipe at all: it keeps each status and prints a failing gate's output only when there is one.

The second is `--committed`, which extracts `git archive HEAD` into a temporary directory and runs the gates there. That is what CI checks out, and it differs from your working directory in **both** directions. An untracked file makes your tree red where CI is green — somebody else's half-built lesson in a shared checkout does this constantly. And an untracked file that a *committed* page links to makes CI red where your tree is green, because `--strict` resolves the link against a tree where the target exists. Only the second one reddens the build for everybody, and only `--committed` can see it coming.

`python3 tools/check_all.py --selftest` proves the runner still reports a failure, in the same spirit as `check_decomposed_literals.py --selftest`.
