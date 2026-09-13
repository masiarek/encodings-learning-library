# `hexdump(1)`, `od(1)`, `xxd(1)` and `strings(1)`: four pages, one column that is the file

**Level:** reference · for anyone who has typed `man hexdump` and wanted to know what `%_p` is, or why `od -a` calls a byte `nl` that `hexdump` calls `lf`

**One line:** Each of the four pages defines a text column, three of them define it differently, and only `hexdump`'s page says in print what the library keeps having to say: the column is a *conversion* applied to the bytes, the hex is the file, and every word on these pages about "characters" is a decision the page's date froze.

**The pages:** [`hexdump(1)`](raw/macos/hexdump.1.txt) (macOS, dated June 29, 2020) · [`od(1)`](raw/macos/od.1.txt) (macOS, December 22, 2011) · [`xxd(1)`](raw/macos/xxd.1.txt) (May 2024, "documents xxd version 1.7") · [`strings(1)`](raw/macos/strings.1.txt) (Apple, Inc., June 7, 2016). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). No Linux dump of these four exists in [`raw/linux/`](raw/PROVENANCE-linux.txt), which holds the encoding pages only; Ubuntu's tools were measured, not their pages.

## What the pages are for

Three of these are the BSD dump utilities and one is a guest. `hexdump(1)` and `od(1)` are section-1 filters that read a file and print numbers, and their pages are mostly a description of *which* numbers: `od`'s interface is a C type (`-t x1`, `-t d2`, `-t fD`) and `hexdump`'s is a `printf`-style format language with three conversions of its own, which the page defines in a section called *Formats*. `od` is the one POSIX requires and the one every stripped-down container has; `hexdump` is BSD's and, on Ubuntu, util-linux's copy of the same code. Neither page has a HISTORY section that says so, but the two `hexdump`s print byte-identical output for everything on this page except one flag.

`xxd(1)` is not a BSD page at all. Its footer reads *Manual page for xxd*, its AUTHOR section is Juergen Weigert's 1990s licence in verse, and it ships with `vim`, which is why it is the only dump here with a reverse mode: `:%!xxd`, edit, `:%!xxd -r` is how a binary is edited in a text editor. Its VERSION section says it *documents xxd version 1.7 from 2024-05*; the two binaries on this Mac answer `xxd 2025-08-24` (`/usr/bin/xxd`) and `xxd 2025-11-26` (`/usr/local/bin/xxd`, first in `PATH`), so the page is older than either program it describes.

`strings(1)` is Apple's own page from cctools, 68 lines, footer *Apple, Inc. June 7, 2016*, and it documents a different program from the GNU `strings` a Linux reader knows: no `-e`, no `-U`, no `--version`, and a default that reads the sections of a Mach-O object rather than the bytes of a file. The library's [`strings` lesson](../../11_Tools/strings/README.md) measured that split at length; this page is about what the two pages *say*.

What all four have in common is a right-hand column that looks like text. The library's [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) calls it a *reading*, not the file, and this page is where the four definitions of that reading are quoted side by side.

## The page, with notes

### `hexdump(1)`: the format language, and the three text conversions

```text title="man 1 hexdump, macOS 26.6.2, dumped 2026-09-13"
     A format string contains any number of format units, separated by
     whitespace.  A format unit contains up to three items: an iteration
     count, a byte count, and a format.
     ...
     If an iteration count and/or a byte count is specified, a single slash
     must be placed after the iteration count and/or before the byte count to
     disambiguate them.
```

That is the whole language: `16/1 "%02x "` is sixteen units of one byte, each printed with `%02x`. The six letter flags on the page (`-b -c -C -d -o -x`) are canned strings in this language, and [the `hexdump` lesson](../../11_Tools/hexdump/README.md) writes all six out and diffs them against the flags. The page also gives the rule that makes `-C` need three `-e` strings rather than one: *the input is manipulated in "blocks", where a block is defined as the largest amount of data specified by any format string*, and each format string is applied to the same block from its start.

```text title="man 1 hexdump, macOS 26.6.2, dumped 2026-09-13"
     _c          Output characters in the default character set.  Nonprinting
                 characters are displayed in three character, zero-padded
                 octal, except for those representable by standard escape
                 notation (see above), which are displayed as two character
                 strings.

     _p          Output characters in the default character set.  Nonprinting
                 characters are displayed as a single ".".

     _u          Output US ASCII characters, with the exception that control
                 characters are displayed using the following, lower-case,
                 names.  Characters greater than 0xff, hexadecimal, are
                 displayed as hexadecimal strings.
```

These three are the text column. `%_p` is the one inside `-C`'s bars, and the page defines `-C` in terms of it: *followed by the same sixteen bytes in %_p format enclosed in "|" characters*. So the page itself states that the readable column is a conversion of the same bytes, which is the sentence every dump tutorial leaves out. What it does not state is what *the default character set* is. On this Mac it is the locale's: under `LC_ALL=C` the byte `c3` prints as `303` for `%_c` and `c3` for `%_u`, and under `en_US.UTF-8` both print the raw byte, exactly as [`od -a` does](../../06_Terminal/inspecting_a_file/README.md), while util-linux's `hexdump` prints the octal in every locale. The measurement is below. `%_u`'s table names `0x0A` as `LF`; `od`'s table for `-t a`, on the next page, names the same byte `NL`.

```text title="man 1 hexdump, macOS 26.6.2, dumped 2026-09-13"
     -s offset
             Skip offset bytes from the beginning of the input.  By default,
             offset is interpreted as a decimal number.  With a leading 0x or
             0X, offset is interpreted as a hexadecimal number, otherwise,
             with a leading 0, offset is interpreted as an octal number.
```

The C rule for integer literals, applied to a command-line argument: `-s 010` skips eight bytes, not ten. It is the same three-way ambiguity as [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md), and `xxd -s` and `od -j` follow the same rule without saying so on their pages. The `-v` paragraph beside it defines the asterisk, *any number of groups of output lines which would be identical to the immediately preceding group ... are replaced with a line comprised of a single asterisk*, and the lesson shows that the squeeze applies to your own `-e` format too, so a plain-hex format without `-v` can print four characters for a 64-byte file.

### `od(1)`: types, names, and the sentence about `**`

```text title="man 1 od, macOS 26.6.2, dumped 2026-09-13"
                    a       Named characters (ASCII).  Control characters are
                            displayed using the following names:

                            000 NUL 001 SOH 002 STX 003 ETX 004 EOT 005 ENQ
                            006 ACK 007 BEL 008 BS  009 HT  00A NL  00B VT
                            ...
                    c       Characters in the default character set.  Non-
                            printing characters are represented as 3-digit
                            octal character codes, except the following
                            characters, which are represented as C escapes:
                            ...
                            Multi-byte characters are displayed in the area
                            corresponding to the first byte of the character.
                            The remaining bytes are shown as `**'.
```

`-t a` says *ASCII* and gives a table of 34 names, for the 32 C0 controls, space and `DEL`; it says nothing about the other 128, and the two implementations invent different names for them, which is why the library records no `od -a` output anywhere: [`od` reads types, not bytes](../../11_Tools/od/README.md). The `**` sentence is the one to test. It is true on this Mac in a UTF-8 locale, where `od -c` decodes `é` and prints its second byte as `**`, and false on Ubuntu, whose `od -c` prints `303 251` in every locale. The page's ENVIRONMENT section, *The LANG, LC_ALL and LC_CTYPE environment variables affect the execution of od*, is the one line that warns you; the `hexdump` page has no such section and its BSD build behaves the same way.

```text title="man 1 od, macOS 26.6.2, dumped 2026-09-13"
     -A base        Specify the input address base.  The argument base may be
                    one of d, o, x or n, which specify decimal, octal,
                    hexadecimal addresses or no address, respectively.
     ...
     -j skip        Skip skip bytes of the combined input before dumping.  The
                    number may be followed by one of b, k, m or g which
                    specify the units of the number as blocks (512 bytes),
                    kilobytes, megabytes and gigabytes, respectively.
     ...
     If no output format is specified, -t oS is assumed.
```

`-A n -t x1` is the incantation, and it is built from these two paragraphs. `-t oS` is octal shorts, sixteen-bit words, so the default output is two-byte numbers in the CPU's byte order at octal offsets: [Grouping is a choice](../../01_Bits_and_Bytes/grouping_is_a_choice/README.md) is why that is a claim about the file and not a picture of it. The COMPATIBILITY section notes that *the traditional -s option to extract string constants is not supported; consider using strings(1)*: on this page `-s` means signed decimal shorts.

### `xxd(1)`: the only page that names the agreement

```text title="man 1 xxd, xxd version 1.7 (May 2024), dumped 2026-09-13 on macOS 26.6.2"
       -E | -EBCDIC
              Change the character encoding in the righthand column from ASCII
              to EBCDIC.  This does not change the hexadecimal representation.
              The option is meaningless in combinations with -r, -p or -i.
```

Two sentences, and they are the clearest statement in the family. The right-hand column has a *character encoding*, it can be changed, and changing it does not touch the hex. `-E` is measured below; the [`xxd` lesson](../../11_Tools/xxd/README.md) makes it the centrepiece. The CAVEATS section says the same thing from the other side: *changes to the printable ASCII (or EBCDIC) columns are always ignored* by `xxd -r`, and *xxd -r never generates parse errors. Garbage is silently skipped.* The page's `-s [+][-]seek` paragraph is worth reading twice: a leading `-` counts from the end of the input, a leading `+` from the current stdin position, and the EXAMPLES section spends a page on what that means when `dd` has already read part of stdin. `-g` and `-c` set the group and line width, `-p` the *PostScript continuous hex dump style* with no offsets or text, `-i` a C array, `-b` bits, and `-R when` colour, which is new since the library's lesson was written.

### `strings(1)`: Apple's page, and what is not on it

```text title="man 1 strings, macOS 26.6.2 (Apple cctools), dumped 2026-09-13"
       Strings looks for ASCII strings in a binary file or standard input.
       Strings is useful for identifying random object files and many other
       things.  A string is any sequence of 4 (the default) or more printing
       characters [ending at, but not including, any other character or EOF].
       Unless the - flag is given, strings looks in all sections of the object
       files except the (__TEXT,__text) section.  If no files are specified
       standard input is read.
```

*ASCII strings* and *printing characters* in one sentence, and the page never says which set *printing* is. The lesson measured it: ASCII plus form feed for a named file, and the locale's `isprint()` one byte at a time for stdin, which is how Apple's `strings` cuts `żółw` after its fifth byte. The default scope, *all sections ... except (__TEXT,__text)*, is why `strings` on a small Mach-O prints nothing at all and `strings -` is the command the tutorials mean. The options are `-a`, `-`, `-o`, `-t d|o|x`, `-n number`, `-number` and `-arch`, and the BUGS section is one sentence: *The algorithm for identifying strings is extremely primitive.* GNU `strings` 2.42 on Ubuntu has `-e s|S|b|l|B|L` for 7-bit, 8-bit, 16-bit and 32-bit units in either byte order, and `-U` for UTF-8; on this Mac `-e` is *unknown flag*, exit 1, which is the loud kind of incompatibility.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| format unit, iteration count, byte count | One `count/size "format"` triple; the count is how many times, the size is how many bytes each conversion eats | [`hexdump` is a format engine](../../11_Tools/hexdump/README.md) |
| block (`hexdump`) | The largest number of bytes any `-e` string asks for; every `-e` string is applied to the same block from its start | [`hexdump` is a format engine](../../11_Tools/hexdump/README.md) |
| `%_p` | The byte if it is printable in the *default character set*, else `.`; the column inside `-C`'s bars | [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) |
| `%_c` | The byte as a character, a C escape, or three octal digits; `-c` is `16/1 "%3_c "` | [`hexdump` is a format engine](../../11_Tools/hexdump/README.md) |
| `%_u` | The byte as *US ASCII* with lower-case control names, `lf` for `0a` | [ASCII](ascii.md) |
| *default character set* | Undefined on the page; on this Mac it is the locale's `LC_CTYPE`, on util-linux it is ASCII | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `-s offset`, `0x`, leading `0` | The C literal rule: `010` is eight | [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) |
| `*` (the squeeze), `-v` | Repeated output lines replaced by one asterisk; `-v` prints them all; `xxd -a` collapses NUL lines only | [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) |
| `-t a`, *named characters* | `od`'s table of 34 names for the control bytes, `nl` for `0a`; the other 128 bytes are named by the implementation | [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) |
| `**` | `od -c`'s placeholder for the continuation bytes of a multibyte character it decoded; BSD only | [`od` reads types, not bytes](../../11_Tools/od/README.md) |
| `-t oS`, `-t x1`, `[d|o|u|x][C|S|I|L|n]` | A type letter and a size: base, then `char`, `short`, `int`, `long` or a byte count | [`od` reads types, not bytes](../../11_Tools/od/README.md) |
| EBCDIC (`xxd -E`) | IBM's other agreement about which byte is which letter; `61` is `/`, `c3` is `C` | [Code pages](../../02_Characters/code_pages/README.md) |
| *mail-safe ASCII representation* | `xxd`'s own description of its output, beside `uuencode`; a hex dump is a binary-to-text encoding at four bits per character | [`bintrans(1)`](binary_to_text.md) |
| *printing characters* | Undefined on the `strings` page; POSIX hands the word to `LC_CTYPE`, GNU fixes it at ASCII plus tab | [`strings` has a printable set](../../11_Tools/strings/README.md) |

## Try it on your machine

**The three text conversions, one byte per line.** A hand-written `-e` format with four `-e` strings, each applied to a one-byte block: decimal offset, hex, `%_u`, `%_c`, `%_p`. The file is `café €` and a newline, ten bytes.

```text title="Measured 2026-09-13 — LC_ALL=C: byte-identical on macOS 26.6.2 (BSD hexdump) and ubuntu:24.04 (util-linux 2.39.3)."
$ printf 'caf\303\251 \342\202\254\n' > s.txt
$ hexdump -v -e '"%2_ad  " 1/1 "%02x  "' -e '1/1 "%-4_u"' -e '1/1 "%-5_c"' -e '1/1 "%_p" "\n"' s.txt
 0  63  c   c    c
 1  61  a   a    a
 2  66  f   f    f
 3  c3  c3  303  .
 4  a9  a9  251  .
 5  20            
 6  e2  e2  342  .
 7  82  82  202  .
 8  ac  ac  254  .
 9  0a  lf  \n   .
```

Three conversions, three answers for `c3`: `c3` from `%_u` (a hex string, as the page says for anything not ASCII), `303` from `%_c` (octal), and a dot from `%_p`. None of them is `é`, because none of them can be: each conversion sees one byte. Under a UTF-8 locale the BSD build changes and the util-linux one does not:

```text title="Measured 2026-09-13 — the same command under LC_ALL=en_US.UTF-8 (macOS) and LC_ALL=C.utf8 (ubuntu:24.04), through cat -v so the raw bytes are printable. Not machine-checked."
                  macOS 26.6.2                 ubuntu:24.04
 3  c3            M-C   M-C    .               c3  303  .
 4  a9            M-)   M-)    .               a9  251  .
 7  82            82  202  .                   82  202  .
 8  ac            M-,   M-,    .               ac  254  .
```

`M-C` is `cat -v`'s spelling of the byte `c3`: BSD `hexdump` asked `isprint()` about `c3` in a UTF-8 locale, was told yes (it is `Ã` in Latin-1's half of the table), and wrote the byte itself, which no UTF-8 terminal can draw. `82` is a C1 control, so it fell through to the hex string. That is the `od -a` fiction, in `hexdump`, from a page that says *US ASCII*.

**The base rule for `-s`.** Four spellings of a skip, three of which mean eight.

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 and ubuntu:24.04."
$ for o in 8 0x8 010 10; do printf -- '-s %-4s ' "$o"; hexdump -C -s $o -n 2 s.txt | head -1; done
-s 8    00000008  ac 0a                                             |..|
-s 0x8  00000008  ac 0a                                             |..|
-s 010  00000008  ac 0a                                             |..|
-s 10   0000000a
```

**`od -c` and the `**` sentence.** Hex over characters, in both locales, on both machines.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD od) and ubuntu:24.04 (GNU coreutils 9.4), through cat -v. Not machine-checked: BSD pads and GNU does not, and only BSD decodes."
$ LC_ALL=C od -An -tx1 -c s.txt                          # both machines, numbers identical, padding not
           63  61  66  c3  a9  20  e2  82  ac  0a
           c   a   f 303 251     342 202 254  \n
$ LC_ALL=en_US.UTF-8 od -An -tx1 -c s.txt                # macOS
           63  61  66  c3  a9  20  e2  82  ac  0a
           c   a   f   M-CM-)  **       M-bM-^BM-,  **  **  \n
$ LC_ALL=C.utf8 od -An -tx1 -c s.txt                     # ubuntu:24.04
  63  61  66  c3  a9  20  e2  82  ac  0a
   c   a   f 303 251     342 202 254  \n
```

BSD `od` did what its page says: the two bytes of `é` and the three of `€` were decoded, written into the first byte's column as raw bytes (`M-CM-)` is `c3 a9`), and the rest marked `**`. GNU `od` printed octal for every byte in every locale, and its page, which was not dumped, would not have told you to expect the difference either.

**`xxd -E`, and the newline's two names.**

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 (xxd 2025-11-26) and ubuntu:24.04 (xxd 2023-10-25)."
$ xxd s.txt
00000000: 6361 66c3 a920 e282 ac0a                 caf.. ....
$ xxd -E s.txt
00000000: 6361 66c3 a920 e282 ac0a                 ./.Cz.Sb..
$ printf 'a\n' | LC_ALL=C od -An -a
   a  nl
$ printf 'a\n' | hexdump -e '2/1 "%_u " "\n"'
a lf
```

Same ten bytes, same hex, and the text column rewritten under IBM's agreement: `61` is `/`, `c3` is `C`, `e2` is `S`. The last two commands are the two pages' tables disagreeing about one byte: `0a` is `NL` on the `od` page and `LF` on the `hexdump` page, on the same machine.

**`strings` on UTF-16.** The file is `Hello café €` in UTF-16LE.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple strings) and ubuntu:24.04 (GNU strings 2.42). Not machine-checked: one build has the flag and one does not."
                                    macOS                                                 ubuntu:24.04
$ strings h16.txt                   (nothing)                                             (nothing)
$ strings -e l h16.txt              error: .../strings: unknown flag: -e   (exit 1)       Hello caf
$ strings -e S s.txt                error: .../strings: unknown flag: -e   (exit 1)       café €
```

GNU's `-e l` reads 16-bit little-endian units and finds `Hello caf`, then stops at `é`: `-e` sets the *width* of a character, not the set of printable ones, and that set is still ASCII, so the accent ends the run exactly as it does in the 8-bit mode. Only `-e S`, the 8-bit width with the top half switched on, returns the whole string, and it does so by no longer asking what the bytes mean. Apple's `strings` has neither flag and says so.

**Where the pages are.** Every page in this family is in Apple's Command Line Tools SDK, and `strings.1` is the one that lives with the tools rather than the SDK.

```text title="Measured 2026-09-13 — macOS 26.6.2. Not machine-checked."
$ man -w 1 hexdump   /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/share/man/man1/hexdump.1
$ man -w 1 strings   /Library/Developer/CommandLineTools/usr/share/man/man1/strings.1
$ command -v xxd     /usr/local/bin/xxd
$ xxd -v             xxd 2025-11-26 by Juergen Weigert et al.
$ /usr/bin/xxd -v    xxd 2025-08-24 by Juergen Weigert et al.
```

## Where the page is dated, and what it does not say

**`hexdump(1)` is dated June 29, 2020** and does not contain the words *locale*, *UTF-8* or `LC_CTYPE`. It defines `%_c` and `%_p` over *the default character set* without saying what that is, and the measurement above shows this Mac's build taking it from the locale one byte at a time. It never says that the `-v` squeeze applies to a format you wrote yourself, which is the trap in the lesson. It has no HISTORY section, so it does not say that Ubuntu's `hexdump` is the same 4.4BSD program carried by util-linux, which is why the two agree everywhere except in a UTF-8 locale under `_c` and `_u`.

**`od(1)` is dated December 22, 2011** and its `**` sentence describes BSD `od` only. Its `-t a` table says *ASCII* and stops at `DEL`; what happens to the other 128 bytes is not on the page, and the two implementations do different things. GNU's `z` suffix, which adds a `>text<` column and turns `od -Ax -tx1z` into something close to `hexdump -C`, is not on this page and not in this binary.

**`xxd(1)` documents version 1.7 of May 2024** on a machine running two newer builds. The `-R when` colour flag is on the page and in both binaries; the little-endian `-e` mode's padding, which differs between the 2023 and 2025 builds, is on neither the page nor the lesson's answer key, only in its dated fence. The word *UTF* does not appear on the page; the page's whole theory of text is `-E`, and it is the honest one.

**`strings(1)` is dated June 7, 2016** and is not the page a Linux reader has read. It documents Apple's cctools `strings`: `-` to read every byte, `-arch`, and no `-e`, `-U`, `-d` or `--version`. It says *ASCII strings* and *printing characters* without defining either, and does not say that the stdin path consults the locale while the named-file path does not, which the lesson measured. The GNU page would tell you about `-e` and `-U`; it was not dumped, and the measurement above stands in for it.

**None of the four pages mentions UTF-8.** Searched: the string `UTF` occurs in none of the four dumps (the three hits in `xxd.1` are the word *outfile*). Four pages about looking at bytes, and not one of them names the encoding those bytes are most likely to be in.

## See also

- [`file(1)` and `magic(5)`](file.md) — the tool that guesses what the bytes are before you dump them
- [`vis(1)` and `vis(3)`](vis.md) — the other respelling of unprintable bytes, with a page that defines every escape
- [`byteorder(3)`](byteorder.md) — why `hexdump`'s default and `od`'s default swap pairs
- [`hexdump` is a format engine wearing six presets](../../11_Tools/hexdump/README.md) — the six flags written out, and the squeeze that destroys data
- [`od` reads types, not bytes](../../11_Tools/od/README.md) — the one that is always installed, and why its output cannot be quoted without naming the machine
- [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) — `-r`, `-E`, and the column it throws away
- [`strings` has a printable set, not an encoding](../../11_Tools/strings/README.md) — the four printable tables, measured
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — the four tools inside a workflow, and which column is the file
- [A page has a date](../a_page_has_a_date/README.md) — an `xxd` page from 2024 on a machine with two 2025 builds
- [What the page does not say](../what_the_page_does_not_say/README.md) — *the default character set*, left undefined
