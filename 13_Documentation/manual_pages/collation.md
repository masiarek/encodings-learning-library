# `strcoll(3)`, `strxfrm(3)` and `strcasecmp(3)`: the order is in a file, not in the string

**Level:** reference · for anyone who has typed `man 3 strcoll`, read *according to the current locale collation*, and wondered where that lives

**One line:** `strcmp` orders bytes and `strcoll` orders by the locale's `LC_COLLATE` file, so `B` sorts before `a` in the C locale and after it in `en_US.UTF-8`, and Polish `ó` moves from beside `o` to after it when the file is `pl_PL`'s; `strxfrm` turns a string into a key that `strcmp` sorts the same way, which is what a database index stores and why an index breaks when the file changes; and `strcasecmp` folds one byte at a time, so `É` and `é` are unequal in UTF-8 on both machines and equal only where the locale calls the single byte `0xC9` a letter.

**The pages:** [`strcoll(3)`](raw/macos/strcoll.3.txt) and [`strxfrm(3)`](raw/macos/strxfrm.3.txt) (macOS, both dated June 4, 1993) · [`wcscoll(3)`](raw/macos/wcscoll.3.txt) and [`wcsxfrm(3)`](raw/macos/wcsxfrm.3.txt) (October 4, 2002) · [`strcasecmp(3)`](raw/macos/strcasecmp.3.txt) (June 9, 1993) · [`wcscasecmp(3)`](raw/macos/wcscasecmp.3.txt), which on this Mac is the `wmemchr(3)` page listing twenty-six wide string functions (March 4, 2009). Ubuntu has a page under every name; none was dumped, and the glibc columns below are behaviour, not documentation. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

Three verbs, six pages. *Compare* is `strcoll`: two strings in, a sign out, and the sign comes from the locale's collation rather than from the bytes. *Transform* is `strxfrm`: one string in, a key out, built so that `strcmp` on two keys gives the sign `strcoll` would have given on the originals, which lets a sort compute each key once instead of consulting the locale on every comparison. *Compare ignoring case* is `strcasecmp`, older than either, kept in `<strings.h>` with an `s`, and with no idea that collation exists. The `wcs` pages are the same three verbs on `wchar_t`. All six are in **section 3**, and the two oldest, from 1993, are among the shortest pages in this folder: ten lines of description each.

They are in this library because of what [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) found: under one locale name, `en_US.UTF-8`, three builds of libc put a hyphen in three different places, and a database index built on one of them is wrong on the next. The function that produced those three orders is `strcoll`, the key the index stored is `strxfrm`'s, and the pages that document them say nothing about where the order comes from or that it can change. This page measures the same comparison on the two machines and reads the pages against the result.

## The page, with notes

### `strcoll(3)`: by the locale, or by bytes if there is none

```text title="man 3 strcoll, macOS 26.6.2, dumped 2026-09-13"
     The strcoll() function lexicographically compares the null-terminated
     strings s1 and s2 according to the current locale collation and returns
     an integer greater than, equal to, or less than 0, according as s1 is
     greater than, equal to, or less than s2.  If information about the
     current locale collation is not available, the value of strcmp(s1, s2) is
     returned.
```

*Lexicographically* means left to right, stopping at the first difference, but what counts as a difference and which side is greater are the collation's decisions, and the last sentence names the case where there is no collation: the C locale, where `strcoll` *is* `strcmp` and the order is byte order. Byte order puts every capital before every lower-case letter and every accented letter after `z`, which is the `LC_ALL=C` order [`tr` and `sort`](../../11_Tools/tr_and_sort/README.md) documents and the only order a script can rely on across machines. The experiment below shows the sign of `strcoll("B", "a")` flipping from -1 to +1 the moment a real collation is loaded, and `é` moving from after `f` to before it. On Ubuntu's stock image the only UTF-8 locale is `C.UTF-8`, whose `LC_COLLATE` is 1,406 bytes and agreed with `strcmp` on every pair tried, so the *ignorable punctuation* order the library page measured on glibc 2.39 needs `en_US.UTF-8` installed and could not be reproduced in this container; the library page did it on the same glibc with the locale present.

### `strxfrm(3)`: the key an index stores

```text title="man 3 strxfrm, macOS 26.6.2, dumped 2026-09-13"
     The strxfrm() function transforms a null-terminated string pointed to by
     s2 according to the current locale collation if any, then copies the
     transformed string into s1.  Not more than n characters are copied into
     s1, including the terminating null character added.  If n is set to 0 (it
     helps to determine an actual size needed for transformation), s1 is
     permitted to be a NULL pointer.

     Comparing two strings using strcmp() after strxfrm() is equal to
     comparing two original strings with strcoll().
```

The second paragraph is the promise every sorted index rests on. A sort key is a byte string whose byte order *is* the collation order, so once every row has one, plain `memcmp` sorts the table and a B-tree can be built over it without ever calling the locale again. The `n = 0` trick is how you learn the size first, because the key is not the string's length: the experiment shows `"a-b"` becoming 21 bytes under `en_US.UTF-8` on this Mac and staying 3 in the C locale. What the paragraph does not say is that the key is only as durable as the file it was derived from. glibc 2.28 corrected its collation data in 2018, keys computed under 2.27 no longer sorted the same as keys computed under 2.28, and [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) has the PostgreSQL consequences; Python's `locale.strxfrm` is this function and inherits all of it.

### `wcscoll(3)`, `wcsxfrm(3)`: a `BUGS` section that expired

```text title="man 3 wcscoll, macOS 26.6.2, dumped 2026-09-13"
     No return value is reserved to indicate errors; callers should set errno
     to 0 before calling wcscoll().  If it is non-zero upon return from
     wcscoll(), an error has occurred.
     ...
BUGS
     The current implementation of wcscoll() only works in single-byte
     LC_CTYPE locales, and falls back to using wcscmp() in locales with
     extended character sets.
```

Two paragraphs, one of them still true. The `errno` protocol is real and unusual: a comparison function has no spare return value for *failed*, so the caller zeroes `errno` beforehand and checks it afterwards, and `EILSEQ` means a `wchar_t` in the string was not a valid character in the current locale. The `BUGS` paragraph, dated 2002, says the wide function gives up in any multibyte locale and compares code points instead. On this Mac in 2026 it does not: `wcscoll(L"é", L"f")` under `en_US.UTF-8` is -1, the collation's answer, where `wcscmp` would say +1 because `0xE9` is greater than `0x66`. The page describes a limitation that was fixed and never taken off the page. `wcsxfrm(3)` carries a second `BUGS` note, that its keys hold only primary weights and so `wcscmp` on them is not always `wcscoll`; that one was not measured here.

### `strcasecmp(3)`: fold each byte, then compare unsigned

```text title="man 3 strcasecmp, macOS 26.6.2, dumped 2026-09-13"
     The strcasecmp() and strncasecmp() return an integer greater than, equal
     to, or less than 0, according as s1 is lexicographically greater than,
     equal to, or less than s2 after translation of each corresponding
     character to lower-case.  The strings themselves are not modified.  The
     comparison is done using unsigned characters, so that `\200' is greater
     than `\0'.
```

*Each corresponding character* is each byte, *translation to lower-case* is `tolower(3)` from [`ctype(3)`](ctype.md), and *unsigned characters* means the bytes above `0x7F` compare as 128 to 255 rather than as negative numbers; `\200` is octal for `0x80`. Nothing here is collation and nothing is Unicode. So `É` and `é` in UTF-8, `c3 89` against `c3 a9`, differ in their second byte and are unequal on both machines in every locale: `tolower(0x89)` is `0x89` everywhere. The single Latin-1 bytes `c9` and `e9` are another matter, and the experiment shows them equal in every non-C locale on this Mac, including the UTF-8 ones, because this libc's `tolower` maps Latin-1 bytes whatever the locale's encoding, and unequal everywhere on glibc. A case-insensitive lookup written with this function is therefore ASCII-only on one machine and Latin-1-ish on the other, and neither is a fold of the *characters*. [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) is the reason, and [Two people, one account](../../12_Adversarial/collisions_by_design/README.md) is what happens when such a fold decides who a user is.

### `wcscasecmp(3)`: twenty-six functions, one sentence

```text title="man 3 wcscasecmp, macOS 26.6.2, dumped 2026-09-13"
     The functions implement string manipulation operations over wide
     character strings.  For a detailed description, refer to documents for
     the respective single-byte counterpart, such as memchr(3).
```

The whole description of `wcscasecmp`, and it refers you to a page that says *each corresponding character*, which now means each `wchar_t` through `towlower`. That is a real case fold at the code point level, one-to-one, and the experiment shows it giving 0 for `É`/`é` and `Ź`/`ź` under a UTF-8 locale on both machines; under the C locale both libcs say nothing above `0x7F` has a case, and under `en_US.ISO8859-1` the Mac folds `É` but not `Ź`, which Latin-1 does not contain.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| collation, *current locale collation* | The order a language reads its alphabet in, as a data file the locale loads; not the same as byte order or code point order | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| `LC_COLLATE` | The locale category that file belongs to, set separately from `LC_CTYPE`; 81 KB for `en_US.UTF-8` on this Mac, 1,406 bytes for `C.UTF-8` on Ubuntu | [`locale(1)` and `setlocale(3)`](locale.md) |
| *lexicographically* | Left to right, stop at the first difference; which differences count is the collation's business | [`tr` and `sort`](../../11_Tools/tr_and_sort/README.md) |
| `strcmp` | Byte order, unsigned, no locale: the order `LC_ALL=C sort` produces and the only one that is the same on every machine | [`tr` and `sort`](../../11_Tools/tr_and_sort/README.md) |
| *transformed string*, sort key | `strxfrm`'s output: bytes whose `strcmp` order equals the originals' `strcoll` order | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| `n` set to 0 | Ask for the key's length without writing it, then allocate; the key is longer than the string | |
| primary, secondary weights | The levels of a multi-level comparison: base letters first, then accents, then case; `wcsxfrm` keeps only the first | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| ignorable | A character the collation treats as absent at the first level, such as a hyphen on glibc 2.39; the reason `a-b` and `ab` can tie | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| *unsigned characters*, `\200` | Bytes compared as 0 to 255, so `0x80` sorts after `0x7F` rather than before `0x00`; `\200` is octal 128 | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| *translation to lower-case* | `tolower(3)` per byte in `strcasecmp`, `towlower(3)` per code point in `wcscasecmp`; one-to-one either way | [`ctype(3)` and `wctype(3)`](ctype.md) |
| `<strings.h>` | The BSD header, with an `s`, where POSIX filed `strcasecmp` to keep it out of ISO C's `<string.h>` | |
| `EILSEQ` | *Illegal byte sequence*: a `wchar_t` that is not a character of the locale, reported through `errno` because the return value is taken | [`multibyte(3)`](multibyte.md) |
| `strcoll_l`, `xlocale(3)` | The same functions with a locale handle instead of the global one, for a program that sorts two languages at once | [`locale(1)` and `setlocale(3)`](locale.md) |
| `restrict` | A C99 promise that the key buffer and the input do not overlap | |
| ISO C90, C99, POSIX.1-2008 | `strcoll` and `strxfrm` are C90; the `wcs` pair C99; `wcscasecmp` POSIX-only, which is why it is on the `wmemchr` page's exception list | |

## Try it on your machine

**The sign of a comparison, under six locales.** One C program, each column a `setlocale` call; `+1` means the first string sorts after the second, `+0` means equal. `en_US.ISO8859-1` is the Mac's Latin-1 locale, given UTF-8 bytes it reads as Latin-1.

```text title="Measured 2026-09-13 — macOS 26.6.2 (libSystem) and ubuntu:24.04 (glibc 2.39; en_US and pl_PL are not installed there). Not machine-checked."
  sign of the result                                        macOS            macOS            macOS            macOS           ubuntu           ubuntu
                                                                C      en_US.UTF-8      pl_PL.UTF-8  en_US.ISO8859-1                C          C.UTF-8
  strcmp("a-b","ab")                                           -1               -1               -1               -1               -1               -1
  strcoll("a-b","ab")                                          -1               -1               -1               -1               -1               -1
  strcoll("a b","ab")                                          -1               -1               -1               -1               -1               -1
  strcoll("B","a")                                             -1               +1               +1               +1               -1               -1
  strcoll("é","f")                                             +1               -1               -1               -1               +1               +1
  wcscoll(L"a-b",L"ab")                                        -1               -1               -1               -1               -1               -1
  wcscoll(L"\u00e9",L"f")                                      +1               -1               -1               -1               +1               +1
  strcasecmp("A","a")                                          +0               +0               +0               +0               +0               +0
  strcasecmp("É","é") [c3 89 vs c3 a9]                         -1               -1               -1               -1               -1               -1
  strcasecmp("\xc9","\xe9") [one byte each]                    -1               +0               +0               +0               -1               -1
  wcscasecmp(L"\u00c9",L"\u00e9")                              -1               +0               +0               +0               -1               +0
  wcscasecmp(L"\u0179",L"\u017a")                              -1               +0               +0               -1               -1               +0
```

Row by row. `a-b` before `ab` in every column, which for this Mac is the *punctuation before letters* order the library page recorded and for the C locales is byte order; the two agree on these strings by coincidence, and glibc's *ignorable* answer, where the hyphen is skipped and the strings tie-break, needs a locale this container lacks. `B` against `a` is the row that shows a collation loading: byte order says `B` first, every real locale says `a` first. `é` against `f` shows the same thing for accents. The `wcscoll` rows match the `strcoll` rows in the UTF-8 columns, which is the `BUGS` paragraph expiring. And the four `casecmp` rows are the two folds: the UTF-8 spelling of `É` never equals `é` byte-wise, the single Latin-1 bytes are equal wherever this Mac's `tolower` runs and never on glibc, and the wide fold is a Unicode fold in a UTF-8 locale on both.

**Fourteen strings, sorted.** `qsort` with `strcoll` as the comparator, under each locale, and the same list under `strcmp`; then `sort(1)` on the ten Polish words as a cross-check that the C library and the tool agree.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
  macOS   C                Osa a b a-b aa ab lód mak osa pas zebra óda łódź źle żuk
  macOS   en_US.UTF-8      a b a-b aa ab lód łódź mak óda osa Osa pas zebra źle żuk
  macOS   pl_PL.UTF-8      a b a-b aa ab lód łódź mak osa Osa óda pas zebra źle żuk
  macOS   en_US.ISO8859-1  a b a-b aa łódź ab óda źle żuk lód mak osa Osa pas zebra
  ubuntu  C                Osa a b a-b aa ab lód mak osa pas zebra óda łódź źle żuk
  ubuntu  C.UTF-8          Osa a b a-b aa ab lód mak osa pas zebra óda łódź źle żuk
  both    strcmp (bytes)   Osa a b a-b aa ab lód mak osa pas zebra óda łódź źle żuk

$ LC_ALL=en_US.UTF-8 sort words.txt | tr '\n' ' '      (macOS)     lód łódź mak óda osa Osa pas zebra źle żuk
$ LC_ALL=pl_PL.UTF-8 sort words.txt | tr '\n' ' '      (macOS)     lód łódź mak osa Osa óda pas zebra źle żuk
$ LC_ALL=C.UTF-8 sort words.txt | tr '\n' ' '          (ubuntu)    Osa lód mak osa pas zebra óda łódź źle żuk
```

Four orders. Byte order (`C`, and `C.UTF-8` on both machines) puts `Osa` first and every accented word last, as `sort` in a container does. English puts `óda` between `mak` and `osa`, because `ó` is an `o` with a secondary difference and `d` comes before `s`. Polish puts `óda` after `Osa`, because `ó` is a letter of its own that follows `o`, which is the one swap the library page's Polish section is about. And the Latin-1 column is what a collation does to bytes it was not built for: `łódź` between `aa` and `ab`, because `c5 82` read as Latin-1 is `Å` followed by a control character. `sort(1)` reproduced the C-library orders exactly, so the tool is not adding an opinion; [`look`](../../11_Tools/look_paste_tee_split/README.md) needs the same guarantee and does not check it.

**What the key looks like.** `strxfrm` of four strings, length and first bytes.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
  macOS   C                strxfrm("a-b") ->  3 bytes: 61 2d 62
  macOS   C                strxfrm("é") ->  2 bytes: c3 a9
  macOS   en_US.UTF-8      strxfrm("a-b") -> 21 bytes: 30 67 30 38 31 35 2e 31 31 31 2e 31 31 31 2e 31 ...
  macOS   en_US.UTF-8      strxfrm("ab") -> 15 bytes: 30 67 31 35 2e 31 31 2e 31 31 2e 31 44 33 33
  macOS   en_US.UTF-8      strxfrm("é") -> 11 bytes: 31 56 2e 31 36 2e 31 31 2e 34 6e
  macOS   en_US.UTF-8      strxfrm("e") ->  9 bytes: 31 56 2e 31 2e 31 2e 34 67
  macOS   pl_PL.UTF-8      strxfrm("é") -> 11 bytes: 31 58 2e 31 36 2e 31 31 2e 34 6e
  ubuntu  C.UTF-8          strxfrm("a-b") ->  3 bytes: 61 2d 62
  ubuntu  C.UTF-8          strxfrm("é") ->  2 bytes: c3 a9
```

In the C locale the key is the string. Under a real collation on this Mac it is a printable string of weights, seven times longer than `a-b`, in which `é` and `e` share their first bytes `31 56` and differ further along, which is *secondary difference* written out; the same `é` under `pl_PL` starts `31 58`, a different primary weight, because Polish gives the accented vowels their own places. Two keys, two locales, and `strcmp` on the wrong pair is meaningless, which is why an index has to record which collation made it.

## Where the page is dated, and what it does not say

**`strcoll(3)` and `strxfrm(3)` are dated June 4, 1993 and `strcasecmp(3)` June 9, 1993**; `wcscoll(3)` and `wcsxfrm(3)` are from 2002 and the `wmemchr(3)` page from 2009. None of the six contains the word Unicode, ISO 14651, CLDR, or *version*, and the collation file the 1993 page reads on this Mac is 81 KB of rules that were not written in 1993.

**`wcscoll(3)`'s `BUGS` section describes a fallback that no longer happens.** The measurement above shows `wcscoll` collating `é` correctly under `en_US.UTF-8`; the paragraph has outlived the bug.

**No page says the order can change under a stored key.** `strxfrm`'s promise is stated as an identity and holds only for one build of one file; the glibc 2.28 change and the PostgreSQL warning it eventually produced are on [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md).

**`strcasecmp(3)` does not say what happens above `0x7F`**, and the two libcs do different things there: glibc leaves the byte alone, this Mac lower-cases it as Latin-1 in every non-C locale, including the UTF-8 ones where the byte is not a character. *ASCII case-insensitive* is a description of glibc's behaviour, not of the page.

**Nothing on the pages connects `look`, `sort`, `uniq` and a database to one another**, though all of them are consumers of this one function and disagree the moment they run under different `LC_COLLATE` values: [`split` cuts characters, `paste` cuts delimiters, `look` needs a sorted file, `tee` does nothing](../../11_Tools/look_paste_tee_split/README.md) has the `look` half.

## See also

- [`ctype(3)` and `wctype(3)`](ctype.md) — `tolower` and `towlower`, the two folds inside the two `casecmp` functions
- [`locale(1)` and `setlocale(3)`](locale.md) — how `LC_COLLATE` gets set, and why `LC_ALL` overrides it
- [The locale source files](locale_files.md) — what a collation definition looks like before it is compiled
- [Lines and fields](lines_and_fields.md) — `sort`, `uniq`, `comm` and `join`, the tools that call `strcoll`
- [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) — the three orders under one locale name, and the index they corrupt
- [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) — why a one-to-one fold is the wrong tool for a string
- [Two people, one account](../../12_Adversarial/collisions_by_design/README.md) — a case-insensitive lookup deciding who you are
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) — `LC_ALL=C` as the only portable order
- [`split`, `paste`, `look`, `tee`](../../11_Tools/look_paste_tee_split/README.md) — `look` bringing its own collation to a file sorted with another
- [A page has a date](../a_page_has_a_date/README.md) — a 1993 page for a file that changed in 2018
