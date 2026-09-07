# Typing a character you cannot type

**Level:** 101 → 201 · for anyone with a keyboard

**One line:** Two venerable systems let you type a character by mnemonic — the X11 compose key and Vim's digraphs — and between them they cover 2,580 characters while agreeing on only 611 of them; the only name that is a *standard* rather than one project's table is the Unicode Name, which is why it is the one your program can use.

```bash
python3 -c "import unicodedata as u; print(u.lookup('EURO SIGN'))"   # €
```

## The question the rest of this library leaves you holding

[`uni`](../uni/README.md) tells you a mystery byte was `U+017C LATIN SMALL LETTER Z WITH DOT ABOVE`. [Writing a code point](../../02_Characters/writing_a_code_point/README.md) tells you how to put that in a source file. Neither tells you how to get a `ż` into the commit message, the ticket, the email to the partner, or the test fixture you are typing right now — and there is no `ż` on your keyboard.

Four systems answer that, and the useful thing to know before choosing one is that **they are four different tables, not four spellings of one**.

| system | names `ż` as | where the table lives | is it a standard? |
|---|---|---|---|
| **Unicode Name** | `LATIN SMALL LETTER Z WITH DOT ABOVE` | [the Unicode Character Database ↗](https://www.unicode.org/ucd/) | **yes**, and frozen forever |
| **X11 keysym** | *(no keysym of its own — `U017C`)* | `keysymdef.h`, and a [Compose file ↗](https://www.x.org/releases/current/doc/man/man5/Compose.5.xhtml) | a convention, per implementation |
| **Vim digraph** | `z.` → `Ctrl-K z .` | [Vim's own table ↗](https://vimhelp.org/digraph.txt.html) | one editor's table |
| **HTML entity** | `&zdot;` | [the HTML5 spec ↗](https://html.spec.whatwg.org/multipage/named-characters.html) | yes, but for documents, not keyboards |

Only the first is filled in for every character, and only the first carries a promise. That is the argument the whole page comes down to, and section 4 of the program is where it is demonstrated rather than asserted.

## The compose key: a path, not a name

On X11 — Linux, BSD, and anything running a traditional desktop — one key is designated **Compose** (`Multi_key`), and the sequence you type after it is looked up in a plain text file. The standard `en_US.UTF-8` one is a real file you can read:

```text title="Measured 2026-09-07 — libx11-data 2:1.8.7-1build1, Ubuntu 24.04, in Docker"
$ wc -l /usr/share/X11/locale/en_US.UTF-8/Compose
5172 /usr/share/X11/locale/en_US.UTF-8/Compose

$ grep -n 'eacute #' /usr/share/X11/locale/en_US.UTF-8/Compose | head -3
<dead_acute> <e>                : "é"   eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <acute> <e>         : "é"   eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <e> <acute>         : "é"   eacute # LATIN SMALL LETTER E WITH ACUTE
```

Parsed whole, that file holds **5,125 sequences**. 4,836 of them produce exactly one character, and those cover **1,884 distinct code points**. The sequences are 1 to 5 keys long — 15 of length 1, 1,206 of 2, 2,388 of 3, 1,141 of 4 and 375 of 5.

Three things follow from reading it rather than being told about it.

**A sequence is a path, so the file can afford to be generous.** The euro has **13** sequences and `é` has **5**. `C=` and `=C` and `c=` and `=c` and `E=` and `e=` all work, and so do the Cyrillic letters that look like `C` and `E`. Nothing is being *parsed* — you are walking a tree, and the file simply lists every branch a person might reasonably try. Compare Vim's table, which has exactly one digraph for the euro.

**No sequence extends another, and that is why you never press Enter.** Checked over all 5,125: **zero** complete sequences are an extension of another complete sequence. So the instant your keystrokes match, the input method can commit — there is no longer path it might still be on. It is the same property that makes UTF-8 self-synchronising ([UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md)), one layer up: a code you can read left to right with no lookahead.

**`<Multi_key> <space> <space>` produces `U+00A0`.** The invisible character this library warns about most is two keystrokes that look exactly like typing a space twice. Worth knowing before you next find one in a config file and assume malice.

And one nuance for a rule this repo states elsewhere. `CONTRIBUTING.md` says you cannot type a decomposed string, because keyboard, editor and clipboard all hand you the composed spelling. On X11 that is not quite true: `<dead_acute> <nobreakspace>` yields `U+0301 COMBINING ACUTE ACCENT` on its own, so a compose key *can* type the mark. It makes [the check](../../CONTRIBUTING.md) more justified rather than less — the possibility is real, so a claim that a literal is decomposed has to be verified rather than assumed.

## Vim digraphs: the other table

Vim needs no window system, so this is the one that works over SSH, in a container, and on a Mac. Type `Ctrl-K` then two characters:

```text title="Measured 2026-09-07 — Vim 9.1 (2024 Jan 02), macOS 26.6, via digraph_get()"
  e'   -> é   U+00E9          a;   -> ą   U+0105
  z.   -> ż   U+017C          s'   -> ś   U+015B
  =e   -> €   U+20AC          l/   -> ł   U+0142
  NS   ->     U+00A0          n'   -> ń   U+0144
  O*   -> Ο   U+039F          c'   -> ć   U+0107

  digraph_getlist(1)  ->  1366 default digraphs
  digraph_getlist()   ->     0 user-defined
```

`:digraphs` prints the whole table, and `ga` tells you the code point under the cursor — so Vim is both the input method and the inspector, which is why it survives as one.

The 1,366 pairs cover **1,307 distinct code points**, because **59 characters have two digraphs each**: `¡` is both `!I` (the mnemonic form) and `~!` (the visual one), and Vim kept both rather than choose. One of those pairs is worth its own sentence: **`NU` and `LF` both give `U+000A`.** The digraph for NUL hands you a line feed, because Vim represents a NUL in a buffer as a newline — the same substitution [The NUL byte](../../02_Characters/the_nul_byte/README.md) documents from the other end.

Two cautions. `digraph_get()` returns the *last character of the pair* when the pair is not in the table, so a wrong guess looks like a result rather than an error. And `uni`'s `%(digraph)` column is Vim's table, one copy behind: on eight code points — including `•`, `…` and `⟨` `⟩` — Vim has a digraph and `uni` prints nothing.

## The two tables barely overlap

This is the number worth carrying away.

| | code points it can type |
|---|---|
| the standard `en_US.UTF-8` Compose file | 1,884 |
| Vim 9.1's default digraphs | 1,307 |
| **both** | **611** |
| Compose only | 1,273 |
| Vim only | 696 |
| either | 2,580 |

*Measured 2026-09-07 by comparing the parsed Compose file against `digraph_getlist(1)`, matching on the code point produced.*

Two systems that have each been shipping for over thirty years, both aimed squarely at "type a letter your keyboard does not have", and of the 2,580 characters they can produce between them only **611 — under a quarter —** are reachable through both. Neither is a subset of the other, and there is no third table that reconciles them, because there was never a body whose job that was. The Unicode Name is the only naming of a character that anybody standardised — which is exactly why it is the one that ends up in code, and why `\N{EURO SIGN}` is worth preferring over `€` when a reader has to check the intent.

## macOS has no compose key, and four other things instead

There is no Compose file on a Mac at all — not in `/usr/share/X11`, not in `/opt/X11`, and no `~/.XCompose` unless you install a third-party tool for it. macOS solved the same problem four other ways, and all four ship with the system:

| method | how | good for |
|---|---|---|
| **dead keys** | `Option`+`e` then `e` → `é`; `Option`+`u` then `u` → `ü`; `Option`+`n` then `n` → `ñ` | the handful of accents in Latin-1 |
| **press and hold** | hold `e`, pick from the popup (`ApplePressAndHoldEnabled`, on by default) | the same handful, discoverable |
| **Character Viewer** | `Control`-`Command`-`Space`; it has a search box | emoji, symbols, anything you can name |
| **Unicode Hex Input** | a keyboard layout: hold `Option`, type four hex digits | when you know the code point |

*Not machine-checked — these are keystrokes, and CI has no keyboard. What was verified on macOS 26.6 on 2026-09-07 is the absence of any Compose file, that `Unicode Hex Input` is present in the system's keyboard-layouts bundle, and that `CharacterPalette.app` — the Character Viewer — is in `/System/Library/Input Methods/`.*

The fourth is the one people do not know they have: it is a keyboard *layout*, so you add it in Keyboard Settings and switch to it, and then `Option` plus `20AC` is a euro. It takes four hex digits, which is the BMP and nothing above it — see the plane discussion in [Writing a code point](../../02_Characters/writing_a_code_point/README.md).

For a Polish keyboard the accented letters are on `Option` in the *Polish Pro* layout rather than composed at all, which is the pattern generally: **a layout beats an input method when you type the same twenty characters every day**, and an input method beats a layout when you need an arbitrary one twice a year.

## `uni` is the input method you already have installed

`uni print` takes a code point and prints the character; pipe it to a clipboard and you have a general-purpose input method that needs no layout, no window system, and no editor:

```bash
uni print U+20AC | pbcopy                       # macOS
uni print U+20AC | xclip -selection clipboard   # X11
uni print U+20AC | wl-copy                      # Wayland
uni search 'z with dot' -c                      # when you know the words, not the number
uni emoji firefighter -tone medium -gender man  # the other database, see the uni page
```

The `search` direction is the one no keyboard has: you do not need the code point, only some of the words in the name. And because the output is bytes on a pipe, the same command works in a script, in a commit hook, and over SSH.

## Whatever you typed, the bytes are the answer

Every method on this page produces a code point, and none of them tells you which one you got. A dead key, a compose sequence, a digraph and a paste from a web page can hand you `U+00E9` or `U+0065 U+0301`, and they are the same picture at every size. A paste can also hand you a [look-alike from another script](../../02_Characters/confusables_and_scripts/README.md), or a no-break space where you wanted a space.

So the last step of typing a character you could not type is checking what you got:

```bash
printf 'caf\303\251' | uni identify -c     # one row: it is composed
python3 -c "import unicodedata as u,sys; s=sys.argv[1]; print(len(s), s==u.normalize('NFC',s))" "café"
```

One row or two is the whole diagnosis, and it takes a second. [Preparing a string](../../02_Characters/preparing_a_string/README.md) is what to do about the answer.

## In Python

<!-- output:typing_a_character_py -->
*Verified output of [`typing_a_character_py.py`](examples/typing_a_character_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FOUR SYSTEMS NAME A CHARACTER, AND THEY ARE NOT ONE TABLE
------------------------------------------------------------------------
   code point  Unicode Name                         keysym         digraph  HTML
   U+0041      LATIN CAPITAL LETTER A               A              -        &#x41;
   U+00E9      LATIN SMALL LETTER E WITH ACUTE      eacute         e'       &eacute;
   U+00A0      NO-BREAK SPACE                       nobreakspace   NS       &nbsp;
   U+0142      LATIN SMALL LETTER L WITH STROKE     -              l/       &lstrok;
   U+017C      LATIN SMALL LETTER Z WITH DOT ABOVE  -              z.       &zdot;
   U+20AC      EURO SIGN                            EuroSign       =e       &euro;
   U+0CA0      KANNADA LETTER TTHA                  -              -        &#xca0;

   Read down the two middle columns. The Polish letters have a Vim
   digraph and no keysym of their own; the Kannada letter has neither,
   which is what 'a script nobody here has a keyboard for' means in
   practice. Only the Name column is filled all the way down, and only
   the Name column is a standard rather than one project's table.

2. A COMPOSE SEQUENCE IS A PATH, NOT A NAME
------------------------------------------------------------------------
   30 sequences, verbatim from the en_US.UTF-8 Compose file:

   keys                                      gives     keysym
   dead_acute e                              U+00E9    eacute
   Multi_key acute e                         U+00E9    eacute
   Multi_key e acute                         U+00E9    eacute
   Multi_key apostrophe e                    U+00E9    eacute
   Multi_key e apostrophe                    U+00E9    eacute
   Multi_key C equal                         U+20AC    EuroSign
   Multi_key equal C                         U+20AC    EuroSign
   Multi_key c equal                         U+20AC    EuroSign
   Multi_key equal c                         U+20AC    EuroSign
   Multi_key E equal                         U+20AC    EuroSign
   Multi_key equal E                         U+20AC    EuroSign
   Multi_key e equal                         U+20AC    EuroSign
   Multi_key equal e                         U+20AC    EuroSign
   Multi_key Cyrillic_ES equal               U+20AC    EuroSign
   Multi_key equal Cyrillic_ES               U+20AC    EuroSign
   Multi_key Cyrillic_IE equal               U+20AC    EuroSign
   Multi_key equal Cyrillic_IE               U+20AC    EuroSign
   dead_currency e                           U+20AC    EuroSign
   dead_stroke l                             U+0142    U0142
   Multi_key slash l                         U+0142    U0142
   Multi_key l slash                         U+0142    U0142
   Multi_key KP_Divide l                     U+0142    U0142
   dead_abovedot z                           U+017C    U017C
   Multi_key period z                        U+017C    U017C
   Multi_key z period                        U+017C    U017C
   Multi_key space space                     U+00A0    nobreakspace
   Multi_key o c                             U+00A9    copyright
   Multi_key O C                             U+00A9    copyright
   Multi_key C O                             U+00A9    copyright
   Multi_key minus minus minus               U+2014    U2014

   The euro alone has 13 of them in that file, and the reason is
   that a compose sequence is not a name being looked up -- it is a PATH
   through a tree, so the file can afford to list every path a person
   might try. C= and =C and c= and =c and E= and e=, plus the Cyrillic
   letters that look like C and E. Vim's table has exactly one: =e.

   Two rows are worth stopping on. <Multi_key> <space> <space> produces
   U+00A0, so the most troublesome invisible character in this library
   is two keystrokes that look exactly like typing a space twice. And
   the em dash takes three keys after Multi_key, not two -- the length
   is not fixed, which is what section 3 is about.

3. WHY IT NEEDS NO TERMINATOR
------------------------------------------------------------------------
   sequence lengths in this sample: [2, 3, 4]
   sequences that EXTEND another complete sequence: 0

   That zero is the whole design. No complete sequence is a prefix of
   another, so the moment the keys you have typed match a sequence, the
   input method can commit -- there is no longer path it might still be
   on, and you never press Enter to say you are done. It holds over the
   whole file too, not just this sample; the page has the number.

   It is the same property that makes UTF-8 self-synchronising, one
   layer up: a code that can be read left to right with no lookahead.

4. THE ONE YOUR PROGRAM CAN ACTUALLY USE
------------------------------------------------------------------------
   Compose needs X11. Digraphs need Vim. The Unicode Name needs
   nothing at all, because it is in the standard library:

   lookup('EURO SIGN')
      -> U+20AC   '€'
   lookup('LATIN SMALL LETTER Z WITH DOT ABOVE')
      -> U+017C   'ż'
   lookup('NO-BREAK SPACE')
      -> U+00A0   '\xa0'
   lookup('KANNADA LETTER TTHA')
      -> U+0CA0   'ಠ'

   And it round-trips: unicodedata.name(unicodedata.lookup(n)) == n for
   every name above -> True

   That round trip is a promise, not an observation: a character's Name
   is frozen when the character is assigned and can never be changed,
   typos included. Neither the keysym table nor the digraph table
   promises anything of the sort. Vim has added digraphs over the
   years, and uni's copy of that table is already behind Vim's own.

5. WHATEVER YOU TYPED, THE BYTES ARE THE ANSWER
------------------------------------------------------------------------
   two ways to end up with the same picture:
      one code point   1  U+00E9        2 bytes
      two code points  2  U+0065 U+0301  3 bytes
      equal?           False

   A dead key, a compose sequence, a digraph and a paste from a web
   page can each hand you either one, and they are the same picture at
   every size. So the last step of typing a character you could not
   type is checking what you actually got: `uni identify` prints one
   row or two, and unicodedata.normalize settles it in a program.

   The Compose file can even produce the bare mark on its own --
   <dead_acute> <nobreakspace> is U+0301 with nothing under it -- which
   is the one route by which a hand-typed decomposed string is possible
   rather than merely claimed.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** `unicodedata.lookup(name)` is the runtime form and `"\N{EURO SIGN}"` the literal form, and they read the same table — so a name that works in one works in the other, and a misspelt name fails at *compile* time in the literal and at run time in the call. That is a reason to prefer the literal where you can. `unicodedata.name(c)` goes back the other way, and raises for characters that have no Name at all (the controls), which is why it takes a default argument. For anything interactive, remember that `input()` gives you whatever the terminal sent, normalisation and all — normalise at that boundary, not later.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* SE80 and ADT have no compose key and no digraphs, so in practice the character arrives by paste, which is the least verifiable route on this page. Two habits are worth more than any input trick. Build the character from its code point in code rather than pasting it — `cl_abap_conv_in_ce=>uccp( '20AC' )` — so the source says which character it is and a reviewer can check it without a hex editor; and where a constant is invisible, name it (`cl_abap_char_utilities` does exactly this for CR/LF and tab, and your own constant can do it for a no-break space). A pasted literal in an ABAP program is the case with no escape form to fall back on, so the discipline has to come from the naming. The code page it finally travels in belongs to the interface agreement, not to the editor — see [SAP code pages](../../07_Real_Data/sap_code_pages/README.md).

## Try it

```bash
cd 11_Tools/typing_a_character/examples
python3 typing_a_character_py.py
```

Then the three one-liners, on whatever machine you are at:

```bash
vim -c 'digraphs' -c 'q'                       # 1366 pairs, and a table you can read
uni search 'no-break' -c                       # the invisible one, by name
ls /usr/share/X11/locale/en_US.UTF-8/Compose   # present on Linux, absent on a Mac
```

Without the machine: a colleague sends a patch whose test fixture contains what looks like `café`, and your test compares it against a string built with `\N{LATIN SMALL LETTER E WITH ACUTE}`. It fails. Name the two things that could have happened at their keyboard, say which command tells them apart in one line, and say which of the two you would fix — the fixture or the comparison.

## See also

- [`uni` — the character's name](../uni/README.md) — the identify direction, and the tool half of this page
- [Writing a code point](../../02_Characters/writing_a_code_point/README.md) — the same question for source code, where the answer is an escape
- [Preparing a string](../../02_Characters/preparing_a_string/README.md) — what to do once you know the two spellings are different
- [Confusables and scripts](../../02_Characters/confusables_and_scripts/README.md) — the paste that gives you the right picture and the wrong letter
- [The NUL byte](../../02_Characters/the_nul_byte/README.md) — where the `NU` digraph's line feed comes from
- [Normalization](../../04_Python/normalization/README.md) — NFC, NFD, and which one to keep
- [The five worth installing](../worth_installing/README.md) — `uni` is on that list for this reason among others
