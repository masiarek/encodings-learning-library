# `multibyte(3)`: the hub page for every conversion function in libc

**Level:** reference · for anyone who has seen `mbrtowc` in a stack trace or `MB_CUR_MAX` in a header and wanted to know what family they belong to

**One line:** One screen of text defines the two representations C has for text, wide characters in memory and multibyte characters on the wire, hands you a ten-function table for moving between them, and states the contract every command-line tool on the machine inherits: `LC_CTYPE` decides what a character is, so `setlocale` changes the meaning of every function on the page.

**The pages:** [`multibyte(3)`](raw/macos/multibyte.3.txt) (macOS, dated April 8, 2004) · [`mbrtowc(3)`](raw/macos/mbrtowc.3.txt) · [`wcrtomb(3)`](raw/macos/wcrtomb.3.txt) · [`mbsrtowcs(3)`](raw/macos/mbsrtowcs.3.txt) · [`wcsrtombs(3)`](raw/macos/wcsrtombs.3.txt) · [`mbstowcs(3)`](raw/macos/mbstowcs.3.txt) · [`wcstombs(3)`](raw/macos/wcstombs.3.txt) · [`mblen(3)`](raw/macos/mblen.3.txt) · [`mbrlen(3)`](raw/macos/mbrlen.3.txt) · [`mbtowc(3)`](raw/macos/mbtowc.3.txt) · [`wctomb(3)`](raw/macos/wctomb.3.txt) · [`btowc(3)`](raw/macos/btowc.3.txt) (one page for `btowc` and `wctob`, dumped under [both names](raw/macos/wctob.3.txt)) · [`mbsinit(3)`](raw/macos/mbsinit.3.txt) · and Linux's [`mbrtowc(3)`](raw/linux/mbrtowc.3.txt) for comparison. Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

C89 had `char` and nothing else, and a `char` is a byte. The 1994 amendment to the standard added a second representation, `wchar_t`, and a set of functions for converting between the two; C99 added the *restartable* versions, the ones with an `r` in the name and an `mbstate_t` argument. FreeBSD 5 got a complete implementation in 2002 to 2004, and the copyright line on nearly every page in this family is Tim J. Robbins', who wrote both the code and the manual for it. macOS inherited the lot. These are the functions that every program on the machine calls when it has to answer *how many characters are in this byte string*, which is to say they are the mechanism behind every bytes-or-characters question in [11_Tools](../../11_Tools/README.md).

`multibyte(3)` is the hub: it has no function of its own, it defines the vocabulary and lists the ten functions. The lesson [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) already tabulates them by *restartable or not*. This page explains the words on the hub and then goes through the individual pages, because the return-value conventions on `mbrtowc(3)` are where the real information is, and finishes with an experiment that turns up the one fact none of the pages states: on this Mac, a `wchar_t` is not necessarily a Unicode code point.

## The page, with notes

### `multibyte(3)`: two representations and one rule

```text title="man 3 multibyte, macOS 26.6.2, dumped 2026-09-13"
     The basic elements of some written natural languages, such as Chinese,
     cannot be represented uniquely with single C chars.  The C standard
     supports two different ways of dealing with extended natural language
     encodings: wide characters and multibyte characters.  Wide characters are
     an internal representation which allows each basic element to map to a
     single object of type wchar_t.  Multibyte characters are used for input
     and output and code each basic element as a sequence of C chars.
     Individual basic elements may map into one or more (up to MB_LEN_MAX)
     bytes in a multibyte character.
```

*Basic element* is the page's careful phrase for what the rest of us call a character, and it is careful on purpose: it does not say code point, because in 1994 there was no promise that a `wchar_t` held one. A **wide character** is one basic element in one integer, sized so that every element of every locale fits. A **multibyte character** is the same element as a run of one or more bytes, which is what a file or a pipe carries. The whole family is the two verbs of [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md): multibyte to wide is decode, wide to multibyte is encode, and the table the verbs run under is named by the locale.

```text title="man 3 multibyte, macOS 26.6.2, dumped 2026-09-13"
     The current locale (setlocale(3)) governs the interpretation of wide and
     multibyte characters.  The locale category LC_CTYPE specifically controls
     this interpretation.  The wchar_t type is wide enough to hold the largest
     value in the wide character representations for all locales.
```

This is the contract. None of the ten functions takes an encoding argument; the encoding is whatever `LC_CTYPE` currently names, and a program that never calls `setlocale` is in the `"C"` locale whatever the shell's `LANG` says. It is why `grep`, `wc -m`, `cut -c` and the shell's `${#var}` all change their answers with the environment, which is the finding of [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) stated as an API rule. And *wide enough for all locales* is a statement about size, not meaning: four bytes on both machines measured below, holding different things.

```text title="man 3 multibyte, macOS 26.6.2, dumped 2026-09-13"
     Multibyte strings may contain `shift' indicators to switch to and from
     particular modes within the given representation.  If explicit bytes are
     used to signal shifting, these are not recognized as separate characters
     but are lumped with a neighboring character.  There is always a
     distinguished `initial' shift state.  Some functions (e.g., mblen(3),
     mbtowc(3) and wctomb(3)) maintain static shift state internally, whereas
     others store it in an mbstate_t object passed by the caller.  Shift
     states are undefined after a call to setlocale(3) with the LC_CTYPE or
     LC_ALL categories.
```

A **shift state** exists because some encodings, ISO 2022 and its relatives, have bytes that mean *the following bytes are in a different set until further notice* rather than a character. UTF-8 has none; every byte says what it is. But the API was designed for the encodings that do, so it carries a state object everywhere, and the state is what makes a function *restartable*: hand `mbrtowc` half a character now and the other half later, with the same `mbstate_t`, and it completes the character. The functions without an `r` keep that state in a static variable inside libc, which is why they cannot be used from two threads or on two streams at once, and why the page names them first when it warns you. The last sentence is the one to remember: change the locale and every state you hold is garbage.

```text title="man 3 multibyte, macOS 26.6.2, dumped 2026-09-13"
     For convenience in processing, the wide character with value 0 (the null
     wide character) is recognized as the wide character string terminator,
     and the character with value 0 (the null byte) is recognized as the
     multibyte character string terminator.  Null bytes are not permitted
     within multibyte characters.
```

Two terminators, one per representation, and a promise that makes C strings possible at all under UTF-8: no byte of any multibyte character is ever `00`. [The NUL byte](../../02_Characters/the_nul_byte/README.md) is that sentence's consequences.

The function table that follows is the one the lesson page already reproduces. Read by question rather than by name it is:

| The question | Non-restartable (static state) | Restartable (`mbstate_t` you own) |
|---|---|---|
| How many bytes is the next character? | `mblen` | `mbrlen` |
| Decode one character | `mbtowc` | `mbrtowc` |
| Decode a whole string | `mbstowcs` | `mbsrtowcs` |
| Encode one character | `wctomb` | `wcrtomb` |
| Encode a whole string | `wcstombs` | `wcsrtombs` |

Use the right-hand column. The left-hand column exists because C89 had it.

### `mbrtowc(3)`: four return values, and the two that are not lengths

```text title="man 3 mbrtowc, macOS 26.6.2, dumped 2026-09-13"
     0       The next n or fewer bytes represent the null wide character
             (L'\0').

     >0      The next n or fewer bytes represent a valid character, mbrtowc()
             returns the number of bytes used to complete the multibyte
             character.

     (size_t)-2
             The next n contribute to, but do not complete, a valid multibyte
             character sequence, and all n bytes have been processed.

     (size_t)-1
             An encoding error has occurred.  The next n or fewer bytes do not
             contribute to a valid multibyte character.
```

This is the most information-dense passage in the family, and everything a decoder can say is in it. A positive number is a length, and it is the answer to *where does the next character start*. Zero is a length too, of the terminator. The two negative values are the two ways bytes can fail to be a character, and the whole of [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) turns on keeping them apart: `(size_t)-2` means *not yet*, the bytes so far are a legal prefix and the caller should fetch more, which is how a decoder reads a character that straddles two buffers; `(size_t)-1` means *never*, no continuation can rescue these bytes, and `errno` is `EILSEQ`, *illegal byte sequence*, the same word `iconv` prints. Python's `UnicodeDecodeError` is the second one; its `codecs` incremental decoder's buffered tail is the first.

Two conventions higher up the page matter too. *If `ps` is `NULL`, `mbrtowc()` uses an internal, static `mbstate_t` object*: pass `NULL` and the restartable function quietly becomes the non-restartable one. And *if `s` is `NULL`, `mbrtowc()` behaves as if `pwc` were `NULL`, `s` were an empty string, and `n` were 1*: that call converts nothing and resets the state to initial, which is the idiom for starting over.

### `wcrtomb(3)`: the other direction fails differently

```text title="man 3 wcrtomb, macOS 26.6.2, dumped 2026-09-13"
     The wcrtomb() function stores a multibyte sequence representing the wide
     character wc, including any necessary shift sequences, to the character
     array s.  A maximum of MB_CUR_MAX bytes will be stored.
     ...
     The wcrtomb() functions returns the length (in bytes) of the multibyte
     sequence needed to represent wc, or (size_t)-1 if wc is not a valid wide
     character code.
```

Encoding has one failure, not two: a wide character either has a spelling in this locale's encoding or it does not, and there is no *not yet*. `MB_CUR_MAX` is the buffer size to allocate and it is a property of the *current* locale, which is why on this Mac it is a function call in disguise; `MB_LEN_MAX` in `<limits.h>` is the compile-time ceiling over all locales. The experiment below prints both on both machines, and they differ on both. *Not a valid wide character code* is Python's `UnicodeEncodeError` under `errors='strict'`, the subject of [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md): under the `C` locale a `ż` has no bytes, and the function says so with `EILSEQ`.

### `mbsrtowcs(3)` and `wcsrtombs(3)`: whole strings, and where they stopped

```text title="man 3 mbsrtowcs, macOS 26.6.2, dumped 2026-09-13"
     If dst is NULL, no characters are stored.

     If dst is not NULL, the pointer pointed to by src is updated to point to
     the character after the one that conversion stopped at.  If conversion
     stops because a null character is encountered, *src is set to NULL.
```

The string versions take `src` as a pointer *to* a pointer for one reason: to tell you where they stopped, whether because the output filled, because the input ended, or because a byte was illegal. That is the same information `iconv(3)` returns through its four in-out pointers, and it is what lets a caller resume. The `dst == NULL` form converts nothing and counts, which is how you size the output buffer, and it is the C spelling of `len(s.decode())`. `mbsnrtowcs`, with a byte limit, is a BSD extension the page marks as such.

### `mblen(3)`, `mbtowc(3)`, `wctomb(3)`: the C89 trio

```text title="man 3 mblen, macOS 26.6.2, dumped 2026-09-13"
     A call with a null s pointer returns nonzero if the current locale
     requires shift states, zero otherwise.  If shift states are required, the
     shift state is reset to the initial state.
```

These three keep their state inside libc, return `int` rather than `size_t`, and fold the two failures of `mbrtowc` into one `-1`. The `NULL` call is a question: *does this locale's encoding have shift states at all?* Measured below, the answer is 0 in every locale installed on either machine; the stateful encodings the API was built for are not in `locale -a` on a 2026 Mac or a stock Ubuntu.

### `btowc(3)` and `wctob(3)`: the single-byte shortcut

```text title="man 3 btowc, macOS 26.6.2, dumped 2026-09-13"
     The btowc() function converts a single-byte character into a
     corresponding wide character.  If the character is EOF or not valid in
     the initial shift state, btowc() returns WEOF.

     The wctob() function converts a wide character into a corresponding
     single-byte character.  If the wide character is WEOF or not able to be
     represented as a single byte in the initial shift state, wctob() returns
     WEOF.
```

The narrow ↔ wide conversion for the case where a character *is* one byte, which under UTF-8 means ASCII and nothing else: `wctob(L'é')` is `WEOF` in a UTF-8 locale because `é` is two bytes. `WEOF` is `EOF`'s wide twin, a `wint_t` value outside the range of any character, and the two functions are how `<ctype.h>` and `<wctype.h>` agree with each other, which is [`ctype(3)`](ctype.md)'s subject. The page's `LEGACY SYNOPSIS` line, *the include file `<stdio.h>` is not necessary*, is Apple's way of saying an older prototype needed it.

### `mbsinit(3)`: is the state clean

One function, one question: is this `mbstate_t` in the initial state, or is it holding half a character? The experiment below asks it after feeding `mbrtowc` a lone lead byte, and it says no.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| wide character, `wchar_t` | One character in one integer, four bytes on both machines here. On glibc always a Unicode scalar value; on macOS whatever the locale's encoding numbers it | [`utf8(5)` and `utf-8(7)`](utf8.md) |
| multibyte character | One character as a run of one to `MB_CUR_MAX` bytes in the locale's encoding, which is what a file holds | [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) |
| *basic element* | The page's word for a character, chosen to avoid promising a code point | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| `MB_LEN_MAX` | The most bytes any character takes in any locale, fixed at compile time in `<limits.h>`: 6 on macOS, 16 on glibc | |
| `MB_CUR_MAX` | The most bytes any character takes in the *current* locale: 1 under `C`, 4 (macOS) or 6 (glibc) under UTF-8, 3 under EUC-JP | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `LC_CTYPE` | The locale category that names the encoding and so gives every function on the page its meaning | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| shift state, initial shift state | Memory of a mode switch inside a stateful encoding such as ISO 2022; every encoding has an *initial* state and UTF-8 never leaves it | [Code pages](../../02_Characters/code_pages/README.md) |
| `mbstate_t` | The opaque object holding a shift state and any partial character; zero it to mean *initial* | |
| restartable | A function that keeps its state in an `mbstate_t` you pass, so it can be resumed mid-character and used on two streams at once | [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) |
| *internal, static `mbstate_t`* | The one hidden state the non-restartable functions share; not thread-safe, and what a `NULL` state argument selects | |
| `(size_t)-1`, `EILSEQ` | *Illegal byte sequence*: the bytes can never become a character. Python's `UnicodeDecodeError`, `iconv`'s *Illegal byte sequence* | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `(size_t)-2` | An incomplete character: a legal prefix that needs more bytes. The value that makes streaming decoders possible | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `EINVAL` | The conversion state is invalid, usually because the locale changed underneath it | |
| null wide character, null byte | `L'\0'` and `'\0'`, the terminators of the two string kinds; no multibyte character contains a `00` | [The NUL byte](../../02_Characters/the_nul_byte/README.md) |
| `restrict` | A C99 promise that two pointer arguments do not overlap, so the function may read and write without re-checking | |
| `_l` suffix, `locale_t` | Apple's per-call locale variants, so a library can decode under a locale without touching the process-wide one | [`locale(1)` and `setlocale(3)`](locale.md) |
| `wint_t`, `WEOF` | An integer wide enough for any `wchar_t` plus one extra value, `WEOF`, that means *no character* | [`ctype(3)`](ctype.md) |
| ISO/IEC 9899:1999, C99 | The standard these functions conform to; the restartable ones are its addition | |
| `mklocale(1)` | Named in `SEE ALSO`; the locale compiler that turned an `ENCODING` line into `LC_CTYPE`, not shipped on this Mac | [`utf8(5)` and `utf-8(7)`](utf8.md) |

## Try it on your machine

**The probe.** One C program, run under each locale the machine has. It prints the three sizes, then asks `mbrtowc` about seven byte strings with a fresh state each time, then asks `wcrtomb` to spell `ż` and `mblen` whether the encoding shifts.

```c title="mb.c — cc -std=c11 -Wall -Wextra -o mb mb.c && ./mb C && ./mb en_US.UTF-8"
#include <errno.h>
#include <limits.h>
#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

static void probe(const char *label, const char *s, size_t n) {
    mbstate_t st; memset(&st, 0, sizeof st);
    wchar_t wc = 0; errno = 0;
    size_t r = mbrtowc(&wc, s, n, &st);
    if (r == (size_t)-1)      printf("  %-26s -> (size_t)-1   errno=%s\n", label, errno == EILSEQ ? "EILSEQ" : "other");
    else if (r == (size_t)-2) printf("  %-26s -> (size_t)-2   incomplete, mbsinit()=%d\n", label, mbsinit(&st) != 0);
    else                      printf("  %-26s -> %zu            wc=U+%04X\n", label, r, (unsigned)wc);
}

int main(int argc, char **argv) {
    const char *want = argc > 1 ? argv[1] : "";
    const char *got = setlocale(LC_CTYPE, want);
    printf("setlocale(LC_CTYPE, \"%s\") -> %s\n", want, got ? got : "NULL (not installed)");
    printf("  MB_CUR_MAX=%d  MB_LEN_MAX=%d  sizeof(wchar_t)=%zu", (int)MB_CUR_MAX, MB_LEN_MAX, sizeof(wchar_t));
#ifdef __STDC_ISO_10646__
    printf("  __STDC_ISO_10646__=%ldL (wchar_t is always a Unicode scalar)\n", (long)__STDC_ISO_10646__);
#else
    printf("  __STDC_ISO_10646__ not defined (wchar_t is whatever the locale says)\n");
#endif
    printf("  mbrtowc(&wc, s, n, &state):\n");
    probe("41            'A'",         "A", 1);
    probe("c3 a9         e-acute",     "\xc3\xa9", 2);
    probe("c3            (n=1, cut)",  "\xc3", 1);
    probe("a9            stray trail", "\xa9", 1);
    probe("c0 80         overlong NUL","\xc0\x80", 2);
    probe("f0 9f 98 80   U+1F600",     "\xf0\x9f\x98\x80", 4);
    probe("00            NUL",         "", 1);
    char buf[MB_LEN_MAX]; mbstate_t st; memset(&st, 0, sizeof st); errno = 0;
    size_t k = wcrtomb(buf, (wchar_t)0x17C, &st);
    if (k == (size_t)-1) printf("  wcrtomb(U+017C z-dot)      -> (size_t)-1   errno=%s\n", errno == EILSEQ ? "EILSEQ" : "other");
    else { printf("  wcrtomb(U+017C z-dot)      -> %zu byte(s):", k); for (size_t i = 0; i < k; i++) printf(" %02x", (unsigned char)buf[i]); printf("\n"); }
    printf("  mblen(NULL, 0) (\"does this encoding have shift states?\") -> %d\n", mblen(NULL, 0));
    return 0;
}
```

**Under a UTF-8 locale the two libraries agree on every byte string** and differ on two constants.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21, en_US.UTF-8) and ubuntu:24.04 (gcc 13.3, glibc 2.39, C.UTF-8). Not machine-checked."
                                              macOS                                   ubuntu:24.04
  MB_CUR_MAX / MB_LEN_MAX / sizeof(wchar_t)   4 / 6 / 4                               6 / 16 / 4
  __STDC_ISO_10646__                          not defined                             201706L
  41            'A'                           1            wc=U+0041                  same
  c3 a9         e-acute                       2            wc=U+00E9                  same
  c3            (n=1, cut)                    (size_t)-2   incomplete, mbsinit()=0    same
  a9            stray trail                   (size_t)-1   errno=EILSEQ               same
  c0 80         overlong NUL                  (size_t)-1   errno=EILSEQ               same
  f0 9f 98 80   U+1F600                       4            wc=U+1F600                 same
  00            NUL                           0            wc=U+0000                  same
  wcrtomb(U+017C z-dot)                       2 byte(s): c5 bc                        same
  mblen(NULL, 0)                              0                                       0
```

Row three is `(size_t)-2` in action: one byte of a two-byte character, a legal prefix, and `mbsinit` confirms the state is now holding it. Row four is the same byte's partner arriving alone, which no prefix can precede, so `(size_t)-1`. Row five is the shortest-form rule from [`utf8(5)`](utf8.md) enforced by the decoder. `MB_CUR_MAX` is 4 on macOS and 6 on glibc for the same encoding: macOS's UTF-8 stops at four bytes, and glibc's constant still describes the [six-byte table](utf8.md). `MB_LEN_MAX` is 6 against 16, so a buffer sized by one platform's header is not sized for the other's.

**Under the `C` locale they disagree about what a byte is.**

```text title="Measured 2026-09-13 — the same program under LC_CTYPE=C. Not machine-checked."
                                              macOS                                   ubuntu:24.04
  MB_CUR_MAX                                  1                                       1
  c3 a9         e-acute                       1            wc=U+00C3                  (size_t)-1   errno=EILSEQ
  a9            stray trail                   1            wc=U+00A9                  (size_t)-1   errno=EILSEQ
  f0 9f 98 80   U+1F600                       1            wc=U+00F0                  (size_t)-1   errno=EILSEQ
  wcrtomb(U+017C z-dot)                       (size_t)-1   errno=EILSEQ               (size_t)-1   errno=EILSEQ
```

The BSD `C` locale maps every byte to the wide character of the same number, so `c3` is `U+00C3` and nothing is ever illegal on the way in. The glibc `C` locale is seven-bit: any byte above `0x7f` is an encoding error. So a program that decodes under `C` never fails on a Mac and fails on the first accented letter on Linux, and both are conforming. Neither man page says which its library does. This is the C-library layer of the `LC_ALL=C` advice in [11_Tools](../../11_Tools/README.md): under `C`, macOS tools see 256 one-byte characters and GNU tools see 128 characters and 128 errors, which is one reason [BSD `grep` and GNU `grep`](../../11_Tools/grep/README.md) part company on undecodable lines.

**Under a Japanese locale, `wchar_t` is not a code point on macOS.**

```text title="Measured 2026-09-13 — macOS 26.6.2 only; ubuntu:24.04 has no such locale installed. Not machine-checked."
setlocale(LC_CTYPE, "ja_JP.eucJP") -> ja_JP.eucJP
  MB_CUR_MAX=3  MB_LEN_MAX=6  sizeof(wchar_t)=4  __STDC_ISO_10646__ not defined
  c3 a9         e-acute      -> 2            wc=U+C3A9
  c0 80         overlong NUL -> 2            wc=U+C080
  wcrtomb(U+017C z-dot)      -> (size_t)-1   errno=EILSEQ

setlocale(LC_CTYPE, "ja_JP.SJIS") -> ja_JP.SJIS
  MB_CUR_MAX=2
  wcrtomb(U+017C z-dot)      -> 2 byte(s): 01 7c
```

Under EUC-JP the bytes `c3 a9` are a valid two-byte character, and the `wchar_t` that comes back is `0xC3A9`, the EUC code itself packed into an integer, not the Unicode number of the kanji it denotes. `unicode(7)` on Linux promises the opposite, *its values are always interpreted by the C library as UCS code values (in all locales)*, and the macro `__STDC_ISO_10646__` is how a program can tell which promise it has. On this Mac the macro is absent and the promise is not made, so `wchar_t` is an encoding-specific number and comparing one with `L'é'` is only meaningful in a UTF-8 locale. Under Shift-JIS the last line is the same fact from the other side: `0x017C` is not a code point to this locale but a two-byte code, and `wcrtomb` writes its two bytes without complaint.

**The same functions at the shell.** `wc -m` and `grep -o .` call these functions; `wc -c` does not.

```text title="Measured 2026-09-13 — printf 'café\n' into a file (6 bytes). macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
                          wc -c   wc -m   grep -o . | wc -l
  LC_ALL=C                6       6       5             both platforms
  LC_ALL=<UTF-8 locale>   6       5       4             both platforms (en_US.UTF-8 on the Mac, C.UTF-8 on Ubuntu)
```

`wc -m` is `mbrtowc` in a loop; `grep -o .` is the same loop stopping before the newline. And on Ubuntu, `LC_ALL=en_US.UTF-8` gave the `C` column, because that locale is not installed there and the tools fell back silently: `setlocale` returned `NULL`, as the probe's first line shows, and `wc` carried on in `C`. Python raises instead, which is why [finding 31 in CONTRIBUTING](../../CONTRIBUTING.md) forbids an example from asking for a human locale at all.

## Where the page is dated, and what it does not say

**`multibyte(3)` is dated April 8, 2004** and conforms to C99. C11 added a third representation, `char16_t` and `char32_t` in `<uchar.h>`, with `mbrtoc16`, `mbrtoc32`, `c16rtomb` and `c32rtomb`, which fix the encoding of the wide side to UTF-16 and UTF-32 and so make the `wchar_t` problem above go away. There is no man page for any of them on either machine (`man -w 3 mbrtoc32` fails on both), and this Mac's SDK has no `<uchar.h>` at all.

**No page in the family says what a `wchar_t` holds.** The hub says it is wide enough; glibc's `unicode(7)` says on Linux it is always a code point; nothing on the Mac says it is not. The EUC-JP measurement is the only place that fact appears.

**No page says what the `C` locale's encoding is.** POSIX leaves it to the implementation, and the two implementations chose opposite answers for bytes above `0x7f`.

**`mbrtowc(3)` on Linux is longer** and worth reading beside the BSD one: it spells out the `s == NULL` reset idiom and the `n == 0` case, and its `ATTRIBUTES` table says which functions are thread-safe with a `NULL` state (none of them). It is in [`raw/linux/mbrtowc.3.txt`](raw/linux/mbrtowc.3.txt).

**None of the pages mention `U+FFFD`.** The API offers refuse (`-1`) and wait (`-2`) and nothing else; replacing a bad byte with a marker is a policy the caller writes, which is what Python's `errors='replace'` and Rust's `from_utf8_lossy` are.

## See also

- [`utf8(5)` and `utf-8(7)`](utf8.md) — the table these functions decode, and the six-byte constant glibc still carries
- [`ctype(3)`](ctype.md) — the classification and case functions that take the `wchar_t` these produce
- [`wcwidth(3)`](wcwidth.md) — the one thing a wide character knows that a byte string cannot: how many columns it takes
- [`locale(1)` and `setlocale(3)`](locale.md) — the call that gives every function here its meaning, and the `_l` variants that bypass it
- [`iconv(1)` and `iconv(3)`](iconv.md) — the other conversion API, which names both tables instead of asking the locale
- [`mbrune(3)` and `rune(3)`](rune.md) — the 4.4BSD API this family replaced
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) — the function table by restartability, and `LC_CTYPE` as the contract
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — where the `-1` and `-2` go in a real program
- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — the environment variables that pick the table
- [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) — these functions, one tool up, and what the two libcs' `C` locales do to it
