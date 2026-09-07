# File type is four questions

**Level:** 201 · for anyone with a terminal

**One line:** Nothing on a Linux system answers "what type is this file?" — four separate mechanisms answer four *different* questions, from four different sources, and on the same file they routinely disagree without any of them being wrong.

There is no field in a file that says what it is. There is no registry the system consults. When you ask a Unix system what kind of file something is, the answer you get depends entirely on **which of four mechanisms you happened to ask**, and they do not share a database, a code path, or even a definition of the word *type*.

Most of the confusion around this subject comes from not noticing that the four exist. A shell script's `[ -f ]`, a double-click in a file manager, `file thing`, and `./thing` are four unrelated pieces of machinery. Below, each one on its own, then all four on one file.

## The four answerers

| What is asking | What it reads | Opens the file? | Its idea of "type" |
|---|---|---|---|
| `ls -l`, `[ -f ]`, `stat()` | four bits of the **inode** | no | one of seven storage kinds |
| `./thing` — `execve(2)` | the **first 256 bytes**, in the kernel | yes | "which handler can launch this" |
| `file thing` | a compiled **magic database**, in userspace | yes | a MIME type or an English phrase |
| double-click in GNOME/KDE | the **filename**, magic second | usually not | a MIME type, for picking an app |

Read down the third column. Two of the four never look inside the file at all, which is why a `.png` full of prose keeps opening in an image viewer, and why `[ -f ]` cannot tell a novel from a core dump.

## Question one — how is it stored?

The filesystem's answer lives in `st_mode`, and it is four bits wide. Seven values: regular file, directory, symlink, FIFO, socket, block device, character device. That is the complete vocabulary — there is no eighth value, and none of the seven is "PNG".

Everything else in `st_mode` is permissions. The type is extracted by masking with `S_IFMT`, which the [Python example](#in-python) prints in octal so you can see how little of the number it is.

This is the layer the shell speaks. `[ -f ]`, `[ -d ]`, `[ -p ]`, `[ -S ]` are `stat(2)` and nothing more; under `strace`, `[ -f liar.txt ]` makes exactly one syscall against the file and never opens it:

```text title="strace of a shell test — Debian bookworm, 2026-09-07, not a command to run"
newfstatat(AT_FDCWD, "liar.txt", {st_mode=S_IFREG|0644, st_size=33, ...}, 0) = 0
```

Compare `file` on the same path, which locates its database and *then* opens your file:

```text title="strace of file(1) — Debian bookworm, 2026-09-07, not a command to run"
openat(AT_FDCWD, "/etc/magic.mgc", O_RDONLY)            = -1 ENOENT
openat(AT_FDCWD, "/usr/share/misc/magic.mgc", O_RDONLY) = 3
openat(AT_FDCWD, "liar.txt", O_RDONLY|O_NONBLOCK|O_CLOEXEC) = 3
```

Two commands about one file; one of them read it.

## Question two — how do I run it?

This is the only place the *kernel* looks at content, and it is not answering "what is this" — it is answering "which binary-format handler can launch this". `execve(2)` reads the first bytes and offers them to each registered handler: `binfmt_elf` wants `7f 45 4c 46`, `binfmt_script` wants `23 21` — the two characters `#!`.

If no handler claims the bytes, the file does not run and `execve` returns `ENOEXEC`. The [C example](#in-c) calls `execve` directly on four files that differ only at offset zero, and shows the two refusals — including the one that reports `ENOENT` for a file that plainly exists, because the thing that was missing is the *interpreter named inside it*.

**This question has a page of its own, and it is the one you will need in anger.** Here the shebang is one of four answerers, demonstrated on files that differ obviously. [The first two bytes](../the_first_two_bytes/README.md) stays on this question for a whole page and makes the files differ *invisibly* — three bytes of BOM in front of `#!`, or a single `0d` at the end of that line — so the same `ENOEXEC` and the same `ENOENT` arrive from a file that looks correct in every editor. Both refusals are worth meeting twice: this page produces the `ENOENT` from an interpreter that was never there, which is the mechanism stated as plainly as it can be; that page produces it from `#!/bin/sh`, an interpreter that *is* there, which is the mechanism as the bug you will actually be handed.

**And here questions two and three contradict each other outright, which is the sharpest form of this page's whole argument.** Put a UTF-8 BOM in front of a perfectly good shebang and `file` still calls it a shell script — it even names the BOM — while the kernel refuses to run it, because `file` searched its database for a signature it has a rule for *anywhere* and the kernel compared offset 0 and found `ef` rather than `#`:

```text title="one file, both questions — macOS file-5.41 and Ubuntu 24.04 file-5.45, 2026-09-07"
bytes      ef bb bf 23 21 2f 62 69 6e 2f 73 68 0a      (BOM, then #!/bin/sh)

file --mime-type -b  bom.sh    text/x-shellscript
file --mime-type -b  plain.sh  text/x-shellscript      ← identical answers
execve("bom.sh")               refused, ENOEXEC
execve("plain.sh")             ran                     ← opposite answers
```

Note what carries it: `--mime-type` returns **the same string** for the file that runs and the file that cannot, on both builds, so this is not an artifact of the English wording that [difference 22](../../CONTRIBUTING.md) warns about — it is the two mechanisms genuinely disagreeing. Neither is wrong. They were never asked the same question. [The first two bytes](../the_first_two_bytes/README.md) measured this case and works through what it does to a script you have been handed.

`binfmt_misc` is the extensible version: writing a magic string and an interpreter path into `/proc/sys/fs/binfmt_misc/register` teaches a running Linux kernel to launch a Java class, a Mono `.exe`, or an ARM binary under `qemu`. It is the only pluggable content-sniffing a kernel has, and it exists purely to answer *how do I run this*.

## Question three — what is in it?

`file(1)` is an ordinary unprivileged program. It gets no help from the kernel, and it runs three test classes **in a fixed order, stopping at the first hit**:

1. **filesystem tests** — `stat()`. Directory? Socket? Zero length? Then that is the answer.
2. **magic tests** — compare bytes against the compiled database.
3. **language and encoding tests** — could this be text, and in what encoding?

The ordering is not a detail; it is most of the behaviour. An empty file named `empty.png` is reported `inode/x-empty`, because stage one answered before stage two could open anything — the [shell example](#in-the-terminal) truncates a PNG to zero bytes and watches the answer change with nothing else about the file changing.

### What is actually inside the magic database

On macOS the rules ship as **333 human-readable files** in `/usr/share/file/magic/`, compiled into a single `magic.mgc` of **7,273,344 bytes**. Debian and Ubuntu ship only the compiled form — `/usr/share/file/magic/` is there but empty, and `/usr/share/misc/magic.mgc` is a symlink to a **8,510,760-byte** blob under `/usr/lib/file/`. Same upstream project either way (Christos Zoulas' `libmagic`), so the rules are the same; only one of the two platforms lets you read them.

Here is the rule that identifies a PNG, verbatim from `/usr/share/file/magic/images` on macOS:

```text title="/usr/share/file/magic/images:494 — file-5.41, macOS, 2026-09-07"
0	string		\x89PNG\x0d\x0a\x1a\x0a\x00\x00\x00\x0DIHDR	PNG image data
!:mime	image/png
!:ext   png
!:strength +10
>16	use		png-ihdr
```

Four columns: **offset · type · value to match · message to print**. Then the annotations — `!:mime` is what `--mime-type` reports, `!:ext` the conventional extension, `!:strength` the weight used to rank competing matches. The last line is a **continuation**: one `>` deep, at offset 16, call a named subroutine. That is where `1 x 1, 8-bit/color RGBA, non-interlaced` comes from — a second pass that parses the IHDR chunk's fields.

So magic rules are a small declarative language with offsets, indirection, arithmetic and subroutines, not a table of byte prefixes. `file -k` will show you every rule that matched instead of just the winner, and `file -e soft` disables stage two entirely — on a PNG that turns `PNG image data, …` into a flat `data`, which is a clean way to prove which stage did the work.

**Stage three is the only one that guesses.** UTF-8 has no signature; `café` matches no rule. When `file` says `utf-8` it means "I found no rule, and these bytes are a valid UTF-8 sequence" — an inference, not a lookup. That distinction is the subject of [`file` guesses](../file_guesses/README.md), which picks up exactly where this page stops.

## Question four — what did the user mean?

Desktop environments do not use `libmagic`. GNOME, KDE and XFCE use **shared-mime-info** (`/usr/share/mime/`), whose database holds `globs2` — filename patterns with priorities — *and* a `magic` file. It consults the glob first, and falls through to magic only when the name is unhelpful.

That is a defensible choice for its job: a file manager is guessing which application you want, and the name you gave the file is good evidence of intent. But it means the desktop and `file` answer differently on the same bytes:

```text title="Debian bookworm, file-5.45 + shared-mime-info 2.2, 2026-09-07"
FILE       BYTES     xdg-mime(desktop)  file(1)
liar.txt   \x89PNG   text/plain         image/png
noext      \x89PNG   image/png          image/png
real.png   just      image/png          text/plain
```

Rows one and three are the whole point. Same file, same instant, two "correct" answers, because `file` asked *what are these bytes* and the desktop asked *what did the user probably mean*. Row two shows the desktop does own a magic database — it just ranks the filename higher whenever there is one to rank.

`xdg-mime` and shared-mime-info are Linux-side, which is why that table is a dated fence rather than a recorded example: there is nothing on macOS to run it against.

## In the terminal

The three stages, in order, with the earlier one taking the answer away from the later one.

<!-- output:file_type_four_questions_sh -->
*Verified output of [`file_type_four_questions_sh.sh`](examples/file_type_four_questions_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. STAGE ONE - THE FILESYSTEM TESTS
   Before file(1) reads a single byte it calls stat(). If the answer is
   'this is not a regular file', or 'this is a regular file of length
   zero', that IS the answer and no other test runs.
   adir       inode/directory
   apipe      inode/fifo
   empty.png  inode/x-empty
   Note empty.png. It is named .png, and a magic test would have to read
   bytes to disagree - but there are no bytes, and stage one already
   answered. inode/x-empty is a claim about the INODE, not the content.

2. STAGE TWO - THE MAGIC TESTS
   Only now does file(1) open the file and compare bytes against its
   compiled database. The filename is not an input to this stage.
   liar.txt   image/png
   noext      image/png
   Same 33 bytes, two names, one answer. And the reverse case:
   real.png   text/plain
   real.png is named .png and file(1) does not care, because no rule in
   the database matches the bytes 'p l a i n'.

3. STAGE THREE - THE LANGUAGE AND ENCODING TESTS
   Nothing matched. The last question is 'could this be text?', which is
   answered by validating byte sequences, not by looking anything up.
   utf8.dat   type=text/plain encoding=utf-8
   real.png   type=text/plain encoding=us-ascii
   'café' has no signature. UTF-8 has no signature. utf-8 here is an
   INFERENCE - those six bytes are a valid UTF-8 sequence, so file(1)
   says so. Stage three is the only stage that guesses.

4. THE STAGES ARE ORDERED, AND THE FIRST HIT WINS
   Give the PNG bytes a length of zero and watch stage one take the
   answer away from stage two:
   33 bytes of PNG        image/png
   same name, 0 bytes     inode/x-empty
   Same path, same name, same database. The only thing that changed is
   which stage got to answer first.

5. THE SHELL NEVER ASKS ANY OF THIS
   [ -f ] and friends are stat() and nothing else. They read no bytes,
   so they cannot be fooled by content and cannot see it either.
   liar.txt   -f -s
   adir       -d -s
   apipe      -p
   empty.png  -f
   liar.txt is -f and -s: a regular file, non-empty. That is the whole
   of what the shell knows, and it is true of a PNG, a novel and a core
   dump alike.
```
<!-- /output -->

## In Python

Each layer has its own API, and picking the wrong one is the classic bug. `mimetypes` is the trap: it is a lookup table over the extension that never opens anything, so it is wrong exactly when the filename is.

<!-- output:file_type_four_questions_py -->
*Verified output of [`file_type_four_questions_py.py`](examples/file_type_four_questions_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE INODE KNOWS SEVEN THINGS, AND CONTENT IS NOT ONE OF THEM
   os.lstat() reads the directory entry. It never opens the file, so
   it cannot be lied to by the bytes and cannot see them either.
   liar.txt   type bits = 0o100000  ->  regular file
   adir       type bits = 0o40000   ->  directory
   alink      type bits = 0o120000  ->  symlink
   The whole type lives in S_IFMT. Everything else in st_mode is
   permissions - so with the permissions pinned to 0o644:
     st_mode   0o100644
     S_IFMT    0o100000  the type: regular file
     & 0o7777  0o644     the permissions
   Four bits carry the type. That is the entire vocabulary the
   filesystem layer has for the question, and 'PNG' is not in it.
   (The permission bits are left out of the rows above on purpose:
   a symlink is 0o120755 on macOS and 0o120777 on Linux, so printing
   them would make this page's answer key depend on the machine.)

2. os.stat FOLLOWS A SYMLINK; os.lstat DOES NOT
   alink -> liar.txt.  A symlink is the one type you can only see by
   asking not to follow it:
   os.lstat('alink') -> symlink
   os.stat('alink')  -> regular file
   pathlib.Path.is_file() follows too, so it answers True for a
   symlink and tells you nothing about which of the two you have.

3. mimetypes ASKS THE FILENAME AND NOTHING ELSE
   It is a lookup table over the extension. It never opens the file,
   so it is wrong exactly when the name is:
   liar.txt   mimetypes.guess_type -> text/plain
   real.png   mimetypes.guess_type -> image/png
   empty.png  mimetypes.guess_type -> image/png
   cafe.dat   mimetypes.guess_type -> None
   Two of those four are wrong, and one is None because .dat is not in
   the table. None means 'no opinion', never 'not a known type'.

4. ONLY READING THE BYTES ANSWERS THE QUESTION ASKED
   file       inode          by name          by bytes
   liar.txt   regular file   text/plain       image/png
   real.png   regular file   image/png        text/plain
   empty.png  regular file   image/png        inode/x-empty
   cafe.dat   regular file   -                text/plain
   adir       directory      -                -
   Three columns, three different questions, and on liar.txt three
   different answers - none of which is wrong. They were asked
   'how is it stored', 'what is it called' and 'what is in it'.
```
<!-- /output -->

## In C

The layer nothing else here can show: the sniff the kernel itself performs, in `execve`.

<!-- output:file_type_four_questions_c -->
*Verified output of [`file_type_four_questions_c.c`](examples/file_type_four_questions_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE KERNEL READS THE FIRST BYTES, AND ONLY THE FIRST BYTES
   Four files, all with the executable bit set, all non-empty.
   The only thing that differs is what is at offset zero.

   #!/bin/sh              ran
   no shebang             refused: ENOEXEC (exec format error)
   #!/nonexistent/interp  refused: ENOENT (no such file or directory)
   01 02 03 04 ...        refused: ENOEXEC (exec format error)

2. READING THE TWO REFUSALS
   no_shebang is a perfectly good shell script and the kernel has
   no idea. It is not ELF, it does not start with #!, so no handler
   claims it: ENOEXEC. When you run the same file from a shell it
   works - because the SHELL catches ENOEXEC and runs the file
   itself. That fallback is POSIX shell behaviour, not the kernel.

   shebang_ghost is the confusing one. ENOENT means 'no such file'
   and the file you named plainly exists - the missing one is the
   INTERPRETER inside it, which the kernel read out of the first
   line and failed to open. This is the whole story behind the
   'bad interpreter: No such file or directory' that a shell shows
   for a script whose shebang has a stray carriage return in it.

3. WHAT THIS COSTS TO EXTEND
   ELF and #! are compiled in. Every other format a Linux kernel
   can launch directly - a Java class, a Mono .exe, an ARM binary
   under qemu - is registered at run time through binfmt_misc, by
   writing a magic string and an interpreter path into
   /proc/sys/fs/binfmt_misc/register. That file is the only
   extensible content-sniffing the kernel has, and it exists to
   answer 'how do I run this', never 'what is this'.
```
<!-- /output -->

## The English wording is not stable — the MIME type is

Everything recorded on this page uses `--mime-type` and `--mime-encoding`. The default English phrase is a different matter: it is prose maintained upstream, and it changes between releases. The same non-executable file holding `#!/bin/sh` was described three ways by three versions on one afternoon:

```text title="one file, three file(1) versions, 2026-09-07"
file-5.41  (macOS 26)       POSIX shell script text executable, ASCII text
file-5.44  (Debian 12)      POSIX shell script, ASCII text executable
file-5.45  (Ubuntu 24.04)   POSIX shell script, ASCII text executable
```

The word `executable` moved from one noun to the other between 5.41 and 5.44. This is *version* drift in a single upstream project, not a BSD/GNU fork difference — Debian's 5.44 already agrees with Ubuntu's 5.45, and macOS is simply behind. So: parse `--mime-type` in a script, and never grep the English.

## If you are coming from Python or ABAP

**Python** has one API per layer, and they are easy to confuse because three of them are one line each:

```python
os.lstat(p).st_mode          # question one — the inode, no read; lstat keeps a symlink a symlink
pathlib.Path(p).is_file()    # question one — same syscall, but it FOLLOWS symlinks
mimetypes.guess_type(p)      # question four — the FILENAME only; never opens the file
magic.from_file(p)           # question three — python-magic, a real libmagic binding
```

`mimetypes` is in the standard library and `python-magic` is not, which is why so much code reaches for the wrong one. `mimetypes.guess_type` returning `None` means *"no opinion about this extension"* and never *"not a known type"* — a `.dat` file gets `None` whatever is in it. If you need to know what a file *contains*, no stdlib module will tell you; read the bytes yourself or bind `libmagic`.

**ABAP** made the opposite choice, and the contrast is worth holding onto: there is essentially no content sniffing anywhere in the stack. `cl_gui_frontend_services=>gui_upload` takes `filetype = 'BIN'` or `'ASC'` — the *caller declares* the type and nothing inspects the bytes to check. MIME repository objects carry a MIME type as stored metadata, set when the object was created. So ABAP only ever has question four's answer, and only because a developer typed it in. That is why a wrong `filetype` on `gui_upload` corrupts data silently: nothing downstream is in a position to notice the declaration was false, whereas `file --mime-type` would have contradicted it in one command. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

1. Take any PNG you have and copy it to `notes.txt`. Ask `file --mime-type -b notes.txt`, then `python3 -c "import mimetypes;print(mimetypes.guess_type('notes.txt')[0])"`. Two answers, both right, different questions.
2. `: > empty.png`, then `file --mime-type -b empty.png`. Explain `inode/x-empty` to someone in terms of which stage answered.
3. Truncate a real PNG to zero bytes in place and run `file` before and after. The name never changed; the answering stage did.
4. `file -k` on any file, and then `file -e soft` on the same one. The first shows every rule that matched, the second shows what is left when stage two is switched off.
5. Write a two-line shell script with no `#!`, `chmod +x` it, and run it. It works. Now run it from a program that calls `execve` directly — the [C example](#in-c) does — and watch it fail with `ENOEXEC`. The difference between those two results is your shell, not the kernel.
6. On a Linux desktop, `xdg-mime query filetype` the file from step 1 and compare with `file`. On a Mac there is nothing to compare — note which of the four questions your machine cannot even ask.

## See also

- [The first two bytes](../the_first_two_bytes/README.md) — question two on its own, at the level of detail a broken shebang actually demands: the invisible bytes, the shell that runs the file anyway, and the exit status it hands you
- [`file` guesses](../file_guesses/README.md) — where this page stops: once stage three is running, *which encoding* is a guess, and a pure-ASCII file is every encoding at once
- [Inspecting a file](../inspecting_a_file/README.md) — the same tool inside a workflow: which column of a dump is the file and which is the tool guessing
- [Locale and `LC_CTYPE`](../locale_and_lc_ctype/README.md) — the other invisible input to what a tool decides about your bytes
- [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) — how to look at the signature bytes a magic rule is matching
- [`find`, and filenames that are bytes](../../11_Tools/find/README.md) — the filename as bytes, one layer down from question four
- [`--pre` and `-z` — decompress, then decode](../../11_Tools/decompress_then_decode/README.md) — what to do once `file` has told you it is gzip
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — the one signature that makes stage three certain instead of inferential
