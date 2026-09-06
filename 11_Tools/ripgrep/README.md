# `ripgrep` — the Rust grep

**Level:** 201 · for anyone who already reaches for `rg`

**One line:** `rg` is one implementation on every platform with no locale to consult, so it gives the same answer on a Mac and on a Linux box — and it is the only common search tool that will read a UTF-16 file, because it looks at the byte-order mark before it searches.

## Why it is on this list at all

[RESOURCES.md](../../RESOURCES.md) says `rg` is "a fast grep" and not about encodings. That is true about why people install it and wrong about what it does. Speed is the reason it spread; the decisions on this page are what you actually get, and three of them are ones [`grep`](../grep/README.md) gets differently or not at all:

| | `grep` | `rg` |
|---|---|---|
| what is a character? | whatever the **locale** says | always a **UTF-8 character**; `--no-unicode` for bytes |
| a UTF-16 file? | invisible — searches bytes, finds nothing | **reads the BOM and transcodes** |
| an undecodable byte? | BSD **drops the line**; GNU keeps it | keeps the line; no Unicode class matches the byte |
| a NUL? | "binary file matches" | "binary file matches (found `\0` byte around offset 5)" |
| BSD vs GNU split? | [seven found so far](../../CONTRIBUTING.md) | none — one codebase, same binary behaviour |

The last row is the quiet one. Every other page in this library has to say *"measured on two machines, and here is where they disagree"*. On `rg` the two machines agree, byte for byte, which is what a single implementation buys you.

## The session

Neither macOS nor Ubuntu ships `rg`, so CI does not have it and **no answer key on this page comes from the tool**. What follows was run twice, on the two machines in the caption, and diffed: identical apart from the version line.

```text title="Measured 2026-09-06 — macOS 26.6 (rg 15.1.0, brew) and ubuntu:24.04 (rg 14.1.0, apt). The two runs were diffed and are identical. Not machine-checked: CI has no rg."
$ rg caf u16.txt                       # UTF-16LE with a BOM
  café

$ grep -a caf u16.txt                  # the same file, the same word
                                       # (nothing — exit 1)

$ rg caf latin1.txt                    # café in Latin-1: 63 61 66 e9 …
  caf� latin1

$ rg 'caf.' latin1.txt
                                       # (nothing — exit 1)

$ rg -E latin1 'café' latin1.txt
  café latin1

$ rg hello withnul.txt
  binary file matches (found "\0" byte around offset 5)

$ rg line invalid.txt                  # the file BSD grep loses a line from
  good line
  bad �� line
  last line

$ rg -i 'żółw' pol.txt                 # the file holds ŻÓŁW and żółw
  ŻÓŁW
  żółw

$ rg -c '^\w+$' pol.txt
  2

$ rg -c --no-unicode '^\w+$' pol.txt
                                       # (nothing — exit 1)
```

Six things in that session are worth naming.

**1. The first two commands are the headline.** One file, one word, two tools: `rg` prints it and `grep` cannot see it. `rg` reads the first bytes, finds `FF FE`, decodes UTF-16LE, and searches the text. `grep` searches the bytes, where `caf` is spelled `63 00 61 00 66 00`, and correctly reports no match. Neither is buggy; they are answering different questions, and only one of them is the question you asked. Without the mark `rg` finds nothing either, and you have to say `rg -E utf-16le`.

**2. The `�` in `caf� latin1` is your terminal, not `rg`.** Piping that line through `xxd -p` gives `636166e9206c6174696e310a` — the original `e9`, untouched. `rg` passed the bytes through and the terminal, asked to draw a byte that is not valid UTF-8, drew the replacement character. This is the same trap as [`od -a`'s question marks](../../06_Terminal/inspecting_a_file/README.md): what you are reading is the last program in the pipe, not the file. Nothing decoded that byte and nothing replaced it.

**3. `caf` matches and `caf.` does not.** `caf` is three ASCII bytes and they are present. `caf.` needs `.` to match the fourth position, and `.` in Unicode mode means *one character* — there is no character at that byte, so no match. That is `rg`'s whole model for invalid input: **it is skipped by anything Unicode-aware and seen by anything byte-oriented**, and `--no-unicode` (or an inline `(?-u)`) is how you ask for the second. Compare `grep`, which in the C locale would have matched, and in a UTF-8 locale on a Mac would have dropped the line entirely.

**4. `-E latin1` changes the output, not just the input.** With the encoding named, the match comes back out of the pipe as **UTF-8** — `c3 a9` where the file has `e9`. So `rg -E` is a search and a transcode in one, which is convenient and is a thing to know before you pipe its output into something that will store it.

**5. The binary notice names the offset.** `found "\0" byte around offset 5` is a diagnosis where the two greps give a refusal, and it is actionable: `xxd -s 0 -l 16 withnul.txt` shows you what is there. `rg -a` searches anyway, exactly like `grep -a`.

**6. `\w` is Unicode by default.** `^\w+$` matches `ŻÓŁW` and `żółw`; `--no-unicode` matches neither, because in byte mode `\w` is `[0-9A-Za-z_]` and those words are not spelled in it. Likewise `-i` case-folds `żółw` to `ŻÓŁW` — four characters, four case mappings, none of them ASCII. This is the one place `rg` is doing *more* than `grep` rather than something different, and it is the reason to leave Unicode mode on unless you have a byte question.

## In Python

The rules above are short enough to apply by hand, which is how this page keeps a machine-checked half. Each section states one of `rg`'s rules, applies it to the same file `rg` was measured on, and prints the answer `rg` gave — `11` and `10` for the byte and character counts, `False` then `True` for the UTF-16 search, three lines in and three lines out.

The honest limit: if `rg` ever changes, this program will keep passing. It tests the model, not the tool. That is why the session above is dated and names its machines.

<!-- output:ripgrep_rules_py -->
*Verified output of [`ripgrep_rules_py.py`](examples/ripgrep_rules_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
RULE 1. A BOM NAMES THE ENCODING, AND IS ACTED ON
   utf-16le + BOM: sniffed                utf-16-le
   utf-16le + BOM: 'caf' in the BYTES     False
   utf-16le + BOM: 'caf' after decoding   True
   utf-8, no BOM: sniffed                 (nothing — assume UTF-8)
   utf-8, no BOM: 'caf' in the BYTES      True
   utf-8, no BOM: 'caf' after decoding    True
   The first file answers False then True: the word is present and the
   bytes do not contain it. That gap is the whole difference between
   grep and rg on this file — rg looks at the first two bytes, decodes,
   and searches the text. grep searches the bytes and finds nothing.
   Note the sniff order: UTF-32LE's mark ff fe 00 00 STARTS with UTF-16LE's
   ff fe, so a shorter-first sniffer reads every UTF-32LE file as UTF-16.

RULE 2. NO BOM: SEARCH THE RAW BYTES, AND A UNICODE CLASS SKIPS
         WHAT IT CANNOT DECODE
   latin-1 bytes                          636166e9206c6174696e310a
   bytes that are not a newline           11
   of those, decodable characters         10
   b'caf' present in the raw bytes        True
   the e9 became U+FFFD?                  False
   Eleven and ten. The e9 is a byte that no character class can match,
   because there is no character there to match — and it did NOT become
   U+FFFD, which is the mistake to avoid: nothing decoded it, nothing
   replaced it, it is simply skipped by anything Unicode-aware and seen
   by anything byte-oriented. Those are rg's two modes: '.' matches ten,
   and '(?-u).' or --no-unicode matches eleven.
   So 'caf' matches (three ASCII bytes, present as bytes) and 'caf.' does
   not (the fourth position is not a character). Naming the encoding is
   the only real fix; rg spells it -E latin1, and then it re-encodes what
   it prints, so the match comes back out of the pipe as UTF-8.

RULE 3. A NUL MEANS BINARY — AND SAY WHERE IT WAS
   first NUL at offset                    5
   lines containing 'hello'               2
   Both greps and rg agree that one NUL reclassifies the file. They
   differ in what they tell you: the two greps name the file, rg names
   the file AND the offset — 'found "\0" byte around offset 5' — which
   is the difference between a refusal and a diagnosis. You now know
   where to look, and xxd -s 0 -l 16 will show you.

RULE 4. INVALID BYTES DO NOT REMOVE A LINE
   lines in the file                      3
   lines after decoding the bad bytes     3
   lines containing 'line'                3
   Three, three, three. Whatever you do with the two bad bytes — keep
   them, replace them, refuse to look at them — the LINE is still there
   and is still searched. That is the rule rg follows and the rule BSD
   grep does not: measured on the grep page, the same file loses a line
   in a UTF-8 locale and grep still exits 0. A line is a run of bytes
   between newlines, and no decoding question changes where they are.
```
<!-- /output -->

## When to reach for which

| You want | Use |
|---|---|
| to search a file whose encoding you do not know | `LC_ALL=C grep -a` — a pure byte matcher that skips nothing |
| to search a UTF-16 or BOM-marked file | `rg`, or `iconv` then `grep` |
| to search a known 8-bit table | `rg -E latin1` (and know it re-encodes the output) |
| a search that behaves the same on every machine | `rg` |
| a search on a machine you cannot install anything on | `grep`, and read [its page](../grep/README.md) first |
| to search bytes, not characters | `rg --no-unicode`, or `LC_ALL=C grep` |

One more difference that is not about encodings but will bite you the first week: **`rg` respects `.gitignore` and skips hidden files**, so `rg pattern` and `grep -r pattern .` can return different sets of files for reasons that have nothing to do with the pattern. `rg -uuu` turns all of that off and is the honest comparison.

## Installing it

```bash
brew install ripgrep        # macOS — the binary is called rg
sudo apt install ripgrep    # Ubuntu 24.04 ships 14.1.0
```

It is a single static binary written in Rust, which is also why there is no BSD/GNU split to document: there is one implementation, and `cargo install ripgrep` builds the same one everywhere.

## If you are coming from Python or ABAP

**Python**: `rg`'s default is `re` on a `str` — Unicode classes, characters not bytes — and `--no-unicode` is `re` on a `bytes`. The BOM sniff is `open(path, encoding='utf-8-sig')` generalised to four marks, and `-E latin1` is `open(path, encoding='latin-1')`. The one behaviour with no clean Python equivalent is what `rg` does with an undecodable byte in the middle of an otherwise valid file: it neither raises nor replaces, it just makes that position unmatchable — closest is `errors='surrogateescape'`, where the byte survives as a lone surrogate that no ordinary character class matches either.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* There is no `rg` here, and the model to carry over is the `-E` one: name the code page at the boundary. `cl_abap_conv_in_ce=>create( encoding = '1100' )` is `rg -E latin1`, and the same warning applies — what comes out is in the system's internal representation, not the file's, so a value you read with one code page and write back with the default has been transcoded whether or not you meant it. Verify any code-page number against the system before relying on it.

## Try it

1. Make a UTF-16 file — `printf 'café\n' | iconv -f UTF-8 -t UTF-16 > u16.txt` — and search it with `grep`, then with `rg`. Then strip the first two bytes with `tail -c +3` and try `rg` again.
2. Run `rg -o . f | wc -l` and `rg -o --no-unicode . f | wc -l` on a file with accented text. The difference is the number of continuation bytes.
3. Run `rg something` in a repo, then `rg -uuu something`. Count the extra files. That gap is `.gitignore`, not encoding — but it is the other reason `rg` and `grep` disagree.
4. Pipe `rg` output for a Latin-1 file through `xxd -p` and confirm for yourself that the `�` you saw was never in the stream.

## See also

- [`grep` on text that is not ASCII](../grep/README.md) — the tool this one is measured against
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — the four marks `rg` sniffs for, and why the order of the check matters
- [`String` is bytes that promise UTF-8](../../05_Rust/string_is_bytes_that_promise_utf8/README.md) — the Rust type that makes `rg`'s "no character there" the natural answer
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — why the `�` was drawn by your terminal
