# `charsets(7)`, `iso_8859-1(7)`, `cp1252(7)`, `koi8-r(7)` and six more: Linux's map of everything before Unicode

**Level:** reference · for anyone who has typed `man 7 cp1252` or `man 7 charsets` and wanted every row on it explained

**One line:** Ten Linux pages, none of them on the Mac, print the upper half of each single-byte code page as a table you can `grep`, and every row checked against `iconv` today holds: Latin-9 is Latin-1 with exactly eight bytes changed and `€` first among them, Windows-1252 assigns 27 of the 32 positions Latin-1 gives to controls and leaves five holes, and clearing bit 7 of a KOI8-R byte gives a Latin letter that spells the Russian one.

**The pages:** [`charsets(7)`](raw/linux/charsets.7.txt) (Linux man-pages 6.7, 2024-01-28; copyright Eric S. Raymond 1996 and Andries Brouwer) · [`iso_8859-1(7)`](raw/linux/iso_8859-1.7.txt) (2024-01-28; Daniel Quinlan 1993–1995) · [`iso_8859-2(7)`](raw/linux/iso_8859-2.7.txt), [`iso_8859-15(7)`](raw/linux/iso_8859-15.7.txt), [`iso_8859-16(7)`](raw/linux/iso_8859-16.7.txt) (2024-01-28) · [`cp1251(7)`](raw/linux/cp1251.7.txt), [`cp1252(7)`](raw/linux/cp1252.7.txt) (2024-01-28; Marko Myllynen 2014) · [`koi8-r(7)`](raw/linux/koi8-r.7.txt) (2022-12-15; Alexey Mahotkin 2001) · [`koi8-u(7)`](raw/linux/koi8-u.7.txt) (2022-12-15) · [`armscii-8(7)`](raw/linux/armscii-8.7.txt) (2022-12-15; Lefteris Dimitroulakis 2009). macOS ships none of them: `man -w 7 charsets` answers *No manual entry*. Dumped 2026-09-13 by [`dump_linux.sh`](dump_linux.sh); the machines are in [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt) and [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt).

## What the pages are for

`charsets(7)` says what it is in its first sentence: *an overview on different character set standards and how they were used on Linux before Unicode became ubiquitous*. It is a map, in section 7 because it documents no file, no function and no command, and it walks from ASCII through the fifteen parts of ISO 8859, KOI8, the East Asian sets, the ISO 2022 switching scheme, TIS-620 and finally Unicode, one paragraph each. Its copyright line is from 1996, when the map was of the present; the page still describes the sets as *used by locale character sets*, and glibc still ships a converter for every set named below.

The other nine are tables. Each prints the upper half of one single-byte code page as one row per byte with the byte in three bases, the glyph and the Unicode character name, and each says of itself that it shows *the characters ... that are printable and unlisted in the `ascii(7)` manual page*, which is the whole idea of a code page in one clause: the low half is ASCII and the page is about the disagreement above it, [Code pages](../../02_Characters/code_pages/README.md). `ascii(7)`'s `SEE ALSO` there lists a page for every part of ISO 8859 that exists, and beside them are two Windows code pages, two KOI8 variants and ArmSCII; this family takes the ten that the library's cast of characters lands on.

macOS has none of these pages, though it has the tables: `iconv -l` on the Mac lists every name used below, `locale -a` lists fifty locales whose encoding is one of Latin-2, Latin-9, KOI8-R, KOI8-U, CP1251 or ArmSCII-8, and every experiment below that could run on both machines gave the same bytes on both but one. The pages are Linux's; the facts are everybody's.

## The page, with notes

### `charsets(7)`: the map

```text title="man 7 charsets, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       ISO/IEC 8859 is a series of 15 8-bit character  sets,  all  of  which
       have ASCII in their low (7-bit) half, invisible control characters in
       positions  128  to  159,  and  96  fixed-width  graphics in positions
       160–255.
       ...
       ISO/IEC 8859-12
              This character set does not exist.
```

Three numbers describe the whole family: 128 ASCII, 32 controls, 96 graphics. The 32 are the C1 controls, `0x80`–`0x9F`, which is why the ISO tables below begin at `0xA0` and have 96 rows, and why Windows, which had no use for C1 controls, put printable characters there instead. *Part 12 does not exist* is the page being precise about a standard that skipped a number. The `Unicode` section at the end says the codespace *permits 20.1 bits*, which is log₂ of 1,114,112, and still prints the six-byte UTF-8 progression that [`utf8(5)` and `utf-8(7)`](utf8.md) dates to 1998.

```text title="man 7 charsets, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       KOI8-R is a non-ISO character set popular in Russia  before  Unicode.
       The  lower half is ASCII; the upper is a Cyrillic character set some‐
       what better designed than ISO/IEC 8859-5.
       ...
       Switching between character sets is done using the shift functions ^N
       (SO  or  LS1), ^O (SI or LS0), ESC n (LS2), ESC o (LS3), ESC N (SS2),
       ESC O (SS3), ESC ~ (LS1R), ESC } (LS2R), ESC | (LS3R).
```

*Somewhat better designed* is explained by the measurement below, not by the page. The ISO 2022 paragraph is the other model of a multi-script world, the one the code pages replaced and UTF-8 replaced in turn: escape sequences that switch which table the following bytes belong to, with four slots `G0`–`G3` and the same *single shift* idea that [`euc(5)`](cjk_encodings.md) uses for its third and fourth code sets. A reader who has met `ESC ( B` in a terminal log has met this paragraph.

### The table, and how to read a row

```text title="man 7 iso_8859-1, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       The following table displays the characters in  ISO/IEC  8859-1  that
       are printable and unlisted in the ascii(7) manual page.
       Oct   Dec   Hex   Char   Description
       ────────────────────────────────────────────────────────────────────
       240   160   A0           NO-BREAK SPACE
       ...
       351   233   E9     é     LATIN SMALL LETTER E WITH ACUTE
       ...
       377   255   FF     ÿ     LATIN SMALL LETTER Y WITH DIAERESIS
```

One byte per row, written three ways, then the glyph, then a name. The three bases are the same number and the reason all three are printed is that `od` speaks octal, `xxd` hex and Python's `bytes` decimal: [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md). The `Char` column is empty for the no-break space and the soft hyphen, which print as nothing. The `Description` column is the Unicode character name, so every row is a byte-to-code-point mapping with the number left out: `é` at `E9` is `U+00E9`, and for Latin-1 alone byte and code point are always equal, the fact [A character is a number](../../02_Characters/a_character_is_a_number/README.md) rests on. On every other page the name is the only key, and the way back to a number is `unicodedata.lookup` or [`uni`](../../11_Tools/uni/README.md).

### `iso_8859-1(7)` and `iso_8859-15(7)`: eight bytes apart

```text title="diff of the table rows in the two dumps (raw/linux/iso_8859-1.7.txt, iso_8859-15.7.txt), 2026-09-13"
<        244   164   A4     ¤     CURRENCY SIGN
>        244   164   A4     €     EURO SIGN
<        246   166   A6     ¦     BROKEN BAR
>        246   166   A6     Š     LATIN CAPITAL LETTER S WITH CARON
<        250   168   A8     ¨     DIAERESIS
>        250   168   A8     š     LATIN SMALL LETTER S WITH CARON
<        264   180   B4     ´     ACUTE ACCENT
>        264   180   B4     Ž     LATIN CAPITAL LETTER Z WITH CARON
<        270   184   B8     ¸     CEDILLA
>        270   184   B8     ž     LATIN SMALL LETTER Z WITH CARON
<        274   188   BC     ¼     VULGAR FRACTION ONE QUARTER
<        275   189   BD     ½     VULGAR FRACTION ONE HALF
<        276   190   BE     ¾     VULGAR FRACTION THREE QUARTERS
>        274   188   BC     Œ     LATIN CAPITAL LIGATURE OE
>        275   189   BD     œ     LATIN SMALL LIGATURE OE
>        276   190   BE     Ÿ     LATIN CAPITAL LETTER Y WITH DIAERESIS
```

The two pages are 96 rows each and differ in exactly eight. Latin-9, which the `NOTES` also calls *Latin-0*, was Latin-1 revised for the euro, and the eight victims were the eight characters judged least missed: the currency placeholder `¤`, the broken bar, three spacing accents and the three fractions. In their places, `€`, the Finnish `Š š Ž ž` and the French `Œ œ Ÿ` that Latin-1 had left out, the omission `charsets(7)` records as *considered tolerable*. The consequence for data is that a Latin-9 file holding `€` is a Latin-1 file holding `¤`, byte for byte, and nothing in the file says which: [Mojibake](../../03_Encodings/mojibake/README.md).

### `iso_8859-2(7)` and `iso_8859-16(7)`: where `ż` and `Ł` live

```text title="man 7 iso_8859-2, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       243   163   A3     Ł     LATIN CAPITAL LETTER L WITH STROKE
       ...
       277   191   BF     ż     LATIN SMALL LETTER Z WITH DOT ABOVE
       ...
       363   243   F3     ó     LATIN SMALL LETTER O WITH ACUTE
```

Latin-2 is the Central European page and the one Polish text was written in before UTF-8. Two of the library's cast are on it, `ż` at `BF` and `Ł` at `A3`, and `Łódź` encodes as `a3 f3 64 bc`. Notice `ó` at `F3`: the letters Latin-2 shares with Latin-1 sit at the same bytes, so a Polish word misread as Latin-1 keeps its vowels and loses its consonants, `£ód¼`, which is how [Mojibake](../../03_Encodings/mojibake/README.md) teaches you to recognise the culprit from the damage. Latin-10, `iso_8859-16(7)`, is *Romanian* in its NAME line and moves `Ł ł Ż ż` to other bytes while adding `€` at `A4` and the comma-below `Ș ș Ț ț` that `charsets(7)` says Latin-2 had settled for cedillas instead of.

### `cp1252(7)` and `cp1251(7)`: the C1 block filled in

```text title="man 7 cp1252, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       The Windows Code Pages include several 8-bit extensions to the  ASCII
       character  set  (also known as ISO/IEC 646-IRV).  CP 1252 encodes the
       characters used in many West European languages.
       ...
       200   128   80     €     EURO SIGN
       202   130   82     ‚     SINGLE LOW-9 QUOTATION MARK
       214   140   8C     Œ     LATIN CAPITAL LIGATURE OE
       216   142   8E     Ž     LATIN CAPITAL LETTER Z WITH CARON
       221   145   91     ‘     LEFT SINGLE QUOTATION MARK
```

Read the octal column and watch it skip: `200`, `202`, then `214`, `216`, `221`. The page has 123 rows where Latin-1 has 96, because Windows-1252 puts printable characters in the 32 positions ISO reserves for C1 controls, and it has 27 rows in that block rather than 32, because five bytes, `81 8D 8F 90 9D`, are assigned nothing at all. That is the count [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) makes, and the page's own table agrees with it: Windows-1252 is not a superset of Latin-1, since over these 32 bytes it keeps none of Latin-1's mappings and drops five. The experiment below shows both `iconv`s refusing the five and Latin-1 accepting everything, which is why one table can always round-trip and the other cannot: [The mojibake round trip](../../07_Real_Data/mojibake_round_trip/README.md). `cp1251(7)`, *Windows Cyrillic*, fills the same block with Serbian and Macedonian letters and the same typographic quotes, puts `€` at `88`, and lays out the Russian alphabet in dictionary order from `А` at `C0` to `я` at `FF`, which is exactly what KOI8-R does not do.

### `koi8-r(7)` and `koi8-u(7)`: the ordering trick

```text title="man 7 koi8-r, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       300   192   C0     ю     CYRILLIC SMALL LETTER YU
       301   193   C1     а     CYRILLIC SMALL LETTER A
       302   194   C2     б     CYRILLIC SMALL LETTER BE
       303   195   C3     ц     CYRILLIC SMALL LETTER TSE
       304   196   C4     д     CYRILLIC SMALL LETTER DE
       305   197   C5     е     CYRILLIC SMALL LETTER IE
       ...
NOTES
       The  differences with KOI8-U are in the hex positions A4, A6, A7, AD,
       B4, B6, B7, and BD.
```

`ю а б ц д е` is not any alphabet's order. Subtract `0x80` from each byte and read the ASCII: `@ A B C D E F G`, and `а` is `A`, `б` is `B`, `ц` is `C`, `д` is `D`. KOI8-R orders its Cyrillic by the Latin letter that transliterates it, so that a byte stream with its high bit stripped, which is what a seven-bit channel does to it, comes out as readable Russian in Latin letters rather than as noise. The lowercase letters sit against ASCII's uppercase, `C0`–`DF` against `40`–`5F`, so the case is inverted on the way, and the experiment below shows it. This is the design `charsets(7)` calls *somewhat better designed than ISO/IEC 8859-5* without saying why, and it is also why sorting KOI8-R bytes does not sort Russian: [A character is a number](../../02_Characters/a_character_is_a_number/README.md) is a number chosen for a reason, and the reason here was transmission, not collation. The `NOTES` on each KOI8 page name eight positions; a `diff` of the two dumps finds exactly those eight, box-drawing pieces in KOI8-R replaced by the Ukrainian `є і ї ґ` and their capitals in KOI8-U.

### `armscii-8(7)`: a second copy of the punctuation

```text title="man 7 armscii-8, Linux man-pages 6.7, dumped 2026-09-13 from ubuntu:24.04"
       244   164   A4     )     RIGHT PARENTHESIS
       245   165   A5     (     LEFT PARENTHESIS
       ...
       251   169   A9     .     FULL STOP
       ...
       253   171   AB     ,     COMMA
       254   172   AC     -     HYPHEN-MINUS
       ...
       262   178   B2     Ա     ARMENIAN CAPITAL LETTER AYB
       263   179   B3     ա     ARMENIAN SMALL LETTER AYB
```

The Armenian page has 94 rows and two things on it break rules the other pages keep. Bytes `A4`, `A5`, `A9`, `AB` and `AC` are a parenthesis pair, a full stop, a comma and a hyphen, characters ASCII already has at `29`, `28`, `2E`, `2C` and `2D`, so under this table one character has two byte spellings and the 1:1 mapping [`utf8(5)`](utf8.md) treats as a security property does not hold. (Note the pair is stored closing-first, `)` before `(`.) And the letters alternate capital, small, capital, small from `B2`, so the case bit of an Armenian letter is bit 0, not the `0x20` of [`ascii(7)`](ascii.md). A byte-oriented `tolower` written for Latin gets both wrong.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| ISO/IEC 646-IRV | The International Reference Version of ISO 646, which is ASCII; the pages' formal name for the low half every code page shares | [`ascii(7)`](ascii.md) |
| *invisible control characters in positions 128 to 159* | The C1 controls, `0x80`–`0x9F`; why the ISO tables start at `A0` and why Windows put printable characters there instead | [Control characters](../../02_Characters/control_characters/README.md) |
| *96 fixed-width graphics* | `0xA0`–`0xFF`: the one printable block an ISO 8859 part defines; 96 rows on each ISO page | [Code pages](../../02_Characters/code_pages/README.md) |
| Latin-1 … Latin-10 | The alphabet numbering, which does not follow the part numbering: Latin-5 is 8859-9, Latin-9 is 8859-15, Latin-10 is 8859-16 | [Code pages](../../02_Characters/code_pages/README.md) |
| `Oct Dec Hex Char Description` | One byte in three bases, its glyph, and its Unicode character name; the name is the only key to the code point on nine of the ten pages | [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| NO-BREAK SPACE, SOFT HYPHEN | `A0` and `AD` on every ISO page, printed with an empty `Char` cell; both invisible, both a common source of "the two strings look equal" bugs | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| CURRENCY SIGN `¤` | Latin-1's `A4`: a placeholder for *whichever currency you use*, which is why the euro took its byte | [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) |
| Windows Code Pages, CP 1252, Windows-1252, *Windows Cyrillic* | Microsoft's numbered single-byte tables; the same tables under SAP's and IBM's numbers are on the SAP page | [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) |
| KOI8-R, KOI8-U, RFC 1489, RFC 2310 | The Russian and Ukrainian eight-bit sets, each defined by an informational RFC rather than an ISO part; *KOI* is a Russian abbreviation for *code for information interchange* | [A character is a number](../../02_Characters/a_character_is_a_number/README.md) |
| G0, G1, G2, G3; SO, SI; SS2, SS3; `ESC ( B` | ISO 2022's four table slots, the shift bytes that select one, and the escape that designates ASCII into G0 | [The CJK pages](cjk_encodings.md) |
| ArmSCII-8 | *Armenian Standard Code for Information Interchange*, eight-bit; the page's expansion of its own name | |
| 94×94, EUC-CN, EUC-JP, JIS X 0208, *not ISO/IEC 2022 compatible* | The two-byte national sets and the encodings built on them, one paragraph each here and six pages on the Mac; KOI8 and Big5 are *not compatible* because their upper halves are not a set the escape scheme could switch to | [The CJK pages](cjk_encodings.md) |

## Try it on your machine

**Where the pages are.** Ten on Ubuntu, none on the Mac; every table on both.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: which pages exist is a fact about the machine."
                          macOS                              ubuntu:24.04
$ man -w 7 charsets       No manual entry for charsets       /usr/share/man/man7/charsets.7.gz
$ locale -a | grep -cE 'ISO8859-2$|ISO8859-15$|KOI8|CP1251|ARMSCII'
                          50                                 0   (C, C.utf8, POSIX only)
$ LC_ALL=pl_PL.ISO8859-2 locale charmap
                          ISO8859-2                          ANSI_X3.4-1968, after three 'Cannot set ... to default locale' warnings
```

**One row from each page, and what `iconv` says about it.** `printf '\xNN' | iconv -f NAME -t UTF-8`, shown as the character and its UTF-8 bytes. Byte-identical on both machines.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39): byte-identical on both. Not machine-checked."
  byte  ISO-8859-1        ISO-8859-15       CP1252            KOI8-R            ISO-8859-2        ARMSCII-8
  80    (C1)  c280        (C1)  c280        €  e282ac         ─  e29480         (C1)  c280        (C1)  c280
  a3    £  c2a3           £  c2a3           £  c2a3           ё  d191           Ł  c581           ։  d689
  a4    ¤  c2a4           €  e282ac         ¤  c2a4           ╓  e29593         ¤  c2a4           )  29
  bf    ¿  c2bf           ¿  c2bf           ¿  c2bf           ©  c2a9           ż  c5bc           է  d5a7
  c1    Á  c381           Á  c381           Á  c381           а  d0b0           Á  c381           ը  d5a8

$ man 7 iso_8859-15 | grep -E '^ +244 '       244   164   A4     €     EURO SIGN
$ man 7 iso_8859-1  | grep -E '^ +244 '       244   164   A4     ¤     CURRENCY SIGN
```

One byte, six meanings, and the rows are the pages' own rows: `grep` the octal on Ubuntu and `iconv` on either machine agree on every cell. `a4` is the page's whole story in one line: the currency placeholder, the euro, the placeholder again, a box-drawing corner, and in ArmSCII a closing parenthesis. `(C1)` is the byte decoding to the control character `U+0080`, invisible and legal under every table but Windows-1252 and KOI8-R, refused by none of them.

**The five holes in Windows-1252, and the eight changes in Latin-9.** The counts, made from the dumps and checked against two `iconv`s and Python.

```text title="Measured 2026-09-13 — dump files read on macOS; iconv on macOS 26.6.2 and ubuntu:24.04 (identical); python3 3.14 on macOS and 3.12 on ubuntu (identical). Not machine-checked."
$ diff <(grep -E '^ {7}[0-7]{3} ' raw/linux/iso_8859-1.7.txt) <(grep -E '^ {7}[0-7]{3} ' raw/linux/iso_8859-15.7.txt) | grep -c '^<'
8
$ grep -cE '^ {7}2[0-3][0-7] ' raw/linux/cp1252.7.txt          # rows in octal 200-237, i.e. 0x80-0x9F
27
missing from cp1252.7.txt:   201(=81) 215(=8D) 217(=8F) 220(=90) 235(=9D)

$ printf '\x81' | iconv -f CP1252 -t UTF-8        iconv: illegal input sequence at position 0     (Apple: Illegal byte sequence)
$ printf '\x81' | iconv -f ISO-8859-1 -t UTF-8    c2 81   (U+0081, a C1 control)
$ python3 -c "..."  cp1252 refuses: 81 8D 8F 90 9D
$ python3 -c "print(bytes(range(0x80,0xa0)).decode('cp1252','replace'))"
€�‚ƒ„…†‡ˆ‰Š‹Œ�Ž��‘’“”•–—˜™š›œ�žŸ
```

Twenty-seven assigned, five refused, and the five are the same five on the page, in both `iconv`s and in Python's codec. The last line is the 32-byte block decoded with `errors='replace'`, and the five replacement characters sit exactly where the octal column skipped. Latin-1 never refuses, because it has a character for all 256 bytes; that asymmetry is the whole of [The mojibake round trip](../../07_Real_Data/mojibake_round_trip/README.md).

**KOI8-R with its high bit stripped.** Encode a Russian phrase, clear bit 7 of every byte, decode the result as ASCII.

```text title="Measured 2026-09-13 — python3 on ubuntu:24.04 and on macOS 26.6.2: identical. Not machine-checked."
$ python3 -c "
s='Привет, мир'.encode('koi8-r')
print('koi8-r bytes :', s.hex(' '))
print('bit 7 cleared:', bytes(b & 0x7f for b in s).decode('ascii'))
"
koi8-r bytes : f0 d2 c9 d7 c5 d4 2c 20 cd c9 d2
bit 7 cleared: pRIWET, MIR

$ printf '\xa4' | iconv -f KOI8-R -t UTF-8    ╓        $ printf '\xa4' | iconv -f KOI8-U -t UTF-8    є
```

*Privet, mir* with the case swapped, because KOI8-R's lowercase sits against ASCII's uppercase. `ц` at `C3` came out as `C` and `в` at `D7` as `W`, the transliteration the table was built around; the comma and the space, being ASCII, came through untouched. The last line is one of the eight positions the `NOTES` name, a box-drawing piece in Russian and a Ukrainian letter in the neighbour.

**Latin-2 has the Polish letters and Latin-1 does not, and the one place the machines differ.** `Łódź` encoded into three tables, then its Latin-2 bytes read back under the wrong one.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39). Not machine-checked."
                                                       macOS                          ubuntu:24.04
$ printf 'Łódź' | iconv -f UTF-8 -t ISO-8859-2 | xxd -p     a3f364bc                       a3f364bc
$ printf 'Łódź' | iconv -f UTF-8 -t ISO-8859-1 | xxd -p     4cf364b47a   exit 0            illegal input sequence at position 0   exit 1
$ printf 'Łódź' | iconv -f UTF-8 -t CP1252     | xxd -p     4cf364b47a   exit 0            illegal input sequence at position 0   exit 1
$ printf '\xa3\xf3\x64\xbc' | iconv -f ISO-8859-1 -t UTF-8  £ód¼                           £ód¼
```

Row one is the page: `Ł` at `A3`, `ó` at `F3`, `ż`'s neighbour `ź` at `BC`. Rows two and three are the difference. GNU `iconv` refuses to write `Ł` into a table that has no `Ł`, and says so with exit 1; Apple's writes `4c f3 64 b4 7a`, which is `Lód´z`, with the stroke dropped and the acute turned into a spacing accent, and exits 0 as if nothing had happened. GNU will do something similar only when asked with `//TRANSLIT`, and does it differently: `4c f3 64 7a`, `Lódz`, measured on Ubuntu only. Which behaviour you get is a fact about the `iconv` on the machine, and neither is on any page here: [`iconv`](../../06_Terminal/iconv/README.md). The last row is the mojibake the page predicts: the bytes are Polish, the reader is Latin-1, the vowels survive.

## Where the page is dated, and what it does not say

**`charsets(7)` carries a 1996 copyright and a 2024 date**, and reads as both: the code-page paragraphs describe a present that is now a past, and its Unicode paragraph still prints the six-byte UTF-8 progression and a 512-glyph Linux console. Its map is nonetheless the only one on either machine. Nor does `koi8-r(7)` explain its own ordering: the transliteration design is visible in the table and named nowhere, and `charsets(7)` calls it *better designed* and stops.

**The table pages give names, not numbers.** Every row's `Description` is a Unicode character name, and no row says `U+`. For Latin-1 the number is the byte; for the other nine you look the name up.

**No page says what happens to a byte it does not list.** The C1 range on the ISO pages and the five holes on `cp1252(7)` are simply absent; that `iconv` refuses the holes and passes the C1 bytes through as controls is measured above and written nowhere.

**`cp1252(7)` does not say that browsers read `ISO-8859-1` as Windows-1252**, the rule that makes the superset claim feel true on the web and false in a data pipeline: [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md).

**None of the ten exists on the Mac**, and the Mac's `iconv(1)` page does not point at anything that replaces them. The nearest thing on the Mac to `man 7 cp1252` is `iconv -l`, which gives the names and none of the rows.

## See also

- [`ascii(7)`](ascii.md) — the low half every one of these pages says it leaves out
- [`utf8(5)` and `utf-8(7)`](utf8.md) — the encoding that made all ten tables legacy, and the 1:1-mapping rule ArmSCII breaks
- [`iconv(1)` and `iconv(3)`](iconv.md) — the tool that has every table above and whose Apple build substitutes silently
- [`locale(5)` and `localedef(1)`](locale_files.md) — the charmap files these tables are compiled from on Linux
- [The CJK pages](cjk_encodings.md) — the two-byte sets `charsets(7)` gives a paragraph each and the Mac gives a page each
- [Code pages](../../02_Characters/code_pages/README.md) — ASCII plus a second opinion, the idea behind every table here
- [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) — the count the `cp1252(7)` table confirms
- [Mojibake](../../03_Encodings/mojibake/README.md) — `£ód¼` and `Ã©`, and how to name the culprit from the damage
- [What the page does not say](../what_the_page_does_not_say/README.md) — the general rule for the gaps listed above
