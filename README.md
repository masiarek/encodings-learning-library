# Encodings — Learning Library

<!-- --8<-- [start:hero] -->

A learning library about **bits, bytes, characters, encodings and strings**, built the same way as its siblings [rust-learning-library ↗](https://github.com/masiarek/rust-learning-library) and [math-learning-library ↗](https://github.com/masiarek/math-learning-library): **one idea per page, and every claim backed by a program that actually runs.**

No page here hand-types what a program prints. Each lesson links real example files — Python, Rust, and a shell script — and a tool runs them, checks the output against a recorded answer key, and pastes that verified output into the page. CI fails, on Ubuntu *and* macOS, if any of the three drift apart. So when a page says *"`café` is five bytes"*, that is not a promise — it is a test result.

📖 **Read it as a site:** <https://masiarek.github.io/encodings-learning-library/>

<!-- --8<-- [end:hero] -->

<!-- --8<-- [start:below-hero] -->

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

Chapters 1, 9 and 10 are written, along with the first pages of chapter 2 and the chapter 8 project; the rest are **stubs** — each page's questions written down, with a notice, and no example behind it yet. [ROADMAP.md](ROADMAP.md) says what is next.

**In a hurry?** [10_Best_Practices](10_Best_Practices/README.md) is the whole modern answer on one page, and [Why UTF-8 won](09_History/why_utf8_won/README.md) is why it is that short.

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

Conventions for anyone writing a page: [CONTRIBUTING.md](CONTRIBUTING.md). Terms: [GLOSSARY.md](GLOSSARY.md). Links, books, videos, tools and katas, each one checked: [RESOURCES.md](RESOURCES.md). What is planned and deliberately not written yet: [ROADMAP.md](ROADMAP.md).

<!-- --8<-- [end:below-hero] -->
