# `printf(3)`, `printf(1)` and `echo(1)`: a format writes bytes, counts bytes, and meets the locale only at `%ls`

**Level:** reference · for anyone who has lined up a table with `%-8s`, watched the Polish row come out short, and wanted the page that says why

**One line:** Field width and precision count bytes on both pages, so `%-8s` pads `Łódź` with one space and `%.3s` cuts it mid-character; `%ls` is the one conversion that runs the locale's encoder at print time, and under `C` it fails with `EILSEQ` for `Ł` on both machines and for `é` only on glibc; and the shell `printf` has three escape systems, of which only octal means the same thing in every implementation measured.

**The pages:** [`printf(3)`](raw/macos/printf.3.txt) (macOS, December 2, 2009) · [`wprintf(3)`](raw/macos/wprintf.3.txt) (July 5, 2003) · [`printf(1)`](raw/macos/printf.1.txt) (July 1, 2020) · [`echo(1)`](raw/macos/echo.1.txt) (April 12, 2003). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). The measurements were repeated in ubuntu:24.04 (glibc 2.39, GNU coreutils, bash 5.2, dash) for comparison.

## What the pages are for

`printf(3)` is five hundred lines because it documents a small language: flags, width, precision, length modifier, conversion, in that order after a `%`. Most of it is about numbers. This page annotates only the part that concerns text: four conversions (`%c`, `%s` and their wide twins `%lc`, `%ls`), the two counters (width and precision), the modifier that makes `%x` print a byte instead of an `int` (`hh`), and the one flag (`'`) that reads the locale. `wprintf(3)` is the same language with a wide format string and the roles of `%s` and `%ls` reversed. `printf(1)` is the shell command modelled on the function, with its own escape syntax bolted on the front; `echo(1)` is the command it exists to replace.

The reason a reader of this library needs them is that `printf` is the tool the library uses to *make* bytes. [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) is built on `printf '\303\251'`; [Writing a code point](../../02_Characters/writing_a_code_point/README.md) is built on the difference between that and `\u00e9`; [The shell has no string type](../../11_Tools/sh/README.md) found that `echo` and `printf` are not the same program in `sh`. Those pages recorded what happened; these are the pages that were supposed to predict it, and the CONTRIBUTING findings numbered 13, 35 and 36 in this repository are three places where the prediction and the machine parted. All three are re-measured below.

## The page, with notes

### `printf(3)`: width and precision count bytes

```text title="man 3 printf, macOS 26.6.2, dumped 2026-09-13"
     o   An optional decimal digit string specifying a minimum field width.
         If the converted value has fewer characters than the field width, it
         will be padded with spaces on the left (or right, if the left-
         adjustment flag has been given) to fill out the field width.

     o   An optional precision, in the form of a period . followed by an
         optional digit string.  If the digit string is omitted, the precision
         is taken as zero.  This gives the minimum number of digits to appear
         for d, i, o, u, x, and X conversions, the number of digits to appear
         after the decimal-point for a, A, e, E, f, and F conversions, the
         maximum number of significant digits for g and G conversions, or the
         maximum number of characters to be printed from a string for s
         conversions.
```

*Characters*, twice, and both times the implementation counts bytes: the experiment shows `%-8s` giving `Łódź` one trailing space and `Lodz` four, and `%.3s` returning `c5 81 c3`, the first byte and a half of a two-character word. The `printf(1)` page, written eleven years later, corrects the word to *bytes* in both places. The width you want for a table is the one [`wcwidth(3)`](wcwidth.md) computes, and neither `printf` will compute it for you.

```text title="man 3 printf, macOS 26.6.2, dumped 2026-09-13"
                 If the l (ell) modifier is used, the wchar_t * argument is
                 expected to be a pointer to an array of wide characters
                 (pointer to a wide string).  For each wide character in the
                 string, the (potentially multi-byte) sequence representing
                 the wide character is written, including any shift sequences.
                 If any shift sequence is used, the shift state is also
                 restored to the original state after the string.  Wide
                 characters from the array are written up to (but not
                 including) a terminating wide NUL character; if a precision
                 is specified, no more than the number of bytes specified are
                 written (including shift sequences).  Partial characters are
                 never written.  If a precision is given, no null character
                 ...
```

The `%s` paragraph above it says *Characters from the array are written up to (but not including) a terminating NUL character*, and that is all `%s` does: it copies bytes. `%ls` *encodes*. Each `wchar_t` goes through `wcrtomb` in the current `LC_CTYPE` at the moment of printing, which is why the same call produces `c3 a9` under a UTF-8 locale and, under `C`, either the byte `e9` (Mac) or a failed call (glibc). *Partial characters are never written* is the one place in the family where a precision respects character boundaries, and the experiment confirms it: `%.3ls` of `Łódź` writes `c5 81`, two bytes, one whole character. `%c` and `%lc` are the single-character forms with the same split, and the length-modifier table reduces the wide story to one row, `l (ell) | wint_t | wchar_t *`. The error is named once, under ERRORS as `[EILSEQ] An invalid wide character code was encountered`, and the BUGS section adds that the functions *do not correctly handle multibyte characters in the format argument*, which means the format is scanned byte by byte for `%`: safe in UTF-8, where no byte of a multibyte character is `25`.

### `printf(3)`: `%x`, `%hhx` and the `'` flag

```text title="man 3 printf, macOS 26.6.2, dumped 2026-09-13"
         `#'               The value should be converted to an "alternate
                           form".  For c, d, i, n, p, s, and u conversions,
                           this option has no effect.  For o conversions, the
                           precision of the number is increased to force the
                           first character of the output string to a zero.
                           For x and X conversions, a non-zero result has the
                           string `0x' (or `0X' for X conversions) prepended
                           to it.  For a, A, e, E, f, F, g, and G conversions,
         ...
         `'' (apostrophe)  Decimal conversions (d, u, or i) or the integral
                           portion of a floating point conversion (f or F)
                           should be grouped and separated by thousands using
                           the non-monetary separator returned by
                           localeconv(3).
         ...
         Modifier                 d, i               o, u, x, X                n
         hh                       signed char        unsigned char             signed char *
```

Three things a byte-dumper needs. `%#x` writes `0xc3` and `%#o` writes `0303`, which is the difference between a number and a picture of bytes on [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md). `hh` says the argument is a `char`, so `%hhx` of a `char` holding `c3` prints `c3` where `%x` prints `ffffffc3`, because a signed `char` is promoted to a negative `int` before `printf` ever sees it. And `'` is the one flag that reads `localeconv`: `%'d` of `1234567` is seven digits under `C`, `1,234,567` under `en_US`, `1.234.567` under `de_DE`, and under `pl_PL` a string with two invisible characters in it that differ between the two machines, as the [`locale(1)`](locale.md) page found.

### `wprintf(3)`: the mirror image

```text title="man 3 wprintf, macOS 26.6.2, dumped 2026-09-13"
     c           The int argument is converted to an unsigned char, then to a
                 wchar_t as if by btowc(3), and the resulting character is
                 written.
     ...
     s           The char * argument is expected to be a pointer to an array
                 of character type (pointer to a string) containing a
                 multibyte sequence.  Characters from the array are converted
                 to wide characters and written up to (but not including) a
                 terminating NUL character; if a precision is specified, no
                 ...
```

In the wide family the plain conversions are the ones that decode. `%s` in `wprintf` runs the multibyte string through the locale on the way *in*, and `%c` runs a byte through `btowc`, which under `C` on glibc fails for anything above `7f`. The page says the functions return *the number of wide characters printed*, a count in characters at last, and says nothing about what the wide-oriented `stdout` will do if the program has already used `printf` on it, which is the orientation trap on the [`stdio(3)`](stdio.md) page.

### `printf(1)`: three escape systems and a byte-counting rule

```text title="man 1 printf, macOS 26.6.2, dumped 2026-09-13"
           \num    Write a byte whose value is the 1-, 2-, or 3-digit octal
                   number num.  Multibyte characters can be constructed using
                   multiple \num sequences.
     ...
     Field Width:
             An optional digit string specifying a field width; if the output
             string has fewer bytes than the field width it will be blank-
             padded ...
     c           The first byte of argument is printed.
     ...
     b           As for s, but interpret character escapes in backslash
                 notation in the string argument.  The permitted escape
                 sequences are slightly different in that octal escapes are
                 \0num instead of \num and that an additional escape sequence
                 \c stops further output from this printf invocation.
```

The command has the function's `%` language and, in front of it, C's backslash escapes, of which the page lists nine plus `\num`. It does not list `\xHH`, and says so under CAVEATS: *ANSI hexadecimal character constants were deliberately not provided*. Then `%b` adds a third system, applied to an *argument* rather than the format, with octal spelled `\0num` and a `\c` that ends the output. The experiments show which shells' builtins honour which of the three, and that the `/usr/bin/printf` binary on the Mac, which this page describes, is the only one that neither knows `\x` nor complains about it (finding 36). *The first byte of argument is printed* for `%c` is exactly right and exactly useless for `Ł`.

```text title="man 1 printf, macOS 26.6.2, dumped 2026-09-13"
           o   If the leading character is a single or double quote, the value
               is the character code of the next character.
     ...
     If the locale contains multibyte characters (such as UTF-8), the c format
     and b and s formats with a precision may not operate as expected.
```

`printf '%d' "'Ł"` is the shell's way to ask for a character's number, and the answer depends on who answers: the Mac binary and GNU say `321` in a UTF-8 locale and `197` (the first byte) under `C`; bash 3.2's builtin says `-59` in either, which is `c5` read as a signed `char`. The CAVEATS sentence is the page admitting, in 2020, what the function's page will not: with multibyte input, `%c` and a precision cut bytes.

### `echo(1)`: `-n`, and why the library prefers `printf`

```text title="man 1 echo, macOS 26.6.2, dumped 2026-09-13"
     -n    Do not print the trailing newline character.  This may also be
           achieved by appending `\c' to the end of the string, as is done by
           iBCS2 compatible systems.  Note that this option as well as the
           effect of `\c' are implementation-defined in IEEE Std 1003.1-2001
           ("POSIX.1") as amended by Cor. 1-2002.  Applications aiming for
           maximum portability are strongly encouraged to use printf(1) to
           suppress the newline character.

     Some shells may provide a builtin echo command which is similar or
     identical to this utility.  Most notably, the builtin echo in sh(1) does
     not accept the -n option.  Consult the builtin(1) manual page.
```

This is the whole case for [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) made by the other page: `-n` is implementation-defined, `\c` is implementation-defined, and the `sh` on this machine prints `-n hi` and a newline (finding 35). There is no `-e` on the page because `/bin/echo` has none; the experiment shows it printing `-e` as text where GNU's interprets it as a flag.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| conversion specification | `%` then flags, width, precision, length modifier, conversion letter, in that order | |
| field width | The minimum size of the output for one conversion, padded with spaces; counted in bytes by both implementations | [`wcwidth(3)`](wcwidth.md) |
| precision (`.n`) | For `%s`, the *maximum* bytes written; for `%ls`, the maximum bytes but never a partial character; for integers, minimum digits | |
| length modifier `hh`, `l` | The argument's type: `hh` a `char`, `l` a `long` for numbers and a wide character or wide string for `%c`/`%s` | [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) |
| `%lc`, `%ls`, `wint_t` | The wide-character conversions; `wint_t` is `wchar_t` widened to hold `WEOF` | [`multibyte(3)`](multibyte.md) |
| shift sequence, shift state | Bytes a stateful encoding emits to change sets, which `%ls` writes and counts against the precision; none exist in UTF-8 | [The CJK pages](cjk_encodings.md) |
| `EILSEQ` | The `errno` for a wide character the current locale cannot encode | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| alternate form `#` | `0x` in front of hex, a leading `0` on octal, a decimal point kept on floats | [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) |
| `'` (apostrophe flag) | Group digits by thousands using `localeconv()->thousands_sep` | [`locale(1)` and `localeconv(3)`](locale.md) |
| `\num`, `\0num` | Octal byte escapes: up to three digits in a format string, a leading `0` then up to three in a `%b` argument | [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) |
| `\xHH`, `\uHHHH` | The hex and code-point escapes some shells add and the Mac binary refuses; the page calls the first *deliberately not provided* | [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| `\c` | End the output here: recognised in `%b` arguments by every implementation, and in the format by only some | |
| `'Ł` (quote operand) | A numeric argument beginning with a quote means *the code of the next character*; which code depends on the locale and the implementation | [A character is a number](../../02_Characters/a_character_is_a_number/README.md) |
| builtin | The shell's own `printf`/`echo`, reached by typing the name; the binary in `/usr/bin` is reached by `env`, `xargs` or `find -exec` | [The shell has no string type](../../11_Tools/sh/README.md) |
| iBCS2, Cor. 1-2002 | The Intel Binary Compatibility Standard, whose `echo` honoured `\c`; the 2002 corrigendum to POSIX.1-2001 under which the page says `-n` and `\c` are implementation-defined | |

## Try it on your machine

**`%ls` encodes at print time.** `snprintf` of a wide string, under `C` and under a UTF-8 locale, on both machines.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21) and ubuntu:24.04 (gcc 13, glibc 2.39). Not machine-checked."
                                  macOS, LC_CTYPE=C          ubuntu, LC_CTYPE=C            both, UTF-8 locale
%ls of L"café"                    4, bytes 63 61 66 e9       -1, errno=84 EILSEQ           5, bytes 63 61 66 c3 a9
%ls of L"Łódź"                    -1, errno=92 EILSEQ        -1, errno=84 EILSEQ           7, bytes c5 81 c3 b3 64 c5 ba
%ls of L"€"                       -1, errno=92 EILSEQ        -1, errno=84 EILSEQ           3, bytes e2 82 ac
%lc of L'Ł'                       -1, errno=92 EILSEQ        -1, errno=84 EILSEQ           2, bytes c5 81
printf("%ls|", L"café") to stdout returned 5, no error       returned -1, errno=84         returned 6
```

Under `C` glibc refuses every non-ASCII character and the whole call fails: the return value is `-1`, nothing is written, and a program that ignores the return value prints nothing where the line should be. The Mac's `C` locale is eight-bit, so `é` becomes the single byte `e9`, Latin-1 by accident, and only `Ł`, which has no one-byte form, fails. The right-hand column is what `setlocale(LC_ALL, "")` under any UTF-8 locale buys.

**Width and precision count bytes; `%.3ls` does not cut a character.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04, UTF-8 locale; byte-identical on both. Not machine-checked."
%-8s  of Łódź (7 bytes, 4 chars)   -> 9 bytes: [Łódź |]
%-8s  of Lodz (4 bytes, 4 chars)   -> 9 bytes: [Lodz    |]
%-8ls of L"Łódź"                   -> 9 bytes: [Łódź |]
%.3s  of the 7-byte word           -> 3 bytes: c5 81 c3
%.3ls of the 4-wide-char word      -> 2 bytes: c5 81
char c = (char)0xc3:  %x -> ffffffc3   %hhx -> c3   %02x of (unsigned char)c -> c3
195:  %o -> 303   %#o -> 0303   %x -> c3   %#x -> 0xc3   %#X -> 0XC3   %#06x -> 0x00c3
%'d of 1234567:   C -> 1234567    en_US.UTF-8 -> 1,234,567    de_DE.UTF-8 -> 1.234.567    pl_PL.UTF-8 -> 1 234 567 (31 c2 a0 32 ... on macOS, 31 e2 80 af 32 ... on glibc)
```

**The shell `printf`, six implementations.** The same format on each machine's builtins and binary, output as hex; a UTF-8 locale unless marked `(C)`.

```text title="Measured 2026-09-13 — macOS 26.6.2: bash 3.2.57 builtin, zsh 5.9 builtin, /usr/bin/printf (BSD). ubuntu:24.04: bash 5.2.21 builtin, dash builtin, /usr/bin/printf (GNU coreutils). Not machine-checked."
                          bash 3.2         zsh 5.9          BSD binary       bash 5.2         dash             GNU binary
printf '\303\251'         c3a9             c3a9             c3a9             c3a9             c3a9             c3a9
printf '\xc3\xa9'         c3a9             c3a9             786333786139     c3a9             5c7863335c786139 c3a9
printf '\xc0'             c0               c0               786330           c0               (literal)        c0
printf '€'                e282ac           e282ac           e282ac           e282ac           e282ac           e282ac
printf '\u20ac'           5c7532306163     e282ac           7532306163       e282ac           5c7532306163     e282ac
printf '\u20ac'  (C)      5c7532306163     (error: character not in range)
                                                            7532306163       5c7532304143     5c7532306163     5c7532304143
printf '%b' '\0303\0251'  c3a9             c3a9             c3a9             c3a9             c3a9             c3a9
printf '%b' '\303\251'    c3a9             5c3330335c323531 (not measured)   c3a9             c3a9             (not measured)
printf 'ab\cd'            61625c6364       6162             61626364         61625c6364       61625c6364       6162
printf '%b' 'ab\cd'       6162             6162             6162             6162             6162             6162
printf '%.3s|' Łódź       c581c37c         c581c3b3647c     c581c37c         c581c37c         c581c37c         c581c37c
printf '%c|' Łódź         c57c             c57c             c57c             c57c             c57c             c57c
printf '%d' "'Ł"          -59              321              321              321              197              321
printf '%d' "'Ł"  (C)     -59              197              197              197              197              197, with a warning
```

Read it a row at a time. Octal is the only row with one answer, which is finding 36's conclusion and this library's rule. `\x` is known to four of the six and mangled by the Mac binary into `xc3xa9`, three printable letters per byte, with exit status 0. `\u` is finding 13 in a table: bash 3.2 predates it and hands it back; zsh and bash 5.2 encode it in a UTF-8 locale; under `C` zsh refuses, bash 5.2 hands it back with the hex uppercased, and the Mac binary drops the backslash and prints `u20ac`. `\c` in a format string is honoured by zsh and GNU, ignored by bash, and stripped to `abcd` by the Mac binary. And two rows show the builtins disagreeing about what a character is: zsh's `%.3s` counts characters and every other implementation counts bytes, and bash 3.2's quote operand returns a signed byte.

**`echo`, on the machine the page describes.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (left) and ubuntu:24.04 (right). Not machine-checked."
                          macOS                              ubuntu:24.04
echo -n hi   (bash)       6869                               6869
sh -c 'echo -n hi'        2d6e2068690a   ("-n hi" + newline)  6869
/bin/echo -n hi           6869                               6869
/bin/echo 'hi\c'          6869           (no newline)        68695c630a   ("hi\c" + newline)
/bin/echo -e 'a\tb'       2d6520615c74620a ("-e a\tb")       6109620a
echo -e 'a\tb'  (bash)    6109620a                           6109620a
```

`/bin/echo` on the Mac does what its page says and nothing else: `-n` works, `\c` works, `-e` is a word. `sh` is bash in POSIX mode, where `-n` is a word (finding 35). GNU `echo` interprets `-e` and not `\c`. Four programs called `echo`, and only `printf '%s'` writes the same bytes through all of them.

## Where the page is dated, and what it does not say

**`printf(3)` is dated 2009 and says *characters* where its own implementation counts bytes.** The `printf(1)` page from 2020 says *bytes* in the same two places. The function page also carries two paragraphs about AltiVec vector conversions, a PowerPC feature, that name *Mac OS X 10.2 and later*.

**Neither `printf` page names `wcwidth`.** A column that lines up on the screen needs a width in terminal cells, which is neither bytes nor characters; the pages count one and say the other, and [`wcwidth(3)`](wcwidth.md) is the missing reference.

**`printf(1)` does not say that its builtins differ from it.** It says *some shells may provide a builtin printf command which is similar or identical to this utility*; the table above has six columns and no two are identical. The page's *deliberately not provided* `\x` is provided by every builtin on the machine, and `\c` in the format is honoured in the binary by silently deleting the backslash.

**`echo(1)` is dated 2003 and cites a 2002 corrigendum.** It is right, and it is the reason [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) exists. What it does not say is that `-e` will be printed as text, or that GNU's `echo` will do the reverse.

**Nothing in the family says that a failed `%ls` writes nothing.** `printf(3)` promises *a negative value if an error occurs*; the measurement shows the whole call abandoned, not just the one conversion, and a program that does not check will print an empty line for every string with an `é` in it.

## See also

- [`stdio(3)`, `fopen(3)` and `fwide(3)`](stdio.md) — the streams these functions write to, and the orientation `wprintf` sets
- [`multibyte(3)`](multibyte.md) — `wcrtomb`, which is what `%ls` runs on each wide character
- [`strtol(3)`](strtol.md) — the other direction: parsing the numbers `printf` writes
- [`wcwidth(3)`](wcwidth.md) — the width that would actually line up a column
- [`locale(1)`, `setlocale(3)` and `xlocale(3)`](locale.md) — which locale `%ls` and `'` consult, and why a C program starts in `C`
- [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) — the lesson built on the octal row
- [Writing a code point](../../02_Characters/writing_a_code_point/README.md) — the `\u20ac` row at full length
- [The shell has no string type](../../11_Tools/sh/README.md) — `sh`, `echo -n`, and finding 35
- [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) and [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) — `%#x`, `%o` and the `'` flag's separator
- [The trailing newline](../../06_Terminal/trailing_newline/README.md) — what `-n` and `\c` remove
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) and [What the page does not say](../what_the_page_does_not_say/README.md) — the chapter
