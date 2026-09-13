# `man(1)`, `mandoc(1)` and `mandoc_char(7)`: the manual is ASCII source that chooses its encoding when you read it

**Level:** reference · for anyone who has typed `man man` and wanted to know where the bold went when they piped it

**One line:** A man page is a text file in which `é` is spelt `\('e` and `€` is `\(Eu`, and the formatter decides at run time from `LC_CTYPE` whether to print `é` or `'e`, `€` or `EUR`, so the same page holds 1,040 non-ASCII bytes under a UTF-8 locale and none under `C`; bold arrives as `N`, backspace, `N` on this Mac and is stripped on Ubuntu, which is why this folder's dumps go through `col -bx`.

**The pages:** [`man(1)`](raw/macos/man.1.txt) (macOS 26.6.2, dated January 9, 2021; it also documents `apropos` and `whatis`) · [`mandoc(1)`](raw/macos/mandoc.1.txt) (August 14, 2021) · [`mandoc_char(7)`](raw/macos/mandoc_char.7.txt) (October 31, 2020). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). Ubuntu's `man-db 2.12.0` with `groff 1.23.0` was measured beside them from [`dump_linux.sh`](dump_linux.sh)'s container; it has no `mandoc` and no `mandoc_char(7)`.

## What the pages are for

Every page in this folder was made by the programs these three pages describe, so this is the family that explains the others' bytes. `man(1)` is the front door: it finds a page by name and section along `MANPATH`, runs it through a formatter, and hands the result to a pager, and on this Mac `man -d` shows the whole pipeline in one line, `zcat -f page | /usr/bin/mandoc | /usr/bin/less -s`. `mandoc(1)` is the formatter, the OpenBSD replacement for `nroff` that this Mac runs; its page is mostly diagnostics, but its `-T` section is where the output encoding is decided. `mandoc_char(7)` is the table of escape sequences a page author writes instead of typing a character the source file cannot hold.

That last point is the reason the family is in an encodings library. Manual sources are written in `roff`, a 1970s markup whose input was assumed to be ASCII, so a page that needs an `é`, an en-dash or a euro sign has to *escape into ASCII*: `\('e`, `\(en`, `\(Eu`, or since Unicode `\[u00E9]`. That is the fourth of the schemes on [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md), and `\[uXXXX]` is another way to [write a code point](../../02_Characters/writing_a_code_point/README.md). The formatter then does at render time what an encoder does at write time: it looks at `LC_CTYPE`, and prints either the UTF-8 bytes or an ASCII approximation, `'e`, `-`, `EUR`.

Two implementations again. Ubuntu has `man-db` and `groff`, which choose a groff *device* (`utf8` or `ascii`) the same way and by default strip all formatting when the output is not a terminal; the Mac's `man` keeps the backspace overstrikes in a pipe, which is what [`col -b`](columns_and_characters.md) is for and what [`dump.sh`](dump.sh) runs. The rest of the library's chapter 13 is about what these pages contain; this page is about how they get from a file to your screen: [The encoding man pages nobody opens](../the_encoding_man_pages/README.md).

## The pages, with notes

### `man(1)`: finding a page

```text title="man 1 man, macOS 26.6.2, dumped 2026-09-13"
     -S mansect
             Restricts manual sections searched to the specified colon
             delimited list.  Defaults to "1:8:2:3:3lua:n:4:5:6:7:9:l".
             Overrides the MANSECT environment variable.
     ...
     -w      Display the location of the manual page instead of the contents
             of the manual page.
```

`man printf` gives you `printf(1)` because `1` is first in that list; `man 3 printf` or `man -S 3 printf` gives you the C function; `man -w` says which file was found without showing it, and on this Mac the answer is usually under `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/share/man`, where the SDK keeps most of the system's pages (`utf8.5`, `man.1`, `stty.1` and `tty.4` all resolve there; `mandoc.1` is in `/usr/share/man`). `-k` and `-f` turn `man` into `apropos` and `whatis`, which search a pre-built index of NAME lines rather than the pages; `-P` names the pager, and `MANWIDTH` overrides the 78 columns the formatter assumes when it is not talking to a terminal.

```text title="man 1 man, macOS 26.6.2, dumped 2026-09-13"
   Locale Specific Searches
     The man utility supports manual pages in different locales.  The search
     behavior is dictated by the first of three environment variables with a
     nonempty string: LC_ALL, LC_CTYPE, or LANG.  If set, man will search for
     locale specific manual pages using the following logic:

           lang_country.charset
           lang.charset
           en.charset
```

The locale reaches `man` twice. Here it chooses which *directory* to look in, so a Japanese page for `ls` would live in `ja_JP.eucJP/man1`; and, one process later, `LC_CTYPE` chooses which *bytes* `mandoc` writes. The example on the page is `ja_JP.eucJP`, one of the [CJK encodings](cjk_encodings.md), and the directory name carries the charset because the page inside is in it.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| *The sections of the manual are: 1. General Commands ... 9. Kernel Developer's* | the nine sections; encodings are file formats, section 5, on BSD | |
| `-M manpath`, `MANPATH`, `manpath(1)` | the search path; a leading or trailing colon adds to the default instead of replacing it | `manpath` on this Mac lists seven directories |
| `-k keyword`, `apropos` | regular-expression search of the `whatis` index | `apropos mandoc_char` finds the page; `man -k utf8` finds Perl and OpenSSL pages named after it |
| `-P pager`, `MANPAGER`, `PAGER` | the display program; `less -s` by default | `man -P cat 5 utf8` keeps the backspaces (see below) |
| `MANWIDTH` | the formatting width when set to a number | `MANWIDTH=40 man 1 rev` renders a 40-column page |
| `-m arch` | *accepted, but not implemented, on macOS* | |
| `-t` *through troff(1)*, `-p [eprtv]` *before running nroff(1)* | the page describes a `troff` pipeline; the machine runs `mandoc` | `man -d` shows `zcat -f ... | /usr/bin/mandoc | /usr/bin/less -s` |

### `mandoc(1)`: the output formats

```text title="man 1 mandoc, macOS 26.6.2, dumped 2026-09-13"
     -T output
             Select the output format.  Supported values for the output
             argument are ascii, html, the default of locale, man, markdown,
             pdf, ps, tree, and utf8.
     ...
   ASCII Output
     Use -T ascii to force text output in 7-bit ASCII character encoding
     documented in the ascii(7) manual page, ignoring the locale(1) set in the
     environment.

     Font styles are applied by using back-spaced encoding such that an
     underlined character `c' is rendered as `_\[bs]c', where `\[bs]' is the
     back-space character number 8.  Emboldened characters are rendered as
     `c\[bs]c'.  This markup is typically converted to appropriate terminal
     sequences by the pager or ul(1).  To remove the markup, pipe the output
     to col(1) -b instead.
```

That paragraph is the recipe this folder uses, in the formatter's own words: bold is the character twice with a backspace between, underline is underscore, backspace, character, and `col -b` removes both. The pager (`less`) is what turns them into terminal attributes when you read a page interactively, and [`ul(1)`](columns_and_characters.md) does the same job for terminals `less` does not know.

```text title="man 1 mandoc, macOS 26.6.2, dumped 2026-09-13"
   Locale Output
     By default, mandoc automatically selects UTF-8 or ASCII output according
     to the current locale(1).  If any of the environment variables LC_ALL,
     LC_CTYPE, or LANG are set and the first one that is set selects the UTF-8
     character encoding, it produces UTF-8 Output; otherwise, it falls back to
     ASCII Output.
     ...
ENVIRONMENT
     LC_CTYPE  The character encoding locale(1).  When Locale Output is
               selected, it decides whether to use ASCII or UTF-8 output
               format.  It never affects the interpretation of input files.
```

Two decisions, kept apart. Output encoding is the locale's, and only ever UTF-8 or ASCII; `-T utf8` and `-T ascii` force one or the other. Input encoding is *never* the locale's: `-K` sets it, and without `-K` the page describes a four-step autodetection, a UTF-8 [byte order mark](../../03_Encodings/byte_order_and_bom/README.md) first, then an Emacs `coding:` line, then *if the first non-ASCII byte introduces a valid UTF-8 sequence*, and otherwise Latin-1. That is the same guess [`file`](../../06_Terminal/file_guesses/README.md) makes, written down as a rule, and a source file that contains a raw non-ASCII byte gets the diagnostic *skipping bad character*, which is why page authors escape instead.

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| `-T utf8` *force text output in UTF-8 multi-byte character encoding* | the same layout as `-T ascii` with the characters filled in | `\(Eu` becomes `e2 82 ac`; `\[u1F600]` becomes `f0 9f 98 80` |
| `-T html` *Non-ASCII characters are rendered as hexadecimal Unicode character references* | `&#x00E9;` for `é`: HTML's own escape into ASCII | measured: `caf&#x00E9; for 5&#x00A0;&#x20AC;` |
| `-T markdown` *encoded as HTML entities ... transliterated to ASCII approximations* in code spans | Markdown output is ASCII too | measured: `caf&#233;`, `&#8364;`, `&#380;&#243;&#322;w` |
| `-O width=width` *instead of the default of 78* | the width `dump.sh` relied on; `man` passes `MANWIDTH` through it | |
| `-K encoding` *us-ascii, iso-8859-1, and utf-8* | the three input encodings a page may be written in | |
| *skipping bad character ... replaced with a question mark* | a raw byte outside printable ASCII in the source | |
| `-T lint`, `-W level` | the checker; `-W style` reports `verbatim "--", maybe consider using \(em` | |

### `mandoc_char(7)`: how a page spells a character

```text title="man 7 mandoc_char, macOS 26.6.2, dumped 2026-09-13"
     In ASCII output, the rendering of some characters may be hard
     to interpret for the reader.  Many are rendered as descriptive strings
     like "<integral>", "<degree>", or "<Gamma>", which may look ugly, and
     many are replaced by similar ASCII characters.  In particular, accented
     characters are usually shown without the accent.
     ...
SPECIAL CHARACTERS
     Special characters are encoded as `\X' (for a one-character escape),
     `\(XX' (two-character), and `\[N]' (N-character).
```

Three spellings, by length of name: `\-` for a minus, `\(en` for an en-dash, `\[bracketlefttp]` for a drawing piece. The table that follows is the page's bulk and is organised by kind, and the *Rendered* column is what `-T ascii` prints: `\(en` is `-`, `\(em` is `--`, `\(Eu` is `EUR`, `\(:e` is `e`, `\(ss` is `ss`. In UTF-8 output every one of those becomes the character itself, which the dump in `raw/` cannot show, because the dump is the ASCII rendering. The two rows below were re-rendered under `en_US.UTF-8` for this page.

```text title="man 7 mandoc_char, macOS 26.6.2, dumped 2026-09-13"
UNICODE CHARACTERS
     The escape sequences

           \[uXXXX] and \C'uXXXX'

     are interpreted as Unicode codepoints.  The codepoint must be in the
     range above U+0080 and less than U+10FFFF.  For compatibility, the
     hexadecimal digits `A' to `F' must be given as uppercase characters, and
     points must be zero-padded to four characters; if greater than four
     characters, no zero padding is allowed.  Unicode surrogates are not
     allowed.
```

The modern escape: any code point by number, with a spelling rule stricter than most languages' (uppercase hex, exactly four digits or exactly as many as needed) and the surrogate exclusion that [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) explains. The NUMBERED CHARACTERS section beneath it, `\N'34'` and `\[char34]`, is the older way, *inserting the character number from the current character set*, which the page calls *inherently non-portable*: a number without a table is [a byte with no code page](../../02_Characters/code_pages/README.md).

| On the page | What it means | Measured 2026-09-13 |
|---|---|---|
| *do not use special-character escape sequences to represent national language characters in author names* | the ASCII fallback would mangle them, so the page asks for transliteration up front | |
| `\(en`, `\(em`, `\-`, plain `-` | en-dash, em-dash, minus, hyphen; the page says plain `-` is enough for all three in manual pages | under UTF-8 the hyphen itself renders as `U+2010`, `e2 80 90` |
| `\~`, `\ `, `\&` | paddable and unpaddable non-breaking spaces, and the zero-width space that protects a leading `.` | `\~` renders as `U+00A0` in UTF-8 and as a space in ASCII |
| `` ` `` and `'` | *converted to U+2018 and U+2019* in some output modes; `\(ga` and `\(aq` force the ASCII ones | |
| `\(Eu`, `\(eu` | the euro, twice, both `EUR` in ASCII | `€` in UTF-8 |
| `\('e`, `\(:e`, `\(/l` | accented letters by two-letter name | in ASCII: `'e`, `e`, `/l`; in UTF-8: `é`, `ë`, `ł` |

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| `roff`, `nroff`, `troff` | the 1970s typesetting language and its terminal and printer formatters; `mandoc` reads the language and replaces both | |
| `mdoc(7)`, `man(7)` | the two macro packages a page is written in: BSD's semantic one and the older presentational one | |
| macro, request | a line starting with `.`: `.Dd` date, `.Nm` name, `.Sh` section | |
| escape sequence (`\X`, `\(XX`, `\[N]`) | a character named in ASCII instead of typed | [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) |
| `\[uXXXX]` | a Unicode code point by number, uppercase hex | [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| back-spaced encoding, overstrike | `c BS c` for bold, `_ BS c` for underline; a printer's way of doing both | [Control characters](../../02_Characters/control_characters/README.md) |
| `-T locale` | choose UTF-8 or ASCII output by `LC_CTYPE` | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `-K`, input encoding, BOM, emacs mode line | how the formatter decides what the *source* is in; never the locale | [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) |
| pager | the program that shows a page one screen at a time and turns overstrikes into bold: `less` | [`stdio(3)`](stdio.md) |
| `whatis` database, `makewhatis` | the index of NAME lines that `apropos` and `man -k` search | |
| `MANPATH`, `manpath(1)` | the list of directories searched, and the tool that prints it | |
| section (`1` ... `9`, `3lua`, `l`) | which manual a name is in; `-S` orders the search | [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) |
| catpage | a pre-formatted copy of a page, which `man -d` reports *not found or old* | |
| `Dd`, `Os`, footer date | the page's own date, printed on its last line | [A page has a date](../a_page_has_a_date/README.md) |
| SGR, `ESC [ 1 m` | the terminal escape for bold that `groff` emits where `mandoc` emits a backspace | [`tty(4)` and `stty(1)`](tty.md) |
| `MAN_KEEP_FORMATTING` | man-db's switch to keep formatting in a pipe; not on these pages | |

## Try it on your machine

**Where the bold goes.** Line 3 of a page is the word `NAME` in bold, read here into a pipe.

```text title="Measured 2026-09-13 — macOS 26.6.2 (man + mandoc) and ubuntu:24.04 (man-db 2.12.0 + groff 1.23.0, via /usr/bin/man.REAL). Not machine-checked."
$ man 5 utf8 | sed -n 3p | od -c                                       macOS
0000000    N  \b   N   A  \b   A   M  \b   M   E  \b   E  \n
$ man 5 utf8 | col -bx | sed -n 3p | od -c                             macOS
0000000    N   A   M   E  \n
$ man.REAL -P cat 7 utf-8 | sed -n 3p | od -c                          Ubuntu
0000000   N   A   M   E  \n
$ MAN_KEEP_FORMATTING=1 man.REAL -P cat 7 utf-8 | sed -n 3p | od -c    Ubuntu
0000000 033   [   1   m   N   A   M   E 033   [   0   m  \n
```

The Mac writes the overstrike format into the pipe and leaves the stripping to you; `man-db` strips everything when its output is not a terminal, and when told to keep it, keeps `groff`'s SGR escape sequences rather than backspaces. `col -bx` is therefore essential on the Mac and a no-op for bold on Ubuntu, where [`dump_linux.sh`](dump_linux.sh) runs it anyway for the tabs.

**A six-line page, rendered five ways.** The source uses one escape of each kind.

```text title="Measured 2026-09-13 — macOS 26.6.2, mandoc; the last two lines from ubuntu:24.04, groff. Not machine-checked."
$ cat enclab.7
.Dd September 13, 2026
.Dt ENCLAB 7
.Os
.Sh NAME
.Nm enclab
.Nd caf\('e for 5\~\(Eu, \[u017C]\('o\[u0142]w, pp.\ 95\(en97 \(em and ``quotes''

$ mandoc -T ascii enclab.7 | col -b | grep caf
     enclab - caf'e for 5 EUR, z'o/lw, pp. 95-97 -- and ``quotes''
$ mandoc -T utf8 enclab.7 | col -b | grep caf
     enclab – café for 5 €, żółw, pp. 95–97 — and ``quotes''
$ mandoc -T markdown enclab.7 | grep caf
**enclab** - caf&#233; for 5&#160;&#8364;, &#380;&#243;&#322;w, pp.&#160;95&#8211;97 &#8212; and \`\`quotes''
$ mandoc -T html enclab.7 | grep caf
    <span class="Nd">caf&#x00E9; for 5&#x00A0;&#x20AC;,
$ LC_ALL=C man ./enclab.7 | grep caf; LC_ALL=en_US.UTF-8 man ./enclab.7 | grep caf
     enclab - caf'e for 5 EUR, z'o/lw, pp. 95-97 -- and ``quotes''
     enclab – café for 5 €, żółw, pp. 95–97 — and ``quotes''
$ LC_ALL=C man.REAL -l enclab.7 | grep caf; LC_ALL=C.UTF-8 man.REAL -l enclab.7 | grep caf     Ubuntu
       enclab -- cafe for 5 EUR, zolw, pp. 95-97 -- and ``quotes''
       enclab — café for 5 €, żółw, pp. 95–97 — and ``quotes''
```

The same six lines, and the ASCII rendering is different on the two machines: `mandoc` keeps an accent mark as a prefix (`caf'e`, `z'o/lw`) and `groff` drops it (`cafe`, `zolw`), the page's *usually shown without the accent*. Markdown and HTML are ASCII too, with the character as a decimal or hex entity. `\[u1F600]`, tested separately, renders as `<?>` in ASCII and as `f0 9f 98 80` in UTF-8, and `\(:e` renders as `e` in ASCII and `ë` in UTF-8.

**How many bytes the locale changes.** The number of bytes above `0x7f` in two whole pages, under `C` and under a UTF-8 locale.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
$ LC_ALL=C           man 7 mandoc_char | LC_ALL=C tr -d '\000-\177' | wc -c       0        macOS
$ LC_ALL=en_US.UTF-8 man 7 mandoc_char | LC_ALL=C tr -d '\000-\177' | wc -c    1040        macOS
$ LC_ALL=C           man.REAL -P cat 7 utf-8 | LC_ALL=C tr -d '\000-\177' | wc -c   0      Ubuntu
$ LC_ALL=C.UTF-8     man.REAL -P cat 7 utf-8 | LC_ALL=C tr -d '\000-\177' | wc -c  78      Ubuntu
$ LC_ALL=en_US.UTF-8 sh -c 'man 7 mandoc_char | col -bx' | grep -E 'Eu  |:e  '                macOS
           \(:e     ë           dieresis e
           \(Eu     €           Euro symbol
$ grep -E 'Eu  |:e  ' raw/macos/mandoc_char.7.txt
           \(:e     e           dieresis e
           \(Eu     EUR         Euro symbol
```

The dumps in `raw/` are the second version: the `C`-locale rendering, all ASCII, which is the reason `col -bx` was safe to run on them. The `col` page's *All unrecognized control characters and escape sequences are discarded* applies to a byte above `0x7f` in the `C` locale, so a UTF-8 rendering piped through `LC_ALL=C col -b` on this Mac would have lost every `é`; the measurement is on [`col(1)`](columns_and_characters.md). Run `col` under the locale you rendered with.

## Where the pages are dated, and what they do not say

**`man(1)` is dated January 9, 2021** and describes a `nroff`/`troff` pipeline with `-t` and `-p [eprtv]` preprocessors, while `man -d` on this machine shows `mandoc` and no preprocessor at all. It documents `-m arch` as *accepted, but not implemented, on macOS*, the one line that admits which system it is on. It does not say that its output keeps overstrikes when piped, and does not mention `MAN_KEEP_FORMATTING`, which is man-db's and not FreeBSD's.

**`mandoc(1)` is dated August 14, 2021** and says `-T markdown` output *almost conforms* to CommonMark and that `-T pdf` and `-T ps` render special characters *as in ASCII Output*, so a PDF of `mandoc_char(7)` prints `EUR`. It documents `-T utf8` in three sentences and does not say what happens to a code point the ASCII table has no approximation for; the answer, measured, is `<?>`.

**`mandoc_char(7)` is dated October 31, 2020**, and its *Rendered* column does not match this `mandoc` for accented letters: the table says `\('e` renders as `e`, and the program prints `'e`. It says the euro is `EUR`, which it is, in ASCII, PostScript and PDF. It has no row for the byte order mark, the no-break space it does list (`\~`) becomes `U+00A0` in UTF-8 output, and nothing on the page says which Unicode version its `\[uXXXX]` range is checked against.

**None of the three says what a section is for**, beyond the list of nine names; that BSD keeps encodings in section 5 as file formats and Linux in section 7 as miscellany is on [The encoding man pages nobody opens](../the_encoding_man_pages/README.md).

**Ubuntu has neither `mandoc` nor `mandoc_char(7)`**, and the `groff` equivalent, `groff_char(7)`, is not installed in the container either. Its `man --version` says `man 2.12.0`; this Mac's `man` has no version flag, `file /usr/bin/man` calls it a *POSIX shell script*, and its first comment line carries a FreeBSD licence tag.

## See also

- [`tr(1)`, `cut(1)`, `fold(1)`, `wc(1)` and the column tools](columns_and_characters.md) — `col -b` and `ul`, the two tools that read the overstrike format
- [`vis(1)` and `vis(3)`](vis.md) — the other ASCII escaping on this machine, and the one that reverses
- [`ascii(7)`](ascii.md) — the table `-T ascii` promises to stay inside
- [`utf8(5)` and `utf-8(7)`](utf8.md) — the pages whose bold this page's experiment counted
- [The index of this folder](README.md) — every family, and the `dump.sh` that made the raw text
- [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) — JSON, URLs, mail headers, domain names, and now `roff`
- [Writing a code point](../../02_Characters/writing_a_code_point/README.md) — `\[u017C]` beside `\u017c`, `\u{17c}` and `&#x17C;`
- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — the variable that chose between `é` and `'e`
- [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) — why `man-db` strips formatting and `less` does not
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) — what is in the pages this family renders
- [What the page does not say](../what_the_page_does_not_say/README.md) — the `<?>` and the missing accent, as a habit of checking
- [A page has a date](../a_page_has_a_date/README.md) — the footer line, and the 2021 page describing a `troff` that is not there
