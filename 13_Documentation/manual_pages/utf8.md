# `utf8(5)` and `utf-8(7)`: one encoding, two pages, twenty years apart

**Level:** reference · for anyone who has typed `man 5 utf8` or `man 7 utf-8` and wanted every word on it explained

**One line:** The BSD page from 2004 and the Linux page from 2024 print the same six-row byte table, cite different RFCs, and are both right about the machine they ship on: this Mac's `iconv` still decodes a six-byte sequence, and Ubuntu's refuses everything past four.

**The pages:** [`utf8(5)`](raw/macos/utf8.5.txt) (macOS, dated April 7, 2004) · [`utf2(5)`](raw/macos/utf2.5.txt) (macOS, October 11, 2002) · [`utf-8(7)`](raw/linux/utf-8.7.txt) (Linux man-pages 6.7, 2024-03-14) · [`unicode(7)`](raw/linux/unicode.7.txt) (Linux man-pages 6.7, 2024-01-28). Dumped 2026-09-13 by [`dump.sh`](dump.sh) and [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

A character encoding is a file format, so BSD files it in **section 5** beside `tar(5)` and `magic(5)`, one page per encoding, and `utf8(5)` is the one for UTF-8. It is forty lines long. It is not a tutorial: it is the byte table, the shortest-form rule stated as a security property, and a reading list, written for the person implementing the `LC_CTYPE` half of a locale. The `SYNOPSIS` says so in its own way: `ENCODING "UTF-8"` is not a command but the first line of a locale source file for `mklocale(1)`, the compiler that turned such a file into `/usr/share/locale/*/LC_CTYPE`. That is what the page is *for*: it documents the encoding as the thing the C library's [`multibyte(3)`](multibyte.md) functions implement when the locale names it.

Linux files the same subject in **section 7**, miscellany, under a different spelling, and writes it as an essay: `utf-8(7)` explains *why* the encoding has the shape it has, and `unicode(7)` beside it explains the character set the encoding is *of*. Neither machine has the other's page. `man utf8` on Ubuntu and `man utf-8` on a Mac both answer *No manual entry*, which is the first reason nobody reads either.

Two pages, two decades apart, and the byte table on both has six rows. That is the lesson [A page has a date](../a_page_has_a_date/README.md) is built on, and this page is where the dated words themselves are explained.

## The page, with notes

### `utf8(5)`: the table

```text title="man 5 utf8, macOS 26.6.2, dumped 2026-09-13"
     The UTF-8 encoding represents UCS-4 characters as a sequence of octets,
     using between 1 and 6 for each character.  It is backwards compatible
     with ASCII, so 0x00-0x7f refer to the ASCII character set.  The multibyte
     encoding of non-ASCII characters consist entirely of bytes whose high
     order bit is set.
```

Three facts in four lines, and each is a whole library page. *UCS-4* is the 31-bit numbering of ISO 10646, not Unicode's 21-bit one, which is why the table below it runs to `0x7fffffff`. *Octet* is the standards word for a byte of exactly eight bits. And *bytes whose high order bit is set* is the property that makes UTF-8 safe for every tool written for ASCII: no byte of a multibyte character can ever be mistaken for a `/`, a NUL or a space, which is [why UTF-8 won](../../09_History/why_utf8_won/README.md).

```text title="man 5 utf8, macOS 26.6.2, dumped 2026-09-13"
     [0x00000000 - 0x0000007f] [00000000.0bbbbbbb] -> 0bbbbbbb
     [0x00000080 - 0x000007ff] [00000bbb.bbbbbbbb] -> 110bbbbb, 10bbbbbb
     [0x00000800 - 0x0000ffff] [bbbbbbbb.bbbbbbbb] ->
             1110bbbb, 10bbbbbb, 10bbbbbb
     [0x00010000 - 0x001fffff] [00000000.000bbbbb.bbbbbbbb.bbbbbbbb] ->
             11110bbb, 10bbbbbb, 10bbbbbb, 10bbbbbb
     [0x00200000 - 0x03ffffff] [000000bb.bbbbbbbb.bbbbbbbb.bbbbbbbb] ->
             111110bb, 10bbbbbb, 10bbbbbb, 10bbbbbb, 10bbbbbb
     [0x04000000 - 0x7fffffff] [0bbbbbbb.bbbbbbbb.bbbbbbbb.bbbbbbbb] ->
             1111110b, 10bbbbbb, 10bbbbbb, 10bbbbbb, 10bbbbbb, 10bbbbbb
```

This is the 1993 table: the six templates of FSS-UTF, kept by [RFC 2279 ↗](https://www.rfc-editor.org/rfc/rfc2279) in 1998. Read each row left to right: the range of numbers it covers, the number written in binary and cut into groups, and the bytes those groups land in. The first four rows are the whole of UTF-8 as it exists today, and [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) is the exercise of applying them with a pencil. The last two rows encode numbers no character will ever have, because [RFC 3629 ↗](https://www.rfc-editor.org/rfc/rfc3629), published in November 2003, five months before the date on this page, cut the codespace at `U+10FFFF` and the table at four bytes.

```text title="man 5 utf8, macOS 26.6.2, dumped 2026-09-13"
     If more than a single representation of a value exists (for example,
     0x00; 0xC0 0x80; 0xE0 0x80 0x80) the shortest representation is always
     used.  Longer ones are detected as an error as they pose a potential
     security risk, and destroy the 1:1 character:octet sequence mapping.
```

One sentence of specification and one of motive. A code point has exactly one legal spelling, and the padded longer spellings are ill-formed even though they decode to the same number: [Overlong sequences](../../03_Encodings/overlong_sequences/README.md) is that paragraph at full length, with the 1999 exploit it alludes to. Note the tense: *are detected as an error*. That is a claim about the C library, and the experiment below checks it.

```text title="man 5 utf8, macOS 26.6.2, dumped 2026-09-13"
     Rob Pike and Ken Thompson, "Hello World", Proceedings of the Winter 1993
     USENIX Technical Conference, USENIX Association, January 1993.
     ...
STANDARDS
     The utf8 encoding is compatible with RFC 2279 and Unicode 3.2.
```

The reading list is the encoding's birth certificate. Pike and Thompson's paper is the one where UTF-8 was designed on a placemat and put into Plan 9; the RFC is the 1998 six-byte one; and *Unicode 3.2* is the 2002 release, which is where the page's idea of the character set stops. The Unicode Character Database this Mac's `python3` carries is 16.0.0. The table has a version, and so does the page.

### `utf2(5)`: the name UTF-8 was born with

```text title="man 5 utf2, macOS 26.6.2, dumped 2026-09-13"
     The UTF2 encoding has been deprecated in favour of UTF-8.  New
     applications should not use UTF2.

     The UTF2 encoding is based on a proposed X-Open multibyte FSS-UCS-TF
     (File System Safe Universal Character Set Transformation Format) encoding
     as used in Plan 9 from Bell Labs.  Although it is capable of representing
     more than 16 bits, the current implementation is limited to 16 bits as
     defined by the Unicode Standard.
```

Same encoding, older name, and a page kept so that a 1990s reference still resolves. *FSS-UCS-TF*, elsewhere *FSS-UTF*, was X/Open's name before the IETF's; *File System Safe* names the design goal, that no byte of a character can be `/` or NUL. *Runes* in the title is the Plan 9 word for a code point, which Go later took for its `int32`: [`rune` is an `int32`](../../02_Characters/rune_is_an_int32/README.md). And *limited to 16 bits* is the 2002 implementation talking: three rows implemented, three more printed underneath as *currently not implemented*. The page is honest about the gap between its table and its code, which is rarer than it should be.

Its `SEE ALSO` names `mklocale(1)`. There is no such page on this Mac, and no such program; the locale compiler that read `ENCODING "UTF2"` did not ship. The reference survives the referent.

### `utf-8(7)`: the same table, with reasons

```text title="man 7 utf-8, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       •  All  UCS  characters  greater than 0x7f are encoded as a multibyte
          sequence consisting only of bytes in the range 0x80 to 0xfd, so no
          ASCII byte can appear as part of another character and  there  are
          no problems with, for example,  '\0' or '/'.

       •  The lexicographic sorting order of UCS-4 strings is preserved.
       ...
       •  The  bytes  0xc0, 0xc1, 0xfe, and 0xff are never used in the UTF-8
          encoding.

       •  The first byte of a multibyte sequence which represents  a  single
          non-ASCII  UCS  character  is always in the range 0xc2 to 0xfd and
          indicates how long this multibyte sequence is.  All further  bytes
          in  a  multibyte sequence are in the range 0x80 to 0xbf.  This al‐
          lows easy resynchronization and makes the encoding  stateless  and
          robust against missing bytes.
```

Where the BSD page gives the table, the Linux page gives the *properties* the table was chosen for, and each bullet is a claim you can check against the rows above. `0xc0` and `0xc1` are never used because a two-byte sequence starting with them would encode a number below `0x80`, an overlong spelling of ASCII. `0xfe` and `0xff` are never used because the templates stop at six bytes, and a lead byte for a seventh or eighth would have been exactly those two values; the useful consequence is that a file starting `FE FF` or `FF FE`, the UTF-16 byte order mark, cannot be UTF-8: [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md). *Resynchronization* is the property the glossary calls self-synchronising: a reader dropped into the middle of a stream can find the next character boundary by skipping bytes that start `10`. And *lexicographic sorting order preserved* means byte order equals code point order, which is a fact about numbers and says nothing about alphabetical order in any language: [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md).

```text title="man 7 utf-8, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       •  UTF-8  encoded UCS characters may be up to six bytes long, however
          the Unicode standard specifies no characters  above  0x10ffff,  so
          Unicode characters can be only up to four bytes long in UTF-8.
       ...
       The  UCS  code  values  0xd800–0xdfff  (UTF-16 surrogates) as well as
       0xfffe and 0xffff (UCS noncharacters) should not appear in conforming
       UTF-8 streams.  According to RFC 3629 no point above U+10FFFF  should
       be used, which limits characters to four bytes.
```

This is the 2024 page and it still prints six rows, then explains in prose why only four can ever be used. Two words carry weight. The surrogates *should not appear*: a decoder that meets `ED A0 80` is looking at half of a UTF-16 pair written in UTF-8, which is what [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) is about and what CESU-8 does on purpose. And the noncharacters *should not appear* in *conforming* streams, which is a weaker rule than the surrogate one, and the experiment below shows both `iconv`s treating it as weaker: [Noncharacters and the private use areas](../../02_Characters/noncharacters_and_private_use/README.md) explains why that is correct.

```text title="man 7 utf-8, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       Application  software  that has to be aware of the used character en‐
       coding should always set the locale with for example

              setlocale(LC_CTYPE, "")

       and programmers can then test the expression

              strcmp(nl_langinfo(CODESET), "UTF-8") == 0
```

The one paragraph on either page that tells a programmer what to *do*. A C program starts in the `"C"` locale whatever the environment says, and stays there until it calls `setlocale` with the empty string, which means *read the environment*. `nl_langinfo(CODESET)` then names the encoding the locale chose, and it is the same string `locale charmap` prints at the shell: [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md). The paragraph after it warns that *a single byte does not necessarily correspond any more to a single character* and that *outputting a single character does not necessarily advance the cursor by one position*, and names `mbsrtowcs(3)` and `wcswidth(3)` as the functions for the two counts. Those are two of the five rulers on [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md), and the functions are on [`multibyte(3)`](multibyte.md) and [`wcwidth(3)`](wcwidth.md).

### `unicode(7)`: the character set the encoding is of

```text title="man 7 unicode, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       The UCS standard (ISO/IEC 10646) describes a 31-bit character set ar‐
       chitecture  consisting  of  128  24-bit groups, each divided into 256
       16-bit planes made up of 256 8-bit rows with  256  column  positions,
       one for each character.
       ...
       Under  GNU/Linux, the C type wchar_t is a signed 32-bit integer type.
       Its values are always interpreted by the C library as UCS code values
       (in all locales), a convention that is signaled by the GNU C  library
       to applications by defining the constant __STDC_ISO_10646__
```

The first passage is the address scheme behind `U+XXXX`: group, plane, row, column, which is the *block then house number* reading on [Unicode code points](../../02_Characters/unicode_code_points/README.md), with the 31-bit ceiling that `utf8(5)`'s table was built for. The second passage is a promise glibc makes and the BSD libc does not: on Linux a `wchar_t` is *always* a code point, so a program can put one in a `switch` and compare it with `L'é'`. On this Mac the macro is not defined, and under a Japanese locale `mbrtowc` hands back the EUC byte pair rather than a code point. That is measured on the [`multibyte(3)`](multibyte.md) page and is the single most surprising fact in this family.

The page's section on combining characters, *Umlaut-A can either be represented by the precomposed UCS code 0x00c4, or alternatively as 0x0041 0x0308*, is [Normalization](../../04_Python/normalization/README.md) in one sentence, and its *Private Use Areas* section records something no Unicode document will: the Linux community's own carve-up of the BMP's private range into a user zone and a coordinated *Linux zone* at `0xf000`.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| `UCS-4`, `UCS-2` | ISO 10646's two fixed-width forms: every character as a 32-bit word, or (BMP only) as a 16-bit word. UCS-2 is what UTF-16 was before surrogates | [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) |
| ISO 10646, *UCS* | The ISO twin of Unicode: same characters, same numbers, a 31-bit codespace on paper until 2003. *Universal Character Set* | [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) |
| octet | A byte of exactly eight bits, the word standards use because *byte* was once machine-dependent | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| *high order bit* | Bit 7, the leftmost, worth 128. Set in every byte of a multibyte character and clear in every ASCII byte | [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| `0bbbbbbb`, `110bbbbb`, `10bbbbbb` | The templates: the fixed bits announce a byte's role and the `b`s carry the code point's bits, most significant first | [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) |
| *shortest representation*, *non-shortest form* | The rule that a code point has one legal spelling; a padded longer one is *overlong* and ill-formed | [Overlong sequences](../../03_Encodings/overlong_sequences/README.md) |
| *1:1 character:octet sequence mapping* | Each character has one byte string and each byte string one character, which is what lets a byte-wise comparison stand in for a character-wise one | [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) |
| `ENCODING "UTF-8"` | The first line of a `mklocale(1)` source file, naming which decoder the `LC_CTYPE` category compiled from it will use | [`multibyte(3)`](multibyte.md) |
| FSS-UCS-TF, FSS-UTF | *File System Safe UCS Transformation Format*, X/Open's 1992 name for the encoding, from the goal that no byte of a character may be `/` or NUL | [Why UTF-8 won](../../09_History/why_utf8_won/README.md) |
| rune | Plan 9's word for a code point; Go's name for its `int32` character type | [`rune` is an `int32`](../../02_Characters/rune_is_an_int32/README.md) |
| Plan 9 | The Bell Labs operating system UTF-8 was designed for and first shipped in, September 1992 | [From the telegraph to Unicode](../../09_History/from_telegraph_to_unicode/README.md) |
| RFC 2279, RFC 3629 | The 1998 six-byte definition of UTF-8 and its 2003 replacement, which cut the codespace at `U+10FFFF` and the table at four bytes | [A page has a date](../a_page_has_a_date/README.md) |
| BMP | The Basic Multilingual Plane, `U+0000` to `U+FFFF`, the first 65,536 numbers and everything UCS-2 can write | [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| surrogates `0xd800`–`0xdfff` | 2,048 numbers reserved so UTF-16 can write the planes above the BMP as pairs; never characters, so never legal in UTF-8 | [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) |
| noncharacters `0xfffe`, `0xffff` | Two of the 66 code points Unicode promises never to assign; well-formed in UTF-8 and meant for internal use only | [Noncharacters and the private use areas](../../02_Characters/noncharacters_and_private_use/README.md) |
| *resynchronization* | Finding the next character boundary from the middle of a stream by skipping continuation bytes; the glossary's *self-synchronising* | [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) |
| *lexicographic sorting order of UCS-4 strings is preserved* | Comparing UTF-8 byte by byte gives the same order as comparing code points. An order by number, not by any alphabet | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |
| `setlocale(LC_CTYPE, "")` | The call that makes a C program read `LANG` and `LC_*`; without it the program is in the `"C"` locale whatever the shell says | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| `nl_langinfo(CODESET)` | The name of the locale's encoding, as a string; `locale charmap` at the shell | [`locale(1)` and `setlocale(3)`](locale.md) |
| ISO/IEC 2022, `ESC % G` | The older switching scheme, where escape sequences change which character set the following bytes belong to; `ESC % G` is the sequence that switches a terminal into UTF-8 | [Code pages](../../02_Characters/code_pages/README.md) |
| double-width characters, combining characters | Why one character is not one column: CJK ideographs take two, and a combining mark takes none | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| combining character, precomposed | `0x00c4` against `0x0041 0x0308`: one character with two spellings, which is what normalization exists to reconcile | [Normalization](../../04_Python/normalization/README.md) |
| implementation levels 1, 2, 3 | ISO 10646's three tiers of support for combining characters, from none to all; a Unicode 3.0 idea that Unicode itself never adopted | |
| `__STDC_ISO_10646__` | A macro glibc defines to promise that `wchar_t` is always a code point. Absent on macOS, where it is not | [`multibyte(3)`](multibyte.md) |
| Private Use Area, *Linux zone* | `0xe000`–`0xf8ff`, never assigned by Unicode; the page records Linux's informal split of it | [Noncharacters and the private use areas](../../02_Characters/noncharacters_and_private_use/README.md) |

## Try it on your machine

**Where the page is.** The same subject, two names, two sections, and each machine has exactly one of them.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: which pages exist is a fact about the machine."
                          macOS                                                              ubuntu:24.04
$ man -w 5 utf8           .../MacOSX.sdk/usr/share/man/man5/utf8.5                           No manual entry for utf8 in section 5   (exit 16)
$ man -w 7 utf-8          No manual entry for utf-8   (exit 1)                                /usr/share/man/man7/utf-8.7.gz
$ man -w 7 unicode        No manual entry for unicode (exit 1)                                /usr/share/man/man7/unicode.7.gz
```

**Which table the decoder believes.** Seven byte strings, each a candidate spelling of one code point, through `iconv -f UTF-8 -t UTF-32BE`. The output column is the code point the decoder produced; `(nothing)` means it refused.

```text title="Measured 2026-09-13 — macOS 26.6.2 (BSD iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39). Not machine-checked."
                                                          macOS                      ubuntu:24.04
  f0 9f 98 80         U+1F600 as 4 bytes (the real one)   0001f600                   0001f600
  f8 88 80 80 80      U+200000 as 5 bytes                 00200000                   illegal input sequence at position 0
  fc 84 80 80 80 80   U+4000000 as 6 bytes                04000000                   illegal input sequence at position 0
  c0 80               U+0000 as 2 bytes (overlong)        Illegal byte sequence      illegal input sequence at position 0
  e0 80 af            U+002F as 3 bytes (overlong slash)  Illegal byte sequence      illegal input sequence at position 0
  ed a0 80            U+D800 (a surrogate)                Illegal byte sequence      illegal input sequence at position 0
  ef bf be            U+FFFE (a noncharacter)             0000fffe                   0000fffe
```

Rows two and three are the finding. This Mac's `iconv` decodes the fifth and sixth rows of the 2004 table, exactly as `utf8(5)` says it does, to numbers no Unicode character has; GNU's refuses them, exactly as the RFC its own page cites says it must. Rows four to six show both decoders agreeing with the shortest-form paragraph and with the surrogate rule. Row seven shows both accepting the noncharacter, which is the *should not* in `utf-8(7)` being read correctly as a weaker rule. Python is the control: `b'\xfc\x84\x80\x80\x80\x80'.decode('utf-8')` raises `UnicodeDecodeError: invalid start byte` on both machines, because the decoder in its standard library is the same code everywhere and was written after 2003.

**What `CODESET` says.** The page tells a C program to compare `nl_langinfo(CODESET)` with `"UTF-8"`. At the shell that value is `locale charmap`, and under the `C` locale the two machines name the same 128-character table two different ways.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked."
                                        macOS            ubuntu:24.04
$ LANG=en_US.UTF-8 locale charmap       UTF-8            UTF-8        (as LANG=C.UTF-8; en_US is not installed there)
$ LANG=C locale charmap                 US-ASCII         ANSI_X3.4-1968
```

`ANSI_X3.4-1968` is ASCII's formal name, the 1968 revision of American National Standard X3.4, and `iconv -l` on either machine lists it as an alias. A string comparison against `"UTF-8"` works on both; a comparison against `"ASCII"` works on neither.

**What `ENCODING "UTF-8"` compiled to.** The locale directory shows the page's `SYNOPSIS` as a file, and shows that every UTF-8 locale on this Mac is one decoder.

```text title="Measured 2026-09-13 — macOS 26.6.2. Not machine-checked."
$ ls /usr/share/locale/en_US.UTF-8/
LC_COLLATE  LC_CTYPE  LC_MESSAGES  LC_MONETARY  LC_NUMERIC  LC_TIME
$ ls -la /usr/share/locale/en_US.UTF-8/LC_CTYPE
lrwxr-xr-x  1 root  wheel  19 Aug 12 22:51 /usr/share/locale/en_US.UTF-8/LC_CTYPE -> ../C.UTF-8/LC_CTYPE
$ man -w 1 mklocale
No manual entry for mklocale
```

Six categories, one file each, which is the *six independent variables* of [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) as a directory listing. The `LC_CTYPE` of `en_US.UTF-8` is a symlink to `C.UTF-8`'s, so the language part of the name changes nothing about what a character is; only the encoding part does. And the compiler that made the file is not on the machine that ships its output.

## Where the page is dated, and what it does not say

**`utf8(5)` is dated April 7, 2004** and cites RFC 2279 (January 1998), which RFC 3629 (November 2003) had obsoleted five months earlier. Its table is the 1993 one and its `iconv` still implements it; the page is stale about Unicode and correct about the machine, which is the whole of [A page has a date](../a_page_has_a_date/README.md). Its idea of the character set ends at Unicode 3.2 (2002).

**`utf-8(7)` is dated 2024-03-14** and still opens with *The Unicode 3.0 character set occupies a 16-bit code space*, a sentence that has been false since 2001. It knows about RFC 3629 and says so in prose, but keeps the six-row table, and its `Standards` line lists both Unicode 3.1 and RFC 3629 as if they agreed. A reader who takes the table and skips the prose gets the 1998 encoding.

**Neither page mentions the byte order mark.** `EF BB BF` at the front of a UTF-8 file, which Excel writes and which breaks the first field of a CSV, appears on neither page. Search the dumps: the string `BOM` and the phrase `byte order` are absent from both. [A BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md) is the page that fills the gap.

**Neither page says what a decoder should do with bad input.** `U+FFFD REPLACEMENT CHARACTER` is not mentioned; neither is the choice between refusing, replacing and skipping, which is the `errors=` argument in Python and the `-c` flag on [`iconv(1)`](iconv.md). *Detected as an error* is all `utf8(5)` says, and the experiment above shows the two libraries detecting different errors.

**Neither page names the variants.** CESU-8, WTF-8 and Modified UTF-8 are all UTF-8 with one rule relaxed, all in daily use, and on neither page: [Why UTF-16 stayed](../../09_History/why_utf16_stayed/README.md) and [`OsStr`, `Path`, and WTF-8](../../05_Rust/osstr_path_and_wtf8/README.md).

**`utf2(5)` points at a program that is not there.** Its `SEE ALSO` names `mklocale(1)`, which this Mac does not ship, in any section.

## See also

- [`multibyte(3)`](multibyte.md) — the functions that implement this table, and the measurement that `wchar_t` is not a code point on macOS
- [The CJK pages](cjk_encodings.md) — the other seven section-5 encoding pages, the ones UTF-8 replaced
- [`charsets(7)` and the code-page pages](charsets.md) — Linux's tour of everything before Unicode
- [`ascii(7)`](ascii.md) — the first row of the table, as its own page on both machines
- [`iconv(1)` and `iconv(3)`](iconv.md) — the tool the experiment above ran, and the page that documents `//TRANSLIT`
- [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) — the four templates applied with a pencil
- [Overlong sequences](../../03_Encodings/overlong_sequences/README.md) — the shortest-form paragraph at full length
- [A page has a date](../a_page_has_a_date/README.md) — the six-byte table, the 1998 RFC, and why the page is still right
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) — where this page sits among the forty
- [What the page does not say](../what_the_page_does_not_say/README.md) — the general rule for the gaps listed above
