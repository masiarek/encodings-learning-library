# Writing a code point

**Level:** 201 · working knowledge

**One line:** One character has many written forms, and the escape a language gives you is not decoration — its shape tells you what that language thinks a character **is**: a scalar value in Rust, a UTF-16 code unit in Java and JSON, a name in Python, and in C something that is not a string feature at all.

```python
"\u20ac" == "\N{EURO SIGN}" == chr(0x20AC) == "€"   # True — one string, four spellings
```

## Four questions that look like one

`U+202E`, `\u{202E}`, the character itself (which draws nothing at all), `E2 80 AE`, `&#8238;`, `M-bM-^@M-.` — six ways of writing one character, and they are not six styles to choose between. They are answers to four different questions, and confusing them is most of the trouble people have here.

| the question | the notation | who owns it |
|---|---|---|
| **What is this character?** | `U+202E`, the name `RIGHT-TO-LEFT OVERRIDE`, decimal `8238` | [Unicode code points](../unicode_code_points/README.md) |
| **How do I write it in my source?** | `"\u{202E}"` (Rust), `"\u202e"` (Python), `"\N{RIGHT-TO-LEFT OVERRIDE}"` (Python, by name) | **this page** |
| **How is it stored or sent?** | UTF-8 `E2 80 AE`; JSON `\u202e`; a URL's `%E2%80%AE`; HTML `&#8238;` | [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md), [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) |
| **How does a tool show it back?** | `cat -v`'s `M-bM-^@M-.`, `xxd`'s `e280ae`, a `�`, a blank | [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) |

Row two is the one nothing else in this library covers, and it is the row a programmer actually types. Row three looks similar and is a different subject: those escapes exist because a *channel* refuses the bytes, and they are chosen by a protocol. The escape on this page exists because a *keyboard*, a *reviewer* or a *diff* refuses the character, and it is chosen by you.

## The escape tells you what the language thinks a character is

Every language on this list can write `😀` as an escape. Look at what each one puts inside it.

| language | `€` (U+20AC) | `😀` (U+1F600) | what goes in the escape |
|---|---|---|---|
| **Rust** | `"\u{20AC}"` | `"\u{1F600}"` | a **scalar value**, 1–6 hex digits, braces instead of a width |
| **Python** | `"\u20ac"` | `"\U0001F600"` | a code point, in **fixed** widths — 4 or 8 — plus `"\N{GRINNING FACE}"` by **name** |
| **C** | `"\u20ac"` | `"\U0001F600"` | a **source-character-set** member, translated before tokenising ([C11 6.4.3 ↗](https://port70.net/~nsz/c/c11/n1570.html#6.4.3)) |
| **Java** | `"\u20AC"` | `"\uD83D\uDE00"` | a **UTF-16 code unit**, 4 hex digits, processed by the lexer ([JLS §3.3 ↗](https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.3)) |
| **JavaScript** | `"\u20AC"` | `"\u{1F600}"` or `"\uD83D\uDE00"` | a code unit, or since ES6 a code point in braces |
| **JSON** | `"\u20AC"` | `"\uD83D\uDE00"` | a **UTF-16 code unit** and nothing else ([RFC 8259 §7 ↗](https://www.rfc-editor.org/rfc/rfc8259#section-7)) |
| **shell** | `printf '\xe2\x82\xac'` | `printf '\xf0\x9f\x98\x80'` | **bytes**. `printf` has no idea what a code point is |

Three families, and the differences are load-bearing rather than cosmetic:

**Rust takes a scalar value**, which is every code point *except* the 2,048 surrogates — exactly what a `char` may hold. So `\u{D800}` is not a spelling Rust has; the compiler refuses it, and `char::from_u32` returns `None` for the same number at run time. The type and the escape agree because they enforce the same rule.

**Java and JSON take a UTF-16 code unit**, which is why an emoji is two escapes there and one everywhere else. That is not a quirk of notation — it is [UTF-16](../../03_Encodings/utf16_and_surrogates/README.md) showing through the syntax, in JSON's case inside a format whose files are UTF-8 and contain no surrogates at all. [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) follows that leak to where it causes bugs.

**The shell takes bytes**, because `printf` writes bytes and has no table. `\xe2\x82\xac` is not "the euro sign" to it; it is three numbers.

### Planes, the BMP, and why one language needs two escapes

Unicode is cut into **17 planes** of 65,536 code points each. Plane 0 — everything up to `U+FFFF` — is the **Basic Multilingual Plane**, the **BMP**, and holds every character UTF-16 can write in a single 16-bit unit. Planes 1 to 16 are the *supplementary* planes, informally the **astral** planes, and a character living there needs a **surrogate pair**: two UTF-16 units, `D83D DE00` for `😀`.

That is the whole explanation for the `😀` column above. A language whose escape names a code point needs one escape whatever plane the character is in. A language whose escape names a code unit needs two as soon as you leave the BMP — and it needs them in a file format that has no surrogates in it.

## The widths are the syntax

Python's escapes have no closing delimiter, so the width *is* how the parser knows where the escape ends: exactly 2 hex digits after `\x`, exactly 4 after `\u`, exactly 8 after `\U`. One digit short is a `SyntaxError`, not a shorter character. Rust closes the escape with a brace instead and accepts 1 to 6 digits, so `\u{41}` needs no padding and `\u{000041}` is the same character.

Neither will read the other's spelling. `"\u{20AC}"` in Python is *truncated `\uXXXX` escape*; `"\u20ac"` in Rust is not an escape at all.

The third Python form takes a name — `"\N{EURO SIGN}"` — and it is the only one that cannot be quietly wrong. A misspelt name is a compile error; a mistyped *number* is a different, perfectly valid character. `U+20AC` is EURO SIGN, `U+20AD` is KIP SIGN, `U+20BC` is MANAT SIGN, and no code review will catch the digit.

### And one language refuses to escape ASCII

C calls its escape a **universal character name**, and the name is the point: it is translated in phase 1, before the source is even tokenised. Two things follow that no other language here has. A UCN works in an **identifier** — `int caf\u00e9 = 7;` compiles and declares one variable. And C **forbids** a UCN below `U+00A0`, except `$`, `@` and `` ` ``:

```text
$ cc -std=c11 -Wall -Wextra -o /dev/null cbad.c        # Apple clang 21.0.0, 2026-09-06
cbad.c:2:22: error: character 'A' cannot be specified by a universal character name
    2 |     const char *a = "\u0041";
      |                      ^~~~~~
cbad.c:3:22: error: invalid universal character
    3 |     const char *b = "\ud800";
      |                      ^~~~~~
```

gcc 13 refuses both too, in its own words (*"`\u0041` is not a valid universal character"*). The reason for the rule is the phase it runs in: if `\u0022` turned into a quotation mark before tokenising, an escape could close a string literal and a comment could end somewhere the reader cannot see. A standards committee wrote that rule so that **the text a compiler tokenises is the text a person read** — which is the same worry as the last section of this page, answered in 1999.

## Printing is a choice of spelling too

The reverse direction is a decision nobody thinks of as one, and the two standard libraries here made the same call independently.

Python's `repr()` prints a character as itself when `str.isprintable()` is true, and as an escape when it is not. Rust's `{:?}` is `char::escape_debug`, which asks its own printability table and reaches the same answer. Two libraries, no shared code, one rule:

> **A character that draws something is printed as itself. A character that draws nothing is printed as an escape.**

That is why `repr()` and `{:?}`, not `str()` and `{}`, are the right way to print a value you did not write — a filename, a form field, a row out of somebody's CSV. Rust ships three escapers so you can see the choice being made: `escape_unicode` escapes everything and is unreadable, `escape_default` keeps ASCII and escapes the rest, `escape_debug` escapes only what would not draw. Python's `ascii()` is roughly `escape_default`; `repr()` is `escape_debug`.

## So: character, or escape?

Write the character when a reader can see it and type it. `"café"` is better than `"café"` in every way that matters — it survives a rename, it is greppable by the word, and nobody has to decode it.

Write the escape in three cases:

1. **The character is invisible or ambiguous.** A no-break space, a zero-width joiner, a combining mark, a bidi control. Written raw, these are absent from the diff, absent from the review, and in the worst case they [change what the line appears to say](../../12_Adversarial/trojan_source/README.md). Written as escapes they are ordinary ASCII: greppable, diffable, and unable to do anything to the page displaying them.
2. **Nobody on the team has the keyboard.** `ಠ` is `\u{CA0}`, and if the alternative is copying a glyph nobody can verify, the escape is the honest form. `\N{KANNADA LETTER TTHA}` is better still.
3. **The tooling between you and the file is not trusted to be UTF-8.** A patch through an old mail relay, a config read by something that guesses, an interface whose code page is somebody else's decision.

This library follows its own rule. Every invisible character in every example on this page reaches your screen as an escape, and the [security chapter](../../12_Adversarial/README.md) makes it a hard house rule: no example may contain or print a raw bidi control, because an answer key holding one would reorder the page that displays it.

## In Python

<!-- output:writing_a_code_point_py -->
*Verified output of [`writing_a_code_point_py.py`](examples/writing_a_code_point_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FIVE SPELLINGS, ONE CHARACTER
------------------------------------------------------------------------
   "€"                   the character itself, pasted in
   "\u20ac"              the four-digit escape
   "\N{EURO SIGN}"       by name
   chr(0x20AC)           from the number, at run time
   chr(8364)             the same number in decimal

   distinct strings among those five: 1
   the one they all are: '€'  U+20AC  EURO SIGN

   Five spellings, one string. Nothing survives into the running
   program except the number -- so the choice between them is a
   message to the next person who reads the file, not to Python.

2. THE WIDTH IS PART OF THE ESCAPE
------------------------------------------------------------------------
   The two numeric escapes have FIXED widths. There is no closing
   delimiter, so the width is the only thing telling the parser where
   the escape stops.

   \x2           truncated \xXX escape
   \xe9          compiles
   \u20a         truncated \uXXXX escape
   \u20ac        compiles
   \U0001F60     truncated \UXXXXXXXX escape
   \U0001F600    compiles

   Exactly 2 digits after \x, 4 after \u, 8 after \U. Rust writes the same character with braces instead of a
   width -- and that spelling is not Python:

   \u{20AC}      truncated \uXXXX escape

   Every one of those failures is a SyntaxError, raised before the
   line can run. An escape is not a function call; it is spelling,
   and the parser is the one doing the reading.

3. THE THIRD FORM TAKES A NAME, AND IT IS CHECKED TOO
------------------------------------------------------------------------
   "\N{EURO SIGN}"           -> '€'
   "\N{euro sign}"           -> '€'    (names are case-insensitive)
   "\N{NOT A REAL NAME}"     -> unknown Unicode character name

   A misspelt name is a SyntaxError, so \N{...} is the one escape
   that cannot be quietly wrong. A misspelt NUMBER is a different
   character that compiles perfectly:

      U+20AC  €  EURO SIGN
      U+20AD  ₭  KIP SIGN
      U+20BC  ₼  MANAT SIGN

   One digit apart, and nothing in a code review would show it. That
   is the argument for the name form wherever a reader has to check
   the intent rather than the value.

4. THE SAME ESCAPE MEANS SOMETHING ELSE IN A BYTES LITERAL
------------------------------------------------------------------------
   \x is the escape both kinds of literal share, and it does
   not mean the same thing in each:

   "\xe9"      'é'         1 character   -- a CODE POINT below 256
   b"\xe9"     b'\xe9'     1 byte        -- a BYTE

   And the two spellings a str has that bytes does not:

   b"\u20ac"   b'\\u20ac'  6 bytes       -- not an escape at all
   r"\u20ac"   '\\u20ac'   6 characters  -- raw: the backslash is data

   A bytes literal has no \u, \U or \N, because
   a byte is not a code point and there would be nothing for them to
   mean. So the backslash is read as data and you get six bytes -- a
   silent six-fold difference in length from the str you meant. Python
   is in the middle of taking that away: compiling that literal
   raises a warning (1 here) whose text says such sequences
   will not work in the future. Which CATEGORY of warning depends on
   your Python version, so this program counts them and the page
   names one, with a date.

5. PRINTING IS A CHOICE OF SPELLING TOO
------------------------------------------------------------------------
   str()    café € ಠ
   repr()   'café € ಠ'
   ascii()  'caf\xe9 \u20ac \u0ca0'

   ascii() escapes everything above 127 and picks the shortest form
   per character -- two widths in one line, \xe9 for the
   e-acute and \u0ca0 for the Kannada letter.

   repr() is the interesting one, because it escapes SOME characters
   and not others. The rule is str.isprintable():

   code point  printable   repr()        name
   U+0041      True        'A'           LATIN CAPITAL LETTER A
   U+20AC      True        '€'           EURO SIGN
   U+0CA0      True        'ಠ'           KANNADA LETTER TTHA
   U+00A0      False       '\xa0'        NO-BREAK SPACE
   U+0009      False       '\t'          <a control: TAB has no name>
   U+202E      False       '\u202e'      RIGHT-TO-LEFT OVERRIDE

   A character that draws something is printed as itself; one that
   draws nothing is printed as an escape. That is the rule you want
   for a log line, an error message or a test failure, and it is why
   repr() rather than str() is the right way to print a value you did
   not write yourself.

   Read the last row again. Printed raw, that character reorders the
   line it lands in -- including this one. repr() will not do that to
   you, and neither will this program: every invisible character above
   reached the screen as an escape.
```
<!-- /output -->

## In Rust

<!-- output:writing_a_code_point_rs -->
*Verified output of [`writing_a_code_point_rs.rs`](examples/writing_a_code_point_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE FORM, ONE TO SIX DIGITS
------------------------------------------------------------------------
   '\u{20ac}'   '\u{20AC}'   '\u{020ac}'   '\u{0020ac}'
   all the same char: true
   and that char is: '€'   U+20AC

   Hex digits are case-insensitive and leading zeros are free,
   because the closing brace is what ends the escape. Python
   spells the same character \u20ac and counts the digits.

2. WHAT GOES IN THE BRACES IS A SCALAR VALUE
------------------------------------------------------------------------
   The escape does not take 'a number'. It takes a Unicode
   SCALAR VALUE, which is every code point except the 2,048
   surrogates -- exactly what a `char` is allowed to hold.

   U+000041  char::from_u32 -> Some   UTF-8 bytes 1   'A'
   U+0020AC  char::from_u32 -> Some   UTF-8 bytes 3   '€'
   U+01F600  char::from_u32 -> Some   UTF-8 bytes 4   '😀'
   U+10FFFF  char::from_u32 -> Some   UTF-8 bytes 4   '\u{10ffff}'
   U+00D800  char::from_u32 -> None   not a scalar value
   U+110000  char::from_u32 -> None   not a scalar value

   The last two are the two ways to be outside the range: a
   surrogate, which belongs to UTF-16's machinery and is not a
   character, and a number above the top of Unicode. Written as
   escapes, `\u{D800}` and `\u{110000}` do not compile at all --
   the page quotes what rustc says. char::from_u32 is the same
   check moved to run time, which is why it returns an Option.

3. THREE ESCAPERS THAT DISAGREE ON PURPOSE
------------------------------------------------------------------------
   code point  escape_       escape_       escape_
               unicode()     default()     debug()
   U+0041      \u{41}        A             A
   U+00E9      \u{e9}        \u{e9}        é
   U+20AC      \u{20ac}      \u{20ac}      €
   U+1F600     \u{1f600}     \u{1f600}     😀
   U+000A      \u{a}         \n            \n
   U+202E      \u{202e}      \u{202e}      \u{202e}

   Read the three columns as three different answers to 'who is
   going to read this?'. escape_unicode() escapes everything, so
   its output is pure ASCII and survives any channel. Nobody can
   read it. escape_default() keeps ASCII and escapes the rest --
   the old, safe, unfriendly choice. escape_debug() escapes only
   what would not draw, so an accented letter, a currency sign
   and an emoji all come through as themselves.

4. {:?} IS escape_debug, AND PYTHON'S repr() AGREES WITH IT
------------------------------------------------------------------------
   {}    café € ಠ
   {:?}  "café € ಠ"

   a string with an invisible character in it, Debug-printed:
   "admin\u{202e} user"

   Eleven characters, and Debug printed ten of them as themselves
   and one as an escape. Python's repr() makes the same split on
   the same string, by asking str.isprintable(); Rust asks its own
   printability table. Two standard libraries, no shared code, one
   rule: a character that draws something is printed as itself, and
   a character that draws nothing is printed as an escape.

   Display ({}) does NOT do this. Printing that string with {}
   would reorder the rest of the line, which is why this program
   does not do it.

5. ONE ESCAPE, THREE LENGTHS
------------------------------------------------------------------------
   escape     chars  bytes  utf-16   plane   as itself
   \u{41}         1      1       1       0   A
   \u{E9}         1      2       1       0   é
   \u{20AC}       1      3       1       0   €
   \u{CA0}        1      3       1       0   ಠ
   \u{1F600}      1      4       2       1   😀

   One escape is always one `char`. It is one to four bytes in
   UTF-8, and one OR TWO units in UTF-16 -- and the last column
   says why. Unicode is cut into 17 planes of 65,536 code points.
   Plane 0 is the Basic Multilingual Plane, the BMP, and it holds
   everything up to U+FFFF; a character in it is one UTF-16 unit.
   Planes 1 to 16 are the supplementary planes, informally the
   ASTRAL planes, and a character there needs a surrogate PAIR --
   two UTF-16 units, which is why JSON, Java and JavaScript spell
   the emoji \uD83D\uDE00 and Rust spells it \u{1F600}.
```
<!-- /output -->

## The C view

<!-- output:writing_a_code_point_c -->
*Verified output of [`writing_a_code_point_c.c`](examples/writing_a_code_point_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A UCN NAMES A CODE POINT; \x NAMES A BYTE
------------------------------------------------------------------------
   literal                n   bytes
   "\u00e9"                2   c3 a9
   "\xc3\xa9"              2   c3 a9
   "\xe9"                  1   e9

   The first two are the same two bytes and got there by different
   routes. \u00e9 names code point U+00E9 and lets the COMPILER
   encode it, in whatever the execution character set is -- UTF-8
   for clang and gcc today. \xc3\xa9 names those two bytes directly.
   \xe9 is one byte and is not the same character at all: it is what
   Latin-1 would have used, sitting in a UTF-8 string where it is
   not valid.

2. THE ESCAPE IS WIDER THAN THE STRING IT IS IN
------------------------------------------------------------------------
   caf\u00e9 = 7

   That is a UCN in an IDENTIFIER, declared with the escape and
   used with it too. C translates universal character names in
   phase 1, before tokenising, so by the time anything asks what a
   string literal contains the escape is long gone. Python and Rust
   both handle their escapes inside the string literal, and neither
   lets you spell an identifier that way.

3. AND C IS THE ONE THAT REFUSES TO ESCAPE ASCII
------------------------------------------------------------------------
   These three compile, because $ @ and ` are the named exceptions:
   "\u0024\u0040\u0060"    3   24 40 60

   This one does not compile at all:
       const char *a = "\u0041";   /* the letter A */

   C11 6.4.3 forbids a UCN below U+00A0 except those three, and
   forbids the surrogates D800-DFFF. The reason is the phase it
   runs in: if \u0022 became a quotation mark before tokenising,
   an escape could close a string literal, and a comment could end
   somewhere the reader cannot see. The rule exists so that the
   text a compiler tokenises is the text a person read.

   Which is the same worry as the invisible-character section of
   this lesson, answered in 1999 by a standards committee, in the
   only language here whose escape runs early enough to need it.
```
<!-- /output -->

## In the terminal

The shell is the one place on this page where the escape that names a code point is the escape you cannot rely on. `printf '\u20ac'` gives three different answers on three configurations, measured the day this page was written:

| bash | locale | `printf '\u20ac'` produces |
|---|---|---|
| 5.2.21, Ubuntu 24.04 | `C.UTF-8` | `e2 82 ac` — the euro sign |
| 5.2.21, Ubuntu 24.04 | `C` | `5c 75 32 30 41 43` — the escape handed back, **hex uppercased** |
| 3.2.57, macOS 26.6 | either | `5c 75 32 30 61 63` — the escape handed back untouched |

*Measured 2026-09-06 on this Mac and on `ubuntu:24.04` in Docker. macOS still ships bash 3.2, which predates `printf`'s `\u` entirely; bash 4.2 and later understand it but can only produce a character the current locale can represent, and hand the escape back when it cannot.*

Six bytes either way, and not the same six. So `\u` is the least portable escape on this page, and `\xHH` and `\NNN` — which name bytes and ask nothing of the locale — are identical everywhere. The example records the *shape* (six bytes, not three) rather than the bytes, which is the only claim that holds on both runners.

<!-- output:writing_a_code_point_sh -->
*Verified output of [`writing_a_code_point_sh.sh`](examples/writing_a_code_point_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE ESCAPES THAT NAME BYTES WORK EVERYWHERE
------------------------------------------------------------------------
   printf "\xe2\x82\xac"       e2  82  ac
   printf "\342\202\254"       e2  82  ac
   the character, pasted in    e2  82  ac

   Three bytes, three ways of asking for them, and none of the three
   mentions Unicode. \xHH is hex and \NNN is octal; both name a byte
   and stop there. It is the same E2 82 AC either way because the
   file this script is written in is UTF-8, not because printf knows
   that U+20AC is a euro sign. It does not.

2. THE ESCAPE THAT NAMES A CODE POINT IS THE ONE THAT TRAVELS BADLY
------------------------------------------------------------------------
   printf '\u20ac' | wc -c   ->  6

   Three, if that escape had produced a euro sign. It produced 6 --
   the six characters of the escape itself, handed back unchanged.
   Under LC_ALL=C there is no euro sign to produce, so printf gives up
   and prints what it was given. Which six bytes it hands back is not
   the same on every machine, so this script counts them and the page
   prints the measurement with a date. Three configurations, three
   answers, is the summary.

3. AND THREE TOOLS SPELL THE SAME BYTES THREE WAYS
------------------------------------------------------------------------
   od -An -tx1        e2  82  ac
   xxd -p            e282ac
   cat -v            M-bM-^BM-,
   wc -c             3

   Same three bytes, four renderings. cat -v is the odd one: M- means
   'the high bit is set', so M-b is 0x62 with the top bit on, which is
   0xE2 -- an ASCII spelling of a non-ASCII byte, which is why it
   survives a pipe, an email and a bug report intact.

   Every line of this section is a SPELLING of one thing. Nothing here
   changed the file; the tools disagree about how to say it out loud.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** You already have all three forms; the habit worth forming is picking the one that makes the intent checkable. Prefer `"\N{NO-BREAK SPACE}"` over `"\u00a0"` in code somebody will review, because the second is a number to look up and the first is a sentence. Use `repr()` (or `!r` in an f-string) for any value that came from outside your program — `print(f"missing: {name!r}")` shows you the trailing no-break space that `print(name)` hides. And know that `\u` in a **bytes** literal is not an escape at all: `b"\u20ac"` is six bytes, Python raises only a warning today, and the warning says it will stop working.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* There is no `\u` escape in an ABAP string literal, which is the difference to lead with — you cannot spell a code point in the source at all. The equivalents are runtime calls: `cl_abap_conv_in_ce=>uccp( )` takes a four-digit code point and returns the character, and `cl_abap_char_utilities` holds the ones you need most often as constants (`cr_lf`, `horizontal_tab`, `newline`) precisely because they cannot be written inline. Both are old interfaces, so check what your release offers before reaching for them — newer systems route byte/character conversion through `cl_abap_conv_codepage`. Two practical consequences: an invisible character in ABAP source is *completely* invisible, with no escape form to make it greppable, so a literal pasted out of a spreadsheet can carry a no-break space that no code review will ever show; and when you need one deliberately, build it with `uccp( )` and a named constant rather than pasting a glyph, so the next reader sees the number. The code page a character is finally written in belongs to the interface agreement, not to the tool — see [SAP code pages](../../07_Real_Data/sap_code_pages/README.md).

## Try it

```bash
cd 02_Characters/writing_a_code_point/examples
python3 writing_a_code_point_py.py
rustc --edition 2024 writing_a_code_point_rs.rs -o /tmp/spellings && /tmp/spellings
cc -std=c11 -Wall -Wextra writing_a_code_point_c.c -o /tmp/spellings_c && /tmp/spellings_c
bash writing_a_code_point_sh.sh
```

Then make a compiler refuse you. Three lines, three different reasons, and each error message names the rule:

```bash
printf 'fn main() { let _ = "\\u{D800}"; }\n' > /tmp/a.rs && rustc --edition 2024 --emit=metadata -o /dev/null /tmp/a.rs
printf 'fn main() { let _ = "\\u{110000}"; }\n' > /tmp/b.rs && rustc --edition 2024 --emit=metadata -o /dev/null /tmp/b.rs
printf 'int main(void){ const char *a = "\\u0041"; return a[0]; }\n' > /tmp/c.c && cc -std=c11 -o /dev/null /tmp/c.c
```

Without the machine: three test fixtures spell one word. The first holds `"caf\u00e9"`, the second holds `"café"` typed as a literal, and the third holds `"cafe\u0301"` — an `e` followed by COMBINING ACUTE ACCENT. Two of the three compare equal. Say which two, say which of the differences is a *spelling* and which is a *different string*, and name the page in this library that settles the second one.

## See also

- [Unicode code points](../unicode_code_points/README.md) — the number these are all spellings of
- [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) — the other escapes: JSON, URLs, mail headers, domain names, chosen by a protocol rather than by you
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — where the pair in `😀` comes from
- [What you see is not what runs](../../12_Adversarial/trojan_source/README.md) — the case where writing the escape is not a style preference
- [Confusables and scripts](../confusables_and_scripts/README.md) — the other half: characters that draw the same picture and are not the same code point
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — the fourth question, how a tool spells bytes back at you
- [Control characters](../control_characters/README.md) — the characters that were never meant to draw anything
