# `re_format(7)`, `regex(3)`, `fnmatch(3)`, `glob(3)`, `grep(1)` and `sed(1)`: a pattern matches what the locale says it matches

**Level:** reference · for anyone who has typed `man 7 re_format` (or `man 7 regex` on Linux) and wanted to know what `[[=e=]]` is and why the page tells you not to write `[a-z]`

**One line:** Henry Spencer's 1994 text, kept almost word for word on both machines, says a bracket range is defined by the *collating sequence* and warns portable programs off it; measured, `[a-z]` matches `é` under one locale's data and not another's, `[[=e=]]` matches it only where the locale defines equivalences, and the two C libraries do not agree on whether a byte that is not a character is an error or a non-match.

**The pages:** [`re_format(7)`](raw/macos/re_format.7.txt) (macOS, dated Sept 29, 2011) · [`regex(3)`](raw/macos/regex.3.txt) (macOS, July 11, 2025) · [`fnmatch(3)`](raw/macos/fnmatch.3.txt) (macOS, April 7, 2025) · [`glob(3)`](raw/macos/glob.3.txt) (macOS, June 23, 2025) · [`grep(1)`](raw/macos/grep.1.txt) (macOS, November 10, 2021) · [`sed(1)`](raw/macos/sed.1.txt) (macOS, December 17, 2024) · [`regex(7)`](raw/linux/regex.7.txt) (Linux man-pages 6.7, 2023-11-01) · [`glob(7)`](raw/linux/glob.7.txt) (Linux man-pages 6.7, 2023-10-31). Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt). On Ubuntu `man 7 re_format` opens `regex.7`.

## What the pages are for

Two of these pages are the same document. `re_format(7)` and `regex(7)` are both Henry Spencer's description of POSIX.2 regular expressions from his 1994 regex package, the one 4.4BSD shipped; the Linux page says so in its AUTHOR section, the BSD page's footer date of 2011 is the last time Apple touched it, and the paragraphs on bracket expressions differ only in punctuation. BSD marks the decisions POSIX left open with `<**>`, Linux with `(!)`. The BSD page then adds forty lines Linux does not have, ENHANCED FEATURES, describing what `REG_ENHANCED` turns on in Apple's TRE-based `regex(3)`: `\d`, `\w`, `\b`, `\x{..}`, `(?:...)`, `(?i)`, non-greedy `*?`. Those are the Perl conveniences, and the page says twice that they *may conflict with the IEEE Std 1003.2 standards*.

`regex(3)` is the C API those two pages describe the syntax of: `regcomp`, `regexec`, `regerror`, `regfree`, plus Apple's `_l`, `n` and `w` variants. `fnmatch(3)`, `glob(3)` and `glob(7)` are a different language, the shell's `*`, `?` and `[...]`, which share the bracket-expression syntax with regular expressions and nothing else. `grep(1)` and `sed(1)` are the two commands that put a regular expression in front of a file, and both of their pages defer the syntax to `re_format(7)`.

The library's [11_Tools](../../11_Tools/README.md) asks three questions of every tool: bytes or characters, who decided, and what happens to text that is not valid. These eight pages are where the second question is answered in writing, and the answer is always the same word: *locale*. It appears on twelve lines of `regex(3)`, five of `glob(7)`, two of `re_format(7)`, and on no line of `grep(1)`.

## The page, with notes

### `re_format(7)`: the bracket expression, and the sentence about ranges

```text title="man 7 re_format, macOS 26.6.2, dumped 2026-09-13"
     A bracket expression is a list of characters enclosed in `[]'.  It
     normally matches any single character from the list (but see below).  If
     the list begins with `^', it matches any single character (but see below)
     not from the rest of the list.  If two characters in the list are
     separated by `-', this is shorthand for the full range of characters
     between those two (inclusive) in the collating sequence, e.g. `[0-9]' in
     ASCII matches any decimal digit.  It is illegal<**> for two ranges to
     share an endpoint, e.g. `a-c-e'.  Ranges are very collating-sequence-
     dependent, and portable programs should avoid relying on them.
```

*Any single character*, four times in five lines, and *the collating sequence* once. The collating sequence is `LC_COLLATE`'s order, which is not code point order in any real locale, so `[a-z]` is a question to the locale and not to ASCII: [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md). The measurement below puts `é` through `[a-z]` on four locale settings and gets both answers. The three special forms follow:

```text title="man 7 re_format, macOS 26.6.2, dumped 2026-09-13"
     Within a bracket expression, a collating element (a character, a multi-
     character sequence that collates as if it were a single character, or a
     collating-sequence name for either) enclosed in `[.' and `.]' stands for
     the sequence of characters of that collating element.  The sequence is a
     ...
     Within a bracket expression, a collating element enclosed in `[=' and
     `=]' is an equivalence class, standing for the sequences of characters of
     all collating elements equivalent to that one, including itself.  (If
     ...
     Within a bracket expression, the name of a character class enclosed in
     `[:' and `:]' stands for the list of all characters belonging to that
     class.  Standard character class names are:
     ...
     These stand for the character classes defined in ctype(3).  A locale may
     provide others.  A character class may not be used as an endpoint of a
     range.
```

`[.ch.]` is for the Spanish and Czech digraphs that sort as one letter; `[=e=]` is *e and everything the locale says is equivalent to it*, which is where `é` belongs if the collation data says so; `[:alpha:]` is `isalpha()` (BSD says `ctype(3)`, Linux says `wctype(3)`, and the difference is the whole of [`ctype(3)` and `wctype(3)`](ctype.md)). Later the page adds *Match lengths are measured in characters, not collating elements*, and in its ENHANCED section the only sentence in the family that says bytes are decoded at all: *when matching a multibyte character string, the string's bytes are converted to wide character before comparing*. The obsolete-versus-modern split, BRE against ERE, is the last third of the page: in BREs `|`, `+` and `?` are ordinary, bounds are `\{ \}`, groups are `\( \)`, and there is one extra atom, the back reference. The BUGS section is four sentences and the first is *Having two kinds of REs is a botch.*

### `regex(3)`: `REG_ILLSEQ`, and the locale stored in the compiled form

```text title="man 3 regex, macOS 26.6.2, dumped 2026-09-13"
     REG_ILLSEQ    illegal byte sequence (bad multibyte character)
     ...
INTERACTION WITH THE LOCALE
     When regcomp() or one of its variants is run, the regular expression is
     compiled into an internal form, which may include specific information
     about the locale currently in effect, such as equivalence classes or
     multi-character collation symbols.  So a reference to the current locale
     is also stored with the internal form, so that when regexec() is run, it
     can use the same locale (even if the locale is changed in-between the
     calls to regcomp() and regexec()).
```

`REG_ILLSEQ` is the third answer to the library's third question: not *match*, not *no match*, but *this is not text in the current locale*. It is in the DIAGNOSTICS list beside `REG_ECOLLATE` (bad `[.x.]`) and `REG_ECTYPE` (bad `[:x:]`), and it is not in glibc's `<regex.h>` at all. The measurement below runs the same five calls on both libraries: this Mac returns 17 for a lone `c3` in the subject *and* for one in the pattern; glibc compiles the pattern, matches it byte-wise, and reports the bad subject as a plain `REG_NOMATCH`. The locale paragraph is the mechanism behind the `[[=e=]]` result: the equivalence class is resolved at `regcomp` time from the locale's collation data, and Apple's `regcomp_l` lets you name which.

### `fnmatch(3)`, `glob(3)` and `glob(7)`: the other pattern language

```text title="man 3 fnmatch, macOS 26.6.2, dumped 2026-09-13"
     FNM_PATHNAME  Slash characters in string must be explicitly matched by
                   slashes in pattern.  If this flag is not set, then slashes
                   are treated as regular characters.
     ...
     FNM_CASEFOLD  Ignore case distinctions in both the pattern and the
                   string.
```

The shell sets `FNM_PATHNAME`, so `*` does not cross a `/` in a pathname; a library caller who forgets the flag gets `*` matching `a/b`. `FNM_CASEFOLD` is a 4.4BSD extension glibc also has under `_GNU_SOURCE`, and *case* here is the locale's: it folds `É` to `é` under a UTF-8 locale and not under `C`. `glob(3)` adds `GLOB_BRACE` for `{a,b}` *like csh(1)*, says the results come back *in ascending collation order* unless `GLOB_NOSORT`, and in its STANDARDS section claims *Collating symbol expressions, equivalence class expressions and character class expressions are not supported*. `glob(7)` on Linux, a history essay rather than an API page, has the clearest sentence in the family on why the bracket forms exist: *so that one can say "[[:lower:]]" instead of "[a-z]", and have things work in Denmark, too, where there are three letters past 'z' in the alphabet.* None of the three pages says whether a `?` is a byte or a character; the measurement shows the two libraries answering differently, and glibc answering twice.

### `grep(1)` and `sed(1)`: the commands

```text title="man 1 grep, macOS 26.6.2, dumped 2026-09-13"
     -a, --text
             Treat all files as ASCII text.  Normally grep will simply print
             "Binary file ... matches" if files contain binary characters.
     ...
     --binary-files=value
             Controls searching and printing of binary files.  Options are:
             binary (default)  Search binary files but do not print them.
             without-match     Do not search binary files.
             text              Treat all files as text.
     ...
BUGS
     The grep utility does not normalize Unicode input, so a pattern
     containing composed characters will not match decomposed input, and vice
     versa.
```

*Binary characters* is not defined; the [`grep` lesson](../../11_Tools/grep/README.md) found a NUL does it, and that in a UTF-8 locale BSD `grep` drops a line it cannot decode, says nothing, and exits 0. The BUGS sentence is the one Unicode sentence on the page, and it is correct and important: [Normalization](../../04_Python/normalization/README.md). `-o` prints the matching part, `--color` marks it up using `GREP_COLOR` (GNU has moved to `GREP_COLORS` and warns), `-w` is defined as `[[:<:]]` and `[[:>:]]`, the BSD word-boundary brackets that GNU `grep` rejects as an *Invalid character class name*. There is no `-P`: `grep -P` on this Mac is `invalid option`, and the Perl syntax lives in [`pcre2`](../../11_Tools/pcre2/README.md) or [`ripgrep`](../../11_Tools/ripgrep/README.md).

```text title="man 1 sed, macOS 26.6.2, dumped 2026-09-13"
     [2addr]l
             (The letter ell.)  Write the pattern space to the standard output
             in a visually unambiguous form.  This form is as follows:
             ...
             Nonprintable characters are written as three-digit octal numbers
             (with a preceding backslash) for each byte in the character (most
             significant byte first).
     ...
     [2addr]y/string1/string2/
             Replace all occurrences of characters in string1 in the pattern
             space with the corresponding characters from string2.
     ...
BUGS
     Multibyte characters containing a byte with value 0x5C (ASCII `\') may be
     incorrectly treated as line continuation characters in arguments to the
     "a", "c" and "i" commands.  Multibyte characters cannot be used as
     delimiters with the "s" and "y" commands.
```

*For each byte in the character* is the page admitting a character can be several bytes, and *nonprintable* is the locale's word: BSD `sed -n l` prints `é` as `\303\251` under `C` and as `é` under a UTF-8 locale, while GNU `sed` prints the octal in both. `y///` pairs *characters*, so `y/é/e/` is two bytes against one under `C` and refused, and one character against one under UTF-8 and done: the [`sed` lesson](../../11_Tools/sed/README.md) has that at length. The `-i extension` paragraph, and the example `sed -i '' -e 's/foo/bar/g' test.txt` at the foot of the page, document the split the library's [CONTRIBUTING finding 28](../../CONTRIBUTING.md) records: BSD wants the suffix as a separate argument, GNU wants it attached or absent, and neither spelling runs on the other.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| modern / obsolete RE, ERE / BRE | POSIX's two syntaxes: `egrep`'s with `+ ? | ( )` special, and `ed`'s with `\( \) \{ \}` and back references | [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) |
| `<**>`, `(!)` | The two pages' marks for decisions POSIX leaves open: not portable | this page, above |
| atom, piece, branch, bound | An atom is one unit, a piece is an atom with `* + ?` or `{n,m}`, a branch is pieces in a row, an RE is branches joined by `\|` | [`re_format(7)`](raw/macos/re_format.7.txt) |
| bracket expression | `[...]`: one character from a list; `^` negates; `-` is a range | this page, above |
| collating sequence | The locale's sort order, `LC_COLLATE`; what a range is defined over | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| collating element, `[.ch.]` | One or more characters that sort as a unit; a digraph is one element | [`strcoll(3)` and `wcscoll(3)`](collation.md) |
| equivalence class, `[=e=]` | Every collating element the locale ranks with `e` at the first level; `é` if the data says so | [`strcoll(3)` and `wcscoll(3)`](collation.md) |
| character class, `[:alpha:]` | The twelve `ctype(3)` predicates by name; a locale may add more | [`ctype(3)` and `wctype(3)`](ctype.md) |
| `[[:<:]]`, `[[:>:]]` | BSD's word-boundary brackets; GNU spells them `\<` `\>` and rejects the bracket form | this page, below |
| `RE_DUP_MAX` | 255, the largest count in a bound | [`re_format(7)`](raw/macos/re_format.7.txt) |
| back reference, `\1` | Match what the first group matched; BRE only in POSIX; *a dreadful botch* in BUGS | [`re_format(7)`](raw/macos/re_format.7.txt) |
| `REG_ENHANCED`, `\d \w \b \x{..} (?i)` | Apple's Perl-style additions, on when the flag or `sed -H` is | [PCRE2](../../11_Tools/pcre2/README.md) |
| `REG_ICASE`, *case-independent matching* | `x` becomes `[xX]`, using the locale's idea of case | [`ctype(3)` and `wctype(3)`](ctype.md) |
| `REG_ILLSEQ` | *Illegal byte sequence*: the subject or pattern is not text in this locale; BSD only | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `REG_ECOLLATE`, `REG_ECTYPE`, `REG_ERANGE` | A `[.x.]` the locale lacks, a `[:x:]` it lacks, a range with its ends reversed | [`regex(3)`](raw/macos/regex.3.txt) |
| `regcomp_l`, `regwcomp`, TRE | Compile under a named locale; compile a `wchar_t` pattern; the engine Apple has used since 10.8 | [`locale(1)` and `setlocale(3)`](locale.md) |
| `FNM_PATHNAME`, `FNM_PERIOD`, `FNM_CASEFOLD` | `*` stops at `/`; a leading `.` must be matched explicitly; fold case | [The shell has no string type](../../11_Tools/sh/README.md) |
| `GLOB_BRACE`, `GLOB_NOSORT`, *ascending collation order* | `{a,b}` expansion; skip the sort; the sort is `LC_COLLATE`'s | [`find`, and filenames that are bytes](../../11_Tools/find/README.md) |
| *binary characters*, `--binary-files` | Undefined on the page; a NUL in practice; `text` to override | [Binary is a verdict, not a property](../../06_Terminal/binary_or_text/README.md) |
| `GREP_COLOR`, `GREP_COLORS` | The old single-colour variable this page names, and GNU's replacement | this page, below |
| pattern space, hold space | `sed`'s current line and its one register | [`sed` matches patterns, not bytes](../../11_Tools/sed/README.md) |
| `l`, `y///`, `-i extension` | Octal-escaped dump of a line; character-for-character transliteration; in-place with a backup suffix | [`sed` matches patterns, not bytes](../../11_Tools/sed/README.md) |

## Try it on your machine

**What matches `é`.** The line is the two bytes `c3 a9`. `grep -c` under `C` and under a UTF-8 locale on each machine, and, on Ubuntu, under an `en_US.UTF-8` built in the container with `localedef` because the image ships only `C.utf8`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD grep 2.6.0-FreeBSD, en_US.UTF-8) and ubuntu:24.04 (GNU grep 3.11; C.utf8, and en_US.UTF-8 generated with localedef). Not machine-checked."
                  macOS                       ubuntu:24.04
                  C      en_US.UTF-8          C      C.utf8   en_US.UTF-8
^[a-z]$           0      0                    0      0        1
^[[:alpha:]]$     0      1                    0      1        1
^[[:lower:]]$     0      1                    0      1        1
^[[=e=]]$         0      1                    0      0        1
^[[.e.]]$         0      0                    0      0        0
^.$               0      1                    0      1        1
^..$              1      0                    1      0        0
```

Every row is the page. `.` is one byte under `C` and one character under UTF-8 on both. `[[:alpha:]]` follows `LC_CTYPE`. `[[=e=]]` follows the collation data: BSD's `en_US.UTF-8` and glibc's `en_US.UTF-8` both rank `é` with `e`, and glibc's `C.utf8`, which sorts by code point and defines no equivalences, does not. And `[a-z]`, *very collating-sequence-dependent*, matches `é` under glibc's `en_US.UTF-8`, where `é` sorts between `e` and `f`, and nowhere else in the table. Two greps, three locales, and the only portable spelling is `[[:lower:]]`, as `glob(7)` says.

**`REG_ILLSEQ`.** A C program that compiles three patterns with `regcomp` and runs `regexec`, under `LC_ALL=C` and a UTF-8 locale. The subject `caf<c3>` is a truncated `é`.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang, TRE regex) and ubuntu:24.04 (gcc, glibc 2.39). Not machine-checked."
                                        macOS, C   macOS, en_US.UTF-8            ubuntu, C   ubuntu, C.utf8
REG_ILLSEQ in <regex.h>                 17         17                            not defined
regexec("^.$"    on "<c3>")             0 match    17 illegal byte sequence      0 match     1 No match
regexec("^caf.$" on "café")             1 no match 0 match                       1 No match  0 match
regexec("^caf..$" on "café")            0 match    1 no match                    0 match     1 No match
regexec("^caf.$" on "caf<c3>")          0 match    17 illegal byte sequence      0 match     1 No match
regcomp("<c3>"), then exec on "café"    0 match    regcomp = 17                  0 match     0 match
```

The last row is the split. Apple's `regcomp` refuses a pattern that is not valid in the locale; glibc compiles it, and the lone byte then matches the first byte of `é` in a UTF-8 locale, which the library's third question would call a wrong answer given confidently. Under `C` the two libraries agree on everything, because there is nothing to decode.

**`fnmatch` and `glob`.** The same C program on both libraries, with a file named `café` in the directory.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04 (glibc 2.39); the UTF-8 column is en_US.UTF-8 on macOS and C.utf8 on Ubuntu (en_US.UTF-8 there gave the same, except [a-z] = match). Not machine-checked."
                                          macOS C      macOS UTF-8   ubuntu C     ubuntu UTF-8
fnmatch("*",     "a/b", 0)                match        match         match        match
fnmatch("*",     "a/b", FNM_PATHNAME)     FNM_NOMATCH  FNM_NOMATCH   FNM_NOMATCH  FNM_NOMATCH
fnmatch("caf?",  "café", 0)               FNM_NOMATCH  match         FNM_NOMATCH  match
fnmatch("caf??", "café", 0)               match        FNM_NOMATCH   match        match
fnmatch("CAFÉ",  "café", FNM_CASEFOLD)    FNM_NOMATCH  match         FNM_NOMATCH  match
fnmatch("[a-z]", "é", 0)                  FNM_NOMATCH  match         FNM_NOMATCH  FNM_NOMATCH
glob("caf?")                              0 matches    café          0 matches    café
glob("{a,b}.txt", GLOB_BRACE)             a.txt b.txt  a.txt b.txt   a.txt b.txt  a.txt b.txt
```

Row four is the surprise: glibc's `fnmatch` in a UTF-8 locale matches `café` against `caf?` *and* against `caf??`, and a further probe found `caf?` followed by the literal byte `a9` matching too, so the second answer is a byte-wise reading accepted beside the character-wise one. BSD gives one answer per locale. `bash`'s own matcher on the same directory, on both machines, expands `caf?` and leaves `caf??` unexpanded, so the shell and the C library disagree on Linux. Row six is the range sentence again: this Mac's `fnmatch` puts `é` in `[a-z]` under `en_US.UTF-8` while its `grep` does not, because `fnmatch(3)` and TRE consult different tables.

**Three things the `grep` and `sed` pages say, on the other implementation.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD grep, BSD sed) and ubuntu:24.04 (GNU grep 3.11, GNU sed 4.9), UTF-8 locales. Not machine-checked."
                                                  macOS                                            ubuntu:24.04
$ grep -P 'caf\xc3'                               grep: invalid option -- P    (exit 2)            (works)
$ grep -c '[[:<:]]cafe'   on 'a cafe'             1                                                grep: Invalid character class name   (exit 2)
$ GREP_COLOR='01;32' grep --color=always é        caf^[[01;32m^[[KM-CM-)^[[m^[[K                   same, plus: grep: warning: GREP_COLOR='01;32' is deprecated; use GREP_COLORS='mt=01;32'
$ printf 'café €\ttab\n' | LC_ALL=C sed -n l      caf\303\251 \342\202\254\ttab$                   caf\303\251 \342\202\254\ttab$
$ ... | LC_ALL=<UTF-8> sed -n l                   café €\ttab$                                     caf\303\251 \342\202\254\ttab$
$ printf 'café\n' | LC_ALL=C sed 'y/é/e/'         sed: 1: "y/é/e/": transform strings are not the same length   sed: -e expression #1, char 7: strings for `y' command are different lengths
$ printf 'café\n' | LC_ALL=<UTF-8> sed 'y/é/e/'   cafe                                             cafe
$ printf 'café\n' | sed 'sécaféXé'                sed: 1: "sécaféXé": RE error: illegal byte sequence   sed: -e expression #1, char 2: delimiter character is not a single-byte character
```

`sed -n l` is the page's *nonprintable* being asked of the locale: BSD prints `é` and `€` as themselves once the locale can, GNU escapes every byte above `7f` regardless. `y///` counts what the locale calls a character, which under `C` is a byte, and both refuse rather than guess. The multibyte delimiter is refused by both with the BSD page's own BUGS sentence as the reason.

## Where the page is dated, and what it does not say

**`re_format(7)` is dated Sept 29, 2011 and `regex(7)` 2023-11-01**, and they are the same 1994 text. The BSD page says character classes come from `ctype(3)`, the Linux page from `wctype(3)`; on both machines the wide functions are what a UTF-8 locale actually consults. Neither page says what `.` matches when the input is not valid in the locale, which is the question the `grep` lesson found the two implementations answering differently. Neither mentions UTF-8, and the BSD page's one sentence about multibyte strings is in the ENHANCED section, where a reader who wants only the standard will not look.

**`regex(3)` is dated July 11, 2025** and documents an API that glibc does not have: `REG_ILLSEQ`, `REG_ENHANCED`, the `_l` variants and the wide variants are all Apple's. Its DIAGNOSTICS are right about this Mac. The glibc page was not dumped, and its list has no code for a bad byte, which the measurement above shows as a `REG_NOMATCH` that says nothing.

**`grep(1)` is dated November 10, 2021** and does not contain the word *locale*. The one behaviour a reader of this library most needs to know about BSD `grep`, that in a UTF-8 locale a line with an undecodable byte is silently skipped, is on no page. `GREP_COLOR` is on the page and deprecated on GNU. `-P` is absent and the page does not say so; the usage line does.

**`sed(1)` is dated December 17, 2024** and is the most honest page in the family: it names `LC_CTYPE` and `LC_COLLATE` in ENVIRONMENT, it says *for each byte in the character* under `l`, and its BUGS admits the `0x5C` problem and the delimiter problem. What it does not say is that its `-i` spelling is incompatible with GNU's; it just uses its own in the last example.

**`glob(3)` is dated June 23, 2025** and says character classes are *not supported*, on a machine whose `fnmatch(3)` matched `[[:alpha:]]` against `é`. Neither `fnmatch(3)` nor `glob(3)` nor `glob(7)` says whether `?` matches a byte or a character; on glibc, measured above, it matches either.

## See also

- [`ctype(3)` and `wctype(3)`](ctype.md) — the twelve `[:class:]` names, and which function answers for them in a UTF-8 locale
- [`locale(1)` and `setlocale(3)`](locale.md) — the setting every row of the tables above hangs on
- [`strcoll(3)` and `wcscoll(3)`](collation.md) — the collating sequence that defines a range and an equivalence class
- [`wcwidth(3)` and the column tools](columns_and_characters.md) — the other place a *character* is counted, and counted differently
- [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) — `.` in two locales, the NUL rule, and the silent drop
- [`sed` matches patterns, not bytes](../../11_Tools/sed/README.md) — `y///`, `s///` and `-i` at length
- ["Supports Unicode" is a level, not a yes](../../02_Characters/what_a_regex_matches/README.md) — the same questions put to Python's engine and PCRE
- [`find`, and filenames that are bytes](../../11_Tools/find/README.md) — where `fnmatch` meets a directory
- [A page has a date](../a_page_has_a_date/README.md) — a 1994 text on two 2020s machines
- [What the page does not say](../what_the_page_does_not_say/README.md) — *locale*, absent from the `grep` page
