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

**Shell: `bash`, and only tools both macOS and Ubuntu ship** — `xxd`, `od`, `hexdump`, `cat`, `file`, `wc`, `printf`, `iconv`, `tr`, `sed`. On Ubuntu `xxd`, `hexdump` and `file` are separate packages, which the examples workflow installs if the runner image ever stops shipping them. CI runs every example on both, which is the only check that catches a BSD/GNU difference. Five already found. **`od -a` names bytes above 127 differently on the two platforms, and no layout helper can fix it** — GNU masks the high bit off and names the remainder (`c3` becomes `C`), BSD asks `isprint()` in the current locale and emits the raw byte when the answer is yes, so the row is both platform- and locale-dependent; record `-tx1` and never `-a`, as [Inspecting a file](06_Terminal/inspecting_a_file/README.md) sets out. Then: `od` pads its lines on macOS and not on Linux (pipe through the `tidy` helper the existing scripts define); `printf '\x..'` is bash, not POSIX (so the scripts run under `bash`, and a page that wants portability shows the octal form); **`cat -A` does not exist on macOS** (`cat -vet` is the portable spelling of the same three flags, and its output is identical on both); and `iconv -c` **repairs differently** — on invalid input macOS iconv stops at the first bad byte while GNU iconv skips it and keeps going, so the same command writes two different files. Plain `iconv -f X -t X` used as a yes/no validator agrees on both, exit status and all, which is what [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) records. And `iconv -t UTF-16` **with no `BE` or `LE` picks the byte order itself** — big-endian on macOS, little-endian on GNU — so the same command writes two different files and there is no key that matches both; name the order explicitly (`UTF-16BE` / `UTF-16LE`), as [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) does.

**Deterministic.** No clocks, no randomness, no network, no reading the filesystem. Every example runs under a fixed environment (`LC_ALL=C`, `PYTHONUTF8=1`) so the key does not depend on who ran it; a lesson whose subject *is* the locale sets its own inside the script, on purpose and in view.

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
python3 tools/run_examples.py --check
python3 tools/check_link_style.py
uv run --group docs mkdocs build --strict
```

All three are what CI runs. `--strict` fails on a broken internal link, which is the failure most likely to reach the published site unnoticed. The examples job also runs on macOS in CI; a shell example that passes here and fails there is a BSD/GNU difference, not a flake.
