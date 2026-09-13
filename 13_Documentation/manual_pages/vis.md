# `vis(1)`, `unvis(1)`, `vis(3)` and `unvis(3)`: the escape you can undo, and the state machine that undoes it

**Level:** reference · for anyone who has piped a file through `cat -v`, wondered how to get the bytes back, and wanted the page that says you cannot, and the one next to it that says you can

**One line:** `vis(3)` promises *a unique, invertible representation composed entirely of graphic characters* and offers six spellings of it under one flag word, from `\M-C` to `%c3` to `=C3`; `unvis(3)` is a five-state decoder you feed one byte at a time; the round trip holds for all 256 byte values in every format but `-b`; and on this Mac the multibyte support the pages describe is absent from the command and unsound in the library.

**The pages:** [`vis(1)`](raw/macos/vis.1.txt) (macOS, February 18, 2021) · [`unvis(1)`](raw/macos/unvis.1.txt) (November 27, 2010) · [`vis(3)`](raw/macos/vis.3.txt) (April 22, 2017) · [`unvis(3)`](raw/macos/unvis.3.txt) (March 12, 2011). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). Ubuntu has none of the four: `man.REAL -w 1 vis` and `-w 3 vis` answer *No manual entry*, `command -v vis unvis` finds nothing, and `#include <vis.h>` fails to compile.

## What the pages are for

`vis` is 4.4BSD's answer to a question this library asks in three chapters: how do you write bytes that a channel will not carry, so that the reader can get the exact bytes back? `cat -v` shows them and cannot be reversed; `od` and `xxd` reverse but do not look like text. `vis(3)` is a library function that turns one byte into a short graphic string, `vis(1)` is the filter built on it, and `unvis(3)` and `unvis(1)` are the inverses. All four are in the BSD tradition and none of them made it into POSIX or glibc, which is why the Linux side of this page is one line long.

The reason to read them here is that `vis(3)` is, without saying so, a catalogue of the escaping schemes the rest of this library treats separately. `VIS_OCTAL` is C's `\303`; `VIS_CSTYLE` is C's `\n` and `\t`; `VIS_HTTPSTYLE` is the percent-encoding of [Terminal hyperlinks](../../06_Terminal/terminal_hyperlinks/README.md) and every URL; `VIS_MIMESTYLE` is the `=C3` of quoted-printable; and `VIS_HTTP1866` in the decoder is HTML's `&eacute;`. [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) explains why these all exist and what each one wraps; [Binary to text](../../03_Encodings/binary_to_text/README.md) is the alternative that gives up on readability; and [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) already quotes the page's one-sentence invariant. This page is the rest of the page: the flags, the formats, the decoder's return codes, and what the machine does with them.

## The page, with notes

### `vis(1)`: `cat -v`, but invertible

```text title="man 1 vis, macOS 26.6.2, dumped 2026-09-13"
     vis is a filter for converting non-printable characters into a visual
     representation.  It differs from `cat -v' in that the form is unique and
     invertible.  By default, all non-graphic characters except space, tab,
     and newline are encoded.  A detailed description of the various visual
     formats is given in vis(3).
     ...
     -b      Turns off prepending of backslash before up-arrow control
             sequences and meta characters, and disables the doubling of
             backslashes.  This produces output which is neither invertible or
             precise, but does represent a minimum of change to the input.  It
             is similar to "cat -v".  (VIS_NOSLASH)
```

*Unique and invertible* is the property [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) wants from `cat -v` and does not get: `cat -v` prints `M-C` for the byte `c3` and also for the three bytes `M-C`, so the output is ambiguous, and the `-b` entry says so about its own imitation of it. The cure is a backslash in front of every escape and a doubled backslash for a real one, which is the same trick every escape scheme on [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) uses. Each option names the `vis(3)` flag it sets: `-o` is `VIS_OCTAL`, `-c` `VIS_CSTYLE`, `-h` `VIS_HTTPSTYLE`, `-m` `VIS_MIMESTYLE`, `-w` `VIS_WHITE`, `-t` `VIS_TAB`, `-M` `VIS_META`, `-l` the hidden-newline marker `\$`, and the page's own EXAMPLES section is reproduced in the experiments. Its MULTIBYTE CHARACTER SUPPORT section says the command *supports multibyte character input* influenced by `LC_CTYPE`; the experiment finds the binary does not import `setlocale` at all.

### `vis(3)`: one invariant, six formats

```text title="man 3 vis, macOS 26.6.2, dumped 2026-09-13"
     The encoding is a unique, invertible representation composed entirely of
     graphic characters; it can be decoded back into the original form using
     the unvis(3), strunvis(3) or strnunvis(3) functions.
     ...
     The strvisx() and strnvisx() functions encode exactly len characters from
     src (this is useful for encoding a block of data that may contain NUL's).
     Both forms NUL terminate dst.  The size of dst must be four times the
     number of bytes encoded from src (plus one for the NUL).  Both forms
     ...
```

Three functions of one character (`vis`, `nvis`, `svis`), four of a string (`strvis`, `strnvis`, `strsvis`, `stravis`), and the `x` forms that take a length so an embedded `00` byte is data rather than a terminator: the [NUL](../../02_Characters/the_nul_byte/README.md) distinction, as an API. *Four times* is the worst case, `\M^?` for one byte, and the `n` forms return `-1` with `ENOSPC` when the buffer is short. Then the two dials, which characters and which spelling:

```text title="man 3 vis, macOS 26.6.2, dumped 2026-09-13"
     VIS_GLOB    Also encode the magic characters (`*', `?', `[', and `#')
                 recognized by glob(3).
     ...
     VIS_SAFE    Only encode "unsafe" characters.  Unsafe means control
                 characters which may cause common terminals to perform
                 unexpected functions.  Currently this form allows space, tab,
                 newline, backspace, bell, and return -- in addition to all
                 graphic characters -- unencoded.
     ...
     (default)   Use an `M' to represent meta characters (characters with the
                 8th bit set), and use caret `^' to represent control
                 characters (see iscntrl(3)).  The following formats are used:

                 \^C    Represents the control character `C'.  Spans
                        characters `\000' through `\037', and `\177' (as
                        `\^?').

                 \M-C   Represents character `C' with the 8th bit set.  Spans
                        characters `\241' through `\376'.

                 \M^C   Represents control character `C' with the 8th bit set.
                        Spans characters `\200' through `\237', and `\377' (as
                        `\M^?').
     ...
     VIS_HTTPSTYLE
                 Use URI encoding as described in RFC 1738.  The form is `%xx'
                 where x represents a lower case hexadecimal digit.

     VIS_MIMESTYLE
                 Use MIME Quoted-Printable encoding as described in RFC 2045,
                 only don't break lines and don't handle CRLF.  The form is
                 `=XX' where X represents an upper case hexadecimal digit.
```

`VIS_GLOB`, `VIS_SHELL`, `VIS_META` and `VIS_SAFE` widen or narrow the set: which bytes are dangerous depends on who reads them next, a shell, a glob, a terminal, which is the whole argument of [The byte that means something to somebody else](../../12_Adversarial/in_band_signals/README.md), and `VIS_SAFE`'s list of terminal-safe controls is [Control characters](../../02_Characters/control_characters/README.md) reduced to five. The default spelling is the `M-`/`^` notation of Emacs and `cat -v` with a backslash prefix, and `\M^C` covers the C1 controls `80` to `9f`, the range [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) fights over. The two named RFCs are the two escape schemes that outgrew BSD: `%xx` for URLs, `=XX` for mail, each with its own case rule, and the MIME entry is honest that it does only the byte part of quoted-printable and none of the line discipline. `VIS_NOSLASH` is the anti-flag: *with this flag set, the encoding is ambiguous and non-invertible*.

### `unvis(3)`: five return codes and a final call

```text title="man 3 unvis, macOS 26.6.2, dumped 2026-09-13"
     0 (zero)         Another character is necessary; nothing has been
                      recognized yet.

     UNVIS_VALID      A valid character has been recognized and is available
                      at the location pointed to by cp.

     UNVIS_VALIDPUSH  A valid character has been recognized and is available
                      at the location pointed to by cp; however, the character
                      currently passed in should be passed in again.

     UNVIS_NOCHAR     A valid sequence was detected, but no character was
                      produced.  This return code is necessary to indicate a
                      logical break between characters.

     UNVIS_SYNBAD     An invalid escape sequence was detected, or the decoder
                      is in an unknown state.  The decoder is placed into the
                      starting state.

     When all bytes in the stream have been processed, call unvis() one more
     time with flag set to UNVIS_END to extract any remaining character (the
     character passed in is ignored).
```

This is a decoder written the way [`mbrtowc(3)`](multibyte.md) is written: state lives in a caller-owned integer, bytes go in one at a time, and the return code says whether a character came out. `UNVIS_VALIDPUSH` is the interesting one, the case where the byte that ended a sequence was not part of it, `%4g` producing `04` and then needing the `g` again. `UNVIS_NOCHAR` is how the hidden newline `\$` decodes to nothing. `UNVIS_END` is the flush, and the experiment shows it returning `UNVIS_SYNBAD` for a trailing lone backslash. The page's BUGS section is unusual enough to quote: *The names VIS_HTTP1808 and VIS_HTTP1866 are wrong. Percent-encoding was defined in RFC 1738, the original RFC for URL*; the experiments find that the decoder behind the second wrong name has a bug of its own.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| graphic character | A character with a visible glyph: `isgraph(3)`, printable and not space. The alphabet every `vis` format is written in | [Control characters](../../02_Characters/control_characters/README.md) |
| invertible | The output determines the input: no two inputs share an encoding and every encoding decodes | [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) |
| meta character (`M-`) | A byte with bit 7 set, written as `M-` plus the byte with the bit cleared; Emacs notation, also `cat -v`'s | [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) |
| control character (`^C`) | Bytes `00`–`1f` and `7f`, written as `^` plus the byte XOR `40`; `\^?` is `DEL` | [Control characters](../../02_Characters/control_characters/README.md) |
| `\M^C` | A meta *and* control byte, `80`–`9f` and `ff`: the C1 range | [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) |
| `VIS_OCTAL`, `\ddd` | Three octal digits, always three, so `\0` can never be mistaken for `\012` | [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) |
| `VIS_HTTPSTYLE`, `%xx` | Percent-encoding, lower-case hex; RFC 1738's scheme for URLs | [Terminal hyperlinks](../../06_Terminal/terminal_hyperlinks/README.md) |
| `VIS_MIMESTYLE`, `=XX` | Quoted-printable's byte escape, upper-case hex, without its line rules | [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) |
| `VIS_HTTP1866`, entity reference, numeric character reference | HTML's `&lt;`, `&eacute;`, `&#233;`; decode-only, and misnamed by the page's own admission | |
| `VIS_NOSLASH` | Drop the backslash prefix and the doubling: `cat -v` output, ambiguous | [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) |
| `VIS_GLOB`, `VIS_SHELL`, `VIS_META`, `VIS_WHITE`, `VIS_SAFE` | Widen or narrow *which* bytes are encoded: glob magic, shell metacharacters, all of those plus white space, or only terminal-unsafe controls | [The byte that means something to somebody else](../../12_Adversarial/in_band_signals/README.md) |
| `strvisx`, `len` | The forms that take a byte count, so a `00` in the data is encoded rather than treated as the end | [The NUL byte](../../02_Characters/the_nul_byte/README.md) |
| `astate`, `UNVIS_END` | The caller-owned decoder state, and the flag for the final flushing call | [`multibyte(3)`](multibyte.md) |

## Try it on your machine

**The formats, over `caf` `c3 a9` `09` `0a`.** Identical under `LC_ALL=C` and `LC_ALL=en_US.UTF-8`, because the command never reads the variable.

```text title="Measured 2026-09-13 — macOS 26.6.2, /usr/bin/vis; the same output under LC_ALL=C and LC_ALL=en_US.UTF-8. Not machine-checked."
$ printf 'caf\303\251\t\n' | vis         caf\M-C\M-)<tab>
$ ... | vis -o                            caf\303\251<tab>
$ ... | vis -c                            caf\M-C\M-)<tab>
$ ... | vis -c -o                         caf\303\251<tab>
$ ... | vis -h                            caf%c3%a9%09%0a
$ ... | vis -m                            caf=C3=A9=09
$ ... | vis -M                            caf\M-C\M-)\011\012
$ ... | vis -w                            caf\M-C\M-)\011\012
$ ... | vis -t                            caf\M-C\M-)\011
$ ... | vis -l                            caf\M-C\M-)<tab>\$
$ ... | vis -b                            cafM-CM-)<tab>
$ cat -v                                  cafM-CM-)<tab>              (byte-identical on ubuntu:24.04)
$ nm -u /usr/bin/vis | grep -c setlocale  0                           (22 undefined symbols, none of them locale functions; /bin/cat imports setlocale)
```

`<tab>` marks a real tab byte the format left alone. Note that `-h` and `-m` treat the newline as a byte to encode (`%0a`; `-m` ends without one), which is why their output has no line structure, and that `-c` alone leaves `é` in `M-` notation, because `VIS_CSTYLE` only has spellings for the nine characters on the page and falls back to the default for the rest. The last line is the finding: the command's page has a MULTIBYTE CHARACTER SUPPORT section, and the binary has no locale code in it.

**Round trips over every byte value.** `all.bin` holds `00` to `ff` in order; `cmp` prints nothing when the round trip is exact.

```text title="Measured 2026-09-13 — macOS 26.6.2, LC_ALL=C (the same results under en_US.UTF-8). Not machine-checked."
  vis          ->  706 bytes; unvis    -> identical
  vis -o       ->  736 bytes; unvis    -> identical
  vis -c       ->  697 bytes; unvis    -> identical
  vis -c -o    ->  722 bytes; unvis    -> identical
  vis -h       ->  622 bytes; unvis -h -> identical
  vis -m       ->  602 bytes; unvis -m -> identical
  vis -w       ->  715 bytes; unvis    -> identical
  vis -M       ->  778 bytes; unvis    -> identical
  vis -c -o -l ->  724 bytes; unvis    -> identical
  vis -b       | unvis -> stdin all.bin differ: char 2, line 1
  cat -v       | unvis -> stdin all.bin differ: char 1, line 1
$ printf '\200\201\202\203\376\377' | vis      \M^@\M^A\M^B\M^C\M-~\M^?
$ printf '\200\201\202\203\376\377' | vis -o   \200\201\202\203\376\377
$ printf '\200\201\202\203\376\377' | vis -h   %80%81%82%83%fe%ff
$ printf '\200\201\202\203\376\377' | vis -m   =80=81=82=83=FE=FF
```

Every invertible format inverts, at between 2.4 and 3 bytes per input byte, and the two the page calls non-invertible are non-invertible from the first or second byte. The second block is the `\M^C` row of the page for the C1 range and `ff`, in all four spellings.

**The decoders, and the page's own examples.**

```text title="Measured 2026-09-13 — macOS 26.6.2. Not machine-checked."
$ printf '\020\n\t' | vis -w -t                        \^P\012\011          (the page's first EXAMPLE, reproduced)
$ printf '%%41%%c3%%a9%%0a' | unvis -h | xxd -p        41c3a90a
$ printf 'caf=\n\303\251\n' | unvis -m | xxd -p        636166c3a90a          (a quoted-printable soft break, removed)
$ printf '&lt;&eacute;&gt;' | unvis -H | xxd -p        3ce93e                (é as the Latin-1 byte e9)
$ printf '&#65;' | unvis -H | xxd -p                   47                    (should be 41, "A")
$ printf '&#233;' | unvis -H | xxd -p                  16                    (should be e9)
$ printf 'a\\Mxb' | unvis                              unvis: <stdin>: offset: 4: can't decode   then "ab"
$ printf 'a\\qb' | unvis | xxd -p                      617162                (an unknown escape yields the letter, no error)
```

`-h` and `-m` decode exactly what `-h` and `-m` encode, and `-m` also removes the `=` soft line break that `-m` never writes. `-H` decodes the named entities, and its numeric references come out wrong: `&#65;`, `&#169;`, `&#233;`, `&#255;` and `&#256;` gave `47`, `c4`, `16`, `2e` and `2f`, which are the values you get by accumulating the decimal digits in base eleven. The `BUGS` section says the flag's name is wrong; the decoder behind it is too.

**The state machine, one byte at a time.** A C program feeds `unvis()` the string `\M-C\M-)\^Ia\$` and a newline, then two malformed inputs, printing each return code.

```text title="Measured 2026-09-13 — macOS 26.6.2, Apple clang 21. Not machine-checked."
feed '\' -> UNVIS_NOCHAR   feed 'M' -> UNVIS_NOCHAR   feed '-' -> UNVIS_NOCHAR   feed 'C' -> UNVIS_VALID  out = 0xc3
feed '\' -> UNVIS_NOCHAR   feed 'M' -> UNVIS_NOCHAR   feed '-' -> UNVIS_NOCHAR   feed ')' -> UNVIS_VALID  out = 0xa9
feed '\' -> UNVIS_NOCHAR   feed '^' -> UNVIS_NOCHAR   feed 'I' -> UNVIS_VALID  out = 0x09
feed 'a' -> UNVIS_VALID  out = 0x61
feed '\' -> UNVIS_NOCHAR   feed '$' -> UNVIS_NOCHAR   feed newline -> UNVIS_VALID  out = 0x0a
UNVIS_END -> UNVIS_NOCHAR (3)
"\Mx":      feed '\' -> UNVIS_NOCHAR   feed 'M' -> UNVIS_NOCHAR   feed 'x' -> UNVIS_SYNBAD
"%c3%4g" with VIS_HTTPSTYLE:
            feed '%' -> UNVIS_NOCHAR   feed 'c' -> UNVIS_NOCHAR   feed '3' -> UNVIS_VALID  out = 0xc3
            feed '%' -> UNVIS_NOCHAR   feed '4' -> UNVIS_NOCHAR   feed 'g' -> UNVIS_VALIDPUSH  out = 0x04   feed 'g' -> UNVIS_VALID  out = 0x67
"ab\":      feed 'a' -> UNVIS_VALID  out = 0x61   feed 'b' -> UNVIS_VALID  out = 0x62   feed '\' -> UNVIS_NOCHAR   UNVIS_END -> UNVIS_SYNBAD (-1)
```

Every code on the page, produced on demand: `NOCHAR` while a sequence is open (the page's `0` never appeared; this implementation says `NOCHAR` instead), `VALID` at the end of one, `VALIDPUSH` when a one-digit `%4` is closed by a non-digit that must be re-fed, `SYNBAD` for `\M` followed by neither `-` nor `^`, and `SYNBAD` from the final `UNVIS_END` when a backslash was left open.

**The library's multibyte support, under a UTF-8 locale.** `strnvisx(VIS_OCTAL)` over single characters and one invalid byte, in a program that calls `setlocale(LC_ALL, "")` under `LANG=en_US.UTF-8`.

```text title="Measured 2026-09-13 — macOS 26.6.2, Apple clang 21. Not machine-checked."
                          no setlocale (C)                   setlocale, en_US.UTF-8
c3 a9 (é)                 \303\251                           c3 a9  (passed through, unencoded)
e2 82 ac (€)              \342\202\254                       e2 82 ac
f0 9f 98 80 (😀)          \360\237\230\200                   f0 9f 98 80
ff (invalid)              \377                               ff     (passed through, unencoded)
c3 (truncated)            \303                               c3     (passed through, unencoded)
61 00 62 2a c3 a9 ff 09 0a 5c, as one buffer:
                          a\000b*\303\251\377<tab><nl>\134    61 5c 30 30 30 62 2a e9 ff 09 0a 5c 31 33 34
                                                             (é written as the single byte e9; ff raw; strunvisx returns 9, not 10)
```

Under `C` the invariant holds: every byte above `7f` is three octal digits behind a backslash. Under the UTF-8 locale a valid character passes through, which is what the page's MULTIBYTE section describes, but so does an invalid byte, raw, and in a buffer that also contains a NUL the `c3 a9` of `é` comes out as one byte `e9`. The output is neither composed of graphic characters nor invertible, and the page's promise that a mismatch means *encoding will be performed byte-by-byte instead* is not what this libc does. `VIS_NOLOCALE`, or not calling `setlocale`, is the only sound mode measured.

**Ubuntu.**

```text title="Measured 2026-09-13 — ubuntu:24.04. Not machine-checked."
$ command -v vis unvis; echo "exit $?"
exit 1
$ ls /usr/include/bsd/vis.h
ls: cannot access '/usr/include/bsd/vis.h': No such file or directory
$ printf '#include <vis.h>\nint main(void){return 0;}\n' > v.c; cc v.c
v.c:1:10: fatal error: vis.h: No such file or directory
$ printf 'caf\303\251\t\n' | cat -v
cafM-CM-)
```

## Where the page is dated, and what it does not say

**`vis(3)` is dated 2017 and says multibyte support *was added in OS X 10.12*.** The support is there in the sense that `strnvisx` calls the locale; it is not there in the sense the invariant requires, as measured above. `vis(1)`, dated 2021, describes the same support for the command, whose binary contains no call to `setlocale`, so the command is `-N` whether or not you pass `-N`.

**`unvis(3)`'s BUGS section corrects two names and misses a decoder.** The page says `VIS_HTTP1866` should be named after RFC 1738 and HTML 2.0; it does not say that `&#65;` decodes to `G`.

**Neither page says that an unknown escape is silently accepted.** `\q` decodes to `q` with no `SYNBAD`; the page's wording, *an invalid escape sequence was detected*, applies only to an incomplete `\M` or `\^` or a trailing backslash.

**Neither page mentions `vis` is BSD-only.** There is no `STANDARDS` section on any of the four; a program that includes `<vis.h>` will not build on Linux, where the same job is done with `printf("%02x")` or an escaping function of your own.

## See also

- [`uuencode(1)`, `base64` and the binary-to-text pages](binary_to_text.md) — the other way to cross a channel that will not carry bytes: give up on readability
- [`od(1)`, `hexdump(1)` and `xxd(1)`](dump_tools.md) — the dumps, which are invertible and not text
- [`cat(1)` and the line tools](lines_and_fields.md) — `cat -v`, the same idea without the backslash
- [`multibyte(3)`](multibyte.md) — the other state machine with a caller-owned state and a flushing call
- [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) — the schemes `VIS_HTTPSTYLE` and `VIS_MIMESTYLE` are, at full length
- [The byte that means something to somebody else](../../12_Adversarial/in_band_signals/README.md) — why `VIS_GLOB` and `VIS_SHELL` exist
- [Terminal hyperlinks, and the URI that is not one](../../06_Terminal/terminal_hyperlinks/README.md) — percent-encoding where it is required
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — `cat -v`, and the ambiguity `vis` was written to remove
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) and [What the page does not say](../what_the_page_does_not_say/README.md) — the chapter
