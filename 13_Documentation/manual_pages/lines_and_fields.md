# `cat(1)`, `sort(1)`, `xargs(1)` and fifteen more: which line tools are encoding-blind, and which ones ask the locale

**Level:** reference · for anyone who has piped `head -c` or `sort` over a file with an accent in it and wanted the page to say what happens

**One line:** Twelve of these eighteen pages cut on newlines, NUL and a one-byte delimiter and never decode, so `head -c 4` on `café` hands back half a character but the same half on every machine; the other six compare or split *text*, and their pages either name `LC_COLLATE` (`sort`, `comm`, `join`), defer to `environ(7)` (`uniq`, `paste`) or admit in BUGS that they ignore it (`look`), and two of them, `uniq -i` and `paste -d`, give different answers on the two machines in a UTF-8 locale.

**The pages:** [`cat(1)`](raw/macos/cat.1.txt) (January 29, 2013) · [`head(1)`](raw/macos/head.1.txt) (April 10, 2018) · [`tail(1)`](raw/macos/tail.1.txt) (November 28, 2023) · [`nl(1)`](raw/macos/nl.1.txt) (June 18, 2020) · [`split(1)`](raw/macos/split.1.txt) (May 26, 2023) · [`csplit(1)`](raw/macos/csplit.1.txt) (February 6, 2014) · [`tee(1)`](raw/macos/tee.1.txt) (June 23, 2020) · [`look(1)`](raw/macos/look.1.txt) (December 29, 2020) · [`uniq(1)`](raw/macos/uniq.1.txt) (December 9, 2024) · [`sort(1)`](raw/macos/sort.1.txt) (September 4, 2019) · [`comm(1)`](raw/macos/comm.1.txt) (July 27, 2020) · [`join(1)`](raw/macos/join.1.txt) (June 20, 2020) · [`paste(1)`](raw/macos/paste.1.txt) (June 25, 2004) · [`lam(1)`](raw/macos/lam.1.txt) (April 7, 2015) · [`rs(1)`](raw/macos/rs.1.txt) (April 7, 2015) · [`jot(1)`](raw/macos/jot.1.txt) (September 21, 2019) · [`seq(1)`](raw/macos/seq.1.txt) (June 20, 2020) · [`xargs(1)`](raw/macos/xargs.1.txt) (September 21, 2020). All macOS 26.6.2, dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). The GNU tools of the same names on ubuntu:24.04 were measured beside them; `lam`, `rs` and `jot` do not exist there, and `look` comes from `bsdextrautils`.

## What the pages are for

These are the tools that work *along* a file rather than across a line: show it, take its first or last part, number it, cut it into pieces, put two files side by side, order it, deduplicate it, find a line in it, generate lines, feed lines to another command. The [columns family](columns_and_characters.md) has to know what a character is before it can start; most of this family does not, because a newline is one byte (`0a`) that can never occur inside a multibyte UTF-8 character, and NUL is a byte no filename and almost no text contains. A tool that cuts only there is *encoding-blind and safe*: it cannot produce a wrong character because it never produces a character at all. The price is that when such a tool is given a byte count instead (`head -c`, `tail -c`, `split -b`), it cuts wherever the count lands, which [the `split` lesson](../../11_Tools/look_paste_tee_split/README.md) shows is the middle of `é`.

The other six do something a byte cannot do alone. `sort`, `comm` and `join` put lines in an *order*, and order is a property of a locale rather than of the text: [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md). `uniq -i` and `look -f` fold case, which needs `LC_CTYPE`. `paste -d` takes a *list of characters* and has to decide where one ends. These pages are where the words *collating sequence*, *lexically sorted* and *LC_COLLATE* appear, and the question to ask each is the second one from [the tools chapter](../../11_Tools/README.md): who decided, and does the page say.

Two of the eighteen are on the page for a third reason. `cat -v` is the family's one *display* of bytes, the `M-x` and `^X` notation that `od -a` and [`vis(1)`](vis.md) share, and its page explains the notation and then admits it does not know about multibyte characters. And `xargs` is the tool that turns lines back into a command line, with its own quoting grammar on the way, which is the subject of [`xargs` splits on the wrong things](../../11_Tools/xargs/README.md).

## The pages, with notes

### `cat(1)`, `head(1)`, `tail(1)`, `split(1)`, `csplit(1)`, `nl(1)`, `tee(1)`: bytes and newlines only

```text title="man 1 cat, macOS 26.6.2, dumped 2026-09-13"
     -v      Display non-printing characters so they are visible.  Control
             characters print as `^X' for control-X; the delete character
             (octal 0177) prints as `^?'.  Non-ASCII characters (with the high
             bit set) are printed as `M-' (for meta) followed by the character
             for the low 7 bits.
     ...
BUGS
     The cat utility does not recognize multibyte characters when the -t or -v
     option is in effect.
```

That is the whole of the notation: a byte below `0x20` is `^` plus the byte with `0x40` added, `0x7f` is `^?`, and a byte above `0x7f` is `M-` plus the same rule applied to its low seven bits. `é` therefore prints as `M-CM-)` on every machine in every locale, because `c3` is `M-` followed by `0x43`, `C`, and `a9` is `M-` followed by `0x29`, `)`. The BUGS line is the point: `-v` is a respelling of *bytes*, which is exactly what makes it useful in [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md), and GNU `cat -A` is the same three flags under one letter that this Mac's `cat` rejects.

| Page | On the page | What it means | Measured 2026-09-13 |
|---|---|---|---|
| `cat` | `-e` ... *a dollar sign at the end of each line*; `-t` ... `^I` | the two invisibles that decide line and column structure, made visible: [The trailing newline](../../06_Terminal/trailing_newline/README.md) | `cat -vet` on `caf` `c3 a9` `00` `09` `0d` `0a` prints `cafM-CM-)^@^I^M$` on both machines |
| `head` | `-c bytes` *Print bytes of each of the specified files* | a byte count; the page never says *character* | `head -c 4` on `café`: `63 61 66 c3` everywhere |
| `tail` | `-c number` *The location is number bytes*; `"-c +2" starts the display at the second byte` | same unit, either end | `tail -c +2` on `éa`: `a9 61`, the second half of `é` first |
| `tail` | STANDARDS: `"-r -c 4" displays the last 4 characters of the last line` | the page says *characters* for a flag it defined as bytes two sections earlier | |
| `split` | `-b byte_count[K|k|M|m|G|g]` *Create split files byte_count bytes in length*; `-l line_count`; `-n chunk_count` | bytes, lines, or equal byte shares; only `-l` and `-p` cut at a boundary that is never inside a character | `split -b 3` on `café`: `63 61 66` and `c3 a9 0a`, on both machines |
| `csplit` | `/regexp/`, `%regexp%`, `line_no`, `{num}` | cuts before a line that matches; the pattern is a basic regular expression over bytes, as in [`sed`](../../11_Tools/sed/README.md) | |
| `nl` | `\:\:\:`, `\:\:`, `\:` *header, body, footer*; `-d delim` *At most two characters* | a line holding only the delimiter starts a section and is not printed; `-d @` replaces the first character only, so the pair becomes `@:` | a line `\:` makes the following line unnumbered on both; `nl -d @` numbers `@@` as an ordinary line 2 |
| `nl` | `-w width` *the number of characters*; BUGS `LINE_MAX (2048) bytes` | width in characters of the number, limit in bytes of the line | |
| `tee` | *copies standard input to standard output, making a copy* | no delimiter, no decode: the control in [the `split` lesson](../../11_Tools/look_paste_tee_split/README.md) | |

### `xargs(1)`: lines into arguments, through a quoting grammar

```text title="man 1 xargs, macOS 26.6.2, dumped 2026-09-13"
     Spaces, tabs and newlines may be embedded in arguments using single
     (`` ' '') or double (``"'') quotes or backslashes (``\'').  Single quotes
     escape all non-single quote characters, excluding newlines, up to the
     matching single quote.
     ...
     -0, --null
             Change xargs to expect NUL (``\0'') characters as separators,
             instead of spaces and newlines.  This is expected to be used in
             concert with the -print0 function in find(1).
```

The first paragraph is a small language of its own, and it is applied to every byte that arrives on the pipe before anything is handed to the command: an apostrophe in a filename opens a quote that never closes. `-0` turns the language off and makes NUL the only separator, which works because NUL is the one byte the kernel will not put in a filename: [The NUL byte](../../02_Characters/the_nul_byte/README.md). The page's BUGS adds that `-I` and `-J` compare *without taking multibyte characters into account*, and `-s size` is *bytes*, so how many times the command runs depends on how the filenames are spelt.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| *reads space, tab, newline and end-of-file delimited strings* | whitespace is a separator by default; `with space.txt` is two arguments | `a b` / `c d` on two lines: four calls of `echo` on both |
| *unterminated quote* | the failure an apostrophe causes; the message is the one place the two `xargs` differ | BSD: `xargs: unterminated quote`; GNU: `unmatched single quote; by default quotes are special to xargs unless you use the -0 option` |
| `-0` | NUL-separated, no quoting | `a b` NUL `c d` NUL: two calls, arguments intact, on both |
| `-r` *does nothing in the FreeBSD version* | GNU runs the command once on empty input; BSD never does | |

### `sort(1)`, `uniq(1)`, `comm(1)`, `join(1)`: the collating sequence

```text title="man 1 sort, macOS 26.6.2, dumped 2026-09-13"
     Comparisons are based on one or more sort keys
     extracted from each line of input, and are performed lexicographically,
     according to the current locale's collating rules and the specified
     command-line options that can tune the actual sorting behavior.
     ...
ENVIRONMENT
     LC_COLLATE  Locale settings to be used to determine the collation for
                 sorting records.

     LC_CTYPE    Locale settings to be used to case conversion and
                 classification of characters, that is, which characters are
                 considered whitespaces, etc.
```

This is the most complete ENVIRONMENT section in either family: seven variables, each with its job. `LC_COLLATE` decides the order, `LC_CTYPE` decides what `-f` folds and what `-b` skips, `LC_NUMERIC` decides what `-n` reads as a decimal point, and the NOTES section promises that in a multibyte locale *the correct collation order is always respected*. [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) measured that promise on both machines with `en_US.UTF-8`: they agree, and `Łódź` moves from last to third. The Docker container this page measured on has only `C.UTF-8`, whose collation is code point order, so the UTF-8 column below is the byte order on Ubuntu and the alphabetical order on the Mac.

`uniq` and `comm` compare *adjacent* lines and *lexically sorted* files, so both inherit whatever order `sort` chose, and `join` says it outright: the files *should be ordered in the collating sequence of sort(1)*. The pair that fails is a file sorted under one locale and joined under another. With `a`, `é`, `z` in `f1` and `a`, `z` in `f2` under `LC_ALL=C`, both machines print only `a 1 x` and lose the `z` match, because `é` sorts after `z` in byte order and the merge has already moved on; GNU `join` warns `join: f1:3: is not sorted: z 3` and exits 1, BSD `join` says nothing and exits 0. When every line pairs, as in the three-line test below, neither warns.

| Page | On the page | What it means | Measured 2026-09-13 |
|---|---|---|---|
| `sort` | `-f` *Convert all lowercase characters to their uppercase equivalent* | uses `LC_CTYPE`'s `toupper`; `é` folds only where the locale has an `É` | `sort -f` on `é É e E`: `e E é É` on the Mac in UTF-8, `E e É é` in `C` and on Ubuntu |
| `sort` | `-t '\0'`, `-z` | NUL as field separator and as record separator, for `find -print0` output | |
| `sort` | `-V` *All string comparisons are performed in C locale* | the one ordering flag that pins its own locale | |
| `sort` | `--radixsort` ... *only be used for trivial locales (C and POSIX)* | byte order is what makes the fast algorithm possible | |
| `uniq` | `-i` *Case insensitive comparison of lines* | BSD folds through the locale; GNU folds ASCII only | `uniq -i` on `é` / `É`: one line on the Mac in UTF-8, two lines everywhere else |
| `uniq` | `-c` *followed by a single space*; `-s chars` *Ignore the first chars characters* | the count's width is not on the page; `-s` says characters and its unit was not measured here | `uniq -c` right-aligns the count in 4 columns on BSD and 7 on GNU |
| `comm` | *should be sorted lexically*; `-i` | byte order or collation, whichever `sort` used; `-i` is a BSD extension | |
| `join` | *ordered in the collating sequence of sort(1), using the -b option* | with `-t`, *without* `-b`: leading blanks are part of the key one way and not the other | files sorted `a é z` join in both locales on both machines; drop `é` from one file and the `z` match is lost, silently on BSD, with a warning on GNU |

### `look(1)`: a binary search, and a BUGS section that answers the question

```text title="man 1 look, macOS 26.6.2, dumped 2026-09-13"
     As look performs a binary search, the lines in file must be
     sorted.
     ...
BUGS
     Lines are not compared according to the current locale's collating order.
     Input files must be sorted with LC_COLLATE set to `C'.
```

A binary search assumes an order and never checks it; a file in the wrong order does not fail, it misses, with the same exit status as a genuinely absent word. The page is the only one in the family that says *which* order: `C`, bytes, regardless of the locale you run it in. The measurement agrees. A file holding `a`, `é`, `z` in that order is sorted alphabetically and not in byte order (`c3` sorts after `z`), and `look é` exits 1 on both machines in both locales.

### `paste(1)`, `lam(1)`, `rs(1)`: delimiters and laminated columns

```text title="man 1 paste, macOS 26.6.2, dumped 2026-09-13"
     -d list     Use one or more of the provided characters to replace the
                 newline characters instead of the default tab.  The
                 characters in list are used circularly, i.e., when list is
                 exhausted the first character from list is reused.
```

`-d` takes a *list*, and the question is what one element of the list is. On this Mac in a UTF-8 locale it is a character, and `paste -d '€' a b c` puts a three-byte `€` after each column; in the `C` locale and on GNU in every locale it is a byte, and the same command uses `e2` after the first column and `82` after the second, [as the `paste` lesson found](../../11_Tools/look_paste_tee_split/README.md). The 2004 page says *characters* and was right about this program once the locale caught up. `lam` and `rs`, the two BSD-only laminators, say in BUGS that they *do not recognize multibyte characters*, and measure that way: `lam -f 6.6` pads `café` with one space, because five bytes need one more to make six, and `rs` sizes its columns in bytes so a column holding `é` comes out one cell narrower than one holding `ab`.

| Page | On the page | Measured 2026-09-13 |
|---|---|---|
| `paste` | `\0` *Empty string (not a null character)* | |
| `paste` | `-s` | one line per file, the *transposed* use |
| `lam` | `-f min.max` *minimum field width and max the maximum field width* | width in bytes: `café` padded to ` café` |
| `rs` | *reads the standard input, interpreting each line as a row of blank-separated entries* | column widths in bytes: `é  b` above `ab  c` |

### `jot(1)` and `seq(1)`: numbers, and whose decimal point

```text title="man 1 seq, macOS 26.6.2, dumped 2026-09-13"
     -f format, --format format
                   Use a printf(3) style format to print each number.  Only
                   the A, a, E, e, F, f, G, g, and % conversion characters are
                   valid, along with any optional flags and an optional
                   numeric minimum field width or precision.
```

Both pages hand the formatting to `printf(3)`, and `printf(3)` prints the decimal point of `LC_NUMERIC`. This Mac has a `de_DE.UTF-8` locale, and under it `/usr/bin/printf '%.1f' 0.5` refuses its own argument (`not completely converted`) and prints `0,0`; `seq 0.5 1` and `jot -p 1 2 0.5 1` print `0.5` under the same locale, because neither program calls `setlocale`, so they stay in the `C` locale their page never mentions. Ubuntu's container has no German locale, so GNU `seq` was not measured; the [`printf(3)` page](printf.md) is where the decimal-point rule itself lives.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| *collating sequence*, *collating rules*, `LC_COLLATE` | the locale's ordering of characters, used by `sort` to compare and assumed by `comm`, `join` and `look`; byte order in `C` | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| *lexically sorted* | ordered by comparing strings position by position, in some collation; the page does not say which | [`strcoll(3)` and collation](collation.md) |
| `LC_CTYPE`, `LC_NUMERIC` | which characters are letters, blanks, upper case; which character is the decimal point | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `^X`, `^?`, `M-x` | `cat -v`'s spelling of a control byte, DEL, and a byte with the high bit set | [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) |
| *meta* | the eighth bit, from keyboards that set it for a Meta key; `M-C` is `0x43` with `0x80` added | [`vis(1)` and `vis(3)`](vis.md) |
| *non-printing character* | anything `isprint` rejects; the page's list is ASCII's | [Control characters](../../02_Characters/control_characters/README.md) |
| NUL, `\0`, `-print0`, `-z` | the byte no filename holds, used as a separator by `xargs -0`, `sort -z`, `find -print0` | [The NUL byte](../../02_Characters/the_nul_byte/README.md) |
| *logical page*, header, body, footer | `nl`'s three sections, delimited by lines of `\:` | |
| *blank*, *white space* | space and tab for `join` and `xargs`; the locale's `isblank` for `sort -b` | [`ctype(3)`](ctype.md) |
| *field* | a maximal run of non-separator characters; `-t` makes every separator significant, so `,,` holds an empty field | |
| *binary search* | halving the file at each step, which only finds a line if the file is in the searched order | [`split`, `paste`, `look` and `tee`](../../11_Tools/look_paste_tee_split/README.md) |
| `ARG_MAX` | the kernel's limit on a command line plus environment, in bytes; `xargs -s` defaults to it minus 4096 | [`xargs` splits on the wrong things](../../11_Tools/xargs/README.md) |
| `expand_number(3)` | the BSD size-suffix parser (`k`, `m`, `g`) `tail` uses for its numbers | |
| `printf(3)` conversion | `%d`, `%g`, `%c` and the rest, which `jot -w` and `seq -f` pass through | [`printf(3)` and `printf(1)`](printf.md) |
| `arc4random(3)`, `random(3)` | `jot -r`'s two generators; the seed decides which | |
| `LINE_MAX` | 2048 bytes, the longest line `nl` and `csplit` accept | |

## Try it on your machine

**The matrix.** Each command under `LC_ALL=C` and under a UTF-8 locale (`en_US.UTF-8` on the Mac, `C.UTF-8` on Ubuntu), output as hex or text; a trailing newline is omitted from every row.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD tools) and ubuntu:24.04 (GNU coreutils 9.4, findutils 4.9.0, util-linux 2.39.3 look). Not machine-checked: no key can match both."
                                             macOS C            macOS UTF-8         Ubuntu C           Ubuntu C.UTF-8
cat -vet         caf c3 a9 00 09 0d 0a       cafM-CM-)^@^I^M$   same               same               same
head -c 4        café                        636166c3           same               same               same
tail -c +2       éa                          a961               same               same               same
split -b 3       café\n                      636166 | c3a90a    same               same               same
nl               x / \: / y                  1 x, then y unnumbered                1 x, blank line, y unnumbered
nl -d @          x / @@ / y                  1 x, 2 @@, 3 y     same               same               same
uniq -i          é / É                       2 lines            1 line: é          2 lines            2 lines
uniq -c          é / é                       "   2 é"           same               "      2 é"        same
sort -f          é É e E                     E e É é            e E é É            E e É é            E e É é
sort             Łódź Zebra café Ada         Ada Zebra café Łódź  Ada café Łódź Zebra  Ada Zebra café Łódź  same as C
join f1 f2       both files a é z            3 lines, no warning                   3 lines, no warning
look é           file a é z                  exit 1             exit 1             exit 1             exit 1
paste -d '€'     a / b / c                   61e2628263         61e282ac62e282ac63  61e2628263         61e2628263
xargs -n1 echo   "a b" LF "c d" LF           a b c d (4 calls)  same               same               same
xargs -0 -n1     "a b" NUL "c d" NUL         a b | c d          same               same               same
seq 0.5 1                                    0.5                0.5                0.5                0.5
lam -f 6.6       café                        " café"            same               (no lam)           (no lam)
rs 0 2           é b ab c                    é  b / ab  c       same               (no rs)            (no rs)
```

The first four rows are the safe half of the family: byte-identical in every cell, and two of them hand back a piece of `é`. `uniq -i` and `paste -d` are the rows where the page's word *character* comes true on exactly one machine in exactly one locale. And `look é` fails everywhere on a file that plainly contains `é`, because the file is in alphabetical order and `look` searches in byte order, which is what its BUGS section said it would do.

**The two `xargs` messages.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD xargs) and ubuntu:24.04 (GNU findutils 4.9.0). Not machine-checked."
$ printf "O'Brien\n" | xargs echo; echo exit=$?
xargs: unterminated quote                                                                       macOS
xargs: unmatched single quote; by default quotes are special to xargs unless you use the -0 option   Ubuntu
exit=1                                                                                          both
```

**Whose decimal point.** The Mac has a German locale; the container does not.

```text title="Measured 2026-09-13 — macOS 26.6.2, LC_ALL=de_DE.UTF-8. Not machine-checked."
$ seq 0.5 1                       0.5
$ seq -f %.1f 0.5 1               0.5
$ jot -p 1 2 0.5 1                0.5   1.0
$ /usr/bin/printf '%.1f\n' 0.5    printf: 0.5: not completely converted
                                  0,0
$ printf '1,5\n1.2\n' | sort -n   1,5   1.2
```

`printf(1)` set the locale and both parsed and printed a comma; `seq` and `jot` did not, and printed a full stop. `sort -n` read `1,5` as the smaller number, which is the `LC_NUMERIC` line of its ENVIRONMENT section doing its job.

## Where the pages are dated, and what they do not say

**`paste(1)` is dated June 25, 2004** and says `-d` takes *characters*. The BSD program keeps that promise in a UTF-8 locale and breaks it in `C`; the GNU program breaks it everywhere. The page cannot tell you which `paste` you have.

**`tail(1)` (2023) defines `-c` as bytes and then, in STANDARDS, says `-r -c 4` shows *the last 4 characters*.** The same flag, two units, on one page. It means bytes both times.

**`sort(1)` (2019) promises that the correct collation is *always respected*** in multibyte locales, and says nothing about `C.UTF-8`, the locale Ubuntu's container ships, whose collation is code point order; under it `sort` behaves as in `C`. It also does not say that `sort -u` compares bytes, so `żółw` composed and `żółw` decomposed are two lines: [Normalization](../../04_Python/normalization/README.md).

**`look(1)` (2020) is the honest page of the family**, and its honesty is in BUGS rather than DESCRIPTION.

**`cat(1)` (2013) documents `-v` and not `-A`**, which is GNU-only, and its EXAMPLES still say `cat` reads standard input *until it receives an EOF (`^D') character*; there is no such character, as [`tty(4)` and `stty(1)`](tty.md) measures.

**`head(1)` (2018) is the shortest page here and says nothing about what `-c` does inside a character.** It does the same thing everywhere, which is more than most of this family can claim.

**`jot(1)` and `seq(1)` do not mention `LC_NUMERIC`**, and behave as if it were always `C`. **`xargs(1)` (2020)** documents `-r` as a no-op on BSD without saying why anyone would want it, which is that GNU `xargs` runs your command once on empty input.

## See also

- [`tr(1)`, `cut(1)`, `fold(1)`, `wc(1)` and the column tools](columns_and_characters.md) — the family that cuts across a line and has to know what a character is
- [`strcoll(3)` and collation](collation.md) — the C function behind `sort`'s *collating rules*
- [`vis(1)` and `vis(3)`](vis.md) — the other ASCII respelling of bytes, and the one that can be reversed
- [`diff(1)`, `cmp(1)` and the checksums](compare.md) — comparing what these tools produced
- [`split`, `paste`, `look` and `tee`](../../11_Tools/look_paste_tee_split/README.md) — the lesson behind four of these pages, with the pieces that are not valid UTF-8
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) — `sort` under two locales on two machines, and why `uniq` counts spellings
- [`xargs` splits on the wrong things](../../11_Tools/xargs/README.md) — the quoting grammar and the byte budget
- [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) — why *sorted* is a property of a file and a locale
- [Binary is a verdict, not a property](../../06_Terminal/binary_or_text/README.md) — what `cat -v` shows, and why nothing in the file says *text*
- [The trailing newline](../../06_Terminal/trailing_newline/README.md) — the `$` that `cat -e` draws, and the line `wc -l` will not count
- [A page has a date](../a_page_has_a_date/README.md) — the 2004 `paste` page and the program it now describes
