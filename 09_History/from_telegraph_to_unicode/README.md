# From the telegraph to Unicode

**Level:** 201 · for anyone starting from zero

**One line:** Nobody designed the mess — it is six sensible decisions, each made under a real constraint, each leaving a scar you still step on: the case bit, `\r\n`, `latin-1` as a byte hack, `.length` counting the wrong thing, and the SAP extract that is not ASCII at all.

## Why a history page in a library about bytes

Because almost everything confusing about text is a *fossil*. `'A' | 0x20` gives `'a'` because a committee in 1963 put the alphabets exactly 32 apart. Windows ends a line with two bytes because a teletype needed time to move its carriage back. Java's `.length` says a smiling face is two characters because in 1991 sixteen bits looked like enough for every script on earth. None of that is arbitrary, and none of it is explicable from the code — you have to know what problem was being solved and what it cost.

Six eras, one line of text, and each era's constraint:

| Era | The constraint | What they did | The scar you still meet |
|---|---|---|---|
| 1874 | five bits on a wire | shift codes: a mode saying "letters follow" / "figures follow" | stateful encodings — lose the mode and the rest is gibberish |
| 1963 | seven bits, one committee | [ASCII](../../02_Characters/a_character_is_a_number/README.md): 128 characters, laid out deliberately | `x ^ 0x20` flips case; `ord(c) - ord('0')` is a digit |
| 1964 | punched-card hardware | EBCDIC: IBM's own numbering, letters not contiguous | the mainframe extract where `A` is `0xC1` |
| 1980s | 256 slots, many alphabets | [code pages](../../02_Characters/code_pages/README.md): everyone claimed the top half | `0xE9` means six different letters; [mojibake](../../03_Encodings/mojibake/README.md) |
| 1980s | thousands of characters | double-byte tables — Shift-JIS, EUC, Big5 | a byte in the middle could be half a character |
| 1991 | one number for everything | [Unicode](../../02_Characters/unicode_code_points/README.md) code points | `len()` is not what a person calls a character |
| 1996 | 65,536 was not enough | surrogates, and a ceiling at U+10FFFF | `.length == 2` for one emoji, in Java and JavaScript |
| 1992 | write those numbers as bytes | [UTF-8](../why_utf8_won/README.md) — and it took until 2008 to win | none, which is the point of the next page |

The rest of this page is that table, run.

## The five-bit era, and the idea that never died

Baudot's telegraph code carried five bits, so 32 patterns, and the alphabet alone needs 26. The answer was not more bits — bits were the expensive thing — but a **mode**: one code meant "everything after this is letters", another meant "everything after this is figures", and 32 patterns did the work of 62.

That trade is still being made. ISO-2022-JP switches into Japanese with an escape sequence and back out with another; a terminal's colours are the same idea; so is every "the next byte means something different" protocol you have debugged. And so is the failure: a corrupted mode byte does not damage one character, it damages **everything after it**. Section 5 of the program below shows a Japanese string doing exactly this, in 2026, in Python's standard library.

## ASCII was designed, and the design leaked into your code

The 1963 committee had seven bits and used them carefully: digits at `0x30` so a digit's value is its code minus `0x30`; the two alphabets at `0x41` and `0x61` so they are exactly one bit apart. That is why `tr 'a-z' 'A-Z'` is a mask, not a lookup table. [A character is a number](../../02_Characters/a_character_is_a_number/README.md) is the whole lesson.

The consequence that matters here is the *other* 128 patterns. Seven bits in an eight-bit byte leaves 128 slots belonging to nobody, and everybody took them.

## IBM had already gone the other way

The System/360 arrived in 1964 with **EBCDIC**, numbered from the holes in a punched card rather than from a committee's grid. It does not agree with ASCII about anything: `A` is `0xC1`, space is `0x40`, and — the part that breaks code rather than just text — **the alphabet has gaps**. `I` is `0xC9` and `J` is `0xD1`, so a loop from `'A'` to `'Z'` walks through eight characters that are not letters. The sort order is inverted too: digits come *after* letters, lowercase *before* uppercase.

This is not history for its own sake if you work near a mainframe. An SAP extract from a non-Unicode system, a COBOL fixed-width file, an MVS dataset: all still EBCDIC, and none of them are recoverable by "try Latin-1". See [SAP code pages](../../07_Real_Data/sap_code_pages/README.md).

## The code-page decades, and the two things people forget

Everyone filled the top 128 slots differently — that is the famous part, and [Code pages](../../02_Characters/code_pages/README.md) is the lesson. Two things get left out:

**The file never says which table it used.** There is no header, no marker, nothing. "Which encoding is this?" is not a question the bytes can answer, which is why every guess-the-encoding library is a heuristic and why the answer has to come from the protocol instead.

**The tables were incomplete, not just incompatible.** No 8-bit table holds Polish and Greek at the same time. A single European organisation with offices in Kraków and Athens could not put both addresses in one file — not "it looked wrong", but *there was no byte to write*. That, and not tidiness, is the argument that finally won.

## Then 1991, and then 1996

Unicode's proposal is one sentence: give every character in every script one number, and stop arguing. The number is the **code point**, `U+00E9`, and it says nothing about bytes — which is the distinction chapter 2 exists to build.

The first design was 16 bits, and in 1991 that was a defensible call. Windows NT, Java and JavaScript all shipped 16-bit characters on the strength of it. Then in 1996 Unicode 2.0 raised the ceiling to U+10FFFF — about 1.1 million slots — and paid for it with **surrogate pairs**: characters above `U+FFFF` are written as *two* 16-bit units. Those three platforms could not change; their strings are UTF-16 to this day, which is why `"😀".length` is `2` in JavaScript and `1` in Python.

Unicode 17.0 (September 2025) defines 159,801 characters, and 18.0 is due this month — so the 1996 ceiling has held for thirty years, and the 1991 one would have been full long ago.

## In Python

<!-- output:from_telegraph_to_unicode_py -->
*Verified output of [`from_telegraph_to_unicode_py.py`](examples/from_telegraph_to_unicode_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FIVE BITS (1874): THE ARITHMETIC THAT FORCED A SHIFT KEY
------------------------------------------------------------------------
   patterns in 5 bits : 2**5 = 32
   letters + digits + a little punctuation : 48
   enough? False
   The fix was a MODE, not more bits: one code said 'letters follow',
   another said 'figures follow', so 32 patterns carried 62 meanings.
   Shift state is the oldest idea in this library — and the oldest bug:
   a lost shift code turns the rest of the message into gibberish.

2. SEVEN BITS (ASCII, 1963/1967): 128 AGREED, 128 UNCLAIMED
------------------------------------------------------------------------
   patterns in 7 bits : 128      patterns in 8 : 256
   'A'   ->  65  0x41  01000001   top bit 0
   'z'   -> 122  0x7A  01111010   top bit 0
   '0'   ->  48  0x30  00110000   top bit 0
   Every ASCII byte has its top bit 0. The other 128 patterns belonged
   to nobody, and that vacancy is the whole of the next forty years.

3. EBCDIC (IBM, 1964): THE OTHER NUMBERING, STILL SHIPPING
------------------------------------------------------------------------
   IBM's System/360 came out a year after ASCII with its own table,
   inherited from punched cards. It does not even agree about 'A'.
   A      ASCII 0x41    EBCDIC 0xC1
   a      ASCII 0x61    EBCDIC 0x81
   0      ASCII 0x30    EBCDIC 0xF0
   space  ASCII 0x20    EBCDIC 0x40

   The alphabet is not contiguous — punched-card rows left two gaps:
      H=0xC8 I=0xC9 J=0xD1 K=0xD2 Q=0xD8 R=0xD9 S=0xE2
   so 'B' - 'A' == 1 but 'J' - 'I' == 8. Loops over letter codes break.

   And the sort order is inverted at every level:
     by ASCII byte  : ['3rd', 'Alpha', 'Zoe', 'apple']
     by EBCDIC byte : ['apple', 'Alpha', 'Zoe', '3rd']
   digits-then-caps-then-lower, versus lower-then-caps-then-digits.
   Reading an EBCDIC file as ASCII is not mojibake, it is nonsense:
     0x41, which is 'A' in ASCII, is '\xa0' in EBCDIC — NO-BREAK SPACE, not a letter at all.

4. CODE PAGES (1980s): EVERYBODY CLAIMED THE TOP HALF
------------------------------------------------------------------------
   The same byte, 0xE9, decoded under the tables that were shipping:
     0xE9 under latin_1    -> 'é'     (Western Europe, ISO 8859-1)
     0xE9 under cp1252     -> 'é'     (Windows Western)
     0xE9 under iso8859_2  -> 'é'     (Central Europe, ISO 8859-2)
     0xE9 under cp1250     -> 'é'     (Windows Central Europe)
     0xE9 under cp437      -> 'Θ'     (the original IBM PC)
     0xE9 under cp850      -> 'Ú'     (PC Western Europe)
     0xE9 under koi8_r     -> 'И'     (Russian)
     0xE9 under mac_roman  -> 'È'     (classic Mac OS)
     0xE9 under cp037      -> 'Z'     (EBCDIC)
   9 tables, 6 answers, and the file says which one it used: nowhere.

   They were also INCOMPLETE, which is the part people forget.
   No 8-bit table holds Polish and Greek and Japanese at once:
     'Łódź καλημέρα' in latin_1    -> UnicodeEncodeError on 'Ł'
     'Łódź καλημέρα' in cp1250     -> UnicodeEncodeError on 'κ'
     'Łódź καλημέρα' in iso8859_2  -> UnicodeEncodeError on 'κ'

5. DOUBLE BYTES (1980s): ASIA NEVER FIT IN 256 AT ALL
------------------------------------------------------------------------
   日本語 in shift_jis   -> 93 fa 96 7b 8c ea                      (6 bytes)
   日本語 in euc_jp      -> c6 fc cb dc b8 ec                      (6 bytes)
   日本語 in iso2022_jp  -> 1b 24 42 46 7c 4b 5c 38 6c 1b 28 42    (12 bytes)
   日本語 in utf_8       -> e6 97 a5 e6 9c ac e8 aa 9e             (9 bytes)
   Three legacy encodings, three different byte strings for the same
   three characters. And look at iso2022_jp: 1b 24 42 is an ESCAPE that
   switches the reader into Japanese and 1b 28 42 switches it back — the
   1874 shift code again, 110 years later, with the same failure mode.
   In shift_jis and euc_jp a byte in the middle of a file could be the
   second half of a character, so you could not scan backwards or split.
   Even inside one region they disagreed: gb2312 cannot hold '語'.

6. UNICODE (1991): NUMBER THE CHARACTERS ONCE, FOR EVERYONE
------------------------------------------------------------------------
   'A'   U+0041       65   LATIN CAPITAL LETTER A
   'é'   U+00E9      233   LATIN SMALL LETTER E WITH ACUTE
   '語'  U+8A9E    35486   CJK UNIFIED IDEOGRAPH-8A9E
   '😀'  U+1F600   128512   GRINNING FACE
   That number is the CODE POINT. Note what has not been said yet:
   nothing at all about how many bytes it takes. That is chapter 3.

7. 1996: THE 16-BIT ASSUMPTION BROKE
------------------------------------------------------------------------
   16 bits holds 65,536 characters. In 1991 that looked like plenty,
   so Windows NT, Java and JavaScript all built 16-bit characters in.
   Unicode 2.0 (1996) raised the ceiling to U+10FFFF = 1,114,112 slots,
   and paid for it with SURROGATES: two 16-bit units for one character.
   café      code points  4   UTF-16 units  4   UTF-8 bytes  5
   Łódź      code points  4   UTF-16 units  4   UTF-8 bytes  7
   日本語    code points  3   UTF-16 units  3   UTF-8 bytes  9
   😀        code points  1   UTF-16 units  2   UTF-8 bytes  4
   '😀' as UTF-16 is d8 3d de 00: the surrogate pair D83D DE00.
   Python counts characters, so len('😀') == 1. Java and JavaScript count
   UTF-16 units, so their .length is 2. Same string, two answers, forever.

8. UTF-8 (1992, WON BY 2008): THE ONE THAT KEPT ASCII WORKING
------------------------------------------------------------------------
   Hi        -> 48 69
   café      -> 63 61 66 c3 a9
   日本語    -> e6 97 a5 e6 9c ac e8 aa 9e
   😀        -> f0 9f 98 80
   Look at 'Hi': an ASCII file is already a UTF-8 file, byte for byte.
   Nothing else on this page could say that, which is why it won.

9. THE SCARS YOU STILL STEP ON
------------------------------------------------------------------------
   ASCII's layout   : chr(ord('a') ^ 0x20) == 'A'   (upper/lower is one bit)
   the teletype     : Windows still ends a line with b'\r\n'
   Latin-1's luck   : it is the only table where byte == code point,
                      so bytes -> latin-1 -> bytes round-trips: True
   the 16-bit era   : len('😀') == 1 here, .length == 2 in JS
   two spellings    : 'é' is c3 a9 composed or 65 cc 81 decomposed,
                      and nfc == nfd is False until you normalize
   bytes vs letters : len('Łódź') == 4, len('Łódź'.encode()) == 7 — a CHAR(4) column is not enough
```
<!-- /output -->

## In the terminal

The same story with no language in between — just `iconv` writing bytes and `xxd` showing what landed.

<!-- output:from_telegraph_to_unicode_sh -->
*Verified output of [`from_telegraph_to_unicode_sh.sh`](examples/from_telegraph_to_unicode_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. 'café' AS EACH ERA WOULD HAVE WRITTEN IT TO DISK
   iconv converts; xxd -p prints the bytes that actually landed.
   CP037     83818651
   LATIN1    636166e9
   CP1252    636166e9
   CP437     63616682
   UTF-8     636166c3a9
   UTF-16BE  00630061006600e9

   CP037 is EBCDIC, and it does not agree even about the 'c'.
   Three of the 8-bit tables give five bytes and disagree on the last.
   UTF-8 is six bytes; UTF-16BE is eight, half of them 00.

2. A POLISH FILE FROM 2005, READ ON FOUR MACHINES
   'Łódź' written under Windows-1250, which is where it lived then:

$ printf '\xc5\x81\xc3\xb3d\xc5\xba' | iconv -f UTF-8 -t CP1250 | xxd -p
a3f3649f

   Those same four bytes, decoded by someone whose machine assumed
   a different table — every one of these 'succeeds':
   read as CP1250      -> Łódź
   read as LATIN1      -> £ód
   read as ISO-8859-2  -> Łód
   read as CP1252      -> £ódŸ
   read as KOI8-R      -> ёСd÷

   Two of those readings look three letters long. They are not — the
   fourth byte decoded to an INVISIBLE control character. Only the bytes
   show it:

$ printf '\xc5\x81\xc3\xb3d\xc5\xba' | iconv -f UTF-8 -t CP1250 | iconv -f LATIN1 -t UTF-8 | xxd -p
c2a3c3b364c29f
   c2 9f is U+009F, a C1 control, sitting where the 'ź' was.

   Four bytes, five readings, no error anywhere. The file does not carry
   its table, so 'which encoding is this?' has no answer from the bytes.

3. WHY UTF-8 COULD BE ADOPTED WITHOUT REWRITING ANYTHING

$ printf 'Hello' | iconv -f UTF-8 -t ASCII | xxd -p
48656c6c6f

$ printf 'Hello' | iconv -f UTF-8 -t UTF-8 | xxd -p
48656c6c6f
   Identical. An ASCII file already IS a UTF-8 file, byte for byte, so
   every tool that only knew ASCII kept working the day UTF-8 arrived.
   The 1991 answer, UTF-16, could not say that:

$ printf 'Hello' | iconv -f UTF-8 -t UTF-16BE | xxd -p
00480065006c006c006f
   Different bytes, and full of 00 — which is what ends a string in C.
   Every existing tool would have had to be rewritten on the same day.
```
<!-- /output -->

Note what section 3 of that script says it is *not* doing: converting a character the target table cannot hold. GNU `iconv` refuses; macOS `iconv` transliterates. That difference is real, it is invisible until a colleague runs your script, and it is the reason the failure half of the story is told by the Python example, where the error is the same everywhere.

## If you are coming from Python or ABAP

**Python.** Every era above is a codec that ships with your interpreter: `cp037` is EBCDIC, `cp1252` is the Windows table, `shift_jis` and `euc_jp` are the Japanese ones, `iso2022_jp` is the stateful one. `bytes([0xE9]).decode(cp)` across a list of them is a working time machine, and it is the whole first half of the program above. Two Python-specific fossils: `latin-1` is the only codec that maps all 256 bytes to code points 0–255, which makes `data.decode('latin-1')` the standard trick for carrying arbitrary bytes through a `str` — deliberate, not a bug, and it works *because* of a 1987 accident. And `unicodedata` is a copy of the Unicode character database sitting in your standard library; `unicodedata.name('é')` will tell you exactly which character you have when the screen will not.

**ABAP.** The line this history draws through your working life is the **non-Unicode → Unicode system** conversion. A non-Unicode SAP system stores text in a code page — one byte per character for Latin-1-family languages, and the code-page number is a property of the *system*, not the file. A Unicode system stores UTF-16, so `xstrlen` on the `xstring` of a character field is twice what you expect and `'A'` is `00 41`. `cl_abap_codepage=>convert_to( source = text codepage = 'UTF-8' )` is the explicit conversion, and `cl_abap_char_utilities=>cr_lf` is the two teletype bytes from 1963 with a name. Anything that reads a fixed-width legacy extract — a bank file, an EDI drop, an archived IDoc — is reading one of the eras above, and the interface spec is where the code page is written down, never the file. *(Not machine-checked — CI cannot run ABAP. Code-page numbers must be verified against your own system.)*

## Try it

```bash
cd 09_History/from_telegraph_to_unicode/examples
python3 from_telegraph_to_unicode_py.py
bash from_telegraph_to_unicode_sh.sh
```

Without the machine: your file contains the four bytes `41 42 C1 C2`. Under ASCII the first two are `AB` — what are the last two, and under which table would all four be letters? (Hint: only one table on this page numbers `A` above `0x80`.) And: why can a file written under Latin-1 never fail to decode, while a file written under UTF-8 often does?

## See also

- [Why UTF-8 won](../why_utf8_won/README.md) — the six properties that ended this story, each one run
- [What to do today](../../10_Best_Practices/README.md) — the checklist that falls out of all of it
- [A character is a number](../../02_Characters/a_character_is_a_number/README.md) — ASCII's layout in detail
- [Code pages](../../02_Characters/code_pages/README.md) — the top-half tables, up close
- [Unicode code points](../../02_Characters/unicode_code_points/README.md) — what `U+00E9` actually is
- [The Absolute Minimum Every Software Developer Must Know About Unicode ↗](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/) — Joel Spolsky, 2003; the classic telling, and still the best short one
