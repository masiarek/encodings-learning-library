# `bintrans(1)`: `base64`, `uuencode` and `uudecode` are one page, and it says which GNU flags it takes

**Level:** reference · for anyone who typed `man base64` on a Mac and got a page called BINTRANS

**One line:** On this Mac `man base64`, `man uuencode` and `man uudecode` open the same FreeBSD page, which documents six command names as front ends to one program and states which GNU `base64` flags it accepts for compatibility; measured, one of the accepted flags is rejected, the file operand the page mentions is refused, and the one behaviour that actually differs from GNU, wrapping at 76, is on the GNU side of the page's silence.

**The pages:** [`base64(1)`](raw/macos/base64.1.txt) · [`uuencode(1)`](raw/macos/uuencode.1.txt) · [`uudecode(1)`](raw/macos/uudecode.1.txt), three dumps of one page, `bintrans(1)`, macOS, dated January 23, 2024; `cmp` finds the three files byte-identical and `man -w` resolves all three names, and `bintrans` itself, to `bintrans.1`. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). Ubuntu 24.04 has GNU coreutils' `base64(1)` and no `uuencode` at all (`sharutils` is not installed); its `base64` was measured.

## What the pages are for

`uuencode` and `uudecode` *appeared in 4.0BSD*, the page's HISTORY says, and they solved the problem [Binary to text](../../03_Encodings/binary_to_text/README.md) describes: a channel that carries only printable ASCII, and a file that is not. `bintrans` is FreeBSD's recent consolidation of the old pair, `base64`, and the `b64encode`/`b64decode` names into one program that looks at `argv[0]`, and the page's NAME line lists all six. On this Mac `ls -l` shows `uuencode`, `uudecode`, `b64encode` and `bintrans` as four hard links to one 136192-byte file, and `base64` and `b64decode` as a second pair of links; `base64 --version` answers *FreeBSD base64*.

The page lives in section 1 because these are commands, and it is a short page: six SYNOPSIS lines, a DESCRIPTION that says what each name does, and three option lists. What it does not contain is the file format. *The encoding uses only printing ASCII characters and includes the mode of the file and the operand name for use by uudecode*, and then SEE ALSO points at `uuencode(5)`, which this Mac does not have: `man -w 5 uuencode` says *No manual entry*. So the format the measurements below take apart, `begin 644 name`, 45-byte lines encoded three bytes to four characters from an alphabet that starts at space, a backtick where a space would be, `end`, is documented on this machine nowhere at all.

The library cares because `base64` is the binary-to-text encoding everyone meets, and because this page is where the flags' meanings are written down, on the platform where they mean something different from GNU's. The library's [CONTRIBUTING finding 14](../../CONTRIBUTING.md) lists five places `base64` disagrees with itself between the two builds; this page is where two of the five are announced and three are not.

## The page, with notes

### Six names, one program

```text title="man 1 base64 (BINTRANS(1)), macOS 26.6.2, dumped 2026-09-13"
NAME
     bintrans, uuencode, uudecode, b64encode, b64decode, base64 - encode /
     decode a binary file

SYNOPSIS
     bintrans [algorithm] [...]
     uuencode [-m] [-r] [-o output_file] [file] name
     uudecode [-cimprs] [file ...]
     uudecode [-i] -o output_file
     b64encode [-r] [-w column] [-o output_file] [file] name
     b64decode [-cimprs] [file ...]
     b64decode [-i] -o output_file [file]
     base64 [-h | -D | -d] [-b count] [-i input_file] [-o output_file]
```

Read the last line against the second: `uuencode` takes a `file` operand and a `name` to write into the header; `base64` takes neither, only `-i input_file`. *The b64encode utility is synonymous with uuencode with the -m flag specified*, so `b64encode` produces the framed `begin-base64` form and `base64` the bare stream. The `[algorithm]` after `bintrans` is one of those five names or `qp`, the quoted-printable converter that has no name of its own.

### The paragraph about GNU

```text title="man 1 base64 (BINTRANS(1)), macOS 26.6.2, dumped 2026-09-13"
     The base64 utility acts as a base64 decoder when passed the --decode (or
     -d) flag and as a base64 encoder otherwise.  As a decoder it only accepts
     raw base64 input and as an encoder it does not produce the framing lines.
     base64 reads standard input or file if it is provided and writes to
     standard output.  Options --wrap (or -w) and --ignore-garbage (or -i) are
     accepted for compatibility with GNU base64, but the latter is
     unimplemented and silently ignored.
```

Four claims, and the measurements below test each. *Reads standard input or file if it is provided*: `base64 s.txt` on this Mac is *invalid argument*, exit 64; only `-i s.txt` reads a file, and the SYNOPSIS line above is the one that is right. *--wrap (or -w) accepted*: true, `-w 8` and `--wrap=8` both break the output, and so do the page's own `-b 8` and `--break=8`. *--ignore-garbage (or -i) accepted*: `--ignore-garbage` is *unrecognized option*, exit 64, and `-i` is the input-file flag, so the letter is taken and the long form is refused; nothing here is *silently ignored*. And what the paragraph does not say is the thing that matters most: this decoder accepts a space inside the payload without `-i`, and GNU's does not without it.

### `uuencode`, `uudecode`, and the filename paragraph

```text title="man 1 base64 (BINTRANS(1)), macOS 26.6.2, dumped 2026-09-13"
     -m     Use the Base64 method of encoding, rather than the traditional
            uuencode algorithm.

     -r     Produce raw output by excluding the initial and final framing
            lines.
     ...
     -p     Decode file and write output to standard output.

     -r     Decode raw (or broken) input, which is missing the initial and
            possibly the final framing lines.  The input is assumed to be in
            ...

     -s     Do not strip output pathname to base filename.  By default
            uudecode deletes any prefix ending with the last slash '/' for
            security reasons.
```

`-m` swaps the 1980 alphabet for base64's and the `begin` line for `begin-base64`, and the terminator for `====`; the bytes in between are exactly what `base64` prints. `-r` on the encoder drops the two framing lines, `-r` on the decoder reads input that has none, and `-r -m` together is what the page says `b64decode` does. `-p` is the flag that keeps a decode off the filesystem. The `-s` paragraph is the page's one security sentence and it is about a real attack: a `uuencode` header names the file the decoder will create, and `begin 644 ../../.ssh/authorized_keys` is a valid header, so the default throws the directories away and `-s` is how you ask to keep them. `-i` refuses to overwrite, `-o` overrides the name entirely, `-c` decodes several files from one stream, which is what the EXAMPLES do with `$MAIL`.

### `base64`'s own options

```text title="man 1 base64 (BINTRANS(1)), macOS 26.6.2, dumped 2026-09-13"
     -b count, --break=count
            Insert line breaks every count characters.  The default is 0,
            which generates an unbroken stream.

     -d, -D, --decode
            Decode incoming Base64 stream into binary data.
     ...
     -i input_file, --input=input_file
            Read input from input_file.  The default is stdin; passing "-"
            also represents stdin.
```

*The default is 0* is the sentence to hold against GNU's `--help`, which says `-w, --wrap=COLS wrap encoded lines after COLS character (default 76)`. The same command, `base64 file > out`, writes a different file on the two machines. `-D` is a BSD spelling GNU rejects; `-d` and `--decode` work on both. And `-i` is the letter that means *input file* here and *ignore garbage* there, neither of which errors when the other was meant.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| `bintrans` | FreeBSD's one binary behind six names; *binary translation* | this page, above |
| `uuencode`, `uudecode` | The 4.0BSD pair: *Unix to Unix*, from the `uucp` mail network the EXAMPLES still mention | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| Base64, *the Base64 method* | Three bytes re-cut into four six-bit numbers, each spelled from a 64-character alphabet | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| *the traditional uuencode algorithm* | The same re-cut with a different alphabet: space plus the value, `0x20` to `0x5f` | this page, below |
| framing lines | `begin MODE NAME` and `end`, or `begin-base64 MODE NAME` and `====`; what `-r` leaves out | this page, below |
| mode (`644`) | The file's permission bits, in octal, carried in the header; `uudecode` restores them minus setuid and execute | [`tar(5)` and `cpio(5)`](archives.md) |
| raw (`-r`) | Just the encoded lines, no header, no terminator | this page, above |
| *break*, *wrap*, `-b`, `-w` | Line length of the encoded output; 0 here, 76 on GNU | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| `=` | Padding: how many bytes the last group really held, not data | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| *garbage*, `--ignore-garbage` | Characters outside the alphabet in a decoder's input; GNU's `-i` skips them, this build rejects the flag | this page, below |
| `qp`, quoted-printable | The escape, not the encoding: `é` becomes `=C3=A9` and `a` stays `a` | [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) |
| *mail-safe*, *transmission mediums that do not support other than simple ASCII data* | The seven-bit channel all of this exists for | [UTF-7, and the seven-bit transport](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) |
| *expanded by 35%* | Four characters per three bytes, plus one length byte and a newline per 45-byte line | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| base filename, *prefix ending with the last slash* | What `uudecode` keeps of the header's name unless `-s` | [A record has to say what it is](../../08_Build_Your_Own/framing_a_format/README.md) |
| `$MAIL` | The user's mailbox file; `uudecode -c < $MAIL` was how attachments arrived | [`bintrans(1)`](raw/macos/base64.1.txt) |
| `base32`, `basenc` | GNU's siblings for the other alphabets; not on this page, not in this base system | [The alphabet is not the encoding](../../03_Encodings/base32_alphabets/README.md) |

## Try it on your machine

**One string, both encoders.** `café €` without a newline is nine bytes, three groups exactly, so no padding.

```text title="Measured 2026-09-13 — byte-identical on macOS 26.6.2 (FreeBSD base64) and ubuntu:24.04 (GNU coreutils 9.4)."
$ printf 'caf\303\251 \342\202\254' | base64
Y2Fmw6kg4oKs
```

**Wrapping, and the flags that set it.** A hundred bytes of `A`, and the nine-byte string with a width of eight.

```text title="Measured 2026-09-13 — macOS 26.6.2 (FreeBSD base64) and ubuntu:24.04 (GNU coreutils 9.4). Not machine-checked: the default differs."
                                        macOS                            ubuntu:24.04
$ head -c 100 /dev/zero | tr '\0' A | base64 | awk '{print length($0)}'
                                        136                              76
                                                                         60
$ base64 -w 8 < s.txt                   Y2Fmw6kg / 4oKs                  Y2Fmw6kg / 4oKs
$ base64 --wrap=8 < s.txt               Y2Fmw6kg / 4oKs                  Y2Fmw6kg / 4oKs
$ base64 -b 8 < s.txt                   Y2Fmw6kg / 4oKs                  base64: invalid option -- 'b'      (exit 1)
$ base64 s.txt                          base64: invalid argument s.txt   Y2Fmw6kg4oKs
                                        (usage follows; exit 64)
```

The page is right that `-w` is accepted, and its DESCRIPTION is wrong that a file operand is. The default is the finding: one line of 136 characters here, 76 and 60 there.

**Decoding: `-D`, `-d`, `-i`, and a space in the payload.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: every row differs."
                                                macOS                                        ubuntu:24.04
$ printf 'Y2Fmw6k=' | base64 -D                 café          exit 0                         base64: invalid option -- 'D'   exit 1
$ printf 'Y2Fmw6k=' | base64 -d                 café          exit 0                         café          exit 0
$ base64 -i s.txt                               Y2Fmw6kg4oKs  exit 0   (input file)          Y2Fmw6kg4oKs  exit 0   (ignore garbage; file operand)
$ printf 'Y2Fm w6k=' | base64 -d | xxd -p       636166c3a9    exit 0                         636166        exit 1   base64: invalid input
$ printf 'Y2Fm w6k=' | base64 -d -i | xxd -p    (usage: -i needs an argument)  exit 64       636166c3a9    exit 0
$ printf 'Y2Fm w6k=' | base64 -d --ignore-garbage
                                                base64: unrecognized option    exit 64       636166c3a9    exit 0
$ printf 'Y2Fm!w6k=' | base64 -d                base64: stdin: (null): error decoding base64 input stream   exit 1
                                                                                             636166  base64: invalid input   exit 1
```

Row three is the quiet one from finding 14: the same command line succeeds on both machines with exit 0, and means *read this file* on one and *skip bad characters in stdin, then read this file* on the other. Rows four to six are the page's GNU paragraph measured: this build decodes past a space without being asked, refuses a `!`, and refuses the flag the page says it accepts. GNU emits the partial `636166`, says `invalid input`, and needs `-i` to continue.

**The `uuencode` format, which no page here documents.** `cat -vet` shows the line ends.

```text title="Measured 2026-09-13 — macOS 26.6.2 (FreeBSD uuencode). Ubuntu has no uuencode; its python3 is the cross-check below. Not machine-checked."
$ uuencode s.txt cafe.txt | cat -vet
begin 644 cafe.txt$
)8V%FPZD@XH*L$
`$
end$
$ uuencode -m s.txt cafe.txt | cat -vet
begin-base64 644 cafe.txt$
Y2Fmw6kg4oKs$
====$
$ head -c 100 /dev/zero | tr '\0' A | uuencode x | awk '{ printf "%2d chars, starts %s\n", length($0), substr($0,1,1) }'
11 chars, starts b
61 chars, starts M
61 chars, starts M
17 chars, starts *
 1 chars, starts `
 3 chars, starts e
```

Every encoded line starts with its own byte count, spelled as space plus the count: `)` is `0x29`, `0x20` + 9, for the nine-byte string; `M` is `0x4d`, `0x20` + 45, for a full line; `*` is 10, the remainder. Then the bytes, three to four characters, each character `0x20` + a six-bit value, so the alphabet runs from space to `_`. A zero would be a space, which mail software trimmed, so the convention writes a backtick (`0x60`) instead, and the terminator is a line holding nothing but that backtick: a zero-length line. The base64 form is `base64`'s output with `begin-base64` above it and `====` below. Ubuntu cannot run any of this, but Python can spell the line:

```text title="Measured 2026-09-13 — ubuntu:24.04 (python3 3.12.3; sharutils not installed)."
$ command -v uuencode; echo "exit $?"
exit 1
$ python3 -c "import binascii,sys; sys.stdout.write(binascii.b2a_uu(open('s.txt','rb').read()).decode())" | cat -vet
)8V%FPZD@XH*L$
$ python3 -c "import binascii; print(binascii.b2a_uu(b'').decode(), end='')" | cat -vet
 $
```

The same thirteen characters as the Mac's line. The zero-length line is where they part: Python writes the space the standard says, FreeBSD's `uuencode` writes the backtick the convention says, and every decoder accepts both. (This Mac's `python3` is 3.14 and its `uu` module is gone; `binascii.b2a_uu` remains on both.)

**The round trip, and the filename.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (FreeBSD uuencode/uudecode). Not machine-checked: Ubuntu has neither."
$ uuencode s.txt cafe.txt > s.uu && uudecode -o out.txt s.uu && cmp s.txt out.txt && echo identical
identical
$ uudecode -p s.uu | xxd -p
636166c3a920e282ac
$ uuencode -m -r s.txt x | uudecode -r -m -p | xxd -p
636166c3a920e282ac
$ uuencode s.txt sub/dir/name.txt | uudecode; ls
name.txt  out.txt  s.txt  s.uu
$ uuencode s.txt sub/dir/name.txt | uudecode -s
uudecode: stdin: sub/dir/name.txt: No such file or directory
$ printf 'caf\303\251 \342\202\254=' | bintrans qp
caf=C3=A9 =E2=82=AC=3D
```

`cmp` is the right judge of a round trip: it compares bytes and says nothing, which is what *identical* should look like. The header asked for `sub/dir/name.txt` and the default wrote `name.txt` in the current directory, as the `-s` paragraph promises; `-s` tried the path and failed because the directory does not exist, which is the safe failure. The last line is `qp`: an escape, not an encoding, which is why `caf` came through as itself and only the bytes above `7f`, and the `=` that would otherwise be ambiguous, were rewritten: [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md).

## Where the page is dated, and what it does not say

**The page is dated January 23, 2024** and describes a `base64` that reads a file operand and accepts `--ignore-garbage`; this Mac's build does neither. Its `-w` claim is right and its `-b` default is right. The page's whole account of GNU compatibility is that paragraph, and the five-way split in finding 14 is mostly outside it: the 76-column default, `-D`, and the space in the payload are not mentioned.

**`uuencode(5)` is cited and absent.** The SEE ALSO points at a page that documents the format, and `man -w 5 uuencode` on this Mac finds nothing. The 45-byte line, the length character, the space-plus-value alphabet and the backtick convention are the format's whole definition and appear on no page on this machine. The measurement above is the only place they are written down here.

**No RFC, no `base64url`, no `base32`.** The page never names [RFC 4648 ↗](https://www.rfc-editor.org/rfc/rfc4648), does not say what happens to `+` and `/` in a URL, and does not have the `base32` or `basenc` commands GNU coreutils ships beside `base64`. The library's [The alphabet is not the encoding](../../03_Encodings/base32_alphabets/README.md) is the page for the alphabets this one leaves out.

**Nothing on the page is about text.** *Encode a binary file* is the NAME line, and it is exact: `base64` takes bytes and returns ASCII, and never asks what encoding the bytes were in. `Y2Fmw6k=` and `Y2Fm6Q==` are both *café*, one from UTF-8 and one from Latin-1, and this page cannot tell them apart because it was never told. The lesson calls that the bug you will actually hit; the page, correctly, does not mention it.

**Ubuntu has half the page.** GNU's `base64(1)` documents `-d`, `-i`, `-w` and nothing else; `uuencode` and `uudecode` are in `sharutils`, which the image does not carry, and `command -v uuencode` exits 1. A script that shells out to `uuencode` runs on this Mac and not on that container, and the page has no way of saying so.

## See also

- [`vis(1)` and `vis(3)`](vis.md) — the other escape into printable ASCII, one character at a time instead of the whole stream
- [`hexdump(1)`, `od(1)`, `xxd(1)` and `strings(1)`](dump_tools.md) — a hex dump is the same idea at four bits per character, and `xxd`'s page says so
- [`diff(1)`, `cmp(1)`, `cksum(1)` and `md5(1)`](compare.md) — `cmp`, the judge of every round trip above
- [Binary to text](../../03_Encodings/binary_to_text/README.md) — three bytes to four characters by hand, the padding, and why base64 has no charset
- [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) — what `qp` is, and how it differs from an encoding
- [The alphabet is not the encoding](../../03_Encodings/base32_alphabets/README.md) — the alphabets this page never names
- [UTF-7, and the seven-bit transport](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) — modified base64, the same trick applied to UTF-16 inside mail
- [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) — `begin`, the length character and `end` as a framing
- [A page has a date](../a_page_has_a_date/README.md) — a 2024 page whose GNU paragraph does not match its binary
- [What the page does not say](../what_the_page_does_not_say/README.md) — the format, cited to a page that is not there
