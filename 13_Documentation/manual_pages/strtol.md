# `strtol(3)` and `strtoul(3)`: base 0 reads the prefix, `endptr` reads the rest

**Level:** reference · for anyone who has typed `man 3 strtol`, seen *the special value 0*, and not noticed that a leading zero then means octal

**One line:** With base 0 a leading `0x` means hexadecimal and a leading `0` means octal, so `"010"` is 8; the only portable record of how much was parsed is `endptr`, with `end == input` meaning nothing was; `ERANGE` on overflow is promised while `errno` after a failed parse is `EINVAL` on this Mac and untouched on glibc, exactly as the page's own *not portable* remark warns; `strtoul("-1")` is `ULONG_MAX` with no error; and `"0b101"` is 0 on both libcs unless glibc is compiled as C23, where it is 5.

**The pages:** [`strtol(3)`](raw/macos/strtol.3.txt) and [`strtoul(3)`](raw/macos/strtoul.3.txt) (macOS, both dated November 28, 2001). Ubuntu has both pages; neither was dumped, and the glibc column in the experiments below is behaviour, not documentation. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

Every number that arrives as text goes through this family or a copy of it: `atoi` is `strtol` with the error reporting removed, `sscanf("%d")` calls it, and the shell's `$((...))`, `printf '%d'` and `read` all have to make the same decisions it makes. The pages are in **section 3** and are one page twice, signed and unsigned, with the same three rules: skip white space, take one optional sign, then read digits in a base that is either given or guessed from a prefix. Each page also carries a BSD-only relative (`strtoq`, `strtouq`) that it calls deprecated, and the C99 additions (`strtoll`, `strtoimax`).

A library about character encodings has a page on it because the guess is a decision about what the characters mean, and that decision is the subject of [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md): the same three bytes `0 1 0` are ten, eight or two depending on a parameter that is not in the string. And because the error reporting belongs to the C library rather than the standard, which is finding 16 in [CONTRIBUTING](../../CONTRIBUTING.md) and the reason [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) prints a pointer comparison and never `errno`. This page reproduces that measurement on both machines and adds two more the library did not have.

## The page, with notes

### Base 0: the prefix chooses

```text title="man 3 strtol, macOS 26.6.2, dumped 2026-09-13"
     The string may begin with an arbitrary amount of white space (as
     determined by isspace(3)) followed by a single optional `+' or `-' sign.
     If base is zero or 16, the string may then include a "0x" prefix, and the
     number will be read in base 16; otherwise, a zero base is taken as 10
     (decimal) unless the next character is `0', in which case it is taken as
     8 (octal).
```

One sentence, three bases, and the trap is in the last clause. `0x` is unambiguous; a bare leading `0` is not, because a form field, a zero-padded date and a Unix file mode all start with one for different reasons, and base 0 reads every one of them as octal. `"010"` is 8, `"09"` stops after the `0` because `9` is not an octal digit, and both return without complaint. Python refuses to guess (`int('010', 0)` raises) and Rust has no base-0 mode at all; C is the language where the guess is a library default, which is why the page for it is here. Note also *base 16 may include 0x*: `strtol("0x1A", &e, 16)` is 26, so a hex parser does not have to strip the prefix first. And white space is *as determined by `isspace(3)`*, the narrow function on [`ctype(3)`](ctype.md), so the answer is the locale's, byte by byte.

### `endptr`: the only honest error report

```text title="man 3 strtol, macOS 26.6.2, dumped 2026-09-13"
     If endptr is not NULL, strtol() stores the address of the first invalid
     character in *endptr.  If there were no digits at all, however, strtol()
     stores the original value of str in *endptr.  (Thus, if *str is not `\0'
     but **endptr is `\0' on return, the entire string was valid.)
```

The parenthesis is the whole API. `strtol` is a longest-prefix parser: it reads what it can and returns it, and `"42abc"` is 42 with `*endptr` pointing at the `a`. Three tests fall out of one pointer. `end == input`: nothing was converted, and the 0 you were returned is not a value. `*end == '\0'`: everything was converted. Anything else: a partial parse, and whether that is an error is the caller's decision. The return value alone cannot tell `"0"` from `"zz"`, since both give 0, so every correct use of this function reads `endptr`, and the one in [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) does. One case the page leaves for the experiment: `"0x"` with nothing after it consumes the `0` and stops at the `x`, so it is a successful parse of zero with one character left over, on both machines.

### `RETURN VALUES` and `ERRORS`: which `errno` is promised

```text title="man 3 strtol, macOS 26.6.2, dumped 2026-09-13"
     If no conversion could be performed, 0 is returned and the global
     variable errno is set to EINVAL (the last feature is not portable across
     all platforms).  If an overflow or underflow occurs, errno is set to
     ERANGE and the function return value is clamped according to the
     following table.

           Function         underflow         overflow
           strtol()         LONG_MIN          LONG_MAX
     ...
     [EINVAL]           The value of base is not supported or no conversion
                        could be performed (the last feature is not portable
                        across all platforms).
```

The page says it twice, in brackets, and it is right: `EINVAL` on *no conversion* is this libc's habit, and glibc leaves `errno` alone, at whatever it was, which is 0 if you zeroed it. `ERANGE` with the clamped value is the one promise ISO C makes, and both libcs keep it: `"9223372036854775808"` returns `LONG_MAX` with `ERANGE` on both. The `EINVAL` for an unsupported base is the other half of the bracket, and the experiment below finds a second difference hiding under it. [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) is why the clamp exists: a `long` is 64 bits on both machines, and a twentieth digit does not fit.

### `strtoul(3)`: a minus sign, negated

```text title="man 3 strtoul, macOS 26.6.2, dumped 2026-09-13"
     The strtoul(), strtoull(), strtoumax() and strtouq() functions return
     either the result of the conversion or, if there was a leading minus
     sign, the negation of the result of the conversion, unless the original
     (non-negated) value would overflow; in the latter case, strtoul() returns
     ULONG_MAX, ...  In all cases, errno is
     set to ERANGE.
```

An unsigned parser that accepts a minus sign. `strtoul("-1")` is `ULONG_MAX`, 18446744073709551615, and the *in all cases* refers to the overflow cases only: the experiment shows `errno` staying 0 for `"-1"`, because 1 does not overflow and its negation is taken modulo 2^64. So `"-18446744073709551615"`, the negation of `ULONG_MAX`, parses to 1 without error, and `"-0x10"` under base 0 is 2^64 minus 16. This is two's complement arithmetic doing exactly what [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) says it does, inside a function whose name says *unsigned*. A field that must not be negative has to check for the `-` itself.

### Not on the page: `0b`

C23 (ISO/IEC 9899:2024) adds a binary prefix to this family: with base 0 or 2, `"0b101"` is 5. Neither page mentions it, and the two libcs treat it differently. glibc 2.38 added a second entry point, `__isoc23_strtol`, and its `<stdlib.h>` redirects `strtol` to it when the program is compiled as C23; Apple's libc has no such entry point, so `-std=c23` changes `__STDC_VERSION__` and nothing else. Under C11 on both, `"0b101"` is 0 with the `b` left over, the same shape as `"0x"` above.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| base | The radix, 2 to 36; `A` to `Z` in either case are the digits 10 to 35 | [Counting in hexadecimal](../../01_Bits_and_Bytes/counting_in_hex/README.md) |
| *the special value 0* | Guess the base from the prefix: `0x` hex, `0` octal, otherwise decimal | [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) |
| `0x` prefix | Two characters announcing hexadecimal; accepted under base 0 and base 16, left unread under base 10 | [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) |
| octal | Base 8, the base a leading zero selects, and the base of a `tar` header and a `chmod` argument | [`tar(5)` and `cpio(5)`](archives.md) |
| `endptr`, *first invalid character* | Where parsing stopped; equal to the input when nothing was parsed | [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) |
| `EINVAL` | *Invalid argument*: an unsupported base everywhere, and *no conversion* on this libc only | |
| `ERANGE` | *Result too large*: the value did not fit, the return is clamped; the one `errno` ISO C promises | [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) |
| clamped, `LONG_MIN`, `LONG_MAX`, `ULONG_MAX` | The largest and smallest values of the type, returned on overflow instead of a wrapped number | [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) |
| *negation of the result* | `strtoul` reads `-N` as `2^64 - N`, unsigned arithmetic wrapping on purpose | [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) |
| `isspace(3)` | The narrow white-space test, so *white space* here is whatever the locale's byte table says | [`ctype(3)` and `wctype(3)`](ctype.md) |
| `intmax_t`, `quad_t`, `u_quad_t` | The widest integer C99 promises, and BSD's older 64-bit name for it; `strtoq` is *deprecated* on the page | |
| `restrict` | A C99 promise that `str` and `*endptr` do not alias, so the compiler may reorder | |
| `strtol_l`, `xlocale(3)` | The same function with a locale handle instead of the global one; it changes what `isspace` says | [`locale(1)` and `setlocale(3)`](locale.md) |
| `strtonum(3)`, `compat(5)` | BSD's range-checked replacement, and the page about its legacy symbols; neither exists on Ubuntu | |
| `atoi`, `atol` | `strtol` with `endptr` and `errno` thrown away | [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) |

## Try it on your machine

**The prefix table.** One C program, forty inputs, run on both machines. The rows below are the ones about base and prefix, and they are byte-identical on macOS and glibc; `consumed` is `end - input` against `strlen(input)`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21) and ubuntu:24.04 (glibc 2.39, gcc 13), both -std=c11. Byte-identical on both. Not machine-checked."
  "0x1A"                   base  0  strtol -> 26                    consumed 4/4  end==input:no  errno=0
  "0X1a"                   base  0  strtol -> 26                    consumed 4/4  end==input:no  errno=0
  "010"                    base  0  strtol -> 8                     consumed 3/3  end==input:no  errno=0
  "10"                     base  0  strtol -> 10                    consumed 2/2  end==input:no  errno=0
  "09"                     base  0  strtol -> 0                     consumed 1/2  end==input:no  errno=0
  "0o17"                   base  0  strtol -> 0                     consumed 1/4  end==input:no  errno=0
  "0b101"                  base  0  strtol -> 0                     consumed 1/5  end==input:no  errno=0
  "010"                    base 10  strtol -> 10                    consumed 3/3  end==input:no  errno=0
  "0x1A"                   base 10  strtol -> 0                     consumed 1/4  end==input:no  errno=0
  "0x1A"                   base 16  strtol -> 26                    consumed 4/4  end==input:no  errno=0
  "z"                      base 36  strtol -> 35                    consumed 1/1  end==input:no  errno=0
  "0x"                     base 16  strtol -> 0                     consumed 1/2  end==input:no  errno=0
  "0xG"                    base 16  strtol -> 0                     consumed 1/3  end==input:no  errno=0
  "  42"                   base 10  strtol -> 42                    consumed 4/4  end==input:no  errno=0
  "42abc"                  base 10  strtol -> 42                    consumed 2/5  end==input:no  errno=0
  "1e3"                    base 10  strtol -> 1                     consumed 1/3  end==input:no  errno=0
  "9223372036854775808"    base 10  strtol -> 9223372036854775807   consumed 19/19  end==input:no  errno=ERANGE
  "-9223372036854775809"   base 10  strtol -> -9223372036854775808  consumed 20/20  end==input:no  errno=ERANGE
  "-1"                     base 10  strtoul-> 18446744073709551615  consumed 2/2  end==input:no  errno=0
  "-0x10"                  base  0  strtoul-> 18446744073709551600  consumed 5/5  end==input:no  errno=0
  "-18446744073709551615"  base 10  strtoul-> 1                     consumed 21/21  end==input:no  errno=0
  "18446744073709551616"   base 10  strtoul-> 18446744073709551615  consumed 20/20  end==input:no  errno=ERANGE
```

The rows to stare at: `"09"` and `"0b101"` and `"0o17"` all parse the `0` and stop, returning a valid-looking zero with most of the string unread; `"0x1A"` under base 10 does the same; `"1e3"` is 1, because there are no floats here; `"- 5"` is nothing, because the sign must touch the digits; and `"0x"` is a successful parse of zero. Every one of these is a case where the return value looks like an answer and `endptr` says it is not.

**Where the two libcs differ.** The same run, the rows that were not byte-identical.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04 (glibc 2.39), both -std=c11, errno zeroed before each call. Not machine-checked."
  strtol("+"    base 10) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:yes errno=0
  strtol("- 5"  base 10) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:yes errno=0
  strtol("abc"  base 10) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:yes errno=0
  strtol(""     base 10) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:yes errno=0
  strtol("zz"   base 16) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:yes errno=0
  strtol("é"    base 10) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:yes errno=0
  strtol("1"    base  1) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:no  errno=EINVAL   (glibc left *endptr untouched)
  strtol("1"    base 37) -> 0    macOS: end==input:yes errno=EINVAL   glibc: end==input:no  errno=EINVAL   (glibc left *endptr untouched)
```

Finding 16, reproduced: six inputs that convert nothing, `EINVAL` here and `0` there, and `end == input` on both, which is why the pointer is the test and `errno` is not. The last two rows are the addition. For an unsupported base both libcs return 0 with `EINVAL`, as the page says, but glibc returns before writing `*endptr` at all; the program had initialised `end` to `NULL` and it stayed `NULL`. A caller that checks `end == input` after passing a bad base reads whatever was in the variable, which on the Mac is the input and on glibc is uninitialised memory.

**`0b` under four compilers.** The one row that depends on the language standard the program was compiled as, and the symbol each binary linked.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21) and ubuntu:24.04 (gcc 13.3, glibc 2.39). Not machine-checked."
  macOS  cc -std=c11   __STDC_VERSION__=201112  strtol("0b101", base 0) -> 0  consumed 1/5
  macOS  cc -std=c23   __STDC_VERSION__=202311  strtol("0b101", base 0) -> 0  consumed 1/5
  glibc  gcc -std=c11  __STDC_VERSION__=201112  strtol("0b101", base 0) -> 0  consumed 1/5
  glibc  gcc -std=c2x  __STDC_VERSION__=202000  strtol("0b101", base 0) -> 5  consumed 5/5

$ nm -u m11 | grep strto                (glibc, -std=c11)          $ nm -u m_strtol | grep strto      (macOS, either -std)
                 U strtol@GLIBC_2.2.5                                _strtol
                 U strtoul@GLIBC_2.2.5                                _strtoul
$ nm -u m2x | grep strto                (glibc, -std=c2x)
                 U __isoc23_strtol@GLIBC_2.38
                 U __isoc23_strtoul@GLIBC_2.38
```

Same source, same libc, two answers, chosen by a compiler flag: glibc's header renames the call to `__isoc23_strtol`, a function that did not exist before glibc 2.38, and the C11 binary keeps the old one. On the Mac there is only `_strtol` and it has never heard of `0b`. A program that parses `"0b101"` is therefore not portable across compiler flags, let alone platforms, and the safe reading is still the C11 one: 0, with four characters left.

**What Python does with the same strings.** The comparison the base page draws, run today.

```text title="Measured 2026-09-13 — macOS 26.6.2, python3 3.14.7. Not machine-checked."
  int('0x1A'      ,  0) -> 26
  int('010'       ,  0) -> ValueError: invalid literal for int() with base 0: '010'
  int('010'       , 10) -> 10
  int('0b101'     ,  0) -> 5
  int('0x'        , 16) -> ValueError: invalid literal for int() with base 16: '0x'
  int('42abc'     , 10) -> ValueError: invalid literal for int() with base 10: '42abc'
  int('-1'        , 10) -> -1
  int('١٢'        , 10) -> 12
```

Four differences in eight lines. Python's base 0 refuses the octal guess, accepts `0b`, and rejects `"0x"` and `"42abc"` outright, because `int()` is all-or-nothing where `strtol` is longest-prefix. And the last line: `int()` reads Arabic-Indic digits as digits, while `strtol` on the same four bytes converts nothing on both machines, because *digit* in C means the ASCII ten. [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) has the Python side; the C side is every row above.

## Where the page is dated, and what it does not say

**Both pages are dated November 28, 2001** and cite C90 and C99. C23's binary prefix is not on them, and on this Mac not in the library either; the page is correct about the machine and silent about the standard that changed under it.

**The *not portable* bracket is exactly right, and the page does not say which way.** It cannot: the other platform's behaviour is not this page's business. The measurement above supplies it, and the rule that follows, test `endptr` and read `errno` only for `ERANGE`, is finding 16 in [CONTRIBUTING](../../CONTRIBUTING.md).

**Nothing says what `*endptr` holds after an unsupported base.** The page lists `EINVAL` for it and moves on; glibc does not write the pointer at all.

**Nothing says which characters are digits.** *Valid digit in the given base* means ASCII `0` to `9` and `A` to `Z`; a string of Arabic-Indic or fullwidth digits converts nothing, silently, on both machines. That is the difference between a byte table and a Unicode property, and [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) measures `int()` making the opposite choice.

**`strtonum(3)`, the page's own recommended replacement, is BSD-only.** `man 3 strtonum` finds it here and nothing on Ubuntu; the portable range check is still `endptr` plus `ERANGE`.

## See also

- [`printf(1)` and `printf(3)`](printf.md) — the other direction: `%x`, `%o` and `%d` turning a number back into these prefixes
- [`byteorder(3)`](byteorder.md) — what happens to the number once it is bytes
- [`tar(5)` and `cpio(5)`](archives.md) — octal in the wild: file sizes and modes stored as ASCII digits in a header
- [`ctype(3)` and `wctype(3)`](ctype.md) — `isspace(3)`, which decides what the leading white space is
- [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) — the octal-by-leading-zero rule, in six languages
- [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) — the `endptr` idiom as the library's C example, and finding 16's first measurement
- [Arithmetic has its own width](../../01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) — why `-1` is `ULONG_MAX` and why the overflow clamps
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — `int(s, 0)` and `int(s, 16)`, the Python side of the table above
- [Counting in hexadecimal](../../01_Bits_and_Bytes/counting_in_hex/README.md) — why `z` is 35
- [What the page does not say](../what_the_page_does_not_say/README.md) — the general rule for the gaps above
