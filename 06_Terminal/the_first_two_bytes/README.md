# The first two bytes

**Level:** 101 → 201 · for anyone with a terminal

**One line:** Whether a file runs at all is decided by its first bytes and nothing else — so three invisible bytes in front of `#!` make the kernel refuse it, one `0d` at the end of that line sends it looking for an interpreter that does not exist, and your shell may then run the broken file anyway and exit `0`.

## The two bytes

```bash
head -c 2 script.sh | xxd -p
```

`2321` means the kernel will treat this file as a script. Anything else means it will not, whatever the file is called, whatever its extension is, and whatever `file` says about it.

## What `./x` actually does

You type `./deploy.sh` and press Enter. Three things happen, and only the third one is about bytes.

**The shell sees a `/` in the word**, so it skips the `$PATH` search entirely and treats what you typed as a path. That is the whole job of the leading dot. `.` is deliberately not in your `$PATH` — if it were, a file named `ls` dropped into any directory you happened to `cd` into would run instead of the real one. The dot is you saying *"yes, this one, the one right here."*

**The shell forks and calls `execve("./deploy.sh", …)`.** From here the shell is out of the picture, and everything is the kernel's decision.

**The kernel opens the file and reads the first few bytes.** Not the name, not the extension, not the `x` permission bit beyond checking that it is set — the actual bytes at offset 0. It compares them against a short list of signatures it knows. `#!` means *"the rest of this line is the path of a program that should be run with this file as its argument."* `7f 45 4c 46` means an ELF executable. `cf fa ed fe` and `ca fe ba be` mean Mach-O. Nothing on the list means `ENOEXEC`, and the kernel gives up.

Which handler claims which bytes, and the three *other* mechanisms that also answer "what kind of file is this" without agreeing with each other, are [File type is four questions](../file_type_is_four_questions/README.md). This page stays on one of them — the kernel's — and on the bytes at offset 0 that it reads.

That is why this page sits in an encodings chapter rather than a shell one. **The kernel does no decoding at all.** It does not know or care what encoding the file is in. It does not skip a byte-order mark, it does not normalize line endings, and it does not strip whitespace. It compares raw bytes at a fixed offset. Every failure below is that one sentence, met from a different direction.

```text title="Measured 2026-09-07 — macOS 26 (Darwin 25.6) and ubuntu:24.04. Not machine-checked: the magic number of your system's own binaries is a fact about your platform, so no example here reads a file it did not write itself."
                first 4 bytes
macOS   /bin/ls   ca fe ba be    Mach-O universal binary (several architectures in one file)
macOS   /bin/sh   ca fe ba be
Ubuntu  /bin/ls   7f 45 4c 46    ELF — and 45 4c 46 is the ASCII for "ELF"
Ubuntu  /bin/sh   7f 45 4c 46
```

`ca fe ba be` is also the first four bytes of every Java `.class` file, which is a genuine collision and predates Mach-O's use of it. A magic number is a convention, not a registry.

## Two ways to break a shebang, and they fail differently

Take one working script and make two copies, each damaged in a way nothing on a screen draws.

| | first bytes | what the kernel finds | what you get |
|---|---|---|---|
| `plain.sh` | `23 21 2f 62` | `#!` at offset 0 | it runs |
| `bom.sh` | `ef bb bf 23` | no signature | `ENOEXEC` |
| `crlf.sh` | `23 21 2f 62` | `#!`, then the path `/bin/sh\r` | `ENOENT` |

`file(1)` is not fooled by any of this, which is the point. It calls three of the four shell scripts, and it even names the mark:

```text title="Measured 2026-09-07 — macOS 26 (file-5.41) and ubuntu:24.04 (file-5.45). Not machine-checked: file's English wording is version-dependent (the word executable moved between 5.41 and 5.44), so only the MIME forms are safe to record."
                 macOS, file-5.41                                  Ubuntu, file-5.45
plain.sh   POSIX shell script text executable, ASCII text    POSIX shell script, ASCII text executable
bom.sh     POSIX shell script text executable,               POSIX shell script, Unicode text,
             Unicode text, UTF-8 (with BOM) text               UTF-8 (with BOM) text executable
crlf.sh    POSIX shell script text executable, ASCII         POSIX shell script, ASCII text executable,
             text, with CRLF line terminators                  with CRLF line terminators
none.sh    ASCII text                                        ASCII text
```

That prose is the vivid version, and it is also the half that drifts — the wording move above is visible on this very example. The **recordable** form is stronger anyway, because it removes the wording from the argument entirely:

```text title="Measured 2026-09-07 — byte-identical on macOS 26 (file-5.41) and ubuntu:24.04 (file-5.45), both columns, all four files."
           --mime-type            --mime-encoding      does it run?
plain.sh   text/x-shellscript     us-ascii             yes
bom.sh     text/x-shellscript     utf-8                no  — ENOEXEC
crlf.sh    text/x-shellscript     us-ascii             no  — ENOENT
none.sh    text/plain             us-ascii             no  — ENOEXEC (the shell rescues it)
```

**Three files carry one identical MIME type and produce three different answers from the kernel.** That is the sentence that survives every future release of `file`, because `--mime-type` is stable where the English is not. Note the `--mime-encoding` column too: on `bom.sh` `file` has *detected the mark* — `utf-8` where its neighbours are `us-ascii` — and still calls the file a shell script, because the question it was asked was never "will this run".

So on `bom.sh` the two answers are flatly opposed: `file` says *POSIX shell script*, and even tells you there is a BOM; the kernel says *this is not a program*. Neither is wrong, because they were asked different questions — `file` reads a magic database looking for a signature **anywhere it has a rule for**, and the kernel compares **offset 0**. That is the whole subject of [File type is four questions](../file_type_is_four_questions/README.md), and `bom.sh` is the cleanest example of the disagreement this library has.

**The BOM lands in front of the `#!`.** A [byte-order mark](../../03_Encodings/byte_order_and_bom/README.md) is `ef bb bf` in UTF-8, and an editor set to "UTF-8 with BOM" writes it at offset 0 of every file it saves. The `#!` is still in the file — it is at offset 3 — but the kernel does not go looking for it. It compares offset 0, finds `ef`, and concludes the file is not a program. The `#!` might as well not be there.

**The CR lands after it.** A file saved with Windows line endings ends each line `0d 0a`. The kernel finds `#!` exactly where it expects, then reads forward to the `0a` and takes everything between as the interpreter's path — which is now `/bin/sh` followed by a carriage return. That is a perfectly legal filename, and nothing on the system has it. So you get an error saying the file does not exist, about a file that plainly does, and it names `/bin/sh` — which also plainly exists. The path in the message and the path the kernel looked for differ by one byte that the message has no way to draw.

Both refusals are worth meeting twice. [File type is four questions](../file_type_is_four_questions/README.md) produces the `ENOENT` from a shebang that names an interpreter which was never there — the clearest possible statement of the mechanism. This page produces the same `ENOENT` from `#!/bin/sh`, an interpreter that *is* there, with one invisible byte after it: the mechanism met as the bug you will actually be handed.

That asymmetry is the thing worth carrying away. The mark before the `#!` means **"this is not a program."** The byte after it means **"that interpreter is missing."** One is a fact about the file, the other is a claim about a different file entirely, and only the second one sounds like it is telling you the truth.

## The rescue is the dangerous part

Here is where the shell steps back in, and where a broken file gets to look fine.

When `execve` comes back `ENOEXEC`, a POSIX shell does not give up. It assumes you meant a shell script that simply forgot to say so, and runs the file itself. That is a genuinely useful convenience — it is why a script with no `#!` at all works — and on a file with a BOM it is a disaster, because the file *runs*:

```text title="Abridged for the lesson — the full run is generated further down"
   ./plain.sh  exit=0       stdout=  I ran
   ./bom.sh    exit=0       stdout=  I ran
   ./crlf.sh   exit=nonzero stdout=(nothing)
   ./none.sh   exit=0       stdout=  I ran
```

`bom.sh` prints an error to stderr, then runs to completion and **exits 0**. Any CI step, `make` rule, or `&&` chain that judges it by exit status passes it. The one line that failed was line 1 — the shebang, which the shell was reading as an ordinary command because the BOM in front of the `#` stopped it being a comment.

And the interpreter that ran it is not the one the file asked for. `bom.sh` says `#!/bin/sh`; it was executed by whatever shell you happened to be typing into. On a script that says `#!/usr/bin/env python3`, the rescue hands your Python to `bash`, and the error you get is about syntax.

```text title="Measured 2026-09-07 — the BOM in the first message is a real U+FEFF and is invisible on screen; it is written out here as <BOM>. Not machine-checked: this text is written by the shell, differs between builds, and is not a property of the file."
macOS bash 3.2.57 and Ubuntu bash 5.2.21 — identical wording, and then it runs anyway:
  ./bom.sh: line 1: <BOM>#!/bin/sh: No such file or directory

The CR, three shells, three sentences:
  macOS bash 3.2.57   /bin/bash: ./crlf.sh: /bin/sh^M: bad interpreter: No such file or directory
  macOS zsh 5.9       zsh:1: ./crlf.sh: bad interpreter: /bin/sh^M: no such file or directory
  Ubuntu bash 5.2.21  bash: line 4: ./crlf.sh: cannot execute: required file not found
```

Read the third one against the first two. Modern bash on Linux has dropped the interpreter path from the message altogether — so the `^M`, the single most useful character in the whole diagnostic, is no longer shown to you at all. The message that tells you the least is the one you are most likely to meet.

The exit status is no more portable than the wording. `crlf.sh` fails with **126** on Apple's `/bin/bash` and **127** on bash `3.2.57` under Linux — the same bash version, so it is not the version — and macOS's own `zsh`, `fish` and `dash` all say 127 as well. What *is* the same everywhere is the part that matters: the three zeros above.

## The line is a fixed buffer

The kernel reads the shebang line into a buffer of a fixed size, and a path longer than that buffer is not truncated into something that half works — the file simply stops being executable.

```text title="Measured 2026-09-07 — macOS 26 (Darwin 25.6) and ubuntu:24.04 under Docker, by lengthening a real symlink to /bin/sh one byte at a time. Not machine-checked: a kernel constant is a property of the platform."
Linux   longest shebang line that runs: 255 bytes   (BINPRM_BUF_SIZE = 256)
macOS   longest shebang line that runs: 511 bytes   (IMG_SHSIZE = 512)
```

Both land one byte under a power of two, which is the constant showing through. The practical shape of this: a `#!/…/.venv/bin/python3` inside a deeply nested project directory can cross 255 on Linux and not on macOS, so the script runs on the laptop it was written on and is "not executable" in CI, with no message that mentions length.

## In the terminal

<!-- output:the_first_two_bytes_sh -->
*Verified output of [`the_first_two_bytes_sh.sh`](examples/the_first_two_bytes_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FOUR FILES, AND THE BYTES AT OFFSET 0
   plain.sh  23212f62696e2f73
   bom.sh    efbbbf23212f6269
   crlf.sh   23212f62696e2f73
   none.sh   6563686f20222020
   The kernel reads THIS, and only this. Not the name, not the extension,
   not what file(1) guesses. 23 21 is the ASCII for #!

2. WHERE THE #! ACTUALLY IS

$ head -c 2 plain.sh | xxd -p
2321

$ head -c 5 bom.sh | xxd -p
efbbbf2321
   In bom.sh the #! is still there — at offset 3. The kernel does not go
   looking for it, so three bytes of byte-order mark are three bytes too many.

3. RUNNING THEM
   ./plain.sh  exit=0       stdout=  I ran
   ./bom.sh    exit=0       stdout=  I ran
   ./crlf.sh   exit=nonzero stdout=(nothing)
   ./none.sh   exit=0       stdout=  I ran
   Three of the four printed something. Only ONE of those three is a
   script the kernel agreed to run: for bom.sh and none.sh the kernel
   refused, and the SHELL caught the refusal and ran the file itself.
   That rescue is why a broken file passes a test that checks exit status.
   (bom.sh and none.sh exit 0 on every shell and both platforms. crlf.sh's
   nonzero value is 126 on Apple's bash and 127 nearly everywhere else, so
   it is a fact about your shell, not about the file, and is not printed.)

4. THE BYTE THAT KILLED crlf.sh

$ cat -vet crlf.sh
#!/bin/sh^M$
echo "  I ran"^M$
   ^M is the CR. The kernel found the #!, then read to the LF — so the
   interpreter it went looking for is /bin/sh followed by a CR, which is
   a filename nothing on the system has. Hence an error about a missing
   file, for a file that is right there.

5. THE INTERPRETER PATH, AS THE KERNEL BUILDS IT

$ sed -n '1s/^#!//p' plain.sh | cat -vet
/bin/sh$

$ sed -n '1s/^#!//p' crlf.sh  | cat -vet
/bin/sh^M$
   Same nine characters on screen. One of them is ten bytes.

6. THE FIX, AND HOW TO CHECK IT AFTERWARDS

$ tr -d '\015' < crlf.sh > fixed.sh && chmod +x fixed.sh && ./fixed.sh
  I ran

$ head -c 12 fixed.sh | xxd -p
23212f62696e2f73680a6563
   Nothing on screen changed when it was broken and nothing changed when
   it was fixed. The dump is the only view that ever showed the defect.
```
<!-- /output -->

## In Python

`subprocess.run([path])` is a bare `execve` with no shell behind it to catch a refusal. That is what makes it the right tool for looking at this: the failures the prompt hides are the ones it reports.

Note what the program prints for a failure — the exception **class** and the **symbolic** errno, never the message. `strerror` text is written by the C library and differs between platforms, so it is a fact about the machine and not about the file.

<!-- output:the_first_two_bytes_py -->
*Verified output of [`the_first_two_bytes_py.py`](examples/the_first_two_bytes_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE FIRST FOUR BYTES OF EACH FILE
   plain.sh  23 21 2f 62  a script — read the rest of the line as an interpreter
   bom.sh    ef bb bf 23  no signature — ENOEXEC, the kernel will not run this
   crlf.sh   23 21 2f 62  a script — read the rest of the line as an interpreter
   none.sh   65 63 68 6f  no signature — ENOEXEC, the kernel will not run this
   All four are executable, all four end in .sh, and file(1) calls three
   of them shell scripts. None of that reaches the kernel.

2. THE #! IS TWO ASCII BYTES, AND ITS OFFSET IS THE WHOLE RULE
   ord('#') = 35 = 0x23     ord('!') = 33 = 0x21
   plain.sh  finds #! at offset 0
   bom.sh    finds #! at offset 3
   Offset 3 is not offset 0. The kernel does not search; it compares.

3. execve(), WITH NO SHELL TO CATCH THE REFUSAL
   plain.sh  ran      rc=0  stdout='I ran'
   bom.sh    refused  OSError  errno 8 (ENOEXEC)
   crlf.sh   refused  FileNotFoundError  errno 2 (ENOENT)
   none.sh   refused  OSError  errno 8 (ENOEXEC)
   Three different outcomes for four files that look identical on screen.

4. WHY THE TWO REFUSALS ARE NOT THE SAME REFUSAL
   bom.sh    kernel sees ef bb, not 23 21 — no interpreter is read
   crlf.sh   kernel sees #!, interpreter = '/bin/sh\r'
   bom.sh   ENOEXEC: 'this is not a program'. The #! was never found.
   crlf.sh  ENOENT:  'that interpreter does not exist'. The #! WAS found,
            and the path read out of it has a 13 on the end.
   The second is the one that reads as a lie: the file it names is there.

5. WHY strip() DOES NOT SAVE bom.sh
   raw first bytes        ef bb bf 23 21
   .strip() changes it?   False
   chr(0xFEFF).isspace()  False
   U+FEFF is named ZERO WIDTH NO-BREAK SPACE and is not in Unicode's
   White_Space property, so no strip anywhere will remove it. It is
   content, and at offset 0 of an executable it is fatal content.

6. THE CHECK WORTH PUTTING IN CI
   plain.sh  first line is a usable shebang: True
   bom.sh    first line is a usable shebang: False
   crlf.sh   first line is a usable shebang: False
   none.sh   first line is a usable shebang: False
   Two questions, both about bytes: does it START with 23 21, and is the
   first line free of 0d. Neither is answerable from the rendered text.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python** hands you both halves of this and does not tell you which you are using. `subprocess.run(["./x"])` — a list — is `execve`, and a file with a BOM raises `OSError` with `errno.ENOEXEC` that no amount of reading the file as text would predict. `subprocess.run("./x", shell=True)` is the shell, rescue included, so the same broken file returns `0` and your check passes. The list form is the safer default for many reasons and this is one more of them. The reading side has the same shape as the kernel's: `open(p, encoding="utf-8")` leaves a BOM in your string as `﻿`, where `encoding="utf-8-sig"` consumes it — and `"﻿".isspace()` is `False`, so no `.strip()` you write will ever remove it. Python protects its *own* source files from this (PEP 263 lets a BOM stand in for the encoding declaration), which is exactly why the habit does not transfer: a `.py` file with a BOM imports fine and the same file with a `#!` line will not execute.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* The nearest thing is the download path, where the same byte does the same damage one system along. `cl_abap_conv_out_ce` and the `GUI_DOWNLOAD` function module can be asked to emit a byte-order mark, and a shell script or `.csv` generated from an SAP system and then run or parsed on Unix carries it into exactly this failure. The line-ending half is the more common one in practice: a file written with `cl_abap_char_utilities=>cr_lf` rather than `newline` produces the `crlf.sh` case above, and the resulting Unix-side error names a missing interpreter rather than a line ending. The check to write is the same in both languages and it is a byte check — read the first three bytes and compare them to `EF BB BF`, do not look at the string.

## Try it

1. `printf '#!/bin/sh\necho hi\n' > a.sh && chmod +x a.sh && ./a.sh`. Now prepend a BOM with `printf '\357\273\277' | cat - a.sh > b.sh && chmod +x b.sh`, run `./b.sh`, and check `echo $?` before you read the error.
2. Run that same `b.sh` through `python3 -c "import subprocess; subprocess.run(['./b.sh'])"`. Explain why one of the two says it worked.
3. Take a working script, `printf` it back out with `\r\n` line endings, and run it. Then read the error message aloud and count how many of the files it names actually exist.
4. Open a script in an editor and look for a "UTF-8 with BOM" setting. Save it both ways and `xxd -l 4` the result each time.
5. `head -c 4 /bin/ls | xxd -p` on every machine you have. Say what each answer means before you look it up.

## Practice

**Three scripts that differ only in bytes you cannot see.** One is ordinary. One has a UTF-8 BOM before `#!`. One has CRLF line endings. All three are `chmod +x`.

Predict, for each: does `./script.sh` run it, and does `sh script.sh` run it? Six answers. Two of them are the surprise — say which, and explain both. Then say why the exit status of the failing case is not something a portable script may test for.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:the_first_two_bytes_kata_sh -->
*Verified output of [`the_first_two_bytes_kata_sh.sh`](examples/the_first_two_bytes_kata_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
   file       first 6 bytes              shebang line, as bytes
   good.sh    23212f62696e               23212f62696e2f73680a
   bom.sh     efbbbf23212f               efbbbf23212f62696e2f73680a
   crlf.sh    23212f62696e               23212f62696e2f73680d0a

RUN THEM DIRECTLY -- this is the kernel reading the first two bytes
   ./good.sh    ran
   ./bom.sh     ran
   ./crlf.sh    did NOT run (126 or 127)

NOW HAND THE SAME FILES TO sh, WHICH DOES NOT LOOK AT THE FIRST TWO BYTES
   sh good.sh    ran
   sh bom.sh     ran
   sh crlf.sh    ran

WHAT HAPPENED, LINE BY LINE

good.sh   23 21 is '#!', so the kernel reads the rest of the line as an
          interpreter path and execs /bin/sh. Nothing else about the file
          matters at this point -- not the name, not the extension.

bom.sh    starts ef bb bf. The kernel compares the first TWO bytes
          against 0x23 0x21, they do not match, so the file has no
          shebang and execve fails with ENOEXEC -- and yet it exited 0.
          That is the shell catching the failure and re-running the file
          with itself, a POSIX fallback older than the shebang. So three
          bytes nothing draws took the kernel out of the loop, the script
          still ran, and no status anywhere records that anything
          unusual happened. Under a different interpreter -- python3,
          awk -- there is no fallback and it simply does not run.

          The status it fails with is itself platform-dependent -- 126
          on macOS, 127 on Ubuntu, measured 2026-09-07 -- which is why
          the table above records a verdict and not a number. A script
          testing for one of the two is testing its own machine.

crlf.sh   the shebang matches, so the kernel takes the rest of the line
          -- and the line ends 0d 0a, so the interpreter it looks for is
          '/bin/sh' with a CARRIAGE RETURN on the end. There is no such
          file. The error names /bin/sh, which is present and correct,
          and the invisible byte is the whole problem.

THE PART THAT CATCHES PEOPLE
   Look at the second block. Both broken files RUN under sh, because the
   shell was told which interpreter to use and never consults the first
   two bytes. So the same file fails one way and works the other, and a
   CI job that invokes 'sh script.sh' passes while the deployed cron
   entry that runs './script.sh' fails.

   crlf.sh under sh is worth its own line: it runs, and every command in
   it receives an argument with a trailing 0d. That usually still exits 0
   -- which is the worst of the three outcomes, because nothing at all
   reports it.
```
<!-- /output -->

</details>

## See also

- [File type is four questions](../file_type_is_four_questions/README.md) — the other three mechanisms that answer "what kind of file is this", and why they disagree
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — where `ef bb bf` comes from, and the other places it is a hard error rather than noise
- [Control characters](../../02_Characters/control_characters/README.md) — `CR` and `LF`, and why a file has both
- [The trailing newline](../trailing_newline/README.md) — the byte at the *other* end of the file, and the six tools that change behaviour over it
- [Inspecting a file](../inspecting_a_file/README.md) — when the screen and the file disagree, which column is the file
- [`file` guesses](../file_guesses/README.md) — the tool that reads magic numbers for a living, and why its answer is still an inference
- [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) — the dump used throughout this page
