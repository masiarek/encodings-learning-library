# CRLF vs LF

**Level:** 101 → 201 · for anyone whose files cross between Windows and Unix

**One line:** A Windows line ends `0d 0a` and a Unix line ends `0a`, and because every tool that shows you *text* hides the extra byte, the failure is never a crash — it is a report whose totals are right to the cent and whose keys match nothing.

## One byte, and it is never the one you are looking at

`LF` and `CR` were two separate motions on a teletype: feed the paper down one line, return the carriage to the left margin. Unix decided the first implied the second and kept `LF` alone. DOS kept both, Windows inherited that, and so did every protocol drafted while DOS was current — HTTP, SMTP, FTP and NNTP all still *require* `CR LF`. The [control characters](../../02_Characters/control_characters/README.md) page is where those two bytes are defined; this page is what to do when a file has the wrong ones.

What makes it a chapter-7 problem rather than a footnote is that the byte is **structurally invisible**. `cat` prints the same characters. An editor draws the same lines. A screenshot is identical, and so is a paste into a chat window — a carriage return moves the cursor to column zero, so a CR pasted into a message *erases the text in front of it* rather than appearing. The one byte this page is about is the one byte that cannot show up in a description of itself, which is why a colleague can send you the header, swear it says `active`, and be looking at `active\r` while they do it.

So the first move is to stop reading the text:

```bash
file report.csv     # ASCII text, with CRLF line terminators
```

`file(1)` reads the ending out of the bytes and says so in words — `with CRLF line terminators`, `with CR line terminators`, or nothing at all for plain LF. It is the fastest question you can ask about a file somebody sent you, it names a **mixed** file as `with CRLF, LF line terminators`, and its wording is identical on macOS and Ubuntu (measured 2026-09-07 on file-5.41 and file-5.45). When you want to see the byte rather than be told about it, `cat -vet` draws it as `^M` before the `$` that is the LF, and `xxd` shows `0d 0a`.

## The interface that half-works

The reason this survives testing is that the damage sorts itself by column type. `int('42\r')` is `42` and `float('3.5\r')` is `3.5` — Python's numeric parsers skip surrounding whitespace, and a carriage return is whitespace. `'Y\r' == 'Y'` is `False`.

**Numbers reconcile. Keys, codes, flags, and dates-held-as-text do not.** An interface with a stray CR on the last field of every record therefore produces a report whose totals are correct to the cent and whose lookups match nothing, which reads like a mapping error, a missing master record, or a bad join — anything except a line ending. Section 3 of the Python run below prints the two comparisons next to each other, because seeing them together is the moment this stops being mysterious.

It is the same shape as the [BOM in a CSV](../bom_in_a_csv/README.md), one byte along and at the other end of the line: an invisible character welded to a field, breaking equality while printing as nothing.

## Two commands strip it, and they are not the same command

```bash
tr -d '\r'  < in.txt > out.txt    # every CR in the file, wherever it sits
sed 's/\r$//' in.txt > out.txt    # only a CR that ends a line
```

Both are installed everywhere. On a file whose CRs are all line endings they produce the same bytes; on a file with a CR in the *middle* of a line they do not, and only you know whether such a CR is damage or data. `dos2unix` does the `sed` job with a safety net — it refuses a binary file and preserves the mode bits — and is the right thing to type at a keyboard, but it ships with neither macOS nor a stock Ubuntu, so keep it out of scripts that have to run anywhere. Going the other way, `sed 's/$/\r/'` is `unix2dos`; `tr` cannot do that direction at all, because `tr` substitutes and deletes and never inserts.

Worth knowing before you reach for either, because the folklore here is stale and the reason it exists is still good. The lore says `\r` in a `sed` pattern is a GNU extension that BSD `sed` does not understand. Measured 2026-09-07 across **three independent implementations** — BSD sed (Darwin 25.6), GNU sed 4.9, and busybox sed (Alpine 3.20) — all three strip a CR with `s/\r$//`, all three leave a word ending in the letter `r` alone, and all three append one with `s/$/\r/`. There is no disagreement left to route around.

What *is* true is the thing underneath the lore: **`\r` is not in POSIX.** A POSIX basic regular expression leaves a backslash before an ordinary character undefined, so every one of those three is extending the standard — they simply extend it the same way. That is why the warning was worth passing on for years, and why it is still the right instinct on a machine you have not measured. `tr -d '\r'` asks nothing of the regex grammar at all, which is what makes it the form to write down for somebody else.

**Neither one is right for a CSV.** A quoted field may contain a real line break, and `sed`, `tr` and `awk` are all line-oriented tools that split on `0a` — so to every one of them that break is just another line ending, and both commands above will quietly rewrite a customer's note from CRLF to LF while the file goes on parsing perfectly. There is no pipeline that gets this right, because getting it right requires knowing which `0a` bytes are inside quotes. Fix the endings of a quoted CSV inside the program that parses it, never in the pipeline in front of it.

## git: the warning says the opposite of what people read into it

Almost everything confusing about git here follows from one fact: **the repository always stores LF.** `core.autocrlf` does not choose what gets committed; it chooses what happens to your working copy on the way in and out.

```text title="Measured 2026-09-07 — git 2.52.0 (macOS 25.6) and git 2.43.0 (Ubuntu 24.04), identical wording on both. Not machine-checked: an answer key cannot hold a carriage return."
$ git config core.autocrlf true   &&  git add .
warning: in the working copy of 'unix.txt', LF will be replaced by CRLF the next time Git touches it

$ git config core.autocrlf input  &&  git add .
warning: in the working copy of 'win.txt', CRLF will be replaced by LF the next time Git touches it

  what got stored, under every setting except false:
    win.txt   6f 6e 65 0a 74 77 6f 0a        <- the CRs are gone
    unix.txt  6f 6e 65 0a 74 77 6f 0a        <- identical
    bin.dat   61 0d 0a 00 62 0d 0a           <- untouched; it contains a NUL,
                                                so git calls it binary
```

Read the warning again: it names your **working copy**, not your commit. It fires on the file that is about to *gain* CRs, not the one that has them. And under `input` it fires on the other file, for the mirror-image reason. Neither message is telling you anything about the blob, which is LF either way.

The consequence people meet is stranger than the warning. With `autocrlf=true`, check out a file committed as LF and every line on disk gains a CR — and `git status` reports the tree **clean**:

```text title="Measured 2026-09-07 — git 2.52.0. Not machine-checked (see above)."
$ git cat-file -p HEAD:f.txt | xxd
00000000: 6f6e 650a 7477 6f0a 7468 7265 650a       one.two.three.

$ git checkout -- f.txt && xxd f.txt
00000000: 6f6e 650d 0a74 776f 0d0a 7468 7265 650d  one..two..three.
00000010: 0a                                       .

$ git status --porcelain
                                                   <- nothing. Clean.
```

Every byte of every line differs from the blob and git says there is no change, because **git's "no change" is a claim about the normalized text, not about the bytes on disk.** That is the setting working exactly as designed, and it is also why a file can be silently rewritten on your disk by a command you thought only read from the repository.

The diagnostic nobody knows is `git ls-files --eol`, which prints both halves at once:

```text title="Measured 2026-09-07 — git 2.52.0, in a scratch repo with the .gitattributes below. Not machine-checked (see above)."
$ git ls-files --eol
i/lf    w/lf    attr/text=auto        	.gitattributes
i/lf    w/lf    attr/text eol=lf      	deploy.sh
i/-text w/-text attr/text=auto        	logo.png
i/lf    w/lf    attr/text=auto        	unix.txt
i/lf    w/crlf  attr/text=auto        	win.txt
```

`i/` is the index and `w/` is the working tree, so the last row reads *"stored as LF, on disk as CRLF"* — the state the previous section describes, printed rather than inferred. `i/-text` is git declining to treat a file as text at all: `logo.png` contains a NUL, so no normalization is applied to it under any setting. And `deploy.sh` shows an attribute overriding the default, which is the next thing.

The fix that outlasts everyone's local config is `.gitattributes`, because it travels with the repository while `core.autocrlf` is one developer's machine:

```gitattributes
* text=auto
*.sh   text eol=lf
*.bat  text eol=crlf
*.png  binary
```

`text=auto` means *normalize to LF in the repository if it looks like text*. `eol=lf` additionally pins the working copy, which is what a shell script needs, for the reason the next section is about.

## The shebang, and the two failures that are not it

A script saved with CRLF is the most memorable version of this bug, and it fails three different ways depending on how you start it. Two of them belong to this page.

Run it as `bash script.sh` and it **works** — and prints a hidden CR into whatever reads its output, because the `\r` was never a line ending to bash: it was the last character of the argument to `echo`. The script ran, the screen looks right, and the file it wrote has a `0d` on the end of every line, which is how this bug reproduces itself downstream.

Give the same script an `if` block and it stops running at all. `fi\r` is not the word `fi`, so a script with no syntax error in it dies with `syntax error: unexpected end of file` and exit **2** — the same wording and the same status on bash 3.2.57 (macOS) and 5.2.21 (Ubuntu), because the error is about the parser reaching the end of the file still looking for the `fi` it never saw. Section 6 of the shell run below shows both.

The third way is executing it directly, where the kernel takes the CR as part of the interpreter's path and goes looking for a `/bin/sh\r` that does not exist. That one is [The first two bytes](../../06_Terminal/the_first_two_bytes/README.md)'s subject rather than this page's, and it is worth reading there for two things this page would only summarise: the exit status is **126 on Apple's bash and 127 nearly everywhere else**, so no answer key may hold it; and of the three shells compared there, modern bash on Linux is the one that has dropped the interpreter path from its message — so the `^M`, the single character that explains the whole failure, is not shown to the reader most likely to meet it.

## In the terminal

<!-- output:crlf_vs_lf_sh -->
*Verified output of [`crlf_vs_lf_sh.sh`](examples/crlf_vs_lf_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FOUR FILES, AND THE ONE COMMAND THAT NAMES THEM
------------------------------------------------------------------------
  unix.txt   ASCII text
  win.txt    ASCII text, with CRLF line terminators
  mac.txt    ASCII text, with CR line terminators
  mixed.txt  ASCII text, with CRLF, LF line terminators

  file(1) reads the ending straight out of the bytes and says so in
  words. It is the fastest question to ask about a file somebody sent
  you, and the last line shows it will tell you when a file has BOTH.

$ xxd unix.txt
00000000: 6f6e 650a 7477 6f0a                      one.two.

$ xxd win.txt
00000000: 6f6e 650d 0a74 776f 0d0a                 one..two..
  0d 0a against 0a. One extra byte per line, at the end of each line,
  and 0d is CR -- the carriage return that was a separate motion on a
  teletype. Unix kept the line feed; DOS kept both; Windows inherited
  it and so did every protocol written in the 1980s.

2. WHAT THE SCREEN WILL NOT SHOW YOU
------------------------------------------------------------------------

$ cat win.txt          (piped through cat -vet, which draws the CR)
  one^M$
  two^M$

  Without -vet, cat prints "one" and "two" and you would swear the file
  was fine. ^M is the CR, $ is the LF, and the pair at the end of every
  line is the signature of a Windows file. That ^M is what vim shows
  you, for the same reason -- it is caret notation, not a warning.

$ wc -l < win.txt | tr -d ' '
2

$ wc -l < mac.txt | tr -d ' '
0
  Two lines, and zero. wc -l counts 0a bytes and the classic-Mac file
  has none at all, so a perfectly readable two-line file reports no
  lines -- the same arithmetic as a missing trailing newline, one byte
  along.

3. THREE PIPELINES THAT QUIETLY GIVE THE WRONG ANSWER
------------------------------------------------------------------------
  grep -c "^two$"     unix 1      win 0
  a CSV field, cut    unix 59     win 590d
  [ "$v" = "Y" ]      NO MATCH

  The anchored grep finds nothing, because $ anchors after the CR, not
  before it. cut hands back 59 0d where you expected 59. And the shell
  compares two strings that print identically and are not equal. Every
  one of those exits 0. Nothing is reported; a report just comes out
  empty, or a lookup silently matches nothing.

4. STRIPPING IT: TWO COMMANDS THAT ARE NOT THE SAME
------------------------------------------------------------------------

$ tr -d '\r' < win.txt | xxd
00000000: 6f6e 650a 7477 6f0a                      one.two.

$ sed 's/\r$//' win.txt | xxd
00000000: 6f6e 650a 7477 6f0a                      one.two.
  Same answer here, and they are not the same command. tr deletes
  EVERY 0d in the file, wherever it sits. sed deletes one only where a
  line ends. On a file whose CRs are all line endings that is the same
  file; on one with a CR in the middle of a line it is not:

$ printf 'a\rb\r\n' | tr -d '\r' | xxd
  00000000: 6162 0a                                  ab.

$ printf 'a\rb\r\n' | sed 's/\r$//' | xxd
  00000000: 610d 620a                                a.b.

  tr produced "ab" and sed produced "a", CR, "b". Which one you want
  depends on whether a CR that is not a line ending is damage or data,
  and only you know that. Reach for sed when the file is text somebody
  saved on Windows, and for tr when you want every CR gone.

  Now the case where NEITHER is right. A CSV may hold a real line break
  inside a quoted field, and both of these are line-oriented tools that
  split on 0a -- so to both of them that break is just another line
  ending:

$ printf '1,"a\r\nb"\r\n' | tr -d '\r' | xxd
  00000000: 312c 2261 0a62 220a                      1,"a.b".

$ printf '1,"a\r\nb"\r\n' | sed 's/\r$//' | xxd
  00000000: 312c 2261 0a62 220a                      1,"a.b".

  The same wrong answer twice: a customer note that said CRLF now says
  LF, and the file still parses, so nothing will ever report it. There
  is no sed or tr or awk that gets this right, because getting it right
  needs a parser that knows which 0a bytes are inside quotes. Fix the
  endings of a quoted CSV in the program that reads it -- section 4 of
  the Python run -- and not in the pipeline in front of it.

  dos2unix does the sed job with a safety net (it refuses a binary file
  and keeps the mode bits) and is the right answer at a keyboard -- but
  it ships with neither macOS nor a stock Ubuntu, so it is not used
  here and should not go in a script you expect to run anywhere.

5. AND BACK THE OTHER WAY
------------------------------------------------------------------------

$ sed 's/$/\r/' unix.txt | xxd
00000000: 6f6e 650d 0a74 776f 0d0a                 one..two..
  tr cannot do this direction at all -- tr substitutes and deletes, it
  never inserts. This is the sed to reach for when a Windows consumer
  insists, and it is what unix2dos does.

6. A SCRIPT SAVED WITH CRLF
------------------------------------------------------------------------
  the script:  #!/bin/bash^M$ echo hello^M$
  bash greet.sh prints:  68656c6c6f0d0a

  68 65 6c 6c 6f is "hello", and then 0d 0a. The CR was never a line
  ending to bash -- it was the last character of the ARGUMENT to echo,
  so the script now prints an invisible carriage return into whatever
  reads it. It ran. It even looks right on screen.

  Give it a block and it stops running at all:
  bash block.sh   exit=2   (a syntax error, on a script with no
                            syntax error in it -- "fi" followed by a
                            CR is not the word fi)

  And when the kernel runs it directly, the CR joins the interpreter
  path: the shebang asks for "/bin/bash", CR, which does not exist. Both
  the message and the exit status for THAT differ by platform, so
  neither can be recorded here -- "The first two bytes" compares three
  shells side by side and is where that half of the story lives.

7. THE FILE THAT IS BOTH
------------------------------------------------------------------------
  mixed.txt  ASCII text, with CRLF, LF line terminators

$ cat -vet mixed.txt
one^M$
two$
  One CRLF line and one LF line, which is what every editor produces
  the moment two people with different settings touch one file. file(1)
  names both. Nothing else here will: grep, cut and wc each answer for
  their own line and never mention that the file disagrees with itself.
```
<!-- /output -->

## In Python

Python translates line endings on exactly one path, which is why this bug is invisible for years and then arrives all at once — on the day the text comes from somewhere that is not a text-mode read.

<!-- output:crlf_vs_lf_py -->
*Verified output of [`crlf_vs_lf_py.py`](examples/crlf_vs_lf_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THREE FILES, ONE TABLE
------------------------------------------------------------------------
   Unix         LF   23 bytes   0a 31 2c 41 64 61 2c 59 ...
   Windows      CRLF 25 bytes   0d 0a 31 2c 41 64 61 2c ...
   classic Mac  CR   23 bytes   0d 31 2c 41 64 61 2c 59 ...

   Same two lines of text. The middle file is one byte per line longer,
   and that byte -- 0d, carriage return -- is the entire subject.

2. READING: PYTHON TRANSLATES, AND ONLY ON THIS ONE PATH
------------------------------------------------------------------------
   CRLF file, open(...) default   'id,name,active\n1,Ada,Y\n'
   CR   file, open(...) default   'id,name,active\n1,Ada,Y\n'
                                   ^ both arrive as \n. That is
   'universal newlines': a text-mode read turns \r\n, \r and \n into \n
   before your code sees anything. It is why a Windows CSV usually just
   works, and why the day it does not comes as a surprise.

   Now the same file down the other two paths:
   CRLF file, newline=''           'id,name,active\r\n1,Ada,Y\r\n'
   CRLF file, open(..., 'rb')      b'id,name,active\r\n1,Ada,Y\r\n'

   Nothing translated. Those are not exotic: newline='' is what the csv
   module asks for, and bytes are what you get from a socket, a zipfile,
   a subprocess with text=False, and a database column. The protection
   covers one path, and the CR is waiting on all the others.

3. THE FIELD THAT QUIETLY STOPS MATCHING
------------------------------------------------------------------------
   text.split(chr(10))[1]     '1,Ada,Y\r'
   .split(',')                ['1', 'Ada', 'Y\r']
   fields[-1] == 'Y'          False   <- the CR is inside the last field
   len(fields[-1])            2   <- two characters, and it prints as one

   And here is why the interface half-works rather than failing:
   int('42\r')                42      numbers survive -- int() strips whitespace
   float('3.5\r')             3.5     so does float()
   '42\r' == '42'             False   strings do not

   Quantities reconcile. Keys, codes, flags and dates-as-text do not.
   A report that adds up correctly and matches nothing is this bug.

   Stripping it, and the near-miss:
   'Y\r'.rstrip()             'Y'    removes any trailing whitespace
   'Y\r'.rstrip(chr(10))      'Y\r'  <- asked for \n, left the \r
   The second is the line people write when they think 'strip the
   newline'. It is exactly correct and it removes the wrong byte.

4. WRITING: newline= IS A SECOND, SEPARATE DECISION
------------------------------------------------------------------------
   csv.writer always emits \r\n of its own. What open() then does to it:

   newline=''        69 64 2c 6e 61 6d 65 0d 0a 31 2c 41 64 61 0d 0a
   newline='\r\n'    69 64 2c 6e 61 6d 65 0d 0d 0a 31 2c 41 64 61 0d 0d 0a

   Look at the second one: 0d 0d 0a. TWO carriage returns. On write, a
   newline= of \r\n means 'translate every \n I write into \r\n' -- and
   the \n the csv module wrote already had a \r in front of it.

   That second line IS Windows' default. newline=None on Windows
   translates to os.linesep, which is \r\n, so the famous blank row
   between every record of an Excel-bound CSV is 0d 0d 0a, and this is
   it reproduced on a Unix machine by naming the ending by hand.
   as text:            'id,name\r\r\n1,Ada\r\r\n'

   newline='' does not mean 'no newlines'. It means 'translate nothing
   in either direction' -- and that is why it is the right argument for
   a csv file on every platform, reading and writing.

5. AND WHY csv ASKS FOR IT: A NEWLINE INSIDE A FIELD
------------------------------------------------------------------------
   the file            b'id,note\r\n1,"first\r\nsecond"\r\n'
   One record. Its second field is a quoted string containing a real
   line break -- legal CSV, and common in any free-text column.

   newline=''    -> [['id', 'note'], ['1', 'first\r\nsecond']]
   newline=None  -> [['id', 'note'], ['1', 'first\nsecond']]

   Both parse into one record, so nothing errors and nothing looks
   wrong. But the field's CONTENT is different: the default read
   rewrote the bytes INSIDE the value before csv ever saw them. Read a
   file that way and write it back and you have edited somebody's data
   without touching it. That is the whole reason the csv docs ask for
   newline='': line splitting is the parser's job, not open()'s.

6. THE RULE
------------------------------------------------------------------------
   reading text you will parse yourself   the default is right: it
                                          normalises everything to \n

   reading or writing csv                 newline='' -- always, both
                                          directions, every platform

   comparing, hashing, or byte-counting   open in 'rb'. Text mode has
                                          already changed the bytes.

   text that did NOT come from open()     assume it has CRs. Sockets,
                                          zips, HTTP, subprocesses and
                                          database columns translate
                                          nothing at all.

   And when you strip: .rstrip() with no argument, or splitlines(),
   or .rstrip('\r\n'). Never .rstrip('\n') and never [:-1].
```
<!-- /output -->

## Which fix belongs where

| Where the text is | What to do | Why |
|---|---|---|
| a text file you parse yourself, in Python | nothing — the default read normalizes `\r\n`, `\r` and `\n` to `\n` | universal newlines, and it is right |
| a CSV, reading or writing, any platform | `newline=''` in the `open()` call | line splitting is the parser's job; `open()` guessing corrupts quoted fields |
| comparing, hashing or byte-counting | open in `'rb'` | text mode has already changed the bytes you meant to measure |
| text from a socket, zip, HTTP body, subprocess or database column | assume CRs; strip explicitly | none of those paths translate anything |
| a file on disk, at a keyboard | `dos2unix`, or `sed 's/\r$//'` | one line, reversible, and `file` confirms it |
| a shell script | `.gitattributes` with `text eol=lf` | the fix has to survive the next checkout on somebody else's machine |
| a `.bat` or a file a Windows tool re-reads | `eol=crlf`, deliberately | CRLF is not wrong there; it is required |

And when you strip in code, strip the right thing: `.rstrip()` with no argument, `splitlines()`, or `.rstrip('\r\n')`. **Never `.rstrip('\n')`** — it is exactly what somebody writes when they mean "remove the newline", it does precisely what it says, and it leaves the CR behind.

## If you are coming from Python or ABAP

**Python.** The reading side and the writing side are two separate decisions that share one keyword, and conflating them is where the famous Excel bug comes from. On **read**, `newline=None` (the default) is universal newlines: `\r\n`, `\r` and `\n` all arrive as `\n`. On **write**, `newline=None` translates every `\n` you write into `os.linesep` — which on Windows is `\r\n`, so a `csv.writer`, which emits its own `\r\n`, ends up writing `\r\r\n` and Excel shows a blank row between every record. Section 4 of the run above reproduces that on a Unix machine by naming the ending by hand, and prints the `0d 0d 0a`. `newline=''` does not mean "no newlines" — it means *translate nothing, in either direction*, which is why the `csv` docs ask for it on both. Beyond `open()`, remember how narrow the protection is: [text in practice](../../10_Best_Practices/python_text_in_practice/README.md) is a habit about `open()`, and a socket, a `zipfile` member, an HTTP body and a `subprocess` with `text=False` are not `open()`.

**ABAP.** Two constants, and picking the wrong one is the usual cause: `cl_abap_char_utilities=>newline` is the application server's own line separator — on the Unix-based servers most systems run, a single LF — while `cl_abap_char_utilities=>cr_lf` is the two-character CR+LF pair. A file built for a Windows consumer wants `cr_lf`; a file another Unix process will parse wants `newline`; and `OPEN DATASET … IN TEXT MODE` already appends the platform's separator per `TRANSFER`, so adding `cr_lf` on top of it writes the CR *and* the server's LF, which is the ABAP spelling of the `\r\r\n` above. In the other direction, `gui_download` runs on the front end, so a download from a Windows GUI arrives with CRLF whatever the server does — and when such a file is read back with `READ DATASET` on the server, the CR stays on the end of every field the delimiter did not consume. That is where the trailing `#` in an SE16 or debugger display comes from: SAP draws an unprintable character as `#`, so a CRLF file displayed where LF was expected grows one `#` per line, always at the end. Check the constants and any code-page numbers against your own system rather than trusting a name from a document. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 07_Real_Data/crlf_vs_lf/examples
bash crlf_vs_lf_sh.sh
python3 crlf_vs_lf_py.py
```

1. `printf 'a,b\r\n' > t.csv`, then `cut -d, -f2 t.csv | xxd -p`. Predict the three bytes before you look, and say which one you did not ask for.
2. Make a two-line file with one CRLF line and one LF line. Ask `file`, then `wc -l`, then `grep -c '^two$'`. Only one of the three will tell you the file disagrees with itself.
3. Set `core.autocrlf=true` in a scratch repository, commit an LF file, delete it, check it out, and run `git status`. Explain "clean" to somebody.
4. Without the machine: an interface has run nightly for a year. This morning every quantity on the reconciliation report is correct and no line item matches a master record. Name the byte, and say which end of the line it is on.

## See also

- [Control characters](../../02_Characters/control_characters/README.md) — what `CR` and `LF` are, and why `Ctrl-M` is 13
- [The trailing newline](../../06_Terminal/trailing_newline/README.md) — the other question about the end of a line: whether the last one has an ending at all
- [A BOM in a CSV](../bom_in_a_csv/README.md) — the same invisible-character bug at the other end of the line
- [The byte that means something to somebody else](../../12_Adversarial/in_band_signals/README.md) — why `CR LF` inside a field is an HTTP response-splitting bug
- [`sed` matches patterns, not bytes](../../11_Tools/sed/README.md) — the tool doing the stripping above
- [`diff` compares lines, `cmp` compares bytes, neither compares text](../../11_Tools/diff_and_cmp/README.md) — for the day two identical-looking files will not compare equal
- [Python text in practice](../../10_Best_Practices/python_text_in_practice/README.md) — `encoding=` and `newline=` as one standing habit
