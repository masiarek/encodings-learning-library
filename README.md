# Encodings — Learning Library

<!-- --8<-- [start:hero] -->

A learning library about **bits, bytes, characters, encodings and strings**, built the same way as its siblings [rust-learning-library ↗](https://github.com/masiarek/rust-learning-library) and [math-learning-library ↗](https://github.com/masiarek/math-learning-library): **one idea per page, and every claim backed by a program that actually runs.**

No page here hand-types what a program prints. Each lesson links real example files — Python, Rust, and a shell script — and a tool runs them, checks the output against a recorded answer key, and pastes that verified output into the page. CI fails, on Ubuntu *and* macOS, if any of the three drift apart. So when a page says *"`café` is five bytes"*, that is not a promise — it is a test result.

📖 **Read it as a site:** <https://masiarek.github.io/encodings-learning-library/>

<!-- --8<-- [end:hero] -->

<!-- --8<-- [start:below-hero] -->

## The root problem: bytes are not characters

A file on disk is just **bytes** — numbers 0 through 255. What you meant to store was **characters**: `A`, `—`, `é`, `你`. An **encoding** is the agreed rulebook mapping one to the other, and there has never been only one rulebook.

The catch is the whole subject: **a file does not record which rulebook was used.** No header, no marker — just bytes. Every program that opens a text file has to decide, from a protocol, a convention, or a guess. When the writer and the reader disagree you get [mojibake](03_Encodings/mojibake/README.md): the bytes are correct and the interpretation is wrong. Worse, [some tables cannot report a problem at all](09_History/why_utf8_won/README.md) — which is why this damage went undiagnosed for twenty years.

That is the plan of the library. Chapter 1 is the bytes, chapter 2 is the characters, chapter 3 is the rulebook, and chapters 4 through 7 are the four places the disagreement actually happens.

## Start here

[**00_Start_Here/**](00_Start_Here/README.md) is the plan: seven chapters in reading order, the four checkpoints they lead to, and how to work a lesson. Then the first three pages, which are the whole of chapter 1:

| Lesson | What it teaches |
|---|---|
| [A byte is eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) | Eight switches, 256 patterns, and why the byte does not know whether it is 65 or `A` |
| [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) | Bits four at a time, so a byte is always two digits — and why `41` on screen is not `'41'` in the file |
| [Reading a hex dump](01_Bits_and_Bytes/reading_a_hex_dump/README.md) | The three columns of `xxd`, and the first sight of `café` being five bytes |

## The course, in order

| Chapter | The question it settles |
|---|---|
| [01_Bits_and_Bytes](01_Bits_and_Bytes/README.md) | What is a file made of? |
| [02_Characters](02_Characters/README.md) | Who decided which number is which letter — and how did 128 become a million? |
| [03_Encodings](03_Encodings/README.md) | How does a code point become bytes, and what does it look like when a file is read under the wrong rule? |
| [04_Python](04_Python/README.md) | Where does Python draw the text/bytes line, and where is it easy to cross by accident? |
| [05_Rust](05_Rust/README.md) | What is the promise a `String` makes, and which rules are that promise being kept? |
| [06_Terminal](06_Terminal/README.md) | How do I see, make, and re-encode bytes with no language at all? |
| [07_Real_Data](07_Real_Data/README.md) | The six shapes this takes when a file crosses an SAP interface |
| [08_Build_Your_Own](08_Build_Your_Own/README.md) | A project: design a silly 3-bit text format with its own code points, then implement it in Rust against a reference that prints every expected result |
| [09_History](09_History/README.md) | Where all of this came from — six eras, six constraints, and why the one that won, won |
| [10_Best_Practices](10_Best_Practices/README.md) | What to actually do on Monday, in nine lines and three pages |
| [11_Tools](11_Tools/README.md) | `grep`, `find`, `rg`, `tr`, `sort`, `uni` — the tools you already run over text, and the encoding decision each one makes for you |

Chapters 1, 9, 10 and 11 are written, along with the first pages of chapter 2, half of chapter 3, and the chapter 8 project; the rest are **stubs** — each page's questions written down, with a notice, and no example behind it yet. [ROADMAP.md](ROADMAP.md) says what is next.

**In a hurry?** [10_Best_Practices](10_Best_Practices/README.md) is the whole modern answer on one page, and [Why UTF-8 won](09_History/why_utf8_won/README.md) is why it is that short.

## Six tools worth installing

The library needs none of these and CI has none of them, so nothing in this section is an answer key: each block is dated and names the machine it ran on. [11_Tools](11_Tools/README.md) measures every one of them against the tool you already have, because half the value is knowing exactly where the free answer stops.

**[`uni`](11_Tools/uni/README.md) earns its place immediately.** It prints every column at once — including the one no dump tool has, the character's *name*, which is the answer to "what **is** this?"

```text title="Measured 2026-09-06 — uni (Unicode 17.0, brew), macOS 26.6"
$ uni identify 'żé€'
             Dec    UTF8        HTML       Name
'ż'  U+017C  380    c5 bc       &zdot;     LATIN SMALL LETTER Z WITH DOT ABOVE
'é'  U+00E9  233    c3 a9       &eacute;   LATIN SMALL LETTER E WITH ACUTE
'€'  U+20AC  8364   e2 82 ac    &euro;     EURO SIGN
```

`UTF8` is the column a hex dump already gives you; the other four are in no dump. It runs backwards too — `uni print U+017C` from the code point, `uni search 'z with dot'` from the name. It matches the *name*, mind: `uni search polish` finds NAIL POLISH before it finds a Polish letter.

The other five each answer one question the base toolbox answers badly:

| Tool | Try it | What you get that you did not have |
|---|---|---|
| [`hexyl`](11_Tools/worth_installing/README.md) | `hexyl demo.txt` | `×` non-ASCII, `_` whitespace, `⋄` NUL, each in its own colour — where `xxd`'s text column draws `.` for all three alike |
| [`uchardet`](11_Tools/worth_installing/README.md) | `uchardet demo.txt` | a real detector. [`file`](06_Terminal/file_guesses/README.md) can only prove a file is *not* valid UTF-8; `uchardet` names the 8-bit table — and is still guessing |
| [`recode`](11_Tools/worth_installing/README.md) | `recode utf8..latin1 file.txt` | `é` converted from two bytes to one — and a **refusal**, file untouched, when the target table cannot carry a character. macOS `iconv` transliterates instead, silently |
| [`dos2unix`](11_Tools/worth_installing/README.md) | `dos2unix -i mixed.txt` | DOS, Unix and bare-CR line counts plus the BOM column, in one line, changing nothing |
| [`coreutils`](11_Tools/worth_installing/README.md) | `brew install coreutils` | the GNU tools beside the BSD ones, so a platform split stops being something only CI can see |

**`coreutils` paid off best, and the result is folded back into the library.** These pages document that BSD and GNU `od -a` disagree about every byte above 127 — but until now the disagreement could only show one side per machine, with CI as the sole witness. Now both sides run in the same second, on one file:

```text title="Measured 2026-09-06 — BSD od beside GNU coreutils 9.11 (brew), macOS 26.6, LC_ALL=C, on café in Latin-1. Trailing padding trimmed for width; the leading indent is real."
$ xxd -p latin1.txt
636166e90a

$ od -An -a latin1.txt        # BSD — the od already on your Mac
           c   a   f  e9  nl

$ god -An -a latin1.txt       # GNU — the same flags, from coreutils
   c   a   f   i  nl
```

One byte, `e9`, and two answers. GNU masks the high bit off and names what is left — `0xe9 & 0x7f` is `0x69`, so it prints `i`, and `cafi` is a wrong answer that reads like a word. BSD asks `isprint()` in your locale, cannot print it, and gives you the byte's number. [Inspecting a file](06_Terminal/inspecting_a_file/README.md) takes that apart and shows the same run untrimmed — BSD indents eleven spaces, pads the line to 72 characters and adds a blank line after it; GNU indents three and does none of that. The short version is that the `-a` row of a hex dump is the one column you should not trust.

## Why three languages

The code is the illustration, never the subject. Each is here for what it shows that the other two cannot:

- **Python** shows the idea in the fewest lines, and draws the text/bytes line as a type boundary you can see (`str` vs `bytes`).
- **The terminal** shows the actual bytes on an actual pipe — `xxd`, `od`, `printf`, `iconv` — with no language's interpretation in between.
- **Rust** shows the same idea with the width (`u8`) and the encoding (`String` promises UTF-8) written into the type, so the compiler holds a line the other two leave to discipline.

A few lessons add a short **C view** — `examples/*.c`, compiled and checked like the rest — where seeing the bytes with no abstraction at all is the fastest explanation; NUL is the first.

Every lesson also carries an *If you are coming from Python or ABAP* section, because those are the two languages a reader of this library already thinks in. The ABAP half is prose — CI cannot run ABAP — and says so on every page.

## How the library works

```
01_Bits_and_Bytes/
  hex_is_a_shorthand/
    README.md                          the lesson  (prose + generated output blocks)
    examples/
      hex_is_a_shorthand_py.py         the Python program a reader can run
      hex_is_a_shorthand_py.out        its recorded output — the answer key
      hex_is_a_shorthand_rs.rs         the same idea in Rust (bare rustc, no crates)
      hex_is_a_shorthand_rs.out
      hex_is_a_shorthand_sh.sh         the same idea on the command line
      hex_is_a_shorthand_sh.out
```

A lesson page never pastes output by hand. It marks the spot:

```markdown
<!-- output:hex_is_a_shorthand_py -->
<!-- /output -->
```

and `tools/run_examples.py` fills it from a real run. Inside the markers is generated; outside is yours.

```bash
python3 tools/run_examples.py            # verify, and refill the pages
python3 tools/run_examples.py --update   # accept current output as the answer key
python3 tools/run_examples.py --check    # write nothing, fail on drift (what CI runs)
```

There is a second block kind, `source:`, which pastes the program itself for pages where the code *is* the lesson.

Conventions for anyone writing a page: [CONTRIBUTING.md](CONTRIBUTING.md). The characters and strings every page demonstrates with: [CAST.md](CAST.md). Terms: [GLOSSARY.md](GLOSSARY.md). Links, books, videos, tools and katas, each one checked: [RESOURCES.md](RESOURCES.md). What is planned and deliberately not written yet: [ROADMAP.md](ROADMAP.md).

<!-- --8<-- [end:below-hero] -->
