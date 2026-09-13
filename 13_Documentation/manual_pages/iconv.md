# `iconv(1)` and `iconv(3)`: two pages that promise two different things when a character cannot be converted

**Level:** reference · for anyone who has typed `iconv -f X -t Y` and wanted to know what the page promises about the byte it could not convert

**One line:** The BSD and GNU pages document one POSIX interface and disagree on the only question that matters in practice, what happens to a character the target cannot hold: BSD's page promises a `?` and continues, GNU's promises to stop unless you append `//TRANSLIT` or `//IGNORE`, and this Mac's `iconv` does a third thing that only the `BUGS` section of `iconvctl(3)` admits to: it transliterates without being asked, turning `Ł` into `L` with exit 0, and stops or substitutes depending on the target for the characters it has no look-alike for.

**The pages:** [`iconv(1)`](raw/macos/iconv.1.txt) (macOS, dated October 22, 2009, from NetBSD's Citrus project) · [`iconv(3)`](raw/macos/iconv.3.txt) (macOS, August 4, 2014) · [`iconvctl(3)`](raw/macos/iconvctl.3.txt) (macOS, November 25, 2009) · [`iconvlist(3)`](raw/macos/iconvlist.3.txt) (macOS, February 23, 2023) · [`iconv(1)`](raw/linux/iconv.1.txt) (Linux man-pages 6.7, 2024-01-28) · [`iconv(3)`](raw/linux/iconv.3.txt) (Linux man-pages 6.7, 2023-10-31) · [`iconv_open(3)`](raw/linux/iconv_open.3.txt) (Linux man-pages 6.7, 2023-10-31). Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

`iconv` is the other conversion API. The [`multibyte(3)`](multibyte.md) family converts between bytes and `wchar_t` under whatever table the locale names; `iconv` converts bytes to bytes and takes *both* table names as arguments, so it is the one to reach for when the file is not in your locale's encoding, which is the usual case. The command in section 1 wraps the three functions in section 3, `iconv_open`, `iconv` and `iconv_close`, and POSIX specifies all four. It does not specify what the names of the codesets are, what happens to a character that has no place in the target, or whether `//TRANSLIT` means anything, and that is where the two implementations and their two pages part company.

There are two `iconv`s in common use. Ubuntu's is glibc's; this Mac's is the Citrus Project's, whose copyright line is 2003, which *first appeared in NetBSD 2.0, and made its appearance in FreeBSD 9.0*, as the command's `HISTORY` section says, and came to macOS from there. They are separate code with separate tables, and the library's [`iconv`](../../06_Terminal/iconv/README.md) lesson and five of the measured findings in [CONTRIBUTING](../../CONTRIBUTING.md) are about the places the two disagree. This page is about what each *page* says, so that you can tell a documented difference from an undocumented one.

## The page, with notes

### `iconv(1)`, BSD: three flags and a count

```text title="man 1 iconv, macOS 26.6.2, dumped 2026-09-13"
     -c    Prevent output of any invalid characters.  By default, iconv
           outputs an "invalid character" specified by the to_name codeset
           when it encounts a character which is valid in the from_name
           codeset but does not have a corresponding character in the to_name
           codeset.
     ...
     -s    Silent.  By default, iconv outputs the number of "invalid
           characters" to standard error if they exist.  This option prevents
           this behaviour.
```

The whole BSD model is in the description of `-c`. A character that is *valid in the source but has no place in the target* is not an error: the program writes the target's *invalid character*, which for ASCII is `?`, carries on, counts, and prints the count to stderr at the end unless `-s` silences it. Refusing is not on offer; `-c` is the option to *drop* rather than substitute. The experiments below find this binary doing three different things depending on the target codeset, only one of which is the paragraph's, so read it as the design and not as a description of the machine.

Note what is *not* here. There is no `//TRANSLIT`, no `//IGNORE`, no `-o`, and `-l` is described in a sentence that hides a real fact: *not all combinations of from_name and to_name are valid*. GNU's page says the opposite of that, *all combinations of the listed values are supported*. The library's [What the page does not say](../what_the_page_does_not_say/README.md) found that this Mac's `iconv` accepts `//TRANSLIT` while no page on the machine mentions it; the pages below are the ones on the other machine that do.

### `iconv(3)`, BSD: the four pointers and the two outcomes

```text title="man 3 iconv, macOS 26.6.2, dumped 2026-09-13"
     If the string pointed to by *src contains a byte sequence which is not a
     valid character in the source codeset, the conversion stops just after
     the last successful conversion.  If the output buffer is too small to
     store the converted character, the conversion also stops in the same way.
     In these cases, the values pointed to by src, srcleft, dst, and dstleft
     are updated to the state just after the last successful conversion.

     If the string pointed to by *src contains a character which is valid
     under the source codeset but can not be converted to the destination
     codeset, the character is replaced by an "invalid character" which
     depends on the destination codeset, e.g., `?', and the conversion is
     continued.  iconv() returns the number of such "invalid conversions".
```

Two paragraphs, two kinds of failure, and this is the distinction every converter has to make. *Not a valid character in the source codeset* is a decode error: the bytes are not text under the table you claimed, and [`mbrtowc(3)`](multibyte.md) calls it `EILSEQ`. *Valid under the source but cannot be converted* is an encode error: the character exists and the target has no number for it, which is `UnicodeEncodeError` in Python. The page says the first stops and the second substitutes. The measured behaviour on this Mac is a third policy that this page does not mention, transliteration, plus both of the page's policies applied by target rather than by kind of failure; the matrix below has it.

The four in-out pointers, `src`, `srcleft`, `dst`, `dstleft`, are the API's way of saying *where I stopped*, so that the caller can refill a buffer and continue. That is the same resumability the restartable multibyte functions get from `mbstate_t`, done with pointer arithmetic, and it is why a correct call to `iconv(3)` is a loop rather than a line. The `src == NULL` case, which *places stateful codesets into their initial state* and may write a closing shift sequence, is the flush at the end of that loop.

```text title="man 3 iconv, macOS 26.6.2, dumped 2026-09-13"
     The __iconv() function works just like iconv() but if iconv() fails, the
     invalid character count is lost there.  This is a not bug rather a
     limitation of IEEE Std 1003.1-2008 ("POSIX.1"), so __iconv() is provided
     as an alternative but non-standard interface.  It also has a flags
     argument, where currently the following flags can be passed:

     __ICONV_F_HIDE_INVALID
           Skip invalid characters, instead of returning with an error.
```

POSIX's `iconv` returns either a count of substitutions or `(size_t)-1`, and cannot do both, so a conversion that substituted twice and then hit a decode error loses the two. The BSD page documents the private function that fixes it, and the flag behind `-c`. `iconv_open_into`, the other extension on the page, is a GNU-compatible way to avoid a heap allocation, and the page marks both as non-standard.

### `iconvctl(3)` and `iconvlist(3)`: the control panel, and a bug the page admits

```text title="man 3 iconvctl, macOS 26.6.2, dumped 2026-09-13"
     ICONV_TRIVIALP
             In this case argument is an int * variable, which is set to 1 if
             the encoding is trivial one, i.e.  the input and output encodings
             are the same.  Otherwise, the variable will be 0.

     ICONV_GET_TRANSLITERATE
             Determines if transliteration is enabled.
     ...
BUGS
     Transliteration is enabled in this implementation by default, so it is
     impossible by design to turn it off.  Accordingly, trying to turn it off
     will always fail and -1 will be returned.  Getting the transliteration
     state will always succeed and indicate that it is turned on, though.
```

`iconvctl` is GNU libiconv's control interface, adopted *for compatibility's sake* as the page says, and its request list is a menu of every policy a converter can have: substitute or not (`ICONV_SET_DISCARD_ILSEQ`), transliterate or not, treat unconvertible as an error or not (`ICONV_SET_ILSEQ_INVALID`), and callbacks for both the success and the failure path. The word *trivial* is worth remembering: a conversion whose source and target codesets are the same, which turns out to be the one path on this Mac that writes a `?` for an *invalid* byte. And the `BUGS` section is the most important paragraph in the family, because it is the only place on the machine that describes what the binary does: *transliteration is enabled in this implementation by default, so it is impossible by design to turn it off.* That sentence, and not `iconv(3)`'s two paragraphs, predicts the matrix below, where `Ł` silently becomes `L`. `iconvlist` is the C form of `iconv -l`, a callback per group of aliases, which is how the lesson page got its count of 215 groups and 873 names.

### `iconv(1)` and `iconv_open(3)`, GNU: the two suffixes, documented

```text title="man 1 iconv, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
              If  the string //IGNORE is appended to to-encoding, characters
              that cannot be converted are discarded and an error is printed
              after conversion.

              If the string //TRANSLIT is appended to  to-encoding,  charac‐
              ters being converted are transliterated when needed and possi‐
              ble.   This  means that when a character cannot be represented
              in the target character set, it can  be  approximated  through
              one  or  several  similar looking characters.  Characters that
              are  outside  of  the  target  character  set  and  cannot  be
              transliterated  are  replaced  with a question mark (?) in the
              output.
```

Here they are. The two suffixes the library found undocumented on the Mac are documented on Ubuntu, on the command's page and again on `iconv_open(3)`, which adds that they are *GNU C library and GNU libiconv* features and not POSIX. Note the exact wording of `//IGNORE`: *an error is printed after conversion*. That is a promise that the exit status will be nonzero even though every convertible character was written, and the experiment confirms it. The page's own example, `echo abc ß α € àḃç | iconv -f UTF-8 -t ASCII//TRANSLIT` giving `abc ss ? EUR abc`, is the whole feature in one line: `ß` has an approximation, `α` does not, `€` becomes a word.

```text title="man 3 iconv, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       •  A  multibyte sequence is encountered that is valid but that cannot
          be translated to the character encoding of the output.  This  con‐
          dition  depends  on  the  implementation and on the conversion de‐
          scriptor.  In the GNU C library and GNU libiconv, if cd  was  cre‐
          ated  without the suffix //TRANSLIT or //IGNORE, the conversion is
          strict: lossy conversions produce this condition.  If  the  suffix
          //TRANSLIT was specified, transliteration can avoid this condition
          in some cases.  In the musl C library, this condition cannot occur
          because  a  conversion  to  '*'  is  used  as  a fallback.  In the
          FreeBSD, NetBSD, and Solaris implementations of iconv(), this con‐
          dition cannot occur either, because a conversion to '?' is used as
          a fallback.
```

The GNU page does something no BSD page does: it names the other implementations and says how each answers the question. Four libraries, three policies: GNU is strict, musl writes `*`, and the BSDs and Solaris write `?`. That sentence about FreeBSD is [finding 29](../../CONTRIBUTING.md) of this library, measured by hand on 2026-09-07, sitting in a man page on the other machine. It is also, as the next section shows, only true of this Mac's binary in the trivial case.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| codeset | The page's word for an encoding, from POSIX; `charset` in a MIME header and `encoding` in Python name the same thing | [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) |
| `from_name`, `to_name` / `fromcode`, `tocode` | The two table names. Note the argument order of `iconv_open`: *target first*, then source, the reverse of the command line | [`iconv`](../../06_Terminal/iconv/README.md) |
| *invalid character* (BSD) | The target codeset's stand-in for a character it cannot hold, `?` for ASCII; what Python calls `errors='replace'` | [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md) |
| *invalid conversions* | The count `iconv(3)` returns on success: how many substitutions it made; the number `iconv(1)` prints to stderr unless `-s` | |
| *not a valid character in the source codeset* | A decode error: the input bytes are not text under the source table. `EILSEQ`, *Illegal byte sequence* | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| *valid ... but can not be converted* | An encode error: the character exists and the target has no number for it, as `€` in Latin-1 | [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) |
| `//TRANSLIT` | GNU suffix: approximate an unconvertible character with one or more similar-looking ones from the locale's table. Accepted and undocumented on the Mac | [What the page does not say](../what_the_page_does_not_say/README.md) |
| `//IGNORE` | GNU suffix: drop unconvertible characters, and still exit nonzero | [What the page does not say](../what_the_page_does_not_say/README.md) |
| transliteration | Replacing a character by a spelling of it in the target's alphabet, `ß` as `ss`, `€` as `EUR`; a table, per locale, and not accent-stripping | [Preparing a string](../../02_Characters/preparing_a_string/README.md) |
| stateful codeset, shift sequence, initial state | An encoding such as ISO-2022-JP whose bytes switch between sets; `iconv(cd, NULL, ...)` writes the sequence that switches back | [`multibyte(3)`](multibyte.md) |
| conversion descriptor, `iconv_t` | The handle `iconv_open` returns: the two tables plus the current shift state | |
| `E2BIG` | The output buffer is full; refill and call again from where the pointers stopped | |
| `EILSEQ` | Illegal byte sequence: a decode error, or on GNU without a suffix an encode error too | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `EINVAL` | On `iconv_open`, no such converter; on `iconv`, the input ends mid-character | |
| *trivial* conversion, `ICONV_TRIVIALP` | Source and target are the same codeset. The one case where this Mac writes a `?` for a byte that is invalid in the source | |
| `-c` | BSD: drop unconvertible characters instead of substituting. GNU: the same as `//IGNORE` but exit 0 | |
| `-s` | BSD: do not print the count of invalid characters. GNU: *ignored; provided only for compatibility* | |
| `-l` | List the codesets: 215 lines of alias groups on the Mac, 1,180 names one per line on Ubuntu | [`iconv`](../../06_Terminal/iconv/README.md) |
| `mkcsmapper(1)`, `mkesdb(1)` | Named in `SEE ALSO`: Citrus's compilers for its mapping and database files. Neither is on this Mac | |
| gconv modules, `GCONV_PATH` | glibc's converters, one shared library per codeset, loaded on demand from `/usr/lib/gconv` | |
| `IBM273` | The BSD page's one example, an EBCDIC code page for German; a hint at where `iconv` is used most | [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) |

## Try it on your machine

**One input, seven conversions.** The file holds `café €` and a newline, `63 61 66 c3 a9 20 e2 82 ac 0a`. Each row is one command over that file; the columns are what came out, the exit status, and what went to stderr.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Citrus iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39), LANG set to a UTF-8 locale on both. Not machine-checked."
                                        macOS                                                     ubuntu:24.04
$ iconv -f UTF-8 -t ASCII               caf            exit=1  Illegal byte sequence              caf        exit=1  illegal input sequence at position 3
$ iconv -f UTF-8 -t ASCII//TRANSLIT     caf'e EUR      exit=1  warning: invalid characters: 2     cafe EUR   exit=0
$ iconv -c -f UTF-8 -t ASCII            caf            exit=1  warning: invalid characters: 2     caf        exit=0
$ iconv -f UTF-8 -t ASCII//IGNORE       caf            exit=1  warning: invalid characters: 2     caf        exit=1  illegal input sequence at position 10
$ iconv -f UTF-8 -t LATIN1              caf<e9>        exit=1  Illegal byte sequence              caf<e9>    exit=1  illegal input sequence at position 6
$ iconv -f UTF-8 -t CP1252              caf<e9> <80>   exit=0                                     same       exit=0
$ iconv -s -f UTF-8 -t ASCII            caf            exit=1  Illegal byte sequence              caf        exit=1  illegal input sequence at position 3
```

Row one is the first surprise. BSD's page says a valid-but-unconvertible `é` becomes `?` and the conversion continues; this Mac stops at it with *Illegal byte sequence*, exit 1, exactly as GNU does. Row two: both accept `//TRANSLIT`, and the tables differ, `'e` against `e`, and the Mac counts its own transliterations as *invalid characters* and exits 1 while GNU exits 0. Row four is the GNU page's *an error is printed after conversion* made visible: the output is complete and the status is still 1, with the position being the end of the input. Rows five and six are the reason [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) exists: `€` has no place in Latin-1 and is `80` in CP1252, on both platforms. And `-s` on the Mac silences the count but not the error, because there was no count to silence.

**When does the `?` appear, and when does something else?** Nine conversions of two three-byte files, `61 e9 62` (a Latin-1 `é` that is invalid ASCII and invalid UTF-8) and `63 61 66 c3 a9` (a UTF-8 `é`), chosen so that the source is sometimes invalid and sometimes valid-but-unconvertible.

```text title="Measured 2026-09-13 — the same two machines. Output as hex; the stderr text is the machine's. Not machine-checked."
                                                 macOS                                                       ubuntu:24.04
source byte invalid in the source codeset:
  -f US-ASCII -t US-ASCII   61 e9 62           61 3f 62                                                    61   illegal input sequence at position 1
  -f US-ASCII -t LATIN1     61 e9 62           61        Illegal byte sequence                             61   illegal input sequence at position 1
  -f US-ASCII -t UTF-8      61 e9 62           61        Illegal byte sequence                             61   illegal input sequence at position 1
  -f UTF-8    -t US-ASCII   61 e9 62           61        unexpected end of file; the last character        61   illegal input sequence at position 1
                                                         is incomplete.
source valid, character has no place in the target:
  -f LATIN1   -t US-ASCII   61 e9 62           61        Illegal byte sequence                             61   illegal input sequence at position 1
  -f UTF-8    -t US-ASCII   63 61 66 c3 a9     63 61 66  Illegal byte sequence                             63 61 66  illegal input sequence at position 3
  -f UTF-8    -t LATIN1     63 61 66 c3 a9     63 61 66 e9                                                 same
  -f LATIN1   -t UTF-8      61 e9 62           61 c3 a9 62                                                 same
```

GNU is strict in every row, as its page says. The Mac writes a `?` in exactly one row, `US-ASCII` to `US-ASCII`, the *trivial* conversion of `iconvctl(3)`, and there it does so for a byte that is *invalid in the source*, the case its own page says should stop. Row four is a smaller finding of its own: given `e9 62` at the end of a UTF-8 file, GNU says *illegal* because `62` is not a continuation byte, while the Mac says *incomplete*, having not yet looked at `62` at all.

**And with an ASCII target out of the way, the Mac does what `iconvctl(3)` said it would.** Eight characters, one at a time, from UTF-8 into six targets. Each cell is the bytes written and the exit status; `-` means nothing was written.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Citrus iconv) above, ubuntu:24.04 (GNU iconv, glibc 2.39) below. Not machine-checked."
macOS         ASCII      LATIN1     ISO-8859-2  CP1252     GBK        EUC-JP
U+00E9 é      -/1        e9/0       e9/0        e9/0       a8a6/0     8fabb1/0
U+20AC €      -/1        -/1        -/1         80/0       a2e3/0     -/1
U+0141 Ł      -/1        4c/0       a3/0        4c/0       4c/0       8fa9a8/0
U+017C ż      -/1        7a/0       bf/0        7a/0       7a/0       8fabf7/0
U+017A ź      -/1        b47a/0     bc/0        b47a/0     3f/1       8fabf5/0
U+00DF ß      -/1        df/0       df/0        df/0       3f/1       8fa9ce/0
U+1F600 😀    -/1        -/1        -/1         -/1        -/1        -/1
U+2212 −      -/1        2d/0       2d/0        2d/0       2d/0       a1dd/0

ubuntu:24.04  ASCII      LATIN1     ISO-8859-2  CP1252     GBK        EUC-JP
U+00E9 é      -/1        e9/0       e9/0        e9/0       a8a6/0     8fabb1/0
U+20AC €      -/1        -/1        -/1         80/0       80/0       -/1
U+0141 Ł      -/1        -/1        a3/0        -/1        -/1        8fa9a8/0
U+017C ż      -/1        -/1        bf/0        -/1        -/1        8fabf7/0
U+017A ź      -/1        -/1        bc/0        -/1        -/1        8fabf5/0
U+00DF ß      -/1        df/0       df/0        df/0       -/1        -/1
U+1F600 😀    -/1        -/1        -/1         -/1        -/1        -/1
U+2212 −      -/1        -/1        -/1         -/1        -/1        a1dd/0
```

Read the Mac's `Ł` row: into Latin-1, CP1252 and GBK, none of which has the letter, it writes `4c`, a plain `L`, and exits 0. `ż` becomes `z`, `ź` becomes `b4 7a`, a spacing acute accent and a `z`, and the minus sign becomes a hyphen. That is transliteration, unasked for and unreported, which is what the `BUGS` paragraph of `iconvctl(3)` says the implementation cannot switch off, and it is silent in the one way that matters: the exit status is 0 and stderr is empty, so a script cannot tell `Łódź` from `Lód´z`. Where no look-alike exists the Mac falls back to the `?` of its `iconv(3)` page for some targets (`ß` and `ź` into GBK, exit 1 and a count on stderr) and to stopping for others (`€` into Latin-1, anything into ASCII, where it never substitutes at all). GNU is strict in every cell but one, and that one, `€` into GBK as `80`, is a difference in the table rather than in policy: glibc's GBK is the Microsoft one with a euro at `0x80`, the Mac's has it at `a2 e3` where GB 18030 put it. Two implementations of one interface, and the only way to know which you have is the row for `Ł`.

**The lists are different sizes and different shapes.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
                                     macOS                                                      ubuntu:24.04
$ iconv -l | wc -l                   215                                                        1180
$ iconv -l | wc -w                   873                                                        1180
$ iconv -l | grep -i '8859-1\b'      ISO-8859-1 CP819 CSISOLATIN1 IBM819 ISO-IR-100 ...         ISO-8859-1//   ISO8859-1//   ISO_8859-1//
                                     (one line: every alias of Latin-1, then Latin-6 ... )      (one name per line, each with // on the end)
$ iconv -f NOSUCH -t UTF-8           iconv_open(UTF-8, NOSUCH): Invalid argument                conversion from `NOSUCH' is not supported
$ iconv --version                    unrecognized option `--version'                            iconv (Ubuntu GLIBC 2.39-0ubuntu8.9) 2.39
```

Same command, two data formats: the Mac prints a *group* per line, every name for one encoding on one row, which is the single richest list of aliases on the machine; GNU prints one name per line with the `//` suffix separator attached. The Mac's error message is the C call that failed, `iconv_open(UTF-8, NOSUCH)`, with the arguments in the C order, target first, which is a good way to learn that order.

## Where the page is dated, and what it does not say

**The BSD `iconv(1)` is dated 2009 and `iconv(3)` 2014**, and the behaviour they describe is the design of a 2003 library. On this Mac the `?` they promise appears for some targets and not others, an ASCII target never gets one, and the policy that actually runs first, transliteration, is documented only as a bug on a third page. Whether that is Apple's change or Citrus's, the pages do not say, and there is no version string to ask, since `iconv --version` is rejected.

**No BSD page mentions `//TRANSLIT` or `//IGNORE`**, which the binary accepts; that is the finding of [What the page does not say](../what_the_page_does_not_say/README.md), and the pages that fill the gap are the GNU ones dumped here, [`iconv(1)`](raw/linux/iconv.1.txt) and [`iconv_open(3)`](raw/linux/iconv_open.3.txt). What neither set says is that the Mac's transliteration table differs from glibc's, `'e` against `e`, or that the Mac counts a transliteration as an invalid character and fails the exit status for it.

**Neither page says what the codeset names are.** POSIX leaves them to the implementation; `iconv -l` is the only authority, and the two lists have 873 and 1,180 entries. The GNU page's *all combinations of the listed values are supported* and the BSD page's *not all combinations ... are valid* are both true of their own binary.

**Neither page says which table a name means.** `CP1252` on the Mac accepts 256 byte values and on Ubuntu 251, and the euro-updated EBCDIC pages `CP1140` to `CP1149` exist on one and not the other; those are findings 29 and 30 in [CONTRIBUTING](../../CONTRIBUTING.md) and the subject of [SAP code pages](../../07_Real_Data/sap_code_pages/README.md). A name is a key into whichever catalogue is about to read it.

**The BSD page documents `-c` as *prevent output of any invalid characters*** and the measurement shows `-c` on the Mac also sets the exit status to 1 and prints the count. The GNU page says `-c` discards *instead of terminating* and the measurement shows exit 0. So `-c` means *drop and fail* on one machine and *drop and succeed* on the other, and neither page states its exit status for the case.

## See also

- [`multibyte(3)`](multibyte.md) — the other conversion API, which asks the locale for its table instead of being told two
- [`locale(1)` and `setlocale(3)`](locale.md) — what `-f ''` and `-t ''` mean: the locale's codeset
- [`locale(5)` and `charmap(5)`](locale_files.md) — where glibc's `//TRANSLIT` table actually lives, in `translit_start` blocks
- [`charsets(7)` and the code-page pages](charsets.md) — the tables `-f` and `-t` name
- [`dd(1)`](dd.md) — the one other converter on the machine, with six EBCDIC tables of its own
- [`iconv`](../../06_Terminal/iconv/README.md) — the lesson: `-f` is your assertion, and `//TRANSLIT` is a table that ships with the implementation
- [What the page does not say](../what_the_page_does_not_say/README.md) — the flag that works and is written down nowhere, on this machine
- [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) — where `iconv -f X -t X` is not a validity test, and the `?` was first measured
- [The CJK pages](cjk_encodings.md) — the same silent `Lód´z` met from the other side, and a GB18030 that stops at the BMP on the Mac
- [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md) — `strict`, `replace`, `ignore` and the rest, which is this page's whole subject with names
- [Mojibake](../../03_Encodings/mojibake/README.md) — what the wrong `-f` produces
