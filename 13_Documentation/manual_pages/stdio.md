# `stdio(3)`, `fopen(3)`, `fgets(3)` and `fwide(3)`: every stream is bytes, and the locale is bolted on by the first wide call

**Level:** reference · for anyone who has written `fopen(path, "rb")` out of habit, or lost a line to `fgets` because it had a NUL in it, and wanted the pages that explain why

**One line:** On this Mac `"b"` is ignored and every stream is binary, a stream becomes byte- or wide-oriented on its first read and cannot change, `fgets` stops at a newline and cannot tell you about a NUL, and the wide functions decode through `LC_CTYPE` and hand back `WEOF` with `EILSEQ` when the bytes are wrong; glibc agrees with all of that except what happens when you ignore the orientation.

**The pages:** [`stdio(3)`](raw/macos/stdio.3.txt) (macOS, March 3, 2009) · [`fopen(3)`](raw/macos/fopen.3.txt) (September 1, 2023) · [`fgets(3)`](raw/macos/fgets.3.txt) (June 4, 1993) · [`fgetln(3)`](raw/macos/fgetln.3.txt) (April 19, 1994) · [`getline(3)`](raw/macos/getline.3.txt) (November 30, 2010) · [`fgetws(3)`](raw/macos/fgetws.3.txt) (August 6, 2002) · [`getwc(3)`](raw/macos/getwc.3.txt) and [`putwc(3)`](raw/macos/putwc.3.txt) (March 3, 2004) · [`fwide(3)`](raw/macos/fwide.3.txt) (October 24, 2001). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). Ubuntu has pages for all of these except `fgetln(3)`, which is BSD-only; the measurements below were repeated in ubuntu:24.04 (glibc 2.39, gcc 13) for comparison.

## What the pages are for

`stdio(3)` is the front page of the C standard I/O library, and the nine pages here are the ones a reader of this library will meet when text goes in or out of a C program: how a stream is opened, how a line is read, and what the wide-character twins of those calls do with the locale. They are all section 3, the library, and the dates run from 1993 to 2023: `fgets(3)` carries a 1993 date, the year after UTF-8 was designed, and `fopen(3)` a 2023 one, and it is the 2023 page that documents the `"x"` and `"e"` mode letters.

The reason they matter here is that they are where three of this library's rules touch C. [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) says a file is bytes and the line ending is data; `stdio(3)` says so in one sentence, and the experiment below shows `"r"` and `"rb"` returning the same six bytes. [The NUL byte](../../02_Characters/the_nul_byte/README.md) says the byte is legal in a file and fatal to a C string; `fgets(3)`, `fgetln(3)` and `getline(3)` are three answers to that, from three decades. And [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) says decoding is the moment invalid bytes should be caught; `fgetws(3)` and `getwc(3)` are that moment in C, they report it as `EILSEQ`, and the experiment shows what each C library does next.

The wide pages are the ones nobody opens. `fwide(3)` is forty lines and documents a property of a `FILE` that most C programmers never learn exists: orientation, chosen by the first I/O call and frozen thereafter. It is the mechanism by which the byte-decoding rule of [`multibyte(3)`](multibyte.md) is attached to a stream.

## The page, with notes

### `stdio(3)`: no text mode, and buffering by `isatty`

```text title="man 3 stdio, macOS 26.6.2, dumped 2026-09-13"
     This implementation makes no distinction between "text" and "binary"
     streams.  In effect, all streams are binary.  No translation is performed
     and no extra padding appears on any stream.
```

This is the sentence that settles `"rb"`. On Windows a text stream turns `0d 0a` into `0a` on the way in and back on the way out, and Python's `open(path)` in text mode does the same on every platform, which is why [Opening a file](../../04_Python/opening_a_file/README.md) spends a page on `newline=`. In a BSD or glibc libc there is nothing to switch off. The paragraph two above it is the one [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) is built on: *the standard input and output streams are fully buffered if and only if the streams do not refer to an interactive or "terminal" device, as determined by the isatty(3) function*, and *_exit(2) does not flush stdio files*. Put those two facts together and a program whose output appears on the screen can produce nothing at all in a pipe; the experiment reproduces it.

### `fopen(3)`: the mode letters

```text title="man 3 fopen, macOS 26.6.2, dumped 2026-09-13"
     An optional "+" following "r", "w", or "a" opens the file for both
     reading and writing.  An optional "x" following "w" or "w+" causes the
     fopen() call to fail if the file already exists.  An optional "e"
     following the above causes the fopen() call to set the FD_CLOEXEC flag on
     the underlying file descriptor.

     The mode string can also include the letter "b" after either the "+" or
     the first letter.  This is strictly for compatibility with ISO/IEC
     9899:1990 ("ISO C90") and has effect only for fmemopen(); otherwise "b"
     is ignored.
```

Three letters beyond `r`, `w` and `a`, and two of them are recent: `"x"` is C11's exclusive-create, the `O_EXCL` of `open(2)` for people who use streams, and `"e"` is close-on-exec, a BSD and glibc extension the STANDARDS section admits *does not conform to any standard*. `"b"` is the one this library cares about, and the page is unusually direct: kept for C90, *otherwise "b" is ignored*. The exception is `fmemopen`, where a text-mode buffer gets a NUL written after the last byte and a binary-mode buffer does not; the experiment checks that too, and finds glibc ignoring the letter even there. The STANDARDS paragraph ends with *The "b" mode does not conform to any standard but is also supported by glibc*, which contradicts the sentence above it (C90 defines `"b"`); read it as being about `fmemopen`'s use of the letter.

### `fgets(3)`, `fgetln(3)`, `getline(3)`: three ways to read a line, thirty years apart

```text title="man 3 fgets, macOS 26.6.2, dumped 2026-09-13"
     The fgets() function reads at most one less than the number of characters
     specified by size from the given stream and stores them in the string
     str.  Reading stops when a newline character is found, at end-of-file or
     error.  The newline, if any, is retained.  If any characters are read and
     there is no error, a `\0' character is appended to end the string.
```

Two things the page says and one it cannot. It says *characters* where it means bytes, because in 1993 they were the same thing, and the count `size` is a byte count on every machine. It says the newline is *retained*, which is the reason for the `strcspn(buf, "\n")` idiom and the subject of [The trailing newline](../../06_Terminal/trailing_newline/README.md). What it cannot say is how long the line was, because the only length `fgets` returns is the position of the first NUL, and if the file contained a NUL that is the wrong answer: [The NUL byte](../../02_Characters/the_nul_byte/README.md). The next two pages are the fixes.

```text title="man 3 fgetln, macOS 26.6.2, dumped 2026-09-13"
     The fgetln() function returns a pointer to the next line from the stream
     referenced by stream.  This line is not a C string as it does not end
     with a terminating NUL character.  The length of the line, including the
     final newline, is stored in the memory location to which len points.
```

```text title="man 3 getline, macOS 26.6.2, dumped 2026-09-13"
     The following code fragment reads lines from a file and writes them to
     standard output.  The fwrite() function is used in case the line contains
     embedded NUL characters.
     ...
BUGS
     There are no wide character versions of getdelim() or getline().
```

`fgetln` is 4.4BSD's answer, 1994: no copy, no NUL, a length, and a pointer that *becomes invalid after the next I/O operation*. `getline` is POSIX.1-2008's, *first appeared in FreeBSD 8.0* according to its HISTORY, and its page is dated 2010: it `realloc`s a buffer you own, returns the byte count as a `ssize_t`, and its own EXAMPLES section uses `fwrite` with that count rather than `fputs` for exactly the NUL reason. `fgetln` does not exist in glibc; the experiment shows the compiler saying so. And the BUGS line is honest about a gap: there is no `getwline`, so a program reading wide lines is back to `fgetws` and its fixed buffer.

### `fwide(3)`, `getwc(3)`, `fgetws(3)`, `putwc(3)`: orientation, and the locale

```text title="man 3 fwide, macOS 26.6.2, dumped 2026-09-13"
     If the orientation of stream has already been determined, fwide() leaves
     it unchanged.  Otherwise, fwide() sets the orientation of stream
     according to mode.

     If mode is less than zero, stream is set to be byte-oriented.  If mode is
     greater than zero, stream is set to be wide-oriented.  Otherwise, mode is
     zero, and stream is unchanged.
```

A fresh stream has no orientation. The first `fgetc` or `fputs` makes it byte-oriented; the first `getwc` or `fputws` makes it wide-oriented; `fwide(f, 0)` asks without changing, and `fwide(f, ±1)` is a request that is honoured only while the answer is still zero. What happens if you then use the other family is undefined in C, and the experiment shows the two libraries choosing differently. The wide-oriented functions are the ones that touch the locale: `getwc` runs [`mbrtowc(3)`](multibyte.md) on the bytes, `putwc` runs `wcrtomb`, and `fgetws(3)` names the failure:

```text title="man 3 fgetws, macOS 26.6.2, dumped 2026-09-13"
     [EILSEQ]           The data obtained from the input stream does not form
                        a valid multibyte character.
```

together with `getwc(3)`'s rule that *if the stream is at end-of-file or a read error occurs, the routines return WEOF* and *feof(3) and ferror(3) must be used to distinguish*. `WEOF` is the wide `EOF`, a `wint_t` value outside the range of any character, and `EILSEQ` is the same *illegal byte sequence* that [`iconv(3)`](iconv.md) and `mbrtowc` return. Which locale decodes is whichever `LC_CTYPE` the program set; a program that never called `setlocale` decodes in `"C"`, and the [`locale(1)`](locale.md) page measured that the two `"C"` locales disagree about what a high byte is. So does this one.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| stream, `FILE` | A buffered byte channel with a position, wrapped round a file descriptor; the unit `stdio` deals in | [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) |
| "text" and "binary" streams | The C standard's two stream kinds, which differ on Windows and not here; `"b"` selects the second | [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) |
| fully buffered, line buffered, unbuffered | When bytes leave the `FILE`: at 4 KB or so, at each newline, or at once; chosen by `isatty` unless `setvbuf` says otherwise | [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) |
| `isatty(3)` | The test for *is this file descriptor a terminal*, and therefore the switch between full and line buffering | [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) |
| `_exit(2)` | The system call that ends a process without flushing `stdio` buffers; `exit(3)` flushes first | |
| `"x"`, `"e"` | Create exclusively (fail if the file exists); set close-on-exec on the descriptor. C11 and an extension respectively | |
| `FD_CLOEXEC` | The descriptor flag that makes `exec` close it, so a child program does not inherit an open file | |
| `fmemopen` | A stream over a memory buffer; the one place on the Mac where `"b"` changes behaviour | |
| embedded NUL | A `00` byte in the middle of a line, legal in the file, terminator to `strlen`; the reason `fgetln` and `getline` return a count | [The NUL byte](../../02_Characters/the_nul_byte/README.md) |
| *the newline, if any, is retained* | `fgets` leaves `0a` in the buffer; the last line of a file may lack one | [The trailing newline](../../06_Terminal/trailing_newline/README.md) |
| `ssize_t`, `getdelim` | A signed byte count that can also be `-1`; the general form of `getline` with any delimiter, `\0` included | |
| orientation, byte-oriented, wide-oriented | Which family of functions a stream belongs to, set by the first I/O call, reported by `fwide` | [`multibyte(3)`](multibyte.md) |
| `wchar_t`, `wint_t`, `WEOF` | A decoded character, the wider type that can also hold `WEOF`, and the value meaning end or error | [`multibyte(3)`](multibyte.md) |
| `EILSEQ` | *Illegal byte sequence*: the bytes were not a valid character in the current `LC_CTYPE` | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `feof(3)`, `ferror(3)`, `clearerr(3)` | The two sticky flags a `NULL` or `WEOF` return forces you to consult, and the call that clears them | |
| `fgetws_l`, `getwc_l` | The `xlocale` twins that decode through an explicit `locale_t` instead of the global locale | [`locale(1)` and `xlocale(3)`](locale.md) |
| `ungetwc(3)` | Push one wide character back; the reason a decoder can peek | |

## Try it on your machine

**`"r"` and `"rb"` read the same bytes.** A file holding `a CR LF b CR LF`, read with `fread` through both modes.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21) and ubuntu:24.04 (gcc 13, glibc 2.39); byte-identical on both. Not machine-checked."
fopen("crlf.txt", "r "): fread -> 6 bytes: 61 0d 0a 62 0d 0a
fopen("crlf.txt", "rb"): fread -> 6 bytes: 61 0d 0a 62 0d 0a
```

**Orientation is set once, and the two libraries differ on what an ill-oriented call gets.** Three streams over the same file: one read first with `getwc`, one with `fgetc`, one told its orientation before any I/O.

```text title="Measured 2026-09-13 — macOS 26.6.2 under en_US.UTF-8 and ubuntu:24.04 under C.UTF-8. Not machine-checked."
                                                        macOS              ubuntu:24.04
stream f: fwide(f, 0) after fopen                       0                  0
          getwc -> U+0061; fwide(f, 0) now              1                  1
          fwide(f, -1) asking for bytes returns         1                  1
          fgetc on the wide-oriented stream ->          13 (the next byte) -1 (EOF)
stream g: fgetc -> 0x61; fwide(g, 0) now                -1                 -1
          fwide(g, +1) asking for wide returns          -1                 -1
          getwc on the byte-oriented stream ->          a character        WEOF
stream h: fwide(h, +1) before any I/O returns           1                  1
```

Both libraries obey the page: zero, then a sign that never changes. Beyond the page, the Mac lets a wide stream be read as bytes and a byte stream as wide characters, and glibc refuses both with an end-of-file that is not one. A program that mixes `printf` and `wprintf` on `stdout` works on one machine and prints nothing on the other, with no error.

**`fgets` and a NUL.** The file holds `61 00 62 0a`. `fgets` reads all four bytes and reports one.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04; identical except that glibc has no fgetln. Not machine-checked."
fgets   -> buf, strlen(buf) = 1, buf holds: 61 00 62 0a 00
getline -> 4, line holds: 61 00 62 0a
fgetln  -> len 4, line holds: 61 00 62 0a                          (macOS only)
$ cc -std=c11 -Wall -Wextra s5.c                                    (ubuntu:24.04, a one-line program calling fgetln)
s5.c:2:38: warning: implicit declaration of function ‘fgetln’; did you mean ‘fgets’? [-Wimplicit-function-declaration]
```

**`fgetws` through two locales, over `caf` `c3 a9` `0a` `ff` `0a` `last` `0a`.** The program calls `setlocale(LC_ALL, "")` and reads four times.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04 (glibc 2.39). Not machine-checked."
                  macOS                                                    ubuntu:24.04
LC_ALL=C          call 1: U+0063 U+0061 U+0066 U+00C3 U+00A9 U+000A         call 1: NULL, errno=84 (Invalid or incomplete multibyte or wide character), feof=0, ferror=1
                  call 2: U+00FF U+000A                                     call 2: NULL, errno=84, feof=0, ferror=1
                  call 3: U+006C U+0061 U+0073 U+0074 U+000A                call 3: NULL, errno=84, feof=0, ferror=1
                  call 4: NULL, errno=0, feof=1, ferror=0                   call 4: NULL, errno=84, feof=0, ferror=1
LC_ALL=en_US.UTF-8 / C.UTF-8
                  call 1: U+0063 U+0061 U+0066 U+00E9 U+000A                call 1: U+0063 U+0061 U+0066 U+00E9 U+000A
                  call 2: NULL, errno=92 (Illegal byte sequence), feof=0, ferror=0
                                                                            call 2: NULL, errno=84, feof=0, ferror=1
                  call 3: NULL, errno=92, feof=0, ferror=0                  call 3: NULL, errno=84, feof=0, ferror=1
                  call 4: NULL, errno=92, feof=0, ferror=0                  call 4: NULL, errno=84, feof=0, ferror=1
```

Under UTF-8 the two agree on the first line, `é` as `U+00E9`, and on the second: the bare `ff` is `EILSEQ`, the page's wording exactly. Two differences after that. glibc sets `ferror`, the Mac does not, so on the Mac `feof`/`ferror`, which the page says *must be used to determine which occurred*, both say nothing happened. And neither library moves past the bad byte: calls 3 and 4 fail identically, `last` is never read, and the stream is stuck. Under `C`, the Mac reads every byte as a character, `U+00C3 U+00A9` for `é` and `U+00FF` for the bad byte, with no error at all; glibc fails on the first line, because `c3` is not ASCII. Same program, same file, four different transcripts.

**`putwc` under `C`.** One wide `é` written to a piped `stdout`.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
                       bytes written     return value      errno
macOS   LC_ALL=C       e9                the character     0
ubuntu  LC_ALL=C       3f                the character     0
both    UTF-8 locale   c3 a9             the character     0
```

The Mac's eight-bit `C` locale writes the byte `e9`, Latin-1 by accident; glibc writes `?` and reports success, which is a substitution the `putwc(3)` page does not mention.

**Buffering, seen.** A program that prints a line and a partial line, then calls `_exit(0)`.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04; identical. Not machine-checked."
stdout is a pipe:   []                                (both printf calls lost)
stdout is a pty:    [isatty(1)=1 hello|]              (the line with the newline flushed; the partial line lost)
stdbuf -o0, pipe:   [isatty(1)=0 hello|partial line]  (unbuffered: everything)
```

**`fmemopen` and the one `"b"` that means something.** `fputs("abc")` into an 8-byte buffer of `X`s.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04 (glibc 2.39). Not machine-checked."
                                     macOS                     ubuntu:24.04
fmemopen(buf, 8, "w"),  fclose       61 62 63 00 58 58 58 58   61 62 63 00 58 58 58 58
fmemopen(buf, 8, "wb"), fclose       61 62 63 58 58 58 58 58   61 62 63 00 58 58 58 58
```

The Mac does what its page says. glibc writes the NUL in both modes, so the letter the Mac page says is *also supported by glibc* changes nothing there either.

## Where the page is dated, and what it does not say

**`fgets(3)` is dated June 4, 1993 and says *characters*.** Every count on the page is a byte count, and the page predates the distinction; `fgetws(3)` from 2002 uses the same words for wide characters, where they are true. Neither page says that `size - 1` bytes may end in the middle of a multibyte character, which is the [Slicing by byte](../../05_Rust/slicing_by_byte/README.md) problem with a C signature.

**`fopen(3)` is the newest page in the family and still has a contradictory STANDARDS paragraph.** It says `"b"` is *strictly for compatibility with ISO/IEC 9899:1990* and then that it *does not conform to any standard*. The `fmemopen` measurement shows the second sentence being about `fmemopen`, and shows glibc not supporting it there.

**`fwide(3)` does not say what happens if you ignore it.** The C standard leaves it undefined; the two libraries measured above differ, and glibc's answer, `EOF` and `WEOF` with no `errno`, is indistinguishable from an empty file.

**`fgetws(3)` and `getwc(3)` do not say the stream stays stuck.** After `EILSEQ` neither library skips the bad byte or advances, and neither page says whether `clearerr` would help or what would. The error is reported once per call, forever.

**`putwc(3)` does not mention substitution.** Its RETURN VALUES promise `WEOF` on error; glibc's `C` locale wrote `?` and returned the character.

**None of the nine pages mention `LC_CTYPE` or `setlocale` by name**, except `fgetws(3)`'s pointer to `xlocale(3)`. The wide functions cannot be understood without the [`locale(1)` and `setlocale(3)`](locale.md) page, and nothing here says so.

## See also

- [`multibyte(3)`](multibyte.md) — `mbrtowc` and `wcrtomb`, which are what `getwc` and `putwc` run on each character
- [`printf(3)` and `printf(1)`](printf.md) — the formatted side of the same streams, and `%ls` failing under `C`
- [`locale(1)`, `setlocale(3)` and `xlocale(3)`](locale.md) — which `LC_CTYPE` the wide functions decode through, and why the two `C` locales differ
- [The NUL byte](../../02_Characters/the_nul_byte/README.md) — why `fgets` reported 1 for a 4-byte line
- [The trailing newline](../../06_Terminal/trailing_newline/README.md) — the `0a` that `fgets` and `getline` keep
- [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) — the translation that `"b"` switches off on Windows and that does not exist here
- [Opening a file](../../04_Python/opening_a_file/README.md) — the language where `'rb'` and `newline=` do matter
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — the `EILSEQ` moment, and why a stuck stream is the right outcome
- [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) — `isatty`, full buffering, and the output that never arrived
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) and [What the page does not say](../what_the_page_does_not_say/README.md) — the chapter
