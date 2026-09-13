# `ctype(3)` and `wctype(3)`: is this byte a letter, is this code point a letter, and who decides

**Level:** reference · for anyone who has typed `man 3 isalpha`, read *must be representable as an unsigned char*, and wondered whether their `char` is

**One line:** The narrow functions take one byte value (0 to 255, or `EOF`) and answer from the locale's `LC_CTYPE` table, so `isalpha(0xE9)` is 0 in the C locale, 1 in every other locale on this Mac and 0 in every locale on glibc, and a plain `char` holding `é` is undefined behaviour; the wide functions take one code point and answer from a Unicode table, one character in and one out, which is why `towupper(L'ß')` is still `ß`; and the class names `wctype` accepts are the `[:alpha:]` of `grep`, `tr` and every POSIX regex.

**The pages:** narrow, `<ctype.h>`: [`ctype(3)`](raw/macos/ctype.3.txt) (macOS, dated March 30, 2004) · [`isalpha(3)`](raw/macos/isalpha.3.txt), [`isprint(3)`](raw/macos/isprint.3.txt), [`tolower(3)`](raw/macos/tolower.3.txt), [`toupper(3)`](raw/macos/toupper.3.txt) (July 17, 2005) · [`isascii(3)`](raw/macos/isascii.3.txt) (October 6, 2002) · [`toascii(3)`](raw/macos/toascii.3.txt) (June 4, 1993). Wide, `<wctype.h>`: [`wctype(3)`](raw/macos/wctype.3.txt) and its alias [`iswctype(3)`](raw/macos/iswctype.3.txt) (March 27, 2004) · [`iswalpha(3)`](raw/macos/iswalpha.3.txt), [`towlower(3)`](raw/macos/towlower.3.txt), [`towupper(3)`](raw/macos/towupper.3.txt), [`wctrans(3)`](raw/macos/wctrans.3.txt) and its alias [`towctrans(3)`](raw/macos/towctrans.3.txt) (October 3, 2002). Ubuntu has a page under every one of these names; none was dumped, and the glibc columns below are behaviour, not documentation. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

`<ctype.h>` is the oldest text API in C: a dozen yes-or-no questions about one character (*is it a letter, a digit, a space, printable*) and two conversions (*upper-case it, lower-case it*), standardised in C90 and older than that. The pages sit in **section 3**, one per function plus the index page `ctype(3)`, and every narrow page was written when a character was a byte. The octal tables on `isalpha(3)` and `isprint(3)` list the ASCII members of each class and stop at `0177`, and the sentence above each table, *the value of the argument must be representable as an unsigned char or the value of EOF*, is the whole contract: the argument is an `int` so that `EOF`, which is -1, can be passed, and every other legal value is a byte.

`<wctype.h>` asks the same questions of a `wchar_t`, and was added by C99 alongside the [`multibyte(3)`](multibyte.md) functions that produce one. Its pages are shorter because they defer to the narrow ones for meaning (*see the description for the similarly-named single byte classification functions*), and they add two ideas the narrow API never had: `wctype(3)` turns the *name* of a class into a handle, so a program can ask about a class chosen at run time, and `wctrans(3)` does the same for the two case mappings. The BSD pages also list four classes of their own, `ideogram`, `phonogram`, `special` and `rune`, which glibc does not have.

The family is in this library because every answer above `0x7F` is a property of the locale, not of the byte or the code point, and the two machines this library runs on give different answers to the same byte. That is [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) at the level of one function call, and the experiments below measure it.

## The page, with notes

### `ctype(3)`: the index, and which of the twenty-three are C

```text title="man 3 ctype, macOS 26.6.2, dumped 2026-09-13"
     digittoint, isalnum, isalpha, isascii, isblank, iscntrl, isdigit,
     isgraph, ishexnumber, isideogram, islower, isnumber, isphonogram,
     isprint, ispunct, isrune, isspace, isspecial, isupper, isxdigit, toascii,
     tolower, toupper - character classification macros
     ...
     They are available as macros, defined in the include file
     <ctype.h>, or as true functions in the C library.
     ...
STANDARDS
     These functions, except for digittoint(), isascii(), ishexnumber(),
     isideogram(), isnumber(), isphonogram(), isrune(), isspecial() and
     toascii(), conform to ISO/IEC 9899:1990 ("ISO C90").
```

Twenty-three names, nine of them BSD's own. *Macros or true functions* matters twice: a macro may evaluate its argument more than once, so `isalpha(*p++)` is a bug on some libcs, and a macro cannot be marked deprecated, which is the same reason `sgetrune` on the [`rune(3)`](rune.md) page compiles without a word. The nine extensions include `isascii` and `toascii`, and the experiment below shows glibc declining to declare them under `-std=c11`, exactly as this `STANDARDS` line predicts.

### `isalpha(3)`, `isprint(3)`: the unsigned-char rule

```text title="man 3 isalpha, macOS 26.6.2, dumped 2026-09-13"
     The isalpha() function tests for any character for which isupper(3) or
     islower(3) is true.  The value of the argument must be representable as
     an unsigned char or the value of EOF.

     In the ASCII character set, this includes the following characters
     (preceded by their numeric values, in octal):

     101 ``A'' 102 ``B'' 103 ``C'' 104 ``D'' 105 ``E''
     ...
COMPATIBILITY
     The 4.4BSD extension of accepting arguments outside of the range of the
     unsigned char type in locales with large character sets is considered
     obsolete and may not be supported in future releases.  The iswalpha()
     function should be used instead.
```

Three sentences, three traps. *Representable as an unsigned char* means 0 to 255, and on this Mac and on x86 Linux a plain `char` is signed, so the byte `0xE9` stored in one is the integer -23 and `isalpha(c)` with that `c` is undefined behaviour. The measured line below shows each libc returning *something* for it, and that is the danger: it does not crash, it answers a different question. The fix is the cast, `isalpha((unsigned char)c)`, on every call. *In the ASCII character set* is a hedge: the table fixes the answer for 52 letters and says nothing about `0x80` to `0xFF`, where the answer belongs to the locale. And the `COMPATIBILITY` paragraph describes an extension, passing a whole code point to a narrow function, that the page has called obsolete since 2005 and that this Mac still honours in 2026: `isalpha(0x4E2D)` is 1.

`isprint(3)` is the same page for the *printable* class, space included and `0177` excluded, and its interesting member is not in its table: `0xA0`, NO-BREAK SPACE, which is printable and a space in a UTF-8 locale on this Mac and neither in the C locale. [Control characters](../../02_Characters/control_characters/README.md) is the page for what *printable* excludes.

### `isascii(3)`, `toascii(3)`: bit 7

```text title="man 3 toascii, macOS 26.6.2, dumped 2026-09-13"
     The toascii() function strips all but the low 7 bits from a letter,
     including parity or other marker bits.

RETURN VALUES
     The toascii() function always returns a valid ASCII character.
```

The oldest page in the family, dated 1993, and it says *parity bits* because that is what the high bit was on a serial line. `toascii(0xE9)` is `0x69`, the letter `i`: not a transliteration of `é` but the bottom seven bits of it, and *always returns a valid ASCII character* is true in the way that always returning 0 would be. There is no locale in it, which makes it the one function in the family whose answer is the same everywhere. [A character is a number](../../02_Characters/a_character_is_a_number/README.md) is the page for what a byte is before anyone interprets it, and [`ascii(7)`](ascii.md) is the 128 values it can return.

### `tolower(3)`, `toupper(3)`: one byte in, one `int` out

```text title="man 3 toupper, macOS 26.6.2, dumped 2026-09-13"
     The toupper() function converts a lower-case letter to the corresponding
     upper-case letter.  The argument must be representable as an unsigned
     char or the value of EOF.
     ...
     If the argument is a lower-case letter, the toupper() function returns
     the corresponding upper-case letter if there is one; otherwise, the
     argument is returned unchanged.
```

*If there is one* is doing the work. In the C locale nothing above `0x7F` has one, on either machine. In a UTF-8 locale glibc still says nothing above `0x7F` has one, because a lone byte `0xE9` is not a character in UTF-8. This Mac says `toupper(0xE9)` is `0xC9`, the Latin-1 answer, and applied byte by byte to a UTF-8 string that turns `€` into an invalid sequence, which is finding 43 on [C or Rust for text](../../10_Best_Practices/c_or_rust_for_text/README.md). Both conform, because the page only promises an answer for letters and whether a byte is a letter is the locale's call.

### `wctype(3)`: a class name becomes a handle

```text title="man 3 wctype, macOS 26.6.2, dumped 2026-09-13"
     The following character class names are recognised:

           alnum       cntrl       ideogram       print       space       xdigit
           alpha       digit       lower          punct       special
           blank       graph       phonogram      rune        upper
     ...
           int
           myiswalpha(wint_t wc)
           {
                   return (iswctype(wc, wctype("alpha")));
           }
     ...
     The "ideogram", "phonogram", "special", and "rune"
     character classes are extensions.
```

Sixteen names, twelve of them standard, and those twelve are exactly the names POSIX puts between `[:` and `:]` in a bracket expression. `grep '[[:alpha:]]'`, `tr '[:lower:]' '[:upper:]'` and `iswctype(wc, wctype("alpha"))` ask the locale one question through three doors, and the experiment below shows all three getting the locale's answer. `wctype("bogus")` returns 0, and `iswctype` is documented to return non-zero *or charclass is zero*, which is a quiet way of saying that a misspelled class name matches everything. [What a regex matches](../../02_Characters/what_a_regex_matches/README.md) is where the class names meet Unicode properties; [`grep`](../../11_Tools/grep/README.md) and [`tr` and `sort`](../../11_Tools/tr_and_sort/README.md) are where they meet bytes.

### `iswalpha(3)`, `towupper(3)`, `wctrans(3)`: the same questions of a code point

```text title="man 3 iswalpha, macOS 26.6.2, dumped 2026-09-13"
CAVEATS
     The result of these functions is undefined unless the argument is WEOF or
     a valid wchar_t value for the current locale.
```

```text title="man 3 towupper, macOS 26.6.2, dumped 2026-09-13"
     If the argument is a lower-case letter, the towupper() function returns
     the corresponding upper-case letter if there is one; otherwise, the
     argument is returned unchanged.
```

The wide page has the same *if there is one*, and now it hides a different fact. `towupper` maps one `wint_t` to one `wint_t`, so it can only return a single character, and `ß` has no single upper-case letter: its upper case is the two letters `SS`. The function returns `ß` unchanged and the wording makes that look like *no upper case exists*, when what is true is *none that fits the return type*. [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) is that sentence at full length, with `İ` going the other way: `towlower(L'İ')` is a plain `i` on both machines, and the full mapping is `i` plus a combining dot. Two answers the wide table does give: `towupper(L'ÿ')` is `Ÿ`, `U+0178`, a letter outside Latin-1 entirely, which is why no single-byte table could ever have held it; and `towupper(L'ż')` is `Ż`. The `wctrans` page adds that the mapping names are exactly two, `tolower` and `toupper`; `wctrans("upper")` is 0 and sets `errno`. And the `CAVEATS` line is the wide form of the unsigned-char rule: a `wchar_t` holding a surrogate, or an EUC byte pair under a Japanese locale, is not *a valid wchar_t value for the current locale*, and the answer is undefined.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| *representable as an unsigned char* | 0 to 255: the argument is a byte value, and a signed `char` holding a byte above `0x7F` is a negative number that is not | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| `EOF`, `WEOF` | -1 and its wide twin: the one non-character value the functions must accept, so a `getchar` result can be tested directly | [`stdio(3)` and the wide stream functions](stdio.md) |
| character classification | Sorting characters into named sets (letter, digit, space, punctuation) rather than converting them | [A character is a number](../../02_Characters/a_character_is_a_number/README.md) |
| macro, *true function* | Each name exists both ways; the macro may evaluate its argument twice and cannot carry a deprecation attribute | [`rune(3)`](rune.md) |
| *the current locale*, `LC_CTYPE` | The table every answer above `0x7F` comes from; the C locale until `setlocale` is called | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `ctype_l`, `xlocale(3)`, `locale_t` | The `_l` twins take a locale handle instead of using the global one | [`locale(1)` and `setlocale(3)`](locale.md) |
| *In the ASCII character set* | The 128 values whose answers are fixed; the octal tables list them and nothing above | [`ascii(7)`](ascii.md) |
| 4.4BSD extension, *locales with large character sets* | Passing a code point to a narrow function; called obsolete in 2005, still working here | [`rune(3)`](rune.md) |
| parity bit, marker bits | The high bit of a byte used as a checksum on a serial line, which `toascii` strips | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| `wctype_t`, `wctrans_t` | Opaque handles for a class and a mapping, made from their names | [What a regex matches](../../02_Characters/what_a_regex_matches/README.md) |
| `alpha` … `xdigit`, `[:alpha:]` | The twelve POSIX class names; the same strings inside a bracket expression | [`grep`](../../11_Tools/grep/README.md) |
| `ideogram`, `phonogram`, `special`, `rune` | BSD's own classes: CJK ideographs, kana, and the catch-all *rune* for every valid character | [The CJK pages](cjk_encodings.md) |
| *corresponding upper-case letter, if there is one* | A one-to-one mapping; the cases with no single answer (`ß`, `İ`) are returned unchanged | [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) |
| NO-BREAK SPACE `0xA0` | Latin-1's non-breaking space; printable and a space in a UTF-8 locale here, neither in the C locale | [Where a line may break](../../02_Characters/where_a_line_may_break/README.md) |

## Try it on your machine

**One byte, four locales.** The narrow functions on the bytes of `é`, `É` and NO-BREAK SPACE as Latin-1 spells them. The C program calls `setlocale` for each column; Ubuntu has only `C` and `C.UTF-8`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (libSystem) and ubuntu:24.04 (glibc 2.39). Not machine-checked."
                                      macOS            macOS            macOS            macOS           ubuntu           ubuntu
                                          C  en_US.ISO8859-1      en_US.UTF-8          C.UTF-8                C          C.UTF-8
  isalpha(0xE9)                           0                1                1                1                0                0
  isupper(0xC9)                           0                1                1                1                0                0
  isprint(0xA0)                           0                0                1                1                0                0
  ispunct(0xA0)                           0                0                0                0                0                0
  isspace(0xA0)                           0                0                1                1                0                0
  toupper(0xE9)                        0xE9             0xC9             0xC9             0xC9             0xE9             0xE9
  tolower(0xC9)                        0xC9             0xE9             0xE9             0xE9             0xC9             0xC9
```

Read down the `isalpha(0xE9)` row. In the C locale both libcs say the byte is not a letter. In `en_US.ISO8859-1`, where the byte *is* `é`, this Mac says it is. In the two UTF-8 locales this Mac still says it is, and glibc says it is not: `0xE9` on its own is not a character in UTF-8, only the tail of one, and glibc is answering the question the locale actually asks. The `toupper` row is the same split with a consequence, since the Mac's `0xC9` written back into a UTF-8 string is a stray lead byte. Nothing on the pages predicts either column; *if there is one* covers both.

**One code point, four locales.** The wide functions on `é`, `ż`, `中`, NO-BREAK SPACE, `Ÿ`, `ß`, `ÿ` and `İ`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (libSystem) and ubuntu:24.04 (glibc 2.39). Not machine-checked."
                                      macOS            macOS            macOS            macOS           ubuntu           ubuntu
                                          C  en_US.ISO8859-1      en_US.UTF-8          C.UTF-8                C          C.UTF-8
  iswalpha(U+00E9)                        0                1                1                1                0                1
  iswalpha(U+017C)                        0                0                1                1                0                1
  iswalpha(U+4E2D)                        0                0                1                1                0                1
  iswprint(U+00A0)                        0                0                1                1                0                1
  iswupper(U+0178)                        0                0                1                1                0                1
  towupper(U+00E9)                   U+00E9           U+00C9           U+00C9           U+00C9           U+00E9           U+00C9
  towupper(U+00DF ss)                U+00DF           U+00DF           U+00DF           U+00DF           U+00DF           U+00DF
  towupper(U+00FF)                   U+00FF           U+00FF           U+0178           U+0178           U+00FF           U+0178
  towupper(U+017C)                   U+017C           U+017C           U+017B           U+017B           U+017C           U+017B
  towlower(U+0130)                   U+0130           U+0130           U+0069           U+0069           U+0130           U+0069
```

Two things to see. The UTF-8 columns agree across the two libcs on every row: once the argument is a code point the table is Unicode's and the answers converge, where the byte table above diverged. And the `ß` row is `U+00DF` in all six columns, the one-to-one limit of the API, while `ÿ` goes to `U+0178`, outside Latin-1, and `İ` comes down to a bare `i`. Under `en_US.ISO8859-1` the Mac's wide table is Latin-1's: `ż`, `中` and `Ÿ` are not characters there at all.

**The trap, the bit, and the handle.** The remaining lines of the same program under `C.UTF-8`: the signed `char`, the two locale-free functions, and `wctype`.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04, under C.UTF-8. Not machine-checked."
  macOS   (int)(char)0xE9 = -23   isalpha((unsigned char)c)=1   isalpha(c)=0
  ubuntu  (int)(char)0xE9 = -23   isalpha((unsigned char)c)=0   isalpha(c)=0

  under C.UTF-8                  macOS                  ubuntu:24.04
  isascii(0xE9)                  0                      0
  toascii(0xE9)                  0x69 ('i')             0x69 ('i')
  wctype("alpha")                nonzero                nonzero
  wctype("bogus")                0                      0
  iswctype(U+00E9, alpha)        1                      1
  iswctype(U+00E9, punct)        0                      0
  wctrans("toupper")             nonzero                nonzero
  wctrans("upper")               0                      0
  towctrans(U+00E9, toupper)     U+00C9                 U+00C9
```

The first two lines are the trap. The same byte in a `char` is -23 on both machines; cast to `unsigned char` it is 233 and this Mac calls it a letter; passed uncast it is undefined behaviour, and both libcs happened to return 0 today, which is the *wrong answer on the Mac and the right one by accident on glibc*. Nothing warned. `toascii` is the same on both because it never consults a locale, and the `wctype` lines show the handle working identically: a real name gives a handle, `bogus` gives 0, and `towctrans` through the `toupper` handle is `towupper`.

**The obsolete extension, still switched on.** Code points, not bytes, handed to the narrow functions on this Mac under `en_US.UTF-8`.

```text title="Measured 2026-09-13 — macOS 26.6.2 only; on glibc this is out-of-bounds table access and was not run. Not machine-checked."
isalpha(0x017C z-dot)=1  isalpha(0x4E2D zhong)=1  isalpha(0x1F600)=0  toupper(0x017C)=0x17B  tolower(0x0178)=0xFF  isprint(0x1F600)=1
```

`isalpha(3)` said in 2005 that this *may not be supported in future releases*. In 2026 `isalpha(0x4E2D)` is 1 and `toupper(L'ż')` through the narrow function is `Ż`. The extension is why old BSD code that passed a `wchar_t` to `isalpha` still works here and crashes or lies elsewhere.

**The same names in `grep` and `tr`.** The system tools, not the ones on `PATH`: `/usr/bin/grep` here is BSD grep 2.6.0 and `/usr/bin/tr` is BSD `tr`; on Ubuntu they are GNU grep 3.11 and GNU `tr`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (LC_ALL=en_US.UTF-8 as the UTF-8 locale) and ubuntu:24.04 (LC_ALL=C.UTF-8). Not machine-checked."
                                                               macOS (BSD)      ubuntu:24.04 (GNU)
$ printf 'é1ż\n' | LC_ALL=<utf-8> grep -o '[[:alpha:]]'        é ż              é ż
$ printf 'é1ż\n' | LC_ALL=C       grep -o '[[:alpha:]]'        (nothing)        (nothing)
$ printf 'é1ż\n' | LC_ALL=<utf-8> tr '[:lower:]' '[:upper:]'   É1Ż              é1ż
$ printf 'é1ż\n' | LC_ALL=<utf-8> tr -d '[:alpha:]'            1                é1ż
```

`grep` on both machines answers as `iswalpha` does: two letters in a UTF-8 locale, none in the C locale, because `[[:alpha:]]` is `wctype("alpha")` asked by a regex engine. `tr` is the odd one out: BSD `tr` decodes and answers per character, GNU `tr` works on bytes and neither upper-cases nor deletes anything above `0x7F`, which is the split [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) is named for. One class name, one locale, and two tools reading it through different decoders.

**Two extensions under strict C11.** Compiling the same source on both machines.

```text title="Measured 2026-09-13 — ubuntu:24.04 (gcc 13.3, glibc 2.39) and macOS 26.6.2 (Apple clang 21). Not machine-checked."
$ gcc -std=c11 -Wall -Wextra -o m m.c                     (ubuntu)
m.c: In function ‘main’:
m.c:33:83: warning: implicit declaration of function ‘isascii’ [-Wimplicit-function-declaration]
m.c:33:108: warning: implicit declaration of function ‘toascii’ [-Wimplicit-function-declaration]
$ cc -std=c11 -Wall -Wextra -o m_ctype m_ctype.c          (macOS: no diagnostics)
```

The `STANDARDS` line on `ctype(3)` lists `isascii` and `toascii` among the non-C90 names, and glibc takes that seriously: in strict C11 mode `<ctype.h>` does not declare them, the program still links because the functions exist, and it runs on an implicit declaration that C23 makes an error. This Mac's header declares them regardless.

## Where the page is dated, and what it does not say

**`toascii(3)` is dated 1993, `isascii(3)` 2002, `ctype(3)` and `wctype(3)` 2004, and `isalpha(3)`, `isprint(3)`, `tolower(3)` and `toupper(3)` July 17, 2005**, the date the `COMPATIBILITY` paragraph about the 4.4BSD extension was added. Twenty-one years later the extension it calls obsolete is measured above, still on.

**The pages never say what a byte above `0x7F` is.** The octal tables stop at `0177`, and the two libcs give different answers for `0xE9` in a UTF-8 locale: this Mac treats the byte as the Latin-1 character with that number, glibc treats it as not a character. Neither behaviour is on any page, and neither is wrong by the page's wording, which is why finding 43 on [C or Rust for text](../../10_Best_Practices/c_or_rust_for_text/README.md) forbids byte-wise `toupper` on UTF-8 text in this library's examples.

**The pages state the unsigned-char rule and not its consequence.** A signed `char` passed uncast is not an error the compiler reports, and the measurement shows it returning a plausible 0 on both machines for a byte one of them calls a letter.

**The wide pages say *corresponding upper-case letter* as if there were always one.** `ß` and `İ` show the one-to-one API returning the input or losing a dot, and no page mentions `SS`, Turkish, or that a string's case mapping can change its length: [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md), and [Two people, one account](../../12_Adversarial/collisions_by_design/README.md) for the case where a fold that merges two letters merges two users.

**No page mentions Unicode or a version.** `iswalpha` and `towupper` answer from a table with an edition, and [`wcwidth(3)`](wcwidth.md) dates the two editions on these machines to Unicode 15.0 and 15.1.

**`wctype(3)` does not say its names are the regex classes**, and `iswctype(wc, 0)` returning non-zero is stated as a return value rather than as the trap it is.

## See also

- [`multibyte(3)`](multibyte.md) — where the `wchar_t` these functions take comes from, and why on this Mac it is not always a code point
- [`wcwidth(3)` and `wcswidth(3)`](wcwidth.md) — `iswprint` as a column count, and the Unicode edition behind the wide tables
- [`strcoll(3)`, `strxfrm(3)` and `strcasecmp(3)`](collation.md) — `tolower` inside `strcasecmp`, and what a locale does to order rather than to class
- [`re_format(7)`, `regex(3)`, `glob(3)` and `fnmatch(3)`](patterns.md) — the bracket expressions the class names live in
- [`ascii(7)`](ascii.md) — the 128 values the octal tables cover
- [`rune(3)`](rune.md) — the locale structure these macros read, under its old name
- [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) — `ß`, `İ` and why one-to-one is the wrong shape
- [Control characters](../../02_Characters/control_characters/README.md) — what `isprint` and `iscntrl` divide between them
- [A character is a number](../../02_Characters/a_character_is_a_number/README.md) — `toascii` as arithmetic on that number
- ["Supports Unicode" is a level, not a yes](../../02_Characters/what_a_regex_matches/README.md) — `[:alpha:]` against `\p{L}`
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) and [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) — the same class names, read by two tools
- [Two people, one account](../../12_Adversarial/collisions_by_design/README.md) — a case fold deciding identity
- [A page has a date](../a_page_has_a_date/README.md) — a 2005 warning about a future that has not arrived
