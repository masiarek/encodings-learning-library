# `tty(4)` and `stty(1)`: the text processor between the keyboard and your program

**Level:** reference · for anyone who has wondered where `\r\n` comes from when they only typed Enter

**One line:** The terminal line discipline assembles a line before your program sees it, turns the Enter key's CR into LF on the way in and every LF into CR LF on the way out, draws `^C` for a control byte, and erases one *byte* per Backspace unless told the input is UTF-8; `stty -a` on this Mac prints 113 words of settings including `-iutf8`, a flag its 1992 `tty(4)` page has never heard of.

**The pages:** [`tty(4)`](raw/macos/tty.4.txt) (footer *BSD 4*, dated August 14, 1992) · [`stty(1)`](raw/macos/stty.1.txt) (macOS 26.6.2, dated October 20, 2018). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machine is in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt). GNU `stty` (coreutils 9.4) and util-linux `script` on ubuntu:24.04 were measured beside them.

## What the pages are for

`tty(4)` is in section 4, devices, because a terminal is one: `/dev/tty03` was a serial port with a teletype on the end, and `/dev/ttys000` today is a *pty*, the same interface with a program on the other side instead of a machine. The page is the `ioctl(2)` view of that device, twenty-odd requests for setting the line discipline, reading the window size and simulating typed input, and it dates itself in its first paragraph by naming `rlogin`, `telnet` and `tip`. It says nothing about what a character is, because in 1992 a character was a byte and the page is about signals, process groups and modem lines.

`stty(1)` is the same device from the shell: every flag on it is a bit in one of the four `termios` words the kernel keeps per terminal, `c_cflag` for the wire, `c_iflag` for input processing, `c_oflag` for output processing, `c_lflag` for the line discipline's own behaviour, plus the table of *control characters* that end a line, erase a character or send a signal. Read together, the two pages describe a text processor that sits between the bytes you type and the bytes `read(2)` returns, and another between `write(2)` and the screen. That processor is why [a pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md): a program writing to a pipe gets its bytes delivered as written, and a program writing to a terminal gets `0d` inserted before every `0a`.

The encoding story is one flag. Canonical mode lets you correct a line before sending it, and to erase a character the driver has to know how many bytes one is. `iutf8` is that knowledge, on `stty(1)` in a single line and absent from `tty(4)`, and the measurement below shows what Backspace does to `café` with and without it.

## The pages, with notes

### `tty(4)`: the line discipline, and the window

```text title="man 4 tty, macOS 26.6.2, dumped 2026-09-13"
     When an interactive user logs in, the system prepares the line to behave
     in a certain way (called a line discipline), the particular details of
     which is described in stty(1) at the command level, and in termios(4) at
     the programming level.
     ...
     The line discipline essentially
     glues the low level device driver code with the high level generic
     interface routines (such as read(2) and write(2) ), and is responsible
     for implementing the semantics associated with the device.
```

The *line discipline* is the module that owns the semantics: when `read(2)` returns, what has been removed from the bytes on the way, what has been added on the way out. The page defers the details to `stty(1)` and `termios(4)`, and lists the four disciplines a 1992 kernel could switch between with `TIOCSETD`: terminal, tablet, SLIP and PPP, the last two being the IP-over-serial-line protocols that made the same device a network interface.

```text title="man 4 tty, macOS 26.6.2, dumped 2026-09-13"
     TIOCGWINSZ struct winsize *ws
                 Put the window size information associated with the terminal
                 in the winsize structure pointed to by ws.  The window size
                 structure contains the number of rows and columns (and pixels
                 if appropriate) of the devices attached to the terminal.  It
                 is set by user software and is the means by which most
                 full-screen oriented programs determine the screen size.
```

The window size is a number *stored in the terminal device*, put there by the terminal emulator and read back by `stty size`, `tput cols` and every program that wraps text to the screen. It is a count of columns, and a column is the unit [`wcwidth(3)`](wcwidth.md) measures in; a fresh pty has `0 0` until somebody sets it, which is what the experiment below does with `TIOCSWINSZ`.

| On the page | What it means | Read more |
|---|---|---|
| `TIOCSTI char *cp` *Simulate typed input* | push one byte into the input queue as if typed; the one request that writes *upstream* | |
| `TIOCGETA`, `TIOCSETA` | get and set the `termios` structure; what `tcgetattr` and `stty` call | |
| `TIOCFLUSH`, `TIOCDRAIN` | throw away or wait for queued bytes | [`stdio(3)`](stdio.md) |
| `TIOCSCTTY`, `TIOCNOTTY` | acquire or drop the *controlling terminal*, the one `^C` reaches | |
| `TIOCM_DTR`, `TIOCM_CTS` ... | modem control lines; `cs7`, `parenb` and `clocal` on `stty` are the same wire | |

### `stty(1)`: the four flag words

```text title="man 1 stty, macOS 26.6.2, dumped 2026-09-13"
     cs5 cs6 cs7 cs8
                 Select character size, if possible.
     ...
     istrip (-istrip)
                 Strip (do not strip) input characters to seven bits.

     iutf8 (-iutf8)
                 Assume input characters are UTF-8 encoded.
```

Three settings, three ideas of what a character is. `cs7` and `cs8` are the width of a character *on the wire*, seven or eight data bits per frame, from the era when `parenb` used the eighth as a checksum. `istrip` clears the high bit of every byte received, which turns `c3 a9` into `43 29` and `café` into `cafC)`, the same arithmetic as [Binary And `7F`](../../15_Hex/binary_and/README.md) and the reason [UTF-7](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) exists. `iutf8` is the only line on either page that names an encoding: it tells the erase logic that a character may be several bytes.

```text title="man 1 stty, macOS 26.6.2, dumped 2026-09-13"
     icrnl (-icrnl)
                 Map (do not map) CR to NL on input.
     ...
     inlcr (-inlcr)
                 Map (do not map) NL to CR on input.
     ...
     onlcr (-onlcr)
                 Map (do not map) NL to CR-NL on output.
     ...
     opost (-opost)
                 Post-process output (do not post-process output; ignore all
                 other output modes).
```

This is where `\r\n` comes from. The Enter key sends CR (`0d`), because a teletype's carriage return was a key; `icrnl` turns it into the LF (`0a`) that Unix calls a line end, so the program reads `a\n` when you typed `a` and Enter. Going out, a bare LF would move the paper down without returning the carriage, so `onlcr` inserts a CR before every LF, and the terminal receives `a\r\n`. Both mappings are on by default, both are gone on a pipe, and `-opost` switches off every output mapping at once. [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) is what happens when the `0d` is written to a file instead.

```text title="man 1 stty, macOS 26.6.2, dumped 2026-09-13"
     echoctl (-echoctl)
                 If echoctl is set, echo control characters as ^X.  Otherwise,
                 control characters echo as themselves.
     ...
     icanon (-icanon)
                 Enable (disable) canonical input (ERASE and KILL processing).
```

`echoctl` is why `^C` appears on the screen: the byte `03` is echoed as the two printable bytes `5e 43`, the same notation `cat -v` uses ([`cat(1)`](lines_and_fields.md)) and the same [control character](../../02_Characters/control_characters/README.md) either way. `icanon` is the switch for the whole text processor: with it set, `read(2)` returns whole lines and ERASE, KILL, WERASE and LNEXT are interpreted; without it, every byte goes straight through, subject to `min` and `time`.

```text title="man 1 stty, macOS 26.6.2, dumped 2026-09-13"
                       eof          VEOF         EOF character
                       eol          VEOL         EOL character
                       erase        VERASE       ERASE character
                       werase       VWERASE      WERASE character
                       intr         VINTR        INTR character
                       kill         VKILL        KILL character
                       lnext        VLNEXT       LNEXT character
```

The control characters are *settings*, not bytes with a fixed meaning: `eof` is `^D` because `stty -a` says so, and `stty eof ^E` would make it `^E`. What `eof` does is make the driver return the line typed so far without waiting for a newline, so `ab^D` gives the program `ab` and `^D` on an empty line gives it zero bytes, which is what end of file *is*: no character called EOF ever reaches the program. `lnext` (`^V`) quotes the next byte, which is how you type a control character literally: [Typing a character you cannot type](../../11_Tools/typing_a_character/README.md).

```text title="man 1 stty, macOS 26.6.2, dumped 2026-09-13"
     raw (-raw)  If set, change the modes of the terminal so that no input or
                 output processing is performed.  If unset, change the modes
                 of the terminal to some reasonable state that performs input
                 and output processing.  Note that since the terminal driver
                 no longer has a single RAW bit, it is not possible to intuit
                 what flags were set prior to setting raw.
```

`raw` is not a flag but a bundle: `-icanon -isig -opost -icrnl ...` and more, which is why the page recommends `stty -g` to save the state first. `sane` is the bundle in the other direction, and `cooked` is its old name. In raw mode the experiment below shows every byte arriving unchanged in both directions, `0d`, `7f` and `04` included.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| line discipline | the kernel module that turns typed bytes into lines and lines into screen output; `termios` is the default one | |
| canonical mode, `icanon` | line-at-a-time input with editing; the opposite is *non-canonical* or raw | |
| `termios`, `c_iflag`, `c_oflag`, `c_cflag`, `c_lflag` | the POSIX terminal structure and its four flag words: input, output, control (wire), local | |
| pty | a pseudo-terminal: the same interface with a program (a terminal emulator, `script`, `ssh`) on the far side | [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) |
| control character (stty sense) | one of the settable bytes `eof`, `erase`, `intr` ...; `^-` or `undef` disables one | [Control characters](../../02_Characters/control_characters/README.md) |
| `VEOF`, `VERASE`, `VLNEXT` ... | the indices into `c_cc[]`, the C names for the same table | |
| `_POSIX_VDISABLE` | the value that means *no character does this* | |
| `MIN`, `TIME` | in non-canonical mode, how many bytes or how long `read(2)` waits | |
| CR, NL | `0d` and `0a`; the page says NL where the rest of the library says LF | [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) |
| `cs7`, `cs8`, `parenb`, `parodd` | data bits per character on the wire, and the parity bit | [UTF-7, and the seven-bit transport](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) |
| `istrip` | clear bit 7 of every byte received; a seven-bit channel by software | [Binary And](../../15_Hex/binary_and/README.md) |
| `iutf8` | *maintain state for UTF-8 VERASE*, as this Mac's `termios.h` puts it: erase whole characters | [`utf8(5)` and `utf-8(7)`](utf8.md) |
| `ixon`, `ixoff`, START, STOP | flow control by `^S` and `^Q`, the reason a terminal sometimes freezes | |
| `winsize`, `TIOCGWINSZ`, `stty size` | rows and columns, stored in the device and set by the emulator | [`wcwidth(3)`](wcwidth.md) |
| `status`, `^T`, `SIGINFO` | the BSD status character; `dd` and `wc` print progress on it | [`dd(1)`](dd.md) |
| `-g` | the settings as one string `stty` can read back | |

## Try it on your machine

**`stty -a` without a terminal.** The Bash session this was measured from has no tty, so `stty -a` fails; `script(1)` lends it one. The three flag lines from each machine, in the fresh pty `script` creates:

```text title="Measured 2026-09-13 — macOS 26.6.2 via script -q /dev/null stty -a, and ubuntu:24.04 (coreutils 9.4) via script -qc 'stty -a' /dev/null. Not machine-checked."
macOS
iflags: -istrip icrnl -inlcr -igncr ixon -ixoff ixany imaxbel -iutf8
	-ignbrk brkint -inpck -ignpar -parmrk
oflags: opost onlcr -oxtabs -onocr -onlret
cflags: cread cs8 -parenb -parodd hupcl -clocal -cstopb -crtscts -dsrflow
	-dtrflow -mdmbuf
cchars: discard = ^O; dsusp = ^Y; eof = ^D; eol = <undef>;
	eol2 = <undef>; erase = ^?; intr = ^C; kill = ^U; lnext = ^V;
Ubuntu
-ignbrk -brkint -ignpar -parmrk -inpck -istrip -inlcr -igncr icrnl ixon -ixoff
-iuclc -ixany -imaxbel -iutf8
opost -olcuc -ocrnl onlcr -onocr -onlret -ofill -ofdel nl0 cr0 tab0 bs0 vt0 ff0
-parenb -parodd -cmspar cs8 -hupcl -cstopb cread -clocal -crtscts

$ stty -a | tr ' \t' '\n\n' | grep -c .        113 on macOS, 114 on Ubuntu
$ stty -a | tr ' ' '\n' | grep -n iutf8         -iutf8 on both
$ stty -a < /dev/null                           stty: stdin isn't a terminal (macOS); Inappropriate ioctl for device (Ubuntu)
```

Both machines start a pty with `icrnl`, `onlcr`, `opost`, `cs8`, `-istrip` and `-iutf8`. The Ubuntu list has `iuclc` and `olcuc`, the Linux-only flags that fold the case of *every* byte, and the delay-style settings `nl0 cr0 tab0` that this Mac's page lists under LEGACY DESCRIPTION.

**`ONLCR` through `script`.** The same `printf`, once into a pipe and once into a pty.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
$ printf 'a\n' | xxd -p
610a                                    both: a pipe carries what was written
$ script -q /dev/null printf 'a\n' < /dev/null | xxd -p                 macOS
5e440808610d0a                          ^D BS BS a CR LF
$ script -qc "printf 'a\n'" /dev/null < /dev/null | xxd -p              Ubuntu
610d0a                                  a CR LF
```

The `0d` before the `0a` is `onlcr`, on both. The Mac's extra `5e 44 08 08` is `script`'s own doing: its standard input was `/dev/null`, so it fed an end-of-file to the pty as the `eof` character, the driver echoed that as `^D` (`echoctl`), and then erased the echo with two backspaces (`echoe`). Nothing was typed, and four bytes of terminal conversation happened anyway.

**The processor, both directions, on a pty from Python.** `os.write` to the slave side is a program printing; `os.write` to the master side is a person typing; the flags are toggled with `termios` between steps.

```text title="Measured 2026-09-13 — macOS 26.6.2 (python 3.14.7) and ubuntu:24.04 (python 3.12.3); identical on both except the iutf8 row. Not machine-checked."
program writes 61 0a; terminal side receives            61 0d 0a           onlcr
  same with -onlcr                                      61 0a
typed 61 0d 62 0a; program reads                        61 0a 62 0a        icrnl: CR became LF
  ...and the terminal gets back as echo                 61 0d 0a 62 0d 0a  echo, then onlcr again
typed 03 0a with -isig; program reads                   03 0a
  echo back                                             5e 43 0d 0a        echoctl draws ^C
typed 63 61 66 c3 a9 0a with istrip; program reads      63 61 66 43 29 0a  "cafC)"
typed caf c3 a9 then DEL then LF; program reads         63 61 66 c3 0a     -iutf8: one BYTE erased; "caf" plus half an é
  same with iutf8 set                                   63 61 66 0a        the whole é erased (macOS termios.IUTF8; Linux 0x4000)
typed 61 62 04; program reads                           61 62              eof mid-line: the line is delivered, no newline, no 04
typed 04 on an empty line; program reads                (0 bytes)          which is EOF
raw mode, program writes 61 0a; terminal receives       61 0a
raw mode, typed 61 0d 62 7f 04; program reads           61 0d 62 7f 04     nothing interpreted, nothing echoed
TIOCGWINSZ on the fresh pty                             (0, 0, 0, 0)       rows, cols, xpixel, ypixel
  after TIOCSWINSZ                                      (24, 80, 0, 0)
```

The `istrip` row is `café` through a seven-bit channel, and the two erase rows are the reason `iutf8` exists: without it, Backspace after `é` removes `a9` and leaves the program a line ending in a lone `c3`, invalid UTF-8 that was never typed. On Linux Python's `termios` module has no `IUTF8` name, so the bit was set as `0x4000`, the value in `/usr/include/asm-generic/termbits.h`; on the Mac it is `termios.IUTF8`, and `sys/termios.h` comments it *maintain state for UTF-8 VERASE*. Neither pty had it on by default; whether your interactive terminal has it is a `stty -a` away, and `stty iutf8` sets it.

## Where the pages are dated, and what they do not say

**`tty(4)` is dated August 14, 1992 and footed *BSD 4*.** It names `rlogin`, `telnet` and `tip`, describes `TIOCNOTTY` as obsolete, lists SLIP and PPP as line disciplines, and has no word for an encoding: `TIOCSTI` simulates *the character pointed to by cp*, one byte, and `winsize` is in columns without saying what a column is. It is documentation of a machine, thirty-four years on, and still correct about every `ioctl` it lists.

**`stty(1)` is dated October 20, 2018 and has `iutf8` in one line**, *Assume input characters are UTF-8 encoded*, without saying what changes when you do: that ERASE and WERASE count characters instead of bytes, and that nothing else does. `tty(4)` and `termios(4)` on this Mac do not mention the flag at all.

**Neither page says what the driver does with an invalid byte**, and the experiment shows the answer is nothing: `istrip` and a byte-wise erase both hand the program bytes that are not UTF-8, in canonical mode, silently.

**Neither page says that `eof` is not a character the program receives**, and two other pages in this folder get it wrong: `wc(1)` says it reads *until receiving EOF, or [^D] in most environments*, and `cat(1)` says *until it receives an EOF (`^D') character*. The row above with zero bytes is the correction: `^D` makes the driver deliver the line; an empty delivery is EOF.

**`stty(1)` documents `-g`, `sane` and `raw` but not `iuclc` and `olcuc`**, which are Linux's and not BSD's, and its LEGACY DESCRIPTION says the `nl0 cr0 tab0` delay settings *are not accepted* in legacy mode while GNU `stty -a` prints them by default.

## See also

- [`wcwidth(3)`](wcwidth.md) — the column that `TIOCGWINSZ` counts in and `stty size` reports
- [`man(1)` and `mandoc(1)`](man.md) — the other text processor between a file and your screen, and its backspace format
- [`stdio(3)`](stdio.md) — `isatty` and line buffering, the userland side of the same boundary
- [`cat(1)`, `sort(1)`, `xargs(1)` and the line tools](lines_and_fields.md) — `cat -v`, the same `^X` notation as `echoctl`
- [A pipe is not a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) — the `isatty` question, measured across Python versions
- [Control characters](../../02_Characters/control_characters/README.md) — the first 32 codes as commands to a teletype, which is what this driver still is
- [CRLF vs LF](../../07_Real_Data/crlf_vs_lf/README.md) — the `0d` this page inserts, when it ends up in a file
- [`printf` writes bytes](../../06_Terminal/printf_writes_bytes/README.md) — the tool that made the input above, byte for byte
- [Typing a character you cannot type](../../11_Tools/typing_a_character/README.md) — `lnext`, and the other ways to get a byte past the driver
- [Terminal hyperlinks, and the URI that is not one](../../06_Terminal/terminal_hyperlinks/README.md) — escape sequences the emulator interprets after the driver has finished
- [From the telegraph to Unicode](../../09_History/from_telegraph_to_unicode/README.md) — the teletype whose carriage return this page still maps
