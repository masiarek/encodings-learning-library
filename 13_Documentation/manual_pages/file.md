# `file(1)` and `magic(5)`: the guess, and the rulebook it is not written in

**Level:** reference · for anyone who has typed `man 5 magic` looking for the rule that says `charset=utf-8`, and not found it

**One line:** `file(1)` describes three classes of test in a fixed order and `magic(5)` documents the rule language for the middle one; the answer this library cares about, the text encoding, comes from a built-in test with no rule file behind it, the page's own TODO admits as much, and the two `-e` names that switch it off each switch off a different half.

**The pages:** [`file(1)`](raw/macos/file.1.txt) (macOS, dated February 5, 2021, *documents version 5.41*) · [`magic(5)`](raw/macos/magic.5.txt) (macOS, May 9, 2021, version 5.41). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). Ubuntu 24.04 ships file 5.45 and has both pages (`man -w` finds `file.1.gz` and `magic.5.gz`), but they are not in [`raw/linux/`](raw/PROVENANCE-linux.txt); its program was measured.

## What the pages are for

`file` is one program on every Unix, from one source: Ian Darwin's 1986 rewrite of the System V command, maintained by Christos Zoulas since 1990, BSD-licensed, and versioned independently of any operating system. That is why the page opens with *This manual page documents version 5.41 of the file command* rather than a date, and why this Mac (5.41) and Ubuntu 24.04 (5.45) run the same program four minor releases apart. The section-1 page documents the command and its flags; the section-5 page documents the *file format* of its rulebook, the magic database, which on this Mac is compiled into `/usr/share/file/magic.mgc` and on Ubuntu lives at `/etc/magic:/usr/share/misc/magic`.

The library's interest is narrow. [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) asks four questions of a file, and the fourth, *what encoding is it*, has no answer in the bytes; [`file` guesses](../../06_Terminal/file_guesses/README.md) measured the guess, and [File type is four questions](../../06_Terminal/file_type_is_four_questions/README.md) sorted the mechanisms. These two pages are where the mechanism is written down, and the useful discovery is where it is not: the encoding test is code, not magic, and `magic(5)` cannot express it.

Both pages are also a small lesson in vocabulary. `file(1)` insists that its output contain one of the words *text*, *executable* or *data*, because *users depend on knowing that all the readable files in a directory have the word "text" printed*, and then, in the sentence after, complains that Berkeley once changed *shell commands text* to *shell script*. The English prose is a contract with a person, and upstream edits it between releases; the MIME form is the contract with a program.

## The page, with notes

### `file(1)`: three sets of tests, and the paragraph between two of them

```text title="man 1 file, file 5.41, macOS 26.6.2, dumped 2026-09-13"
     file tests each argument in an attempt to classify it.  There are three
     sets of tests, performed in this order: filesystem tests, magic tests,
     and language tests.  The first test that succeeds causes the file type to
     be printed.
```

Filesystem tests are `stat(2)`: empty, directory, socket, symlink. Magic tests are the database. Language tests look for *particular strings ... that can appear anywhere in the first few blocks*, `.br` for troff, `struct` for C. And then there is the paragraph the page puts between the second and third, which belongs to neither:

```text title="man 1 file, file 5.41, macOS 26.6.2, dumped 2026-09-13"
     If a file does not match any of the entries in the magic file, it is
     examined to see if it seems to be a text file.  ASCII, ISO-8859-x, non-
     ISO 8-bit extended-ASCII character sets (such as those used on Macintosh
     and IBM PC systems), UTF-8-encoded Unicode, UTF-16-encoded Unicode, and
     EBCDIC character sets can be distinguished by the different ranges and
     sequences of bytes that constitute printable text in each set.  If a file
     passes any of these tests, its character set is reported.  ASCII,
     ISO-8859-x, UTF-8, and extended-ASCII files are identified as "text"
     because they will be mostly readable on nearly any terminal; UTF-16 and
     EBCDIC are only "character data" because, while they contain text, it is
     text that will require translation before it can be read.
```

*Distinguished by the different ranges and sequences of bytes* is the whole method, and it is validation with a fallback rather than statistics: all bytes under 128 is ASCII, a valid UTF-8 sequence is UTF-8, high bytes that are not UTF-8 are *some* 8-bit table. The lesson's ladder is this paragraph rewritten as code. Two words carry weight. *Ranges* is why one byte, `85`, is counted as text and an otherwise-ASCII file with a Windows ellipsis in it reports `us-ascii`. And *reported* is honest: the character set is a verdict about the bytes examined, and the `-P` table further down the page says how many that is, `encoding 65536 max number of bytes to scan for encoding evaluation`, which is the 64 KiB window the lesson found by padding a file until the answer changed. The HISTORY section dates the test: *Altered by Eric Fischer, July, 2000, to identify character codes*.

```text title="man 1 file, file 5.41, macOS 26.6.2, dumped 2026-09-13"
     -i      If the file is a regular file, do not classify its contents.

     -I, --mime
             Causes the file command to output mime type strings rather than
             the more traditional human readable ones.  Thus it may say
             `text/plain; charset=us-ascii' rather than "ASCII text".

     --mime-type, --mime-encoding
             Like -I, but print only the specified element(s).
```

On this page `-i` means *do not look inside*, and `-I` is MIME. On GNU/Linux `-i` is `--mime` and `-I` does not exist. The page knows: its LEGACY DESCRIPTION says *The -i option displays mime type information (same as -I in conformance mode)*, and its own EXAMPLES section, inherited from upstream, runs `file -i file.c` and gets `text/x-c`, which is the *other* meaning. The library's [CONTRIBUTING finding 32](../../CONTRIBUTING.md) records the polarity: the Ubuntu mistake is loud (`invalid option`, exit 1), the macOS mistake is silent (`regular file`, exit 0). `--mime-encoding` is spelled the same on both, and is the flag every example in this library uses.

```text title="man 1 file, file 5.41, macOS 26.6.2, dumped 2026-09-13"
     -e, --exclude testname
             Exclude the test named in testname from the list of tests made to
             determine the file type.  Valid test names are:

             apptype   EMX application type (only on EMX).

             ascii     Various types of text files (this test will try to
                       guess the text encoding, irrespective of the setting of
                       the `encoding' option).

             encoding  Different text encodings for soft magic tests.

             tokens    Ignored for backwards compatibility.
             ...
             soft      Consults magic files.

             tar       Examines tar files.
```

This list is the page's map of what is a rule and what is code. `soft` is the magic database, the only test `magic(5)` describes. `ascii` is the text-encoding guess above, and the parenthesis is a warning that it does not listen to `encoding`. `encoding` is something else: `magic(5)` explains that a top-level pattern whose types are `regex` or `search` is a *text* pattern, tried only after *the file looks like text* and *its encoding is determined*, and `encoding` is that determination. The measurement below shows the two halves: `-e ascii` turns `Unicode text, UTF-8 text` into `data` and leaves `--mime-encoding` saying `utf-8`; `-e encoding` leaves the prose alone and turns `--mime-encoding` into `binary`. `tar` is the third built-in on this list that matters here, because the lesson on [archives](archives.md) says `file` recognises `tar` by `ustar` at offset 257, and it is *not* the magic database that does it.

The remaining flags are short. `-b` drops the filename. `-k` keeps going after the first match and, on this page, joins the matches with *the string `\012- '* (see the measurement: 5.41 prints a newline, 5.45 prints the six characters). `-z` looks inside compressed files. `-s` reads block and character devices that `file` otherwise refuses to open. `-m` names a magic file to use instead of the default, `-M` (on this page; not in 5.45) the same but *the default rules are not applied*, and `-C` compiles a magic file into `.mgc`.

### `magic(5)`: offset, type, test, message

```text title="man 5 magic, file 5.41, macOS 26.6.2, dumped 2026-09-13"
     The format of the source fragment files that are used to build this
     database is as follows: Each line of a fragment file specifies a test to
     be performed.  A test compares the data starting at a particular offset
     in the file with a byte value, a string or a numeric value.  If the test
     succeeds, a message is printed.
```

Four whitespace-separated fields: `offset`, `type`, `test`, `message`. The offset is a byte count, negative from the end of the file at level 0. The type says how many bytes to read and how to interpret them: `byte`, `short`, `long`, `quad` in native order, `be`- and `le`-prefixed forms for a stated byte order, `me` for the PDP-11's middle-endian, dates, floats, and then the types that read *text*:

```text title="man 5 magic, file 5.41, macOS 26.6.2, dumped 2026-09-13"
                  string          A string of bytes.  The string type
                                  specification can be optionally followed by
                                  /[WwcCtbTf]*.  The "W" flag compacts
                                  ...
                                  "c" flag specifies case insensitive
                                  matching: lower case characters in the magic
                                  match both lower and upper case characters
                                  in the target, whereas upper case characters
                                  in the magic only match upper case
                                  characters in the target.  The "C" flag
                                  ...
                                  The "t" flag forces the test to be done for
                                  text files, while the "b" flag forces the
                                  test to be done for binary files.
                  ...
                  bestring16      A two-byte unicode (UCS16) string in big-
                                  endian byte order.
                  ...
                  lestring16      A two-byte unicode (UCS16) string in little-
                                  endian byte order.
```

`string` is *a string of bytes*, compared byte for byte, and its `c` flag folds case in one direction only (lower in the rule matches either; upper in the rule matches upper), which is a byte-table notion of case, not a locale's. `bestring16` and `lestring16` are the page's whole idea of Unicode: two-byte code units, called *UCS16*, a name that predates surrogates: [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md). There is no `utf8string` type, because a UTF-8 signature is a byte string and `string` already matches it. `pstring` is a length-prefixed string with a modifier for the width and order of the length. `search/N` is a literal looked for at up to `N` positions. `regex` is *extended POSIX regular expression syntax (like egrep)*, limited to 8 KiB unless `/N` says otherwise, with `^` and `$` matching *individual lines*, and a paragraph discouraging it on performance grounds; [`re_format(7)`](patterns.md) is the syntax it means. `indirect` starts the database again at an offset read from the file.

```text title="man 5 magic, file 5.41, macOS 26.6.2, dumped 2026-09-13"
     file type.  These additional tests are introduced by one or more >
     characters preceding the offset.  The number of > on the line indicates
     the level of the test; a line with no > at the beginning is considered to
     be at level 0.  Tests are arranged in a tree-like hierarchy: if the test
     on a line at level n succeeds, all following tests at level n+1 are
     performed, and the messages printed if the tests succeed, until a line
     with level n (or less) appears.
     ...
           0      string   MZ
           >0x18  leshort  <0x40   MS-DOS executable
           >0x18  leshort  >0x3f   extended PC executable (e.g., MS Windows)
```

The `>` is an `if`: a level-0 line with an empty message matches silently, and the level-1 lines under it add the words. The MIME type is not a field but an annotation on its own line, `!:mime MIMETYPE`, *the next non-blank or comment line after the magic line*, and `!:strength` adjusts the priority `-l` lists. The measurement below writes a three-line rule for the library's own container format and watches both flags read it.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| magic number | *Some invariant identifier at a small fixed offset*; the bytes a format writes first so readers can recognise it | [A record has to say what it is](../../08_Build_Your_Own/framing_a_format/README.md) |
| filesystem tests, magic tests, language tests | `stat(2)`, the database, and keyword sniffing, in that order; the encoding guess sits between the last two and belongs to neither | [File type is four questions](../../06_Terminal/file_type_is_four_questions/README.md) |
| *text*, *executable*, *data* | The three words the prose promises to contain; *data* is the surrender | [Binary is a verdict, not a property](../../06_Terminal/binary_or_text/README.md) |
| extended-ASCII, ISO-8859-x | The 8-bit tables; `iso-8859-1` in MIME output means *high bytes that are not UTF-8*, not a positive identification | [`file` guesses](../../06_Terminal/file_guesses/README.md) |
| `-e ascii` | Switch off the text-encoding guess; the prose becomes `data` | this page, below |
| `-e encoding` | Switch off encoding determination for text-typed magic; `--mime-encoding` becomes `binary` | this page, below |
| `-P encoding 65536` | How many bytes the encoding guess reads: the 64 KiB window | [`file` guesses](../../06_Terminal/file_guesses/README.md) |
| `-i` / `-I` / `--mime` | *Do not classify* on this page; MIME on GNU/Linux; `--mime-encoding` is spelled the same everywhere | [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) |
| offset, type, test, message | The four fields of a magic line | this page, above |
| `>`, continuation level | Nesting: a line at level *n+1* runs only if the preceding level-*n* line matched | this page, above |
| `string/c`, `/C`, `/t`, `/b`, `/W`, `/w`, `/f`, `/T` | Case folding in one direction each, force text or binary classification, whitespace compaction, whole word, trim | this page, above |
| `lestring16`, `bestring16`, *UCS16* | Two-byte code units in a stated order; the page's name for what is now UTF-16 without surrogates | [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) |
| `search/N`, `regex/N`, `/l` | A literal or an ERE looked for within `N` bytes, or `N` lines with `/l` | [`re_format(7)` and `regex(3)`](patterns.md) |

## Try it on your machine

**Four small files, two versions of `file`.** The MIME encoding, the MIME type and the prose, for ASCII, UTF-8 `café`, Latin-1 `café` (`63 61 66 e9`) and UTF-16LE `café` with a BOM.

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 (file-5.41) and ubuntu:24.04 (file-5.45)."
$ for f in ascii.txt utf8.txt latin1.txt u16le.txt; do printf '%-11s %-11s %-24s %s\n' "$f" "$(file -b --mime-encoding $f)" "$(file -b --mime-type $f)" "$(file -b $f)"; done
ascii.txt   us-ascii    text/plain               ASCII text
utf8.txt    utf-8       text/plain               Unicode text, UTF-8 text
latin1.txt  iso-8859-1  text/plain               ISO-8859 text
u16le.txt   utf-16le    text/plain               Unicode text, UTF-16, little-endian text
```

Two inferences, one negative and one piece of evidence, as [`file` guesses](../../06_Terminal/file_guesses/README.md) sorts them; the last row is the only one that rests on bytes written *in* the file. Note that the MIME type is `text/plain` for all four, including the UTF-16 file the prose calls *character data* elsewhere.

**The short flags.** Same file, both machines, the swap from finding 32.

```text title="Measured 2026-09-13 — macOS 26.6.2 (file-5.41) and ubuntu:24.04 (file-5.45). Not machine-checked: the point is that they differ."
                        macOS                                     ubuntu:24.04
$ file -i utf8.txt      utf8.txt: regular file           exit 0   utf8.txt: text/plain; charset=utf-8    exit 0
$ file -I utf8.txt      utf8.txt: text/plain; charset=utf-8       file: invalid option -- 'I'            exit 1
$ file --mime utf8.txt  utf8.txt: text/plain; charset=utf-8       utf8.txt: text/plain; charset=utf-8
```

**A three-line magic file.** The library's [Tribit](../../08_Build_Your_Own/tribit/README.md) container starts with the ASCII letters `T3` and a byte saying how many padding bits the last byte carries; `café` packs to `54 33 05 e1 d8 37 40`. A rule for it, a `!:mime` line, and a level-1 line that prints the pad count:

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 (file-5.41) and ubuntu:24.04 (file-5.45) except the last line."
$ cat my.magic
0	string	T3	Tribit packed text
!:mime	application/x-tribit
>2	ubyte	x	\b, %d padding bits
$ printf 'T3\005\341\330\067\100' > cafe.tribit
$ file -m my.magic cafe.tribit
cafe.tribit: Tribit packed text, 5 padding bits
$ file -m my.magic --mime cafe.tribit
cafe.tribit: application/x-tribit; charset=binary
$ file cafe.tribit
cafe.tribit: data
$ file -m my.magic utf8.txt latin1.txt
utf8.txt:   Unicode text, UTF-8 text
latin1.txt: ISO-8859 text
$ file -M my.magic utf8.txt cafe.tribit
utf8.txt:    data                                          # macOS; ubuntu: file: invalid option -- 'M'
cafe.tribit: Tribit packed text, 5 padding bits
```

The `\b` in the message suppresses the space before the comma, as the page says; `%d` prints the byte the level-1 line read. The fourth command is the finding: with `-m` replacing the whole database, the two text files are still classified, because the encoding guess is not in any database. `-M`, which the 5.41 page documents as *like -m, except that the default rules are not applied*, does turn it off on this Mac and does not exist on 5.45.

**Which `-e` switches off which half.** One UTF-8 file, the prose and the MIME encoding, with each test excluded in turn.

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 (file-5.41) and ubuntu:24.04 (file-5.45)."
file -b                          Unicode text, UTF-8 text
file -b -e ascii                 data
file -b -e encoding              Unicode text, UTF-8 text
file -b -e soft                  Unicode text, UTF-8 text
file -b --mime-encoding          utf-8
file -b --mime-encoding -e ascii utf-8
file -b --mime-encoding -e encoding binary
```

`-e soft` removes the database and changes nothing, which is the proof that the guess is code. `-e ascii` removes the guess from the prose but the MIME encoding still says `utf-8`; `-e encoding` does the reverse. Two names, two halves of one answer, and neither the page nor the `--help` text says which is which.

**The tar test is not magic either.** A tar archive says `ustar` at byte 257; `-e tar` switches off the built-in test and the magic rule takes over with a longer message; switching off both leaves `data`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (file-5.41, bsdtar) and ubuntu:24.04 (file-5.45, GNU tar). Not machine-checked: the archives differ."
$ xxd -s 257 -l 8 t.tar            macOS: 00000101: 7573 7461 7200 3030   ustar.00      ubuntu: 00000101: 7573 7461 7220 2000   ustar  .
$ file -b t.tar                    POSIX tar archive                                      POSIX tar archive (GNU)
$ file -b -e tar t.tar             POSIX tar archive, file ._utf8.txt, mode 000644 ...    POSIX tar archive (GNU), file utf8.txt, mode 0000644 ...
$ file -b -e soft -e tar t.tar     data                                                   data
```

**`-k` on two versions.** The page says matches are joined by *the string `\012- '* and that `-r` is a no-op.

```text title="Measured 2026-09-13 — macOS 26.6.2 (file-5.41) and ubuntu:24.04 (file-5.45), through cat -vet. Not machine-checked."
$ file -k s.sh | cat -vet
  macOS:   s.sh: POSIX shell script text executable$
           - a /bin/sh script text executable$
  ubuntu:  s.sh: POSIX shell script text executable\012- a /bin/sh script, ASCII text executable$
$ file -k -r s.sh | cat -vet
  ubuntu:  s.sh: POSIX shell script text executable$
           - a /bin/sh script, ASCII text executable$
```

## Where the page is dated, and what it does not say

**`file(1)` documents 5.41 and Ubuntu runs 5.45.** Between the two, `-M` disappeared, `-k` started printing the literal `\012- ` that this page describes and 5.41 does not do, `-r` stopped being a no-op, and the prose moved the word *executable* from one noun to another. The page's FILES section says `/usr/share/file/magic.mgc`; on Ubuntu `file -v` says `/etc/magic:/usr/share/misc/magic`. Its `-i` paragraph is right about this Mac and its EXAMPLES section is right about Linux.

**The encoding test has no page.** `magic(5)` cannot express *is this valid UTF-8*, and `file(1)`'s own TODO section says so: *Some of the encoding logic is hard-coded in encoding.c and can be moved to the magic files if we had a !:charset annotation.* The text-encoding paragraph names ASCII, ISO-8859-x, extended-ASCII, UTF-8, UTF-16 and EBCDIC and gives no rule for any of them; the 64 KiB window is a number in the `-P` table; the twenty-five byte values that make a file *data* are on no page at all. The lesson measured all three.

**Neither page mentions the byte order mark.** The string `BOM` and the phrase *byte order mark* appear in neither dump (`magic(5)` says *byte order* only of its integer types). The one case where `file`'s answer is evidence rather than inference, `ff fe` or `ef bb bf` at offset 0, is a magic rule in the database and is not described in the prose: [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md).

**`magic(5)`'s Unicode is UCS-2.** `bestring16` and `lestring16` are *two-byte unicode (UCS16)* strings; nothing on the page can name a character above `U+FFFF`, and there is no UTF-8 string type because none is needed. `string/c` folds case by byte table, and `regex` runs over bytes with ERE syntax, so a rule cannot ask for `[[:alpha:]]` in the file's encoding, only in the locale's.

**Neither page defines *text*.** `file(1)` says *only printing characters and a few common control characters*; which control characters, and whether a NUL is one of them, is not on the page, and the lesson's answer, twenty-five byte values with the NUL only one of them, differs from `grep`'s rule and from `git`'s: [Binary is a verdict, not a property](../../06_Terminal/binary_or_text/README.md).

## See also

- [`hexdump(1)`, `od(1)`, `xxd(1)` and `strings(1)`](dump_tools.md) — the tools that show the bytes `file` guessed from
- [`tar(5)` and `cpio(5)`](archives.md) — `ustar` at offset 257, the signature both a magic rule and a built-in test look for
- [`re_format(7)` and `regex(3)`](patterns.md) — the ERE syntax `magic(5)`'s `regex` type means
- [`file` guesses](../../06_Terminal/file_guesses/README.md) — the encoding ladder measured: the window, the one byte above 127, the twenty-five that mean *data*
- [File type is four questions](../../06_Terminal/file_type_is_four_questions/README.md) — what is actually inside the magic database
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — the three shapes of `file`'s answer, beside the dumps
- [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) — why a format should start with something `magic(5)` can match
- [A page has a date](../a_page_has_a_date/README.md) — a page that documents 5.41 on a machine, and 5.45 on the other
- [What the page does not say](../what_the_page_does_not_say/README.md) — the encoding test, which no page describes
