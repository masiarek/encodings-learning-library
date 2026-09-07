# Terminal hyperlinks, and the URI that is not one

**Level:** 201 · for anyone with a terminal

**One line:** A clickable filename in your terminal is an escape sequence wrapped around ordinary text, and the URI inside it is percent-encoded for a space and a `#` but **not** for the accent in your filename — which the OSC 8 specification that ripgrep's own manual links calls undefined behaviour.

## Why this is a chapter 6 page

Everything else in [this chapter](../README.md) is a tool whose job is bytes. A hyperlink is the opposite: bytes whose job is to be *invisible*. The terminal draws `plain.txt` and sends forty-two bytes, and the difference between those two numbers is where every question in this library lives — [what is on the wire versus what is on the screen](../inspecting_a_file/README.md), and what happens to a character on the way.

It is also the shortest real example of [escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) that you can run right now. That page is the theory of `%XX`: it escapes **bytes** and never says whose. This page is one program doing it in front of you, getting the reserved characters right and the non-ASCII ones wrong.

## The anatomy

```text title="Measured 2026-09-06 — macOS 26.6 (rg 15.1.0, brew) and ubuntu:24.04 (rg 14.1.0, apt). The two runs were diffed and are identical apart from the version line. Not machine-checked: CI has no rg."
$ rg --color=always --hyperlink-format=default -H here plain.txt | head -c 8 | xxd
  00000000: 1b5d 383b 3b66 696c                      .]8;;fil

$ rg ... | cat -v | sed 's#file://[^^]*#file://HOST/ABS/PATH#'
  ^[]8;;file://HOST/ABS/PATH^[\^[[0m^[[35mplain.txt^[[0m^[]8;;^[\:cafM-CM-) X ^[[0m^[[1m^[[31mhere^[[0m
```

`1b 5d 38 3b 3b` is `ESC ] 8 ; ;` — an **OSC**, an Operating System Command, one of the escape sequences in [the control characters](../../02_Characters/control_characters/README.md) that a terminal acts on rather than draws. The shape is:

```text
ESC ] 8 ; <params> ; <URI>  ST      the text you can see      ESC ] 8 ; ; ST
```

`ST` is the string terminator, `ESC \` — `1b 5c` — and the closing sequence has an empty URI, which is how you say *"the link stops here"*. The visible payload between them is nine characters; the whole construction is over eighty bytes. That is not a criticism, it is the design: a link has to be invisible to every program that is only reading text.

## What goes into the URI

```text title="Measured 2026-09-06 — same two machines, diffed, identical apart from the version line. `uritail` is a five-line script that pulls the URI out of rg's output and prints its last segment plus that segment's bytes."
$ ./uritail rg --color=always --hyperlink-format=default -H here 'with space.txt'
  with%20space.txt  bytes: 77 69 74 68 25 32 30 73 70 61 63 65 2e 74 78 74

$ ./uritail rg --color=always --hyperlink-format=default -H here 'café.txt'
  café.txt  bytes: 63 61 66 c3 a9 2e 74 78 74
```

Two names, two treatments. The space became `%20`; so do `#` and `?`, checked the same way (`a#b?c.txt` → `a%23b%3Fc.txt`). The `é` did **not**: `c3 a9` goes into the URI as itself.

That is worth holding against three documents.

- **ripgrep's manual**, on `{path}`: *"The path is guaranteed to be absolute and percent encoded such that it is valid to put into a URI."*
- **RFC 3986**, which defines a URI as a sequence of characters from a restricted ASCII set — `c3 a9` is not in it. What ripgrep emits for this filename is a valid **IRI** ([RFC 3987](https://www.rfc-editor.org/rfc/rfc3987 ↗)), which is a different specification.
- **The [OSC 8 specification ↗](https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda)** — the one ripgrep's own manual links at the end of the `--hyperlink-format` entry — which says: *"For portability, the parameters and the URI must not contain any bytes outside of the 32–126 range. If they do, the behavior is undefined. Bytes outside of this range in the URI must be URI-encoded."*

So the guarantee in the manual is not met for a non-ASCII filename, and the sequence lands in the part of the OSC 8 spec marked undefined.

**And it is deliberate**, which is the part worth reading before deciding it is a bug. ripgrep's `HyperlinkPath::encode` has an arm that passes every byte from `128` up through untouched, and the comment above it gives the reasoning: [RFC 8089 ↗](https://www.rfc-editor.org/rfc/rfc8089#section-4), which defines the `file:` scheme, *"does not mandate precise encoding requirements for non-ASCII characters"*, and Windows' own `UrlCreateFromPathW` does not encode them either — encoding them there would produce `file://` URLs that Windows rejects. What comes out for a UTF-8 filename is a perfectly usable IRI, and the terminals people actually run are UTF-8 and cope.

That leaves the manual's wording as the thing that is simply wrong — the code comment is precise where the user-facing text is not — and one case the reasoning does not reach, which is the next section.

## The filename the URI cannot survive

The undefined case stops being theoretical the moment a filename is not valid UTF-8 at all — which a Linux filesystem allows, because [a filename is bytes](../../11_Tools/find/README.md), and macOS does not.

```text title="Measured 2026-09-06 — macOS 26.6 and ubuntu:24.04. This block DIFFERS between the two machines, which is the point; both are shown."
macOS, APFS
  create 'bad\xff.txt'   -> refused, OSError 92
  files on disk          -> ['café.txt', 'ok.txt']          # NFC and NFD folded into one

ubuntu:24.04, overlayfs
  create 'bad\xff.txt'   -> yes
  files on disk          -> ['bad\udcff.txt', 'café.txt', 'café.txt', 'ok.txt']
  URI tail for bad\xff   -> 62 61 64 ff 2e 74 78 74
  URI tail for the NFD   -> 63 61 66 65 cc 81 2e 74 78 74
  URI tail for the NFC   -> 63 61 66 c3 a9 2e 74 78 74
```

Three things there. A lone **`ff`** — not valid UTF-8 in any position, and outside 32–126 — goes into the URI unescaped; `%FF` would have been both legal and lossless. This is the case the RFC 8089 reasoning above does not cover, because there is nothing to be lenient *about*: the byte is not part of any character, so the result is neither a URI nor an IRI, and the Windows argument cannot apply because the Windows code path already refuses a path it cannot read as UTF-8 while the Unix one takes the raw OS bytes. Reported upstream as [ripgrep#3526 ↗](https://github.com/BurntSushi/ripgrep/issues/3526). The **two `café.txt` entries are two files**, spelled `65 cc 81` and `c3 a9`, so they get two different URIs while drawing identically on screen — the [normalization](../../04_Python/normalization/README.md) question arriving in a hyperlink. And on the Mac neither problem can be demonstrated, because APFS refuses the first name outright (`Errno 92`) and folds the other two together, which is the same split [the `find` page](../../11_Tools/find/README.md) measures from the other direction.

## The column that counts bytes

The `vscode` alias expands to `vscode://file{path}:{line}:{column}`, and `{column}` is [ripgrep's column, which counts bytes](../../11_Tools/ripgrep/README.md):

```text title="Measured 2026-09-06 — same two machines, diffed, identical apart from the version line."
$ ./uritail rg --color=always --hyperlink-format=vscode --column -H here plain.txt
  plain.txt:1:9  bytes: 70 6c 61 69 6e 2e 74 78 74 3a 31 3a 39

$ python3 -c "s=open('plain.txt').read().rstrip(); print(s.index('here')+1, s.encode().index(b'here')+1)"
  character 8  byte 9
```

The line is `café X here`. The word starts at **character 8** and **byte 9**, and the URI says 9. Nothing in the URI records which unit that is, so the editor at the other end applies its own convention — and lands one position early per non-ASCII character to the left of the match, on the file it has just opened for you. The number is not wrong; it is unlabelled, which is the same defect as [a `%XX` sequence that does not name its charset](../../03_Encodings/escaping_into_ascii/README.md).

## What switches it off

Hyperlinks are **opt-in** — no format, no links — and then gated a second time by whether colour is on at all, because ripgrep treats `--color` as the proxy for *"may I emit ANSI escapes"*.

```text title="Measured 2026-09-06 — same two machines, diffed, identical apart from the version line. The tty cases run under python's `pty.spawn`, which is the same command on both platforms."
  TERM=xterm-256color    hyperlink
  + NO_COLOR=1           none
  TERM=dumb              none
  piped, no tty          none
  piped + --color=always hyperlink
```

So the honest summary is that **four separate things must all be true** before a link appears: you passed `--hyperlink-format`, stdout is a tty (or you forced `--color=always`), `TERM` is not `dumb`, and `NO_COLOR` is unset. Anyone debugging *"why is nothing clickable"* is usually missing the second or the third. Ripgrep also skips the link when the path is not in the output at all — searching a single file prints no filename unless you add `-H`.

To keep links and drop colour, the manual's own recipe works, and is the one case where you need it spelled out:

```bash
rg --hyperlink-format=default \
   --colors 'path:none' --colors 'line:none' \
   --colors 'column:none' --colors 'match:none' PATTERN
```

The aliases are worth knowing before you write a format string by hand — `default` and `file` are the same thing, and only one of them carries a column:

| alias | expands to |
|---|---|
| `default`, `file` | `file://{host}{path}` |
| `kitty` | `file://{host}{path}#{line}` |
| `vscode` | `vscode://file{path}:{line}:{column}` |

## In Python

The rules are checkable without the tool, because the interesting half is the standard rather than the implementation: which bytes OSC 8 allows, and what `urllib.parse.quote` does with the same filenames.

<!-- output:terminal_hyperlinks_py -->
*Verified output of [`terminal_hyperlinks_py.py`](examples/terminal_hyperlinks_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
RULE 1. THE LINK IS AN ESCAPE SEQUENCE WRAPPED AROUND THE TEXT
   the opener, as bytes                     1b 5d 38 3b 3b
   the terminator (ST), as bytes            1b 5c
   whole link, bytes on the wire            42
   what the terminal draws                  6
   Six characters of visible text inside forty-odd bytes of sequence, and
   ESC is a C0 control -- so every byte that makes the link clickable is
   invisible by design. Pipe the output anywhere and the difference shows
   up as length: `wc -c` counts the sequence, your eyes do not.

RULE 2. THE SPEC SAYS 32-126. THE FILENAME DOES NOT ASK PERMISSION
   ascii: bytes outside 32-126              none
   ascii: urllib quote() gives              ok.txt
   space: bytes outside 32-126              none
   space: urllib quote() gives              with%20space.txt
   NFC: bytes outside 32-126                [195, 169]
   NFC: urllib quote() gives                caf%C3%A9.txt
   The middle row is the one everyone gets right -- a space is 0x20, inside
   the range, and still reserved, so every implementation escapes it. The
   third row is the one to look at: 0xc3 0xa9 are outside the range, the
   OSC 8 spec says such bytes 'must be URI-encoded' and that the behaviour
   is undefined otherwise, and Python's quote() duly writes %C3%A9.
   Measured on the page: rg writes the raw bytes.

RULE 3. TWO SPELLINGS OF ONE NAME ARE TWO DIFFERENT URIs
   NFC quoted                               caf%C3%A9.txt
   NFD quoted                               cafe%CC%81.txt
   same string?                             False
   same after NFC normalisation?            True
   Both draw as café.txt. On Linux they are two files and two URIs; on a
   Mac the filesystem folds them together, so the second name cannot exist
   beside the first. A URI is a byte sequence and has no opinion about
   normalisation -- whatever the filesystem handed over is what gets linked.

RULE 4. A COLUMN IS A NUMBER, AND THE UNIT IS NOT WRITTEN DOWN
   the line                                 'café X here'
   'here' at character (1-based)            8
   'here' at byte (1-based)                 9
   difference                               1
   Eight and nine. rg's --column counts bytes and says so in its own docs,
   and the vscode hyperlink alias puts that number into the URI as
   {column}. Nothing in the URI records which unit it is, so an editor that
   counts characters lands one position early -- once per non-ASCII
   character to the left of the match, silently, on the line it just
   opened for you.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** `urllib.parse.quote` is the correct behaviour on this page's third row — it escapes every byte outside its `safe` set, so `café.txt` becomes `caf%C3%A9.txt`, and `unquote` gives the bytes back. Two traps carry straight over: `quote` defaults to `safe='/'`, which is right for a path and wrong for a query value; and `quote` takes a `str` and encodes it as UTF-8 first, so a name that came off a Linux filesystem as undecodable bytes needs `quote(os.fsencode(name))` rather than the string form, or you get a `UnicodeEncodeError` on the surrogate.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* `cl_http_utility=>escape_url` is the same job, and the same question applies to it that applies to `rg`: which bytes does it consider safe, and does it encode the string as UTF-8 before escaping or in the system code page? That answer decides whether a URL built in ABAP is the same URL built anywhere else. Check it against your own system rather than against this page.

## Try it

1. `rg --hyperlink-format=default PATTERN | cat -v` in a real terminal, and then the same command without `| cat -v`. The first shows you the sequence; the second shows you six clickable characters. Same bytes.
2. Make a file with an accent in its name and hyperlink it. Compare `./uritail`'s bytes against `python3 -c "import urllib.parse;print(urllib.parse.quote('café.txt'))"`.
3. `NO_COLOR=1 rg --hyperlink-format=default PATTERN` in that terminal. Nothing is clickable, and no message says why.
4. On Linux only: `touch $'bad\xff.txt'`, then hyperlink it and dump the URI's bytes. On a Mac, watch the `touch` fail instead — that failure is the feature.

## See also

- [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) — the theory of `%XX`, and the three other schemes that escape something else
- [Control characters](../../02_Characters/control_characters/README.md) — what `ESC` is, and why a terminal acts on it instead of drawing it
- [`ripgrep` — the Rust grep](../../11_Tools/ripgrep/README.md) — where `--column` counts bytes, and the rest of the flags that are encoding decisions
- [`find`, and filenames that are bytes](../../11_Tools/find/README.md) — the filesystem half of the `bad\xff.txt` split
