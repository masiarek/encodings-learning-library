# Sorting and collation

**Level:** 301 · for anyone who has shipped an alphabetical list

**One line:** `sorted()` puts `Łódź` after `Zebra`, and no Polish speaker would — because code point order is not alphabetical order in any language, which order *is* right is a property of the locale rather than of the text, the locale data is a versioned file on the machine that can change underneath a database that has already sorted on it — and even with the locale right, a collation ignores things on purpose, so *correct* does not yet mean *repeatable*.

## Three questions, and only the first one has an obvious answer

*Are these two strings the same?* is [normalization](../../04_Python/normalization/README.md). *Which of these two strings comes first?* is collation, and it is the harder of the two, because equality has a right answer that Unicode can define and ordering does not — the correct order for one list of names genuinely differs between two readers, and both are right.

`sorted()` in Python and `.sort()` in Rust order by code point, which is an index into a table nobody ever sorted. The Latin letters got their numbers in three eras — ASCII in the 1960s, the Latin-1 supplement in the 1980s, Latin Extended-A when Unicode shipped in 1991 — so every accented letter is numerically behind every unaccented one, in a block. Section 1 of the run below shows the block. It is not a near miss to be nudged; it is a different principle.

## The comparison is three questions, not one

Before which order, what a comparison *is*. [UTS #10 ↗](https://www.unicode.org/reports/tr10/) — the Unicode Collation Algorithm, and the specification every locale's data is poured into — does not compare two strings once. It compares them up to three times, on three keys, in a fixed order:

| level | what it distinguishes | UTS #10's own example |
|---|---|---|
| **L1 — primary** | the base letters | `role < roles < rule` |
| **L2 — secondary** | the accents | `role < rôle < roles` |
| **L3 — tertiary** | the case | `role < Role < rôle` |
| L4 — quaternary | punctuation, where it is not ignored outright | `role < “role” < Role` |
| Ln — identical | the tie-break: normalized code point order | `role < ro□le < “role”` |

Those are not five contributions to one score. They are five questions in a fixed order, and **the first one that answers stops the comparison** — which is why the second row repays a second reading. `rôle` and `roles` differ by an accent *and* by a base letter, and the accent never gets a vote, because L1 has already decided.

That structure is not a metaphor for the data; it is the data. The default weight table UTS #10 ships holds one line per character and three numbers on it:

```text title="Six lines from allkeys-17.0.0.txt (the DUCET, dated 2025-07-23). Quoted, not machine-checked — nothing read out of a Unicode data file may become an answer key here, for the reason [CONTRIBUTING](../../CONTRIBUTING.md) gives."
0061  ; [.23EC.0020.0002] # LATIN SMALL LETTER A
0041  ; [.23EC.0020.0008] # LATIN CAPITAL LETTER A
0301  ; [.0000.0024.0002] # COMBINING ACUTE ACCENT
00AD  ; [.0000.0000.0000] # SOFT HYPHEN
200D  ; [.0000.0000.0000] # ZERO WIDTH JOINER
FEFF  ; [.0000.0000.0000] # ZERO WIDTH NO-BREAK SPACE
```

Read the columns and the model falls out of them. `a` and `A` share a primary weight *and* a secondary weight and differ only in the third — that is "case is a tertiary difference", written as two numbers rather than asserted. The combining acute has a **zero** primary and a real secondary: an accent is a character with no opinion about which letter you are looking at and a firm one about which of two otherwise identical letters comes first. And the last three are zero all the way across. They are **completely ignorable** — a soft hyphen, a zero-width joiner, and a stray [BOM](../bom_in_a_csv/README.md), which is worth noticing on a page in this chapter. The algorithm is told to behave as though they were not in the string.

This is the vocabulary the rest of the page runs on, and it is what makes the differences below describable rather than merely observable: English and Polish do not disagree about *how much* `ó` matters, they disagree about **which level** its difference lands on — secondary in one, primary in the other. Section 1 of [the levels run below](#the-comparison-in-three-levels-and-the-tie-that-breaks-it) reproduces all three rows of that table from a toy key in about a dozen lines, so the shape can be read rather than believed.

## The locale is the missing data, and it may not be there

Which locales a machine has is not a property of your program. A stock `ubuntu:24.04` image ships exactly three — `C`, `C.utf8` and `POSIX` — and no human language at all, and `locale.setlocale` **raises** for anything else rather than falling back to something near enough. Section 2 measures that, including the part people miss: the call raises *and changes nothing*, so a program that needs Polish ordering has to have a plan for not getting it.

That is also why this page's example does not ask for a locale. Every example in this library runs under a pinned environment (`LC_ALL=C`, `PYTHONUTF8=1`) so an answer key is a property of the code rather than of whoever ran it; [CONTRIBUTING](../../CONTRIBUTING.md) carves out a lesson whose *subject* is the locale, which may set its own inside the script, in view — and the [`LC_CTYPE` page](../../06_Terminal/locale_and_lc_ctype/README.md) does exactly that. Collation cannot take that carve-out, because the locales it would need are not installed on both CI runners and there is no answer key that matches a machine that has `pl_PL.UTF-8` and one that does not. So the recorded run holds only what no machine can disagree about, and the comparison the page is really about is below it in a dated fence.

## In Python

<!-- output:sorting_and_collation_py -->
*Verified output of [`sorting_and_collation_py.py`](examples/sorting_and_collation_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. CODE POINT ORDER IS NOT ALPHABETICAL ORDER IN ANY LANGUAGE
----------------------------------------------------------------------
   sorted(names)             Cma Osa Swit Zebra Zuk Óda Ćma Łódź Świt Żuk

   Read the tail: every accented word is behind every unaccented one,
   in a block. That is not a near miss, it is a different principle.

     Z  U+005A     90   ASCII, 1963
     Ó  U+00D3    211   Latin-1 Supplement, 1987
     Ć  U+0106    262   Latin Extended-A, 1991
     Ł  U+0141    321   Latin Extended-A, 1991
     Ż  U+017B    379   Latin Extended-A, 1991

   Three blocks, three eras. 'Z' is in ASCII, which fixed its 128
   numbers in the 1960s. 'Ó' is in the Latin-1 supplement, the second
   half of an 8-bit table from the 1980s. 'Ł', 'Ć' and 'Ż' are in
   Latin Extended-A, a block Unicode added in 1991 for the languages
   the first two had no room for.

   So 'Ł' is U+0141 and 'Z' is U+005A because of when each letter got
   a number, not because of anything about the letters. A code point
   is an index into a table nobody ever sorted; sorting by it is
   sorting by the history of the standard.

2. ASKING FOR A LOCALE IS A CALL THAT CAN FAIL, AND IT DOES NOT FALL BACK
----------------------------------------------------------------------
   LC_COLLATE at the start        'C'
   asked for a locale nobody has  locale.Error
   LC_COLLATE afterwards          'C'

   It raised, and it changed nothing. There is no quiet fallback to a
   near-enough locale, and there is no way to ask 'do you have one for
   Polish?' other than trying it -- so a program that wants a specific
   ordering has to handle NOT GETTING IT, on every machine it will run
   on. A container is the likely place to find out: a stock
   ubuntu:24.04 image ships C, C.utf8 and POSIX, and no human language
   at all, so this call fails there for every locale you would want.

   Two more things about the call, both of which surprise people:
     * it is PROCESS-GLOBAL state, not an argument. Setting it in one
       thread changes the sort in every other one.
     * LC_COLLATE is not LC_CTYPE. Setting the character type to a
       UTF-8 locale says nothing about ordering, and the wrong one of
       the six is the usual reason 'I set the locale' did not work.

3. THE TWO SPELLINGS, AND WHAT THE C LOCALE MEANS BY 'COLLATE'
----------------------------------------------------------------------
   key=locale.strxfrm        Cma Osa Swit Zebra Zuk Óda Ćma Łódź Świt Żuk
   cmp_to_key(strcoll)       Cma Osa Swit Zebra Zuk Óda Ćma Łódź Świt Żuk
   sorted(names)             Cma Osa Swit Zebra Zuk Óda Ćma Łódź Świt Żuk

   the two collation spellings agree with each other   True
   ...and with plain code point order                  True

   Both are the real thing: strxfrm turns a string into a sort KEY so
   the transformation happens once per element, strcoll compares two
   strings and costs a comparison every time. Prefer strxfrm for a
   sort and strcoll for a one-off test.

   And here they change nothing, because this process is in the C
   locale, where collation IS code point order. That is not a broken
   configuration -- it is the default in every container, cron job and
   CI runner, which means the production answer to 'sort these names'
   is usually the one at the top of section 1.

4. STRIPPING THE ACCENTS IS NOT COLLATION -- IT IS ONE LOCALE'S ANSWER
----------------------------------------------------------------------
   key=strip_marks           Ćma Cma Óda Osa Świt Swit Zebra Żuk Zuk Łódź

   Look at the first two. 'Ćma' and 'Cma' are DIFFERENT WORDS and the
   trick gives them the same key ('Cma' == 'Cma'), so it cannot
   order them at all -- Python's sort is stable, so what you get back
   is the order they arrived in. Shuffle the input and the output
   changes. A collation has to be a total order over the strings it
   is given; this is not one, and nothing reports that.

   Polish's nine special letters   ą ć ę ł ń ó ś ź ż
   NFD decomposes                  ą ć ę ń ó ś ź ż   (8 of 9)
   NFD leaves alone                ł   (1 of 9)

   That is the flaw, and it is silent. Eight of the nine come apart
   into a base letter and a combining mark, so the trick files them
   next to their base letter. 'ł' does not: U+0142 is a letter with a
   stroke THROUGH it, and a stroke is not a combining mark, so there
   is nothing to strip and 'Łódź' stays out at the end where the code
   points put it. Same word list, same trick, two different rules
   applied depending on how Unicode happened to encode each letter.

   It is worth being precise about what the trick gets right, too:
   filing 'ó' next to 'o' IS the correct answer -- in English. In
   Polish 'ó' is a LETTER, with its own place after 'o', so a Polish
   list sorts 'Osa' before 'Óda' and an English one the other way
   round. The trick cannot express that, because it has thrown the
   distinction away before the comparison starts.

   Which is the general point: an accent is not noise on a letter.
   Whether it is noise is a fact about the LANGUAGE, and it is the
   fact a locale carries.

5. WHAT A COLLATION ACTUALLY IS: LEVELS, OVER AN ALPHABET YOU DECLARE
----------------------------------------------------------------------
   key=pl_key (toy Polish)   Cma Ćma Łódź Osa Óda Swit Świt Zebra Zuk Żuk
   key=strip_marks           Ćma Cma Óda Osa Świt Swit Zebra Żuk Zuk Łódź
   sorted(names)             Cma Osa Swit Zebra Zuk Óda Ćma Łódź Świt Żuk

   The toy gets Polish right for this list -- 'Cma' then 'Ćma', 'Osa'
   then 'Óda', 'Swit' then 'Świt', 'Zuk' then 'Żuk', and 'Łódź' up
   between 'l' and 'm' where it belongs -- and it does it with thirty
   lines and ONE STRING: the alphabet, written out in order. That
   string is the entire difference between this and sorted().

   Two levels is also the shape of the real thing. Compare base
   letters first; if they tie, compare accents; if they still tie,
   compare case. That is why two locales can both look 'right' and
   still disagree -- they are not disagreeing about the levels, they
   are disagreeing about which differences belong on which level.

   What the toy has no room for is the rest of the data, and the
   omissions are not exotic:
     * contractions -- Czech sorts 'ch' as ONE letter, after 'h', so
       'chata' comes after 'hrad'; a per-character rank cannot say it
     * expansions -- German 'ß' compares as 'ss', one character
       weighing as two
     * variable weighting -- whether a space or a hyphen counts at all
       before the letters have been compared. Nobody thinks about that
       one, and it is the rule that moved in glibc 2.28.
```
<!-- /output -->

**Section 3 is the one to take to work.** In the C locale, `strxfrm` and `strcoll` agree with each other and with plain code point order, because the C locale *has* no collation. That is not a broken configuration — it is the default in every container, cron job and CI runner, which means the production answer to "sort these names" is usually the one at the top of section 1, arrived at through code that looks locale-aware.

**Section 4 is the trick everybody tries first.** Decompose to NFD, drop the combining marks, sort on what is left. It has three faults and all three are silent. It **fails on `ł`** — eight of Polish's nine special letters decompose into a base letter and a mark, and `ł` does not, because a stroke through a letter is not a combining mark, so `Łódź` stays out at the end while `ó` and `ż` get filed correctly. It is **not a total order** — `Ćma` and `Cma` get the same key, so their order is whatever order they arrived in, and shuffling the input changes the output. And where it *works*, it has hard-coded English: filing `ó` next to `o` is right in English and wrong in Polish, where `ó` is a letter with its own place after `o`. Those decomposition facts are safe to build on, incidentally, in a way most Unicode data is not: canonical decompositions are frozen by Unicode's stability policy, so `ł` will not start decomposing in a later release.

**Section 5 builds the real shape out of one string.** A toy two-level collation — primary weight from a declared alphabet, secondary from case — gets Polish right for this list in about thirty lines, and the only thing it knows that `sorted()` does not is the alphabet, written out in order. That is what a locale *is*, and shipping it for every language is what CLDR and ICU are. What the toy has no room for is the rest: contractions (Czech `ch` is one letter, after `h`), expansions (`ß` weighs as `ss`), and **variable weighting** — whether a space or a hyphen counts at all before the letters are compared. Nobody thinks about the last one. It is the rule that moved in glibc 2.28.

## One list, five correct answers

Nine words, five locales, measured through `locale.strxfrm` on three C libraries eight years apart:

```text title="Measured 2026-09-07 — macOS 26.6.2 (Darwin libc), glibc 2.39 (ubuntu:24.04) and glibc 2.27 (ubuntu:18.04). All three produced these rows byte for byte identically."
  code points    Aalborg  Azur  Osa  Zebra  chata  hrad  index  Óda  Öland
  en_US          Aalborg  Azur  chata  hrad  index  Óda  Öland  Osa  Zebra
  pl_PL          Aalborg  Azur  chata  hrad  index  Öland  Osa  Óda  Zebra
  cs_CZ          Aalborg  Azur  hrad  chata  index  Óda  Öland  Osa  Zebra
  sv_SE          Aalborg  Azur  chata  hrad  index  Óda  Osa  Zebra  Öland
  da_DK          Azur  chata  hrad  index  Óda  Osa  Zebra  Öland  Aalborg
```

Five orders, and each is the only acceptable one to the people who use it:

- **English** treats an accent as a small difference on a base letter, so `Óda` files with `O`, before `Osa` on the second letter.
- **Polish** treats `ó` as a **letter**, with its own place immediately after `o` — so `Osa` comes before `Óda`, the opposite of English, and the two lists differ by one swap that looks like a bug from either side.
- **Czech** sorts `ch` as **one letter**, after `h` — so `hrad` comes before `chata`, which no per-character comparison can produce.
- **Swedish** puts `Ö` **after `Z`**, at the end of the alphabet rather than beside `O`.
- **Danish** does the same with `Å`, and reads `Aa` as a way of spelling it — so `Aalborg` moves from the very front of the list to the very back.

The thing worth noticing is what did **not** vary. Three C libraries, two operating systems, eight years, and the letter rules are identical — which is the opposite of the usual result in this library, where [`tr`, `paste`, `od`, `grep` and `base64` all disagree across the same two platforms](../../CONTRIBUTING.md). Collation data is shared: glibc took its ordering from ISO 14651 and macOS's derives from the same CLDR-shaped source, so on letters they have converged. The disagreements are in the punctuation, which is the next section, and that is the reverse of where anybody looks.

## The change that invalidated indexes: glibc 2.28

**glibc 2.28 was released on 2018-08-01, and its release notes record a locale-data update to match the 2016 edition of ISO 14651 — bringing it in line with Unicode 9.0.0** ([glibc bug #14095 ↗](https://sourceware.org/bugzilla/show_bug.cgi?id=14095) is the work). Roughly eighteen years of accumulated changes landed in one release. It reached ordinary machines fast: Ubuntu 18.10 and later, Debian 10, RHEL/Rocky/Alma 8 and later, and SLE 15 SP3, per [the PostgreSQL wiki's page on the change ↗](https://wiki.postgresql.org/wiki/Locale_data_changes).

Here is what it did, in four strings under one locale name:

```text title="Measured 2026-09-07 under LC_ALL=en_US.UTF-8 on glibc 2.27 (ubuntu:18.04), glibc 2.39 (ubuntu:24.04) and macOS 26.6.2 — twice, through Python's locale.strxfrm and through sort(1), which agreed on every row"
  glibc 2.27     aa  ab  a b  a-b        strcoll('a-b','ab')  ->  a-b > ab
  glibc 2.39     aa  a b  a-b  ab        strcoll('a-b','ab')  ->  a-b < ab
  macOS 26.6.2   a b  a-b  aa  ab        strcoll('a-b','ab')  ->  a-b < ab

  and for comparison, all three under LC_ALL=C
                 a b  a-b  aa  ab
```

Same four strings, same locale name, three different orders — and the comparison of `a-b` against `ab` **changed sign** across the glibc upgrade. glibc 2.27 sorted punctuation *after* the letters; 2.39 makes it ignorable at the first level, so the strings compare as though it were not there and then tie-break below; macOS puts it *before* the letters, which for these four happens to coincide with byte order. Nothing about any of that is a bug. It is a data file being corrected, and a corrected data file is a different function.

It is worth running the same four strings through `sort` yourself, because the second measurement is what rules out "this is a Python thing": `LC_ALL=en_US.UTF-8 sort` reproduced all three rows exactly, and `LC_ALL=C sort` gave the same single answer everywhere. Which is the practical rule for a script — **`LC_ALL=C` is the only ordering you can depend on across machines**, and it is the one that is wrong for every human reader.

**Why that matters more than a wrong-looking list.** A B-tree index is a structure whose *invariant is the sort order*. PostgreSQL sorted the rows once, at insert time, using the collation the operating system provided then; the index records the resulting positions, not the rule. Change the rule underneath and the tree is still a tree, still passes every structural check, and no longer answers questions correctly. PostgreSQL's own documentation is blunt about the mechanism — a change in collation definitions can lead to **corrupt indexes**, because the system relies on stored objects having a particular order — and the wiki page above spells out the three symptoms: a query can fail to find data that is there, an update can insert a duplicate that should have been disallowed, and on a partitioned table a query can look in the wrong partition while an update writes to it.

None of those three announces itself. Every one is a correct-looking answer to a query that ran without error.

**And for two years nothing said a word.** PostgreSQL **10** had added ICU as an optional collation provider, and its release notes give ICU's own versioning — which allows a collation change to be *detected* — as part of the reason; the default stayed the operating system's library, which had no such handle. Detection for that default arrived in **PostgreSQL 13**, released 2020-09-24, whose release notes describe using the glibc version as a collation version identifier and warning about possible corruption of collation-dependent indexes when it changes. glibc 2.28 shipped in August 2018. So for the two years between them the failure mode was: upgrade the OS, restart the database, get no message of any kind, and run a subtly wrong index until somebody noticed a missing row. On a modern server the warning reads:

```text title="PostgreSQL's collation version mismatch warning, quoted from the ALTER COLLATION documentation"
WARNING:  collation "xx-x-icu" has version mismatch
DETAIL:  The collation in the database was created using version 1.2.3.4, but the operating system provides version 2.3.4.5.
HINT:  Rebuild all objects affected by this collation and run ALTER COLLATION pg_catalog."xx-x-icu" REFRESH VERSION, ...
```

The remedy is what the wiki says it is: `REINDEX` every index over `text`, `varchar`, `char` and `citext` before the upgraded instance takes traffic, then `ALTER COLLATION … REFRESH VERSION` to clear the warning. The lesson for this library is one line and it is not about databases: **an encoding is a fact about bytes and a collation is a versioned data file, so anything you persist in collated order has a dependency on a version you did not write down.**

## Correct is not the same as repeatable

Everything above is about *which* order. This is about whether there is one, and it is a separate failure that survives getting the locale entirely right. UTS #10 gives it [an appendix ↗](https://www.unicode.org/reports/tr10/#Deterministic_Sorting), opening with the note that the confusion here "often leads people to make mistakes in their software architecture". Three things wear the same two adjectives:

| | a property of | what it promises |
|---|---|---|
| **stable sort** | the sort **algorithm** | equal elements come out in the order they went in |
| **deterministic sort** | the sort **algorithm** | the same input gives the same output every time |
| **deterministic comparison** | the **comparison function** | strings that are not identical never compare equal |

A stable sort is always deterministic; a deterministic sort need not be stable; and neither is affected in the slightest by which comparison you hand it. Python's `sorted` is stable, `sort -s` is stable, Rust's `slice::sort` is stable — and none of that is the guarantee wanted here, for a reason that takes one line to state.

**A collation exists in order to ignore things.** That is the job: ignore case until L3, ignore accents until L2, ignore a joiner at every level. So a collation *manufactures ties*, on purpose, between strings that are not equal — the `[.0000.0000.0000]` rows above are the standard undertaking to do exactly that. And a stable sort's promise about a tie is that the elements keep the order they arrived in, which is not an order at all; it is a restatement of the input. Feed the same two rows in the other order and the output changes, from the same correct collation and the same stable sort:

```text
a = 'Davis'                        b = 'Da\u200dvis'        the same name, plus a joiner

sorted([a, b], key=collate)   ->   ['Davis', 'Da<U+200D>vis']
sorted([b, a], key=collate)   ->   ['Da<U+200D>vis', 'Davis']
```

Nothing there is broken, which is what makes it expensive. The trick in section 4 above produced the same shape and could be dismissed as a bad key — `Ćma` and `Cma` tying is a flaw in something home-made. This is the *specified* algorithm doing what it is specified to do, and no amount of getting the locale right removes it.

**The fix is in the standard and it is one line.** A.3.2 gives it as pseudo-code: when the collation returns equal, fall through to a binary comparison of the strings themselves. As a sort key that is a tuple:

```python
key=lambda s: (collate(s), s)   # UTS #10 A.3.2, spelled as a Python sort key
```

The tie-break has to be the **raw code points** rather than a second collation, because code point order is the one ordering no locale tailors, no library version rewrites and no platform implements differently — the only part of this whole subject that survived the previous two sections unscathed.

**And the standard's own objection, which is worth carrying with the fix.** A.3.1 is titled *Avoid Deterministic Comparisons* and gives three reasons: the sort key roughly doubles in size, which a database pays for in memory and on disk; it does not make a non-deterministic *sort* deterministic, because that was never a property of the comparison; and the order it produces is decided by differences nobody can see — above, `Davis` now precedes `Da<U+200D>vis` because of a character no font draws. That order is not *meaningful*. It is only *the same every time*, which is the entire trade:

| what breaks without it | how it looks when it breaks |
|---|---|
| `LIMIT`/`OFFSET` pagination | a row on two consecutive pages and another on neither — no error, no duplicate key |
| a nightly export diffed against yesterday's | a diff full of moved lines nobody edited |
| a test that sorts before asserting | green locally, red in CI, green on the re-run |
| `sort -u`, or `SELECT DISTINCT` | a row dropped that was not a duplicate, and the input order picks which |
| a cache keyed on a sorted list | two keys for one query |

**Where a unique field is in reach, use that instead.** A.1.1 says so plainly: append the primary key, the row id, a sequence number. That is deterministic *and* meaningful, costs nothing in key size, and is the reason `ORDER BY name, id` is the form to write in SQL and `sort -k2,2 -k1,1` the form to write in a pipeline. Keep the code point tie-break for when there is no such field — a list of strings and nothing else.

### The comparison in three levels, and the tie that breaks it

<!-- output:sorting_and_collation_levels_py -->
*Verified output of [`sorting_and_collation_levels_py.py`](examples/sorting_and_collation_levels_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THREE KEYS, COMPARED IN ORDER -- UTS #10 TABLE 2, REPRODUCED
------------------------------------------------------------------------
   L1  primary    base letters  role < roles < rule
   L2  secondary  accents       role < rôle < roles
   L3  tertiary   case          role < Role < rôle

   And the key itself, for the four words those three rows are built
   from. Read down the columns rather than across:
     role   L1 'role'    L2 ('', '', '', '')                         L3 (0, 0, 0, 0)
     roles  L1 'roles'   L2 ('', '', '', '', '')                     L3 (0, 0, 0, 0, 0)
     rôle   L1 'role'    L2 ('', '<U+0302>', '', '')                 L3 (0, 0, 0, 0)
     Role   L1 'role'    L2 ('', '', '', '')                         L3 (1, 0, 0, 0)

   L1 is the word with its accents and its case taken away. L2 is where
   the accents went. L3 is where the case went. Nothing was discarded
   and nothing was added up -- the string was taken apart into three
   answers, and a comparison consults them in that order.

2. A LOWER LEVEL IS NOT A SMALLER VOTE. IT IS A LATER QUESTION
------------------------------------------------------------------------
   role   vs rule    decided at L1   (different base letters)
   role   vs rôle    decided at L2   (same letters, one accent)
   role   vs Role    decided at L3   (same letters, same accents, one capital)
   rôle   vs roles   decided at L1   (an accent AND a base-letter difference)

   The last row is the one to stare at. `rôle` carries an accent and
   `roles` does not, and the accent never gets a vote: the base letters
   already differ, so L1 answers and the comparison stops. Levels are
   not weights in a sum -- each is a question asked only when every
   question above it came back equal. That is why 'this locale cares
   more about accents' is never the right description of a difference
   between two locales; what differs is which level a character's
   difference lands on.

3. AND THE CASE WHERE ALL THREE SAY NOTHING
------------------------------------------------------------------------
   a = Davis
   b = Da<U+200D>vis      the same name, plus one zero-width joiner
   a == b                     False
   sort_key(a) == sort_key(b) True
   The joiner is a request about rendering, so a collation is right to
   ignore it at every level -- and two strings that are not equal now
   compare equal. That is not a defect. A collation exists in order to
   ignore things: case at L1 and L2, accents at L1, a format character
   everywhere. Ignoring anything means making ties on purpose.

   So ask the same question twice, changing only the input order:
     sorted([a, b], key=sort_key)  ->  ['Davis', 'Da<U+200D>vis']
     sorted([b, a], key=sort_key)  ->  ['Da<U+200D>vis', 'Davis']

   Same two strings, same key, two answers. Python's sorted() is STABLE,
   which is exactly the mechanism: stability promises that equal
   elements keep the order they arrived in, so the arrival order is
   what you are reading back. Stability is a property of the sort
   ALGORITHM and says nothing at all about the comparison -- which is
   why it cannot rescue this. A list whose input order varies has no
   fixed output order, however stable the sort that produced it.

4. THE FIX, AND THE STANDARD'S OWN OBJECTION TO IT
------------------------------------------------------------------------
   UTS #10 A.3.2, in one line: when the collation says equal, fall
   through to a comparison of the raw strings.
     def det_key(s): return (sort_key(s), s)
     sorted([a, b], key=det_key)  ->  ['Davis', 'Da<U+200D>vis']
     sorted([b, a], key=det_key)  ->  ['Davis', 'Da<U+200D>vis']
   One answer now, whatever order the rows arrive in. The tiebreak has
   to be the raw code points and not a second collation, because code
   point order is the one ordering no locale tailors, no library
   version rewrites and no platform implements differently -- the only
   part of this subject that is the same everywhere.

   And the objection, which is the standard's rather than this page's.
   A.3.1 is titled 'Avoid Deterministic Comparisons' and gives three
   reasons: the sort key roughly doubles in size, which a database pays
   for; it does not make a non-deterministic SORT deterministic,
   because that was never a property of the comparison; and the order
   it produces is decided by differences nobody can see. Above, Davis
   now precedes Da<U+200D>vis because of a character no font draws.
   That order is not MEANINGFUL. It is only the same every time --
   which is the whole trade, and is worth making only when something
   downstream depends on two runs agreeing.

5. WHAT IT COSTS: A ROW ON TWO PAGES AND A ROW ON NONE
------------------------------------------------------------------------
   Six customers, one tie in the middle, three rows to a page.
     page 1  (rows 0-2 of one query)   ['Adams', 'Baker', 'Davis']
     page 2  (rows 3-5 of the next)    ['Davis', 'Evans', 'Foster']
     on both pages                     ['Davis']
     on neither page                   ['Da<U+200D>vis']

   Nothing failed. Both queries were correct and both used the same
   collation; the second one merely saw the two tied rows in the other
   order, which is all a database has to do differently -- a changed
   plan, an updated row, two workers finishing out of order. The
   reader gets one customer twice and never sees the other.

   The same shape reaches further than pagination: a nightly export
   diffed against yesterday's shows moved lines nobody edited, a test
   that sorts before asserting is green locally and red in CI, and
   SELECT DISTINCT or sort -u drops a row that was not a duplicate.

   And where there is a unique field to reach for, reach for it
   instead. UTS #10 A.1.1 says so: appending the primary key, a row
   id or a sequence number is deterministic AND meaningful, and costs
   nothing in key size. It is why `ORDER BY name, id` is the form to
   write. Use the code point tiebreak when there is no such field.
```
<!-- /output -->

### In the terminal

`sort` has been quietly doing half of this for you. When its keys tie it applies a **last-resort comparison** — the whole line, bytewise — which is A.3.2 wired into the tool; `--stable` is the flag that takes it out, which is the opposite of what the name suggests to most people. And where Python's `setlocale` *raises* for a locale nobody has, `sort` accepts it, sorts by bytes and exits 0.

<!-- output:sorting_and_collation_sh -->
*Verified output of [`sorting_and_collation_sh.sh`](examples/sorting_and_collation_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A COLLATION THAT IS NOT INSTALLED IS NOT AN ERROR
------------------------------------------------------------------------

$ LC_ALL=zz_ZZ.UTF-8 sort ./_names.txt 2>/dev/null; echo "exit=$?"
Ant
Zebra
Łodz
Żeromski
exit=0

  bytes written to stderr: 0
  same output as LC_ALL=C: yes
   Byte order, exit 0, and an empty stderr. This is the mirror of what
   Python does with the same request: section 2 of the other example
   shows locale.setlocale RAISING for a locale nobody has, and here the
   shell tool takes it, says nothing, and sorts by bytes. One of those
   two failures you can catch; the other reaches production as a list
   that is merely wrong. A container is where you meet it, because a
   stock image ships no human-language locales at all.

2. sort ALREADY CARRIES A COLLATION, AND -f IS A TOY ONE
------------------------------------------------------------------------
   -f folds case, so 'bravo' and 'Bravo' become EQUAL to the comparison
   without becoming equal as strings. Every real collation does that at
   some level -- it is what ignoring case, or an accent, or a joiner
   means. Here it gives us a tie we can hold still and look at.

$ LC_ALL=C sort -f ./_case.txt | tr '\n' ' '; echo
alpha Bravo bravo 

3. THE TIE-BREAK sort DOES FOR YOU, AND THE FLAG THAT REMOVES IT
------------------------------------------------------------------------
   The same three lines, in two input orders:
     A:  bravo Bravo alpha
     B:  Bravo bravo alpha

     default   A -> alpha Bravo bravo 
     default   B -> alpha Bravo bravo 
     with -s   A -> alpha bravo Bravo 
     with -s   B -> alpha Bravo bravo 

   The default gives ONE answer for both inputs. -s gives two, which is
   backwards from how the flag reads: -s is --stable, and stability is
   the promise that equal lines keep the order they ARRIVED in -- so it
   is the route by which the input order reaches the output.
   Without it, sort applies a LAST-RESORT COMPARISON: when the keys tie
   it compares the whole lines bytewise. That is UTS #10 A.3.2's recipe
   for a deterministic comparison, already wired into the tool, and -s
   is the switch that takes it out.

4. AND -u THROWS AWAY A LINE THAT IS NOT A DUPLICATE
------------------------------------------------------------------------

     -f -u     A -> alpha bravo 
     -f -u     B -> alpha Bravo 

   Three lines in, two out, both times -- and a different survivor each
   time. -u means 'unique according to the comparison', not 'byte
   identical', so a comparison that ignores case makes bravo and Bravo
   one line and the input order picks which one lives. Under a real
   collation the same flag merges rows differing by an accent, a soft
   hyphen or a zero-width joiner nobody can see. SELECT DISTINCT is the
   same statement in the other language.

5. THE SAME THING ON A KEY FIELD, WHICH IS WHERE IT ACTUALLY HAPPENS
------------------------------------------------------------------------

     sort -k2,2       3 a/1 b/2 b/
     sort -k2,2 -s    3 a/2 b/1 b/

   Sorting records on one column is the everyday case, and no locale is
   involved: the two rows whose column 2 is 'b' simply have no order of
   their own. The default breaks the tie on the whole line and gets 1
   before 2; -s keeps the file order and gets 2 before 1. Neither is
   wrong, and only one of them is the same tomorrow if the file is
   regenerated in a different order. Name a second key -- sort -k2,2
   -k1,1 -- and the question does not arise, which is the shell's
   spelling of ORDER BY name, id.
```
<!-- /output -->

## Rust has no collation at all, on purpose

`String` and `&str` compare by their UTF-8 bytes, which for [well-formed UTF-8 is exactly code point order](../../05_Rust/from_utf8_and_lossy/README.md), and no environment variable changes it. There is no `strcoll` in `std` and no plan for one: Rust's position is that a comparison whose answer depends on an ambient setting is worse than a consistent one you can override deliberately — the same argument [PEP 540 ↗](https://peps.python.org/pep-0540/) makes about encodings, reached from the other side.

The price is that the correct answer is simply unavailable in the standard library, and you reach for a crate (`icu_collator`, or `rust_icu`) to get it. That is the same gap ["Handles Unicode" is four questions](../../10_Best_Practices/what_your_language_gives_you/README.md) names when it says most languages' text handling is ICU wearing a hat — and the page that will demonstrate it is ranked but unwritten, as item 34 in [TODO.md](../../TODO.md). Being explicit about the gap is the honest version of what every other language does implicitly, which is to sort correctly only where somebody installed the data.

## If you are coming from Python or ABAP

The Python half is above. The one habit to carry: `key=locale.strxfrm` for a sort, `locale.strcoll` for a single comparison — the key form transforms once per element, the comparator costs a call per comparison — and both are useless unless something set `LC_COLLATE` first, which is a separate variable from the `LC_CTYPE` you probably set.

**ABAP separates the two orders in the statement itself, which is more honest than most languages manage.** A plain `SORT itab BY name` compares the internal representation — binary order, the same class of answer as `sorted()`. `SORT itab BY name AS TEXT` asks for the *text* order instead, and that one is resolved against the current text environment, which `SET LOCALE LANGUAGE` changes. So the two readings of "alphabetical" are two different keywords rather than a hidden setting, and a report that returns different orders in two systems has almost always been written without `AS TEXT` in one of them.

What transfers unchanged is the dependency, not the syntax: `AS TEXT` is only as portable as the locale data the system carries, so the same list can order differently on two application servers, and the order is not a property of the table. Do not persist a sorted order and assume it survives an upgrade — sort at read time, or store an explicit sort key you generate yourself and can version. Verify any locale or code-page setting against the system rather than a document. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

1. Run `locale` and then `printf 'Osa\nÓda\nZebra\nŁódź\n' | sort` in your own shell, then the same pipeline under `LC_ALL=C`. If the two agree, your `LC_COLLATE` is `C` and every `sort` you have ever run in that shell was byte order. ([`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) has the rest of that story.)
2. `locale -a | wc -l` on your machine, then in a container: `docker run --rm ubuntu:24.04 locale -a`. The gap between those two numbers is the gap between where you tested and where it runs.
3. Take a name column out of a system you maintain, sort it with your database and with `sorted()` in Python, and diff the two lists. Every line that moved is a place where the two components disagree about your users' names.
4. If you run PostgreSQL on Linux: `SELECT collname, collversion FROM pg_collation WHERE collversion <> '';` and compare against `pg_database`'s `datcollversion`. If your instance has ever crossed a distribution major version without a `REINDEX`, that is the query that tells you.
5. Export a sorted report twice from the same data, changing only the order the rows are read in, and `diff` the two files. Anything that moves is a tie, and you have just found which rows have one.
6. Without a machine: an overnight job pages through a customer list a thousand rows at a time, writing each page to its own file. One customer turns up in two files and nobody errored. Name which of the three properties in the table above was assumed, which one actually held, and the one-line change that fixes it.

## Practice

**Four pairs, and the one no level can separate.** For each pair, say which of the three levels decides it — L1 base letters, L2 accents, L3 case — before running anything:

```text
role   vs  rule
rôle   vs  roles
role   vs  rôle
role   vs  Role
```

One of those four is not what it looks like. Then the fifth pair, which is the point: `Davis` against `Da\u200dvis` — the same name with a zero-width joiner welded into the middle, which is what a copy-paste out of a rendered document does. Say which level decides *that* one, what `sorted()` gives for `[a, b]` and for `[b, a]`, and why `sorted` being stable does not save you.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:sorting_and_collation_kata_py -->
*Verified output of [`sorting_and_collation_kata_py.py`](examples/sorting_and_collation_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
WHICH LEVEL DECIDES
   role           vs rule           L1     role < rule
   rôle           vs roles          L1     rôle < roles
   role           vs rôle           L2     role < rôle
   role           vs Role           L3     role < Role
   Davis          vs Da<U+200D>vis  none   Davis < Da<U+200D>vis

   Row 2 is the one that catches people. An accent LOOKS like a level-2
   difference, and it is -- but rôle and roles do not have the same base
   letters, so L1 answers first and L2 is never consulted. A level is a
   question asked only when every question above it came back equal.

THE PAIR NO LEVEL DECIDES
   'Davis' == 'Da<U+200D>vis'            -> False
   sort_key equal                       -> True
   U+200D ZERO WIDTH JOINER is a rendering request. A collation is
   right to ignore it -- and two unequal strings now compare equal, so
   their order is not decided by the comparison at all.

   Same key, same two strings, two input orders:
     sorted([a, b]) -> ['Davis', 'Da<U+200D>vis']
     sorted([b, a]) -> ['Da<U+200D>vis', 'Davis']
   Python's sorted() is stable, which is exactly why: stability keeps
   equal elements in the order they arrived, so the arrival order is
   what you are reading. Stability is a property of the sort algorithm;
   it cannot make an order reproducible across two different inputs.

THE ONE-LINE FIX, AND WHAT IT BUYS
   key=lambda s: (sort_key(s), s)      -- UTS #10, Appendix A.3.2
     sorted([a, b]) -> ['Davis', 'Da<U+200D>vis']
     sorted([b, a]) -> ['Davis', 'Da<U+200D>vis']
   One answer, whatever order the rows arrive in. The tiebreak is the
   raw code points, which is the only ordering no locale tailors and no
   library version changes -- so it is the half of the key that is the
   same on every machine and in every year.
   It buys reproducibility and nothing else: Davis now precedes
   Da<U+200D>vis because of a character no font draws. UTS #10 spends
   section A.3.1 arguing you usually do not want this, and it is right
   -- unless something downstream is paginating, diffing or caching the
   order, in which case reproducibility IS the requirement.
```
<!-- /output -->

</details>

## See also

- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — six independent variables, and this page is about a different one
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) — the tool-level version of the same gap
- [Normalization](../../04_Python/normalization/README.md) — equality has the same shape of problem as ordering, with a defined answer
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — where a collation is actually chosen, usually by accident
- ["Handles Unicode" is four questions](../../10_Best_Practices/what_your_language_gives_you/README.md) — which languages ship the data, and which make you install it
- [Sorting is not comparing ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/sorting_is_not_comparing/index.html) — the Python half next door: the hand-written key built out, and the diacritic-stripping shortcut that is right for a search box and wrong for a list
- [A BOM in a CSV](../bom_in_a_csv/README.md) — the completely-ignorable character from the weight table above, met as a column name
- [Two people, one account](../../12_Adversarial/collisions_by_design/README.md) — what happens when the thing being made equal on purpose is a username
