# `tr(1)`, `cut(1)`, `fold(1)`, `wc(1)` and eight more: twelve column tools, and whether the page promises bytes or characters

**Level:** reference · for anyone who has typed `man cut` and wondered whether `-c` means what it says

**One line:** Every one of these twelve BSD pages uses the word *character*; four of them mean it only in a UTF-8 locale, three confess in BUGS that they *do not recognize multibyte characters*, and the GNU tools behind the same names on Ubuntu count bytes in `fold`, `cut -c` and `tr` whatever the page says, so the promise is about one implementation and `LC_CTYPE` is the switch.

**The pages:** [`tr(1)`](raw/macos/tr.1.txt) (October 13, 2006) · [`cut(1)`](raw/macos/cut.1.txt) (August 3, 2017) · [`fold(1)`](raw/macos/fold.1.txt) (October 29, 2020) · [`fmt(1)`](raw/macos/fmt.1.txt) (October 29, 2020) · [`expand(1)`](raw/macos/expand.1.txt) and [`unexpand(1)`](raw/macos/unexpand.1.txt) (one page, June 6, 2015) · [`col(1)`](raw/macos/col.1.txt) (October 21, 2020) · [`colrm(1)`](raw/macos/colrm.1.txt) (June 23, 2020) · [`pr(1)`](raw/macos/pr.1.txt) (July 3, 2004) · [`ul(1)`](raw/macos/ul.1.txt) (October 7, 2020) · [`rev(1)`](raw/macos/rev.1.txt) (June 27, 2020) · [`wc(1)`](raw/macos/wc.1.txt) (April 11, 2020). All macOS 26.6.2, dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). The GNU and util-linux tools of the same names on ubuntu:24.04 were measured beside them, not read.

## What the pages are for

These are the section 1 pages for the tools that work *across* a line: substitute characters, pick columns, wrap, pad, number columns, reverse, count. None of them is about encodings, and every one of them has to decide what a character is before it can do its job, which is [the first question the tools chapter asks of any command](../../11_Tools/README.md): bytes or characters, and who decided. A man page answers it in one of three ways. It says *bytes* outright (`cut -b`, `fold -b`, `wc -c`), it says *characters* and defers to the locale through a one-sentence ENVIRONMENT section (`The LANG, LC_ALL and LC_CTYPE environment variables affect the execution of X as described in environ(7)`), or it says in BUGS that the program never learned about multibyte characters at all (`pr`, and on the next page `lam` and `rs`).

Eleven of the twelve pages carry that ENVIRONMENT sentence. The one that does not is `rev(1)`, which is also the tool whose output changes most when the locale changes: it reverses characters in a UTF-8 locale and bytes in the `C` locale, taking `é` apart, and on Ubuntu the `C`-locale run does not finish at all. Reading the ENVIRONMENT section is therefore necessary and not sufficient. The pages describe the BSD programs on this Mac; the GNU coreutils programs that answer to the same names on Ubuntu have their own documentation, and where the two disagree the page you are reading is right about only one of them.

The organising fact of this family is that *character* on these pages means whatever `LC_CTYPE` says it means, which is [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) applied twelve times, and that *column* means something else again: a count of terminal cells, where `中` takes two and a combining mark takes none, which is the fifth ruler on [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) and the subject of [`wcwidth(3)`](wcwidth.md).

## The pages, with notes

### `tr(1)`: sets of characters, in a locale the page half-trusts

```text title="man 1 tr, macOS 26.6.2, dumped 2026-09-13"
     c-c        For non-octal range endpoints represents the range of
                characters between the range endpoints, inclusive, in
                ascending order, as defined by the collation sequence.
     ...
     "[=equiv=]" expression and collation for ranges are implemented for
     single byte locales only.
```

The page defines its sets in terms of characters and collation, then withdraws half of it in COMPATIBILITY: equivalence classes and collated ranges are *single byte locales only*. The measurement below is more generous than the page. In a UTF-8 locale this Mac's `tr '[=e=]' e` turns `café` into `cafe`, exactly the EXAMPLES entry *Remove diacritical marks from all accented variants of the letter e*, and `tr '[:lower:]' '[:upper:]'` produces `CAFÉ`. GNU `tr` does neither, in any locale, and its own documentation says it handles single-byte characters only. That split is the headline of [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md).

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| `[:class:]` ... `ideogram`, `phonogram`, `rune`, `special` | POSIX classes plus four BSD ones. `rune` is *valid characters*, the Plan 9 word: [`rune(3)`](rune.md) | in a UTF-8 locale `[:lower:]`/`[:upper:]` reach `é`; in `C` only ASCII |
| `\octal` | a byte, written in octal; the only way to name a byte above `0x7f` without typing it | `tr -d 'é'` is `tr -d '\303\251'`: a set of two bytes, in `C` on both machines |
| `-C` / `-c` | complement the *set of characters* / the *set of values*: characters against bytes, as two flags | |
| *stripped NUL's ... removed this behavior as a bug* | NUL passes through `tr` now: [The NUL byte](../../02_Characters/the_nul_byte/README.md) | |

### `cut(1)`: the one page that defines the difference

```text title="man 1 cut, macOS 26.6.2, dumped 2026-09-13"
     -b list
             The list specifies byte positions.

     -c list
             The list specifies character positions.
     ...
     -n      Do not split multi-byte characters.  Characters will only be
             output if at least one byte is selected, and, after a prefix of
             zero or more unselected bytes, the rest of the bytes that form
             the character are selected.
```

This is the only page in the family that names both units and gives a flag for the boundary between them. `-n` is the interesting one: a byte selection that refuses to cut a character in half. On this Mac `cut -b1-4 -n` on `café` prints `caf`, because byte 4 is the first byte of `é` and byte 5 was not selected, and `cut -b4-5 -n` prints the whole `é`. GNU `cut` accepts `-n` and ignores it, and its `-c` is `-b` under another name; [`cut` counts what it is told to count](../../11_Tools/cut/README.md) has the measurement and the fixed-width record it costs money on.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| `-c list` | character positions, counted by the `LC_CTYPE` decoder | `cut -c1-4` on `café`: 5 bytes on the Mac in UTF-8, 4 everywhere else |
| `-d delim` | one delimiter *character* | a multibyte delimiter is accepted only by BSD `cut` in a UTF-8 locale |
| `-w` | whitespace-delimited fields, a BSD extension | |

### `fold(1)` and `fmt(1)`: columns, not bytes, and one that deletes what it cannot read

```text title="man 1 fold, macOS 26.6.2, dumped 2026-09-13"
     -b      Count width in bytes rather than column positions.
```

`fold` counts *column positions* by default and bytes with `-b`, so a wide character costs two of the eighty. On this Mac `fold -w 4` on `中文字` breaks after `中文` (four columns) and on `😀😀😀` after two faces; GNU `fold` has no multibyte support and breaks after four *bytes* in either locale, in the middle of the second character. `fmt` counts in the same way and has a worse failure: in the `C` locale the BSD `fmt` deletes every byte above `0x7f` from its input, so `café naïve` comes out `caf nave`. The page says nothing about either; where a line may be broken at all is [Where a line may break](../../02_Characters/where_a_line_may_break/README.md), and neither tool knows that rule.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| *breaking the lines to have a maximum of 80 columns* | columns are terminal cells, [`wcwidth(3)`](wcwidth.md) per character | `中文字` at `-w 4`: `中文` / `字` on the Mac, mid-character on Ubuntu |
| `-s` *after the last blank* | a word boundary is a blank, nothing more | |
| `fmt` *goal length ... maximum* | 65 and 75 by default; `-w` sets both | `fmt -w 10` keeps `café naïve` on one line on the Mac (10 characters) and splits it on Ubuntu (12 bytes) |
| `fmt -d chars`, `-l`, `-t` | sentence-ending characters; tab stops for indentation | |

### `expand(1)`, `unexpand(1)`, `col(1)`, `colrm(1)`: tab stops and the overstrike format

```text title="man 1 col, macOS 26.6.2, dumped 2026-09-13"
     -b      Do not output any backspaces, printing only the last character
             written to each column position.
     ...
     -x      Output multiple spaces instead of tabs.
     ...
     All unrecognized control characters and escape sequences are discarded.
```

`col` reads the format a printer would: characters advance a column, backspace retreats one, a reverse line feed goes up, and `-b` keeps only the last thing written in each cell. That is exactly what `man` emits for bold (`N`, backspace, `N`) and underline (`_`, backspace, `x`), which is why this folder's [`dump.sh`](dump.sh) renders every page through `col -bx`: `-b` strips the overstrikes and `-x` turns the tabs `col` would otherwise insert into spaces. The last sentence quoted is the trap. In the `C` locale this Mac's `col` treats every byte above `0x7f` as an unrecognised control character and *discards* it, so `printf 'é\n' | LC_ALL=C col -b` prints an empty line; util-linux `col` instead rewrites the byte as the six characters `\xc3`. A dump made under the wrong locale would have lost its accents silently, and the reason the dumps in `raw/` are intact is that `man` chose ASCII output under that locale to begin with, which is the subject of [`man(1)` and `mandoc(1)`](man.md).

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| `expand -t tab1,tab2,...` | tab stops at column positions; default every 8 | `é<TAB>x` becomes `é` plus 7 spaces on the Mac in UTF-8, 8 in `C`, 6 on Ubuntu |
| *Backspace characters ... decrement the column count* | `expand` and `colrm` both count the overstrike format | |
| `colrm` *A column is defined as a single character in a line* | the page says character; the program counts cells | `colrm 2 2` on `中文字` removes `中` on the Mac, prints a space for its other half on Ubuntu |
| `col` ESC-7, ESC-8, ESC-9 | the SUSv2 spellings of reverse, half-reverse and half-forward line feed: [Control characters](../../02_Characters/control_characters/README.md) | |
| `col` *shift in*, *shift out* | `0x0f` and `0x0e`, the ISO 2022 alternate-character-set switches, which `col` tracks and re-emits | |

### `pr(1)` and `ul(1)`: a 2004 page that admits it, and the overstrike format going the other way

`pr` is the pagination filter, and its BUGS section says in one sentence what the rest of the family leaves to measurement: *The pr utility does not recognize multibyte characters.* Two-column output at width 9 truncates `café` to `caf` plus the lead byte of `é` on this Mac; GNU `pr` keeps the character. `ul` is `col -b` in reverse: it reads the same `_`-backspace-`x` format and writes the terminal's own underline sequence for it, looked up by `TERM`, so `printf '_\bx\n' | ul -t vt100` prints `ESC [ 4 m x ESC [ m` on both machines. That sequence is the [terminal escape family](../../06_Terminal/terminal_hyperlinks/README.md) doing what a 1970s printer did with a backspace.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| `pr -L locale` | a per-run locale, unique in this family | |
| `pr -w width` *column positions* | for multi-column output only; single-column lines are never truncated | `pr -t -2 -w 9`: `caf\xc3 xyz` on the Mac, `café  xyz` on Ubuntu |
| `ul -i` *a separate line containing appropriate dashes* | underline as a second line, for terminals that cannot | on Ubuntu `ul` needs `TERM` set even for `-i` |
| `ul` *degenerates to cat(1)* | if the terminal overstrikes natively, the backspaces pass through | |

### `rev(1)` and `wc(1)`: the shortest page and the page with a definition of *word*

```text title="man 1 wc, macOS 26.6.2, dumped 2026-09-13"
     A word is defined as a string of characters delimited by white space
     characters.  White space characters are the set of characters for which
     the iswspace(3) function returns true.
     ...
     -m      The number of characters in each input file is written to the
             standard output.  If the current locale does not support
             multibyte characters, this is equivalent to the -c option.
```

`wc` is honest about all three of its units: `-c` is bytes, `-m` is characters *if the locale has any*, and a word ends wherever `iswspace(3)` says, which is the locale's table, not ASCII's. On both machines a no-break space counts as a separator in a UTF-8 locale and not in `C`; the ideographic space `U+3000` separates words on Ubuntu and not on this Mac. `-L` is the one unit the two implementations define differently: the BSD page says *bytes (default) or characters (when -m is provided)*, and GNU counts display columns, so `wc -L` on `中文` is 6 here and 4 there. `rev(1)` has no ENVIRONMENT section, no STANDARDS section and no BUGS section, and reverses *the order of characters in every line*; which characters is [Logical and visual order](../../02_Characters/logical_and_visual_order/README.md) (it reverses code points, not glyphs, so a combining mark ends up on the wrong base) and, in the `C` locale, bytes, the one case in the tools chapter where `LC_ALL=C` is the cause of the damage rather than the escape from it.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| `wc -c` *cancel out any prior usage of the -m option* | `-c` and `-m` are one counter with two units; `wc -cm` reports only `-m` | |
| `wc -L` | longest line, in bytes or (with `-m`) characters; GNU: columns | `中文`: 6 bytes, 2 characters, 4 columns |
| `wc` *until receiving EOF, or [^D] in most environments* | `^D` is the terminal's `eof` character; it makes the driver return the line, and an empty line is EOF: [`tty(4)` and `stty(1)`](tty.md) | |
| `rev` *reversing the order of characters* | code points in a UTF-8 locale, bytes in `C` | Ubuntu's `rev` under `LC_ALL=C` never returns on `café` |

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| *column position* | one terminal cell; a character takes 0, 1 or 2 of them by `wcwidth(3)`, and a tab advances to the next multiple of 8 | [`wcwidth(3)`](wcwidth.md) |
| *multi-byte character* | one character spelt as several bytes; only a locale with `MB_CUR_MAX > 1` has any | [`multibyte(3)`](multibyte.md) |
| `LC_CTYPE` | the locale category that decides what a character is and which bytes make one | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `[:class:]` | a named set from `ctype(3)`: `alpha`, `space`, `print` ... whose members depend on the locale | [`ctype(3)`](ctype.md) |
| `[=equiv=]` | an equivalence class: every character the collation treats as a variant of `e` | [`strcoll(3)` and collation](collation.md) |
| *collation sequence*, *collating order* | the locale's idea of alphabetical order; byte order in `C` | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| `iswspace(3)` | the wide-character test for white space, which is why `wc -w` changes with the locale | [`ctype(3)`](ctype.md) |
| *reverse line feed*, *half line feed* | printer carriage motions, `ESC 7`, `ESC 8`, `ESC 9`, that `col` turns into ordinary lines | [Control characters](../../02_Characters/control_characters/README.md) |
| backspace overstrike | `c BS c` for bold and `_ BS c` for underline; the format `man` writes and `col -b` and `ul` read | [`man(1)` and `mandoc(1)`](man.md) |
| *shift in*, *shift out* | `SI` (`0x0f`) and `SO` (`0x0e`), the switches between a normal and an alternate character set | [Code pages](../../02_Characters/code_pages/README.md) |
| tab stop | a column at which a tab lands; every 8 unless `-t` says otherwise, so a tab has no width of its own | [Control characters](../../02_Characters/control_characters/README.md) |
| `\octal` | a byte value written in base 8, the one portable way to put a byte in an argument | [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) |
| `SIGINFO`, `^T` | the BSD status signal, sent by the terminal's `status` character; `wc` reports its interim count on it | [`tty(4)` and `stty(1)`](tty.md) |
| `libxo`, `--libxo` | FreeBSD's structured-output library; `wc --libxo` can print JSON | |
| `LINE_MAX` | the POSIX minimum maximum line length, 2048 bytes, which several BSD tools still enforce | |

## Try it on your machine

**The matrix.** One small input per tool, run under `LC_ALL=C` and under a UTF-8 locale (`en_US.UTF-8` on the Mac, `C.UTF-8` on Ubuntu, the only one the container has), output shown as hex. The cast: `café` is `63 61 66 c3 a9`, `naïve` has `c3 af`, `Łódź` is `c5 81 c3 b3 64 c5 ba`, `中文字` is three 3-byte characters of width 2, and `😀` is `f0 9f 98 80`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD tools) and ubuntu:24.04 (GNU coreutils 9.4, util-linux 2.39.3 col/colrm/rev/ul). Not machine-checked: no key can match both."
                                        macOS C          macOS UTF-8        Ubuntu C           Ubuntu C.UTF-8
tr '[:lower:]' '[:upper:]'  café        434146c3a9 CAFé  434146c389 CAFÉ    434146c3a9 CAFé    434146c3a9 CAFé
tr '[=e=]' e                café        636166c3a9       63616665   cafe    636166c3a9         636166c3a9
tr -d 'é'                   naïve       6e61af7665       6e61c3af7665       6e61af7665         6e61af7665
cut -c1-4                   café        636166c3         636166c3a9         636166c3           636166c3
cut -b1-4 -n                café        636166c3         636166     caf     636166c3           636166c3
fold -w 4                   中文字      (no break)       中文|字            e4b8ade6|9687e5ad|97  same as C
fold -w 4                   😀😀😀      (no break)       😀😀|😀            😀|😀|😀           same as C
fold -w 4                   Łódź        (no break)       (no break)         Łó|dź              Łó|dź
fmt -w 10                   café naïve  caf nave         café naïve         café|naïve         café|naïve
expand                      é<TAB>x     é + 8 spaces     é + 7 spaces       é + 6 spaces       é + 6 spaces
unexpand -a                 é+7sp+x     unchanged        c3a90978 é<TAB>x   c3a9092078         c3a9092078
col -b                      é<BS>_      5f _             5f _               \xc3\xa_           5f _
col -b                      é           0a  (é gone)     c3a90a             \xc3\xa9           c3a90a
colrm 4 4                   café        636166c3a9       636166 caf         636166 caf         636166 caf
colrm 2 2                   中文字      unchanged        文字               (nothing)          ' 文字'
pr -t -2 -w 9               café / xyz  caf\xc3 xyz      caf\xc3 xyz        café  xyz          café  xyz
ul -t vt100                 _<BS>x      1b5b346d781b5b6d  same              same               same
rev                         café        a9c3666163       c3a9666163         (never returns)    c3a9666163
rev                         Łódź        bac564b3c381c5   c5ba64c3b3c581     (never returns)    c5ba64c3b3c581
wc -m                       café\n      6                5                  6                  5
wc -L                       中文        6                6                  0                  4
wc -mL                      中文        7 6              3 2                7 0                3 4
wc -w                       a<NBSP>b    1                2                  1                  2
wc -w                       a<U+3000>b  1                1                  1                  2
```

Four rows are the family's story. `tr`, `cut -c`, `fold` and `colrm` keep their page's promise on the Mac in a UTF-8 locale and nowhere else: the GNU column is byte arithmetic top to bottom, and it is the same in both locales because those programs never ask. `fmt` and `col` in the `C` locale on the Mac do not count the bytes they cannot classify, they *delete* them, which no page says. And `rev` on Ubuntu under `LC_ALL=C` did not finish in ten seconds on a five-byte line, on either input; `timeout` killed it with status 124, and it reverses `abc` instantly. The `C`-locale row for `rev` on the Mac is the one [the tools chapter measured](../../11_Tools/README.md): the bytes of `é` come back in the wrong order, and the output is no longer UTF-8.

**The `-n` flag, which only one `cut` implements.**

```text title="Measured 2026-09-13 — macOS 26.6.2, LC_ALL=en_US.UTF-8. Not machine-checked."
$ printf 'café\n' | cut -b1-4 -n | xxd -p
636166
$ printf 'café\n' | cut -b4-5 -n | xxd -p
c3a9
```

Byte 4 alone is not a character, so `-n` drops it; bytes 4 and 5 together are `é`, so `-n` keeps them. This is the page's *after a prefix of zero or more unselected bytes, the rest of the bytes that form the character are selected*, and it is the only byte-selection flag in the family that cannot produce invalid UTF-8. Ubuntu prints `636166c3` for the first command.

**What `col -b` does to a page under the wrong locale.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
$ printf 'é\n' | LC_ALL=C col -b | xxd -p
0a                          macOS: the character is discarded as an unrecognised control
5c7863335c7861390a          Ubuntu: the two bytes are respelt as the text \xc3\xa9
$ printf 'é\n' | LC_ALL=en_US.UTF-8 col -b | xxd -p     (LC_ALL=C.UTF-8 on Ubuntu)
c3a90a                      both: unchanged
```

## Where the pages are dated, and what they do not say

**`tr(1)` is dated October 13, 2006** and says equivalence classes and collated ranges are *single byte locales only*. On this Mac `[=e=]` matches `é` in a UTF-8 locale, so the page is more cautious than the program. It does not say that a non-ASCII character in `string1` is a set of bytes in the `C` locale, which is the damage [the `tr` lesson](../../11_Tools/tr_and_sort/README.md) is named for, and it does not say that GNU `tr` behaves as if every locale were single-byte.

**`pr(1)` is dated July 3, 2004** and its BUGS line is still true of the BSD program and false of the GNU one. **`cut(1)` (2017)** documents `-n`, which GNU `cut` accepts and ignores. **`fold(1)` (2020)** says *columns* and GNU `fold` counts bytes.

**No page in the family says what happens to a byte the locale cannot decode.** Measured today: `fmt` deletes it, BSD `col` deletes it, util-linux `col` respells it, `cut -c` on the Mac prints `cut: stdin: Illegal byte sequence` and exits 1 (GNU `cut -c` passes the byte through), and util-linux `rev` does not return. Three different silent outcomes and one hang, and the ENVIRONMENT sentence the pages share does not distinguish them; [What the page does not say](../what_the_page_does_not_say/README.md) is the general rule.

**`rev(1)` has no ENVIRONMENT section at all**, on a tool whose output is decided by the locale.

**`wc(1)` says `^D` is EOF** *in most environments*. It is the terminal's `eof` character, which makes the line discipline hand over the line typed so far; a zero-length read is what EOF actually is. The measurement is on [`tty(4)` and `stty(1)`](tty.md).

**`ul(1)` reads `/etc/termcap`**, says the page; this Mac has no such file (`ls /etc/termcap` fails), and `ul -t vt100` still worked.

## See also

- [`cat(1)`, `sort(1)`, `xargs(1)` and the line tools](lines_and_fields.md) — the other eighteen pages, cut on lines and delimiters instead of columns
- [`wcwidth(3)`](wcwidth.md) — the function behind *column position* in `fold`, `colrm` and GNU `wc -L`
- [`ctype(3)`](ctype.md) — the classes `tr` names and the `iswspace` that `wc -w` uses
- [`man(1)` and `mandoc(1)`](man.md) — the overstrike format that `col -b` strips and `ul` renders
- [`multibyte(3)`](multibyte.md) — what a *multi-byte character* is to the C library these tools call
- [`cut` counts what it is told to count](../../11_Tools/cut/README.md) — the `-b`/`-c` measurement, and the fixed-width record it bites
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) — `tr -d 'é'` damaging the word next door
- [The shell has no string type](../../11_Tools/sh/README.md) — the same question inside `${#var}`, with no tool involved
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) — bytes, code points and columns as three of the five rulers
- [Where a line may break](../../02_Characters/where_a_line_may_break/README.md) — what `fold` and `fmt` would need to know and do not
- [Logical and visual order](../../02_Characters/logical_and_visual_order/README.md) — why `rev` reverses the wrong thing for Hebrew and for combining marks
- [What the page does not say](../what_the_page_does_not_say/README.md) — the gaps listed above, as a habit of reading
