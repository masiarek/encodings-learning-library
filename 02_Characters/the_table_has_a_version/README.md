# The table has a version

**Level:** 201 · for anyone who records what a program printed

**One line:** There is no *the* Unicode version on your computer — every program carries its own copy of the table, and on the machine this page was written on the two languages this library teaches were a **year apart**.

```python
import unicodedata
unicodedata.unidata_version              # '16.0.0'  <- your interpreter's table
unicodedata.ucd_3_2_0.unidata_version    # '3.2.0'   <- the frozen one, the same everywhere
```

Chapter 2 has been saying *the table* as though there were one. There is one **standard**, and it is versioned: a release every September, each one adding characters and never removing any. What sits on your disk is not the standard but a stack of independent copies of it — one inside the Python interpreter, one inside every binary `rustc` ever built for you, one in the C library, one in the browser, one in the operating system's own character viewer. Nobody updates them together.

That is not a defect, and it very rarely bites. It bites in exactly one place, which is why this page exists: **the moment you write down what a program printed and expect it back.**

## Four answers on one machine, on one afternoon

```text title="Measured on one Mac, macOS 26.6.2, 2026-09-06 — not machine-checked; the whole point is that it varies"
$ python3 --version
Python 3.14.2
$ python3 -c 'import unicodedata; print(unicodedata.unidata_version)'
16.0.0                                   # Unicode 16.0, September 2024

$ rustc --version
rustc 1.98.0 (88d9e12ae 2026-08-18)
$ cat v.rs; rustc --edition 2024 v.rs && ./v
fn main() { println!("{:?}", char::UNICODE_VERSION); }
(17, 0, 0)                               # Unicode 17.0, September 2025

$ uni version                            # a third-party CLI, not part of this library
git; Unicode 17.0 (September, 2025)

$ sw_vers -productVersion                # macOS's own Character Viewer database
26.6.2                                   # ships no version to ask for at all
```

Read the first two again. `python3` and `rustc`, on one laptop, in one repository, running the examples on one page — **a full release apart**. Not a broken install; both are current. Python 3.14 was cut before Unicode 17.0 landed and Rust's was cut after, and neither has any reason to care what the other thinks.

## What a release apart actually costs

A version string is easy to shrug at. Here are the same three tools asked about one code point that exists and one that does not:

```text title="Measured on the same Mac, 2026-09-06 — not machine-checked, and not machine-checkable: uni is on neither CI runner and the toolchains differ per runner"
                             U+11DB0                    U+0378
                             TOLONG SIKI LETTER I       nothing, in any version
                             (new in Unicode 17.0)      (reserved, never assigned)
      -------------------------------------------------------------------------
  uni 2.9.0        UCD 17.0  TOLONG SIKI LETTER I       uni: unknown codepoint
  rustc 1.98.0     UCD 17.0  is_alphabetic() -> true    is_alphabetic() -> false
  python3 3.14.2   UCD 16.0  category() -> 'Cn'         category() -> 'Cn'
                             name() -> ValueError       name() -> ValueError
```

Read the bottom two rows across. **Python gives the identical answer to both columns** — and one of those columns is a letter somebody writes their language in. `Cn` does not mean *"not in my edition"*; it means *unassigned*, a claim about Unicode rather than about the interpreter, and it comes with no hedge. The older table does not report a gap in its knowledge. It reports a fact, confidently, and the fact is false.

That is the same failure this library has already met twice: [`od -a`](../../06_Terminal/inspecting_a_file/README.md) inventing the letter `C` for a byte it cannot name, and [`file`](../../06_Terminal/file_guesses/README.md) guessing rather than declining. A tool that says *"I don't know"* costs you five minutes. A tool that answers wrongly costs you the afternoon, because there is nothing in the output to investigate.

One thing the row does *not* explain away: Rust's `is_alphabetic` is the Alphabetic property, a superset of Python's `isalpha` (`L*`), so a `true`/`false` split between them is normally suspect on definitional grounds alone. Not here — a `Cn` code point is in neither set. That disagreement is the table edition and nothing else.

The fourth line is the one that should make you uneasy, and it is the reason `uni` is in the list at all. `uni` ships its own copy of the Unicode Character Database, so it can *tell you* which one — 17.0, dated. macOS's Character Viewer reads `CharacterDB.sqlite3` out of a private framework, and there is nothing to ask: no version string, no date, and names that are Apple's rather than the standard's. A tool that cannot name its table is a tool you cannot quote.

## Two tables in one interpreter

Python ships the frozen table as well as the live one, and that is a gift, because a frozen table's answers can be printed on a page.

<!-- output:the_table_has_a_version_py -->
*Verified output of [`the_table_has_a_version_py.py`](examples/the_table_has_a_version_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE MODULE, TWO UNICODE TABLES
------------------------------------------------------------------------
   unicodedata               the table this interpreter was built with
   unicodedata.ucd_3_2_0     Unicode 3.2.0, sealed in 2002

   The frozen one is here because IDNA and stringprep pinned their table
   on purpose: a domain name must not change meaning when Unicode grows.
   That makes it the one Unicode table whose answers are the same on
   every machine under every Python -- which is why this program may
   print them, and may not print the other one's.

2. THE SAME QUESTION, ASKED OF BOTH TABLES
------------------------------------------------------------------------
   code point  char   name, from whichever table knows it   in 2002?
   U+00E9      é      LATIN SMALL LETTER E WITH ACUTE       yes
   U+017C      ż      LATIN SMALL LETTER Z WITH DOT ABOVE   yes
   U+20AC      €      EURO SIGN                             yes
   U+0CA0      ಠ      KANNADA LETTER TTHA                   yes
   U+1E9E      ẞ      LATIN CAPITAL LETTER SHARP S          no
   U+1F600     😀      GRINNING FACE                         no
   U+20BD      ₽      RUBLE SIGN                            no
   U+20BF      ₿      BITCOIN SIGN                          no

   4 of the 8 are missing from the 2002 table.
   Nothing was ever removed from Unicode -- these had not arrived yet.

3. GROWING IS THE ONLY THING THE TABLE EVER DID
------------------------------------------------------------------------
   code points the 2002 table and this one name differently:  0
   code points this table has names for, over 100,000:        True

   The zero is not luck. A Name is one of Unicode's stability guarantees:
   once a code point is assigned, its name may never change and the code
   point may never be reused. So a NAME is safe to put in an answer key.
   The count beside it is not -- which is why it is printed as a question
   with a stable answer rather than as a number.

4. AN OLD TABLE DOES NOT SAY "I DO NOT KNOW"
------------------------------------------------------------------------
   the frozen 2002 table, asked about four very different code points:

   code point  category  name          what it actually is
   U+1F600     Cn        ValueError    GRINNING FACE, real since 2010
   U+1E9E      Cn        ValueError    CAPITAL SHARP S, real since 2008
   U+0378      Cn        ValueError    genuinely unassigned, still is
   U+FFFE      Cn        ValueError    a noncharacter -- never will be

   Four different truths and one answer. Cn means UNASSIGNED, so on the
   top two rows the table is not reporting a gap in its own knowledge --
   it is making a false statement about Unicode, with no hedge in it.

   That is the whole hazard in a line. An out-of-date table does not
   fail, and it does not say it is out of date. It answers confidently
   and wrongly, the way od -a invents a letter for a byte it cannot
   name -- and you cannot tell the four cases apart from the answer,
   because the answer is the same.

5. THE VERSION IS THE ONE THING THIS PROGRAM WILL NOT PRINT
------------------------------------------------------------------------
   unicodedata.unidata_version is a str in three parts:   True
   and it is newer than the frozen table:               True

   The value itself -- '16.0.0', '17.0.0', whatever yours says -- is
   deliberately absent. Recording it would put the machine that built
   this page into the answer key, and the next machine would then fail
   a check about nothing. Ask your own copy instead:

       python3 -c 'import unicodedata; print(unicodedata.unidata_version)'

6. WHAT SURVIVES THE VERSION, AND WHAT DOES NOT
------------------------------------------------------------------------
   arithmetic -- true under every version ever published:
      usable scalar values, 0x110000 minus 2,048 surrogates   1112064

   guaranteed -- Unicode promises these never change:
      the name of an assigned code point   LATIN SMALL LETTER E WITH ACUTE
      the code point of that character     U+00E9

   a lookup -- true today, in this table, on this machine:
      how many code points are assigned
      whether U+11DB0 is one of them
      whether a character is alphabetic, uppercase, whitespace

   The first two groups belong in a test.
   The third belongs in a sentence with a date on it.
```
<!-- /output -->

`ucd_3_2_0` exists for [IDNA and stringprep ↗](https://datatracker.ietf.org/doc/html/rfc3454), which pinned Unicode 3.2 deliberately: a domain name must not change meaning because the standard grew. That makes it the one Unicode table in the stdlib whose answers are identical on every machine — so this page can print them, and cannot print the other one's.

Section 3 is the load-bearing one. **Zero renames across the whole number line**, and that zero is a policy, not an accident. Unicode's [stability guarantees ↗](https://www.unicode.org/policies/stability_policy.html) say a code point, once assigned, keeps its name forever and is never reused. So a **name** is safe to write into a test. A **count** is not, and neither is *"is this assigned yet"* — the program prints the first as a value and the second two as questions with stable answers.

## Rust bakes it in instead

<!-- output:the_table_has_a_version_rs -->
*Verified output of [`the_table_has_a_version_rs.rs`](examples/the_table_has_a_version_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE TABLE TRAVELS WITH THE BINARY
------------------------------------------------------------------------
   char::UNICODE_VERSION is a (u8, u8, u8) const, baked in by rustc.
   Its value is not printed here, for the reason the Python program
   gives: it is a fact about the toolchain that built this file, not
   a fact about Unicode.

   is it at least 9.0?   true
   ...and the compiler agreed before the program ever ran:
      const _: () = assert!(char::UNICODE_VERSION.0 >= 9);

   That const assert is the whole difference from Python. Python
   reads unicodedata at run time, so the answer follows whichever
   interpreter you launch. Rust settles it at compile time, so a
   binary keeps the table its rustc had. Two machines running the
   SAME binary can never disagree; two machines compiling the same
   source very well can.

2. DEFINITIONAL HERE TOO, AND STILL FREE OF THE TABLE
------------------------------------------------------------------------
   char::MAX                        U+10FFFF
   char::from_u32(0xD800)           None   <- the surrogate hole
   char::from_u32(0x110000)         None   <- past the end
   usable scalar values             1112064

   None of those four consult a table. They are the shape of the
   number line, fixed when UTF-16 fixed it, and no Unicode release
   can move them.

3. THESE DO CONSULT IT -- AND THESE ANSWERS ARE STILL SAFE
------------------------------------------------------------------------
   code point  alphabetic  uppercase  len_utf8   char
   U+00E9      true        false      2          é
   U+1E9E      true        true       3          ẞ
   U+1F600     false       false      4          😀
   U+FFFE      false       false      3          ￾

   The first three have been settled since 2010 at the latest, and
   General_Category is not a property Unicode changes lightly -- but
   note that it is NOT on the stability list, so `settled` here means
   observed, not promised. The fourth row is the promised one:
   U+FFFE is a PERMANENT noncharacter, guaranteed never to be assigned
   anything, so `false` there is not a reading of today's table but a
   statement about every future one. That is the kind of lookup that
   can safely go in a test.

4. AND THE ONE THIS PROGRAM REFUSES TO ANSWER
------------------------------------------------------------------------
   U+11DB0 TOLONG SIKI LETTER I arrived in Unicode 17.0, in September
   2025. A rustc built before that says `false`; one built after says
   `true`. Same source, same machine, same input, and no bug -- so the
   row is described here and not printed. Ask your own compiler:

       fn main() { println!("{}", '\u{11DB0}'.is_alphabetic()); }

   Then ask the python3 next to it. On the machine this page was
   written on the two did not agree, and the page says so in a fence
   with a date on it, because that is the only honest place for it.

5. ONE MORE THE TABLE DECIDES FOR YOU
------------------------------------------------------------------------
   'ß'.to_uppercase()               "SS"   (2 chars)
   U+1E9E exists as a single char   Some('ẞ')

   Uppercasing ß gives two characters, not the single one that has
   existed since 2008. That is not arithmetic and not an oversight --
   it is a line in SpecialCasing.txt, which is to say a row in the
   table, which is to say something that has a version.
```
<!-- /output -->

The mechanism differs in a way worth holding on to. Python reads its table at run time, so the answer follows whichever interpreter you launch — change the `python3` on your `PATH` and the answer changes under a program you did not touch. Rust resolves `char::UNICODE_VERSION` at *compile* time, which the const assert proves: a value the compiler can `assert!` on before the program runs is a value that is already fixed. So a Rust binary carries its table with it — two machines running the same binary can never disagree — while two machines *compiling the same source* very well can.

Which is the sharper failure, because it is invisible in the diff. Nothing in the source changed; the toolchain did.

## So what do you actually record?

Three groups, and the whole discipline is telling them apart.

| | example | safe in an answer key? |
|---|---|---|
| **Arithmetic** | `0x110000 − 2048 = 1,112,064`; `char::MAX`; the surrogate hole | yes, under every version ever published |
| **Guaranteed** | a name (`LATIN SMALL LETTER E WITH ACUTE`); a code point (`U+00E9`); `U+FFFE` is a noncharacter | yes — these are written into the stability policy |
| **A lookup** | how many code points are assigned; whether `U+11DB0` is one; `is_alphabetic`, `is_uppercase`, `is_whitespace` | no — put it in a sentence with a date on it |

The middle row is doing more work than it looks. `is_alphabetic('é')` has been `true` since 1991 and will be `true` next year too, but *nothing promises that* — General_Category is not on the stability list. It is observed, not guaranteed, which is a different word and belongs in a different column.

This is the rule that already governs this repo, arrived at from the other direction. [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) found `od -a` naming bytes in two dialects and recorded `-tx1` instead; the same page's tool comparison sits in a dated, hand-labelled fence because no key could match both platforms. Neither `python3` nor `rustc` is pinned in this library's CI, and it runs on Ubuntu *and* macOS — so a key derived from a table lookup would break on one runner only, which is the failure no local check can see.

The one measured survivor is worth knowing: [Unicode code points](../unicode_code_points/README.md) scans all 1,114,112 slots for `char::is_whitespace` and prints the runs, and it is green on both runners, because `White_Space` has been 25 code points since 2005. That scan is safe **for that property**. It is not a licence.

## If you are coming from Python or ABAP

**Python.** `unicodedata.unidata_version` is the version of the table compiled into *this* interpreter, and `unicodedata.ucd_3_2_0` is a second module object exposing the frozen 3.2 table — same API, `name`, `category`, `decomposition`, all of it. The practical consequence is in tests: `assert unicodedata.name(c) == "..."` is fine forever, `assert len([c for c in ... if c.isalpha()]) == 4237` is a time bomb that goes off when someone upgrades Python. If you genuinely need a pinned table, the `unicodedata2` package on PyPI exists to give you a newer one than your interpreter has — which tells you how routine the skew is.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* The same split exists and is harder to see, because the table lives in the kernel rather than in something you can print a version of. `cl_abap_conv_*` and the `cl_abap_char_utilities` constants resolve against whatever the kernel and its code-page tables were built with, and a system copy carries the source system's kernel, not the target's. Practical version: a character-classification result that came out of Development is evidence about Development, and a code page number quoted from anywhere should be checked against the system that will actually run the job rather than repeated from a document.

## Try it

- Run the two commands in the fence above on your own machine. If your `python3` and your `rustc` agree, wait a September.
- `python3 -c "import unicodedata as u; print(u.name(chr(0x11DB0), 'not in your table'))"` — the character this page's Rust program deliberately refuses to answer for. Then ask `rustc` the same thing, and see whether your two agree.
- Find a test in your own work that asserts on a character property rather than a character name, and decide which of the three rows of the table above it belongs in.
- Ask the frozen table something modern: `unicodedata.ucd_3_2_0.name('😀', 'nope')`. Then ask why a 2002 table is still shipped in 2026.

## See also

- [Unicode code points](../unicode_code_points/README.md) — the number line this table assigns names to
- [A code point is not a character](../a_code_point_is_not_a_character/README.md) — the other thing the table alone will not tell you
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — where `U+FFFE`'s permanent-noncharacter status does the same job as proof
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — the same discipline, arrived at from `od -a`
- [Conventions](../../CONTRIBUTING.md) — what may and may not go into a recorded key
- [Unicode Character Encoding Stability Policies ↗](https://www.unicode.org/policies/stability_policy.html)
- [`uni` ↗](https://github.com/arp242/uni) — a CLI that ships its own UCD, so it can tell you which one
