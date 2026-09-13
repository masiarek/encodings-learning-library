# `dd(1)`: the byte mover with six code-page tables inside it

**Level:** reference · for anyone who has typed `dd if=... of=...` and skipped the `conv=` paragraph

**One line:** `dd` copies blocks and never reads text, except under `conv=`, where it carries six 256-byte tables from the 1970s, a byte-swapper that turns UTF-16LE into UTF-16BE, a case-mapper that on this Mac damages UTF-8 lead bytes in a UTF-8 locale, and a record padder that is the fixed-width-field problem as a command.

**The pages:** [`dd(1)`](raw/macos/dd.1.txt) (macOS 26.6.2, dated May 19, 2021). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). GNU `dd` (coreutils 9.4) on ubuntu:24.04 was measured beside it.

## What the page is for

`dd` is the oldest tool in this folder that is still spelt the way it was: its `operand=value` syntax is usually explained as a nod to the `DD` statement of IBM's Job Control Language, and the job its `conv=` operands describe, turning fixed-width records in EBCDIC into newline-terminated lines in ASCII, is still on the page as `conv=ascii` and `conv=unblock`. The HISTORY line says only that *A dd command appeared in Version 5 AT&T UNIX*. Everything else on the page is about *blocks*: how many bytes to read at a time, how many to write, how many to skip, and what to do when a read comes up short. None of that is text. A block is a count of bytes, and `dd` is the one tool in the library that will copy a partial UTF-8 character without any opinion about it.

The page is in section 1 and is one long list of operands, which is why it is a family of one. It matters here for the `conv=` list, which is a small museum of character-encoding history: the four EBCDIC tables and two ASCII tables are [code pages](../../02_Characters/code_pages/README.md) built into a program rather than looked up by name, `swab` is [byte order](../../01_Bits_and_Bytes/which_end_comes_first/README.md) as a verb, `lcase` and `ucase` are [case as a per-byte table](../../02_Characters/case_is_not_per_character/README.md), and `block`/`unblock` are [fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) with the padding rule written down. `parnone` and its siblings even document the seven-bit channel.

Two implementations answer to the name. The page describes the BSD one on this Mac; GNU `dd` accepts most of the same operands, refuses three of the six tables, spells its size suffixes differently, and prints a different summary line. Where they differ is measured below.

## The page, with notes

### Blocks, counts and sizes

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
     bs=n     Set both input and output block size to n bytes, superseding the
              ibs and obs operands.  If no conversion values other than
              noerror, notrunc or sync are specified, then each input block is
              copied to the output as a single block without any aggregation
              of short blocks.

     cbs=n    Set the conversion record size to n bytes.  The conversion
              record size is required by the record oriented conversion
              values.
```

Three sizes, three jobs. `ibs` is how much one `read(2)` asks for, `obs` is how much one `write(2)` sends, and `bs` sets both and switches off the re-blocking in between, so a short read becomes a short write. `cbs` is different in kind: it is the width of a *record* for `block`, `unblock` and the code-page conversions, the number that turns a stream into rows. `count`, `skip` and `seek` are counted in input blocks, output blocks and input blocks respectively, and `skip` on a pipe *reads and discards* because a pipe cannot seek.

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
     Where sizes or speed are specified, a decimal, octal, or hexadecimal
     number of bytes is expected.  If the number ends with a "b", "k", "m",
     "g", "t", "p", or "w", the number is multiplied by 512, 1024 (1K),
     1048576 (1M), 1073741824 (1G), 1099511627776 (1T), 1125899906842624 (1P)
     or the number of bytes in an integer, respectively.  Two or more numbers
     may be separated by an "x" to indicate a product.
```

`b` is a disk block of 512, the unit `tail -b` and `ls -s` still use; `w` is *the number of bytes in an integer*, which is 4 here and 2 on GNU `dd`, whose `--help` defines `w=2`. The `x` product is old JCL habit: `bs=2x3` is six bytes. GNU `dd` rejects the lowercase `m` and the `0x` prefix this page accepts, and accepts `M` and `kB` instead.

### The summary

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
     When finished, dd displays the number of complete and partial input and
     output blocks, truncated input records and odd-length byte-swapping
     blocks to the standard error output.  A partial input block is one where
     less than the input block size was read.
```

`0+1 records in` means no complete block and one partial one, which is what a five-byte `printf` on a pipe produces against the 512-byte default. `status=none` silences it on both implementations; `status=noxfer` keeps the record counts and drops the transfer line, which is the line whose wording differs.

### `conv=`: the six tables

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
              ascii, oldascii
                       The same as the unblock value except that characters
                       are translated from EBCDIC to ASCII before the records
                       are converted.  (These values imply unblock if the
                       operand cbs is also specified.)  There are two
                       conversion maps for ASCII.  The value ascii specifies
                       the recommended one which is compatible with AT&T
                       System V UNIX.  The value oldascii specifies the one
                       used in historic AT&T UNIX and pre-4.3BSD-Reno systems.
              ...
              ebcdic, ibm, oldebcdic, oldibm
                       The same as the block value except that characters are
                       translated from ASCII to EBCDIC after the records are
                       converted.  (These values imply block if the operand
                       cbs is also specified.)  There are four conversion maps
                       for EBCDIC.  The value ebcdic specifies the recommended
                       one which is compatible with AT&T System V UNIX.  The
                       value ibm is a slightly different mapping, which is
                       compatible with the AT&T System V UNIX ibm value.  The
                       values oldebcdic and oldibm are maps used in historic
                       AT&T UNIX and pre-4.3BSD-Reno systems.
```

Six 256-entry tables, named by lineage rather than by any code-page number: *System V*, *historic AT&T UNIX*, *pre-4.3BSD-Reno*. [POSIX ↗](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/dd.html) standardises `ascii`, `ebcdic` and `ibm`; the three `old` ones are BSD extensions that GNU `dd` does not have, and the page's own STANDARDS section lists all six as extensions. None of the names says which IBM code page it is, and the page does not say either, so the experiment below asks `iconv`. The answer for the ASCII range is that `ibm` is CP1047 byte for byte on every character tested, that `ebcdic` is the same table except for `^` and `~`, identically on both machines, and that `oldebcdic` is CP500 except for `|`. None of the six is CP037. Above `0x7f` the tables are not any code page: they are a permutation that makes `ebcdic` then `ascii` a round trip, which is a property of bytes and says nothing about what the bytes mean.

### `conv=`: swab, case, records, padding

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
              lcase    Transform uppercase characters into lowercase
                       characters.
              ...
              swab     Swap every pair of input bytes.  If an input buffer has
                       an odd number of bytes, the last byte will be ignored
                       during swapping.
              ...
              ucase    Transform lowercase characters into uppercase
                       characters.
```

`swab` is [Swap Bytes](../../15_Hex/swap_bytes/README.md) on the whole stream with a width of two: UTF-16LE in, UTF-16BE out, byte order mark included, and [`swab(3)`](byteorder.md) is the same operation as a C library function. The case conversions are two lines each and the two lines do not say *which* characters, in *which* locale, by *which* table. The measurement below is the answer: it is `toupper(3)` applied to each byte, and on this Mac in a UTF-8 locale `toupper` and `tolower` have opinions about single bytes between `0xc0` and `0xff`, so `conv=lcase` turns the lead byte `c3` of `É` into `e3` and the output is no longer UTF-8. GNU `dd` folds ASCII only, in every locale.

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
              block    Treats the input as a sequence of newline or end-of-
                       file terminated variable length records independent of
                       input and output block boundaries.  Any trailing
                       newline character is discarded.  Each input record is
                       converted to a fixed length output record where the
                       length is specified by the cbs operand.  Input records
                       shorter than the conversion record size are padded with
                       spaces.  Input records longer than the conversion
                       record size are truncated.
              ...
              unblock  Treats the input as a sequence of fixed length records
                       independent of input and output block boundaries.  The
                       length of the input records is specified by the cbs
                       operand.  Any trailing space characters are discarded
                       and a newline character is appended.
```

This is a fixed-width file format in two paragraphs: a record is `cbs` bytes, short ones are padded with spaces, long ones are cut, and the cut is at a byte count. `printf 'ab\ncdef\n' | dd conv=block cbs=4` writes `ab  cdef`, eight bytes and no newline, and a five-letter line would lose its fifth letter and be counted in the summary as a *truncated record*. The library's [Packing a record](../../07_Real_Data/packing_a_record/README.md) and [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) are this paragraph with a UTF-8 character straddling the cut. `sync` is the block-level cousin, padding a short *input block* to `ibs` with NUL, or with spaces when a record conversion is in effect; `noerror` keeps going past a read error, which with `sync` means the missing data becomes padding; `notrunc` leaves the rest of the output file alone.

```text title="man 1 dd, macOS 26.6.2, dumped 2026-09-13"
              pareven, parnone, parodd, parset
                       Output data with the specified parity.  The parity bit
                       on input is stripped unless EBCDIC to ASCII conversions
                       is also specified.
```

Four operands for a world where the eighth bit was a checksum rather than data. `parnone` is the seven-bit channel that [UTF-7](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) was designed to survive, and `istrip` on [`stty(1)`](tty.md) is the same bit being stripped by the terminal driver. The EXAMPLES section still shows `dd if=file conv=parnone of=file.txt`.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| block | a fixed number of bytes read or written in one system call; 512 by default | |
| record | a row of a file, either newline-terminated (`block`'s input) or exactly `cbs` bytes long (`block`'s output) | [Packing a record](../../07_Real_Data/packing_a_record/README.md) |
| `cbs`, *conversion record size* | the width of a fixed record, in bytes, never characters | [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) |
| partial block, *0+1 records* | a read that returned fewer bytes than `ibs`; a pipe delivers those routinely | |
| truncated record | a line longer than `cbs`, cut and counted | |
| EBCDIC | IBM's 8-bit code, in which the letters are not contiguous and `a` is `0x81` | [Code pages](../../02_Characters/code_pages/README.md) |
| System V, 4.3BSD-Reno | the AT&T release of 1983 and the Berkeley release of 1990, the two ancestors the six tables are named after | [From the telegraph to Unicode](../../09_History/from_telegraph_to_unicode/README.md) |
| CP037, CP500, CP1047 | the three IBM EBCDIC pages `iconv` knows here; SAP numbers them differently again | [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) |
| parity bit | the eighth bit used as a check on a seven-bit character; `parnone` clears it | [UTF-7, and the seven-bit transport](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) |
| `swab` | swap adjacent bytes; UTF-16LE to UTF-16BE and back | [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) |
| `lcase`, `ucase` | `tolower`/`toupper` per byte; not a Unicode case mapping | [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) |
| `sync`, `noerror` | pad a short input block; continue after a read error; together, the disk-imaging idiom | |
| `sparse` | seek instead of writing a block of NULs, leaving a hole in the file | |
| `fillchar=c` | a BSD extension: the pad byte, *an ASCII character* | |
| `F_NOCACHE`, `O_SYNC` | the `iflag`/`oflag` values: bypass the cache, write synchronously | |
| `SIGINFO` | the BSD status signal (`^T` at the terminal), on which `dd` prints its counts and continues | [`tty(4)` and `stty(1)`](tty.md) |
| `b`, `k`, `m`, `g`, `w`, `x` | 512, 1024, 1024², 1024³, *bytes in an integer*, and multiplication | |

## Try it on your machine

**Which code page is inside `dd`.** Fifteen ASCII bytes chosen because the IBM pages disagree about them, then `caf` and the two bytes of `é`, through each of the six tables and through `iconv` for the three IBM pages both machines know. The input is read as bytes; `iconv` is told it is Latin-1 so that `c3 a9` is two characters, `Ã` and `©`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD dd, GNU libiconv) and ubuntu:24.04 (GNU dd 9.4, glibc iconv). Not machine-checked: no key can match both."
input   a  [  b  ]  !  |  ^  ~  \  {  }  #  @  $  sp c  a  f  c3 a9
        61 5b 62 5d 21 7c 5e 7e 5c 7b 7d 23 40 24 20 63 61 66 c3 a9
dd conv=ebcdic      81 ad 82 bd 5a 4f 9a 5f e0 c0 d0 7b 7c 5b 40 83 81 86 80 51   both machines
dd conv=ibm         81 ad 82 bd 5a 4f 5f a1 e0 c0 d0 7b 7c 5b 40 83 81 86 80 51   both machines
dd conv=oldebcdic   81 4a 82 5a 4f 6a 5f a1 e0 c0 d0 7b 7c 5b 40 83 81 86 80 51   macOS; Ubuntu: invalid conversion
dd conv=oldibm      81 ad 82 bd 5a 4f 5f a1 e0 c0 d0 7b 7c 5b 40 83 81 86 80 51   macOS; Ubuntu: invalid conversion
iconv -t IBM1047    81 ad 82 bd 5a 4f 5f a1 e0 c0 d0 7b 7c 5b 40 83 81 86 66 b4   Ubuntu; macOS has no IBM1047
iconv -t IBM500     81 4a 82 5a 4f bb 5f a1 e0 c0 d0 7b 7c 5b 40 83 81 86 66 b4   both machines
iconv -t IBM037     81 ba 82 bb 5a 4f b0 a1 e0 c0 d0 7b 7c 5b 40 83 81 86 66 b4   both machines
dd conv=ascii on 81 82 c3 a9        61 62 43 7a   ("abCz")                         both machines
conv=ebcdic then conv=ascii, café   63 61 66 c3 a9                                  both machines
```

Read the columns for `[`, `]`, `^`, `~` and `|`. `conv=ibm` matches CP1047 on all fifteen ASCII bytes; `conv=ebcdic` differs from it at `^` (`9a` against `5f`) and `~` (`5f` against `a1`); `conv=oldebcdic` is CP500 except that `|` is `6a`. CP037, the page most often meant by *EBCDIC US*, is none of them: it puts the brackets at `ba` and `bb`. Then read the last two bytes. `iconv` mapped `Ã` and `©` to `66` and `b4`, their EBCDIC code points; `dd` mapped `c3` and `a9` to `80` and `51`, which is `a9` becoming EBCDIC `z`, because its tables are seven-bit tables padded out to 256 entries, and `conv=ascii` on `c3 a9` prints `Cz`. The round trip is exact and meaningless, which is the distinction [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md) draws between a bijection and a decoding.

**`swab`.** The UTF-16LE byte order mark and a `c`, swapped.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
$ printf '\xff\xfec\x00' | dd conv=swab 2>/dev/null | xxd -p
feff0063                                     both: UTF-16BE, BOM first
$ printf 'abc' | dd conv=swab 2>&1 >/dev/null | grep -c 'odd length'
1                                            macOS reports "1 odd length swab record"; Ubuntu says nothing
```

Both write `bac`: the pair is swapped and the odd byte is copied through, which is what *ignored during swapping* turns out to mean.

**`ucase` and `lcase` are per-byte, and on this Mac per-locale.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD dd) and ubuntu:24.04 (GNU dd 9.4). Not machine-checked."
                                           macOS LC_ALL=C     macOS en_US.UTF-8    Ubuntu C and C.UTF-8
printf 'café\n'  | dd conv=ucase           434146c3a90a       434146c3a90a         434146c3a90a
printf 'CAFÉ\n'  | dd conv=lcase           636166c3890a       636166e3890a         636166c3890a
printf 'żółw 中文\n' | dd conv=ucase       (unchanged)        c5bcc3b3c5825720c4b8adc696870a   (unchanged)
printf 'ŻÓŁW 中文\n' | dd conv=lcase       (unchanged)        e5bbe393e5817720e4b8ade696870a   (unchanged)
```

In the `C` locale and on GNU, only the ASCII letters change and `é` survives as `c3 a9`. In a UTF-8 locale on this Mac, `lcase` maps the byte `c3` to `e3` and `c5` to `e5`, because to the single-byte `tolower` those are `Ã` and `Å`; `ucase` maps the lead bytes `e4` and `e6` of `中` and `文` to `c4` and `c6`. Every output in that column is invalid UTF-8 (`iconv -f UTF-8` rejects `e3 89`), and `dd` reports nothing. [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) is why no per-byte table can do this job.

**`block` and `unblock`, and the summary line.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
$ printf 'ab\ncdef\n' | dd conv=block cbs=4 | xxd -p
6162202063646566                             both: "ab  cdef", two 4-byte records, no newline
$ printf 'ab\ncdefgh\n' | dd conv=block cbs=4 2>&1 >/dev/null
0+1 records in
0+1 records out
1 truncated record                           both, word for word
8 bytes transferred in 0.000009 secs (888889 bytes/sec)      macOS
8 bytes copied, 3.8197e-05 s, 209 kB/s                       Ubuntu
$ printf 'ab  cdef' | dd conv=unblock cbs=4 2>/dev/null | xxd -p
61620a636465660a                             both: the lines come back
$ printf 'ab' | dd ibs=4 conv=sync 2>/dev/null | xxd -p
61620000                                     both; with conv=sync,block cbs=4 the pad is 2020
```

**Sizes and status.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04, bytes written by dd if=/dev/zero bs=SIZE count=1. Not machine-checked."
bs=      1b    1k    1w   2x3   1m         0x10      1M       1kB
macOS    512   1024  4    6     1048576    16        1048576  invalid
Ubuntu   512   1024  2    6     invalid    invalid   1048576  1000
$ printf 'café' | dd of=/dev/null status=none; echo exit=$?      -> exit=0 with no output, on both
```

## Where the page is dated, and what it does not say

**The page is dated May 19, 2021** and its `conv=` tables are named after AT&T System V (1983) and 4.3BSD-Reno (1990). It does not say which IBM code page any of them is, and the measurement above is the only way to find out; the answer, CP1047 for `ibm`, is not on the page and not in POSIX either. [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) is where the numbering schemes are untangled.

**It does not say the tables are seven-bit.** A byte above `0x7f` goes through the table too and comes out as an unrelated EBCDIC value; `é` in UTF-8 becomes two EBCDIC bytes that mean nothing, and `iconv -t IBM037` is the tool that would have meant something.

**It does not say what `lcase` and `ucase` fold, or that the locale matters.** Two lines, no ENVIRONMENT section, and on this Mac the answer depends on `LC_CTYPE` in a way that corrupts UTF-8. GNU's documentation is not on this machine but its behaviour is: ASCII only.

**GNU `dd` is not this page.** It refuses `oldascii`, `oldebcdic` and `oldibm`, reads `w` as 2, rejects `1m` and `0x10`, adds `conv=excl`, `conv=nocreat` and `conv=fdatasync`, and words its last line differently. `status=none` is on both, and the page documents it.

**`fillchar=c` is *an ASCII character*.** The pad byte is one byte; a fixed-width record of UTF-8 text padded with anything else would need a multibyte pad, and there is none.

## See also

- [`byteorder(3)` and `swab(3)`](byteorder.md) — the library function `conv=swab` is built on, and `htons` beside it
- [`iconv(1)` and `iconv(3)`](iconv.md) — the tool that knows the IBM pages by name, and the one to use instead of `conv=ebcdic`
- [`tr(1)`, `cut(1)`, `fold(1)`, `wc(1)` and the column tools](columns_and_characters.md) — the other tools that cut at a byte count
- [`tar(5)` and `cpio(5)`](archives.md) — the tape formats `dd` was written to read, with their own fixed-width fields
- [Code pages](../../02_Characters/code_pages/README.md) — what a 256-entry table is, and why the second half is the whole argument
- [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) — IBM's, Microsoft's and SAP's numbers for the same tables
- [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) — `conv=block cbs=` with an accent in the record
- [The bytes do not say which end](../../01_Bits_and_Bytes/which_end_comes_first/README.md) — why `swab` is a conversion and not a repair
- [Swap Bytes](../../15_Hex/swap_bytes/README.md) — the same operation in the hex editor, one value at a time
- [What the page does not say](../what_the_page_does_not_say/README.md) — the gaps above, as a method
