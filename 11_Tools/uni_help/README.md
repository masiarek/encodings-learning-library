# `uni -h`, line by line

**Level:** 201 · for anyone who has run `uni -h` and wanted every word on it explained

**One line:** `uni`'s help screen is a map of what a character *has* — one number in five notations, three byte spellings, three escape formats, and a list of facts that can only be looked up in somebody's table — so this page reads it line by line, links each keyword to the page here that explains it, and ends with five places where the screen and the program disagree.

[`uni`](../uni/README.md) has no man page — on a Homebrew install `man uni` answers *No manual entry for uni* — so this screen is the documentation on your machine. It is also a better tour of this library than it has any right to be: nearly every word on it is the subject of a page somewhere here. Below is the whole screen, verbatim, in six pieces, each followed by what its words mean and where to read more. It is reproduced from `uni` 2.9.0, © Martin Tournoij, under the [MIT licence ↗](https://github.com/arp242/uni/blob/main/LICENSE).

## What prints it

`uni -h`, `uni --help` and `uni help` print the same 222 lines, byte for byte, on standard output, and exit 0. `uni` with no arguments prints a 20-line summary instead — each flag and each command on one line — and ends by pointing at `uni help`. The only thing that changes with *where* the screen goes is emphasis. To a terminal, the three headings `Flags:`, `Commands:` and `Format:` arrive wrapped in `ESC[1m` … `ESC[0m`, the bold escape; through a pipe they arrive plain. Strip those six escape sequences, and the carriage returns the terminal driver adds, and the two are the same 10,693 bytes — so `uni -h | less` loses the bold and nothing else. That is the program asking [whether its standard output is a terminal](../../06_Terminal/pipe_is_not_a_terminal/README.md) — the only thing that differed between the two runs — and changing as little as it can on the answer.

## Usage and flags

```text title="Measured 2026-09-10 — uni -h, uni 2.9.0 (Homebrew), macOS 26.6.2. Verbatim, in six pieces split at its own headings; only the blank line at each split is dropped. Not machine-checked: neither CI runner ships uni."
Usage: uni [command] [flags]

uni queries the unicode database. https://github.com/arp242/uni

Flags:
    Flags can appear anywhere; "uni search euro -c" and "uni -c search euro"
    are identical. Use "uni search -- -c" if you want to search for "-c".

    -f, -format    Columns to print and their formatting; see Format section
                   below for details.

    -a, -as        How to print the results: list (default), json, or table.

                     json    The columns listed in -format are included,
                             ignoring formatting flags. Use "-format all" to
                             include all columns.
                     table   Output as table; instead of listing the codepoints
                             on every line. This ignores the -format flag.

    -c, -compact   More compact output; don't print header, "no matches", etc.
                   For json output it uses minified output, and for table it
                   has less padding.

    -r, -raw       Don't use graphical variants for control characters and
                   don't add ◌ (U+25CC) before combining characters.

    -p, -pager     Output to $PAGER.

    -o, -or        Use "or" when searching: match if at least one parameter
                   matches, instead of only when all parameters match.

    -q, -quiet     Backwards-compatible alias for -c/-compact.
    -j, -json      Backwards-compatible alias for -as json
```

| On the screen | What it means | Read more |
|---|---|---|
| `the unicode database` | `uni` carries its **own** copy of the Unicode Character Database — `uni version` says *Unicode 17.0* — rather than asking the operating system or Python for one | [The table has a version](../../02_Characters/the_table_has_a_version/README.md) |
| `Flags can appear anywhere` | options may come after the command; a lone `--` ends them, which is how you search for the text `-c` | |
| `-f, -format` | which columns to print, and how wide | [Format, below](#format-the-column-mini-language) |
| `-a, -as` · `json` | the same columns as data; `-format all` puts in every column there is — including one, `script`, that [the placeholder list never mentions](#one-column-the-list-leaves-out) | |
| `table` | code points sixteen to a row, each row labelled with its last hex digit replaced by `x` (`U+004x`) — a hex dump's layout, with a character in each cell | [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) |
| `-c, -compact` | no header and no *no matches* — the form every fence on [the `uni` page](../uni/README.md) uses | |
| `-r, -raw` · `graphical variants for control characters` | an invisible character is drawn as a visible stand-in from Unicode's Control Pictures block, so a TAB comes out as `␉` U+2409 — three bytes that are not the byte you asked about. `-r` prints the real one | [Control characters](../../02_Characters/control_characters/README.md) |
| `◌ (U+25CC) before combining characters` | DOTTED CIRCLE, the base every Unicode chart draws a combining mark on, so the mark has something to sit on other than the column before it | [The use that saves an afternoon](../uni/README.md#the-use-that-saves-an-afternoon) |
| `-p, -pager` | send the output through `$PAGER` — `less`, usually | |
| `-o, -or` | `search` ANDs its words unless told otherwise | |
| `-q` · `-j` | older spellings of `-c` and `-as json`, kept so old scripts still work | |

The stand-in is easiest to see as bytes, and `search`'s AND is easiest to see by breaking it:

```text title="Measured 2026-09-10 — uni 2.9.0, macOS 26.6.2."
$ uni identify -c "$(printf '\t')" | head -c 5 | xxd
00000000: 27e2 9089 27                             '...'
$ uni identify -c -r "$(printf '\t')" | head -c 3 | xxd
00000000: 2709 27                                  '.'
$ uni search euro pound
uni: no matches
$ uni search -or euro pound -c | head -2
'#'  U+0023  35     23          &num;      NUMBER SIGN [pound sign, hashtag, hash, crosshatch, octothorpe]
'£'  U+00A3  163    c2 a3       &pound;    POUND SIGN [pound sterling, Irish punt, lira, etc.]
```

`e2 90 89` is U+2409 SYMBOL FOR HORIZONTAL TABULATION and `09` is the tab itself; a character that draws nothing at all, such as U+200D ZERO WIDTH JOINER, gets `␣` U+2423 OPEN BOX instead. *no matches* goes to standard error with exit status 1, so a script can test for it. And `-or` found NUMBER SIGN for *pound* through one of its aliases, *pound sign*: `search` reads the bracketed words as well as the names.

## The commands

### list, identify, search and print

```text title="uni -h, continued — verbatim."
Commands:
    list [query]     Show an overview of blocks, categories, scripts,
                     properties, planes, or unicode versions. Every name can be
                     abbreviated (i.e. "b" for "block"). Use "all" to show
                     everything.

    identify [text]  Identify all the characters in the given arguments.

    search [query]   Search description for any of the words.

    print [query]    Print characters. The query can be any of the following:

                       Codepoint   Specific codepoint, in number formats:
                                     hexadecimal   U+20, U20, 0x20, x20, 20
                                     decimal       0d32
                                     octal         0o40, o40
                                     binary        0b100000

                       Range       Range of codepoints, as "start-end" or
                                   "start..end", using the same notation as
                                   Codepoints. These are all identical:

                                      U+2042..U+2050
                                      U+2042-U+2050
                                      2042..2050
                                      '0o20102 - 0d8272'

                       UTF-8       UTF-8 byte sequence, optionally separated by
                                   any combination of '0x', '-', '_', or spaces.
                                   For example these are all U+20AC (€):

                                     utf8:e282ac
                                     utf8:0xe20x820xac
                                     'utf8:e2 82 ac'
                                     utf8:0xe2-0x82_0xac

                       Category    Prefix with "category:", "cat:", or "c:".
                                   Both the long as short name can be used.

                       Block       Prefix with "block:" or "b:".

                       Property    Prefix with "property:", "prop:", or "p:".

                       all         All codepoints we know about.

                    The category, block, and property can be abbreviated, and
                    non-letter characters can be omitted. These are identical:

                        block:'Block Drawing'     block:box

                    As are these:

                        cat:Dash_Punctuation      cat:dashpunctuation

                    If nothing of the above matches it will try to find by
                    block, category, or property, giving an error if more than
                    one matches.
```

| On the screen | What it means | Read more |
|---|---|---|
| `list` · `blocks` | a block is a named run of code points — *Dingbats*, *Currency Symbols* — and knowing a couple of dozen is how people read a code point on sight | [Unicode code points](../../02_Characters/unicode_code_points/README.md#the-blocks-are-the-whole-trick) |
| `categories` · `properties` | every code point has exactly one General_Category (`Lu`, `Nd`, `So`…) and a set of yes-or-no properties (`White_Space`, `Bidi_Control`…) — what a regex's `\p{…}` asks about | ["Supports Unicode" is a level, not a yes](../../02_Characters/what_a_regex_matches/README.md) |
| `scripts` | the writing system a character belongs to — `Latin`, `Cyrillic`, or `Common` for what they share | [The standard library has no `script()`](../../02_Characters/confusables_and_scripts/README.md#the-standard-library-has-no-script) |
| `planes` | the code space in seventeen slices of 65,536 (listed below); everything above plane 0 needs a surrogate pair in UTF-16 | [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) |
| `unicode versions` | each release and its date, from 1.1 (June 1993) to 17.0 — what `%(unicode)` reports for each character | |
| `identify [text]` | characters in, one row of facts per character | [`uni` — the character's name](../uni/README.md) |
| `search [query]` | words in, characters out — the direction no dump tool can go | [It goes both ways](../uni/README.md#it-goes-both-ways) |
| `hexadecimal U+20, U20, 0x20, x20, 20` | five spellings of one number, and the last is the trap: **a bare number is hexadecimal**, so `uni print 20` is SPACE and twenty is `0d20` (below) | [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md#the-spellings), [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| `decimal 0d32` · `octal 0o40` · `binary 0b100000` | thirty-two, in bases 10, 8 and 2 | [A character is a number](../../02_Characters/a_character_is_a_number/README.md), [the octal row](../../01_Bits_and_Bytes/counting_in_hex/README.md#a-note-on-the-octal-row), [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| `Range` · `U+2042..U+2050` | a run of code points, which is all a block is | |
| `UTF-8` · `utf8:e282ac` | bytes in, code point out — the `UTF8` column read backwards, which is what decoding is | [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md#decoding-is-the-same-table-backwards) |
| `Category` · `cat:` | one General_Category, by long name or short: `cat:Sc` lists the currency signs | |
| `Block` · `block:box` | one block, and names may be abbreviated: `box` finds *Box Drawing* | |
| `Property` · `prop:` | one yes-or-no property: `prop:bidicontrol` lists the characters that can reorder a line on screen | [What you see is not what runs](../../12_Adversarial/trojan_source/README.md) |
| `all` | everything in the table — 40,575 lines here — stored the way Unicode's own `UnicodeData.txt` stores it, so its 20 long ranges (the CJK ideographs, the Hangul syllables, Tangut, the surrogates, the private-use areas) come out as two rows each, a `First>` and a `Last>`, rather than one row per character | |

Two of those, measured:

```text title="Measured 2026-09-10 — uni 2.9.0, macOS 26.6.2."
$ uni list planes
U+0000  - U+FFFF    Basic Multilingual Plane
U+10000 - U+1FFFF   Supplementary Multilingual Plane
U+20000 - U+2FFFF   Supplementary Ideographic Plane
U+30000 - U+3FFFF   Tertiary Ideographic Plane
U+40000 - U+DFFFF   Unassigned
U+E0000 - U+EFFFF   Supplementary Special-purpose Plane
U+F0000 - U+10FFFF  Supplementary Private Use Area planes
$ uni print 20 0d20 -c
'␔'  U+0014  20     14          &#x14;     DEVICE CONTROL FOUR
' '  U+0020  32     20          &#x20;     SPACE
```

Seven rows for seventeen planes, since planes 4 to 13 are one *Unassigned* row and 15 and 16 share another. And `print`'s rows come out in code point order, not the order you typed them: decimal twenty is a control character, drawn as its Control Picture `␔`, and `20` on its own is SPACE.

### emoji

```text title="uni -h, continued — verbatim."
    emoji [query]    Search emojis. The query is matched on the emoji name and
                     CLDR data.

                     The CLDR data is a list of keywords. For example 🙏
                     (folded hands) contains "ask, high 5, high five, please,
                     pray, thanks", which represents the various scenarios in
                     which it's used.

                     You can use <prefix>:query to search in specific fields:

                         group: g:    Group and subgroup
                         name:  n:    Emoji name
                         cldr:  c:    CLDR data

                     The query parameters are AND'd together, so this:

                         uni emoji smiling g:cat-face

                     Will match everything in the cat-face group with smiling
                     in the name. Use the -or flag to change this to "cat-face
                     group OR smiling in the name".

                     Use "all" to show all emojis.

                     Modifier flags, both accept a comma-separated list:

                         -g, -gender   Set the gender:
                                           p, person, people
                                           m, man, men, male
                                           f, female, w, woman, women

                         -t, -tone     Set the skin tone modifier:
                                           n,  none
                                           l,  light
                                           ml, mediumlight, medium-light
                                           m,  medium
                                           md, mediumdark, medium-dark
                                           d,  dark

                     Use "all" to include all combinations; the default is to
                     include no skin tones and the "person" gender.

                     Note: emojis may not be accurately copied by select & copy
                     in terminals. It's recommended to copy to the clipboard
                     directly by piping to e.g. xclip.
```

| On the screen | What it means | Read more |
|---|---|---|
| `The CLDR data is a list of keywords` | CLDR is the Unicode Consortium's *Common Locale Data Repository* — locale data for hundreds of languages, from how a date is written to how a language sorts, and for each emoji a short name and a list of search keywords | [CLDR ↗](https://cldr.unicode.org/), [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| `group:` · `name:` · `cldr:` | where a query looks. The groups and subgroups are the headings of Unicode's own emoji list — *People & Body*, *person-role* | [emoji-test.txt ↗](https://unicode.org/Public/emoji/latest/emoji-test.txt) |
| `-g, -gender` · `-t, -tone` | many emoji are **several code points** drawn as one picture — a person, a skin-tone modifier, a ZERO WIDTH JOINER, an object — and these choose the person and the modifier | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| `may not be accurately copied by select & copy` | do not copy an emoji out of the terminal window; send it to the clipboard instead — `pbcopy` on a Mac, `xclip` on X11 | [Typing a character you cannot type](../typing_a_character/README.md) |

```text title="Measured 2026-09-10 — uni 2.9.0, macOS 26.6.2."
$ uni emoji -tone medium -gender f -f '%(cpoint)  %(name)' firefighter
CPoint  Name
U+1F469 U+1F3FD U+200D U+1F692  woman firefighter: mediun skin tone
```

Four code points — WOMAN, EMOJI MODIFIER FITZPATRICK TYPE-4, ZERO WIDTH JOINER, FIRE ENGINE — and one picture. The name is the part to distrust: Unicode's emoji-test.txt calls this *woman firefighter: medium skin tone*, and `mediun` is `uni`'s own, from a typo in [the table of tone names it builds these from ↗](https://github.com/arp242/uni/blob/e242227ab4b90fb7db775f0d15aeb5b30245e1cc/unidata/emoji.go#L263). Only the medium tone has it.

## Format: the column mini-language

```text title="uni -h, continued — verbatim."
Format:
    You can use the -format or -f flag to control what to print; placeholders
    are in the form of %(name) or %(name flags), where "name" is a column name
    and "flags" are some flags to control how it's printed.

    %name is a shortcut for %(name l:auto).

    If the format string starts with "+" it will prepend the format string with
    the character, codepoint, and name. This is an easy way to quickly list
    properties yo're interested in. For example, "-f +%unicode to quickly get
    the Unicode version it was introduced. Otherwise it works exactly as below.

    The special value "all" includes all columns; this is useful especially
    with json if you want to get all information uni knows about a codepoint
    or emoji.

    Flags:
        %(name l:5)     Left-align and pad with 5 spaces
        %(name l:auto)  Left-align and pad to the longest value
        %(name r:5)     Right-align and pad with 5 spaces (also supports auto)
        %(name q)       Quote with single quotes, excluding any padding
        %(name q:")     Quote with "
        %(name q:[:],)  Quote with [ at the start, and ], at the end
        %(name Q)       Quote like q, but omit the quotes if the value is empty
        %(name Q:[:])
        %(name t)       Trim this column if it's longer than the screen width
        %(name f:C)     Fill this column with character C instead of space when
                        aligning; useful for numbers: %(bin r:auto f:0)
        %(name h)       Don't include in header.

    Placeholders that work for all commands:
        %(tab)           A literal tab when outputting to a terminal, or four
                         spaces if not; this helps with aligning emojis in
                         terminals, but some tools like dmenu don't work well
                         with tabs.
```

| On the screen | What it does |
|---|---|
| `%(name)` | one column, by name — the names are [the placeholders, below](#the-placeholders) |
| `%(name l:5)` · `%(name r:5)` | left- or right-align in five cells |
| `l:auto` | pad to the longest value in the whole output — so `uni` has to see the entire column before it prints the first row |
| `q` · `q:"` · `q:[:],` | quote with `'`, with `"`, or with any start and end strings you give |
| `Q` | quote, but leave an empty value empty |
| `t` | trim the column to the screen width |
| `f:C` | fill with the character C instead of a space: `%(bin r:auto f:0)` zero-pads the binary column |
| `h` | print the column but leave it out of the header |
| `%name` | short for `%(name l:auto)`, since 2.7.0 |
| a leading `+` | prepend the character, code point and name: `uni identify -f +'%unicode %plane' é` |
| `all` | every column there is; most useful with `-as json` |
| `%(tab)` | a real TAB when standard output is a terminal and four spaces when it is not — measured both ways, the terminal half under `script(1)` |

If that looks familiar, it is Python's format mini-language under other letters; [the bridge below](#if-you-are-coming-from-python-or-abap) spells it out.

## The placeholders

```text title="uni -h, continued — verbatim."
    Placeholders for identify, search, and print:
        Placeholder      Description                   Example
        -----------      -----------                   -------
        %(char)          The literal character         ✓
                         (also see -raw flag)
        %(cpoint)        As codepoint                  U+2713
        %(hex)           As hex                        2713
        %(oct)           As octal                      23423
        %(bin)           As binary (little-endian)     10011100010011
        %(dec)           As decimal                    10003
        %(utf8)          As UTF-8                      e2 9c 93
        %(utf16le)       As UTF-16 LE (Windows)        13 27
        %(utf16be)       As UTF-16 BE                  27 13
        %(html)          HTML entity (name or hex)     &check;
        %(xml)           XML entity                    &#x2713;
        %(json)          JSON escape                   \u2713
        %(keysym)        X11 keysym; can be blank      checkmark
        %(digraph)       Vim Digraph; can be blank     OK
        %(name)          Code point name               CHECK MARK
        %(cat)           Category name                 Other_Symbol
        %(block)         Block name                    Dingbats
        %(props)         Properties, separated by ,    Pattern Syntax
        %(plane)         Plane name                    Basic Multilingual Plane
        %(width)         Character width               Narrow
        %(cells)         Number of cells it display    1
                         as, 0, 1, or 2
        %(unicode)       First assigned in Unicode     1.1
        %(wide_padding)  Blank for wide characters,
                         space otherwise; for alignment
        %(aliases)       Alias names                   factorial, bang
        %(refs)          Reference other codepoints,   U+221A, U+1F5F8, U+1FBB1
                         usually similar/alternatives

        The default is:
        %(char q h l:3)%(wide_padding) %(cpoint h l:7) %(dec l:6) %(utf8 l:11) %(html l:10) %(name t) %(aliases t h Q:[:])
```

The *Example* column is meant to be one character's row, ✓ U+2713 CHECK MARK — so the quickest way to read the table is to ask `uni` for that character's every column at once:

```text title="Measured 2026-09-10 — uni 2.9.0, macOS 26.6.2."
$ uni print U+2713 -as json -format all
[{
	"aliases": "",
	"bin":     "10011100010011",
	"block":   "Dingbats",
	"cat":     "Other_Symbol",
	"cells":   "1",
	"char":    "✓",
	"cpoint":  "U+2713",
	"dec":     "10003",
	"digraph": "OK",
	"hex":     "2713",
	"html":    "&check;",
	"json":    "\\u2713",
	"keysym":  "",
	"name":    "CHECK MARK",
	"oct":     "23423",
	"plane":   "Basic Multilingual Plane",
	"props":   "Pattern Syntax",
	"refs":    "U+221A, U+1F5F8, U+1FBB1",
	"script":  "Common",
	"unicode": "1.1",
	"utf16be": "27 13",
	"utf16le": "13 27",
	"utf8":    "e2 9c 93",
	"width":   "narrow",
	"xml":     "&#x2713;"
}]
```

| Placeholder | ✓ gives | Arithmetic, or a table? | Read more |
|---|---|---|---|
| `%(char)` | `✓` | the character itself — its UTF-8 bytes, handed to your terminal to draw | [A character and its bytes on one line](../../06_Terminal/character_and_its_bytes/README.md) |
| `%(cpoint)` | `U+2713` | arithmetic: the number in hex, at least four digits after `U+` | |
| `%(hex)` · `%(dec)` · `%(oct)` | `2713` · `10003` · `23423` | arithmetic: the same number in bases 16, 10 and 8 | |
| `%(bin)` | `10011100010011` | arithmetic, base 2 — and **not** little-endian, whatever the screen says: [a numeral has no byte order](#a-numeral-has-no-byte-order) | [MSB and LSB](../../01_Bits_and_Bytes/counting_in_hex/README.md#msb-and-lsb-the-abbreviation-does-not-say-which) |
| `%(utf8)` | `e2 9c 93` | arithmetic: the UTF-8 encoding | [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) |
| `%(utf16le)` · `%(utf16be)` | `13 27` · `27 13` | arithmetic: UTF-16 in both byte orders — the only columns on the screen that *have* a byte order. *(Windows)* because a Windows `wchar_t` string is UTF-16LE | [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md), [Why UTF-16 stayed](../../09_History/why_utf16_stayed/README.md) |
| `%(html)` | `&check;` | a table, WHATWG's named character references — with the numeric `&#x…;` form for a character that has no name | [the list ↗](https://html.spec.whatwg.org/multipage/named-characters.html) |
| `%(xml)` | `&#x2713;` | arithmetic. The screen says *entity*; XML's own word for `&#x2713;` is a **character reference** — an entity reference is `&name;` | [XML 1.0, §4.1 ↗](https://www.w3.org/TR/xml/#sec-references) |
| `%(json)` | `\u2713` | arithmetic in UTF-16 code units, so above U+FFFF it takes two: `😀` is `\ud83d\ude00` | [The surrogate that leaks into a UTF-8 format](../../03_Encodings/escaping_into_ascii/README.md#the-surrogate-that-leaks-into-a-utf-8-format) |
| `%(keysym)` | *(blank)* | a table, X11's `keysymdef.h` — and `uni`'s copy is [keyed by the wrong number](#the-keysym-column-reads-the-wrong-number) | [The compose key](../typing_a_character/README.md#the-compose-key-a-path-not-a-name) |
| `%(digraph)` | `OK` | a table, RFC 1345's two-letter mnemonics — which is where Vim's default digraphs come from, hence the screen's *Vim Digraph* | [Vim digraphs: the other table](../typing_a_character/README.md#vim-digraphs-the-other-table) |
| `%(name)` | `CHECK MARK` | a table, the UCD — and the one column Unicode promises never to change | [The column no dumper has](../uni/README.md#the-column-no-dumper-has) |
| `%(cat)` | `Other_Symbol` | a table: General_Category, spelled out (`So` for short) | |
| `%(block)` | `Dingbats` | a table, `Blocks.txt` | |
| `%(props)` | `Pattern Syntax` | a table: the yes-or-no properties that are *yes* for this character | |
| `%(plane)` | `Basic Multilingual Plane` | arithmetic for the number — `0x2713 >> 16` is 0 — and a short list for the name | |
| `%(width)` | `narrow` | a table, East_Asian_Width — [printed under the wrong name](#the-width-column-swaps-two-of-its-names) | [The five rulers](../../02_Characters/a_code_point_is_not_a_character/README.md#the-five-rulers) |
| `%(cells)` | `1` | `uni`'s estimate of the terminal columns; the terminal drawing it keeps its own table | |
| `%(unicode)` | `1.1` | a table, the UCD's Age: the release that assigned the character | |
| `%(wide_padding)` | *(a space)* | layout, not data — nothing for a wide character and a space otherwise, so the next column still lines up | |
| `%(aliases)` | *(blank)* | a table: the alias lines of Unicode's `NamesList.txt`. `!` has *factorial, bang*; U+FEFF has *BYTE ORDER MARK, BOM, ZWNBSP*; ✓ has none | [NamesList.txt ↗](https://www.unicode.org/Public/17.0.0/ucd/NamesList.txt) |
| `%(refs)` | `U+221A, U+1F5F8, U+1FBB1` | a table: `NamesList.txt`'s cross-references, its `x` lines — often a look-alike, which makes this the confusables column | [Confusables and scripts](../../02_Characters/confusables_and_scripts/README.md) |

And the emoji placeholders, which describe a sequence rather than a code point:

```text title="uni -h, the end — verbatim."
    Placeholders for emoji:

        %(emoji)       The emoji itself                🧑‍🚒
        %(name)        Emoji name                      firefighter
        %(group)       Emoji group                     People & Body
        %(subgroup)    Emoji subgroup                  person-role
        %(cpoint)      Codepoints                      U+1F9D1 U+200D U+1F692
        %(cldr)        CLDR data, w/o emoji name       firetruck
        %(cldr_full)   Full CLDR data                  firefighter, firetruck

        The default is:
        %(emoji h)%(tab)%name  %(cldr t Q:[:])
```

| Placeholder | What it is |
|---|---|
| `%(emoji)` | the emoji — often several code points |
| `%(name)` | CLDR's short name, in lower case: `firefighter`. Not a Unicode Name — those belong to single code points, and the firefighter is three |
| `%(group)` · `%(subgroup)` | the emoji-test.txt headings it sits under |
| `%(cpoint)` | every code point in the sequence: `U+1F9D1 U+200D U+1F692` is ADULT, ZERO WIDTH JOINER, FIRE ENGINE |
| `%(cldr)` · `%(cldr_full)` | the search keywords, without and with the name |

## Arithmetic, or somebody's table

Sort the placeholders by where their answers come from and the list splits in two.

**Arithmetic on the one number:** `cpoint`, `hex`, `dec`, `oct`, `bin`, `utf8`, `utf16le`, `utf16be`, `xml`, `json`, and the plane's number. Every program on every machine, at every Unicode version, gives the same answers — which is why [the Python example](#in-python) can recompute them and record them as an answer key, and why its U+2713 column matches `uni`'s JSON above, value for value.

**A row in a table somebody publishes:** `name`, `cat`, `block`, `props`, `script`, `unicode` and `width` from the Unicode Character Database; `aliases` and `refs` from its names list; `html` from WHATWG; `keysym` from X11; `digraph` from RFC 1345; the emoji columns from CLDR. Each of those tables has an owner and an edition, and a program printing one holds a copy of one edition — which is the whole argument of *The table has a version*, and why that page is careful about which lookups it lets into an answer key.

Every wrong *value* in the next section is in the second list. The first list's only problem is a word.

## Five places the screen and the program disagree

A help screen is prose, and nothing checks prose against the program it describes — [What the page does not say](../../13_Documentation/what_the_page_does_not_say/README.md) makes that case for man pages, and `uni -h` bears it out. All five were measured on `uni` 2.9.0. The first two are bugs in the data rather than the prose, found in `uni`'s source and still there on its main branch at commit `e242227` (2026-02-23).

### The width column swaps two of its names

East_Asian_Width has six values, and two of them have names that are easy to swap: **Na** is *Narrow* — an East Asian narrow form, ASCII being the classic case — and **N** is *Neutral*, a character no East Asian legacy character set ever had ([UAX #11 ↗](https://www.unicode.org/reports/tr11/)). `uni` prints each under the other's name:

```text title="Measured 2026-09-10 — uni 2.9.0, macOS 26.6.2."
$ uni print U+0041 U+2713 U+00E9 U+65E5 -c -f '%(cpoint l:7) %(width l:9) %(cells)'
U+0041  neutral   1
U+00E9  ambiguous 1
U+2713  narrow    1
U+65E5  wide      2
```

`A` is Narrow and ✓ is Neutral — [section 5 of the Python example](#in-python) asks Python's own table and gets `Na` and `N`. Across the whole table the swap is exact: every character the UCD calls Na, and no other, comes out *neutral*; every N comes out *narrow*; the other four values agree.

```bash
uni print all -c -f '%(hex) %(width)' | python3 -c '
import sys, unicodedata as u, collections
seen, skipped = collections.Counter(), 0
for line in sys.stdin:
    h, w = line.split()
    c = chr(int(h, 16))
    if u.category(c) == "Cn":
        skipped += 1
    else:
        seen[w, u.east_asian_width(c)] += 1
for (w, e), n in sorted(seen.items()):
    print(f"uni {w:<9}  UCD {e:<2}  {n:>6}")
print(f"skipped, unassigned in this Python (UCD {u.unidata_version}): {skipped}")
'
```

```text title="Measured 2026-09-10 — uni 2.9.0 against Python 3.14.2's unicodedata, macOS 26.6.2."
uni ambiguous  UCD A     1277
uni full       UCD F      104
uni half       UCD H      123
uni narrow     UCD N    31327
uni neutral    UCD Na     111
uni wide       UCD W     7170
skipped, unassigned in this Python (UCD 16.0.0): 463
```

The cause is two lines in the generator that reads Unicode's `EastAsianWidth.txt` ([source ↗](https://github.com/arp242/uni/blob/e242227ab4b90fb7db775f0d15aeb5b30245e1cc/unidata/gen/codepoints.awk#L116-L121)):

```text title="unidata/gen/codepoints.awk, lines 116–121, at commit e242227 — indentation trimmed"
case "A":  width = "WidthAmbiguous"; break
case "F":  width = "WidthFullWidth"; break
case "H":  width = "WidthHalfWidth"; break
case "N":  width = "WidthNarrow";    break
case "Na": width = "WidthNeutral";   break
case "W":  width = "WidthWide";      break
```

`%(cells)` survives it, since both kinds take one column. What breaks is anything that reads the word: grep `uni print all` for *narrow* and you get tens of thousands of Neutral characters and not one of the 111 that are Narrow. Reported upstream as [arp242/uni#61 ↗](https://github.com/arp242/uni/issues/61).

### The keysym column reads the wrong number

X11 gives every key meaning a number, and `keysymdef.h` lists each one with the Unicode character it stands for in a comment ([keysymdef.h ↗](https://gitlab.freedesktop.org/xorg/proto/xorgproto/-/blob/master/include/X11/keysymdef.h)). For Latin-1 the keysym's number *is* the code point — `XK_eacute` is `0x00e9`, and so is `é`. Everywhere else it is not: `XK_zabovedot` is `0x01bf` and stands for U+017C `ż`. `uni` keys its table by the keysym's number and looks it up by the code point, so it is right exactly where the two coincide:

```text title="Measured 2026-09-10 — uni 2.9.0; keysymdef.h from xorgproto's main branch."
$ uni print U+00E9 U+017C U+2713 U+01A1 -c -f '%(cpoint l:7) %(keysym l:9) %(name)'
U+00E9  eacute    LATIN SMALL LETTER E WITH ACUTE
U+017C            LATIN SMALL LETTER Z WITH DOT ABOVE
U+01A1  Aogonek   LATIN SMALL LETTER O WITH HORN
U+2713            CHECK MARK
$ grep -E 'XK_(eacute|Aogonek|zabovedot|checkmark) ' keysymdef.h
#define XK_eacute                        0x00e9  /* U+00E9 LATIN SMALL LETTER E WITH ACUTE */
#define XK_Aogonek                       0x01a1  /* U+0104 LATIN CAPITAL LETTER A WITH OGONEK */
#define XK_zabovedot                     0x01bf  /* U+017C LATIN SMALL LETTER Z WITH DOT ABOVE */
#define XK_checkmark                     0x0af3  /* U+2713 CHECK MARK */
```

`ż` and `✓` come back blank although X11 names both, and characters with no keysym at all get somebody else's: `ơ` U+01A1 is given `Aogonek` — which is `Ą`'s — because `XK_Aogonek` happens to be `0x01a1`. Across the whole header, 1,633 code points have a one-to-one keysym (27 more appear only in parentheses, the header's mark for a mapping that is not one-to-one). `uni` names all 192 whose keysym number equals the code point — Latin-1 and the euro, six of them by another name for the same number, such as the deprecated `quoteright` for the apostrophe — and none of the other 1,441 correctly: 1,307 blank and 134 wrong. The parser keeps the third field of each `#define` and never reads the comment ([source ↗](https://github.com/arp242/uni/blob/e242227ab4b90fb7db775f0d15aeb5b30245e1cc/unidata/gen/codepoints.awk#L65-L70)):

```text title="unidata/gen/codepoints.awk, lines 65–70, at commit e242227 — indentation trimmed"
while (getline line <".cache/keysymdef.h" > 0) {
    if (match(line, "^#define XK") == 0)
        continue
    split(line, fields, " ")
    all_sym[strtonum(fields[3])] = gensub("^XK_", "", 1, fields[2])
}
```

A blank in that column is therefore not evidence of anything. X11's Polish keyboard layout sends `zabovedot` and `lstroke` (`symbols/pl` in xkb-data 2.41), so both Polish letters have keys of their own; it is `uni`'s column that does not know them. Reported upstream as [arp242/uni#62 ↗](https://github.com/arp242/uni/issues/62).

### A numeral has no byte order

The screen glosses `%(bin)` as *As binary (little-endian)*. What it prints for ✓, `10011100010011`, is the ordinary numeral, most significant digit first — exactly what `format(0x2713, 'b')` writes. Byte order describes how the *bytes* of a multi-byte number are laid out in memory or on a wire, and a numeral on a screen has none. If a word must be attached, the numeral reads like the big-endian bytes with the leading zeros dropped — [section 2 of the Python example](#in-python) prints all three side by side. The columns on this screen that really are little-endian are `%(utf16le)`, and they say so in their name.

### The Example column is not one character's row

Every example in the placeholder list is ✓'s value but three. *factorial, bang* are the aliases of `!` U+0021, and ✓ has none. *checkmark* is X11's keysym for ✓, which `uni` itself never prints, as above. And *Narrow* is the width label with the swap applied, in a capital the program never uses.

```text title="Measured 2026-09-10 — uni 2.9.0, macOS 26.6.2."
$ uni print U+0021 U+2713 -c -f '%(cpoint l:7) %(aliases)'
U+0021  factorial, bang
U+2713
```

### One column the list leaves out

`-format all` gives 25 columns and the placeholder list documents 25 — but not the same 25. The JSON above carries `script` (✓ is *Common*), which the list never mentions, and the list carries `%(wide_padding)`, which is layout and so has no place in the JSON. `%(script)` works like any other placeholder; it is simply [written down nowhere](../../13_Documentation/what_the_page_does_not_say/README.md#a-flag-that-works-and-is-written-down-nowhere).

Three smaller slips are the screen's own and not this page's transcription: *yo're* for *you're*, a `"-f +%unicode` whose quote never closes, and — in `emoji`'s output rather than its help — `mediun`.

## In Python

Every arithmetic column is one expression in Python, and `unicodedata` has three of the table columns — enough to check `uni` against, and the thing to reach for on a machine where you cannot install it.

<!-- output:uni_help_py -->
*Verified output of [`uni_help_py.py`](examples/uni_help_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE COLUMNS A PENCIL CAN FILL IN
------------------------------------------------------------------------
   placeholder    U+2713, the help's    U+1F600, above U+FFFF
   %(cpoint)      U+2713                U+1F600
   %(hex)         2713                  1f600
   %(dec)         10003                 128512
   %(oct)         23423                 373000
   %(bin)         10011100010011        11111011000000000
   %(utf8)        e2 9c 93              f0 9f 98 80
   %(utf16le)     13 27                 3d d8 00 de
   %(utf16be)     27 13                 d8 3d de 00
   %(xml)         &#x2713;              &#x1f600;
   %(json)        \u2713                \ud83d\ude00
   plane number   0                     1

   Nothing above came out of a table. Every value is the one number
   rewritten -- in another base, as UTF-8 or UTF-16 bytes, or as an
   escape -- so no Unicode version and no machine can change it. The
   last row is the plane's number, cp >> 16; the plane's NAME, which is
   what %(plane) prints, has to come from a list of names.

2. %(bin) IS A NUMERAL, AND A NUMERAL HAS NO BYTE ORDER
------------------------------------------------------------------------
   U+2713 in base 2              10011100010011
   as two bytes, big-endian      00100111 00010011   27 13
   as two bytes, little-endian   00010011 00100111   13 27

   The first row is the ordinary numeral, most significant digit
   first. Set beside the other two it is the big-endian bytes with the
   leading zeros dropped, and nothing like the little-endian ones.
   Byte order describes how a number's BYTES are laid out in memory or
   on a wire; a numeral written on a screen has no bytes to order.

3. ABOVE U+FFFF, JSON SPENDS TWO ESCAPES AND XML SPENDS ONE
------------------------------------------------------------------------
   0x1f600 - 0x10000             = 0xf600
   0xd800 + (0xf600 >> 10)       = 0xd83d
   0xdc00 + (0xf600 & 0x3ff)     = 0xde00
   json.dumps(chr(0x1f600))      = "\ud83d\ude00"
   the XML reference             = &#x1f600;

   The XML reference names the code point, however many digits that
   takes. JSON's \u escape names one UTF-16 code unit -- four hex
   digits, no more -- so a character above U+FFFF is written as its
   surrogate pair: two escapes, and still nothing but arithmetic.

4. A BARE NUMBER IS HEX TO uni AND DECIMAL TO PYTHON
------------------------------------------------------------------------
   uni print 20     int('20', 16) = 32  U+0020  SPACE
   uni print 0d20   int('20', 10) = 20  U+0014  (no Name: name() raises ValueError)

   Python's int() reads decimal unless told otherwise; uni reads hex
   unless told otherwise (0d decimal, 0o octal, 0b binary). U+0014 is
   a control character, and controls have no Name -- DEVICE CONTROL
   FOUR is one of its aliases, which lookup() accepts even though
   name() never returns it:
   unicodedata.lookup('DEVICE CONTROL FOUR') -> U+0014

5. THE COLUMNS THAT NEED A TABLE, AND WHICH ONES PYTHON HAS
------------------------------------------------------------------------
   %(name)     unicodedata.name()               CHECK MARK
   %(cat)      unicodedata.category()           So
   %(width)    unicodedata.east_asian_width()   N
   %(html)     html.entities.html5              &check;  &checkmark;
   %(block)    unicodedata.block()              exists: False
   %(script)   unicodedata.script()             exists: False
   %(unicode)  unicodedata.age()                exists: False
   %(aliases), %(refs)  NamesList.txt, which Python does not ship
   %(keysym)            X11's keysymdef.h: not a Unicode table at all
   %(digraph)           RFC 1345's mnemonics: not a Unicode table at all

   EAST_ASIAN_WIDTH: THE TABLE'S LETTERS, AND WHAT EACH ONE MEANS
   U+0041  Na  Narrow -- an East Asian narrow form           A
   U+2713  N   Neutral -- never in an East Asian legacy set  ✓
   U+00E9  A   Ambiguous                                     é
   U+65E5  W   Wide                                          日

   A is Na and CHECK MARK is N. The letters are hard to confuse; the
   words Narrow and Neutral are not, which is why it is worth reading
   the letter whenever a tool prints only the word.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** The placeholders are Python's own old `%`-formatting — `'%(name)s' % row` is the same brackets with a conversion letter on the end — and the flags are the format-spec mini-language under other letters: `%(dec r:6 f:0)` is `f'{dec:0>6}'`, and `l:5` is `<5`. The one flag with no one-line equivalent is `l:auto`, which has to see the whole column before it prints the first row; in Python that is `max(len(v) for v in column)` first and the loop second. And the three spellings of help are a choice somebody made: `argparse` gives you `-h` and `--help` for nothing, and never a `help` subcommand.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* The column mini-language is the string template's formatting options under other names: `|{ lv_dec WIDTH = 6 ALIGN = RIGHT PAD = '0' }|` is `%(dec r:6 f:0)`. The arithmetic half is all within reach — the code point from the character's UCS-2 value, the byte columns from `cl_abap_conv_codepage` once you name the code page, as any interface should. The table half is not: the ABAP runtime ships no Unicode Character Database, so a name, a category or a block means an external table — which is the case for having `uni` on the machine you debug from.

## Try it

1. `uni identify -f +'%unicode %block %script' "$(pbpaste)"` on whatever is in your clipboard: which Unicode release each character arrived in, where it lives, and which writing system it belongs to. On Linux, `xclip -o`.
2. Take the strangest character in a bug report or a log and run `uni print -as json -format all` on its code point — every column at once, as data you can paste into the ticket.
3. Find a multi-byte sequence in a hex dump of one of your own files and hand the bytes to `uni print utf8:…` — the code point from the bytes, with no arithmetic.
4. `uni emoji -tone all -f '%(cpoint)  %(name)'` on an emoji you send every day, and count the code points in each row.
5. `uni print all -c -f '%(width)' | sort | uniq -c`, then reread [the width section](#the-width-column-swaps-two-of-its-names) before you believe the `narrow` row.

## Practice

**Predict the row, then name the tables.** Without running `uni`, write down what this prints:

```bash
uni print U+20AC -c -f '%(cpoint) %(dec) %(oct) %(bin) %(utf8) %(utf16be) %(xml)'
```

Then pick two placeholders whose value for `€` you could not have worked out on paper, and say whose table each one comes from. Last, the trap: which character does `uni print 100` print, and which does `uni print 0d100`?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:uni_help_kata_py -->
*Verified output of [`uni_help_kata_py.py`](examples/uni_help_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE ROW, WITH A PENCIL
   U+20AC 8364 20254 10000010101100 e2 82 ac 20 ac &#x20ac;

   %(cpoint)   U+20AC           the number in hex, at least four digits
   %(dec)      8364             2*4096 + 0*256 + 10*16 + 12*1
   %(oct)      20254            the same number in base 8
   %(bin)      10000010101100   0010 0000 1010 1100, leading zeros dropped
   %(utf8)     e2 82 ac         1110 0010  10 000010  10 101100
   %(utf16be)  20 ac            one 16-bit unit (it is below U+FFFF), high byte first
   %(xml)      &#x20ac;         the hex again, between &#x and ;

THE COLUMNS NO PENCIL FILLS IN
   %(name)     EURO SIGN        Unicode's Name property -- unicodedata.name()
   %(cat)      Sc               General_Category -- unicodedata.category()
   %(html)     &euro;           WHATWG's named references -- html.entities.html5
   %(keysym)   EuroSign         X11's keysymdef.h
   %(digraph)  =e               RFC 1345 -- except that the RFC has no euro sign

   Any two of these answer the question. Each is a row in somebody's
   table, with an owner and an edition -- the first block has neither.

A BARE NUMBER IS HEX TO uni
   uni print 100     int('100', 16) = 256  U+0100  Ā  LATIN CAPITAL LETTER A WITH MACRON
   uni print 0d100   int('100', 10) = 100  U+0064  d  LATIN SMALL LETTER D

   The same three digits, two characters. The prefix is the only thing
   that says which number you meant.
```
<!-- /output -->

</details>

## See also

- [`uni` — the character's name](../uni/README.md) — the commands in use, and why the name is the column that matters
- [Typing a character you cannot type](../typing_a_character/README.md) — the keysym, digraph and HTML tables side by side
- [The table has a version](../../02_Characters/the_table_has_a_version/README.md) — why the second half of the placeholder list is the half to be careful with
- [What the page does not say](../../13_Documentation/what_the_page_does_not_say/README.md) — documentation measured against the program it describes
