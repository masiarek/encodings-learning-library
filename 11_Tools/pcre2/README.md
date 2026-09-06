# PCRE2 — the other regex engine

**Level:** 201 · for anyone who already reaches for `rg`

**One line:** `rg -P` swaps ripgrep's linear-time engine for PCRE2, which is the only regex engine already installed on your machine that can match a **grapheme cluster** — and the price is that a pattern the default engine would have rejected with a paragraph of advice now matches nothing and says nothing.

## Why it is on this list at all

Every other page in this chapter asks [the same three questions](../README.md) of one tool. This page asks them of one *flag*, because `-P` changes the answer to all three inside a tool you have already chosen:

| | The question | `rg` default engine | `rg -P` (PCRE2) |
|---|---|---|---|
| 1 | bytes or characters? | code points; `--no-unicode` for bytes | **the same** — and it adds a third unit, the grapheme cluster |
| 2 | who decided? | you did, by not passing a flag | you did — or **`--engine=auto` decided for you**, by looking at your pattern |
| 3 | what on a pattern it cannot handle? | refuses it, and names the flag that would help | compiles it, matches nothing, **exit 1** |

Row 3 is the one that costs people an afternoon, and row 1 is the one that earns the page a place in a library about encodings. `\X` is the only way any tool in this chapter can be asked *"how many characters would a person say that is?"* — and [`a_code_point_is_not_a_character`](../../02_Characters/a_code_point_is_not_a_character/README.md) says neither Python's nor Rust's standard library will answer it. `rg -P` will, and you already have it.

## The session

Neither macOS nor Ubuntu ships `rg`, so CI does not have it and **no answer key on this page comes from the tool**. What follows was run twice, on the two machines in the caption, and diffed.

```text title="Measured 2026-09-06 — macOS 26.6 (rg 15.1.0 brew, PCRE2 10.45) and ubuntu:24.04 (rg 14.1.0 apt, PCRE2 10.42). The two runs were diffed and are identical apart from the version line. Not machine-checked: CI has no rg."
$ xxd nfd.txt
  00000000: 6361 6665 cc81 0a                        cafe...

$ rg    -c '^.{5}$' nfd.txt
  1

$ rg -P -c '^.{4}$' nfd.txt
                                          # (nothing — exit 1)

$ rg -P -c '^\X{4}$' nfd.txt
  1

$ rg    -o '\X' nfd.txt
  rg: regex parse error:
      (?:\X)
         ^^
  error: unrecognized escape sequence

$ rg    -o '(?<=caf)e' nfd.txt
  rg: regex parse error:
      (?:(?<=caf)e)
         ^^^^
  error: look-around, including look-ahead and look-behind, is not supported

  Consider enabling PCRE2 with the --pcre2 flag, which can handle backreferences
  and look-around.

$ rg -P -o '(\w)\1' dbl.txt
  aa
  bb

$ rg    'a\nb' ab.txt
  rg: the literal "\n" is not allowed in a regex

  Consider enabling multiline mode with the --multiline flag (or -U for short).
  When multiline mode is enabled, new line characters can be matched.

$ rg -P 'a\nb' ab.txt
                                          # (nothing — exit 1)

$ rg --engine=auto 'a\nb' ab.txt
                                          # (nothing — exit 1)
```

Four things in that session are worth naming.

**1. The file is one word and it has two lengths.** `nfd.txt` holds `café` written the decomposed way — `63 61 66 65 cc 81`, which is `c`, `a`, `f`, `e`, and `U+0301 COMBINING ACUTE ACCENT`. Six bytes, **five code points, four graphemes**. So `^.{5}$` matches under the default engine and `^.{4}$` matches under neither, while `^\X{4}$` matches under PCRE2. Nobody is wrong; a quantifier has to count *something*, and `.` counts code points while `\X` counts what a cursor moves over. Only one of those is what a person means by "four characters".

One word is a modest demonstration. Here is an immodest one — the same three questions asked of a single family emoji:

```text title="Measured 2026-09-06 — macOS 26.6 (rg 15.1.0 brew) and ubuntu:24.04 (rg 14.1.0 apt). Diffed: identical apart from the version line. Not machine-checked: CI has no rg."
$ wc -c < fam.txt
  26
$ rg -o '.'    fam.txt | wc -l
  7
$ rg -P -o '\X' fam.txt | wc -l
  1
```

**26 bytes, 7 code points, 1 character.** That is the whole argument of [a code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) in three commands, and `\X` is what turns the third number from a thing you know into a thing you can compute at a prompt.

**2. The default engine refuses what it cannot do, and names the fix.** `\X`, lookbehind and backreferences all come back as parse errors — and the look-around one ends with *"Consider enabling PCRE2 with the --pcre2 flag"*. That is a refusal you can act on, and it is a deliberate design choice: rg's default engine is a finite automaton with a linear-time guarantee, and those three features are exactly what that guarantee costs.

**3. And then PCRE2 does the one thing the default engine never does — nothing.** `rg 'a\nb'` prints four lines telling you a literal newline is not allowed and naming `-U`. `rg -P 'a\nb'` prints nothing and exits 1, which is **the same thing it prints when the file genuinely does not contain what you asked for**. The mechanism is not mysterious: rg searches a line at a time, a line has no newline in it by definition, so the pattern can compile perfectly and never match. The default engine has enough introspection to see that coming; PCRE2 does not, and rg cannot invent it.

**4. `--engine=auto` inherits the silence, and it inherits it in exactly the wrong case.** Auto's rule is *"use the default engine; if the pattern will not compile there, fall back to PCRE2"*. A pattern with a literal `\n` will not compile in the default engine — so auto swallows the error message and hands you PCRE2's silence. The convenience flag removes the diagnosis precisely when you needed it.

## Where you can even get it

`-P` is not available everywhere, and the split is not the usual BSD/GNU one — it is sharper than that.

| | PCRE2 available? | measured |
|---|---|---|
| `rg -P`, macOS (brew) | **yes** — PCRE2 10.45, JIT | `rg --version` |
| `rg -P`, Ubuntu 24.04 (apt) | **yes** — PCRE2 10.42, JIT | `rg --version` |
| `grep -P`, GNU grep 3.11 (Ubuntu) | **yes** | `printf 'aa\n' \| grep -P '(\w)\1'` → `aa` |
| `grep -P`, BSD grep 2.6.0 (macOS) | **no — there is no such flag** | `grep: invalid option -- P` |
| `pcre2grep` | only if installed | on this Mac via Homebrew; absent from a bare `ubuntu:24.04` |

So on a Mac, `rg -P` is not merely the convenient door to PCRE2 — it is the only one you have without installing something. That is worth knowing before you write a `grep -P` one-liner into a script that has to run on both.

Note also that PCRE2 is an **optional** ripgrep feature. `rg --version` prints a `+pcre2` or `-pcre2` line and then says which PCRE2 it found; a build without it fails `-P` with an error rather than falling back.

## Where the two engines agree

The interesting half of the measurement is how little `-P` changes. On every encoding question put to both engines, on both machines, the answer was the same:

| Asked of both engines | default | `-P` |
|---|---|---|
| `-o caf` on `caf\xe9 latin1` (invalid UTF-8) | `caf` | `caf` |
| `-o 'caf.'` on the same file | no match | no match |
| `-o 'latin'` on the same file | `latin` | `latin` |
| `-o '\w+'` on `żółw` | `żółw` | `żółw` |
| the same with `--no-unicode` | `w` | `w` |
| `-o '\d+'` on `٤٢` and `42` | both | both |
| `-i` `strasse` on `straße` / `STRASSE` | `STRASSE` only | `STRASSE` only |
| `-i k` against `U+212A KELVIN SIGN` | matches | matches |

Two of those are worth a sentence. **Invalid UTF-8 does not upset PCRE2 here** — the obvious guess is that a UTF-mode regex engine would refuse a file it cannot decode, and it does not; ripgrep runs it in a mode that tolerates invalid input, so [the ripgrep page's model](../ripgrep/README.md) holds under `-P` too. And **neither engine folds `ß` to `ss`** while both fold `U+212A` to `k`: that is simple case folding, not full case folding, and it is a property of Unicode's tables rather than of either engine.

So `-P` is not a second opinion about your text. It is a different set of questions you are allowed to ask about it, at a price paid in error messages.

## In Python

The rules above are short enough to apply by hand, which is how this page keeps a machine-checked half — and Python is unusually good for it, because `re` is a backtracking engine like PCRE2 and the `str`/`bytes` split is the same one `--no-unicode` makes.

The honest limit is the ripgrep page's: if `rg` changes, this program keeps passing. It tests the model, not the tool.

<!-- output:pcre2_rules_py -->
*Verified output of [`pcre2_rules_py.py`](examples/pcre2_rules_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
RULE 1. FOUR ANSWERS TO 'HOW LONG IS café'
   NFC  café: UTF-8 bytes                   5
   NFC  café: UTF-16 code units             4
   NFC  café: code points                   4
   NFC  café: grapheme clusters             4
   NFD  cafe+U+0301: UTF-8 bytes            6
   NFD  cafe+U+0301: UTF-16 code units      5
   NFD  cafe+U+0301: code points            5
   NFD  cafe+U+0301: grapheme clusters      4
   NFC(NFD form) is the NFC form?           True
   but the two literals compare equal?      False
   The NFD row is why this page exists. Five code points, four graphemes,
   and a regex quantifier has to mean one or the other. rg's default
   engine counts code points, so '^.{5}$' matches and '^.{4}$' does not;
   PCRE2's \X counts grapheme clusters, so '^\X{4}$' matches. Both are
   right about different questions, and only one of them is the question
   a person asking 'how many characters' means.

RULE 2. A BACKTRACKING ENGINE ACCEPTS PATTERNS AN AUTOMATON REFUSES
   lookbehind '(?<=caf)e' on NFD            True
   backreference r'(\w)\1' on 'aa'          True
   does Python's re have \X?                no -- bad escape \X
   Python's re is backtracking, like PCRE2, so the first two work here and
   in `rg -P`, and rg's default engine rejects both by design: it is a
   finite automaton and guarantees linear time, which those features cost.
   But the third line is the one to read twice. \X is not something you
   get for free by backtracking -- Python backtracks and does not have it.
   It is a feature PCRE2 chose to implement, which is why 'rg -P' can
   count graphemes and no other tool in this chapter can.

RULE 3. A PATTERN CAN COMPILE AND STILL NEVER MATCH
   pattern compiles?                        True
   matches the whole text?                  True
   matches any single LINE?                 False
   Both greps and rg search a line at a time, and a line by definition has
   no newline in it -- so a pattern containing one can never match, however
   well it compiles. That is the whole of 'rg -P "a\nb"' printing nothing.
   rg's default engine refuses the pattern up front and says so in four
   lines, naming the -U flag; PCRE2 compiles it and returns no match, which
   is indistinguishable from the file not containing what you asked for.
   --engine=auto inherits the silence, because 'the default engine could
   not compile it' is exactly its rule for switching to PCRE2.

RULE 4. ON ENCODING QUESTIONS THE TWO ENGINES AGREE
   U+212A is the letter K?                  False
   U+212A lowercases to 'k'?                True
   'żółw' matches ^\w+$ on str              True
   ...and on bytes (the --no-unicode model) False
   '٤٢' matches ^\d+$ on str                True
   Measured on the page: rg's two engines give the same answer to every one
   of these -- same case folding, same Unicode \w and \d, same reduction to
   ASCII under --no-unicode, and the same behaviour on a file of invalid
   UTF-8. So -P is not a different opinion about your text. It is a
   different set of questions you may ask about it, at a different price.
```
<!-- /output -->

## When to reach for which

| You want | Use |
|---|---|
| to count characters the way a person would | `rg -P '\X'` — nothing else in this chapter can |
| look-around or a backreference | `rg -P`, and expect the linear-time guarantee to be gone |
| a search that cannot blow up on a hostile pattern | the default engine — that is what it is for |
| to know *why* your pattern found nothing | the default engine first, always; ask `-P` only once it compiles |
| `grep -P` in a script that runs on macOS too | it does not exist there — use `rg -P` |

The general rule that falls out: **debug with the default engine, then switch.** Its refusals are the best documentation either engine has, and they disappear the moment you pass `-P`.

## If you are coming from Python or ABAP

**Python.** `re` is the PCRE2 side of this page — backtracking, look-around, backreferences, and the same catastrophic-backtracking risk that rg's default engine exists to avoid. Two things do not carry over. `re` has **no `\X`**: grapheme clusters need the third-party `regex` module, so PCRE2 is doing something here that Python's standard library does not. And `re` on a `str` is Unicode mode while `re` on a `bytes` is `--no-unicode` — the same split, spelled as a type rather than a flag, which is [`str` vs `bytes`](../../04_Python/str_vs_bytes/README.md) again.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* `FIND ... REGEX` and `cl_abap_regex` run on a backtracking engine, so the PCRE2 half of this page is the familiar one and the linear-time engine is the unfamiliar one. **Which** engine, and whether your release offers a choice, is a per-release question — check it against your own system rather than against this page. The transferable warning is row 3 of the first table: a regex that compiles and returns `sy-subrc = 4` is telling you *"no match"*, and that answer covers both "not in the data" and "this pattern could never have matched" — distinguish them yourself, because the engine will not.

## Try it

1. Make the decomposed file — `printf 'cafe\xcc\x81\n' > nfd.txt` — and run `rg -c '^.{4}$'`, `rg -c '^.{5}$'` and `rg -P -c '^\X{4}$'` on it. Then run the same three on a composed `café` and watch which answers move.
2. Do the emoji count above on an emoji of your own — a flag, a skin-toned hand, a keycap. Every one of them is a different reason the two numbers differ, and `rg -P -o '\X' | wc -l` gets all of them right.
3. Run `rg 'a\nb' somefile` and then `rg -P 'a\nb' somefile`. Keep the first output; it is the better error message you will not get next time.
4. Run `rg --version` and find the `+pcre2` line. If it says `-pcre2`, none of this page works on your build.

## See also

- [`ripgrep` — the Rust grep](../ripgrep/README.md) — the tool this flag lives inside, and its default engine's whole model
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) — what `\X` is counting, and why the standard libraries stop short of it
- [Normalization](../../04_Python/normalization/README.md) — where the `e` + `U+0301` spelling of café comes from in the first place, and why you meet it without asking
- [`grep` on text that is not ASCII](../grep/README.md) — the tool whose `-P` you cannot use on a Mac
