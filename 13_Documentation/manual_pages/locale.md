# `locale(1)`, `setlocale(3)` and `xlocale(3)`: the shell sets the variables, and a C program is in the C locale until it asks

**Level:** reference · for anyone who has typed `man setlocale` after a program printed `?` where an `é` should have been, and wanted every word on it explained

**One line:** `LC_ALL` beats `LC_xxx` beats `LANG`, both `environ(7)` pages say so in different words, and none of it reaches a C program until it calls `setlocale(LC_ALL, "")`; the five 2005 `xlocale` pages exist because that call is process-wide and a library has no business making it.

**The pages:** [`locale(1)`](raw/macos/locale.1.txt) (Darwin, August 27, 2004) · [`setlocale(3)`](raw/macos/setlocale.3.txt) and [`localeconv(3)`](raw/macos/localeconv.3.txt) (macOS, November 21, 2003) · [`nl_langinfo(3)`](raw/macos/nl_langinfo.3.txt) (May 3, 2001) · [`xlocale(3)`](raw/macos/xlocale.3.txt), [`newlocale(3)`](raw/macos/newlocale.3.txt), [`uselocale(3)`](raw/macos/uselocale.3.txt), [`duplocale(3)`](raw/macos/duplocale.3.txt) and [`querylocale(3)`](raw/macos/querylocale.3.txt) (all March 11, 2005) · [`environ(7)`](raw/macos/environ.7.txt) (April 12, 2003) · and for comparison, from Linux man-pages 6.7: [`environ(7)`](raw/linux/environ.7.txt) (2023-10-31), [`setlocale(3)`](raw/linux/setlocale.3.txt) (2024-02-25), [`nl_langinfo(3)`](raw/linux/nl_langinfo.3.txt) (2024-01-28) and [`locale(1)`](raw/linux/locale.1.txt) (2023-10-31). Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

A locale is the C library's answer to three questions it cannot answer from the bytes alone: what a byte sequence means, how a number is written, and in what order words sort. It is chosen from *outside* the program, by environment variables, and this family is the paper trail of that choice. `environ(7)` sits in section 7, miscellany, and is the page that lists the variables. `locale(1)` is the command that shows which of them won. `setlocale(3)`, `localeconv(3)` and `nl_langinfo(3)` are the library, section 3, and are how a program reads the result. This library cares about one of the six categories above all others, `LC_CTYPE`, because it is the one that decides whether `c3 a9` is one character or two: [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) is the lesson, and this page is the manual behind it.

The Apple pages are dated 2001 to 2005, the years Mac OS X acquired a locale system at all; `locale(1)` says in its own HISTORY that it *appeared in Mac OS X 10.4*. The five `xlocale` pages all carry one date, March 11, 2005, and describe something ISO C did not have: a locale as an object, `locale_t`, that a program can hold in a variable, attach to one thread, or hand to a function spelled with an `_l` suffix. POSIX.1-2008 later standardised most of that design, which is why `newlocale(3)` and `uselocale(3)` have pages on Ubuntu too, and `querylocale(3)` does not.

The reason the family matters to a reader of this library is the gap it documents. The shell may say `UTF-8` in every variable it has, and a C program still starts in the `"C"` locale, where `MB_CUR_MAX` is 1 and `nl_langinfo(CODESET)` names ASCII. Python calls `setlocale` for you at startup, which is why [Python text in practice](../../10_Best_Practices/python_text_in_practice/README.md) can mostly ignore this page and [Opening a file](../../04_Python/opening_a_file/README.md) cannot; a C program, and every tool written in C, has to ask. The experiments below show a program asking, and one deliberately not asking.

## The page, with notes

### `environ(7)`: the precedence rule, stated twice

```text title="man 7 environ, macOS 26.6.2, dumped 2026-09-13"
     LANG         This variable configures all programs which use setlocale(3)
                  to use the specified locale unless the LC_* variables are
                  set.

     LC_ALL       Overrides the values of LC_COLLATE, LC_CTYPE, LC_MESSAGES,
                  LC_MONETARY, LC_NUMERIC, LC_TIME and LANG.
```

```text title="man 7 environ, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       LANG   The name of a locale to use for  locale  categories  when  not
              overridden  by  LC_ALL  or more specific environment variables
              such as LC_COLLATE, LC_CTYPE, LC_MESSAGES, LC_MONETARY, LC_NU‐
              MERIC, and LC_TIME (see locale(7) for further details  of  the
              LC_* environment variables).
```

Three tiers, the same on both machines: `LC_ALL` if set wins everything, otherwise the per-category `LC_xxx`, otherwise `LANG`, otherwise `"C"`. The two pages divide the work differently. The BSD page gives each of the eight variables its own entry and a one-line job description, and one of them, `LC_COLLATE`, carries a warning that belongs on [`regex(3)` and the pattern pages](patterns.md): *"[A-Z]" may include characters that "[[:upper:]]" would not, depending on how the specified locale orders characters*. The Linux page has one entry, sends the reader to `locale(7)` (on the [`locale(5)` and `localedef(1)`](locale_files.md) page), and in a later bullet names three variables the Mac page does not have at all: `LANGUAGE`, `NLSPATH` and `LOCPATH`. The first and third are glibc's, and `LOCPATH` is how the experiments on that sibling page install a Polish locale without root. Note the condition in the Mac page's first sentence, *all programs which use setlocale(3)*: it is the whole subject of this page.

### `locale(1)`: which variable won

```text title="man 1 locale, Darwin (macOS 26.6.2), dumped 2026-09-13"
     LANG         Used as a substitute for any unset LC_* variable.  If LANG
                  is unset, it will act as if set to "C".  If any of LANG or
                  LC_* are set to invalid values, locale acts as if they are
                  all unset.
     ...
     -m       Lists all available public charmaps.  Darwin locales do not
              support charmaps, so list all CODESETs instead.
```

```text title="man 1 locale, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       When invoked without arguments, locale displays  the  current  locale
       settings  for each locale category (see locale(5)), based on the set‐
       tings of the environment variables that control the locale  (see  lo‐
       cale(7)).   Values  for  variables set in the environment are printed
       without double quotes, implied values are printed with double quotes.
```

The command prints one line per category with the name of the locale that category ended up with, which is the only reliable way to see the precedence rule applied. The Linux page promises a typographic hint, quotes for implied values and none for values that came straight from the environment; the experiment below shows the Mac quoting everything, so on this machine the hint does not exist. The Mac page's `-m` entry is an admission worth keeping: Darwin has no charmap files (the [sibling page](locale_files.md) is about the platform that does), so `locale -m` lists the 29 encodings its compiled locales use instead. And *acts as if they are all unset* is the Mac's answer to a misspelt `LANG`: silence and the C locale. glibc prints three warnings and then does the same.

### `setlocale(3)`: the C locale until told otherwise

```text title="man 3 setlocale, macOS 26.6.2, dumped 2026-09-13"
     Only three locales are defined by default: the empty string "" (which
     denotes the native environment) and the "C" and "POSIX" locales (which
     denote the C language environment).  A locale argument of NULL causes
     setlocale() to return the current locale.  An argument of "" will
     determine the name of the new locale taking into account the environment
     variables LANG and LC_*.  If these environment variables yield a locale
     that is invalid, NULL will be returned and the current locale will remain
     unchanged.  By default, C programs start in the "C" locale.  The only
     function in the library that sets the locale is setlocale(); the locale
     is never changed as a side effect of some other routine.
```

Every clause here is load-bearing. `""` is not a locale name but an instruction, *read the environment*; `NULL` is a question, not an assignment; and the last two sentences are the rule the whole library keeps tripping over: the shell's `LANG` is a suggestion that nothing in libc acts on until the program says `setlocale(LC_ALL, "")`. The Linux page says the same, adds the order in which glibc reads the variables (*first (regardless of category), the environment variable LC_ALL is inspected, next the environment variable with the same name as the category ... and finally the environment variable LANG*), and lists twelve categories where the Mac lists six, marking the extra six with an asterisk as GNU extensions. Its ATTRIBUTES table has one row, `setlocale() | Thread safety | MT-Unsafe const:locale env`, which is the problem the next section solves.

### `localeconv(3)` and `nl_langinfo(3)`: the decimal point and the codeset

```text title="man 3 localeconv, macOS 26.6.2, dumped 2026-09-13"
     decimal_point      The decimal point character, except for currency
                        values, cannot be an empty string.

     thousands_sep      The separator between groups of digits before the
                        decimal point, except for currency values.
```

```text title="man 3 nl_langinfo, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       CODESET (LC_CTYPE)
              Return a string with the name of the character  encoding  used
              in  the  selected  locale,  such  as "UTF-8", "ISO-8859-1", or
              "ANSI_X3.4-1968" (better known as US-ASCII).  This is the same
              string that you get with "locale  charmap".   For  a  list  of
              character encoding names, try "locale -m" (see locale(1)).
```

`localeconv` returns one `struct lconv` of 24 fields, almost all of them about money; the two quoted are the ones `printf("%'d")` and `strtod` use, and the experiment shows them changing from `.` and `,` to `,` and `.` to `,` and a no-break space as the locale moves from American to German to Polish. `nl_langinfo` is the more general lookup, one item at a time, and `CODESET` is the item this library exists for: it is the string `locale charmap` prints, the string `utf-8(7)` tells a program to compare with `"UTF-8"` on the [`utf8(5)`](utf8.md) page, and the only way a C program can learn which decoder [`multibyte(3)`](multibyte.md) will use. The Mac `nl_langinfo` page, dated 2001, does not mention `CODESET`, or any item; its one example is `ABDAY_1` returning *"Dom"* for Portuguese.

### `xlocale(3)`: a locale you can hold in a variable

```text title="man 3 xlocale, macOS 26.6.2, dumped 2026-09-13"
     -   LC_GLOBAL_LOCALE - A special locale_t value that corresponds to the
         global, process-wide locale.
     ...
CAVEATS
     The POSIX setlocale(3) function only affects the global locale, so using
     it when a per-thread locale is in effect will not change locale behavior
     for that thread.  However, it will change behavior for threads with no
     per-thread locale in effect.
     ...
CONVENIENCE FUNCTIONS
     The xlocale API also includes "convenience functions": functions that can
     be executed using a given locale, rather than the current locale.  These
     functions all take one extra locale_t argument at the end of the
     traditional argument list, except in the case of variable-argument
     functions, in which case the extra argument comes before the format
     string.  If a NULL locale_t is passed, the C locale will be used.
```

This is the fix for `MT-Unsafe`. `setlocale` changes one global, so a library that needs to parse `"3.14"` with a dot cannot call it without silently changing the decimal point for every other thread in the process. The 2005 design gives three ways out. `newlocale(3)` builds a `locale_t` from a name, `"C"` or `"en_US.UTF-8"`, with a mask saying which categories to take from it; `uselocale(3)` attaches that object to the calling thread only, returning `LC_GLOBAL_LOCALE` if there was none before; and every locale-sensitive function gains a twin with an `_l` suffix, `strtod_l`, `mbrtowc_l`, `printf_l`, listed by header on the page, that takes the object explicitly and never looks at the global at all. `duplocale(3)` copies one, `querylocale(3)` reads a category's name back, and its note that the mask *happens to scan the categories alphabetically* is the reason the composite string measured below reads `COLLATE/CTYPE/MESSAGES/MONETARY/NUMERIC/TIME`. One wrinkle to read twice: the DESCRIPTION says *if a NULL locale_t is given, the current locale is used* for the five basic routines, and the CONVENIENCE FUNCTIONS section says *if a NULL locale_t is passed, the C locale will be used* for the `_l` functions. Same page, two rules for `NULL`.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| category, `LC_COLLATE` ... `LC_TIME` | The six independent parts of a locale, each settable on its own; glibc adds six more (`LC_PAPER`, `LC_NAME`, ...) | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `LC_ALL` | As a variable, the override that beats the rest; as a `setlocale` argument, *all categories at once* | [`locale(7)` and the locale files](locale_files.md) |
| `LC_CTYPE` | The category that owns the bytes-to-characters rule, `isalpha`, `toupper` and `MB_CUR_MAX` | [`multibyte(3)`](multibyte.md) |
| `"C"`, `"POSIX"` | The two names every system must have: ASCII, `.` for the decimal point, byte order for sorting. The locale every C program starts in | [`ascii(7)`](ascii.md) |
| `""` (the native environment) | Not a name: the instruction to read `LC_ALL`, `LC_*` and `LANG` and pick a locale from them | |
| `setlocale(cat, NULL)` | A query. Returns the current name for that category without changing anything | |
| `CODESET`, codeset, charmap | The name of the locale's encoding, `UTF-8` or `US-ASCII` or `ANSI_X3.4-1968`; `locale charmap` at the shell | [`utf8(5)`](utf8.md) |
| `RADIXCHAR`, `decimal_point` | The character between the integer and fraction digits of a number; `.` in `C`, `,` in `de_DE` | [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) |
| `THOUSEP`, `thousands_sep`, `grouping` | The digit-group separator and the group sizes; empty in `C`, a no-break space in `pl_PL` | [`printf(3)`](printf.md) |
| `D_FMT` | The locale's date layout as a `strftime` format: `%m/%d/%y` in `C`, `%d.%m.%Y` in `de_DE` | |
| `MB_CUR_MAX` | The most bytes one character can take in the current locale: 1 in `C`, 4 for UTF-8 on the Mac and 6 on glibc | [`utf8(5)`](utf8.md) |
| `struct lconv` | The 24-field record `localeconv` returns; `decimal_point` and `thousands_sep` first, then twenty fields about currency | |
| `locale_t` | An opaque handle to a locale held as a value rather than as process state; made by `newlocale`, freed by `freelocale` | |
| `LC_GLOBAL_LOCALE` | The special `locale_t` meaning *the process-wide locale that setlocale sets*; what `uselocale` returns when no per-thread locale is in force | |
| `LC_CTYPE_MASK`, `LC_ALL_MASK` | Bit flags for `newlocale` saying which categories to take from the named locale | |
| per-thread locale | A `locale_t` installed by `uselocale` that overrides the global one for the calling thread only | |
| `_l` suffix (`mbrtowc_l`, `strtod_l`) | The convenience functions: the ordinary function plus an explicit `locale_t`, ignoring both global and per-thread state | |
| `MT-Unsafe const:locale env` | glibc's attribute for `setlocale`: it writes process state that other threads may be reading | |
| `LANGUAGE`, `LOCPATH`, `NLSPATH` | glibc's extra variables: a colon list of preferred languages for messages, a search path for compiled locales, a path for message catalogs | [`locale(7)` and the locale files](locale_files.md) |
| message catalog, `catopen(3)` | The translated-strings mechanism `LC_MESSAGES` selects; older than gettext and still in the SEE ALSO lines | |
| `<rune.h>` | The pre-xlocale BSD character interface that `xlocale(3)` calls deprecated | [`rune(3)`](rune.md) |

## Try it on your machine

**What `locale` prints, and how many categories it prints.** Nothing set, then `LANG` alone, then `LANG` with one category overridden. The Mac prints six categories and quotes every value; Ubuntu prints twelve, names the empty case `POSIX`, adds a `LANGUAGE=` line, and quotes only the values it inferred.

```text title="Measured 2026-09-13 — macOS 26.6.2 (left) and ubuntu:24.04, glibc 2.39 (right). Not machine-checked: facts about two machines."
$ env -u LANG -u LC_ALL locale                $ env -u LANG -u LC_ALL locale
LANG=""                                       LANG=
LC_COLLATE="C"                                LANGUAGE=
LC_CTYPE="C"                                  LC_CTYPE="POSIX"
LC_MESSAGES="C"                               LC_NUMERIC="POSIX"
LC_MONETARY="C"                               LC_TIME="POSIX"
LC_NUMERIC="C"                                LC_COLLATE="POSIX"
LC_TIME="C"                                   LC_MONETARY="POSIX"
LC_ALL=                                       LC_MESSAGES="POSIX"
                                              LC_PAPER="POSIX"
                                              LC_NAME="POSIX"
                                              LC_ADDRESS="POSIX"
                                              LC_TELEPHONE="POSIX"
                                              LC_MEASUREMENT="POSIX"
                                              LC_IDENTIFICATION="POSIX"
                                              LC_ALL=

$ LANG=en_US.UTF-8 LC_NUMERIC=de_DE.UTF-8 locale   $ LANG=C.UTF-8 LC_NUMERIC=de_DE.UTF-8 locale
LANG="en_US.UTF-8"                                  LANG=C.UTF-8
LC_COLLATE="en_US.UTF-8"                            LANGUAGE=
LC_CTYPE="en_US.UTF-8"                              LC_CTYPE="C.UTF-8"
LC_MESSAGES="en_US.UTF-8"                           LC_NUMERIC=de_DE.UTF-8
LC_MONETARY="en_US.UTF-8"                           LC_TIME="C.UTF-8"
LC_NUMERIC="de_DE.UTF-8"                            ... (twelve lines, the rest "C.UTF-8")
LC_TIME="en_US.UTF-8"                               LC_ALL=
LC_ALL=
```

**The override, and the invalid value.** `LC_ALL=C` beats a UTF-8 `LANG` on both, and the `C` charmap has two names.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
                                                  macOS               ubuntu:24.04
$ LC_ALL=C LANG=en_US.UTF-8 locale charmap        US-ASCII            ANSI_X3.4-1968     (LANG=C.UTF-8 there)
$ LANG=en_US.UTF-8 locale charmap                 UTF-8               UTF-8
$ LANG=xx_XX.bogus locale charmap                 US-ASCII, exit 0    ANSI_X3.4-1968, exit 0, after three lines of
                                                                      "locale: Cannot set LC_CTYPE to default locale: No such file or directory"
$ locale -a | wc -l                               288                 3       (C, C.utf8, POSIX)
$ locale -m | wc -l                               29                  236
```

**What a C program sees.** The program below prints `setlocale(LC_ALL, NULL)`, `nl_langinfo(CODESET)`, `RADIXCHAR`, `THOUSEP`, `D_FMT` and `MB_CUR_MAX` before and after `setlocale(LC_ALL, "")`, then `localeconv()->thousands_sep` in hex. Before the call, every run on both machines printed `C`, `US-ASCII` or `ANSI_X3.4-1968`, `.`, `""`, `%m/%d/%y` and `1`, whatever `LANG` said. After it:

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21) and ubuntu:24.04 (gcc 13, glibc 2.39; de_DE and pl_PL compiled with localedef into LOCPATH, see locale_files.md). Not machine-checked."
                          setlocale(LC_ALL, NULL)   CODESET  RADIXCHAR  THOUSEP  D_FMT      MB_CUR_MAX  thousands_sep bytes
macOS   LANG=en_US.UTF-8  en_US.UTF-8               UTF-8    .          ","      %m/%d/%Y   4           2c
        LANG=de_DE.UTF-8  de_DE.UTF-8               UTF-8    ,          "."      %d.%m.%Y   4           2e
        LANG=pl_PL.UTF-8  pl_PL.UTF-8               UTF-8    ,          " "      %Y.%m.%d   4           c2a0
        LANG=en_US.UTF-8 LC_NUMERIC=de_DE.UTF-8
                          en_US.UTF-8/en_US.UTF-8/en_US.UTF-8/de_DE.UTF-8/en_US.UTF-8/en_US.UTF-8
                                                    UTF-8    ,          "."      %m/%d/%Y   4           2e
ubuntu  LANG=C.UTF-8      C.UTF-8                   UTF-8    .          ""       %m/%d/%y   6           (empty)
        LANG=de_DE.UTF-8  de_DE.UTF-8               UTF-8    ,          "."      %d.%m.%Y   6           2e
        LANG=pl_PL.UTF-8  pl_PL.UTF-8               UTF-8    ,          " "      %d.%m.%Y   6           e280af
        LANG=C.UTF-8 LC_NUMERIC=de_DE.UTF-8
                          LC_CTYPE=C.UTF-8;LC_NUMERIC=de_DE.UTF-8;LC_TIME=C.UTF-8;...;LC_IDENTIFICATION=C.UTF-8
```

Three things to take from the table. `MB_CUR_MAX` for the same UTF-8 is 4 on the Mac and 6 on glibc, which is the six-row table of [`utf8(5)`](utf8.md) showing through a macro. The Polish thousands separator is a *different* invisible character on the two machines, `U+00A0 NO-BREAK SPACE` on the Mac and `U+202F NARROW NO-BREAK SPACE` on glibc, both of which a CSV parser will keep. And when the categories disagree, the string `setlocale` returns is a composite in a platform-specific syntax, slashes in alphabetical category order on the Mac and `NAME=value;` pairs on glibc; the Linux page calls it an *opaque string* for that reason.

**A locale you can hold, while the global one stays `C`.** The second program never calls `setlocale`. It decodes `c3 a9` with `mbrtowc` under the global `C` locale, builds a UTF-8 `locale_t` with `newlocale(LC_CTYPE_MASK, ...)`, decodes again through `mbrtowc_l` (Mac only; glibc has no such function) and again after `uselocale`, and asks `setlocale(LC_ALL, NULL)` in between.

```text title="Measured 2026-09-13 — macOS 26.6.2 (newlocale of en_US.UTF-8) and ubuntu:24.04 (newlocale of C.UTF-8), run with LANG unset. Not machine-checked."
                                          macOS                                 ubuntu:24.04
global locale at start                    C                                     C
mbrtowc(c3 a9) under global C             1 byte, wc = U+00C3                   (size_t)-1, errno=84 Invalid or incomplete multibyte or wide character
querylocale(LC_CTYPE_MASK, loc)           en_US.UTF-8                           (no querylocale on glibc)
mbrtowc_l(c3 a9, loc)                     2 bytes, wc = U+00E9                  (no mbrtowc_l on glibc)
uselocale(loc) returned                   LC_GLOBAL_LOCALE                      LC_GLOBAL_LOCALE
mbrtowc(c3 a9) after uselocale            2 bytes, wc = U+00E9                  2 bytes, wc = U+00E9
setlocale(LC_ALL, NULL) meanwhile         C                                     C
mbrtowc(c3 a9) after uselocale(LC_GLOBAL_LOCALE)
                                          1 byte, wc = U+00C3                   (size_t)-1, errno=84
```

The first row is a finding in its own right: the two `C` locales are not the same locale. glibc's is seven-bit and rejects `c3` outright; the Mac's accepts every byte as a one-byte character whose value is the byte, so `é` comes back as two characters, `Ã` and `©`, with no error at all. That is the difference between a `?` and mojibake, and it is why [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) says to check the input yourself. The rest of the table is the `xlocale` promise kept on both machines: the thread decodes UTF-8, the process-wide locale still says `C`, and the decoder goes back to the byte rule the moment the per-thread locale is withdrawn.

## Where the page is dated, and what it does not say

**The Apple pages are twenty years old and cite ISO C99 and SUSv2.** `setlocale(3)` says *only three locales are defined by default*, lists `$PATH_LOCALE/locale/category` as a search path, and names `colldef(1)` and `mklocale(1)` in SEE ALSO; neither page nor program exists on this Mac (`man -w 1 colldef` and `man -w 1 mklocale` both answer *No manual entry*, and `command -v` finds nothing), while `localedef(1)` and `/usr/bin/localedef`, which replaced them, are not mentioned. `nl_langinfo(3)` is dated 2001, says the function *first appeared in FreeBSD 4.6*, and never names `CODESET`. `xlocale(3)` says `<rune.h>` is deprecated, which the [`rune(3)`](rune.md) page confirms is still shipped.

**Neither `setlocale` page says what the return string looks like.** Both call it a string that will restore the locale if passed back. The two composite formats measured above are on neither page, and a program that compares the string to `"en_US.UTF-8"` will be wrong the moment one category differs.

**Neither `environ(7)` says that `C.UTF-8` exists.** It is on both machines (`locale -a` lists it on the Mac and `C.utf8` on Ubuntu) and it is the locale to reach for when you want UTF-8 with no language attached; on the Mac, `/usr/share/locale/en_US.UTF-8/LC_CTYPE` is a symlink to `../C.UTF-8/LC_CTYPE`, so `en_US.UTF-8` *is* `C.UTF-8` as far as `LC_CTYPE` is concerned.

**The Mac `locale(1)` page promises a quoting rule it does not keep.** It does not state one; the Linux page does, and the Mac binary quotes everything, so the reader who learned the rule on Linux will misread the Mac's output.

**Neither page says the `C` locale is eight-bit clean on BSD and seven-bit on glibc.** That difference decides what `mbrtowc`, `fgetws` and `printf("%ls")` do with a byte above `0x7f` when nobody called `setlocale`, and it is measured here and on the [`stdio(3)`](stdio.md) and [`printf(3)`](printf.md) pages.

## See also

- [`locale(5)`, `charmap(5)` and `localedef(1)`](locale_files.md) — where a glibc locale comes from, and the `LOCPATH` the experiments above rely on
- [`multibyte(3)`](multibyte.md) — the `LC_CTYPE` functions this page's `setlocale` call switches on
- [`utf8(5)` and `utf-8(7)`](utf8.md) — the encoding `CODESET` names, and the six-row table behind `MB_CUR_MAX = 6`
- [`strcoll(3)` and the collation pages](collation.md) — the `LC_COLLATE` category, and the regex-range warning in `environ(7)`
- [`iconv(1)` and `iconv(3)`](iconv.md) — the converter whose `//TRANSLIT` tables live in the locale
- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — the six variables as a lesson, with the terminal's own settings kept separate
- [The shell has no string type](../../11_Tools/sh/README.md) — what `${#v}` counts depends on the same variables
- [Python text in practice](../../10_Best_Practices/python_text_in_practice/README.md) and [Opening a file](../../04_Python/opening_a_file/README.md) — the language that calls `setlocale` for you, and the one call where the locale still leaks in
- [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) — `LC_COLLATE`, and why the order is data that may not be installed
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md), [A page has a date](../a_page_has_a_date/README.md), [What the page does not say](../what_the_page_does_not_say/README.md) — the chapter these pages belong to
