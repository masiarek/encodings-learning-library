# `locale(5)`, `charmap(5)` and `localedef(1)`: the source code of a locale, on the one platform that ships it

**Level:** reference · for anyone who has wondered where `iconv //TRANSLIT` gets `EUR` for `€`, or where a program learns that `c3 a9` is `LATIN SMALL LETTER E WITH ACUTE`, and wanted the file shown to them

**One line:** On glibc a locale is compiled, by `localedef(1)`, from a text source in the format of `locale(5)` and a character map in the format of `charmap(5)`, and those two files are where the transliteration tables, the collation rules and the name-to-bytes table this library keeps referring to are actually written down; this Mac has a `localedef` binary and a page for it, and nothing for it to compile.

**The pages:** [`locale(7)`](raw/linux/locale.7.txt) (Linux man-pages 6.7, 2024-02-25) · [`locale(5)`](raw/linux/locale.5.txt) (2024-01-28) · [`charmap(5)`](raw/linux/charmap.5.txt) (2023-10-31) · [`repertoiremap(5)`](raw/linux/repertoiremap.5.txt) (2023-10-31) · [`localedef(1)`](raw/linux/localedef.1.txt) (2023-10-31). All dumped 2026-09-13 from ubuntu:24.04 by [`dump_linux.sh`](dump_linux.sh); the machine is in [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt). On macOS 26.6.2, `man -w 7 locale`, `man -w 5 locale`, `man -w 5 charmap` and `man -w 5 repertoiremap` all answer *No manual entry*; `man -w 1 localedef` finds a different, FreeBSD-derived page dated June 29, 2023, discussed at the end.

## What the pages are for

A glibc locale is not a setting, it is a build product. Someone wrote a text file called `pl_PL` in the language of `locale(5)`, one section per category, and a second text file called `UTF-8` in the language of `charmap(5)`, one line per character; `localedef(1)` read both and wrote the binary `LC_CTYPE`, `LC_COLLATE` and ten other files that `setlocale(3)` loads. `locale(7)` is the overview that names the categories, including the six glibc invented, and `repertoiremap(5)` describes an optional third input that the page itself calls deprecated. Four of the five pages sit in sections 5 and 7 because they describe file formats and a concept; only `localedef` is a command.

The reason a reader of this library should open them is that three things the other chapters treat as facts of nature turn out to be lines in these files. [What the page does not say](../what_the_page_does_not_say/README.md) found that no man page on the Mac documents `//TRANSLIT`; `locale(5)` is the page that documents its *data*, the `translit_start` section of an `LC_CTYPE` definition, and `locale(7)` is the page that says, in one sentence, that the tables are part of the locale. [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) calls the mapping from character names to bytes a *character map*; `charmap(5)` is that map as a file, `<U00E9> /xc3/xa9 LATIN SMALL LETTER E WITH ACUTE`, one line per character, one file per encoding, 233 of them in the container. And [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) says the order is data that may not be installed; the `LC_COLLATE` section of `pl_PL`, with its `collating-symbol <l-stroke>` and `reorder-after` lines, is that data.

This is a Linux-only family. The Mac ships compiled locales under `/usr/share/locale/` and nothing to compile them from, which is why its `utf8(5)` page's SEE ALSO points at a `mklocale(1)` that is not there (the [`utf8(5)`](utf8.md) page measured that), and why the experiments here all run in the container.

## The page, with notes

### `locale(7)`: the categories, the extra six, and the sentence about `iconv`

```text title="man 7 locale, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       LC_CTYPE
              This  category determines the interpretation of byte sequences
              as characters  (e.g.,  single  versus  multibyte  characters),
              character classifications (e.g., alphabetic or digit), and the
              behavior  of  character classes.  On glibc systems, this cate‐
              gory also determines the character transliteration  rules  for
              iconv(1) and iconv(3).  It changes the behavior of the charac‐
              ter  handling and classification functions, such as isupper(3)
              and toupper(3), and the multibyte character functions such  as
              mblen(3) or wctomb(3).
```

The fourth sentence is the one the Mac's forty encoding pages lack. `iconv -t ASCII//TRANSLIT` does not carry its own table; it asks the current `LC_CTYPE` for one, which is why the experiment below gets `?` for `ż` under `LC_ALL=C` and `z` under `C.UTF-8` from the same command on the same bytes. The page lists twelve categories, marks `LC_ADDRESS`, `LC_IDENTIFICATION`, `LC_MEASUREMENT`, `LC_NAME`, `LC_PAPER` and `LC_TELEPHONE` as *GNU extension, since glibc 2.2*, gives the three-step rule for `setlocale(LC_ALL, "")` that the [`setlocale(3)`](locale.md) page quotes from the Mac, and documents one variable the Mac has no equivalent of: `LOCPATH`, *a list of pathnames, separated by colons (':'), that should be used to find locale data*. It is how a user without root installs a locale, and every Polish result on this page and on the [`locale(1)`](locale.md) page was obtained through it.

### `locale(5)`: the source format, and where `//TRANSLIT` lives

```text title="man 5 locale, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       The  locale  definition  has one part for each locale category.  Each
       part can be copied from another existing locale  or  can  be  defined
       from  scratch.  If the category should be copied, the only valid key‐
       word in the definition is copy followed by the name of the locale  in
       double  quotes  which should be copied.  The exceptions for this rule
       are LC_COLLATE and LC_CTYPE where a copy statement can be followed by
       locale-specific rules and selected overrides.
```

`copy` is the reason a real locale file is short. `pl_PL`'s `LC_CTYPE` section is six lines: `copy "i18n"` takes the whole Unicode character classification from a shared file, and the rest is the transliteration block. Almost every glibc locale does the same, which means the answer to *what does `isalpha` say about `ż` in Polish* is not in `pl_PL` at all but in `i18n`, and is the same answer in German.

```text title="man 5 locale, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       translit_start
              marks  the  start  of  the transliteration rules section.  The
              section can contain the include keyword in the beginning  fol‐
              lowed by locale-specific rules and overrides.  Any rule speci‐
              fied  in  the locale file will override any rule copied or in‐
              cluded from other files.  In case of  duplicate  rule  defini‐
              tions in the locale file, only the first rule is used.

              A  transliteration rule consist of a character to be translit‐
              erated followed by a list of transliteration targets separated
              by semicolons.  The first target which can be presented in the
              target character set is used, if none of them can be used  the
              default_missing character will be used instead.
```

This is `//TRANSLIT`, documented. A rule is a source character and a semicolon-separated list of fallbacks; the converter takes the first one the target encoding can hold, and `default_missing`, `?` in glibc's `C` source, when none can. The `include` keyword is why the rules are not in `pl_PL` either: it pulls in `translit_combining`, a 95 KB file whose line 1729 says `<U00E9> <U0065>` and whose line 1979 says `<U017C> <U007A>`, and the source file `C`, from which the container's `C.utf8` is compiled, pulls in `translit_neutral`, whose line 572 says `<U20AC> "<U0045><U0055><U0052>"`. That is `é` to `e`, `ż` to `z` and `€` to `EUR`, as three lines of text. The [`iconv(1)`](iconv.md) page shows the same rules from the converter's side; this is the side where you can edit them.

The rest of the page is the keyword list for each category: `upper`, `lower`, `alpha`, `digit`, `space`, `cntrl`, `punct`, `graph`, `print`, `xdigit`, `blank`, `toupper`, `tolower` for `LC_CTYPE`, which are the classes of [`ctype(3)`](ctype.md) as data; `collating-symbol`, `reorder-after` and `order_start` for `LC_COLLATE`; `decimal_point`, `thousands_sep` and `grouping` for `LC_NUMERIC`, the fields [`localeconv(3)`](locale.md) returns; `abday`, `d_fmt` and `era` for `LC_TIME`. Every value `locale -k` prints has a keyword here, spelled the same way.

### `charmap(5)`: names to bytes

```text title="man 5 charmap, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       <character> byte-sequence comment
              This form defines exactly one character and its byte sequence,
              comment being optional.

       <character>..<character> byte-sequence comment
              This  form  defines  a  character range and its byte sequence,
              comment being optional.
       ...
EXAMPLES
       The Euro sign is defined as follows in the UTF-8 charmap:

       <U20AC>     /xe2/x82/xac EURO SIGN
```

A charmap is the encoding as a table, and the example line is the whole idea of [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) on one line: a name on the left, `<U20AC>`, a code point written as a symbolic name; a byte sequence on the right, `/xe2/x82/xac`, in the file's escape syntax; and the Unicode character name as the comment. The header keywords `<code_set_name>`, `<mb_cur_max>` and `<escape_char>` are what the experiment below prints from the real file, and the optional `WIDTH` section is where [`wcwidth(3)`](wcwidth.md) gets its zeros for combining marks. The same `<U00E9>` line exists in `ISO-8859-2` with `/xe9` on the right, which is [Code pages](../../02_Characters/code_pages/README.md) as a directory of files: one name, many byte sequences, one file each.

### `repertoiremap(5)` and `localedef(1)`: the deprecated input and the compiler

A repertoire map let a locale source say `<Eu>` instead of `<U20AC>` (the page's example is `<Eu> <U20AC> EURO SIGN`), a mnemonic from the days before every character had a number. Its NOTES say *Repertoire maps are deprecated in favor of Unicode code points*; `localedef --help` in the container still prints a default directory for them, and the directory does not exist. `localedef(1)` is the compiler:

```text title="man 1 localedef, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       The  localedef  program  reads the indicated charmap and input files,
       compiles them to a binary form quickly usable by the locale functions
       in the C library (setlocale(3), localeconv(3), etc.), and places  the
       output in outputpath.
       ...
       Some of the following options are sensible only  for  certain  opera‐
       tions;  generally, it should be self-evident which ones.  Notice that
       -f and -c are reversed from what you might expect; that is, -f is not
       the same as --force.
       ...
           localedef -f UTF-8 -i fi_FI fi_FI.UTF-8
```

`-i` names the `locale(5)` source, `-f` names the `charmap(5)` file, and the operand is either a locale name to add to the system archive or, if it contains a slash, a directory to write twelve files into. The exit-status table is worth knowing before scripting it: `0`, `1` for *warnings or errors occurred, output files were written*, and `4` for *no output created*. The Mac's `localedef` returned 4 below.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| locale definition file | The text source of a locale, one `LC_xxx ... END LC_xxx` section per category, compiled by `localedef` | [`locale(1)` and `setlocale(3)`](locale.md) |
| charmap, character set description | The text table from symbolic character names to byte sequences that defines one encoding; the *character map* of UTR #17 | [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) |
| `<U00E9>`, `<U0001F600>` | A character written as its code point in the files' symbolic-name syntax; four hex digits, or eight above the BMP | [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| `/xc3/xa9` | A byte sequence in charmap syntax: the file's `escape_char` (`/`) then `x` and two hex digits per byte | [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| `<code_set_name>`, `<mb_cur_max>` | The charmap header: the encoding's name, and the most bytes one character takes (`6` in glibc's `UTF-8`) | [`utf8(5)`](utf8.md) |
| `escape_char`, `comment_char` | Two declarations that let a file change its own syntax; glibc's files use `/` and `%` | |
| `WIDTH` | The optional charmap section giving column widths, `0` for combining marks, `2` for East Asian wide | [`wcwidth(3)`](wcwidth.md) |
| `copy "i18n"` | Take this whole category from another source file; `i18n` is glibc's shared Unicode classification | [`ctype(3)`](ctype.md) |
| `translit_start` ... `translit_end` | The block of transliteration rules in an `LC_CTYPE` section; the data behind `iconv //TRANSLIT` | [`iconv(1)` and `iconv(3)`](iconv.md) |
| `include "translit_combining";""` | Pull a shared rule file into the block; the file that maps `é` to `e` and `ż` to `z` | [What the page does not say](../what_the_page_does_not_say/README.md) |
| `default_missing` | The character used when no target of a rule fits the output encoding; the `?` in `caf?` | [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md) |
| repertoire map, `<Eu>` | A mnemonic-to-code-point table, so sources could name characters without numbers; deprecated | |
| `collating-symbol`, `reorder-after`, `iso14651_t1` | The `LC_COLLATE` vocabulary: named weights, a way to move a character in the order, and the shared table almost every locale copies | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| `LOCPATH`, `I18NPATH` | Where `setlocale` looks for compiled locales before the system archive; where `localedef` looks for sources and charmaps | [`locale(1)` and `setlocale(3)`](locale.md) |
| `locale-archive`, `outputpath` | One memory-mapped file holding every system locale (absent in the container); the directory `localedef` writes instead, one file per category | |

## Try it on your machine

**The character maps as files.** 233 of them, gzipped, one per encoding; the header of `UTF-8`, and one character looked up in five of them.

```text title="Measured 2026-09-13 — ubuntu:24.04, glibc 2.39, locales package installed. Not machine-checked: facts about one container."
$ ls /usr/share/i18n/charmaps | wc -l
233
$ zcat /usr/share/i18n/charmaps/UTF-8.gz | head -10
<code_set_name> UTF-8
<comment_char> %
<escape_char> /
<mb_cur_min> 1
<mb_cur_max> 6

% CHARMAP generated using utf8_gen.py
% alias ISO-10646/UTF-8
CHARMAP
<U0000>     /x00         NULL
$ zcat /usr/share/i18n/charmaps/UTF-8.gz | grep -E '^<U00E9>|^<U017C>|^<U20AC>|^<U0001F600>'
<U00E9>     /xc3/xa9     LATIN SMALL LETTER E WITH ACUTE
<U017C>     /xc5/xbc     LATIN SMALL LETTER Z WITH DOT ABOVE
<U20AC>     /xe2/x82/xac EURO SIGN
<U0001F600> /xf0/x9f/x98/x80 GRINNING FACE
                        ISO-8859-2        ISO-8859-1    ISO-8859-15   CP1252
<U00E9>                 /xe9              /xe9          /xe9          /xe9
<U017C>                 /xbf              (absent)      (absent)      (absent)
<U20AC>                 (absent)          (absent)      /xa4          /x80
```

`<mb_cur_max> 6` is the six-byte table of [`utf8(5)`](utf8.md) again, and it is why the [`locale(1)`](locale.md) page measured `MB_CUR_MAX` as 6 on glibc. The four right-hand columns are [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) in two rows: `€` is `a4` in one and `80` in the other, and `ż` is in none of them but `ISO-8859-2`.

**Where `//TRANSLIT` comes from.** The rules for `é`, `ż` and `€`, the six-line `LC_CTYPE` section of `pl_PL` that includes them, and the converter obeying them.

```text title="Measured 2026-09-13 — ubuntu:24.04, glibc 2.39. Not machine-checked."
$ grep -n -m1 'translit_start' /usr/share/i18n/locales/translit_combining
17:translit_start
$ grep -n -E '^<U00E9>|^<U017C>' /usr/share/i18n/locales/translit_combining
1729:<U00E9> <U0065>
1979:<U017C> <U007A>
$ grep -n '^<U20AC>' /usr/share/i18n/locales/translit_neutral
572:<U20AC> "<U0045><U0055><U0052>"
$ sed -n '/^LC_CTYPE/,/^END LC_CTYPE/p' /usr/share/i18n/locales/pl_PL
LC_CTYPE
copy "i18n"

translit_start
include  "translit_combining";""
translit_end
END LC_CTYPE
$ for L in C C.UTF-8 pl_PL.UTF-8; do printf '%-12s ' "LC_ALL=$L"; printf 'ż é € ß Łódź\n' | LOCPATH=/tmp LC_ALL=$L iconv -f UTF-8 -t ASCII//TRANSLIT; done
LC_ALL=C     ? ? EUR ss ??d?
LC_ALL=C.UTF-8 z e EUR ss Lodz
LC_ALL=pl_PL.UTF-8 z e EUR ss Lodz
```

The last three lines are `locale(7)`'s sentence about `iconv` made visible: same bytes, same command, three answers, chosen by `LC_CTYPE`. Under `LC_ALL=C`, a locale compiled from no file in this directory, the `€` still becomes `EUR` and `ß` still becomes `ss`; the source file `C` says in a comment that *POSIX locales have +1600 transliterations that are built into the locales*, so those two rules are compiled into glibc itself, and only the combining-character rules, `é` and `ż`, come from `translit_combining`.

**Compiling a locale, and what changes.** The container ships only `C`, `C.utf8` and `POSIX`. `localedef` turns the `pl_PL` source and the `UTF-8` charmap into twelve files in a directory of your choosing, and `LOCPATH` makes them visible.

```text title="Measured 2026-09-13 — ubuntu:24.04, glibc 2.39. Not machine-checked."
$ locale -a | tr '\n' ' '
C C.utf8 POSIX
$ localedef -i pl_PL -f UTF-8 /tmp/pl_PL.UTF-8; echo "exit $?"
exit 0
$ ls /tmp/pl_PL.UTF-8
LC_ADDRESS  LC_COLLATE  LC_CTYPE  LC_IDENTIFICATION  LC_MEASUREMENT  LC_MESSAGES  LC_MONETARY  LC_NAME  LC_NUMERIC  LC_PAPER  LC_TELEPHONE  LC_TIME
   (LC_COLLATE is 2,586,758 bytes and LC_CTYPE 360,460; the other ten total under 5 KB)
$ locale -a | tr '\n' ' '; LOCPATH=/tmp locale -a | tr '\n' ' '
C C.utf8 POSIX C C.utf8 POSIX
$ LC_ALL=pl_PL.UTF-8 locale charmap
locale: Cannot set LC_CTYPE to default locale: No such file or directory
locale: Cannot set LC_MESSAGES to default locale: No such file or directory
locale: Cannot set LC_ALL to default locale: No such file or directory
ANSI_X3.4-1968
$ LOCPATH=/tmp LC_ALL=pl_PL.UTF-8 locale charmap
UTF-8
$ LOCPATH=/tmp LC_ALL=pl_PL.UTF-8 locale -k decimal_point thousands_sep abday
decimal_point=","
thousands_sep=" "
abday="nie;pon;wto;śro;czw;pią;sob"
$ printf 'ż\nz\nł\nl\nm\nŁódź\nLodz\nlody\n' > w
$ LC_ALL=C sort w | tr '\n' ' '                          Lodz l lody m z Łódź ł ż
$ LC_ALL=C.UTF-8 sort w | tr '\n' ' '                    Lodz l lody m z Łódź ł ż
$ LOCPATH=/tmp LC_ALL=pl_PL.UTF-8 sort w | tr '\n' ' '   l lody Lodz ł Łódź m z ż
```

Two things the pages do not warn about. `locale -a` does not list a `LOCPATH` locale before or after, so the only test of whether the compile worked is to use it. And the two big files are `LC_COLLATE` and `LC_CTYPE`: a locale is 2.9 MB of sorting weights and character classes and a few hundred bytes of everything else. The three `sort` lines are that `LC_COLLATE` at work: `C` and `C.UTF-8` sort by byte, so every capital precedes every lower-case letter and every accented letter follows `z`; Polish puts `ł` after `l` and `ż` after `z`, exactly as the `% &L<ł<<<Ł` and `% &Z<ź<<<Ź<ż<<<Ż` comments in `pl_PL`'s 74-line `LC_COLLATE` section say, and ignores case at the first level so `lody` and `Lodz` sort by their third letter.

**What the Mac has instead.** Four of the five pages are absent; the fifth documents a program with no input.

```text title="Measured 2026-09-13 — macOS 26.6.2. Not machine-checked."
$ man -w 5 locale; man -w 5 charmap; man -w 7 locale; man -w 5 repertoiremap
No manual entry for locale
No manual entry for charmap
No manual entry for locale
No manual entry for repertoiremap
$ man -w 1 localedef; command -v localedef
/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/share/man/man1/localedef.1
/usr/bin/localedef
$ localedef -i pl_PL -f UTF-8 ./pl_test; echo "exit $?"
fopen: No such file or directory
exit 4
$ ls /usr/share/locale/pl_PL.UTF-8
LC_COLLATE  LC_CTYPE  LC_MESSAGES  LC_MONETARY  LC_NUMERIC  LC_TIME
```

The Mac's `localedef(1)` is the FreeBSD one: a 2023 page listing six categories, no `translit_start`, and an OUTPUT section saying the result *should generally be copied into the appropriate subdirectory of /usr/share/locale*. There is no `/usr/share/i18n` on the Mac, so `-i pl_PL` has nothing to open; the six compiled files in `pl_PL.UTF-8` were made elsewhere and shipped.

## Where the page is dated, and what it does not say

**`locale(5)` is dated 2024 and still scopes its collation notes to *as of glibc 2.23*.** It lists `LC_COLLATE` keywords glibc does *not* support (`coll_weight_max` is *recognized but ignored*), and the `copy` exception is the reason a real file is mostly one `copy` line. What it does not say is which file to read for the rules `include` pulls in, or that the built-in `C` locale carries rules of its own that no source file in the directory shows.

**`charmap(5)` cites POSIX.2 and does not say where the table came from.** The file's own comment does, *CHARMAP generated using utf8_gen.py*, so the Unicode version behind `isalpha` is the version that script was run against: [The table has a version](../../02_Characters/the_table_has_a_version/README.md).

**`localedef(1)` does not say that `locale -a` will not show the result.** Its EXAMPLES compile into a directory and set `LOCPATH`, and the only test offered is to run `date`. Neither it nor `locale(1)` says that a `LOCPATH` locale is invisible to `locale -a`.

**None of the five pages exist on the Mac, and the Mac's `localedef(1)` is a different program with the same name.** Its ENVIRONMENT section even lists `LC_MUMERIC`, a typo the Linux page does not have. The Mac has the compiled output of a locale system and the compiler for a different one, and no source for either; `repertoiremap(5)` meanwhile documents a directory the container does not have.

## See also

- [`locale(1)`, `setlocale(3)` and `xlocale(3)`](locale.md) — the pages that read what these pages compile, and the `LOCPATH` runs that used the Polish locale built above
- [`iconv(1)` and `iconv(3)`](iconv.md) — `//TRANSLIT` from the converter's side
- [`charsets(7)` and the code-page pages](charsets.md) — the encodings that have charmap files here, described in prose on Linux
- [`strcoll(3)` and the collation pages](collation.md) — the functions that read the compiled `LC_COLLATE`
- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — what the variables mean at the shell
- [What the page does not say](../what_the_page_does_not_say/README.md) — the `//TRANSLIT` gap on the Mac that this page fills from the other side
- [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) — the character map, as a concept
- [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) and [Code pages](../../02_Characters/code_pages/README.md) — the two kinds of data these files hold
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) and [A page has a date](../a_page_has_a_date/README.md) — the chapter
