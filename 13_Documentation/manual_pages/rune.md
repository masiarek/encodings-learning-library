# `rune(3)` and `mbrune(3)`: the API that named Go's character type, deprecated since macOS 10.4

**Level:** reference · for anyone who has typed `man 3 rune` on a Mac, seen a 1994 date, and wondered what a rune is doing in a C library

**One line:** Two pages document 4.4BSD's *rune* API, the multibyte layer that C99's wide-character functions replaced; on this Mac `sgetrune` still decodes `é` (and libc scolds you on stderr for calling it), `setrunelocale` segfaults, and `rune_t` is `wchar_t` under another name, the type Go's `rune` later turned into a bare `int32`.

**The pages:** [`mbrune(3)`](raw/macos/mbrune.3.txt) (macOS, dated April 19, 1994) · [`rune(3)`](raw/macos/rune.3.txt) (macOS, October 6, 2002). Neither exists on Ubuntu: `man 3 rune` there answers *No manual entry*. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt).

## What the pages are for

Before ISO C had `mbrtowc` and `wcrtomb`, 4.4BSD had runes. The header `<rune.h>` on this Mac still carries the 1993 Berkeley copyright and the credit *contributed to Berkeley by Paul Borman at Krystal Technologies*, and the page's `HISTORY` says the functions were *inspired by Plan 9 from Bell Labs*, the system UTF-8 was designed for. A rune is Plan 9's word for one decoded character, and the API is the set of verbs for moving between a multibyte string and runes: `sgetrune` reads one out of a byte string, `sputrune` writes one back, `fgetrune` and `fputrune` do the same on a `FILE`, and `setrunelocale` loads the `LC_CTYPE` table that says which encoding the bytes are in.

Both pages open with the same sentence: the API *has been deprecated in favour of the ISO C99 extended multibyte and wide character facilities*. So they sit in **section 3** but document a layer under the one you are meant to call; [`multibyte(3)`](multibyte.md) is the replacement, function for function. They are still shipped in 2026 because the header is, and because the names live on: `rune_t` is a field type in the locale structure every `isalpha` on this Mac reads, and *rune* is the word Go chose for its character type. [`rune` is an `int32`](../../02_Characters/rune_is_an_int32/README.md) is about what the word came to mean; this page is about what it meant first.

## The page, with notes

### `mbrune(3)`: `strchr` for multibyte strings

```text title="man 3 mbrune, macOS 26.6.2, dumped 2026-09-13"
     The 4.4BSD "rune" functions have been deprecated in favour of the ISO C99
     extended multibyte and wide character facilities and should not be used
     in new applications.  Consider working with wide characters instead, and
     using wcschr(3), wcsrchr(3), and wcsstr(3) instead of these functions.
     ...
HISTORY
     The mbrune(), mbrrune(), and mbmb() functions first appeared in Plan 9
     from Bell Labs as utfrune(), utfrrune(), and utfutf().
```

`strchr` on a UTF-8 string is safe only because no byte of a multibyte character can be mistaken for an ASCII one, and it is useless the moment the character you want is not ASCII: `strchr(s, 'é')` does not compile, because `'é'` is two bytes. `mbrune` took the rune, walked the string one *character* at a time, and returned a pointer into the bytes; the replacement the page names does the same job on the far side of the decoder, convert everything to `wchar_t` and then `wcschr`. The `HISTORY` is the genealogy: `utfrune` is in Plan 9's C library to this day, and Go has `strings.IndexRune`. The word outlived two operating systems.

### `rune(3)`: reading one character out of bytes

```text title="man 3 rune, macOS 26.6.2, dumped 2026-09-13"
     The sgetrune() function tries to read a single multibyte character from
     string, which is at most n bytes long.  If sgetrune() is successful, the
     rune is returned.  If result is not NULL, *result will point to the first
     byte which was not converted in string.  If the first n bytes of string
     do not describe a full multibyte character, _INVALID_RUNE is returned and
     *result will point to string.  If there is an encoding error at the start
     of string, _INVALID_RUNE is returned and *result will point to the second
     character of string.
```

This is `mbrtowc` with the return codes in different places. `mbrtowc` reports *incomplete* as `(size_t)-2` and *invalid* as `(size_t)-1` through the return value; `sgetrune` returns `_INVALID_RUNE` for both and tells them apart by where `*result` lands, on the start of the string for *incomplete* and one byte in for *invalid*. That last rule, skip exactly one byte after a bad one, is the recovery policy [`rune` is an `int32`](../../02_Characters/rune_is_an_int32/README.md) finds in Go's `range` loop, one `U+FFFD` per bad byte, thirty years later in the same family.

```text title="man 3 rune, macOS 26.6.2, dumped 2026-09-13"
     The setrunelocale() controls the type of encoding used to represent runes
     as multibyte strings as well as the properties of the runes as defined in
     <ctype.h>.  The locale argument indicates which locale to load.  If the
     locale is successfully loaded, 0 is returned, otherwise an errno value is
     returned to indicate the type of error.
     ...
     /usr/share/locale/locale/LC_CTYPE  binary LC_CTYPE file for the locale
```

`setrunelocale` is `setlocale(LC_CTYPE, name)` under an older name, and its description says what a locale's `LC_CTYPE` half *is*: one binary file that decides both how bytes group into characters and which characters are letters. `/usr/share/locale/en_US.UTF-8/LC_CTYPE` is still where this Mac keeps it, and [`utf8(5)`](utf8.md) shows it is a symlink to the `C.UTF-8` one. The page lists `EINVAL`, `ENOENT` and `EFTYPE` as the possible returns; the experiment below shows what the function does instead of returning.

### What the header says

The page is silent on three things the header `<rune.h>` states. Its banner reads *This interface is depreciated and will eventually be removed*, with that spelling. `sgetrune` and `sputrune` are not functions but macros, `(*__sgetrune)((s), (n), (r))`, calling through the current locale's function pointers, so a use of them cannot be flagged as deprecated and links without complaint; the named functions carry `__OSX_AVAILABLE_BUT_DEPRECATED(__MAC_10_0, __MAC_10_4, ...)`, which dates the deprecation to macOS 10.4, 2005. And `rune_t` is `__darwin_wchar_t`, under a comment in `i386/_types.h` that reads *rune_t is not covered by ANSI nor other standards ... Use wchar_t. wchar_t and rune_t must be the same type*: it is 4 bytes and holds whatever `wchar_t` holds, a code point under a UTF-8 locale and an EUC byte pair under a Japanese one, as [`multibyte(3)`](multibyte.md) measures.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| rune | Plan 9's word for one decoded character, what this library calls a code point; BSD borrowed it for its multibyte layer, Go for its `int32` | [`rune` is an `int32`](../../02_Characters/rune_is_an_int32/README.md) |
| `rune_t` | The C type of a rune; on this Mac a typedef of `wchar_t`, 4 bytes | [`multibyte(3)`](multibyte.md) |
| `_INVALID_RUNE` | The rune value returned for bad or incomplete input; `mbrtowc` uses `(size_t)-1` and `(size_t)-2` instead | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `LC_CTYPE`, `$PATH_LOCALE` | The locale category that says how bytes form characters and which are letters; the directory its binary file is loaded from | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| Plan 9, `utfrune` | The Bell Labs system UTF-8 was designed for in 1992; its `strchr` for UTF-8, which became `mbrune` here | [Why UTF-8 won](../../09_History/why_utf8_won/README.md) |

## Try it on your machine

**Where the pages are.** `rune.3` is installed on the Mac under every name in its `NAME` line, so `man 3 sgetrune` finds it; `utfrune`, the Plan 9 name the page cites, resolves nowhere, and `utf2(4)` is cited in the wrong section.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: which pages exist is a fact about the machine."
                            macOS                                                      ubuntu:24.04
$ man -w 3 setrunelocale    .../MacOSX.sdk/usr/share/man/man3/setrunelocale.3          No manual entry for setrunelocale in section 3
$ man -w 3 utfrune          No manual entry for utfrune   (exit 1)
$ man -w 4 utf2             No manual entry for utf2      (man -w 5 utf2 finds it)
```

**Does it still compile, link and run?** Ten lines: `setlocale(LC_ALL, "en_US.UTF-8")`, then `sgetrune("\xc3\xa9", 2, &rest)` and a `printf` of the rune, the bytes consumed and `sizeof(rune_t)`. A second program calls the two named functions `setrunelocale` and `fgetrune`.

```text title="Measured 2026-09-13 — macOS 26.6.2, Apple clang 21. Not machine-checked."
$ cc -std=c11 -Wall -Wextra -o rune1 rune1.c          (no diagnostics: sgetrune is a macro, so nothing can be marked deprecated)
$ ./rune1
sgetrune and other functions prototyped in rune.h are depreciated in favor of
the ISO C99 extended multibyte and wide character facilities and should not
be used in new applications.
sgetrune("c3 a9") -> U+00E9, consumed 2 byte(s), sizeof(rune_t) = 4

$ cc -std=c11 -Wall -Wextra -o rune2 rune2.c          (rune2.c: setrunelocale("en_US.UTF-8"), then fgetrune(stdin))
rune2.c:6:14: warning: 'setrunelocale' is deprecated: first deprecated in macOS 10.4 [-Wdeprecated-declarations]
rune2.c:8:14: warning: 'fgetrune' is deprecated: first deprecated in macOS 10.4 [-Wdeprecated-declarations]
2 warnings generated.
$ printf '\xc3\xa9' | ./rune2
Segmentation fault: 11                                (exit 139)

$ printf '\xc3\xa9' | ./rune4                         (fgetrune alone, no setlocale call: the C locale)
fgetrune -> 195
$ printf '\xc3\xa9' | ./rune5                         (fgetrune after setlocale(LC_ALL, "en_US.UTF-8"))
after setlocale(LC_ALL, "en_US.UTF-8"): fgetrune -> 0 = U+0000
```

Four outcomes for one API. The macro path still works: `sgetrune` decodes `c3 a9` to `U+00E9`, consumes two bytes, and libc prints a three-line warning to stderr with the header's spelling. The named functions compile with a warning that dates the deprecation, link against `libSystem`, and then `setrunelocale` crashes rather than returning any of the three errno values the page lists. `fgetrune` alone does not crash but does not decode either: `195` is `0xC3`, the first byte of `é` handed back as a character of the C locale, and after `setlocale` it returns `0`. The page describes return values for functions that no longer return them, and nothing on it says since when.

**What the header declares.** The typedef chain `rune_t` resolves through, and how much of the locale structure is built on it.

```text title="Measured 2026-09-13 — macOS 26.6.2, in /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include. Not machine-checked."
$ grep -n 'typedef.*rune_t' sys/_types/_rune_t.h i386/_types.h
sys/_types/_rune_t.h:31:typedef __darwin_rune_t rune_t;
i386/_types.h:85:typedef int                     __darwin_ct_rune_t;     /* ct_rune_t */
i386/_types.h:129:typedef __darwin_ct_rune_t      __darwin_wchar_t;       /* wchar_t */
i386/_types.h:132:typedef __darwin_wchar_t        __darwin_rune_t;        /* rune_t */
$ grep -c __darwin_rune_t runetype.h
8
```

`rune_t` is `__darwin_rune_t` is `__darwin_wchar_t`, and the eight uses in `runetype.h` are fields of `_RuneLocale`, the structure every `isalpha` and `toupper` on this Mac reads: deprecated for you, load-bearing for libc.

## Where the page is dated, and what it does not say

**`mbrune(3)` is dated April 19, 1994 and `rune(3)` October 6, 2002.** The deprecation sentence was written for the C99 functions and the header dates it to macOS 10.4 (2005). Twenty-one years on, the header, the pages and the symbols are still shipped, one named entry point segfaults and another returns 0 for `é`, and the page says none of this. It does spell *deprecated* correctly, which the header and the run-time message do not.

**The `SEE ALSO` points at the wrong section.** `euc(4)` and `utf2(4)` find nothing; on this Mac the encoding pages are in section 5, where [`utf8(5)`](utf8.md) and [the CJK pages](cjk_encodings.md) read them.

**Neither page says `sgetrune` is a macro**, which is why it survives when the functions do not and why it complains at run time instead of compile time. **Neither says what a rune's value is.** `rune_t` is `wchar_t`, a code point only in a UTF-8 locale here, an EUC byte pair under `ja_JP.eucJP`; Plan 9's `Rune` was always a code point and Go's `rune` is an `int32` that may or may not hold one.

## See also

- [`multibyte(3)`](multibyte.md) — the replacement API, function for function, and the measurement that `wchar_t` is not always a code point here
- [`utf8(5)`](utf8.md) — `utf2(5)`, the *encoding of runes* these functions were written to read, and where `LC_CTYPE` lives on disk
- [`ctype(3)` and `wctype(3)`](ctype.md) — the classification macros that read the same `_RuneLocale` structure
- [`rune` is an `int32`](../../02_Characters/rune_is_an_int32/README.md) — the word's third life, in Go, and the one-`U+FFFD`-per-byte policy inherited from `sgetrune`
- [Why UTF-8 won](../../09_History/why_utf8_won/README.md) — Plan 9, where the word and the encoding come from
- [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) — what `sgetrune` does to `c3 a9`, with a pencil
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) — where this pair sits among the forty, and the short note this page extends
- [A page has a date](../a_page_has_a_date/README.md) — a 1994 page in a 2026 library
