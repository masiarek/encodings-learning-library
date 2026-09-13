# `diff(1)`, `cmp(1)`, `cksum(1)` and `md5(1)`: four definitions of the same

**Level:** reference · for anyone who has typed `man cmp` to find out whether `char 4` means a character, and `man cksum` to find out what `sum` is

**One line:** Four pages, four meanings of *the same*: `diff` compares lines and keeps a private rule for when to stop, `cmp` compares bytes and calls them `char` because POSIX wrote the message, `cksum` reduces a file to a CRC that both machines compute identically, and `md5` is the honest way to say two files hold the same bytes without showing either, which is why two spellings of `café` that draw the same get two different hashes.

**The pages:** [`diff(1)`](raw/macos/diff.1.txt) (macOS, dated January 7, 2025; FreeBSD's page for the BSD `diff` written by Todd Miller of OpenBSD) · [`cmp(1)`](raw/macos/cmp.1.txt) (macOS, September 23, 2021) · [`cksum(1)`](raw/macos/cksum.1.txt) (macOS, April 28, 1995; also `sum`) · [`md5(1)`](raw/macos/md5.1.txt) (macOS, February 13, 2024; also `sha1`, `sha256`, `sha512` and the `-sum` names). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). Ubuntu 24.04 runs GNU diffutils 3.10 and coreutils 9.4; their pages exist but are not in [`raw/linux/`](raw/PROVENANCE-linux.txt).

## What the pages are for

All four are section-1 commands that answer *are these the same* and the pages are mostly about the format of the answer. The `diff(1)` page is the longest and the newest, and its HISTORY section is the reason it reads differently from the `diff` page a Linux user knows: *The diff implementation used in FreeBSD was GNU diff until FreeBSD 11.4. This was replaced in FreeBSD 12.0 by a BSD-licensed implementation written by Todd Miller. Some GNUisms were lost in the process.* Apple ships that implementation; `diff --version` on this Mac says *Apple diff (based on FreeBSD diff)*. The page documents three algorithms by name, `myers`, `patience` and `stone`, and cites Hunt and McIlroy's 1976 Bell Labs report for the last of them.

`cmp(1)` is from Version 1 AT&T UNIX and its page is a hundred lines. `cksum(1)` is the oldest page in the five families this library annotates, dated 1995, and it is the only one that prints its algorithm: the generating polynomial of the POSIX CRC, in full, with the procedure. `md5(1)` is FreeBSD's 2024 page for one program with a dozen names, half of them in BSD mode and half in GNU mode, and it documents both option sets because `/sbin/md5sum` and `/sbin/md5` on this Mac are the same binary.

The library's [`diff` compares lines, `cmp` compares bytes, neither compares text](../../11_Tools/diff_and_cmp/README.md) is the lesson these pages sit under. What that page measured, these pages *say*, and the interesting places are where they say it in a word from 1976.

## The page, with notes

### `diff(1)`: `-a`, and the rule that is not on the page

```text title="man 1 diff, macOS 26.6.2, dumped 2026-09-13"
     -a --text
             Treat all files as ASCII text.  Normally diff will simply print
             "Binary files ... differ" if files contain binary characters.
             Use of this option forces diff to produce a diff.
     ...
     -b --ignore-space-change
             Causes trailing blanks (spaces and tabs) to be ignored, and other
             strings of blanks to compare equal.
     ...
     -i --ignore-case
             Ignores the case of letters.  E.g., "A" will compare equal to
             "a".
     ...
     --strip-trailing-cr
             strip carriage return on input files
```

*Binary characters* is not defined anywhere on the page, and the two implementations define it differently: both stop at a NUL, but BSD looks for one anywhere in the file and GNU only in the first block it reads, so a log with a stray NUL near the end is *Binary files ... differ* on this Mac and an ordinary line diff on Ubuntu. That is the library's [CONTRIBUTING finding 17](../../CONTRIBUTING.md), and `-a` is the flag that makes both behave. *Blanks (spaces and tabs)* is the page's whole definition of whitespace, so `-b` and `-w` know nothing of `U+00A0 NO-BREAK SPACE`; the lesson measured `-w` leaving it alone. *The case of letters* means ASCII letters: the measurement below shows `-i` treating `CAFÉ` and `café` as different in every locale on both machines. `--strip-trailing-cr` is one line on this page and it is the right one line: it redefines *the same* for one run, which is the correct answer when a Windows checkout meets a Unix one and the wrong answer when you wanted to know why the checksum changed: [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md).

The page's `-I pattern` takes an *extended regular expression* and points at [`re_format(7)`](patterns.md); its `-x pattern` excludes files by `fnmatch(3)`. Its EXIT STATUS is the contract a script should read, `0` same, `1` different, `>1` trouble, and the lesson has the `if diff a b; then` bug that follows from not testing for 2.

### `cmp(1)`: *char* means byte

```text title="man 1 cmp, macOS 26.6.2, dumped 2026-09-13"
     The cmp utility compares two files of any type and writes the results to
     the standard output.  By default, cmp is silent if the files are the
     same; if they differ, the byte and line number at which the first
     difference occurred is reported.

     Bytes and lines are numbered beginning with one.
     ...
     -l, --verbose
             Print the byte number (decimal) and the differing byte values
             (octal) for each difference.
     ...
     -x      Like -l but prints in hexadecimal and using zero as index for the
             first byte in the files.
```

The page says *byte* on seven of its lines and never *char*, and the program prints `char 4`. The word in the message is POSIX's, and this Mac's `cmp` prints it in every locale; GNU `cmp` has printed *byte* instead *outside the POSIX locale* since diffutils 2.8 (its NEWS says so), so under `LC_ALL=C` the two agree word for word and under a UTF-8 locale they do not. Either way the number is a byte offset: `café` and `cafe` differ at *char 4*, which is the first byte of `é` against the `e`, and character 4 is `é` in one file and `e` in the other. `-l` lists every differing byte in octal, and the offset column is padded on BSD and not on GNU, [finding 18](../../CONTRIBUTING.md). `-x` is the BSD extension the page lists under STANDARDS; GNU rejects it. `-s` is the portable spelling, because the exit status is identical everywhere and the message is not.

### `cksum(1)`: one CRC, two historic sums

```text title="man 1 cksum, macOS 26.6.2, dumped 2026-09-13"
     The sum utility is identical to the cksum utility, except that it
     defaults to using historic algorithm 1, as described below.  It is
     provided for compatibility only.
     ...
     -o      Use historic algorithms instead of the (superior) default one.

             Algorithm 1 is the algorithm used by historic BSD systems as the
             sum(1) algorithm and by historic AT&T System V UNIX systems as
             the sum(1) algorithm when using the -r option.  This is a 16-bit
             checksum, with a right rotation before each addition; overflow is
             discarded.

             Algorithm 2 is the algorithm used by historic AT&T System V UNIX
             systems as the default sum(1) algorithm.  This is a 32-bit
             checksum, and is defined as follows:
             ...
             Algorithm 3 is what is commonly called the `32bit CRC' algorithm.
             This is a 32-bit checksum.

             Both algorithm 1 and 2 write to the standard output the same
             fields as the default algorithm except that the size of the file
             in bytes is replaced with the size of the file in blocks.  For
             historic reasons, the block size is 1024 for algorithm 1 and 512
             for algorithm 2.
```

Three fields: the checksum, the *number of octets* (or blocks, for the old algorithms), the name. The default is the POSIX CRC, and the page prints `G(x)` and the procedure, including the detail that the file's *length* is appended, least significant octet first, before division; that is why `cksum` of an empty file is not zero. GNU coreutils' `cksum` computes the same number, as the measurement shows. The two historic algorithms are the BSD `sum` (`-o 1`, `sum -r` on GNU, 1024-byte blocks) and the System V `sum` (`-o 2`, `sum -s` on GNU, 512-byte blocks), and `sum` on both machines defaults to the BSD one. *Algorithm 3* is a third thing: the page says *the 32bit CRC* as if it were the default, but it prints a different number, and the measurement identifies it as the CRC-32 that `zip`, `gzip` and `zlib.crc32` use. Same name, two polynomial conventions, two answers.

### `md5(1)`: `-s`, `-r`, `-q`, `-c`, and the `-sum` names

```text title="man 1 md5, macOS 26.6.2, dumped 2026-09-13"
     -c string, --check=string
             Compare the digest of the file against this string.  If combined
             ...
     -q, --quiet
             Quiet mode -- only the checksum is printed out.  Overrides the -r
             or --reverse option.
     -r, --reverse
             Reverses the format of the output.  This helps with visual diffs.
     -s string, --string=string
             Print a checksum of the given string.
     ...
     This is almost but not quite identical to the output from GNU mode:
           $ md5sum /boot/loader.conf /etc/rc.conf
           ada5f60f23af88ff95b8091d6d67bef6  /boot/loader.conf
     Note the two spaces between hash and file name.
```

Two option sets on one page, selected by the program's name: *BSD mode ... when the program is invoked with a name that does not end in "sum"*, GNU mode otherwise. `-c` is the sharpest split: in BSD mode it takes a *string* and compares one file against it (exit 2 on failure), in GNU mode it takes a *digest file* and checks every line in it. `-r` puts the hash first, *almost but not quite* GNU's format, one space short. `-s` hashes a string from the command line, which means the bytes the shell handed over: `md5 -s café` on this Mac and `printf café | md5sum` on Ubuntu give the same digest, because both hashed `63 61 66 c3 a9`. The page's DESCRIPTION dates itself, *As of 2017-03-02, there is no publicly known method to reverse either algorithm*, and recommends SHA-512 for new work. What none of this changes is why the library reaches for a hash: it answers *the same bytes* without printing them, and a terminal that draws `c3 a9` and `65 cc 81` identically cannot be trusted to show the difference a hash will: [Normalization](../../04_Python/normalization/README.md).

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| line | The bytes between two `0a`s; the unit `diff` compares, with no idea what they encode | [`diff` compares lines, `cmp` compares bytes](../../11_Tools/diff_and_cmp/README.md) |
| `XXaYY`, `XXdYY`, `XXcYY` | The default output: `ed(1)` commands that turn file1 into file2 | [`diff(1)`](raw/macos/diff.1.txt) |
| context diff, unified diff, hunk | `-c` and `-u`: changes shown with lines around them; a hunk is one such group | [`diff(1)`](raw/macos/diff.1.txt) |
| `myers`, `patience`, `stone` | Three ways to find the longest common subsequence; `stone` is Hunt–McIlroy from 1976 | [`diff(1)`](raw/macos/diff.1.txt) |
| *binary characters* | Undefined on the page; a NUL in practice, anywhere on BSD and in the first block on GNU | [Binary is a verdict, not a property](../../06_Terminal/binary_or_text/README.md) |
| blanks | Spaces and tabs, and nothing else; what `-b` and `-w` ignore | [`diff` compares lines, `cmp` compares bytes](../../11_Tools/diff_and_cmp/README.md) |
| `\ No newline at end of file` | `diff`'s notation for a last line without `0a`; `cmp` reports it as an early EOF on stderr | [The trailing newline](../../06_Terminal/trailing_newline/README.md) |
| `char` (in `cmp`'s message) | POSIX's word for a byte offset, 1-based; the page itself says *byte* | [`cmp` in POSIX ↗](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/cmp.html) |
| octal (in `cmp -l`) | The two differing byte values, in base 8: `303` is `c3` | [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| SI size suffixes, `expand_number(3)` | `k`, `m`, `g` on `cmp`'s skip arguments, powers of two despite the name; the page's BUGS says so | [`dd(1)`](dd.md) |
| CRC, generating polynomial `G(x)` | Cyclic redundancy check: the file as a polynomial over GF(2), divided, the remainder kept | [A record has to say whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) |
| ISO 8802-3: 1989 | Ethernet; the standard the polynomial comes from | [A record has to say whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) |
| octet | A byte of eight bits; the page's second field | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| historic algorithm 1, 2, 3 | BSD `sum`, System V `sum`, and the CRC-32 of `zip` and `gzip`; blocks of 1024, 512 | this page, below |
| message digest, fingerprint | A fixed-size number from arbitrary input, with collisions infeasible to construct; MD5 no longer qualifies | [Collisions by design](../../12_Adversarial/collisions_by_design/README.md) |
| BSD format, GNU format | `MD5 (f) = hash` against `hash  f`; `md5 -r` is one space away from the second; `--tag` asks GNU for the first | this page, below |
| `-c` (two meanings) | A digest string to compare against, or a digest file to check, by the program's name | this page, above |
| `-p`, `--passthrough` | Copy stdin to stdout and append the hash: a checksum on a pipe | [`md5(1)`](raw/macos/md5.1.txt) |

## Try it on your machine

**`cmp` on `café` and `cafe`.** The first is six bytes, the second five.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD cmp) and ubuntu:24.04 (GNU diffutils 3.10). Not machine-checked: the wording is the finding."
                              macOS                                             ubuntu:24.04
$ cmp cafe_utf8.txt cafe.txt  cafe_utf8.txt cafe.txt differ: char 4, line 1     cafe_utf8.txt cafe.txt differ: byte 4, line 1   (LANG=C.UTF-8)
$ LC_ALL=C cmp ...            cafe_utf8.txt cafe.txt differ: char 4, line 1     cafe_utf8.txt cafe.txt differ: char 4, line 1
$ cmp -l ...  (stdout)             4 303 145                                    4 303 145
                                   5 251  12                                    5 251  12
              (stderr)        cmp: EOF on cafe.txt                              cmp: EOF on cafe.txt after byte 5
$ cmp -b ...                  ... differ: char 4, line 1 is 303 <c3> 145 e      ... differ: byte 4, line 1 is 303 M-C 145 e
$ cmp -x ...                  00000003 c3 65                                    cmp: invalid option -- 'x'
                              00000004 a9 0a
```

`303` is `c3`, `145` is `e`, `12` is the newline that the shorter file reaches first. `-b` prints the byte as a character too, and the two builds draw `c3` differently: BSD writes the raw byte, GNU writes `M-C`. `-x` counts from zero and prints hex, and is the one flag here Ubuntu does not have.

**`diff` and the two flags that redefine *the same*.**

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 and ubuntu:24.04."
$ printf 'one\r\ntwo\r\n' > dos.txt; printf 'one\ntwo\n' > unix.txt
$ diff dos.txt unix.txt | cat -vet            # exit 1
1,2c1,2$
< one^M$
< two^M$
---$
> one$
> two$
$ diff --strip-trailing-cr dos.txt unix.txt   # exit 0
$ printf 'a\000b\n' > n1; printf 'a\000c\n' > n2
$ diff n1 n2                                  # exit 1
Binary files n1 and n2 differ
$ diff -a n1 n2 | cat -v                      # exit 1
1c1
< a^@b
---
> a^@c
$ diff -b t1 t2        # 'a<tab>b  ' against 'a    b'     exit 0
$ diff -i up.txt cafe_utf8.txt                # CAFÉ against café: exit 1 under LC_ALL=C and under a UTF-8 locale, on both
$ diff -i up2.txt cafe.txt                    # Cafe against cafe:  exit 0
```

The NUL is at byte 2 here, where the two implementations agree; the lesson has the file where they do not. `-i` folded `C` to `c` and left `É` alone in every locale, so *the case of letters* on this page means the twenty-six.

**`cksum`, `sum`, and the three algorithms.** One six-byte file, every spelling.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD cksum) and ubuntu:24.04 (GNU coreutils 9.4). Not machine-checked: the flags differ, the numbers do not."
                            macOS                        ubuntu:24.04
$ cksum cafe_utf8.txt       2581856615 6 cafe_utf8.txt   2581856615 6 cafe_utf8.txt
$ sum cafe_utf8.txt         10405 1 cafe_utf8.txt        10405     1 cafe_utf8.txt
$ cksum -o 1 / sum -r       10405 1 cafe_utf8.txt        10405     1 cafe_utf8.txt
$ cksum -o 2 / sum -s       672 1 cafe_utf8.txt          672 1 cafe_utf8.txt
$ cksum -o 3 / cksum -a crc 2302995666 6 cafe_utf8.txt   2581856615 6 cafe_utf8.txt
$ python3 -c 'import zlib; print(zlib.crc32(open("cafe_utf8.txt","rb").read()))'
                            2302995666                   2302995666
```

The POSIX CRC is the same number on both machines, which is the whole point of a standard checksum. `sum` is the same number on both because both default to the BSD algorithm. The last two rows are the page's *Algorithm 3*: it is not the default CRC but the other one, `zlib.crc32`, and GNU has no spelling for it at all; GNU's `-a crc` is the default again.

**`md5 -s` against `md5sum`, and two spellings of one word.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (/sbin/md5, /sbin/md5sum) and ubuntu:24.04 (coreutils 9.4). Not machine-checked: one machine has md5 and one does not."
                                          macOS                                                  ubuntu:24.04
$ md5 -s café                             07117fe4a1ebd544965dc19573183da2                       md5: command not found
$ printf 'café' | md5sum                  07117fe4a1ebd544965dc19573183da2  -                    07117fe4a1ebd544965dc19573183da2  -
$ md5 cafe_utf8.txt                       MD5 (cafe_utf8.txt) = 6e99834b7c3e3fd53529a5489725d7e8
$ md5 -r cafe_utf8.txt                    6e99834b7c3e3fd53529a5489725d7e8 cafe_utf8.txt
$ md5sum cafe_utf8.txt                    6e99834b7c3e3fd53529a5489725d7e8  cafe_utf8.txt         6e99834b7c3e3fd53529a5489725d7e8  cafe_utf8.txt
$ md5sum --tag cafe_utf8.txt              MD5 (cafe_utf8.txt) = 6e99834b7c3e3fd53529a5489725d7e8    MD5 (cafe_utf8.txt) = 6e99834b7c3e3fd53529a5489725d7e8
$ md5 -c 0c4a...c0c1 cafe_utf8.txt        MD5 (cafe_utf8.txt) = 6e99834b... [ Failed ]   exit 2
$ md5sum -c digest   (a BSD-format line)  cafe_utf8.txt: OK   exit 0                              cafe_utf8.txt: OK   exit 0
$ md5sum cafe_utf8.txt nfd.txt            6e99834b7c3e3fd53529a5489725d7e8  cafe_utf8.txt         (identical)
                                          a16ca62b084a682c2fed893d70768146  nfd.txt
```

The first two rows are one hash: `md5 -s` was handed the five bytes `63 61 66 c3 a9` by the shell and `md5sum` read them from a pipe. The last row is the reason for the family. `nfd.txt` is `cafe` with `U+0301 COMBINING ACUTE ACCENT`, seven bytes that draw as `café`; `diff` prints two identical-looking lines and `cmp` says *char 4*, and only the hash makes the difference visible without asking you to trust the terminal.

## Where the page is dated, and what it does not say

**`diff(1)` is dated January 7, 2025 and is not the GNU page.** A script written against GNU `diff`'s long options may find them missing here; the SYNOPSIS lists what survived, and `--speed-large-files` is documented as a *stub option for compatibility with GNU diff*. The binary rule is not on the page, and the two implementations disagree about it. The page never says *locale*, *byte* or *UTF*; its whole idea of text is *ASCII text* under `-a`, and its whitespace and case are ASCII's.

**`cmp(1)` is dated September 23, 2021** and says *byte* where its program prints `char`. The GNU page, not dumped, documents `--ignore-initial` and `--bytes` under the same names, and its program prints `byte` unless the locale is `C` or `POSIX`; a script that greps `cmp`'s message will find the word depends on `LANG`. `-x` is BSD-only and `-z` is too.

**`cksum(1)` is dated April 28, 1995**, the oldest page here, and it is still exactly right about the number `cksum` prints. It is wrong, or at least loose, about *Algorithm 3*: *the 32bit CRC* names a different polynomial convention from the default, and the page does not say so. GNU coreutils 9.4's `cksum` has grown `-a` with `md5`, `sha1`, `sha256`, `blake2b` and more, so on Ubuntu `cksum` is a front for every digest on the `md5` page; none of that is on this page or in this binary.

**`md5(1)` is dated February 13, 2024** and carries its own date inside: *As of 2017-03-02*. It documents the `-sum` names, and this Mac has them in `/sbin`, which is not where a Linux hand would look. It says the BSD `-c` *is not yet useful if multiple files are specified*, which is honest. It does not say that a hash compares bytes and not text, because it does not need to; that is the reason this library uses one.

**None of the four pages mentions an encoding.** *UTF*, *Unicode* and *locale* appear on none of them. That is correct: these tools compare and summarise bytes, and the pages are right to describe them that way. The trap is on the reading end, where *char*, *letters* and *text* sound like they were about characters.

## See also

- [`hexdump(1)`, `od(1)`, `xxd(1)` and `strings(1)`](dump_tools.md) — how to see the bytes `cmp -l` numbered
- [`cat(1)`, `cut(1)` and the line tools](lines_and_fields.md) — `cat -vet`, which is how a CRLF diff can be shown at all
- [`file(1)` and `magic(5)`](file.md) — a third private definition of *binary*
- [`bintrans(1)`](binary_to_text.md) — the other family where the page says *GNU compatible* and the flags disagree
- [`diff` compares lines, `cmp` compares bytes, neither compares text](../../11_Tools/diff_and_cmp/README.md) — the four questions that all sound like *are these the same file*
- [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) — what `--strip-trailing-cr` is for, and what it hides
- [Normalization](../../04_Python/normalization/README.md) — `c3 a9` against `65 cc 81`, the pair the hash tells apart
- [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) — a CRC as the third field of a record
- [A page has a date](../a_page_has_a_date/README.md) — a 1995 page that is still right about its number
- [What the page does not say](../what_the_page_does_not_say/README.md) — *binary characters*, undefined on the page that depends on them
