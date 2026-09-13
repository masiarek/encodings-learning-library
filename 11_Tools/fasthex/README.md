# `fasthex -h`, line by line

**Level:** 201 · for anyone who has run `fasthex -h` and wants every flag shown once, beside what the dumps already on the machine print

**One line:** `fasthex` is a hex dump written for the sixty-gigabyte file — it formats in parallel and never asks what a byte *means*, which is why it is sixty-five times faster than `xxd` on the machine that measured it — and its help screen, read a line at a time, is a list of everything a dump decides before it prints: one byte or two, which end first, which of five tables draws the text column, and whether an offset is a label or an instruction. This page runs every line of it once and reads the answer against [`hexdump`](../hexdump/README.md), [`xxd`](../xxd/README.md) and [`od`](../od/README.md).

`fasthex` is a Rust program by CallMeAlphabet, on [crates.io ↗](https://crates.io/crates/fasthex) and [GitHub ↗](https://github.com/CallMeAlphabet/fasthex) under the Apache-2.0 licence, and it has no man page: `fasthex -h` is the documentation on your machine, and it is reproduced below verbatim, in seven pieces. Neither CI runner has the tool, so every `fasthex` fence here is dated and names the machine it ran on — fasthex 0.3.27 on macOS 26.6.2, x86-64 — and none of them is an answer key. What CI does check is [the baseline at the end](#the-baseline-what-you-already-have-prints): the same files through the tools every machine has, which is what each fasthex fence is read against.

## Installing it, and the error you meet first

`cargo install fasthex` fails on a stable toolchain, before the tool has printed anything:

```text title="Measured 2026-09-13 — cargo 1.98.0 and rustc 1.98.0 (stable), building the source of fasthex 0.3.27 in place. cargo install fasthex fails the same way, with the registry path in the arrow line."
error[E0554]: `#![feature]` may not be used on the stable release channel
 --> src/main.rs:1:1
  |
1 | #![feature(portable_simd)]
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: unnecessary `unsafe` block
    --> src/main.rs:3633:9
     |
3633 |         unsafe {
     |         ^^^^^^ unnecessary `unsafe` block
     |
     = note: `#[warn(unused_unsafe)]` (part of `#[warn(unused)]`) on by default
```

The first line of `src/main.rs` is `#![feature(portable_simd)]`, and a `#![feature]` gate is what nightly Rust is *for*: `std::simd` is where the speed on this page comes from, and it has not been stabilised. The crate says so — it ships a `rust-toolchain.toml` pinning `channel = "nightly"` — but `rustup` reads that file from the directory you *build in*, and `cargo install` builds in a temporary one, so the pin never applies. Name the toolchain on the command line instead:

```bash
cargo +nightly install fasthex
```

`rustup toolchain install nightly` first if you have none. The binary lands in `~/.cargo/bin`, which `rustup` puts on your `PATH`.

## What prints it

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -h | wc -l | tr -d ' '
61

$ fasthex -h > /dev/null; echo exit=$?
exit=0

$ fasthex --help | cmp - <(fasthex -h) && echo identical
identical

$ fasthex -v
fasthex 0.3.27
```

`-h` and `--help` print the same 61 lines to standard output and exit 0; `-v` and `--version` print the one line. There is no summary form and no `help` subcommand: `fasthex` with no arguments reads standard input, so typed alone at a terminal it waits for you.

## Usage

```text title="Measured 2026-09-13 — fasthex -h, fasthex 0.3.27 (cargo), macOS 26.6.2. Verbatim, in seven pieces split at its own headings; only the blank line at each split is dropped. Not machine-checked: neither CI runner ships fasthex."
fasthex 0.3.27 - a very fast hex dumper

Usage:
  fasthex [options] [file]...
  fasthex -r [options] [file] [-j <offset>]
  fasthex [options] -          read from stdin explicitly

Multiple files are concatenated and treated as one stream.
If no file is given, reads from stdin.
```

| On the screen | What it means | Read more |
|---|---|---|
| `[file]...` · `concatenated` | several files are one stream: the offsets run on across the seam, and `-s` and `-n` count through it | below |
| `-r [options] [file] [-j <offset>]` | reverse mode, which reads a dump and writes bytes — with a `-j` that [changed nothing measured](#where-the-screen-and-the-program-disagree) | [the way back](#plain-and-the-way-back) |
| `-` | standard input, named — for the day the file is called `-` | |
| `reads from stdin` | a pipe is fine, and a seekable file is better: [one flag](#offset-and-navigation) needs one | |

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex s.txt s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a 63 61 66 c3  |caf..: 1....caf.|
00000010: a9 3a 20 31 e2 82 ac 0a                          |.: 1....        |
00000018

$ fasthex -s 10 -n 4 s.txt s.txt
0000000a: ac 0a 63 61                                      |..ca            |
0000000e

$ fasthex nonexistent.bin; echo exit=$?
fasthex: nonexistent.bin: No such file or directory (os error 2)
exit=1

$ fasthex -q nonexistent.bin; echo exit=$?
exit=1

$ fasthex s.txt nonexistent.bin; echo exit=$?
Error: Custom { kind: NotFound, error: "nonexistent.bin: No such file or directory (os error 2)" }
exit=1

$ fasthex empty.bin | wc -c | tr -d ' '
0
```

Two files of twelve bytes are one stream of twenty-four, and `-s 10 -n 4` reads across the join. The errors are worth a look because there are two of them: one missing file gets a sentence and exit 1, and `-q` removes the sentence and keeps the status; a missing file *among several* gets Rust's debug rendering of the same error, from a different code path. An empty file prints nothing at all — no final offset line — which is what `hexdump -C` and `xxd` do too.

## Output format

```text title="fasthex -h, continued — verbatim."
OUTPUT FORMAT
  Rule: lowercase = one-byte mode, UPPERCASE = two-byte mode.

      (default)               canonical hex + ASCII display
  -x, --hex                   one-byte hexadecimal display
  -X, --hex-wide              two-byte hexadecimal display
  -o, --octal                 one-byte octal display
  -O, --octal-wide            two-byte octal display
  -d, --decimal               one-byte decimal display
  -D, --decimal-wide          two-byte decimal display
  -c, --chars                 one-byte character display
  -b, --binary                binary display (8 bits per byte)
  -p, --plain                 plain hex string, no offset or ASCII
  -i, --include               C include file style output
  -r, --reverse               convert hex dump back to binary
```

### The default, and the rule

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf..: 1....    |
0000000c

$ xxd s.txt
00000000: 6361 66c3 a93a 2031 e282 ac0a            caf..: 1....

$ hexdump -C s.txt
00000000  63 61 66 c3 a9 3a 20 31  e2 82 ac 0a              |caf..: 1....|
0000000c
```

The default row is assembled from the two dumps under it: `xxd`'s offset, with the colon, in front of `hexdump -C`'s cells — one per byte, a wider gap after the eighth — and `hexdump -C`'s text panel in pipes, padded to sixteen where hexdump's is not. The final line is the length, as in `hexdump -C`. Like both of them, and unlike a bare `hexdump`, the default shows the bytes in file order.

The rule on the screen — *lowercase = one-byte mode, UPPERCASE = two-byte mode* — is [chapter 1's byte-order lesson](../../01_Bits_and_Bytes/which_end_comes_first/README.md) as a case convention, and the two-byte modes are where this tool departs from the one everyone has:

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -x s.txt
00000000:   63  61  66  c3  a9  3a  20  31  e2  82  ac  0a                
0000000c

$ fasthex -X s.txt
00000000:  6361 66c3 a93a 2031 e282 ac0a          
0000000c

$ fasthex -X -E little s.txt
00000000:  6163 c366 3aa9 3120 82e2 0aac          
0000000c

$ hexdump -x s.txt
0000000    6163    c366    3aa9    3120    82e2    0aac                
000000c
```

Read the first pair. `fasthex -X` prints `6361`, which is the file: byte `63`, then byte `61`. `hexdump -x` prints `6163`, which is the number those two bytes make when a little-endian CPU reads them as one 16-bit integer — [the default that lies](../hexdump/README.md), one preset along. `fasthex`'s two-byte modes default to `-E big`, which for a dump is the same thing as *file order*, and `-E little` is the flag that reproduces `hexdump`. So the flag that makes `fasthex` agree with `hexdump` is the one that makes it swap, and `hexdump -x` has no flag to go the other way. `-x`, the one-byte mode, is the same bytes in wider cells and nothing more to say.

Decimal and octal follow the rule:

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -D s.txt
00000000:  25441 26307 43322 08241 57986 44042            
0000000c

$ fasthex -D -E little s.txt
00000000:  24931 50022 15017 12576 33506 02732            
0000000c

$ hexdump -d s.txt
0000000   24931   50022   15017   12576   33506   02732                
000000c

$ fasthex -o s.txt
00000000:  143 141 146 303 251 072 040 061 342 202 254 012                
0000000c

$ fasthex -O s.txt
00000000:  061541 063303 124472 020061 161202 126012              
0000000c
```

`25441` is `0x6361` and `24931` is `0x6163`: `-D` reads big-endian, `-D -E little` reads what `hexdump -d` reads. `-O` is the same pairs in six octal digits. None of the numeric views has a text panel — only the default does — so `-A` and `-T` do nothing to them, as with `hexdump -x`.

| On the screen | What it means | Read more |
|---|---|---|
| `(default)` | file order, one byte per cell, `hexdump -C`'s panel behind `xxd`'s offset | above |
| `-x` / `-X` | hex, one byte or two per cell; two-byte cells read in `-E`'s order, **big by default**, which is the file's | [Which end comes first](../../01_Bits_and_Bytes/which_end_comes_first/README.md) |
| `-o` / `-O`, `-d` / `-D` | octal and decimal, same rule; `-D -E little` is `hexdump -d` | [`hexdump`'s six presets](../hexdump/README.md) |
| `-c` | one *character* per cell, octal for what it cannot draw — `hexdump -c`'s view, with [one difference](#characters-and-bits) | [Control characters](../../02_Characters/control_characters/README.md) |
| `-b` | eight bits per byte — the view `xxd -b` has and `hexdump` does not | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| `-p` | the hex and nothing else, `xxd -p` | [`xxd`](../xxd/README.md) |
| `-i` | the file as a C array | [below](#the-file-as-a-c-array) |
| `-r` | a dump back to bytes — reading its own and `hexdump -C`'s, and [not `xxd`'s](#plain-and-the-way-back) | [`xxd -r`](../xxd/README.md) |

### Characters and bits

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -c s.txt
00000000:    c   a   f 303 251   :       1 342 202 254  
                
0000000c

$ hexdump -c s.txt
0000000   c   a   f 303 251   :       1 342 202 254  \n                
000000c

$ fasthex -b s.txt
00000000:  01100011 01100001 01100110 11000011 10101001 00111010 00100000 00110001
00000008:  11100010 10000010 10101100 00001010                                    
0000000c

$ fasthex -b -W 4 s.txt
00000000:  01100011 01100001 01100110 11000011 10101001 00111010 00100000 00110001
00000008:  11100010 10000010 10101100 00001010                                    
0000000c
```

`-c` is `hexdump -c`'s view with one change that costs the row: the newline byte `0a` is drawn as a newline. `hexdump` writes `\n` in the cell; `fasthex` writes the byte, so the row breaks where the file's line does and the rest of the cells arrive on the next line. A tab does the same. `-b` is eight ones and zeros per byte, eight bytes per row, and the second run shows that `-W` does not reach it: `-b -W 4` prints the same eight per row.

### Plain, and the way back

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -p s.txt
636166c3a93a2031e282ac0a

$ fasthex s.txt | fasthex -r | cmp - s.txt && echo identical
identical

$ fasthex s.txt | sed 's/caf..: 1/OVERWRITTEN/' | fasthex -r | cat
café: 1€

$ fasthex s.txt | sed 's/: 63 61/: 43 61/' | fasthex -r | cat
Café: 1€

$ fasthex -w runs.bin | fasthex -r | cmp - runs.bin && echo identical
identical
```

`-p` is `xxd -p`, character for character. `-r` reads a dump and writes the bytes, and on its own output it is exact: the file comes back identical, the text panel can be overwritten with anything and changes nothing, a digit changed in the hex column lands, and a dump squeezed with `-w` expands its `*` back to the right number of rows. Those are the four properties [the `xxd` page](../xxd/README.md) demonstrates for `xxd -r`, and `fasthex -r` has all four on its own dumps.

It is what it reads *beyond* its own dumps that needs measuring:

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. runs.bin is 80 bytes of A, five rows; section 5 of the baseline puts the same deleted row through xxd -r."
$ hexdump -C s.txt | fasthex -r | xxd -p
636166c3a93a2031e282ac0a

$ hexdump -C runs.bin | fasthex -r | wc -c | tr -d ' '
20

$ xxd s.txt | fasthex -r | xxd -p
636166c3a93a2031e282ac0aca

$ fasthex runs.bin | sed '2d' | fasthex -r | wc -c | tr -d ' '
64

$ printf '636166650a' | fasthex -r | xxd -p
636166650a

$ printf '63 61 66 65 0a\n' | fasthex -r | xxd -p
6166650a

$ printf '636166650a' | fasthex -r -p | xxd -p
33363333333633313336333633363335333036310a
```

Line by line. **A `hexdump -C` dump comes back exactly** — until it has a `*` in it, when the star is not expanded and the final offset line is read as four bytes of data: 20 bytes for an 80-byte file. **An `xxd` dump comes back one byte long.** `xxd` writes its text column with no pipes around it, and `fasthex -r` reads on past the hex into `caf..: 1....`, takes `ca` for a byte, and stops at the `f`. **Deleting a row shortens the file**, from 80 bytes to 64: `fasthex -r` reads the hex column and ignores the offsets, where `xxd -r` seeks to each one and leaves a hole of NULs — [the baseline](#the-baseline-what-you-already-have-prints) has `xxd`'s 80. So a `fasthex` offset is a label and an `xxd` offset is an instruction, which is the safer reading and the less capable one. **A single unbroken hex string comes back**, so `-p` output does; **a line of separate pairs loses its first pair**, which is read as the offset. And **`-r -p` is not the reverse of `-p`**: it copies its input through unchanged, so what came out is the hex of the text `636166650a` — ten bytes for the five it should have been.

| `fasthex -r` reads | and does not read |
|---|---|
| its own default, `-x`, `-X`, `-u`, any `-T`, and `-w` dumps | its `-o`, `-d`, `-b`, `-B` and `--minimal` output |
| `hexdump -C` without a `*` | `hexdump -C` with one, or an `xxd` dump — each gains bytes |
| one unbroken hex string per line | pairs separated by spaces, which lose the first pair; `-r -p`, which reverses nothing |

### The file as a C array

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. Through cat -vet, so the line ends show."
$ fasthex -i s.txt | cat -vet
unsigned char s[] = {$
  0x63, 0x61, 0x66, 0xc3, 0xa9, 0x3a, 0x20, 0x31, 0xe2, 0x82, 0xac, 0x0a, $
$
};$
unsigned int s_len = 12;$

$ fasthex -i < s.txt
unsigned char data[] = {
  0x63, 0x61, 0x66, 0xc3, 0xa9, 0x3a, 0x20, 0x31, 0xe2, 0x82, 0xac, 0x0a
};
unsigned int data_len = 12;
```

`xxd -i` names the array after the file with every non-identifier character replaced — `s_txt` — and `fasthex -i` drops the last extension first, so this is `s[]` and `s_len`; from standard input it is `data`. The two runs differ in one more thing: from a file the array ends with a comma and an empty line, from a pipe it does not. Both compile.

## Layout

```text title="fasthex -h, continued — verbatim."
LAYOUT
  -W, --width <N>             bytes per row (default: 16)
  -g, --group <N>             bytes per group: 1, 2, 4, 8
  -E, --endian <MODE>         big | little  (default: big)
  -B, --border <STYLE>        none | ascii | unicode  (default: none)
  -A, --no-ascii              hide the ASCII panel
  -P, --no-position           hide the offset/position column
      --minimal               compact rows: offset + hex + ascii, no separators
```

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -W 8 s.txt
00000000: 63 61 66 c3  a9 3a 20 31 |caf..: 1|
00000008: e2 82 ac 0a              |....    |
0000000c

$ fasthex -g 2 s.txt
00000000: 63 61  66 c3  a9 3a  20 31  e2 82  ac 0a                |caf..: 1....|
0000000c

$ fasthex -g 4 s.txt
00000000: 63 61 66 c3  a9 3a 20 31  e2 82 ac 0a               |caf..: 1....|
0000000c

$ fasthex -g 3 s.txt; echo exit=$?
fasthex: -g must be 1, 2, 4, or 8
exit=1

$ fasthex -B unicode s.txt
┌─────────────────┬─────────────────────────────────────────────────┬─────────────────┐
│     offset      │                       hex                       │      ascii      │
├─────────────────┼─────────────────────────────────────────────────┼─────────────────┤
│00000000:        │63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             │caf..: 1....     │
└─────────────────┴─────────────────────────────────────────────────┴─────────────────┘

$ fasthex -A s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a            
0000000c

$ fasthex -P s.txt
63 61 66 c3 a9 3a 20 31  e2 82 ac 0a              |caf..: 1....|

$ fasthex --minimal s.txt
00000000 636166c3a93a2031e282ac0a caf..: 1....
0000000c
```

| On the screen | What it means | Read more |
|---|---|---|
| `-W, --width` | bytes per row; the wider gap moves to the half-row, so `-W 8` splits at four | [Grouping is a choice](../../01_Bits_and_Bytes/grouping_is_a_choice/README.md) |
| `-g, --group` | the gap every 2, 4 or 8 bytes instead; 3 is refused with a sentence and exit 1, and that page says why a group is a power of two | same |
| `-E, --endian` | the order two-byte cells are read in; big is the file's | [above](#the-default-and-the-rule) |
| `-B, --border` | a box with a header row — `offset`, `hex`, `ascii` — in `+-\|` or box-drawing characters; `hexyl`'s look | [`hexyl`](../worth_installing/README.md) |
| `-A`, `-P` | drop the text panel, drop the offsets; both together is the hex column alone | |
| `--minimal` | offset, one unbroken hex string, text, no pipes — the form `-r` [reads one byte too far](#plain-and-the-way-back) | |

Only the default view has a text panel, so `-A`, `-B` and the `-T` tables below act on that view and are silent on `-x`, `-o`, `-d` and `-b`.

## Offset and navigation

```text title="fasthex -h, continued — verbatim."
OFFSET & NAVIGATION
  -s, --skip <N>              skip first N bytes (negative = from end)
  -n, --length <N>            read only N bytes
  -j, --jump <N>              bias added to every displayed offset
  -u, --uppercase             uppercase hex digits (A-F)
      --offset-dec            show offsets in decimal
```

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -s 2 -n 4 s.txt
00000002: 66 c3 a9 3a                                      |f..:            |
00000006

$ fasthex -s -4 s.txt
00000008: e2 82 ac 0a                                      |....            |
0000000c

$ fasthex -j 0x100 s.txt
00000100: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf..: 1....    |
0000010c

$ fasthex -u s.txt
00000000: 63 61 66 C3 A9 3A 20 31  E2 82 AC 0A             |caf..: 1....    |
0000000C

$ fasthex --offset-dec s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf..: 1....    |
00000012
```

`-s` and `-n` are `xxd -s` and `xxd -l`: the offset column keeps counting from the front of the file, so what it prints is an address in the file and not in the window, and the last line is where the window ended. `-s -4` counts from the end, which `xxd -s -4` does too, and needs a file it can seek in — the next block has what a pipe gets. `-j` adds a bias to every offset printed, the last line included, for a dump of a piece that lives at `0x100` in something larger; `-u` uppercases the hex digits, offsets included; `--offset-dec` prints the offsets in eight decimal digits, and the last line reads `00000012` for twelve bytes. **The suffixes are two arithmetics:**

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. big.txt is 2,100 bytes of the alphabet repeated; section 8 of the baseline lands xxd -s on the same two offsets."
$ fasthex -s 2K -n 16 big.txt
00000800: 78 79 7a 0a 61 62 63 64  65 66 67 68 69 6a 6b 6c  |xyz.abcdefghijkl|
00000810

$ fasthex -s 2kB -n 16 big.txt
000007d0: 63 64 65 66 67 68 69 6a  6b 6c 6d 6e 6f 70 71 72  |cdefghijklmnopqr|
000007e0

$ fasthex -n 1K big.txt | wc -l | tr -d ' '
65

$ fasthex -n 1kB big.txt | wc -l | tr -d ' '
64

$ cat s.txt | fasthex -s -4
fffffffffffffffc: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf..: 1....    |
00000008
```

`2K` and `2KiB` are 2,048 and land at `0x800`; `2kB` is 2,000 and lands at `0x7d0`. `-n 1K` prints 64 rows and `-n 1kB` prints 63, the half row rounded up, each plus the final line. That is [the base question](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) again — a bare `K` is binary here and decimal to `dd` — and `0x` is accepted wherever a number is. The last run is `-s -4` on a pipe: no file to measure from the end of, so the offset column prints `fffffffffffffffc`, nothing is skipped, and the final line says `00000008`.

## Colour, and the five tables

```text title="fasthex -h, continued — verbatim."
COLOR
  -L, --color <WHEN>          auto | always | never  (default: auto)
  -S, --scheme <NAME>         default | type | gradient
  -T, --table <MODE>          ascii | default | braille | cp437 | ebcdic
```

`-L auto` is the usual test of [whether standard output is a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md): through a pipe the dump is plain, and `--color always` puts the escapes back. `cat -v` shows them as `^[[32m` and friends:

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. mix.bin is one byte of each kind: 41 00 09 0a 1b 7f 20 c3 a9."
$ fasthex mix.bin | cat -v
00000000: 41 00 09 0a 1b 7f 20 c3  a9                      |A..... ..       |
00000009

$ fasthex --color always -S type mix.bin | cat -v
^[[36m00000000:^[[0m ^[[32m41^[[0m ^[[90m00^[[0m ^[[33m09^[[0m ^[[33m0a^[[0m ^[[33m1b^[[0m ^[[33m7f^[[0m ^[[36m20^[[0m ^[[31mc3^[[0m  ^[[31ma9^[[0m                      |^[[32mA^[[0m^[[90m.^[[0m^[[90m.^[[0m^[[90m.^[[0m^[[90m.^[[0m^[[90m.^[[0m^[[32m ^[[0m^[[90m.^[[0m^[[90m.^[[0m       |
^[[36m00000009^[[0m
```

Three schemes, read off `cat -v` for those nine bytes:

| byte | `default` | `type` | `gradient` |
|---|---|---|---|
| `41` `A` | 32 green | 32 green | 32 green |
| `00` NUL | 32 green | 90 grey | 90 grey |
| `09` `0a` `1b` — tab, newline, escape | 32 green | 33 yellow | 34 blue |
| `7f` DEL | 32 green | 33 yellow | 32 green |
| `20` space | 32 green | 36 cyan | 34 blue |
| `c3` `a9` — above 127 | 32 green | 31 red | 31 red, 33 yellow |

`default` paints every byte the same green and is a colour, not a classification. `type` is the one that does what [`hexyl`](../worth_installing/README.md) does — NUL, control, space, printable and high byte each in a colour of its own — and `gradient` colours by *value*, low to high, so `7f` is green beside `1b`'s blue. The text panel is painted the same way under all three, printable green and the rest grey, and the offsets cyan.

### The text column under five agreements

This is the flag that belongs to this library. `xxd` has one switch on its text column, `-E`, and [its page](../xxd/README.md) calls that the only place in any of these tools where you get to say which agreement is being applied; `fasthex -T` has five settings, here on the same nine bytes and then on `café: 1€`:

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. mix.bin: a letter, NUL, tab, newline, escape, DEL, space, and the two bytes of é."
$ fasthex -T ascii mix.bin
00000000: 41 00 09 0a 1b 7f 20 c3  a9                      |A..... ..       |
00000009

$ fasthex -T default mix.bin
00000000: 41 00 09 0a 1b 7f 20 c3  a9                      |A⋄•••• ••       |
00000009

$ fasthex -T braille mix.bin
00000000: 41 00 09 0a 1b 7f 20 c3  a9                      |⡁⠀⠉⠊⠛⡿⠠⣃⢩       |
00000009

$ fasthex -T cp437 mix.bin
00000000: 41 00 09 0a 1b 7f 20 c3  a9                      |A ○◙←⌂ ├⌐       |
00000009

$ fasthex -T ebcdic mix.bin
00000000: 41 00 09 0a 1b 7f 20 c3  a9                      |.....".Cz       |
00000009
```

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2."
$ fasthex -T ascii s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf..: 1....    |
0000000c

$ fasthex -T default s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf••: 1••••    |
0000000c

$ fasthex -T braille s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |⡣⡡⡦⣃⢩⠺⠠⠱⣢⢂⢬⠊    |
0000000c

$ fasthex -T cp437 s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |caf├⌐: 1Γé¼◙    |
0000000c

$ fasthex -T ebcdic s.txt
00000000: 63 61 66 c3 a9 3a 20 31  e2 82 ac 0a             |./.Cz...Sb..    |
0000000c
```

The hex column is identical in all ten runs, because it is the file. The panel is five readings of it:

| `-T` | The agreement | What the nine bytes became |
|---|---|---|
| `ascii` | `hexdump -C`'s rule: printable ASCII as itself, a dot for everything else | `A..... ..` — six kinds of byte, one glyph |
| `default` | `hexyl`'s idea with two glyphs: `⋄` for NUL, `•` for anything else it will not draw | `A⋄•••• ••` — NUL told apart, nothing else |
| `braille` | U+2800 plus the byte: one glyph per value, all 256 of them, NUL the blank pattern | `⡁⠀⠉⠊⠛⡿⠠⣃⢩` — nine bytes, nine different glyphs |
| `cp437` | the IBM PC's table, where the control range holds pictures — `○` for tab, `◙` for newline, `←` for escape, `⌂` for DEL — and `├⌐` for `c3 a9` | `A ○◙←⌂ ├⌐` |
| `ebcdic` | IBM's other table, the one `xxd -E` reads — `61` is `/`, `c3` is `C`, `e2` is `S` | `.....".Cz`, and `./.Cz...Sb..` for the twelve, which is `xxd -E`'s column exactly |

Two of those rows are checked by the baseline rather than taken on trust. The braille table is a formula — [the baseline](#the-baseline-what-you-already-have-prints) computes U+2800 plus each byte, as three UTF-8 bytes in a shell loop, and gets `fasthex -T braille`'s twelve glyphs — and it is the only text column on these pages that loses nothing: `ascii` draws six kinds of byte as one dot, `default` as two, and braille draws 256 values as 256 patterns, so its panel could be read back into the file. The `cp437` row for the bytes above 127 is `iconv -f CP437`'s reading — `├⌐Γé¼` for `c3 a9 e2 82 ac`, identical on both platforms, the picture a DOS screen drew of UTF-8 `é€`, and [Code pages](../../02_Characters/code_pages/README.md) has why that table holds box-drawing where ISO 8859 holds accents. `ebcdic` is `xxd -E` glyph for glyph, so [the mainframe reading](../../07_Real_Data/sap_code_pages/README.md) of a file is one flag here as it is there. What none of the five is: a UTF-8 reading. `é` is two glyphs under every table, because a text panel draws *bytes*, and [a character is a number](../../02_Characters/a_character_is_a_number/README.md) only once you say which table — which is the point of having the flag.

`-T` reaches only the default view's panel: `-c` prints its octal cells the same under `-T ebcdic`, [measured below](#where-the-screen-and-the-program-disagree).

## Filtering and flow

```text title="fasthex -h, continued — verbatim."
FILTERING & FLOW
  -w, --squeeze               replace identical rows with '*'
  -m, --max-lines <N>         stop after N output lines
  -q, --quiet                 suppress warnings
```

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. zeros.bin is 64 NUL bytes; runs.bin is 80 bytes of A."
$ fasthex zeros.bin | wc -l | tr -d ' '
5

$ fasthex -w zeros.bin
00000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000040

$ fasthex -w runs.bin
00000000: 41 41 41 41 41 41 41 41  41 41 41 41 41 41 41 41  |AAAAAAAAAAAAAAAA|
*
00000050

$ fasthex -m 2 runs.bin
00000000: 41 41 41 41 41 41 41 41  41 41 41 41 41 41 41 41  |AAAAAAAAAAAAAAAA|
00000010: 41 41 41 41 41 41 41 41  41 41 41 41 41 41 41 41  |AAAAAAAAAAAAAAAA|
00000050
```

The squeeze is off unless asked — 64 zero bytes are four rows and a length line, where a bare `hexdump -C` would already have starred them — and `-w` follows [`hexdump`'s rule, not `xxd -a`'s](../xxd/README.md): *any* repeated row collapses, so the eighty `A`s become one row and a star, which `xxd -a` leaves as five rows because none of them is NUL. Section 6 of the baseline has both. `-m 2` stops after two rows and then prints `00000050` — the file's length, not the offset it stopped at, so the last line of a truncated dump reads as if nothing were missing. `-q` was measured [above](#usage): it silences the missing-file sentence and leaves the exit status.

## Custom format

```text title="fasthex -h, continued — verbatim."
CUSTOM FORMAT
  -F, --format <FMT>          hexdump -e style format string
  -f, --format-file <FILE>    read format strings from file
```

*hexdump -e style* is the claim, and the [`hexdump` page](../hexdump/README.md) has the language: `count/size "printf format"`, conversions that consume the bytes they print, and the `_a` and `_p` extensions. Handed the same strings, `fasthex -F` does this:

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. Section 7 of the baseline runs the second, third and fourth strings through hexdump -e."
$ fasthex -F '16/1 "%02x " "\n"' s.txt
63 61 66 c3 a9 3a 20 31 e2 82 ac 0a 00 00 00 00 

$ hexdump -e '16/1 "%02x " "\n"' s.txt
63 61 66 c3 a9 3a 20 31 e2 82 ac 0a            

$ fasthex -F '8/1 "%02x " "  " 8/1 "%03u " "\n"' s.txt
63 61 66 c3 a9 3a 20 31   %03u %03u %03u %03u %03u %03u %03u %03u 

$ fasthex -F '"%08_ax: " 16/1 "%02x " "\n"' s.txt
00000000: 61 66 c3 a9 3a 20 31 e2 82 ac 0a 00 00 00 00 00 

$ fasthex -F '16/1 "%_p" "\n"' s.txt
%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p%_p

$ fasthex -F '16/1 "%_c" "\n"' s.txt
caf..: 1........
```

The first string is the one that works, and even it pads the short last row with four `00` cells that are not in the file, where `hexdump` leaves the row short. `%03u` is printed as the four characters `%03u`, eight times; so is `%_p`. `%_ax` prints an offset and then a row that starts at `61` — the conversion consumed the file's first byte, `63`, as if it were data. `%_c` works, and prints the default view's text panel. So `-F` understands the *syntax* of a hexdump format string — the count, the slash, the quoted pieces, several `-F` in sequence — and, of its conversions, `%02x`-shaped hex and `%_c`. Anything else comes out literally, with no diagnostic, and `-f` reads the same string from a file to the same effect. For a layout `hexdump` can express, run `hexdump`.

## Misc, and the size suffixes

```text title="fasthex -h, continued — verbatim."
MISC
  -h, --help                  show this help
  -v, --version               show version

SIZE SUFFIXES: KiB/K/MiB/M/GiB/G/TiB/T/PiB/P/EiB/E  kB/MB/GB/TB/PB/EB  0x…
```

Both flags are [above](#what-prints-it). The suffix line reads as one list and is two: `K`, `KiB`, `M`, `MiB` and so on are powers of 1,024, `kB`, `MB` and so on are powers of 1,000, and `0x` is hex — [measured](#offset-and-navigation), one row apart.

## How fast, and why

The README's benchmark is a 1.5 GiB file on Linux, and puts `xxd` at 55 times slower. A 256 MiB file of random bytes, on the Mac that measured everything else on this page, output to `/dev/null`:

```text title="Measured 2026-09-13 — Intel Core i5-10500 (6 cores, 12 threads), macOS 26.6.2, internal SSD, file already in the page cache. Wall-clock seconds, one run each, output to /dev/null. fasthex 0.3.27, xxd 2025-11-26, BSD hexdump, hexyl 0.17.0, BSD od."
$ head -c 268435456 /dev/urandom > big.bin

fasthex big.bin                     0.213 s
fasthex -p big.bin                  0.152 s
hexyl --color never big.bin         8.403 s
xxd big.bin                        13.901 s
od -An -tx1 -v big.bin             29.203 s
xxd -p big.bin                     29.502 s
hexdump -C big.bin                 83.884 s

cat big.bin | fasthex               0.166 s     the stdin path
fasthex big.bin | wc -c             0.421 s     1,325,400,073 bytes through a pipe
fasthex f | fasthex -r | cmp - f    6.209 s     64 MiB round trip; cmp agreed
```

Sixty-five times `xxd`, thirty-nine times `hexyl`, nearly four hundred times `hexdump -C`. And the fast path prints the same hex as the slow one:

```text title="Measured 2026-09-13 — fasthex 0.3.27 and xxd 2025-11-26, macOS 26.6.2, on the first 64 MiB of the same file."
$ fasthex -p sixty4.bin | tr -d '\n' | md5
6af5732c6c93ea3a6f25e5afecf2cf10

$ xxd -p -c 256 sixty4.bin | tr -d '\n' | md5
6af5732c6c93ea3a6f25e5afecf2cf10
```

The README says how, and none of it is a trick: the file is memory-mapped and formatted in 64 MiB chunks in parallel, 32 bytes per SIMD call under AVX2 — the `portable_simd` the install error was about — with a writer thread draining finished chunks while the next ones are formatted, and on Linux a `vmsplice` and `splice` pair that hands the kernel pages instead of copying them. A Mac has no `splice`, so here it falls back to `write`, and is still this fast. `-r` has none of that, which is the 6 seconds.

What the speed costs is the thing this chapter asks of every tool. [The three questions at the top of it](../README.md) — bytes or characters, who decided, what happens on invalid input — have one answer each here: bytes, the flag, and nothing, because a dump that never decodes cannot meet a byte it cannot decode. That is the honest column, and it is why the text panel needs five tables rather than a locale: there is no *characters* mode to fall back on.

## Where the screen and the program disagree

A help screen is prose, and nothing checks it against the program — [What the page does not say](../../13_Documentation/what_the_page_does_not_say/README.md) makes that case for man pages, and `uni -h` [bore it out five times](../uni_help/README.md). Twelve on `fasthex` 0.3.27, all measured on this page:

1. **`-c` draws a newline as a newline.** The screen calls it *one-byte character display*; a row holding `0a` breaks in two, and a tab is drawn as a tab. `hexdump -c` writes `\n` and `\t`.
2. **`-b` ignores `-W`.** Eight bytes per row, whatever width is asked for.
3. **`-r` does not seek.** Offsets are labels; a deleted row shortens the file where `xxd -r` leaves a hole.
4. **`-r` reads an unfenced text column as hex.** An `xxd` dump comes back a byte long — `ca` — and so does `--minimal` output.
5. **`-r` on a `hexdump -C` dump with a `*`** neither expands the star nor skips the final offset, which becomes four bytes of data.
6. **`-r -p` reverses nothing.** It copies its input through, so the *hex of the hex* comes out.
7. **A line of space-separated pairs loses its first pair** to the offset column; one unbroken string does not.
8. **`-F` is hexdump's syntax without most of hexdump's conversions.** `%03u`, `%_p` and the rest print themselves; `%_ax` consumes a byte; a short last row is padded with `00`.
9. **`-i` from a file ends with a comma and an empty line**; from a pipe it does not.
10. **`-s -N` needs a file.** On a pipe the offset column prints `fffffffffffffffc` and nothing is skipped.
11. **`-m N`'s last line is the file's length**, not where the dump stopped.
12. **`-j` in `-r` mode**, which the usage line offers, changed nothing: `-r -j 4` and `-r` alone wrote the same eight bytes for a dump that starts at offset 4. And a missing file among several is reported through a second code path — Rust's `Error: Custom { … }` — where a lone missing file gets a sentence.

```text title="Measured 2026-09-13 — fasthex 0.3.27, macOS 26.6.2. The -T note from the tables section, and item 12."
$ fasthex -T ebcdic -c s.txt | head -1
00000000:    c   a   f 303 251   :       1 342 202 254  

$ fasthex -r -j 4 <(fasthex -s 4 s.txt) | xxd -p
a93a2031e282ac0a

$ fasthex -r <(fasthex -s 4 s.txt) | xxd -p
a93a2031e282ac0a
```

None of the twelve touches the hex column of the default view, which is the column that is the file: `fasthex f | fasthex -r` is exact, and the fast path matches `xxd` byte for byte. They are the edges of the tool, and a help screen is where edges go unmentioned.

## The baseline: what you already have prints

Every fasthex fence above is read against one of these sections, and this block is the one CI runs — on both platforms, and the two runs agreed byte for byte on 2026-09-13.

<!-- output:fasthex_baseline_sh -->
*Verified output of [`fasthex_baseline_sh.sh`](examples/fasthex_baseline_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE FILES

$ xxd -p s.txt
636166c3a93a2031e282ac0a

$ xxd -p mix.bin
4100090a1b7f20c3a9
   mix.bin is one byte of each kind: a letter, NUL, a tab, a newline, an
   escape, DEL, a space, and the two bytes of é.

2. THE TWO DUMPS FASTHEX'S DEFAULT IS ASSEMBLED FROM

$ xxd s.txt
00000000: 6361 66c3 a93a 2031 e282 ac0a            caf..: 1....

$ hexdump -C s.txt
00000000  63 61 66 c3 a9 3a 20 31  e2 82 ac 0a              |caf..: 1....|
0000000c
   xxd writes the offset with a colon and pairs the bytes; hexdump -C
   writes one cell per byte, a gap after the eighth, and the text in
   pipes. fasthex's default row is xxd's offset in front of hexdump -C's
   cells and panel — its panel padded to sixteen where hexdump's is not.

3. TWO BYTES AT A TIME, IN TWO ORDERS

$ hexdump -x s.txt
0000000    6163    c366    3aa9    3120    82e2    0aac                
000000c

$ hexdump -d s.txt
0000000   24931   50022   15017   12576   33506   02732                
000000c
   Both presets read the file two bytes at a time as a NUMBER, in the
   CPU's order: 63 61 becomes 0x6163, which is 24931. fasthex -X and -D
   read the same pairs in FILE order unless told -E little — 0x6361,
   which is 25441 — so the flag that makes fasthex agree with hexdump is
   the one that makes it swap. hexdump -x has no flag to do the reverse.

4. THE TEXT COLUMN, UNDER OTHER AGREEMENTS

$ xxd -E s.txt
00000000: 6361 66c3 a93a 2031 e282 ac0a            ./.Cz...Sb..
   The same twelve bytes read as EBCDIC — the column fasthex -T ebcdic
   prints. Its braille table is one glyph per byte value, U+2800 plus the
   byte, which is a rule a shell loop can apply without the tool (the
   braille function at the top of this script):

$ braille s.txt
⡣⡡⡦⣃⢩⠺⠠⠱⣢⢂⢬⠊
   and its cp437 table is the IBM PC's, which iconv knows by name, here
   for the bytes above 127:

$ printf '\303\251\342\202\254' | iconv -f CP437 -t UTF-8; echo
├⌐Γé¼

5. WHAT xxd -r DOES WITH A LINE THAT IS MISSING

$ xxd runs.bin | sed '2d' | xxd -r | wc -c | tr -d ' '
80
   80 bytes from a dump with a row deleted: xxd -r seeks to each offset,
   so the gap is a hole of NULs and the length is unchanged. fasthex -r
   reads the hex and ignores the offsets, and the same dump comes back
   16 bytes shorter — the page has the run.

6. WHICH ROWS A STAR STANDS FOR

$ hexdump -C runs.bin
00000000  41 41 41 41 41 41 41 41  41 41 41 41 41 41 41 41  |AAAAAAAAAAAAAAAA|
*
00000050

$ xxd -a runs.bin | wc -l | tr -d ' '
5
   hexdump collapses ANY repeated row into a star; xxd -a collapses only
   rows of NUL, so five rows of 'A' stay five rows. fasthex -w follows
   hexdump's rule, and is off unless asked.

7. THE FORMAT STRINGS hexdump RUNS, FOR COMPARISON WITH -F

$ hexdump -e '16/1 "%02x " "\n"' s.txt
63 61 66 c3 a9 3a 20 31 e2 82 ac 0a            

$ hexdump -e '8/1 "%02x " "  " 8/1 "%03u " "\n"' s.txt
63 61 66 c3 a9 3a 20 31  226 130 172 010                

$ hexdump -e '"%08_ax: " 16/1 "%02x " "\n"' s.txt
00000000: 63 61 66 c3 a9 3a 20 31 e2 82 ac 0a            
   A short last row is left short; %03u prints decimal — of the NEXT
   eight bytes, since conversions in one string consume what they print;
   and %_ax prints the offset without consuming a byte. Each of those is
   a place where fasthex -F, handed the same string, prints something else.

8. THE SIZE SUFFIXES ARE TWO DIFFERENT ARITHMETICS

$ printf '%x %x\n' 2048 2000
800 7d0

$ xxd -s 2048 -l 16 big.txt
00000800: 7879 7a0a 6162 6364 6566 6768 696a 6b6c  xyz.abcdefghijkl

$ xxd -s 2000 -l 16 big.txt
000007d0: 6364 6566 6768 696a 6b6c 6d6e 6f70 7172  cdefghijklmnopqr
   K and KiB are 1024; kB is 1000. fasthex -s 2K lands at 0x800 and
   -s 2kB at 0x7d0, which is the second row here.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** `-p` is `data.hex()`; `-X` is `int.from_bytes(data[i:i+2], 'big')` for each pair, and `-X -E little` is the same call with `'little'`. The two table rules the baseline checks in the shell are one line each here — `chr(0x2800 + b)` for braille, `data.decode('cp437')` for the PC table — though Python's `cp437` maps the control range to control characters rather than to `○◙←⌂`, so it agrees with `-T cp437` only above 127. `-r`'s comfort with one unbroken string and its trouble with anything else is `bytes.fromhex()`'s temperament too: it takes `'636166650a'`, tolerates spaces, and raises on a `*` or an offset. Nothing in Python is the fast path — that is SIMD over a memory map — but `mmap` and `memoryview` are how you read a file without copying it, which is the half of the trick that transfers.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* `-T ebcdic` is the column that will matter: the bytes of a file that arrived from a mainframe interface, read under the agreement the sender used, which in `cl_abap_conv_codepage` terms is a code page such as `CP037` or `CP500` named in the interface specification and verified against the system, never inferred from which conversion produced fewer question marks. `-X` and `-E` are the byte-order question you meet when an `xstring` holds a two-byte integer written by another host: `-X` shows a big-endian field as it reads, `-X -E little` shows one written by an x86 machine, and the bytes on disk are the same either way.

## Try it

1. `fasthex -X -E little f | head -3` beside `hexdump -x f | head -3`, on any file of yours: the numbers agree. Drop `-E little` and read the file's own order — then decide which of the two you wanted.
2. Time the biggest file on your disk: `time fasthex f > /dev/null`, then `time xxd f > /dev/null`. Then check the fast one against the slow one — `fasthex -p f | tr -d '\n' | md5` against `xxd -p -c 256 f | tr -d '\n' | md5`. On Linux, `md5sum`.
3. `fasthex -T braille f | head` on a file with NULs, tabs and a non-ASCII word in it: every byte is a different glyph. Then `-T default` on the same rows, and count how many became `•`.
4. `fasthex f | fasthex -r | cmp - f`. Then delete one row from the dump and reverse it, and `wc -c` the result; then do the same with `xxd f | sed '2d' | xxd -r`, and compare the two lengths with the file's.
5. `fasthex -F '16/1 "%02x " "\n"' f | tail -1` — count the `00` cells the file does not have. Then the same string through `hexdump -e`, and look at what it does with a short row.

## See also

- [`hexdump` is a format engine wearing six presets](../hexdump/README.md) — the default that swaps pairs, and the `-e` language `-F` borrows the syntax of
- [`xxd` is the dump you can put back](../xxd/README.md) — the reverse that seeks, the text column it ignores, and `-E`
- [`od` reads types, not bytes](../od/README.md) — the one that is there when nothing is installed
- [The five worth installing](../worth_installing/README.md) — `hexyl`, whose categories `-S type` and `-T default` reproduce
- [`uni -h`, line by line](../uni_help/README.md) — the same treatment of the other help screen with no man page
- [Which end comes first](../../01_Bits_and_Bytes/which_end_comes_first/README.md) — what `-E` decides
- [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) — `2K` against `2kB`
- [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) — the three columns, if this page assumed one you have not met
- [A character is a number](../../02_Characters/a_character_is_a_number/README.md) and [Code pages](../../02_Characters/code_pages/README.md) — the chapter the five tables belong to
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — the dump tools inside a workflow
- [fasthex on GitHub ↗](https://github.com/CallMeAlphabet/fasthex) — the README with the mechanism and the Linux benchmark
