# `wcwidth(3)` and `wcswidth(3)`: the fifth ruler, with a Unicode version baked in

**Level:** reference · for anyone who has typed `man 3 wcwidth`, seen four possible return values, and wanted to know which one an emoji gets

**One line:** `wcwidth` answers 0, 1, 2 or -1 for one code point from a table that has an edition, so this Mac (Unicode 15.0) calls `U+2FFC` unprintable while glibc 2.39 (Unicode 15.1) gives it two columns and both call every Unicode 16 emoji -1; `wcswidth` of a string with a TAB in it is -1 rather than a sum; and neither the shell's `printf '%-10s'` nor Python's `'{:<10}'` pads by the number either function returns.

**The pages:** [`wcwidth(3)`](raw/macos/wcwidth.3.txt) (macOS, dated August 17, 2004) · [`wcswidth(3)`](raw/macos/wcswidth.3.txt) (macOS, August 20, 2002) · [`wcwidth(3)`](raw/linux/wcwidth.3.txt) (Linux man-pages 6.7, 2023-10-31). Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

Of the five rulers [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) lays along a string (bytes, code units, code points, grapheme clusters, terminal columns) the fifth is the one no language's standard library returns, and `wcwidth` is the C library's attempt at it. It lives in **section 3**, takes one `wchar_t`, and returns how many cells of a fixed-width display that character occupies; `wcswidth` adds it up over a string. `fold(1)`, `column(1)`, `ls` in a narrow window, every curses program and every terminal multiplexer call it to decide where a line wraps and where the cursor is, so it is the function behind the Polish word that wrapped early and the CJK table whose borders do not line up.

The two macOS pages are BSD's, from 2002 and 2004, and say what the functions return. The Linux page is from 2023 and mostly says what you must `#define` to be allowed to call the function. None of the three says where the numbers come from, and that is why the pages are here: the table behind `wcwidth` is a copy of one edition of the Unicode Character Database, the copy differs between the two machines, and the experiment below finds each edition by asking about characters added in successive years. [The table has a version](../../02_Characters/the_table_has_a_version/README.md) is the general rule; this page is the rule inside libc.

## The page, with notes

### `wcwidth(3)` on macOS: four answers, three of them named

```text title="man 3 wcwidth, macOS 26.6.2, dumped 2026-09-13"
     The wcwidth() function returns 0 if the wc argument is a null wide
     character (L'\0'), -1 if wc is not printable; otherwise, it returns the
     number of column positions the character occupies.
```

**0** is named only for `L'\0'`, but it is also the answer for every character that occupies no cell of its own: a combining mark such as `U+0301`, a zero-width joiner, a variation selector, a zero-width space. **1** is a narrow character: `A`, `é`, `ż`, `€`, and a regional-indicator letter on its own. **2** is a wide one: a CJK ideograph, a fullwidth Latin letter, an ideographic space, and every emoji with emoji presentation. **-1**, *not printable*, covers TAB, ESC and DEL on both machines, SOFT HYPHEN on this Mac only, and on both anything the table has never heard of, which is how the table's edition becomes visible from outside. [Control characters](../../02_Characters/control_characters/README.md) is the page for the first group; the last group is the experiment below.

```text title="man 3 wcwidth, macOS 26.6.2, dumped 2026-09-13"
           while ((ch = getwchar()) != WEOF) {
                   w = wcwidth(ch);
                   if (w > 0 && column + w >= 20) {
                           putwchar(L'\n');
                           column = 0;
                   }
                   putwchar(ch);
                   if (ch == L'\n')
                           column = 0;
                   else if (w > 0)
                           column += w;
           }
```

The example is `fold(1)` in twelve lines, and the `w > 0` test is what lets it survive the other two answers: zero-width and unprintable characters are copied through without moving the column. It is worth reading for what it assumes. It assumes the terminal agrees with `wcwidth` about every character, which the family emoji on the ruler page disproves, and it assumes a line may break between any two characters, which [Where a line may break](../../02_Characters/where_a_line_may_break/README.md) disproves: at column 20 it will split an `e` from the `U+0301` that follows it.

### `wcswidth(3)`: a sum, unless

```text title="man 3 wcswidth, macOS 26.6.2, dumped 2026-09-13"
     The wcswidth() function returns 0 if pwcs is an empty string (L""), -1 if
     a non-printing wide character is encountered; otherwise, it returns the
     number of column positions occupied.
```

One unprintable character poisons the whole sum. `wcswidth(L"a\tb", 3)` is -1, not 2, so a caller padding a column must have stripped every control character first or must test the sign, and much code does neither. What it adds up correctly is the point of the ruler page: `café` is 4 whether it is four code points or five with a combining acute, `中文` is 4 for two characters, and `a` ZWJ `b` is 2 for three. The number is neither a byte count nor a code point count, and the last experiment holds all three side by side.

### `wcwidth(3)` on Linux: the feature macro, and the locale

```text title="man 3 wcwidth, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
SYNOPSIS
       #define _XOPEN_SOURCE       /* See feature_test_macros(7) */
       #include <wchar.h>

       int wcwidth(wchar_t c);
       ...
NOTES
       The behavior of wcwidth() depends on the  LC_CTYPE  category  of  the
       current locale.
```

`wcwidth` is in POSIX's XSI option, not in ISO C, so glibc's `<wchar.h>` hides the declaration unless the program asks for it with `_XOPEN_SOURCE`; without it gcc 13 warns *implicit declaration of function* and links anyway, as the experiment shows, while the macOS header declares it unconditionally. The `NOTES` line is the one that matters and it is on the Linux page only: in the C locale `wcwidth(L'é')` is -1 on both machines, because in the C locale `é` is not a character, so a program that never called `setlocale` gets -1 for everything above `0x7F` and wraps nothing correctly. That is [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) as a return value.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| column position | One cell of a fixed-width terminal; the fifth ruler, the one people mean when they ask how long a string is | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| wide character, `wchar_t` | One decoded character as one integer; on glibc always a code point, on this Mac only in a UTF-8 locale | [`multibyte(3)`](multibyte.md) |
| `wint_t`, `WEOF` | `wchar_t` widened so that end-of-file has a value that is not a character; the wide `int` and `EOF` | [`multibyte(3)`](multibyte.md) |
| null wide character `L'\0'` | The wide NUL, width 0 by definition, and the only 0 the page names | [The NUL byte](../../02_Characters/the_nul_byte/README.md) |
| *not printable*, *non-printing* | `iswprint` is false: a control character, or a code point the table does not know | [Control characters](../../02_Characters/control_characters/README.md) |
| combining character | A mark drawn over the previous character and given width 0, so `e` + `U+0301` is one column | [Normalization](../../04_Python/normalization/README.md) |
| East_Asian_Width | The Unicode property the table is built from: `W` wide and `F` fullwidth are 2, `N` narrow and `Na` are 1, `A` ambiguous is a decision the table makes for you | [`uni -h`, line by line](../../11_Tools/uni_help/README.md) |
| fullwidth | The double-cell copies of ASCII at `U+FF01` onward, kept so CJK text lines up | [The CJK pages](cjk_encodings.md) |
| emoji presentation, VS16 | Whether a character is drawn as a coloured picture two cells wide; `U+FE0F` asks for it and has width 0 itself | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| ZERO WIDTH JOINER | `U+200D`, width 0, gluing emoji into one glyph the table cannot see | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| regional indicator | `U+1F1E6` to `U+1F1FF`, width 1 each; a pair is drawn as one flag two cells wide, so the sum is right by coincidence | [Logical and visual order](../../02_Characters/logical_and_visual_order/README.md) |
| `_XOPEN_SOURCE`, XSI | The feature-test macro that unlocks the X/Open extensions in glibc's headers; `wcwidth` is one | [`locale(1)` and `setlocale(3)`](locale.md) |
| `LC_CTYPE` | The locale category the table belongs to; in the C locale nothing above `0x7F` is printable | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `getwchar`, `putwchar` | The wide `getchar` and `putchar`; the decode and encode happen inside them | [`stdio(3)` and the wide stream functions](stdio.md) |
| `fold(1)` | The line-wrapping filter the example reimplements | [Columns and characters](columns_and_characters.md) |
| MT-Safe locale | The Linux page's thread-safety note: safe unless another thread changes the locale meanwhile | |

## Try it on your machine

**Which edition each table is.** Thirty-one code points through `wcwidth` in a UTF-8 locale, chosen so that the last few were added to Unicode in successive years. The C program sets `en_US.UTF-8` on the Mac and `C.UTF-8` on Ubuntu, where `en_US` is not installed.

```text title="Measured 2026-09-13 — macOS 26.6.2 (libSystem, en_US.UTF-8, MB_CUR_MAX=4) and ubuntu:24.04 (glibc 2.39, C.UTF-8, MB_CUR_MAX=6). Not machine-checked."
                                                                            macOS   ubuntu:24.04
  U+00000  NUL                                                                  0              0
  U+00009  TAB                                                                 -1             -1
  U+0001B  ESC                                                                 -1             -1
  U+0007F  DEL                                                                 -1             -1
  U+00041  A                                                                    1              1
  U+000A0  NO-BREAK SPACE                                                       1              1
  U+000AD  SOFT HYPHEN                                                         -1              1
  U+000E9  e-acute                                                              1              1
  U+0017C  z-dot-above                                                          1              1
  U+020AC  EURO SIGN                                                            1              1
  U+00301  COMBINING ACUTE ACCENT                                               0              0
  U+0200B  ZERO WIDTH SPACE                                                     0              0
  U+0200D  ZERO WIDTH JOINER                                                    0              0
  U+0FE0F  VARIATION SELECTOR-16                                                0              0
  U+02764  HEAVY BLACK HEART (text default)                                     1              1
  U+04E2D  CJK ideograph zhong                                                  2              2
  U+0FF21  FULLWIDTH LATIN CAPITAL A                                            2              2
  U+03000  IDEOGRAPHIC SPACE                                                    2              2
  U+0E000  private use                                                          1              1
  U+1F1F5  REGIONAL INDICATOR P   (Unicode 6.0, 2010)                           1              1
  U+1F600  GRINNING FACE          (Unicode 6.1, 2012)                           2              2
  U+1F3FB  EMOJI MODIFIER TYPE-1-2 (Unicode 8.0, 2015)                          2              2
  U+1F97A  FACE WITH PLEADING EYES (Unicode 11.0, 2018)                         2              2
  U+1F6D7  ELEVATOR               (Unicode 13.0, 2020)                          2              2
  U+1FAE0  MELTING FACE           (Unicode 14.0, 2021)                          2              2
  U+1FA77  PINK HEART             (Unicode 15.0, 2022)                          2              2
  U+31350  CJK Extension H start  (Unicode 15.0, 2022)                          2              2
  U+02FFC  IDEOGRAPHIC DESCRIPTION SURROUND FROM RIGHT (Unicode 15.1, 2023)    -1              2
  U+1FAE9  FACE WITH BAGS UNDER EYES (Unicode 16.0, 2024)                      -1             -1
  U+1FADC  ROOT VEGETABLE         (Unicode 16.0, 2024)                         -1             -1
  U+1FBFA  unassigned as of Unicode 16                                         -1             -1
```

Read the bottom five rows as a calendar. Everything through Unicode 15.0 is wide on both machines. `U+2FFC`, added in 15.1 (September 2023), is wide on glibc 2.39 and unprintable on this Mac: the Mac's table stops at 15.0, glibc's at 15.1. Both stop before 16.0 (September 2024), so every emoji from that release is *not printable* to `wcwidth`, and a program using the `fold` loop above will copy it through as if it took no room, on a machine whose terminal draws it two cells wide. One older row differs too: SOFT HYPHEN is -1 here and 1 on glibc, a disagreement about what *printable* means for a character that is invisible until a line breaks at it. This Mac's `python3` (`unicodedata.unidata_version` is 16.0.0) knows the names of both 16.0 characters, and the `uni` tool here is on 17.0; the libc table is the oldest edition on the machine.

**A sum, and its sign.** The same program's `wcswidth` calls, byte-identical on both machines.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04, same locales as above. Byte-identical on both. Not machine-checked."
  wcswidth("caf\u00e9" NFC) =  4   (4 wchar_t)
  wcswidth("cafe\u0301" NFD) =  4   (5 wchar_t)
  wcswidth("\u0141\u00f3d\u017a") =  4   (4 wchar_t)
  wcswidth("\u4e2d\u6587") =  4   (2 wchar_t)
  wcswidth("\U0001F600"  ) =  2   (1 wchar_t)
  wcswidth("a\tb"        ) = -1   (3 wchar_t)
  wcswidth("a\u200db"    ) =  2   (3 wchar_t)
```

`café` composed and decomposed are the same width and different lengths, which is the reason [Normalization](../../04_Python/normalization/README.md) exists; `Łódź` is four columns for seven bytes; two ideographs are four columns for two code points; and the TAB row is the sign test the page's `RETURN VALUES` warns about, one control character turning a width into an error.

**The feature macro.** Compiling the same source on the two machines.

```text title="Measured 2026-09-13 — ubuntu:24.04 (gcc 13.3) and macOS 26.6.2 (Apple clang 21). Not machine-checked."
$ gcc -std=c11 -Wall -Wextra -o m m.c                     (ubuntu, no _XOPEN_SOURCE)
m.c: In function ‘widths’:
m.c:42:65: warning: implicit declaration of function ‘wcswidth’ [-Wimplicit-function-declaration]
m.c: In function ‘main’:
m.c:51:69: warning: implicit declaration of function ‘wcwidth’ [-Wimplicit-function-declaration]
$ gcc -std=c11 -D_XOPEN_SOURCE=700 -Wall -Wextra -o m m.c  (ubuntu: no diagnostics, output identical)
$ cc -std=c11 -Wall -Wextra -o m m.c                      (macOS: no diagnostics)
```

The Linux page's first `SYNOPSIS` line is not decoration. Without it the function is called through an implicit `int wcwidth()` declaration, which happens to work on x86-64 and is an error in C23.

**What pads by what.** `printf '%-10s'` in both shells, `/usr/bin/printf` on both machines, and Python's format, given a four-letter Polish word and a two-character Chinese one.

```text title="Measured 2026-09-13 — macOS 26.6.2 (bash 3.2, BSD printf, LC_ALL=en_US.UTF-8) and ubuntu:24.04 (bash 5.2, GNU coreutils printf, LC_ALL=C.UTF-8). Byte-identical on both. Not machine-checked."
  Łódź is 7 bytes, 4 characters
  中文 is 6 bytes, 2 characters
  builtin printf  [%-10s] -> [Łódź   ]
  /usr/bin/printf [%-10s] -> [Łódź   ]
  builtin printf  [%-10s] -> [中文    ]
  /usr/bin/printf [%-10s] -> [中文    ]
  python  {:<10}     -> [Łódź      ]
  python  {:<10}     -> [中文        ]
```

Count the spaces. `printf` gave `Łódź` three and `中文` four: it padded to ten **bytes**, on four implementations. Python gave them six and eight: it padded to ten **code points**. Neither padded to ten columns, which would be six spaces for both words, and the `中文` line shows why the difference is visible: two code points that are six bytes and four columns cannot be aligned by anything that does not call `wcwidth`. That is the third ruler in a shell that was written for the first, and it is why `column -t` and `ls` line up CJK text and `printf` never will.

## Where the page is dated, and what it does not say

**`wcswidth(3)` is dated August 20, 2002 and `wcwidth(3)` August 17, 2004**, both citing POSIX.1-2001; the Linux page is dated 2023-10-31 and cites POSIX.1-2008. None of the three mentions Unicode, East_Asian_Width, or that there is a table with an edition. The experiment above dates the two tables to Unicode 15.0 and 15.1, on pages that do not know the word.

**No page says what a sequence is worth.** `wcwidth` is per code point and `wcswidth` is a sum, so a family emoji built from four people and three joiners is worth 8 to `wcswidth` and 2 to the terminal that draws it as one glyph. The ruler page lists three defensible answers for that string; libc gives one and does not say it is one of three.

**No page says *ambiguous*.** `é` and `U+0301` are East_Asian_Width `A`, one cell in a Western terminal and two in a legacy East Asian one, and `wcwidth` returns 1 and 0 with no way to say *it depends*. The table decided for you, in favour of the Western answer.

**The two libcs disagree about SOFT HYPHEN**, -1 here and 1 on glibc, and neither page lists which characters count as printable.

**The shell is not on either page.** `printf(1)`'s `%-10s` pads by bytes on both machines, and `printf(3)`'s `%-10s` does the same in C; the width these pages compute is available only to programs that ask for it. [Columns and characters](columns_and_characters.md) is the page for the tools that do.

## See also

- [`multibyte(3)`](multibyte.md) — how a byte string becomes the `wchar_t` these functions take, and why that is locale-dependent
- [`ctype(3)` and `wctype(3)`](ctype.md) — `iswprint`, the function that decides -1
- [`utf8(5)` and `utf-8(7)`](utf8.md) — the Linux page that names `wcswidth` as the column counter and `mbsrtowcs` as the character counter
- [Columns and characters](columns_and_characters.md) — `fold`, `expand`, `cut -c` and `wc -m`, the tools that need this function
- [`tty(4)` and `stty(1)`](tty.md) — the terminal that has its own opinion about width
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) — the five rulers, and the family emoji with three column counts
- [Control characters](../../02_Characters/control_characters/README.md) — the -1 group
- [`uni -h`, line by line](../../11_Tools/uni_help/README.md) — its width column, which prints the East_Asian_Width property the table is built from
- [Logical and visual order](../../02_Characters/logical_and_visual_order/README.md) — the other thing a column count cannot tell you
- [The table has a version](../../02_Characters/the_table_has_a_version/README.md) — why the answer for `U+1FAE9` will change on the next OS update
- [Normalization](../../04_Python/normalization/README.md) — `café` at two lengths and one width
- [A page has a date](../a_page_has_a_date/README.md) — a 2004 page on a 2026 table
