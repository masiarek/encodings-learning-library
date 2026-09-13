# `euc(5)`, `big5(5)`, `gb2312(5)`, `gbk(5)`, `gb18030(5)` and `mskanji(5)`: the encodings UTF-8 replaced, one page each

**Level:** reference · for anyone who has typed `man 5 gbk` or `man 5 euc` and wanted every byte range on it explained

**One line:** Six BSD pages from 2003 describe the Chinese, Japanese and Korean multibyte encodings as lead-byte and trail-byte ranges plus one mask formula, and this Mac still ships the locales that implement them: `ja_JP.SJIS` counts `83 5c` as one character, the backslash inside a GBK character is on the `gbk(5)` page as a trail-byte range, and GB18030's four-byte form reaches every code point on Ubuntu but stops at the Basic Multilingual Plane in Apple's `iconv`.

**The pages:** [`euc(5)`](raw/macos/euc.5.txt) (macOS, dated November 8, 2003; copyright line 1993) · [`big5(5)`](raw/macos/big5.5.txt) (August 7, 2003) · [`gb2312(5)`](raw/macos/gb2312.5.txt) (November 7, 2003) · [`gbk(5)`](raw/macos/gbk.5.txt) (August 10, 2003) · [`gb18030(5)`](raw/macos/gb18030.5.txt) (August 10, 2003) · [`mskanji(5)`](raw/macos/mskanji.5.txt) (August 7, 2003). The five encoding-specific pages carry a *Copyright (c) 2002, 2003 Tim J. Robbins* line in their source. Ubuntu ships none of the six; its one page on the subject is [`charsets(7)`](raw/linux/charsets.7.txt), annotated on [`charsets(7)` and the code-page pages](charsets.md). Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

These are the other six section-5 encoding pages beside [`utf8(5)`](utf8.md), and they exist for the same reason it does: each `SYNOPSIS` is the first line of a locale source file for the `mklocale(1)` compiler, `ENCODING "BIG5"`, `ENCODING "GBK"`, `ENCODING "MSKanji"`, and the page documents the decoder that the C library's [`multibyte(3)`](multibyte.md) functions run when a locale names it. The pages are short because a decoder for these encodings is short: a byte below `0x80` is ASCII, a byte in one range starts a two-byte character, the next byte must be in another range, and that is the whole grammar. What the pages leave out is what the two bytes *mean*, because that is a table of several thousand rows kept in `/usr/share/locale/*/LC_CTYPE`, not on a manual page.

They were written in 2002 and 2003 for FreeBSD, whose C library was acquiring its multibyte support at the time, and macOS inherited them with the library. The dates matter twice over. Unicode 3.0 and GB 18030-2000 are the newest standards any of them cite, and the encodings themselves were, by 2003, already the thing UTF-8 was replacing: [Why UTF-8 won](../../09_History/why_utf8_won/README.md) is the story these pages are the *before* of. They are still the pages to read when a file from a Japanese or Chinese system turns up and `file` says `data`, because the byte ranges on them are exactly what you need to recognise it by eye: [Code pages](../../02_Characters/code_pages/README.md).

Linux has no equivalent. `man 5 euc`, `man 5 gbk` and the rest answer *No manual entry* on Ubuntu 24.04, and its `charsets(7)` covers all of East Asia in five paragraphs. The glibc decoders exist and agree with the BSD ones byte for byte in every experiment below but one, so the difference is in documentation, not in the machines.

## The page, with notes

### `euc(5)`: four code sets and a mask

```text title="man 5 euc, macOS 26.6.2, dumped 2026-09-13"
SYNOPSIS
     ENCODING "EUC"

     VARIABLE len1 mask1 len2 mask2 len3 mask3 len4 mask4 mask

DESCRIPTION
     EUC implements a system of 4 multibyte codesets.  A multibyte character
     in the first codeset consists of len1 bytes starting with a byte in the
     range of 0x00 to 0x7f.  To allow use of ASCII, len1 is always 1.  A
     multibyte character in the second codeset consists of len2 bytes starting
     with a byte in the range of 0x80-0xff excluding 0x8e and 0x8f.  A
     multibyte character in the third codeset consists of len3 bytes starting
     with the byte 0x8e.  A multibyte character in the fourth codeset consists
     of len4 bytes starting with the byte 0xf.
```

EUC, *Extended Unix Code*, is not one encoding but a frame with four slots, and this page is the frame. Code set 1 is ASCII. Code set 2 is the national two-byte set, both bytes with the high bit set: JIS X 0208 in Japan, GB 2312 in China, KS X 1001 in Korea, each a 94×94 grid whose row and column are written as a byte in `0xA1`–`0xFE`. Code sets 3 and 4 are reached through the two *single shift* bytes, `0x8e` (SS2) and `0x8f` (SS3), which say *the next character comes from the other table*; in `ja_JP.eucJP` SS2 introduces the half-width katakana of JIS X 0201 and SS3 the supplementary kanji of JIS X 0212. The shift applies to one character and then the stream is back in code set 2, which is why EUC is stateless where ISO 2022 is not, and why the last experiment below can start decoding at any byte.

```text title="man 5 euc, macOS 26.6.2, dumped 2026-09-13"
     For example, the ja_JP.eucJP locale has the following VARIABLE line:

     VARIABLE        1 0x0000 2 0x8080 2 0x0080 3 0x8000 0x8080

     Codeset 1 consists of the values 0x0000 - 0x007f.

     Codeset 2 consists of the values who have the bits 0x8080 set.

     Codeset 3 consists of the values 0x0080 - 0x00ff.

     Codeset 4 consists of the values 0x8000 - 0xff7f excluding the values
     which have the 0x0080 bit set.
```

Read the line in pairs: code set 1 is one byte long, code set 2 two bytes, code set 3 two bytes (the shift byte and one more), code set 4 three bytes, and each pair's second number is the mask that stamps the code set's identity into the `wchar_t`, so that the two bits `0x8080` alone say which table a value came from. This is a description of what a `wchar_t` holds under a BSD EUC locale, and it is the reason [`multibyte(3)`](multibyte.md) finds that a `wchar_t` on this Mac is not a code point: under `ja_JP.eucJP` the value for `b0 a1` is `0xb0a1`, the two bytes packed, and the experiment below shows the 2026 library packing the shift byte in as well, which the 2003 formula said it removed. Note also a slip on the page itself: it says *Codesets 2 and 3 are special in that the leading byte (0x8e or 0x8f) is first removed*, but by its own definitions `0x8e` and `0x8f` introduce code sets 3 and 4.

### `big5(5)`: one paragraph

```text title="man 5 big5, macOS 26.6.2, dumped 2026-09-13"
     "Big Five" is the de facto standard for encoding Traditional Chinese
     text.  Each character is represented by either one or two bytes.
     Characters from the ASCII character set are represented as single bytes
     in the range 0x00 - 0x7F.  Traditional Chinese characters are represented
     by two bytes: the first in the range 0xA1 - 0xFE, the second in the range
     0x40 - 0xFE.
```

*De facto* is the operative phrase: Big5 was a vendor agreement in Taiwan, never a national standard, and `charsets(7)` adds that it is not ISO 2022 compliant, meaning its trail bytes go below `0x80`. That is the property to notice. A trail byte in `0x40`–`0x7E` is an ASCII byte, `@`, a letter, `[`, `\`, `]`, `{`, `|`, `}`, and a program that scans Big5 bytes for ASCII punctuation will find it inside characters: the experiment below decodes `a4 5c` as one character, and the backslash is its second half. The Mac's locale list has both `zh_TW.Big5` and `zh_HK.Big5HKSCS`, the Hong Kong extension the page does not mention.

### `gb2312(5)`, `gbk(5)`, `gb18030(5)`: three supersets

```text title="man 5 gb2312 / gbk / gb18030, macOS 26.6.2, dumped 2026-09-13"
     Simplified Chinese characters are represented
     by two bytes, both in the range 0xA1-0xFE.                       (gb2312)

     Chinese characters are represented by two
     bytes, beginning with a byte in the range 0x80-0xFE and ending with a
     byte in the range 0x40-0xFE.                                     (gbk)

     Characters that are represented by two bytes begin with a byte in the
     range 0x81-0xFE and end with a byte either in the range 0x40-0x7E or
     0x80-0xFE.

     Characters that are represented by four bytes begin with a byte in the
     range 0x81-0xFE, have a second byte in the range 0x30-0x39, a third byte
     in the range 0x81-0xFE and a fourth byte in the range 0x30-0x39.  (gb18030)
```

Three pages, three byte grammars, each a superset of the last. GB 2312 is the EUC form of the 1980 mainland standard, both bytes above `0xA0`, 7,445 characters. GBK (*Guojia biaozhun kuozhan*, national standard extension, and the `STANDARDS` section is candid: *GBK is not a standard*) keeps every GB 2312 pair and widens the trail byte down to `0x40`, which is where the backslash comes in: `bf 5c` is one GBK character and two Latin-1 ones, and [Two readers, one byte string](../../12_Adversarial/parser_differentials/README.md) is the page about what happens when an escaping routine sees the second half. GB 18030 keeps every GBK pair and adds the four-byte form, whose second and fourth bytes are ASCII digits `0`–`9`. Count the positions: 126 × 10 × 126 × 10 is 1,587,600, the page's *over 1.5 million*, and the form is a linear number: `81 30 81 30` is `U+0080`, `84 31 A4 39` is `U+FFFF`, and `90 30 81 30` begins `U+10000`, from which the 1,048,576 code points above the BMP run in order to `E3 32 9A 35` = `U+10FFFF`. That makes GB 18030 a Unicode transformation format by another name, one Chinese regulation requires software sold there to support; the page says it *provides code space for all Unicode 3.0 code points*, and the experiment below finds that Ubuntu's `iconv` uses all of it and this Mac's uses the BMP only.

### `mskanji(5)`: Shift-JIS as Microsoft shipped it

```text title="man 5 mskanji, macOS 26.6.2, dumped 2026-09-13"
     Characters from the ASCII/JIS-Roman character set are encoded as single
     bytes between 0x00 and 0x7F (ASCII) or 0xA1 and 0xDF (Half-width
     katakana).

     Characters from the JIS X 0208 character set are encoded as two bytes.
     The first ranges from 0x81 - 0x9F, 0xE0 - 0xEA, 0xED - 0xEE (not JIS:
     NEC-selected IBM extended characters), 0xF0 - 0xF9 (not JIS: user
     defined), or 0xFA - 0xFC (not JIS: IBM extended characters).  The second
     byte ranges from 0x40 - 0xFC, excluding 0x7F (delete).
```

The name is the Windows name: code page 932, and `iconv` on both machines accepts `CP932` and `WINDOWS-31J` for it as well as `SJIS` and `SHIFT_JIS`. Three things on this page are worth slowing down for. First, the trail byte range `0x40`–`0xFC` contains every ASCII letter and digit and the punctuation `[ \ ] ^ _ \` { | } ~`, so a Shift-JIS file cannot be searched for `\` or `|` byte-wise; `83 5c` is the katakana ソ, and the experiment below shows both `iconv`s agreeing. Second, *ASCII/JIS-Roman* is written as if it were one set, and it is not: JIS X 0201 Roman has ¥ at `0x5C` and an overline at `0x7E`, which is why a Japanese Windows path separator draws as a yen sign, and the two names `SHIFT_JIS` and `CP932` decode those two bytes differently on both machines. Third, the *not JIS* ranges are the vendor additions that make CP932 more than the standard, and they are the reason `81 7c` is `U+2212 MINUS SIGN` under one name and `U+FF0D FULLWIDTH HYPHEN-MINUS` under the other.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| `ENCODING "EUC"`, `VARIABLE` | Lines of a `mklocale(1)` source file: which decoder the compiled `LC_CTYPE` uses, and its parameters | [`utf8(5)` and `utf-8(7)`](utf8.md) |
| codeset | One of the up-to-four character tables an EUC stream can draw from; the lead byte says which | [Code pages](../../02_Characters/code_pages/README.md) |
| single shift, `0x8e`, `0x8f` | SS2 and SS3: a byte meaning *the next character only comes from code set 3 (or 4)*; the stream then returns to code set 2 | [Code pages](../../02_Characters/code_pages/README.md) |
| `len`, `mask`, *ANDed with ~mask and ORed with maskN* | The recipe for packing a character's bytes into a `wchar_t` and stamping it with its code set | [`multibyte(3)`](multibyte.md) |
| wide character, `wchar_t` | The C type a multibyte character decodes to; on this Mac its value is the packed bytes, not a code point | [`multibyte(3)`](multibyte.md) |
| 94×94 | The grid every national two-byte set is laid out on (from `charsets(7)`): row and column each written as one byte, `0x21`–`0x7E` bare or `0xA1`–`0xFE` with the high bit set | [`charsets(7)` and the code-page pages](charsets.md) |
| JIS X 0201, JIS X 0208 | Japan's one-byte set (ASCII-like Roman plus half-width katakana) and its main two-byte kanji set | [`charsets(7)` and the code-page pages](charsets.md) |
| half-width katakana | The 63 katakana of JIS X 0201, one byte each at `0xA1`–`0xDF` in Shift-JIS and behind SS2 in EUC-JP; *half-width* because they take one terminal column | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| GB 2312-1980, GB 11383-1981 | The 1980 mainland Chinese character set, and the page's name for China's national edition of ASCII | [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) |
| GBK, *Guojia biaozhun kuozhan* | *National standard extension*: GB 2312 plus every CJK ideograph of Unicode 2.1, in the wider trail-byte range | [Two readers, one byte string](../../12_Adversarial/parser_differentials/README.md) |
| GB 18030-2000 | The 2000 standard that made the four-byte form mandatory, so that all of Unicode fits; reissued since (2005, 2022) | [Why UTF-16 stayed](../../09_History/why_utf16_stayed/README.md) |
| Unihan Extension A | The 6,582 extra CJK ideographs Unicode 3.0 added at `U+3400`; GB 18030 was the first national encoding to carry them | [Unicode code points](../../02_Characters/unicode_code_points/README.md) |
| Big Five, "Big5" | Taiwan's de facto two-byte encoding for Traditional Chinese; named, by the usual account, for the five companies that agreed it | [Code pages](../../02_Characters/code_pages/README.md) |
| lead byte, trail byte | The first and second byte of a two-byte character; the page's *first in the range* and *second in the range* | [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) |
| MS Kanji, Shift-JIS, SJIS, CP932 | Four names for the Japanese encoding Microsoft shipped; `iconv` takes `SJIS`, `SHIFT_JIS`, `CP932`, `MS_KANJI` and `WINDOWS-31J` but not the page's own `MSKanji` | [`iconv(1)` and `iconv(3)`](iconv.md) |
| *not JIS: NEC-selected IBM extended characters* | Vendor additions to JIS X 0208 that live in CP932 and not in the national standard; why two decoders can disagree on one byte pair | [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) |
| `ja_JP.eucJP`, `zh_CN.GB18030`, `zh_TW.Big5` | Locale names on this Mac whose `LC_CTYPE` half is one of these decoders | [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) |
| *superset* | Every byte sequence valid in the smaller encoding is valid, and means the same character, in the larger one; true of GB 2312 → GBK → GB 18030, false of Latin-1 → Windows-1252 | [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) |
| *is believed to be compatible with* | The page's honest hedge: the decoder was written from the standard's text, not certified against it | [What the page does not say](../what_the_page_does_not_say/README.md) |

## Try it on your machine

**Where the pages are.** Six on the Mac, none on Ubuntu.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: which pages exist is a fact about the machine."
                       macOS                                                          ubuntu:24.04
$ man -w 5 euc         .../MacOSX.sdk/usr/share/man/man5/euc.5                        No manual entry for euc in section 5
$ man -w 5 gbk         .../MacOSX.sdk/usr/share/man/man5/gbk.5                        No manual entry for gbk in section 5
$ man -w 5 mskanji     .../MacOSX.sdk/usr/share/man/man5/mskanji.5                    No manual entry for mskanji in section 5
$ man -w 7 charsets    No manual entry for charsets                                   /usr/share/man/man7/charsets.7.gz
```

**The trail byte that is a backslash, and the byte that is a yen sign.** Bytes through `iconv -f NAME -t UTF-8`, shown as the character and its UTF-8. Byte-identical on both machines.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39): byte-identical on both. Not machine-checked."
  bytes    -f SHIFT_JIS         -f CP932             -f GBK               -f BIG5              -f LATIN1
  83 5c    ソ  e382bd           ソ  e382bd           .                    .                    \x83 \  c2835c
  bf 5c    .                    .                    縗  e7b897           .                    ¿ \     c2bf5c
  a4 5c    .                    .                    .                    么  e4b988           .
  5c       ¥   c2a5             \   5c               \   5c               \   5c               \       5c
  7e       ‾   e280be           ~   7e               .                    .                    .
  81 7c    −   e28892 U+2212    －  efbc8d U+FF0D    .                    .                    .
```

Row one is the `mskanji(5)` trail-byte range at work: `5c` is the second half of ソ, and `83 5c` is one character to every Japanese decoder and *a control byte and a backslash* to a Latin-1 one. Rows two and three are the same property in GBK and Big5, the measurement behind [Two readers, one byte string](../../12_Adversarial/parser_differentials/README.md). Row four is the *ASCII/JIS-Roman* elision: the name `SHIFT_JIS` decodes `5c` as JIS X 0201 (¥) and the name `CP932` as ASCII (`\`), on both machines, and a Japanese file has no way to say which it meant. Row six is one of the *not JIS* vendor differences in a single byte pair.

**Which names `iconv -l` accepts.** Tested with `printf 'A' | iconv -f NAME -t UTF-8`; the same 20 accepted and the same one refused on both machines. `MSKANJI`, the page's own `ENCODING` name without its underscore, is the refusal; `MS_KANJI` works.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04: identical. Not machine-checked."
accepted: SJIS SHIFT_JIS SHIFT-JIS CP932 MS_KANJI WINDOWS-31J EUC-JP EUCJP GB2312 EUC-CN EUCCN GBK CP936 GB18030 BIG5 BIG-5 CP950 EUC-KR EUCKR CP949
refused:  MSKANJI
```

**GB 2312 ⊂ GBK ⊂ GB 18030, and the four-byte form.** Each character encoded from UTF-8 into the three names; *refused* is `iconv` exiting 1 with no output.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39). Not machine-checked."
                       macOS                                    ubuntu:24.04
                       GB2312     GBK        GB18030            GB2312     GBK        GB18030
  中  U+4E2D           d6d0       d6d0       d6d0               d6d0       d6d0       d6d0
  縗  U+7E17           refused    bf5c       bf5c               refused    bf5c       bf5c
  é   U+00E9           a8a6       a8a6       a8a6               a8a6       a8a6       a8a6
  ż   U+017C           refused    7a  ('z')  81309734           refused    refused    81309734
  €   U+20AC           refused    a2e3       3f ('?'), exit 1   refused    80         a2e3
  😀  U+1F600          refused    refused    refused            refused    refused    9439fc36

$ printf '\x90\x30\x81\x30' | iconv -f GB18030 -t UTF-32BE | xxd -p
                       Illegal byte sequence                    00010000
$ printf '\xe3\x32\x9a\x35' | iconv -f GB18030 -t UTF-32BE | xxd -p
                       Illegal byte sequence                    0010ffff
$ python3 -c "print('😀'.encode('gb18030').hex(' '))"
                       94 39 fc 36                              94 39 fc 36
```

Rows one to three are the superset chain as the pages describe it: what GB 2312 can write, GBK writes with the same bytes, and GB 18030 likewise. Row four is the four-byte form, `81 30 97 34` for ż, identical on both. The last two rows are where the machines part. GNU's GB18030 decodes `90 30 81 30` as `U+10000` and `E3 32 9A 35` as `U+10FFFF`, the whole of Unicode as the page promises; Apple's refuses every four-byte sequence above the BMP, and Python's own codec on the same Mac (last row) has no such limit. Two smaller differences are also real: Apple's GBK quietly writes `z` for ż and exits 0 where GNU refuses, and GNU's `GBK` puts € at `80`, the Microsoft code page 936 position, where Apple's puts it at GB 18030's `a2 e3`. Which table a name selects is a fact about the implementation, not the name: [`iconv`](../../06_Terminal/iconv/README.md).

**EUC: the same two bytes under three names, and the `VARIABLE` line in a `wchar_t`.** The first block is `iconv` on both machines, byte-identical; the second is a C program calling `mbrtowc(3)` under the Mac's own locales, which Ubuntu does not have.

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04 (iconv rows identical on both); mbrtowc rows are macOS only, the container has no such locales. Not machine-checked."
$ printf '\xb0\xa1' | iconv -f EUC-JP -t UTF-8      亜   (JIS X 0208 row 16, column 1)
$ printf '\xb0\xa1' | iconv -f EUC-KR -t UTF-8      가   (KS X 1001 row 16, column 1)
$ printf '\xb0\xa1' | iconv -f EUC-CN -t UTF-8      啊   (GB 2312 row 16, column 1)
$ printf '\x8e\xb1' | iconv -f EUC-JP -t UTF-8      ｱ    (SS2: code set 3, half-width katakana)
$ printf '\x8f\xb0\xa1' | iconv -f EUC-JP -t UTF-8  丂   (SS3: code set 4, JIS X 0212)
$ printf '\x8e\xb1' | iconv -f EUC-CN -t UTF-8      illegal input sequence   (EUC-CN has no code set 3)

mbrtowc() on this Mac, setlocale(LC_CTYPE, ...) then the bytes:
ja_JP.eucJP   b0 a1      -> 2 bytes, wchar_t = 0xb0a1
ja_JP.eucJP   8e b1      -> 2 bytes, wchar_t = 0x8eb1
ja_JP.eucJP   8f b0 a1   -> 3 bytes, wchar_t = 0x8fb0a1
ja_JP.eucJP   41         -> 1 bytes, wchar_t = 0x0041
zh_CN.eucCN   bf 5c      -> 2 bytes, wchar_t = 0xbf5c
ja_JP.SJIS    83 5c      -> 2 bytes, wchar_t = 0x835c
en_US.UTF-8   c3 a9      -> 2 bytes, wchar_t = 0x00e9
```

The first three lines are code set 2 being *national*: the frame is the same, the table behind it is Japanese, Korean or Chinese, and the bytes do not say which. The `mbrtowc` lines are the `VARIABLE` line's promise checked against the library. Code set 2 comes back as the page says, the bytes packed with `0x8080` set. Code sets 3 and 4 do not: the page says the shift byte is *first removed* and code set 3 is `0x0080`–`0x00ff`, and the library returns `0x8eb1` and `0x8fb0a1`, the shift byte packed in with the rest. The `zh_CN.eucCN` line shows what neither page nor library checks: `5c` is not a legal code set 2 trail byte, and `mbrtowc` returns it packed anyway, where GNU's `iconv -f EUC-CN` refuses the pair.

**The locales are still here.** What `locale -a` lists, what `locale charmap` says a locale's encoding is, and how many characters `wc -m` counts in `83 5c`.

```text title="Measured 2026-09-13 — macOS 26.6.2. Not machine-checked."
$ locale -a | grep -E 'eucJP|SJIS|GB|Big5|eucKR|eucCN|CP949'
ja_JP.SJIS ja_JP.eucJP ko_KR.CP949 ko_KR.eucKR zh_CN.GB18030 zh_CN.GB2312 zh_CN.GBK zh_CN.eucCN zh_HK.Big5HKSCS zh_TW.Big5
$ LC_ALL=ja_JP.SJIS locale charmap        SJIS
$ LC_ALL=zh_CN.GB18030 locale charmap     GB18030
$ printf '\x83\x5c' | LC_ALL=ja_JP.SJIS wc -m       1
$ printf '\x83\x5c' | LC_ALL=en_US.UTF-8 wc -m      wc: stdin: Illegal byte sequence   2
$ printf '\x83\x5c' | LC_ALL=C wc -m                2
$ ls -l /usr/share/locale/zh_CN.GB18030/LC_CTYPE    74664 bytes    (ja_JP.SJIS: 22116; zh_CN.GBK: 29304; zh_CN.GB2312 and zh_CN.eucCN: 26952, identical files)
```

One byte string, three counts, and the only thing that changed is the `LC_CTYPE` named on the command line: [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md). The file sizes are the tables the pages leave out, and the identical `GB2312` and `eucCN` files are the page's own claim that they are one encoding under two names.

## Where the page is dated, and what it does not say

**All six are dated 2003**, and the newest things they cite are Unicode 3.0 (2000) and GB 18030-2000. GB 18030 has been reissued twice since (2005 and 2022 editions), Unicode is at 16 on this Mac's Python, and `gb2312(5)`'s *still in wide use* was true of 2003. The `wchar_t` recipe in `euc(5)` describes the library as it was when the page was written; the library that ships beside the page today packs the shift byte in and the page still says it is removed.

**`euc(5)` contradicts itself** about which code sets the single shifts introduce (see above), and no page in the family says what happens to a trail byte outside the stated range. The measurement is that this Mac's `mbrtowc` accepts it silently and GNU's `iconv` refuses it.

**`gb18030(5)` says *all Unicode 3.0 code points*** and this Mac's `iconv` stops at `U+FFFF`. The page is right about the encoding and wrong about the machine it ships on, the reverse of the usual case on [A page has a date](../a_page_has_a_date/README.md).

**`mskanji(5)` writes *ASCII/JIS-Roman* as one set** and never mentions that `0x5C` is ¥ in one and `\` in the other, the single most-reported Shift-JIS problem. Nor does it give the encoding's Windows name, `CP932`, which is the name most files that use it were written under.

**None of the pages names a Unicode mapping**, though every use of these encodings today is a conversion to or from UTF-8, and none names the `iconv` aliases the experiment above had to discover by trial. `MSKanji`, the page's own `ENCODING` string, is not one of them.

**None of them exists on Linux**, and `charsets(7)` does not point at them, so a reader on Ubuntu has no way to learn that a fuller description of EUC-JP is one `ssh` away on a Mac.

## See also

- [`utf8(5)` and `utf-8(7)`](utf8.md) — the seventh section-5 encoding page, and the one that replaced these
- [`multibyte(3)`](multibyte.md) — the functions that run these decoders, and why `wchar_t` here is packed bytes rather than a code point
- [`iconv(1)` and `iconv(3)`](iconv.md) — the tool every experiment above ran, and the page on its names and its `//TRANSLIT`
- [`charsets(7)` and the code-page pages](charsets.md) — Linux's one page on this subject, and the single-byte encodings beside it
- [Code pages](../../02_Characters/code_pages/README.md) — what a byte above `0x7F` means before somebody names a table
- [Two readers, one byte string](../../12_Adversarial/parser_differentials/README.md) — the GBK trail byte `5c` eating a backslash, as an exploit
- [SAP code pages](../../07_Real_Data/sap_code_pages/README.md) — the same encodings under SAP's, IBM's and Microsoft's numbers
- [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) — where a 94×94 character set ends and an encoding of it begins
- [Why UTF-16 stayed](../../09_History/why_utf16_stayed/README.md) — the other fixed-width answer, and why GB 18030 is the one Chinese law requires
- [The encoding man pages nobody opens](../the_encoding_man_pages/README.md) — where these six sit among the forty
