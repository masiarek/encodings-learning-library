# Opening a file

**Level:** 101 → 201 · for Python programmers

**One line:** `open(path)` with no `encoding=` is a bet on the machine's locale, and the only portable call is `open(path, encoding='utf-8')`; `'rb'` is how you refuse to bet at all.

```python
open("data.csv", encoding="utf-8")            # says what it means, everywhere
open("data.csv", "rb")                        # refuses to guess; decide later
open("data.csv")                              # asks a machine you have not met
```

Three calls, and only the third one's behaviour depends on who runs it.

## Which library answers which question

`open()` makes four decisions — `mode`, `buffering`, `encoding` and `newline` — and this page is about one of them. The Python library has a page with the same name, [Opening a file ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/opening_a_file/index.html), and the two split the subject down one line, settled on 2026-09-08: **this library owns the codec, that one owns the call.**

**Here, the codec.** Which encoding the default resolves to, and on which machine; UTF-8 Mode and PEP 686; what a wrong bet looks like when it finally surfaces; and how to find every unnamed `open()` in a codebase before it does.

**There, the call.** What each `mode` does, including the truncation that happens at `open()` before a byte is written; when your output actually leaves the process; why `tell()` in text mode returns a cookie rather than a position; how many lines a file has, which depends on who is counting; how to replace a file without a reader ever seeing half of it; and the same calls side by side in Rust, C and ABAP. Line endings come up on this page only as the second way a string can differ from its file.

The two halves meet on stdout, and [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) is where this library measures the meeting: `print()` makes this page's bet on the way out, and on macOS and Linux a pipe changes *when* that output leaves, never *which encoding* it leaves in. The Python library's page measures the *when* half again, as part of `buffering`.

## What the bet is on

`open()` in text mode has to turn bytes into a `str`, so it needs an encoding. Give it none and it asks the C library what the current locale's encoding is, and uses that.

That is a question about the machine, not about the file. The file has no encoding recorded anywhere — [a file is bytes](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md), and nothing in it says what they mean. So the same script, the same file, and two machines give you two different strings, and on a good day one of them raises.

The values you will actually meet:

| where it runs | the locale's encoding | what `open(path)` does with UTF-8 bytes |
|---|---|---|
| your laptop, a UTF-8 locale | UTF-8 | reads correctly |
| a container, cron, systemd, CI | ASCII (the C locale) | `UnicodeDecodeError` on the first non-ASCII byte |
| a colleague's Windows box | cp1252, or cp932, or… | reads *something*, raises nothing |

The third row is the one that matters. The first two are a working program and a loud failure; the third is [mojibake](../../03_Encodings/mojibake/README.md) with a zero exit status, travelling onward into whatever you write next.

## This page's own environment is rigged, and says so

Every example in this library runs under a [fixed environment](../../CONTRIBUTING.md) — `LC_ALL=C`, `LANG=C`, `PYTHONUTF8=1` — so an answer key does not depend on whose machine recorded it. For this page that environment is a problem: it leaves the interpreter in UTF-8 Mode, and UTF-8 Mode is precisely what stops `open()`'s default from being the locale's. A naive example here would demonstrate the opposite of its own thesis and record a passing answer key while doing it.

The variable named after the mode is not what turns it on. The runner starts Python with `-I`, which implies `-E`, and `-E` ignores every `PYTHON*` variable — `PYTHONUTF8=1` included. UTF-8 Mode is on because `LC_ALL=C` is a C locale, and [PEP 540 ↗](https://peps.python.org/pep-0540/) switches the mode on by itself under one. Section 0 of the program shows both halves: a child started the runner's way and told `PYTHONUTF8=0` comes up in UTF-8 Mode anyway. The Python library's page reads the same two flags side by side, in [The environment this page runs in ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/opening_a_file/index.html#the-environment-this-page-runs-in-and-why-it-matters-here-more-than-elsewhere).

So the program takes CONTRIBUTING's carve-out for a lesson whose subject *is* the environment: it sets its own, in view, and every answer about a default comes from a **child interpreter** whose variables are printed beside the result — started without `-I`, so that it hears them, and without the runner's `PYTHONUTF8=1`, which a child that hears its variables would obey. Nothing below asks the running process what `open()` would do.

## The program

<!-- output:opening_a_file_py -->
*Verified output of [`opening_a_file_py.py`](examples/opening_a_file_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
0. THIS PROGRAM'S OWN ENVIRONMENT IS RIGGED
------------------------------------------------------------------------
   The library runs every example under LC_ALL=C and LANG=C so that
   answer keys do not depend on whose machine recorded them. For this
   page that is a problem, because it leaves this interpreter in UTF-8
   Mode -- the switch that stops open() asking the locale at all:

     sys.flags.utf8_mode:                   1

   The runner also sets PYTHONUTF8=1, and that is NOT why:

     PYTHONUTF8 in os.environ:              1
     sys.flags.isolated (-I):               1
     sys.flags.ignore_environment (-E):     1

   The runner starts Python with -I, which implies -E, and -E ignores
   every PYTHON* variable -- this one included. UTF-8 Mode is on for
   the reason section 1's bottom row shows: the locale is C, and
   PEP 540 turns a C locale into UTF-8 Mode by itself. Two children,
   both under LC_ALL=C and both told PYTHONUTF8=0, settle which:

     python3 -I   utf8_mode 1   the variable is ignored
     python3      utf8_mode 0   without -I, it is obeyed

   So nothing below asks THIS interpreter what open() would do. Each
   answer comes from a child whose environment is printed with it, and
   none of those children gets -I: they have to hear their variables.

1. WHAT open() BETS ON
------------------------------------------------------------------------
     child env        utf8_mode  open()    print()     io.text_encoding
     PYTHONUTF8=1     1          utf-8     utf-8       utf-8
     PYTHONUTF8=0     0          ascii     ascii       locale
     (unset)          1          utf-8     utf-8       utf-8

   Three things in that table.

   The middle row is the honest default: under a C locale with UTF-8
   Mode off, open() decodes as ASCII -- so any byte over 127 ends the
   program. That is what a container, a cron job and a systemd unit
   look like unless somebody set a variable.

   The bottom row turned UTF-8 Mode on WITHOUT being asked. PEP 540
   reads a C locale as a machine describing its own configuration
   rather than its data, and overrides it. The locale page works
   through that; the point here is only that the default has to be
   asked about rather than assumed.

   The print() column is the same bet made on the way OUT, and it is
   why a script that prints an e-acute happily in your terminal dies
   under cron: cron does not set your locale. Nothing about the
   program changed -- only who started it.

   io.text_encoding(None) answers 'locale' rather than a name. That
   string IS the encoding argument that means 'go and ask' -- it is
   what open() uses when you pass nothing.

2. ONE FILE, FOUR READINGS
------------------------------------------------------------------------
   A file holding the four characters c-a-f-e-acute, written UTF-8:

     bytes on disk    63 61 66 c3 a9 0a

   Read with an encoding named explicitly, four ways. Only the
   first is right, and only the second says so:

     encoding  result              code points
     utf-8     caf\xe9             U+0063 U+0061 U+0066 U+00E9
     ascii     UnicodeDecodeError  byte 3 is not ASCII
     cp1252    caf\xc3\xa9         U+0063 U+0061 U+0066 U+00C3 U+00A9
     latin-1   caf\xc3\xa9         U+0063 U+0061 U+0066 U+00C3 U+00A9

   And the reading that refuses to bet at all:

     'rb'      bytes               63 61 66 c3 a9 0a

   The ASCII row is the safe failure: it stops. The cp1252 and
   latin-1 rows are the dangerous ones -- five characters where the
   file has four, no error, no exit status, and the corruption
   travels onward into whatever you write next.

3. THE FLIP PEP 686 CAUSES, AND WHY IT IS QUIET
------------------------------------------------------------------------
   PEP 686 makes UTF-8 Mode the default, so open()'s guess stops
   depending on the machine. Most code this silently FIXES. The
   case it silently breaks needs bytes that decode cleanly under
   both the old default and the new one -- and there are two of
   them right here:

     bytes on disk    63 61 66 c3 a9 0a

     read as                result              code points
     cp1252 (a Windows box) caf\xc3\xa9         U+0063 U+0061 U+0066 U+00C3 U+00A9
     utf-8 (after PEP 686)  caf\xe9             U+0063 U+0061 U+0066 U+00E9

   No exception on either line. Same file, same call, two answers,
   and the only thing that changed was a default. That pair --
   C3 A9 read as two Latin-1 letters -- is the mojibake this
   library keeps meeting; here it is arriving as an UPGRADE.

   The other direction is louder and so matters less. A genuine
   Windows-1252 file:

     bytes on disk    63 61 66 e9 0a
     read as cp1252         caf\xe9             U+0063 U+0061 U+0066 U+00E9
     read as utf-8          UnicodeDecodeError  byte 3 cannot start a sequence

   That one you find on the first run. It is the quiet row above
   that reaches production.

4. FINDING THESE CALLS IN CODE YOU ALREADY HAVE
------------------------------------------------------------------------
   PEP 597 added a warning for exactly this, and it is off by
   default. Turn it on and every open() that did not say an
   encoding reports itself:

     python3 -X warn_default_encoding  (or PYTHONWARNDEFAULTENCODING=1)
       warnings raised: 1
       EncodingWarning from line 4

     without the flag:
       warnings raised: 0

   One call warned and one did not, and the difference between them
   is the whole lesson: the second one said encoding='utf-8'.

   Only the warning's CLASS is printed above. Its wording is
   CPython's and may be reworded in any release, which is not
   something this library puts in an answer key.

   If you WRITE functions that take an encoding argument, there is
   a matching call for the other side of the boundary:

     def load(path, encoding=None):
         encoding = io.text_encoding(encoding)   # <- one line
         return open(path, encoding=encoding).read()

   io.text_encoding() returns 'locale' or 'utf-8' as appropriate
   AND blames the caller's line rather than yours, so the warning
   points at the code that has to change.

5. TEXT MODE ALSO REWRITES YOUR LINE ENDINGS
------------------------------------------------------------------------
   Encoding is not the only thing open() decides. In text mode it
   translates line endings on the way in, which is a second silent
   difference between the file and the string:

     bytes on disk               61 0d 0a 62 0a
     open(..., encoding='utf-8') 'a\nb\n'
     ... plus newline=''         'a\r\nb\n'
     open(..., 'rb')             b'a\r\nb\n'

   The default is usually what you want for reading prose and is
   wrong for the csv module, which does its own line handling and
   documents newline='' as required -- a quoted field is allowed to
   contain a bare CR or LF, and translating it corrupts the record.

6. AND open() DOES NOT NORMALISE
------------------------------------------------------------------------
   Decoding settles which characters the bytes name. It does not
   settle which SPELLING of a character was written, and the
   e-acute has two:

     form     chars  bytes on disk          code points
     NFC      4      63 61 66 c3 a9         U+0063 U+0061 U+0066 U+00E9
     NFD      5      63 61 66 65 cc 81      U+0063 U+0061 U+0066 U+0065 U+0301

     the two strings compare equal:           False
     ...after unicodedata.normalize('NFC'):   True

   Both files are valid UTF-8, both were read with the correct
   encoding, both print the same word, and they are not the same
   string. encoding= was never the question here -- which is worth
   knowing before you spend an afternoon on it.

7. THE RULE
------------------------------------------------------------------------
     open(path, encoding='utf-8')   says what it means, everywhere
     open(path, 'rb')               refuses to guess; decide later
     open(path)                     asks a machine you have not met

   Pass encoding=, and nothing on this page can reach your program.
```
<!-- /output -->

## Two things that could not go in the answer key

Both are facts about the machine rather than about Python, and both were caught by running the program on macOS and in a Debian container before recording anything. UTF-8 Mode changes what each one looks like, so each machine is measured twice — with the mode off, as in the middle row of section 1, and with `LC_ALL=C` alone, which switches it on:

```text title="Measured 2026-09-10 under LC_ALL=C, the Debian column in python:3.13-slim under Docker — not machine-checked: the two columns disagree"
                                      macOS 26.6.2     Debian 13.6
                                      CPython 3.14.7   CPython 3.13.15
UTF-8 Mode off (PYTHONUTF8=0)
  open(path).encoding                 'US-ASCII'       'ANSI_X3.4-1968'
  locale.getpreferredencoding(False)  'US-ASCII'       'ANSI_X3.4-1968'
  locale.getencoding()                'US-ASCII'       'ANSI_X3.4-1968'
  codecs.lookup(any of them).name     'ascii'          'ascii'
  sys.getfilesystemencoding()         'utf-8'          'ascii'
UTF-8 Mode on (PYTHONUTF8 unset; PEP 540)
  open(path).encoding                 'utf-8'          'utf-8'
  locale.getpreferredencoding(False)  'utf-8'          'utf-8'
  locale.getencoding()                'US-ASCII'       'ANSI_X3.4-1968'
  sys.getfilesystemencoding()         'utf-8'          'utf-8'
```

**Two functions that look alike answer different questions.** `locale.getpreferredencoding(False)` answers the one `open()` asks — *what do I use when nobody said?* — so it moves with UTF-8 Mode, and `open()` moves with it. `locale.getencoding()` asks the locale and nothing else, and is the only line that reads the same in both halves. [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) meets the same pair from the locale's side.

**The spelling** is why the program never prints the locale's encoding by name: the C locale has two, one per C library, and `getencoding()` shows the machine's with the mode on or off. `codecs.lookup().name` canonicalises both, which is the recordable form and the one to use in your own code — comparing `enc == 'utf-8'` is a bug waiting for a machine that spells it `UTF8`.

**The filesystem encoding** is sharper, and is the reason `sys.getfilesystemencoding()` is not in the table the program prints. With UTF-8 Mode off, macOS answers `utf-8` where glibc answers `ascii`, because the Mac's filesystem *requires* valid UTF-8 filenames and CPython hardcodes it accordingly — the Python-side face of the same fact [`find`, and filenames that are bytes](../../11_Tools/find/README.md) measures from the shell, where APFS refuses a non-UTF-8 name with `Errno 92` and Linux accepts any bytes but `NUL` and `/`. With the mode on, both say `utf-8`: Python stops disagreeing, and the filesystems underneath disagree exactly as much as before.

## Finding these calls in code you already have

[PEP 597 ↗](https://peps.python.org/pep-0597/) added `EncodingWarning` for exactly this, and it is **off by default** — you have to ask:

```bash
python3 -X warn_default_encoding your_script.py
```

or `PYTHONWARNDEFAULTENCODING=1` in the environment. Every `open()` that did not name an encoding then reports itself, at the line that called it. On the builds above the message reads `EncodingWarning: 'encoding' argument not specified`, but the program prints only the warning's *class*: CPython's wording is CPython's, and [an interpreter's diagnostic text is not a property of your data](../../CONTRIBUTING.md).

If you *write* functions that take an encoding, there is a matching call for the other side of the boundary:

```python
import io

def load(path, encoding=None):
    encoding = io.text_encoding(encoding)     # 'locale' or 'utf-8', and blames the caller
    return open(path, encoding=encoding).read()
```

`io.text_encoding()` resolves `None` the way `open()` would, and — the part worth the line — attributes the warning to *your caller's* line rather than to yours. Without it, a library that helpfully defaults `encoding=None` turns every one of its users' warnings into a report about the library.

## What PEP 686 changes, and what it quietly does not

[PEP 686 ↗](https://peps.python.org/pep-0686/) makes UTF-8 Mode the default, which removes the machine from the answer. Most code this silently **fixes**: the container that crashed and the Windows box that mangled will both start agreeing with the laptop.

The interesting half is what it silently breaks, and it needs bytes that decode cleanly under *both* defaults — no exception either way, just a different answer. Section 3 of the program has the canonical pair: `C3 A9` is `é` in UTF-8 and `Ã©` in cp1252, and both are valid. A Windows program that was correctly reading a cp1252 file will, after the flip, read the same bytes as UTF-8 and get different characters, with nothing raised and nothing logged.

The louder direction — a genuine cp1252 file read as UTF-8 — raises on the first run and gets fixed that afternoon. It is the quiet one that reaches production, and the defence is the same as it has always been: name the encoding, and the default cannot reach you.

## Two things `encoding=` does not settle

**Line endings.** Naming the encoding does not hand you the file's characters as written: text mode decodes and *then* translates, so the `\r\n` in the file arrives as `\n` in the string — section 5 of the program has the bytes. That is as much of `newline=` as this page needs. The rest of it is the call's half, measured in [the Python library's page ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/opening_a_file/index.html): the lone `\r` that universal newlines also rewrites, and how many lines one file has depending on who is counting. The bytes themselves are [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md), and [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md) is where `encoding='utf-8-sig'` and `newline=''` belong in the same call.

**Normalization.** Decoding settles which characters the bytes name; it does not settle which *spelling* was written. `é` has two — one code point (`U+00E9`) or two (`U+0065 U+0301`) — and both are valid UTF-8, both read back correctly, and the two strings are not equal. Section 6 of the program shows it. `encoding=` was never the question there, which is worth knowing before you spend an afternoon on it; [Normalization](../normalization/README.md) is.

## If you are coming from Python or ABAP

**Python.** The rule is one line long — pass `encoding=` at every text boundary — and the boundaries are more numerous than `open()`: `subprocess.run(text=True)`, `pathlib.Path.read_text()`, `csv`, `configparser`, `json.load` on a file object, `tempfile` in text mode, and `sys.stdout` itself all make the same guess. Three habits worth the keystrokes. Use `errors=` deliberately rather than reaching for it in a panic — [Encode, decode and errors](../encode_decode_and_errors/README.md) has the eight of them, and `'ignore'` is never the answer. Prefer `'rb'` plus an explicit `.decode()` when you do not yet know what a file is, which is [the habit this whole library teaches](../../10_Best_Practices/interfaces_and_storage/README.md): look at the bytes, then decide. And for output, `print()` inherits `sys.stdout`'s encoding from the environment, so a script that prints an `é` on your terminal can raise under `cron` — `PYTHONIOENCODING=utf-8` in the unit file is the fix, and naming it beats discovering it.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* ABAP made the argument compulsory where Python made it optional, and the comparison flatters ABAP. `OPEN DATASET` will not compile without a mode: `IN BINARY MODE` is Python's `'rb'`, and `IN TEXT MODE` *requires* an `ENCODING` addition. `ENCODING UTF-8` is `encoding='utf-8'` and is what you want; `ENCODING DEFAULT` is the bet — on a Unicode system it resolves to UTF-8, on a non-Unicode one to the system code page — and `ENCODING NON-UNICODE` asks for that code page explicitly. So the failure mode Python has does not exist here; what does exist is `ENCODING DEFAULT` written by habit in a program that will one day be read on a system configured differently, which is the same bug with a longer name. For in-memory conversion the pair is `cl_abap_conv_in_ce` / `cl_abap_conv_out_ce` (newer systems: `cl_abap_conv_codepage`), and any code-page number you find in a document is something to verify against the system that will run the job rather than to copy.

## Try it

- `python3 -c "import locale, codecs; print(codecs.lookup(locale.getpreferredencoding(False)).name)"` on your laptop, then the same line in a container with a C locale and UTF-8 Mode off: `docker run --rm -e LC_ALL=C -e PYTHONUTF8=0 python:3-slim python3 -c "import locale, codecs; print(codecs.lookup(locale.getpreferredencoding(False)).name)"`. On a Mac or a Linux laptop the first says `utf-8`; the container says `ascii`. Two machines, two answers, and neither of them consulted a file. Both `-e` flags are needed: without `PYTHONUTF8=0` the C locale switches UTF-8 Mode on by itself, and without `LC_ALL=C` the image — which sets no locale at all — has its missing locale coerced to `C.UTF-8` ([PEP 538 ↗](https://peps.python.org/pep-0538/)). Either way the container says `utf-8` too.
- Run your own project under `python3 -X warn_default_encoding -m pytest` (or however it starts) and count the warnings. Every one is a call that behaves differently on somebody else's machine.
- Take the worst CSV you have, `head -c 3 file.csv | xxd`, and decide from the bytes whether it needs `utf-8-sig`. Then open it with `encoding='utf-8'` and `newline=''` and see whether the first column's name still has something invisible in front of it.
- `git grep -n "open(" | grep -v encoding=` in a repo you maintain. The interesting hits are the ones reading data somebody else produced.

## Practice

**One file, and a default you cannot see.** A file holds the six bytes `63 61 66 c3 a9 0a`. Predict, for each of `encoding='utf-8'`, `'ascii'`, `'cp1252'` and `mode='rb'`: what comes back, how many characters it has, and which of the four raises.

Then answer the harder one. The script runs on a laptop with a UTF-8 locale, in a container with none, and on a Windows machine — with **no** `encoding=` anywhere. Say which of the three gets the right answer, which fails loudly, which fails silently, and what changes on each of the three after PEP 686.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:opening_a_file_kata_py -->
*Verified output of [`opening_a_file_kata_py.py`](examples/opening_a_file_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
ONE FILE, FOUR READINGS
   bytes on disk   63 61 66 c3 a9 0a

   encoding   result              chars  code points
   utf-8      caf\xe9             4      U+0063 U+0061 U+0066 U+00E9
   ascii      UnicodeDecodeError  -      byte 3 is over 127
   cp1252     caf\xc3\xa9         5      U+0063 U+0061 U+0066 U+00C3 U+00A9
   'rb'       bytes               6      63 61 66 c3 a9 0a

   Only 'ascii' raises. utf-8 gives four characters, cp1252 gives
   five, and the extra one is not an error -- C3 and A9 are both
   perfectly good Windows-1252 letters. 'rb' gives six bytes and
   no opinion, which is the only honest answer before you know
   what wrote the file.

THE SAME SCRIPT ON THREE MACHINES, WITH NO encoding= ANYWHERE

   machine                default   result        how it fails
   laptop, UTF-8 locale   utf-8     caf\xe9       it does not
   container, C locale    ascii     raises        loudly, first run
   Windows, cp1252        cp1252    caf\xc3\xa9   silently, forever

   One file. One script. Three answers, and the exit status is 0 on
   two of them.

AND WHAT PEP 686 DOES TO EACH ROW

   laptop      no change -- it was already UTF-8 Mode in all but name
   container   FIXED, silently: the crash stops, and nobody learns
               that the machine was misconfigured
   Windows     CHANGED, silently: the same bytes now decode as UTF-8,
               so the third row above turns into the first one.
               Right answer, no announcement -- and for a file that
               really was cp1252, the reverse: it starts raising.

   The pattern is the point. A default that becomes correct is still
   a default that changed, and the code that was relying on the old
   one gets no warning at all. Both rows below the first are fixed
   permanently by one keyword argument, today, on every Python.

THE ONE LINE
   open(path, encoding='utf-8')   and PEP 686 cannot reach you either.
```
<!-- /output -->

</details>

## See also

- [Encode, decode and errors](../encode_decode_and_errors/README.md) — the same two arguments, and what each `errors=` policy throws away
- [Normalization](../normalization/README.md) — the difference `encoding=` cannot fix
- [`str` vs `bytes`](../str_vs_bytes/README.md) — what `'rb'` hands you instead
- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — where the locale's encoding comes from, and what Python declines to take from it
- [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) — this page's bet on the way out: a pipe changes `sys.stdout`'s buffering and not its encoding
- [Mojibake](../../03_Encodings/mojibake/README.md) — the silent row of the table above, in full
- [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md) — `utf-8-sig` and `newline=''` in one call
- [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) — the translation text mode performs
- [`find`, and filenames that are bytes](../../11_Tools/find/README.md) — why macOS reports a different filesystem encoding
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — decode at the boundary, and write the encoding into the contract
- [Opening a file ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/opening_a_file/index.html) — the other half of this subject, in the Python library: `mode`, buffering, the `tell()` cookie, counting lines, and replacing a file safely
- [PEP 540 — UTF-8 Mode ↗](https://peps.python.org/pep-0540/) — the switch, and why a C locale turns it on by itself
- [PEP 597 — Add optional EncodingWarning ↗](https://peps.python.org/pep-0597/) — the warning and `io.text_encoding()`
- [PEP 686 — Make UTF-8 mode default ↗](https://peps.python.org/pep-0686/) — the plan, and its own account of what it breaks
