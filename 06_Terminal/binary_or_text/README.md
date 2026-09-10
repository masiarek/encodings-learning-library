# Binary is a verdict, not a property

**Level:** 101 → 201 · for anyone with a terminal

**One line:** Nothing in a file says *binary*: every reader brings its own test, so the three bytes `c0 ff ee` are an error to a UTF-8 decoder, three letters to Latin-1 and plain text to `file`, `grep` and `git` — and renaming the file changes none of those verdicts, only which app a Mac opens it with, where `.bin` means *MacBinary archive*.

```bash
printf '\xc0\xff\xee' > output.bin      # bash, zsh, fish; a portable sh wants '\300\377\356'
cp output.bin output.txt
cmp output.bin output.txt && echo same  # same
```

Two names, one set of bytes. A filename is kept in the directory, not in the file, so the only place *binary* could be written down is in the bytes themselves — and bytes are only numbers. *Binary* is something a reader concludes about them, each reader concludes it by its own test, and the name is an input to exactly one of those tests.

The page uses `c0 ff ee` rather than a member of [the cast](../../CAST.md) because the property it needs is bytes that spell no character at all in UTF-8 — and these three fail for three different reasons, which the [Python example](#in-python) takes apart.

## Who calls it what

Every row was measured on the same three bytes. The shell and Python examples below reproduce all but the last two, which need a real `git` and a Mac.

| Who reads it | The test it applies | Verdict on `c0 ff ee` |
|---|---|---|
| a UTF-8 decoder — `open(p, encoding="utf-8")`, Rust's `read_to_string`, `iconv -f UTF-8` | every sequence must be well-formed UTF-8 | **not text** — it fails at byte 0 |
| a Latin-1 or Windows-1252 decoder | none: each of these bytes is a letter | **text**: `Àÿî` |
| a Mac OS Roman decoder — the table [TextEdit falls back to](#what-textedit-shows-you) | none | **text**: `¿ˇÓ` |
| `file --mime-encoding` | its magic database, then *valid UTF-8? a plausible ISO-8859?* | **text**: `iso-8859-1` |
| `grep`, in the C locale | a NUL byte | **text** |
| `git diff` | a NUL byte in the first 8,000 | **text** |
| the Finder | the **name** | whatever the extension says — [below](#what-the-name-changes-on-a-mac) |

Only the first row refuses these bytes, and it refuses them *as UTF-8* — a verdict about one encoding, not about the file. Every 8-bit table finds a character for each byte: Latin-1 maps all 256 byte values to characters, so under Latin-1 **no** file can fail to decode, which is precisely why Latin-1 can never tell you that a file is binary.

The tools whose job is to *call* a file binary lean on one byte above all — `00`, the byte that [ends a string in C](../../02_Characters/the_nul_byte/README.md). It is `git`'s entire test and `grep`'s first one, and `file` gives up on it too. That is also why all three call a BOM-less UTF-16 file binary: in UTF-16 every ASCII letter carries a `00`.

**`grep` is the row that moves.** In a UTF-8 locale, a line that is not valid UTF-8 changes what both greps do, in opposite styles:

```text title="Measured 2026-09-10 — macOS 26.6.2 (BSD grep 2.6.0-FreeBSD) and ubuntu:24.04 (GNU grep 3.11; en_US.UTF-8 generated, and C.UTF-8 gave the same). File: printf 'good line\nbad \377\376 line\nlast line\n'. Not machine-checked: no answer key can match both."
                          LC_ALL=C          LC_ALL=en_US.UTF-8                   -c, UTF-8
BSD  grep line f          lines 1, 2, 3     lines 1 and 3, nothing on stderr     2
BSD  grep -a line f       lines 1, 2, 3     lines 1 and 3, nothing on stderr     2
GNU  grep line f          lines 1, 2, 3     lines 1 and 3, then on stderr:       3
                                            grep: f: binary file matches
GNU  grep -a line f       lines 1, 2, 3     lines 1, 2, 3                        3
```

By default both greps leave line 2 out, and only one of them tells you. GNU *found* it — `-c` counts three — and withheld it, because printing bytes that are not valid in your locale is part of GNU's definition of binary; `-a` puts it back. BSD never counted it, `-a` changes nothing, and whether BSD sees that line at all depends on the pattern: `grep bad`, which matches the line's first three characters, finds it, while `grep line`, `grep ' '` and `grep 'bad.*line'` do not. [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) has the full comparison, and the advice that follows from it: search a file of unknown encoding under `LC_ALL=C`, where every row in the table above says *text*.

## Why UTF-8 is the one that can say no

A single-byte table is a list of 256 characters, so it cannot fail. UTF-8 is built the other way round: the leading bits of a byte announce how long the sequence is, every byte after the first must begin `10`, and whole ranges of lead bytes are forbidden outright. Most byte strings break one of those rules within a few bytes, which is what makes *not valid UTF-8* such a strong hint in practice. [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) has the rules; [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) has where the check runs.

`c0 ff ee` breaks three different rules, one per byte:

- `c0` announces a two-byte sequence, but a two-byte sequence starting `c0` can only spell `U+0000`–`U+003F`, which ASCII already spells in one byte. That is an [overlong form](../../03_Encodings/overlong_sequences/README.md), so `c0` is never valid anywhere.
- `ff` has eight leading 1 bits, and no UTF-8 sequence starts with more than four.
- `ee` is a perfectly good start of a three-byte sequence — and the file ends.

So `errors="replace"` gives three `U+FFFD`, one for each byte. And notice what the rules do *not* forbid: a NUL is valid UTF-8, since it is the character `U+0000`. A file of `00` bytes passes any UTF-8 decoder and is the one file `grep`, `git` and `file` all call binary. *Binary* and *not UTF-8* are different questions, and the [kata](#practice) turns on it.

## What the name changes on a Mac

macOS picks the application for a double-click through **Launch Services**, which reads the file's **extension**, maps it to a *Uniform Type Identifier* (UTI) — `public.plain-text`, `public.png` — and hands the file to whichever app has registered for that type. It does not open the file.

```text title="Measured 2026-09-10 — macOS 26.6.2. UTI and Kind from mdls; app = the default that Launch Services reports for the file, NSWorkspace.urlForApplication(toOpen:). Every file holds c0 ff ee except the last two. Not machine-checked: Launch Services exists only on macOS."
name          UTI                            Kind                   opens in
output.txt    public.plain-text              Plain Text Document    the default text editor
output.bin    com.apple.macbinary-archive    MacBinary archive      Archive Utility
output.raw    com.panasonic.raw-image        Panasonic raw image    Photos
output.dat    dyn.ah62d4rv4ge80k2py          DAT file               whatever claims .dat
output.hex    dyn.ah62d4rv4ge80u3p2          Document               nothing
output        public.data                    Document               TextEdit
runme         public.unix-executable         Unix Executable File   Terminal     (no extension, chmod +x)
photo.txt     public.plain-text              Plain Text Document    the default text editor   (a real PNG inside)
note.png      public.png                     PNG image              Preview      (plain text inside)
```

The default text editor is TextEdit on a new Mac; on the one measured, its owner had pointed `public.plain-text` at another editor, which is exactly what that column is for. `.dat` and `.hex` have no type of their own — `dyn.…` is a *dynamic* UTI, minted from the extension on the spot — so what opens them depends on what is installed. The machine measured had VLC, which declares `.dat` among the document types it opens; nothing on it claimed `.hex`.

Four things to read off that table.

**`.bin` does not mean *raw bytes* to a Mac. It means MacBinary** — a 1985 format that packed a classic Mac file's two forks and its Finder metadata into one stream, so the file could survive a trip through systems that had nowhere to keep them ([Wikipedia ↗](https://en.wikipedia.org/wiki/MacBinary)). `.bin` was its extension, the system still maps the extension to it, and Archive Utility is registered to unpack it. So a double-click on `output.bin` sends three bytes that were never packed to an unpacker. macOS's own tool agrees that they are not MacBinary:

```text title="Measured 2026-09-10 — macOS 26.6.2, /usr/bin/macbinary 1.0"
$ macbinary probe output.bin; echo $?
29                                              ← not MacBinary
$ printf 'plain text\n' > real.txt && macbinary encode real.txt
$ macbinary probe real.txt.bin; echo $?
0
$ xxd real.txt.bin | head -1
00000000: 0008 7265 616c 2e74 7874 0000 0000 0000  ..real.txt......
```

A real MacBinary file is 128 bytes of header — the name, the Finder type and creator, the two fork lengths — and then the forks, so eleven bytes of text became 256. `.raw` is no safer as a name for raw bytes: the system declares it a Panasonic camera-raw image, and Photos claims it.

**Content is never read.** A real PNG named `photo.txt` goes to the text editor, and plain text named `note.png` goes to Preview. A PNG with *no* extension is `public.data` and opens in TextEdit, not Preview: unlike the Linux desktops in [File type is four questions](../file_type_is_four_questions/README.md), Launch Services has no magic-number fallback at all.

**Two pieces of metadata do count, and neither is content.** An extensionless file with its execute bit set becomes `public.unix-executable` and goes to Terminal. And a file carrying a classic Finder *type code* in its `com.apple.FinderInfo` extended attribute is typed by that code: an extensionless file stamped `TEXT` becomes `com.apple.traditional-mac-plain-text`, Kind *SimpleText Document*. That is the pre-extension Mac way of recording a file's type — exactly the metadata MacBinary existed to carry across.

**A missing extension is not a guess that the file is text.** `output` opens in TextEdit because TextEdit registers as a *viewer* for `public.data`, the type of anything with no better name — which is why the extensionless PNG opens there too.

## What TextEdit shows you

So the name decides which app gets the bytes, and the app then has to decide what they are. A text editor facing bytes that are not valid UTF-8 does not refuse: it falls back to an 8-bit table and shows you whatever letters that table has.

```text title="Measured 2026-09-10 — macOS 26.6.2. textutil reads files 'using the mechanisms provided by the Cocoa text system' (its man page), the system TextEdit is built on, with no encoding named — TextEdit's own default is Automatic. Sublime Text's fallback is the default setting shipped in build 4200. Not machine-checked: neither exists on the Linux runner."
$ textutil -convert txt -encoding UTF-8 -stdout output.txt | xxd -p
c2bfcb87c393        ¿ˇÓ   U+00BF U+02C7 U+00D3   Mac OS Roman

Sublime Text        "fallback_encoding": "Western (Windows 1252)"
                    Àÿî   U+00C0 U+00FF U+00EE   Windows-1252
```

Two editors, two different wrong answers, and neither one refuses. Which of them you see depends on which app owns `.txt` on your Mac — the previous section — so a rename that was meant to protect the file decides, instead, which [mojibake](../../03_Encodings/mojibake/README.md) you get.

## In the terminal

<!-- output:binary_or_text_sh -->
*Verified output of [`binary_or_text_sh.sh`](examples/binary_or_text_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE NAME IS NOT IN THE BYTES
   output.bin  c0 ff ee   3 bytes
   output.txt  c0 ff ee   3 bytes
   output.dat  c0 ff ee   3 bytes
   output      c0 ff ee   3 bytes
   cmp finds no difference between any of them.
   Four names, one set of bytes. A filename is kept in the directory,
   not in the file, so nothing that reads the file can see it.

2. file(1) READS THE BYTES - AND CALLS THEM TEXT
   output.bin  text/plain  iso-8859-1
   output.txt  text/plain  iso-8859-1
   output.dat  text/plain  iso-8859-1
   output      text/plain  iso-8859-1
   The same answer four times, because the name is not an input to
   file(1). And the answer is text: iso-8859-1 means 'high bytes, not
   UTF-8, so some 8-bit table' - and in Latin-1, c0, ff and ee are
   three ordinary letters.

3. A READER THAT INSISTS ON UTF-8 SAYS NO
   iconv -f UTF-8 -t UTF-8 < output.bin      exit 1
   Non-zero: these bytes are not UTF-8. Of the readers in this script it
   is the only one that objects, and its objection is about one
   encoding, not about the file.

4. THREE 8-BIT TABLES, THREE READINGS, NO REFUSALS
   read as ISO-8859-1  Àÿî   written back out as UTF-8: c3 80 c3 bf c3 ae
   read as CP1252      Àÿî   written back out as UTF-8: c3 80 c3 bf c3 ae
   read as MACINTOSH   ¿ˇÓ   written back out as UTF-8: c2 bf cb 87 c3 93
   Latin-1 and Windows-1252 agree on all three bytes, and Mac OS Roman
   disagrees with them on every one. None of the three refused: each
   found a character for every byte, so none of them can call a file
   binary.

5. THE BYTE THAT DOES MAKE A FILE BINARY, TO grep AND file(1)
   output.bin  c0 ff ee     grep -I: text    valid UTF-8: no   file(1): iso-8859-1
   nul.txt     61 00 62 0a  grep -I: binary  valid UTF-8: yes  file(1): binary
   nul.txt is valid UTF-8 - a NUL is the character U+0000 - and it is
   the one grep and file(1) call binary. output.bin is not UTF-8 at all,
   and both of them call it text. 'Binary' and 'not UTF-8' are two
   different questions: a decoder asks the second, and grep asks the
   first - which, in the C locale this script runs in, is a question
   about one byte value, 00.
```
<!-- /output -->

**Section 2 is the surprise.** `file` — the tool whose whole job is saying what a file is — calls these bytes text four times, and never sees a name. **Section 5 is the distinction the page turns on:** the file with a NUL in it is valid UTF-8 and is binary to both tools; the file that is not UTF-8 at all is text to both — in the C locale the example runs in, which is the locale the [`grep` table above](#who-calls-it-what) says to search in.

## In Python

<!-- output:binary_or_text_py -->
*Verified output of [`binary_or_text_py.py`](examples/binary_or_text_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE SET OF BYTES, SIX READINGS
   the bytes              c0 ff ee
   utf-8, strict          UnicodeDecodeError at byte 0
   utf-8, replace         3 of 3 characters are U+FFFD
   latin-1                Àÿî   U+00C0 U+00FF U+00EE
   cp1252                 Àÿî   U+00C0 U+00FF U+00EE
   mac_roman              ¿ˇÓ   U+00BF U+02C7 U+00D3
   git's rule             text - is there a NUL in the first 8000 bytes?
   Strict UTF-8 refuses at the first byte. 'replace' keeps going and
   keeps nothing. The three 8-bit tables each find three characters
   and disagree about which. git's rule never decodes anything at all.
   Latin-1 maps all 256 byte values to characters, so under Latin-1
   no file can fail to decode - which is exactly why it cannot tell you
   that a file is binary.

2. WHY UTF-8 SAYS NO - A DIFFERENT REASON FOR EACH BYTE
   byte  bits      leading 1s  verdict
   c0    11000000  2           overlong - it could only spell U+0000..U+003F
   ff    11111111  8           never valid - no sequence starts with more than four 1s
   ee    11101110  3           truncated - needs 2 continuation bytes, the file ends
   Three bytes, three different failures, and 'replace' puts one U+FFFD
   in place of each - the three that section 1 counted. A random byte
   string almost never gets past these rules, which is what makes 'not
   UTF-8' such a strong hint. It is still a hint about one encoding.

3. THE NAME IS A LABEL - THE MODE IS THE DECLARATION
   written under 4 names with 'wb', read back with 'rb': all identical? True
   open('output.txt', 'rb').read()          -> b'\xc0\xff\xee'
   open('output.txt', encoding='utf-8')     -> UnicodeDecodeError
   open('output.txt', encoding='latin-1')   -> 'Àÿî'
   open(..., 'w').write(<bytes>)            -> TypeError
   open(..., 'wb').write(<str>)             -> TypeError
   The file is called output.txt and Python did not care: 'rb' handed
   back bytes, utf-8 refused, latin-1 found three letters, and each
   write failed on a TYPE, never on a name. Every line would read the
   same for output.bin. The b in the mode is what makes a file binary
   to Python; the extension is a note for the next person to read it.

4. A .hex FILE IS USUALLY TEXT THAT DESCRIBES BYTES
   :03000000C0FFEE50    count, address, type 00 (data), the data, checksum
   :00000001FF          type 01: end of file
   30 bytes, highest byte 0x46, valid UTF-8: True
   That is Intel HEX, the format most .hex files hold. The same three
   bytes of data, spelled as ASCII with an address and a checksum - so
   every reader in section 1 would call this file text.
```
<!-- /output -->

**Section 3 is the part of the usual advice that holds up.** In a program a file is binary because you opened it `'rb'`, and the name plays no part: `'rb'` hands back bytes from `output.txt`, and each wrong write fails on a *type* — `bytes` into a text file, `str` into a binary one — never on a name. So `.bin` is a note to the next person, not an instruction to the program, and that is a perfectly good reason to use it. **Section 4** is what most `.hex` files hold: [Intel HEX](../../08_Build_Your_Own/framing_a_format/README.md), where the same three bytes become two lines of ASCII with an address and a checksum — a text file describing binary data.

## In Rust

<!-- output:binary_or_text_rs -->
*Verified output of [`binary_or_text_rs.rs`](examples/binary_or_text_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. File::create WRITES BYTES, WHATEVER THE NAME SAYS
   wrote c0 ff ee to output.txt; fs::read returns c0 ff ee
   No mode was asked for, and there is none to ask for: a File is
   bytes in and bytes out, whatever its name.

2. ASKING FOR A String IS ASKING 'IS THIS UTF-8?'
   fs::read_to_string -> Err, kind InvalidData
   str::from_utf8     -> Err, valid_up_to 0, error_len Some(1)
   valid_up_to 0: not one byte of it is UTF-8. error_len Some(1): the
   first bad sequence is one byte long - the c0 on its own.

3. from_utf8_lossy SAYS YES BY REPLACING
   3 chars, 3 of them U+FFFD, 9 bytes: ef bf bd ef bf bd ef bf bd
   Three bytes in, nine out, and nothing of the original left in them.

4. LATIN-1 IS THE TABLE WHERE `b as char` IS THE WHOLE DECODER
   "Àÿî"   U+00C0 U+00FF U+00EE
   fs::write of that String -> c3 80 c3 bf c3 ae
   Every u8 is a char under Latin-1, so this step cannot fail. Written
   back, the three letters are six bytes, because a String is UTF-8.
```
<!-- /output -->

Rust has no `'wb'` because it has no text mode: a `File` moves bytes in both directions, and the only place Rust asks *is this text?* is where you ask for a `String` — `read_to_string`, `String::from_utf8` — which is always the same UTF-8 check, and says `InvalidData` for `c0 ff ee` whatever the file is called. [From UTF-8, and lossy](../../05_Rust/from_utf8_and_lossy/README.md) has the three ways past that check.

## `git` asks one question, about one byte

```text title="Measured 2026-09-10 — git 2.52.0 (macOS 26.6.2) and git 2.43.0 (ubuntu:24.04), identical. Not machine-checked: git is not among the tools this library's examples may call."
$ git add coffee.bin nul.txt utf8.dat && git diff --cached --numstat
1       0       coffee.bin        ← c0 ff ee: text, one line added
-       -       nul.txt           ← 78 00 79: binary, no line count
1       0       utf8.dat          ← café in UTF-8: text
```

`git` calls a file binary when a NUL appears in its first 8,000 bytes, and for no other reason — the whole test is `buffer_is_binary()` in git's `xdiff-interface.c`, a search for a zero byte over `FIRST_FEW_BYTES`, which is 8000. So `c0 ff ee` gets a line diff, and so does any `.bin` without a NUL near its start — unless `.gitattributes` says `*.bin binary`, which is how you tell git what the extension could not.

## Which name, then

The usual advice is right that a name is a message. It is a message to people, and to one part of a Mac.

| Name | What it promises | What a Mac does with it |
|---|---|---|
| `.txt` | text — in an encoding it does not name | your text editor, which [has to guess](../file_guesses/README.md) the encoding |
| `.bin` | by convention, bytes in no particular format: firmware, a disk image, a dump | MacBinary archive → Archive Utility |
| `.raw` | by convention, headerless samples or pixels | Panasonic camera raw image → Photos |
| `.dat` | nothing at all | no type of its own; whichever app claims it |
| `.hex` | usually Intel HEX — ASCII lines that *describe* bytes, with addresses and checksums, so a text file | no type of its own |
| none | nothing | `public.data` → TextEdit |

If the bytes have a format, the format's own extension is the honest name: a PNG is binary and is called `.png`, never `.bin`. If they have none, `.bin` is the convention and a fine one — every program ignores it and every person reads it correctly. Just do not expect a double-click to honour it, and do not expect `.txt` to tell anyone the encoding.

## Looking at the bytes

A text editor is the wrong tool for a file whose verdict you do not know, because it will pick a table and show you letters. Use a dump — [`xxd`](../../11_Tools/xxd/README.md) in the terminal:

```bash
xxd output.bin      # 00000000: c0ff ee   ...
```

— or a hex editor. The usual free one on a Mac is **[Hex Fiend ↗](https://hexfiend.com/)** (`brew install --cask hex-fiend`; BSD-2-Clause, by Peter Ammon). It edits in place — inserting and deleting, not only overwriting — opens files far larger than memory, compares two files, and has a data inspector that reads the selected bytes as integers or floats in either byte order. For this library the interesting part is its right-hand column: that column's encoding is a **menu** — ASCII, Mac OS Roman, Latin-1, Latin-2 and both UTF-16 byte orders by default, and others, UTF-8 among them, through *Choose String Encoding…* — where `xxd`'s is fixed at ASCII. It is the one dump in which the question this page is about is a setting you can change and watch.

*Not measured here: Hex Fiend is a GUI, and it was not installed on the machine this page was measured on. The features are from its [README ↗](https://github.com/HexFiend/HexFiend#readme); the encoding menu is read from its source, `app/sources/Encodings.swift`.*

## If you are coming from Python or ABAP

**Python.** The mode is the declaration, and the name is not an input: `open(p, 'rb')` hands you `bytes` from a file called `notes.txt`, and `open(p, encoding='utf-8')` tries to decode one called `firmware.bin`. The one standard-library function that *does* read the name is `mimetypes.guess_type()`, and it is the Finder's logic in miniature — a table keyed on the extension that never opens the file ([File type is four questions](../file_type_is_four_questions/README.md) shows it being wrong). And `bytes.decode('latin-1')` cannot fail, which makes it a way to *avoid* a `UnicodeDecodeError`, never a way to learn what the bytes meant.

**ABAP.** `OPEN DATASET … IN BINARY MODE` against `IN TEXT MODE ENCODING UTF-8` is Python's `'rb'` against `encoding='utf-8'`: the program declares, and the dataset name is a path and nothing more. Text mode is where the check happens — bytes that are invalid in the named encoding raise `CX_SY_CONVERSION_CODEPAGE` unless the statement says `IGNORING CONVERSION ERRORS` — while binary mode hands you an `xstring` and checks nothing, which is the `'rb'` promise exactly. The same shape runs through `GUI_DOWNLOAD`, whose `FILETYPE = 'BIN'` or `'ASC'` is the caller's declaration and never a sniff. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

1. Copy a photo to `photo.txt` and double-click it. Then ask `mdls -name kMDItemContentType photo.txt` and `file --mime-type photo.txt` — the question macOS asked, and the answer the bytes give.
2. Open a file that is not valid UTF-8 in TextEdit, then open it again with **File → Open…**, choosing a different *Plain Text Encoding* under **Options**. Same bytes, different letters — and no setting anywhere that says *binary*.
3. Find a file your tools call binary — a PDF, a `.docx`, a compiled program — and see which test fired: `head -c 8000 f | tr -dc '\000' | wc -c` counts the NULs `git` would see.
4. Stamp a Finder type code on an extensionless text file with `xattr -wx com.apple.FinderInfo 5445585400000000000000000000000000000000000000000000000000000000 note`, and ask `mdls -name kMDItemKind note`. Remove it with `xattr -d com.apple.FinderInfo note` and ask again.
5. On a Linux machine, `grep` a Latin-1 file under `LC_ALL=C` and then under `LC_ALL=C.UTF-8`, with and without `-a`. Count the lines that come back each time, and read stderr.

## Practice

**Four files, twelve answers, and a rename.**

```text
coffee.txt    c0 ff ee
notes.bin     63 61 66 c3 a9 0a        café, in UTF-8
legacy.txt    63 61 66 e9 0a           café, in Latin-1
data.txt      61 00 62 0a
```

For each file, predict three things: is it valid UTF-8? Does it have a NUL in its first 8,000 bytes — `git`'s test? And what does `file --mime-encoding` say? Then rename all four to `.dat`. How many of your twelve answers change — and which verdict on a Mac *does* the rename change?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:binary_or_text_kata_sh -->
*Verified output of [`binary_or_text_kata_sh.sh`](examples/binary_or_text_kata_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FOUR FILES, TWELVE ANSWERS
   file        bytes               valid UTF-8  NUL in first 8000  file(1)
   coffee.txt  c0 ff ee            no           no                 iso-8859-1
   notes.bin   63 61 66 c3 a9 0a   yes          no                 utf-8
   legacy.txt  63 61 66 e9 0a      no           no                 iso-8859-1
   data.txt    61 00 62 0a         yes          yes                binary

2. RENAME ALL FOUR TO .dat, AND ASK AGAIN
   file        bytes               valid UTF-8  NUL in first 8000  file(1)
   coffee.dat  c0 ff ee            no           no                 iso-8859-1
   notes.dat   63 61 66 c3 a9 0a   yes          no                 utf-8
   legacy.dat  63 61 66 e9 0a      no           no                 iso-8859-1
   data.dat    61 00 62 0a         yes          yes                binary
   Not one of the twelve answers moved. Each reader opened the file and
   looked at bytes, and none of them was ever told the file's name.

3. THE TWO THAT SURPRISE
   data is VALID UTF-8 - a NUL is the character U+0000 - and it is the
   only one of the four that git's rule and file(1) call binary.
   legacy is NOT valid UTF-8, and both of them call it text.
   'Binary' and 'not UTF-8' are two different questions. A decoder asks
   the second. git's rule asks the first, and for git the first is a
   question about a single byte value, 00 - on all four files file(1)
   gave the same verdict.
```
<!-- /output -->

**The verdict the rename does move is the Finder's**, which never read any of the four. Before it, `.txt` went to the text editor and `.bin` to Archive Utility; after it, all four are `.dat`, a dynamic UTI that opens in whatever app has claimed `.dat` — VLC, on the machine [measured above](#what-the-name-changes-on-a-mac), and nothing at all on a Mac where no app has.

</details>

## See also

- [File type is four questions](../file_type_is_four_questions/README.md) — the four mechanisms that answer "what kind of file is this?", and the Linux desktop's version of the Finder's question
- [`file` guesses](../file_guesses/README.md) — what `iso-8859-1` means when `file` says it, and why a pure-ASCII file is every encoding at once
- [Mojibake](../../03_Encodings/mojibake/README.md) — what the editor showed you, and how to read it backwards
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — where the UTF-8 check runs, and what gets past it
- [The NUL byte](../../02_Characters/the_nul_byte/README.md) — the one byte every binary test looks for
- [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) — the locale split in full, and the line BSD grep never shows you
- [`printf` writes bytes](../printf_writes_bytes/README.md) — making the test file in the first place, and the `printf` that drops your backslash
- [Opening a file](../../04_Python/opening_a_file/README.md) — Python's side of the mode, and the default encoding it bets on
- [From UTF-8, and lossy](../../05_Rust/from_utf8_and_lossy/README.md) — Rust's side of the one question
- [A record has to say what it is](../../08_Build_Your_Own/framing_a_format/README.md) — Intel HEX, the text most `.hex` files hold
