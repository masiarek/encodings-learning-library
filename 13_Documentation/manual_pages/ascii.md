# `ascii(7)`: the same 128 numbers, three ways on the Mac and one way on Linux

**Level:** reference · for anyone who has typed `man ascii` to look up a code and wondered why the two machines print it so differently

**One line:** Both machines ship a page that is nothing but the ASCII table, the BSD one from 1993 printed three times over in octal, hex and decimal, the Linux one from 2024 printed once with the control names and the C escapes beside them, and the Mac also ships the table as a data file, so one `grep` of `/usr/share/misc/ascii` answers *where is the backslash* in all three bases at once.

**The pages:** [`ascii(7)`](raw/macos/ascii.7.txt) (macOS, dated June 5, 1993; copyright 1989, 1990, 1993) · [`ascii(7)`](raw/linux/ascii.7.txt) (Linux man-pages 6.7, 2024-01-28; copyright Michael Haardt 1993) · `/usr/share/misc/ascii` is the data file the BSD page's `FILES` section names, 50 lines, 3,170 bytes, on the Mac only. Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

This is the one encoding page both machines have under the same name in the same section, and it is not documentation of a program or a file but of an *agreement*: that the number 65 means `A`. It is in section 7, miscellany, because there is nothing else to file it under, and it exists so that a person at a terminal can answer *what is `0x1B`* or *what number is `~`* without leaving the terminal. That is a real need. Every hex dump on [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) is read against this table, and every claim on [A character is a number](../../02_Characters/a_character_is_a_number/README.md) is a claim about one of its rows.

The two pages are the same table with different ideas about what a lookup table is. The BSD page, written in 1989 and last touched in 1993, prints the whole set three times, once per base, with the control characters as lowercase two- and three-letter names, and points at a data file that is the same thing in `grep`-able form. The Linux page, from 1993 and revised in 2024, prints the set once with all three bases on every row, spells the control names out in full with the C escape that produces each, adds two compact tables for finding a code by eye, and ends with three notes of history, one of which is where the Mac's data file comes from: *`/etc/ascii` (VII) appears in the UNIX Programmer's Manual*. Seventh Edition Unix shipped the table as a file in 1979; the Mac still does, one directory over.

Neither page says a word about bytes above `0x7F`, because ASCII has none. The Linux page says so in its second sentence, *It is a 7-bit code*, and points at the fifteen `iso_8859-*(7)` pages for what the eighth bit was used for: [`charsets(7)` and the code-page pages](charsets.md).

## The page, with notes

### `ascii(7)` on the Mac: three sets

```text title="man 7 ascii, macOS 26.6.2, dumped 2026-09-13"
     The octal set:

     000 nul  001 soh  002 stx  003 etx  004 eot  005 enq  006 ack  007 bel
     010 bs   011 ht   012 nl   013 vt   014 np   015 cr   016 so   017 si
     020 dle  021 dc1  022 dc2  023 dc3  024 dc4  025 nak  026 syn  027 etb
     030 can  031 em   032 sub  033 esc  034 fs   035 gs   036 rs   037 us
     040 sp   041  !   042  "   043  #   044  $   045  %   046  &   047  '
     ...
     100  @   101  A   102  B   103  C   104  D   105  E   106  F   107  G
     ...
     140  `   141  a   142  b   143  c   144  d   145  e   146  f   147  g
     ...
     170  x   171  y   172  z   173  {   174  |   175  }   176  ~   177 del
```

Eight columns, sixteen rows, octal, and the layout is doing work the page never explains. Octal groups bits in threes, so a three-digit octal code is `column × 8 + row`, and the eight names on each line share their low three bits. The first four lines are the 32 control characters, named as the 1960s teletype named them: `bel` rang a bell, `bs` backed the carriage up, `ht` was a horizontal tab and `cr` a carriage return. Two names are older than the standard's own. `nl` at `012` is what the rest of the world calls LF, line feed, and `np` at `014` is FF, form feed, *new page*; these are older names than the standard's, and the BSD table has kept them. [Control characters](../../02_Characters/control_characters/README.md) is the page on what the 32 are for and which three still matter, and [The NUL byte](../../02_Characters/the_nul_byte/README.md) is about the first one.

The same table is then printed as *the hexadecimal set* and *the decimal set*, so a reader can look up a code in whichever base the tool in front of them speaks, `od` in octal, `xxd` in hex, Python's `ord()` in decimal, without converting. [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) is why the three are one number.

### `ascii(7)` on Linux: one table, with the escapes

```text title="man 7 ascii, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       C program '\X' escapes are noted.

       Oct   Dec   Hex   Char                        Oct   Dec   Hex   Char
       ────────────────────────────────────────────────────────────────────────
       000   0     00    NUL '\0' (null character)   100   64    40    @
       001   1     01    SOH (start of heading)      101   65    41    A
       ...
       007   7     07    BEL '\a' (bell)             107   71    47    G
       010   8     08    BS  '\b' (backspace)        110   72    48    H
       011   9     09    HT  '\t' (horizontal tab)   111   73    49    I
       012   10    0A    LF  '\n' (new line)         112   74    4A    J
       ...
       033   27    1B    ESC (escape)                133   91    5B    [
       034   28    1C    FS  (file separator)        134   92    5C    \  '\\'
       ...
       077   63    3F    ?                         │ 177   127   7F    DEL
```

Two columns of 64, and each row pairs a code with the code 64 above it, which is why the control character `SOH` shares a line with `A`: `001` and `101` differ in one bit. The escapes are the page's addition. `'\0'`, `'\a'`, `'\b'`, `'\t'`, `'\n'` and `'\\'` are how a C, Python or Rust source file spells these bytes, and the table is the only place on either machine that puts the escape, the name and the three numbers on one line. Note that `ESC` has no escape of its own in C, which is why terminal code is full of `\033` and `\x1b`.

```text title="man 7 ascii, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       Uppercase  and  lowercase  characters  differ by just one bit and the
       ASCII character 2 differs from the double quote by just one bit, too.
       That made it much easier to encode characters mechanically or with  a
       non-microcontroller-based  electronic  keyboard  and that pairing was
       found on old teletypes.
```

This paragraph is the reason the table has the shape it has. `A` is `0x41` and `a` is `0x61`: the difference is `0x20`, bit 5, and the shift key on a teletype was a wire that cleared it. `2` is `0x32` and `"` is `0x22`, one bit apart in bit 4, because `"` was shift-2 on that keyboard and the same wire did the job. The digits sit at `0x30`–`0x39` so that a digit's value is its low four bits, and the lowercase letters are the uppercase ones with bit 5 set, which is the fact that makes `tr 'A-Z' 'a-z'` correct for ASCII and wrong for every other alphabet: [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md). And because the table is arithmetic, arithmetic on it is a cipher with no key: [Rotation is not encryption](../../02_Characters/rotation_is_not_encryption/README.md).

One more row to look at closely: `` ` `` at `0x60` and `'` at `0x27`. They are different characters in different rows, the backtick being the lowercase counterpart of `@` and the apostrophe sitting among the punctuation, and a font that draws them alike is the reason so much shell code has the wrong one in it.

### `/usr/share/misc/ascii`: the same table as a file

```text title="cat /usr/share/misc/ascii, macOS 26.6.2, 2026-09-13 (lines 1, 9 and 26 of 50)"
|000 nul|001 soh|002 stx|003 etx|004 eot|005 enq|006 ack|007 bel|
|100  @ |101  A |102  B |103  C |104  D |105  E |106  F |107  G |
| 40  @ | 41  A | 42  B | 43  C | 44  D | 45  E | 46  F | 47  G |
```

The three sets again, pipe-delimited, and this is what the BSD page is rendered from. The point of a data file is that it is not a page: `grep` reads it, and the experiment below is a one-line lookup that returns the octal, hex and decimal codes of a character together. The library's own tour of the forty pages, [The encoding man pages nobody opens](../the_encoding_man_pages/README.md), calls it *occasionally exactly what you want*.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| *octal set*, *hexadecimal set*, *decimal set* | One table, three bases; a byte is three octal digits, two hex digits, or up to three decimal ones | [Counting in hexadecimal](../../01_Bits_and_Bytes/counting_in_hex/README.md) |
| `nul`, NUL, `'\0'` | Code 0: the C string terminator, the one byte no text file should contain, and a legal UTF-8 character | [The NUL byte](../../02_Characters/the_nul_byte/README.md) |
| `soh stx etx eot`, `enq ack nak syn etb` | Message framing and handshake codes from the teletype era: start of heading, start and end of text, end of transmission, enquiry, acknowledge | [Control characters](../../02_Characters/control_characters/README.md) |
| `bel`, `'\a'` | Code 7: rang the bell on a teletype; still beeps in a terminal | [Control characters](../../02_Characters/control_characters/README.md) |
| `bs ht nl vt np cr`, `'\b' '\t' '\n' '\v' '\f' '\r'` | The six carriage movements: backspace, tab, new line (LF), vertical tab, new page (FF), carriage return. `nl` and `np` are older names the BSD table keeps | [Control characters](../../02_Characters/control_characters/README.md) |
| `so`, `si` | Shift out and shift in, codes 14 and 15: switch a printer to its alternate character set and back, which ISO 2022 later reused to switch tables | [`charsets(7)` and the code-page pages](charsets.md) |
| `esc`, ESC, `0x1B` | The byte that begins every terminal control sequence; the one control with no C escape of its own | [Control characters](../../02_Characters/control_characters/README.md) |
| `fs gs rs us` | File, group, record and unit separators, codes 28–31: four delimiters ASCII reserved for structured data, almost never used, and therefore safe | [The byte that means something to somebody else](../../12_Adversarial/in_band_signals/README.md) |
| `sp`, SPACE, `0x20` | Code 32, the first printable character; also the case bit | [Rotation is not encryption](../../02_Characters/rotation_is_not_encryption/README.md) |
| `del`, DEL, `0x7F` | Code 127, all seven bits set: on paper tape, punching every hole erased a character. A control that sits after the printables | [Control characters](../../02_Characters/control_characters/README.md) |
| *differ by just one bit* | `A` `0x41` against `a` `0x61`; `2` `0x32` against `"` `0x22`: the shift key as a bit | [A character is a number](../../02_Characters/a_character_is_a_number/README.md) |
| `'\X'` escapes, `'\\'` | How source code spells a byte that has no printable glyph; `\` itself needs one | [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| *7-bit code* | 128 codes, `0x00`–`0x7F`; the eighth bit of a byte is what every code page and UTF-8 disagree about | [Code pages](../../02_Characters/code_pages/README.md) |
| ISO/IEC 646-IRV | The international standard whose *International Reference Version* is ASCII; national versions swapped `#`, `$`, `[` and `\` for local letters | [`charsets(7)` and the code-page pages](charsets.md) |
| USASI, 1968 | The United States of America Standards Institute, later ANSI; the 1968 revision is the `ANSI_X3.4-1968` that `locale charmap` prints under `LANG=C` on Ubuntu | [`utf8(5)` and `utf-8(7)`](utf8.md) |
| *backarrow*, *up-arrow* | What `_` and `^` looked like on 1960s terminals, before the 1968 revision gave them their present shapes | |
| `/etc/ascii` (VII) | The Seventh Edition data file, now `/usr/share/misc/ascii` on the Mac and absent on Ubuntu | [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) |

## Try it on your machine

**Where the page is, and where the file is.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: which files exist is a fact about the machine."
                                   macOS                                              ubuntu:24.04
$ man -w 7 ascii                   .../MacOSX.sdk/usr/share/man/man7/ascii.7           /usr/share/man/man7/ascii.7.gz
$ man 7 ascii | grep -c .          60                                                 118
$ ls -l /usr/share/misc/ascii      3170 bytes, 50 lines                               No such file or directory
```

**One grep, three bases.** The data file holds the octal, hex and decimal sets one after another, so a pattern that matches the character's cell matches three times.

```text title="Measured 2026-09-13 — macOS 26.6.2. Not machine-checked."
$ grep -o '[0-9a-f]\{1,3\}  \\ ' /usr/share/misc/ascii
134  \
5c  \
92  \
$ grep -o '[0-9a-f]\{1,3\} esc' /usr/share/misc/ascii     033 esc  1b esc  27 esc
$ grep -o '[0-9a-f]\{1,3\} del' /usr/share/misc/ascii     177 del  7f del  127 del
$ man 7 ascii | grep -o '[0-9a-f]\{1,3\}  A '              101  A   41  A   65  A
```

Backslash is `134` octal, `5c` hex, `92` decimal, and the three answers arrive in the order the file prints its sets. The last line does the same to the rendered page, which works because `man` output is text. On Ubuntu the equivalent is one row, and the row carries its neighbour 64 codes below:

```text title="Measured 2026-09-13 — ubuntu:24.04. Not machine-checked."
$ man 7 ascii | grep -E '134 +92 +5C'
       034   28    1C    FS  (file separator)        134   92    5C    \  '\\'
$ man 7 ascii | grep -E '  101 +65 +41 +A'
       001   1     01    SOH (start of heading)      101   65    41    A
```

**The shell can do the lookup without the page.** POSIX `printf` reads a leading quote as *the numeric value of the next character*.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04: identical. Not machine-checked."
$ printf '%d %o %x\n' "'A" "'A" "'A"
65 101 41
$ printf '\x41\x61\n'
Aa
```

**The case bit and the digit offset, in Python.** Each line is a claim from the Linux page's `NOTES`, checked.

```text title="Measured 2026-09-13 — python3 3.14 on macOS 26.6.2 and 3.12 on ubuntu:24.04: identical. Not machine-checked."
$ python3 -c "print(hex(ord('A')), hex(ord('a')), hex(ord('A') ^ ord('a')), chr(ord('a') & ~0x20), chr(ord('Q') | 0x20))"
0x41 0x61 0x20 A q
$ python3 -c "print(hex(ord('2')), hex(ord('\"')), hex(ord('2') ^ ord('\"')))"
0x32 0x22 0x10
$ python3 -c "print(ord('7') - 0x30, chr(0x30 + 7), ord('0'), ord('9'))"
7 7 48 57
$ python3 -c "print(hex(ord('\`')), hex(ord(\"'\")))"
0x60 0x27
$ printf 'Zebra 42\n' | tr 'A-Z' 'a-z'
zebra 42
```

`A ^ a` is `0x20`, one bit, and clearing it is uppercase, setting it lowercase. `2 ^ "` is `0x10`, one bit, the page's second claim. A digit's value is the digit minus `0x30`. And `tr 'A-Z' 'a-z'` is the case bit as a command, correct for the 26 letters and for nothing outside the table: [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md).

**Reproduce a row.** The BSD octal set, line `100`–`107`, from a one-line Python program.

```text title="Measured 2026-09-13 — python3 3.14 on macOS 26.6.2. Not machine-checked."
$ python3 -c "print('   '.join(f'{i:03o}  {chr(i)}' for i in range(0o100, 0o110)))"
100  @   101  A   102  B   103  C   104  D   105  E   106  F   107  G
$ grep -E '^ +100 ' raw/macos/ascii.7.txt
     100  @   101  A   102  B   103  C   104  D   105  E   106  F   107  G
```

The row is arithmetic and the table is a program's output, which is the whole point: nobody memorises it. What is worth memorising is the shape, digits at `0x30`, uppercase at `0x41`, lowercase at `0x61`, `0x20` between the cases.

## Where the page is dated, and what it does not say

**The BSD page is dated June 5, 1993** and has not needed a change since, because its subject was frozen in 1968. Its names for two codes, `nl` and `np`, are older than the standard's LF and FF, and a reader who searches the page for `LF` finds nothing. It gives no C escapes and no names in full: `soh` is never expanded to *start of heading*.

**The Linux page is dated 2024-01-28** and its content is also from 1993; what changed in between is presentation, the compact tables and the three notes. Its `SEE ALSO` lists fifteen `iso_8859-*(7)` pages, none of which is on the Mac.

**Neither page says what a byte above `0x7F` is.** The Linux page says ASCII is 7-bit and stops; the BSD page does not say even that. The answer is on [`charsets(7)`](charsets.md) for the single-byte tables and on [`utf8(5)`](utf8.md) for the one that won.

**Neither page mentions that the table is a subset of Unicode**, that `U+0041` is `0x41`, or that the C escapes it lists (Linux) are also the Python and Rust ones. The bridge from this table to every other is [A character is a number](../../02_Characters/a_character_is_a_number/README.md).

**The data file is undocumented as a file.** `ascii(7)` names it under `FILES` and says nothing about its format; it has no page of its own, and Ubuntu, which has no such file, has nowhere to look one up.

## See also

- [`charsets(7)` and the code-page pages](charsets.md) — the upper half, which every one of those pages says it leaves to this one
- [`utf8(5)` and `utf-8(7)`](utf8.md) — the encoding whose first row is this table
- [`ctype(3)` and the character classes](ctype.md) — `isalpha`, `isdigit`, `toupper`: this table as C functions, and where the case bit stops being the rule
- [`man(1)` and `mandoc(1)`](man.md) — why `man 7 ascii | grep` works: the page is text
- [A character is a number](../../02_Characters/a_character_is_a_number/README.md) — the 1963 agreement, and why the layout is not an accident
- [Control characters](../../02_Characters/control_characters/README.md) — the first 32 rows, and the three that still decide how text files are cut
- [The NUL byte](../../02_Characters/the_nul_byte/README.md) — row zero
- [Rotation is not encryption](../../02_Characters/rotation_is_not_encryption/README.md) — arithmetic on this table, with the shift published in the name
- [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) and [Counting in hexadecimal](../../01_Bits_and_Bytes/counting_in_hex/README.md) — why the three sets are one set
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) — where this page and its data file sit among the forty
