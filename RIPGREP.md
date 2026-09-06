# rg — the menu

**Level:** reference · for anyone who has `rg` installed and uses four of its flags

**One line:** `rg` is fast because of what it refuses to open — your `.gitignore`, your dotfiles, and anything it judges binary — so the flags worth knowing are the ones that say *look anyway*, plus the one that teaches it a format it cannot read on its own.

Measured on **2026-09-06**, macOS 26.6.2, `ripgrep 15.1.0` (Homebrew), `pdftotext 25.12.0` (Poppler). **Nothing on this page is machine-checked:** neither macOS nor Ubuntu ships `rg`, so CI has no copy of it and `tools/run_examples.py` cannot hold an answer key for any fence here. Every block below is a real run pasted unedited — the `wc -l` column padding is BSD `wc`'s, not a typo. The file counts are this repository at that moment and will drift; the *ratios* are the lesson.

This page is the practical menu. What `rg` decides about **character encodings** — why it reads a UTF-16 file that `grep` cannot see, and what it does with a byte that decodes to nothing — is a separate subject with its own page: [`ripgrep` — the Rust grep](11_Tools/ripgrep/README.md).

## The menu

Four questions, in the order you ask them.

**What am I looking for?**

| Flag | What it does | When you reach for it |
|---|---|---|
| `-i` | case-insensitive | almost always, in prose |
| `-S` | smart case — insensitive until your pattern has a capital | better default than `-i`; put it in your config file |
| `-w` | whole word | `rg -w id` stops matching `width`, `valid`, `uuid` |
| `-F` | fixed string, no regex | a pattern full of `.` `(` `[` — a stack trace, a version number |
| `-e PAT` | another pattern | repeatable: `rg -e TODO -e FIXME` |
| `-U` | let the pattern cross line ends | the only way to match a two-line construct |
| `-P` | full PCRE2 — lookaround, backreferences | `rg -P '(?<!def )foo'`; slower, and your build must have it |

Check the last one before you rely on it: `rg --version` prints `+pcre2` or `-pcre2` on its features line.

**Where should it look?**

| Flag | What it does |
|---|---|
| `-g GLOB` | keep or drop paths — `-g '*.md'`, and `-g '!site/**'` to exclude |
| `-t TYPE` / `-T TYPE` | include / exclude a language — `-t py`, `-T lock` |
| `--type-list` | every type it knows, with the globs behind it |
| `-u` `-uu` `-uuu` | the ladder below — ignore your `.gitignore`, then hidden files, then binary |
| `--pre CMD` | run each file through a program first — [how PDFs get searched](#searching-pdfs) |
| `-j N` | thread count; `-j1` when you want output in a stable order |

**What do I want back?**

| Flag | What it does |
|---|---|
| `-l` / `--files-without-match` | names of files that match / that don't |
| `--files` | every file it *would* search, and no searching — the flag that answers "why did it miss that?" |
| `-c` | count matching **lines** per file; add `-o` and pipe to `wc -l` for a count of **matches** |
| `-o` | print the matched part only, one per line |
| `-A n` `-B n` `-C n` | lines of trailing / leading / surrounding context |
| `--stats` | matches, files searched, time — a sanity check on a search that returned less than you expected |
| `--json` | one JSON object per event, for a script downstream |

**What do I want to do with it?**

`-r` rewrites matches on the way to the screen (`rg 'v(\d+)' -r 'version $1'`) and changes nothing on disk — `rg` has no in-place edit, by design. `--passthru` prints every line and highlights the matches, which is how you use it as a highlighter in a pipe.

## What rg does not search

The default is not "this directory". It is "the files a `git` working tree would show you", and three separate filters get applied before a byte is read. `--files` makes them visible, because it lists exactly what would be searched:

```text title="Measured 2026-09-06 in this repository — macOS 26.6.2, rg 15.1.0. Counts drift with the build output; the ratios are the point. Not machine-checked: CI has no rg."
$ rg --version
ripgrep 15.1.0

$ rg --files | wc -l                 # what rg searches by default
     264

$ rg --files -u | wc -l              # -u: also .gitignored files
     570

$ rg --files -uu | wc -l             # -uu: also hidden files
   18550

$ rg --files -uu | sed "s#/.*##" | sort | uniq -c | sort -rn | head -3
17080 .venv
 887 .git
 305 site
```

Read the last block before you make `-uu` a habit. Adding hidden files to a Python project means adding `.venv` — 17,080 files of vendored library source, sixty-five times the repository itself — and in any git repository it also means `.git`, where a match is a line from a packed object that no longer corresponds to anything you can edit. `-uu` is the right flag for *"I know it is in a dotfile"* and the wrong one for *"search harder"*.

The third rung, `-uuu`, adds binary files. It does not change the file list at all — `--files` reports the same 18,550 — because it changes what happens *inside* a file rather than which files are opened. Searching this repository for `the` matched 1,542 files at `-uu` and 2,065 at `-uuu`; those 523 extra files are ones `rg` had opened, sniffed, and stopped reading.

Binary detection is a NUL byte, and `rg` says so out loud rather than going quiet:

```text title="Measured 2026-09-06 — macOS 26.6.2, rg 15.1.0. The file is `printf 'hello\000world hello\n'`. Not machine-checked: CI has no rg."
$ rg hello withnul.bin
binary file matches (found "\0" byte around offset 5)

$ rg -a hello withnul.bin | cat -v
hello^@world hello
```

That message is the difference between `rg` and one of the two `grep`s, and it is the reason this library has [a page on what `grep` does with the same file](11_Tools/grep/README.md).

## Searching PDFs

`rg` cannot search a PDF, and the failure is silent — not an error, not a warning, just no hits:

```text title="Measured 2026-09-06 — macOS 26.6.2, rg 15.1.0, pdftotext 25.12.0. Not machine-checked: CI has no rg."
$ ls 10-Ownership.pdf
10-Ownership.pdf

$ rg -c ownership 10-Ownership.pdf
exit=1

$ rg -c -a ownership 10-Ownership.pdf        # -a does not help
exit=1

$ pdftotext -q 10-Ownership.pdf - | rg -c ownership
3
exit=0
```

A file named `10-Ownership.pdf` reports **no matches** for `ownership`. The word is in there three times as a lowercase line, and `pdftotext` finds it.

The reason is not binary detection, which is why `-a` changes nothing: a PDF keeps its text in **compressed streams** (usually FlateDecode, the same algorithm as gzip), so the letters `o-w-n-e-r-s-h-i-p` are never on disk as those bytes. There is nothing for a byte search to match. Anything that decompresses first will find it; nothing that does not, will.

`--pre` is the hook for exactly this. It names a program that `rg` runs on each file, reading the program's stdout instead of the file:

```sh title="~/.local/bin/rg-pre"
#!/bin/sh
# ripgrep --pre preprocessor: make PDFs searchable by piping them through pdftotext.
# rg passes the filename as $1 and reads our stdout. Non-PDFs pass through unchanged.
case "$1" in
    *.pdf|*.PDF) exec pdftotext -q "$1" - ;;
    *)           exec cat "$1" ;;
esac
```

`--pre-glob` is not optional in practice. Without it every file gets a process spawned for it; with it, only PDFs take the slow path and everything else stays on `rg`'s normal one:

```bash
rg --pre ~/.local/bin/rg-pre --pre-glob '*.pdf' PATTERN .
```

Worth wrapping, since nobody types that twice. In fish, as an autoloaded function at `~/.config/fish/functions/rgp.fish` — `--wraps rg` is what makes it inherit `rg`'s own tab completions:

```fish title="~/.config/fish/functions/rgp.fish"
function rgp --wraps rg --description "ripgrep that also searches inside PDFs (via pdftotext)"
    command rg --pre $HOME/.local/bin/rg-pre --pre-glob '*.pdf' $argv
end
```

In bash or zsh the same thing is a function in your rc file, because an `alias` cannot take arguments in the middle:

```bash
rgp() { rg --pre "$HOME/.local/bin/rg-pre" --pre-glob '*.pdf' "$@"; }
```

**On cost:** over a folder of about a hundred Rust books, `rgp -l 'Pin<&mut'` took **23.7 s** wall for **123 s** of CPU — `rg` runs the preprocessor on many files at once, so the wall clock is roughly the CPU time divided by your cores. That is fine to type when you are looking for something. It is the wrong shape for a search you will run repeatedly: dump once with `pdftotext -layout` into a `.txt` beside each PDF and search those at full speed, and you get real page numbers for citations as a side effect.

## The same trick, other formats

The rule is more general than PDFs: **any format that is a compressed container is invisible to a byte search.** A `.docx` is a zip of XML, and behaves identically —

```text title="Measured 2026-09-06 — macOS 26.6.2, rg 15.1.0. demo.docx is a zip holding word/document.xml with the word in it. Not machine-checked: CI has no rg."
$ rg ownership demo.docx
exit=1

$ unzip -p demo.docx word/document.xml | rg -o ownership
ownership
```

— and so do `.xlsx`, `.pptx`, `.epub`, `.odt`, and `.jar`. Each needs its own branch in the preprocessor. If you want all of them without writing any of it, [ripgrep-all ↗](https://github.com/phiresky/ripgrep-all) is `rg` plus a preprocessor for PDF, Office, ebooks, archives, subtitles and media metadata; `brew install ripgrep-all` gives you `rga`, which takes `rg`'s flags.

One container `rg` *does* handle by itself: `-z` / `--search-zip` reads gzip, bzip2, xz, lz4, Brotli and zstd. It is for compressed **streams** — `access.log.2.gz` — not for archives with several files inside, which is why it does nothing for a PDF or a `.docx`.

## What stays out of reach

A **scanned** PDF has no text layer at all: the page is a photograph, and `pdftotext` returns nothing because there is nothing to return. No preprocessor helps; that needs OCR (`ocrmypdf` writes a text layer back into the file, after which everything above works). The tell is that extraction comes back empty, which is worth checking before you trust a search that found nothing:

```bash
for f in *.pdf; do printf '%8s  %s\n' "$(pdftotext -q "$f" - 2>/dev/null | wc -c)" "$f"; done | sort -n | head
```

Anything near zero at the top of that list is a file your search silently could not read. Run over a shelf of 92 Rust books on 2026-09-06 it turned up none: the smallest extraction was 1,031 bytes, and that file is a one-page container cheat sheet which really does hold about that much text. A clean result looks like that — small numbers that match small documents — rather than zeros. The same check catches an **encrypted** PDF, where `pdftotext` fails outright — `rg` reports the preprocessor's failure rather than swallowing it, which is the behaviour you want.

## See also

- [`ripgrep` — the Rust grep](11_Tools/ripgrep/README.md) — the encoding half: the BOM it reads, the locale it ignores, the UTF-32 file it gets wrong.
- [`grep` on text that is not ASCII](11_Tools/grep/README.md) — where the two tools part company, including the line BSD `grep` drops without saying so.
- [The five worth installing](11_Tools/worth_installing/README.md) — the rest of the toolbox.
- [ripgrep's own guide ↗](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md) — Andrew Gallant's, and the place to read about configuration files (`RIPGREP_CONFIG_PATH`), which is where `-S` belongs once you have decided you want it everywhere.
