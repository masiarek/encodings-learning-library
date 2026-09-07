# `--pre` and `-z` — decompress, then decode

**Level:** 201 · for anyone who already reaches for `rg`

**One line:** `-z` and `--pre` add a stage *before* everything else ripgrep does — a `.gz` gets decompressed, a PDF gets converted — and then the encoding machinery runs on the result exactly as it always did, which is why a UTF-32 file is still unreadable through gzip, and why `--pre` is how you finally read it.

> **Two pages, two halves.** The *how* of `--pre` — `--pre-glob`, the shell wrapper, what it costs over a hundred PDFs — is [rg — the menu](../../RIPGREP.md) and [the file whose text is not there](../ripgrep/README.md#the-file-whose-text-is-not-there). The `pdftotext` shim itself is shown [in the session below](#the-session) as well, generated from the one file all three pages share, because the contrast with this page's own preprocessor is the fastest way to see what `--pre` actually is. This page is the other half: what these two flags do to the **encoding** stage, how each of them decides whether to run at all, and how each of them fails.

## Why it is on this list at all

These two flags look like conveniences and are really a **pipeline seam**. Put through [the chapter's three questions](../README.md), they answer in a way no other page here does:

| | The question | `-z` | `--pre` |
|---|---|---|---|
| 1 | bytes or characters? | neither — it runs **before** that decision, and does not touch it | the same, except that *you* choose what bytes arrive |
| 2 | who decided? | the **file extension**, not the file's contents | you did, in a shell script |
| 3 | what when it cannot? | **silently searches the file uncompressed**, exit 0 or 1 | names the file, names the command, reproduces its stderr, exit 2 |

Row 3 holds both extremes in this chapter in one page: the loudest diagnostic ripgrep prints anywhere, and a fallback that answers your question without mentioning that it could not do what you asked.

## The session

Neither macOS nor Ubuntu ships `rg`, so CI does not have it and **no answer key on this page comes from the tool**. What follows was run twice, on the two machines in the caption, and diffed.

```text title="Measured 2026-09-06 — macOS 26.6 (rg 15.1.0, brew) and ubuntu:24.04 (rg 14.1.0, apt). The two runs were diffed and are identical apart from the version line. Not machine-checked: CI has no rg."
# one stage before the encoding stage — and the encoding stage is unchanged
$ rg -z -o 'café' plain.txt.gz
  café

$ rg -z -o 'café' u16.txt.gz
  café

$ rg -z -o 'café' u32.txt.gz
                                            # (nothing — exit 1)

$ rg -z -E latin1 -o 'café' l1.txt.gz
  café

# -z reads the NAME, not the bytes
$ rg -z -o 'café' notgz.txt
                                            # (nothing — exit 1)

$ xxd notgz.txt | head -1
  00000000: 1f8b 0800 0000 0000 0003 4b4e 4c3b bc52  ..........KNL;.R

$ file -b --mime-type notgz.txt
  application/gzip

# --pre: the escape hatch, and the gap it closes
$ rg -o 'café' u32.txt
                                            # (nothing — exit 1)

$ rg --pre ./pre.sh -o 'café' u32.txt
  café

# they override each other, and the LAST one wins
$ rg --pre ./pre.sh -z -o 'café' plain.txt.gz
  café

$ rg -z --pre ./pre.sh -o 'café' plain.txt.gz
                                            # (nothing — exit 1)

# the two failure shapes
$ rg --pre ./fail.sh -o 'café' plain.txt
  rg: plain.txt: preprocessor command failed: '"./fail.sh" "plain.txt"':
  -------------------------------------------------------------------------------
  cannot read plain.txt
  -------------------------------------------------------------------------------

$ PATH=<only rg> rg -z -o 'café' plain.txt.gz
                                            # (nothing — exit 1)
  # rg exit=1

$ PATH=<only rg> rg -z --debug ... 2>&1 | grep falling
  error spawning command '"gzip" "-d" "-c" "plain.txt.gz"': No such file or directory (os error 2) (falling back to uncompressed reader)
```

`pre.sh` above is this file, and it is the whole of `--pre`:

<!-- source:pre_iconv_shim_sh -->
*[`pre_iconv_shim_sh.sh`](examples/pre_iconv_shim_sh.sh) in full — pasted here by `tools/run_examples.py` from the file CI runs.*

```bash
#!/bin/sh
# A ripgrep --pre preprocessor that lifts an ENCODING ceiling rather than a
# format one: it hands rg a UTF-8 rendering of a UTF-32LE file, which is an
# encoding rg's own -E flag has no name for and its BOM sniffer misreads.
#
#     rg --pre <this file> PATTERN .
#
# Same contract as any other preprocessor: rg runs it once per file searched,
# passes the filename as $1, and reads this program's stdout instead of the
# file. Anything that is not matched by the first branch is passed through
# untouched, so every other file searches exactly as it would have.
#
# Dispatching on the NAME is the cheap choice and is what this page's session
# measured. Dispatching on content -- `case $(file -b "$1") in ...` -- is the
# honest one, and is what you want if the names cannot be trusted.
#
# Run with no arguments it explains itself, which is also how CI checks that
# the copy printed on the page is the copy in this file.
case "$1" in
    "")     echo "usage: rg --pre $(basename "$0") PATTERN ." ;;
    *u32*)  exec iconv -f UTF-32LE -t UTF-8 "$1" ;;
    *)      exec cat "$1" ;;
esac
```
<!-- /source -->

That one lifts an **encoding** ceiling: `iconv` reads a UTF-32 file that `rg -E` has no name for. The other job `--pre` does is to lift a **format** ceiling, and the shape is identical — same hook, same one-argument contract, a different command in the middle:

<!-- source:rg_pre_shim_sh -->
*[`rg_pre_shim_sh.sh`](../ripgrep/examples/rg_pre_shim_sh.sh) in full — pasted here by `tools/run_examples.py` from the file CI runs.*

```bash
#!/bin/sh
# A ripgrep --pre preprocessor: make PDFs searchable by piping them through
# pdftotext. rg runs this once per file, hands it the filename as $1, and reads
# this program's stdout instead of the file itself. Anything that is not a PDF
# is passed through untouched, so the search result is the same as without it.
#
#     rg --pre <this file> --pre-glob '*.pdf' PATTERN .
#
# --pre-glob is not optional in practice: without it, every file in the search
# pays for a spawned process, not just the PDFs.
#
# Run with no arguments it explains itself, which is also how CI verifies that
# the copy printed on the page is the copy in this file.
case "$1" in
    "")          echo "usage: rg --pre $0 --pre-glob '*.pdf' PATTERN ." ;;
    *.pdf|*.PDF) exec pdftotext -q "$1" - ;;
    *)           exec cat "$1" ;;
esac
```
<!-- /source -->

Side by side they make the point better than either does alone. `--pre` knows nothing about PDFs and nothing about UTF-32. It knows how to hand a command one filename and read its stdout; everything else is a decision you made. What to *do* with the second one — `--pre-glob`, the shell wrapper, what it costs across a folder of a hundred PDFs — is on [rg — the menu](../../RIPGREP.md#searching-pdfs).

Five things in that session are worth naming.

**1. The four `-z` lines are one claim: decompression happens first, and changes nothing after it.** A UTF-16 file with a BOM is still sniffed and transcoded through gzip. A Latin-1 file still needs `-E latin1` through gzip, and still gets it. And a **UTF-32 file is still broken** through gzip, in precisely the way [the ripgrep page measures it uncompressed](../ripgrep/README.md#what-rg-does-not-sniff) — `FF FE 00 00` begins with `FF FE`, so it is read as UTF-16 and every letter comes back with a NUL welded to it. Compression is not an encoding, and `-z` does not pretend otherwise; it hands the decompressed bytes to the same sniffer and steps out of the way.

**2. `-z` decides from the file's NAME.** `notgz.txt` starts `1f 8b` — the gzip magic — and `file` says `application/gzip` on the very run where `rg -z` searches it as text and finds nothing. That is a design choice, not a bug: deciding by extension costs nothing, while deciding by content means opening every file in the tree before you know whether to skip it. But it means `-z` is only as good as your naming, and the failure is the quiet kind. If you have files with the right bytes and the wrong names, `--pre` with a `file`-based dispatch is the tool, and the example script in `man rg`'s own `--pre` entry is exactly that — it runs `pdftotext` on a `*.pdf` and otherwise asks `file` what it is holding.

**3. `--pre` is where the encoding ceiling comes off.** `rg -E` can only name encodings ripgrep was built knowing; `--pre` can name anything with a command behind it — `iconv` for the UTF-32 file above, or an SAP export in a code page that is on nobody's list. (For the *other* thing `--pre` is for, reading formats rather than encodings, that is the PDF shim above.) Two rules before you reach for it: it **spawns a process per file searched**, which is what `--pre-glob` is for; and it is **not run on stdin at all**, so `cat u32.txt | rg --pre ./pre.sh …` quietly goes back to finding nothing.

**4. `--pre` and `-z` override each other, and the last one on the command line wins.** Both man-page entries say "this overrides the other", which reads like a contradiction until you see it: `--pre … -z` decompresses, `-z … --pre` runs the preprocessor. If your preprocessor is the one that handles compression, put it last.

**5. The two failure shapes are opposites, and the good one is the loud one.** A preprocessor that exits non-zero gets you the file, the exact command, the child's stderr reproduced between two rules, and **exit 2** — as clear a diagnostic as anything in this chapter. A **missing decompressor** gets you nothing: `rg` falls back to reading the file uncompressed and searches the compressed bytes, and only `--debug` mentions it. Which wrong answer you get depends on how well the file compressed. A small or already-compact payload is stored nearly verbatim, so the search appears to work — measured the same day, a 22-byte file compressed to a 35-byte `.zst` and searched with `zstd` off the PATH reported `binary file matches (found "\0" byte around offset 7)` and **exit 0** — because at that size zstd stores the bytes almost raw, so `café` really was sitting in the "compressed" file at offset 9. A real archive reports no match. One missing binary, two plausible answers, no complaint either way.

## Which decompressors you actually have

`-z` shells out, so its format list is a list of *binaries on your PATH*, not of things ripgrep can do. The man page names gzip, bzip2, xz, LZ4, LZMA, Brotli and Zstd; what that buys you depends entirely on the machine:

| | macOS 26.6 (this Mac) | `ubuntu:24.04`, bare image |
|---|---|---|
| `gzip` | ✓ `/usr/bin/gzip` | ✓ `/usr/bin/gzip` |
| `bzip2` | ✓ `/usr/bin/bzip2` | **absent** |
| `xz` · `lzma` | ✓ (Homebrew) | **absent** |
| `lz4` · `brotli` | ✓ (Homebrew) | **absent** |
| `zstd` | ✓ (Homebrew) | **absent** |

So on a minimal container — a CI runner, a `FROM ubuntu` build stage — `rg -z` handles `.gz` and silently mis-answers everything else. That is worth knowing before you put `rg -z` in a pipeline that runs somewhere other than your laptop.

## In Python

The four rules are short enough to apply by hand, which is how this page keeps a machine-checked half. `gzip`, `zlib` and `pathlib` are enough for all of them — including the fallback, where `zlib.compress(data, 0)` reproduces the "stored almost verbatim" case that makes a missing decompressor look like a working search.

The honest limit is this chapter's usual one: if `rg` changes, this program keeps passing. It tests the model, not the tool.

<!-- output:decompress_then_decode_py -->
*Verified output of [`decompress_then_decode_py.py`](examples/decompress_then_decode_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
RULE 1. TWO STAGES, AND THE SECOND ONE DOES NOT KNOW ABOUT THE FIRST
   utf-8: gzipped to                          31 bytes
   utf-8: 'café' found after decoding         True
   utf-16+BOM: gzipped to                     43 bytes
   utf-16+BOM: 'café' found after decoding    True
   utf-32+BOM: gzipped to                     51 bytes
   utf-32+BOM: 'café' found after decoding    False
   True, True, False -- and the False is not about compression. Decompress
   first, then hand the result to the same sniffer, and a UTF-32 file fails
   exactly the way it fails uncompressed: the mark ff fe 00 00 begins with
   UTF-16LE's ff fe, so it is read as UTF-16 and every letter gets a NUL.
   That is the point of the ordering. -z and --pre are a stage BEFORE the
   encoding stage; they add a step and change nothing about the step after.

RULE 2. THE DETECTOR READS THE NAME; THE MAGIC IS IN THE BYTES
   plain.txt.gz: suffix says gzip?            True
   plain.txt.gz: first two bytes say gzip?    True
   notgz.txt: suffix says gzip?               False
   notgz.txt: first two bytes say gzip?       True
   Identical bytes, two names, two answers. rg -z asks the first question
   and `file` asks the second, which is why `file` can call notgz.txt
   application/gzip on the very run where rg searches it as text. Neither
   is buggy; only one of them opened the file to find out.

RULE 3. AN OFFSET IS INTO THE LAST STREAM, NOT THE FILE
   'utf16' at byte N of the FILE              12
   'utf16' at byte N after decoding           6
   file is this many bytes                    24
   decoded text is this many bytes            12
   Twelve and six. rg -b reports the second, because that is the stream it
   printed from -- and the same applies after -z or --pre, where the file
   on disk may share no bytes at all with what was searched. So a -b offset
   is a position in rg's output, not a `dd skip=` argument, unless nothing
   transformed the input.

RULE 4. THE FALLBACK ANSWERS. IT DOES NOT COMPLAIN
   searching the COMPRESSED bytes, level 0    True
   searching the COMPRESSED bytes, level 9    False
   True then False, from the same query against the same content. When the
   decompressor is missing, rg silently falls back to reading the file
   uncompressed -- and what you get back depends on how well the file
   happened to compress. A small or already-compact payload is stored
   almost verbatim, so the search 'works'; a real one does not, and reports
   no match. Two different wrong answers, one missing binary, and neither
   run says a word about it unless you pass --debug.
```
<!-- /output -->

## When to reach for which

| You want | Use |
|---|---|
| to search `.gz` / `.xz` / `.zst` you control the names of | `rg -z` |
| to search compressed files with the wrong names | `--pre`, dispatching on `file` |
| to search an encoding `rg -E` does not know | `--pre` with `iconv -f … -t UTF-8` |
| to search a PDF or a `.docx` | `--pre` too — but [that half is written up elsewhere](../../RIPGREP.md) |
| to be *told* when the stage before the search failed | `--pre` — it says so; `-z` does not |
| to know why `rg -z` found nothing | `--debug`, and read for `falling back` |

The rule of thumb: **`-z` is the convenience and `--pre` is the contract.** `-z` is one letter and guesses from the name; `--pre` is a script you wrote, fails loudly when it fails, and can do anything a command can do.

## If you are coming from Python or ABAP

**Python.** This is `gzip.open(path, 'rt', encoding='utf-8')` pulled apart into its two halves, and the page is an argument for keeping them apart. `gzip.open` in text mode does exactly what `rg -z` does — decompress, then decode — and it takes an `encoding=` because *the compression layer has no opinion about it*. The `--pre` model is `subprocess.run([...], stdout=PIPE)` feeding the same decode: any transform you can spawn, with the decode step unchanged behind it.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* The seam is the same one as `cl_abap_gzip` followed by `cl_abap_conv_in_ce`: decompress into an `xstring`, then convert with a code page you name. The transferable rule is that the second step still needs its argument — a payload that arrived compressed is not thereby known to be UTF-8, and the compression class will not tell you. Verify any code-page number against your own system rather than against this page.

## Try it

1. `printf 'café\n' | iconv -t UTF-32LE > u32.txt` then `gzip -k u32.txt`. Search it with `rg -z`, then with `rg -z --pre` and a script that runs `iconv -f UTF-32LE`. Only one of the two finds the word — and note which flag has to come last.
2. Rename a `.gz` to `.txt` and run `rg -z` on it, then `file -b --mime-type` on the same file. Two tools, one file, two answers about what it is.
3. Take a `.gz` you care about and run `rg -z --debug 'anything' file.gz 2>&1 | grep -i decompress`. On a machine that has `gzip` this says nothing interesting, which is the point: it is the line you will want to have seen on the machine that does not.
4. Compress a two-line file and a two-thousand-line file, then search the raw `.gz` bytes for a word that is in both — `rg -a --no-filename word file.gz`. The short one may well match. That is the fallback's whole failure mode in one command.

## See also

- [rg — the menu](../../RIPGREP.md) — the same two flags from the other side: PDFs, `--pre-glob`, the wrapper, and what it costs
- [`ripgrep` — the Rust grep](../ripgrep/README.md) — the encoding stage this page runs in front of, and the UTF-32 gap `--pre` closes
- [PCRE2 — the other regex engine](../pcre2/README.md) — the other flag that changes ripgrep from the inside
- [`iconv`](../../06_Terminal/iconv/README.md) — the command a `--pre` script is usually wrapping
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — why the UTF-32 file fails, compressed or not
- [The five worth installing](../worth_installing/README.md) — the neighbouring tools, and where `ripgrep-all` gets a mention: `--pre` with the converters already chosen
