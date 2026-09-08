# Windows-1252 vs Latin-1

**Level:** 201 · for anyone repairing data

**One line:** Windows-1252 keeps 224 of Latin-1's 256 mappings and **replaces** the other 32 — it keeps none of them and drops five outright — so it is not a superset, and the five it drops are what decide whether damaged text can be repaired at all.

## The two tables agree on 224 bytes, and that is the problem

These are the two code pages a European interface is most likely to be wrong about, and they are close enough to hide. Every byte below `0x80` is ASCII in both. Every byte from `0xA0` to `0xFF` is the same accented letter in both — `é` is `E9`, `ö` is `F6`, `ß` is `DF`. That is 224 of 256 byte values on which the two tables are indistinguishable.

What is left is the 32 bytes `0x80`–`0x9F`. In ISO-8859-1 that range holds no printable character at all: it is the C1 control range, `U+0080`–`U+009F`, whose control functions are defined by ISO/IEC 6429 and emitted by almost nothing. Microsoft took the range and put the characters a word processor actually needs there — the euro sign, the curly quotes, the en and em dashes, the ellipsis, the bullet.

So a file labelled with the wrong one of these two tables is not garbled. It is **correct except for the punctuation**, and that is the fingerprint: a customer name that reads perfectly, next to a price where the currency symbol has turned into something else, next to a description whose apostrophes have gone strange. Nobody files a ticket about a right-looking name.

## Is it a superset? No, and the count is not close

The claim you will meet everywhere is that Windows-1252 is a superset of Latin-1 — that it keeps everything and adds the missing punctuation on top. A superset would have to preserve every mapping Latin-1 makes. Over the disputed 32 bytes, Windows-1252 preserves **zero** of them. It is a *replacement* of that block, not an extension of it, and section 2 of the run below counts it rather than asserting it.

The distinction sounds academic until you need it. Twenty-seven of the 32 are reassigned to a different character, which means a byte that was a control is now punctuation and vice versa — a substitution, and substitutions are reversible if you know which way round they went. The other five are the ones that matter: `0x81`, `0x8D`, `0x8F`, `0x90` and `0x9D` are **not assigned to anything** in Windows-1252. Latin-1 has a character for all 256 byte values and therefore cannot fail to decode; Windows-1252 decodes 251. Those five holes are the entire difference between a table that always round-trips and one that does not, which is why the [mojibake round trip](../mojibake_round_trip/README.md) turns on them.

And the myth survives for a reason worth naming: because the 32 disputed bytes are C1 controls in Latin-1, and real text does not contain C1 controls, **mislabelling the two usually works**. Ordinary accented text passes through either table unharmed. The bug only appears when somebody types a euro sign or Word inserts a curly apostrophe, which is a small fraction of records and always the same small fraction — so the interface looks stable for months and then fails on one row.

## Not every character tells you which table was used

The natural diagnostic is to look at the mojibake and name the culprit, and for the two tables on this page that only works with the right character. Take `é`, the library's [standard mojibake case](../../CAST.md): its UTF-8 bytes are `C3 A9`, and **both** of these bytes are outside `0x80`–`0x9F`. Read those bytes as Latin-1 and you get `Ã©`; read them as Windows-1252 and you get `Ã©`. Identical. A page full of `Ã©` proves the reader used a one-byte table and says nothing whatever about which one.

The euro sign settles it, because its UTF-8 bytes are `E2 82 AC` and the middle one is inside the disputed block. As Latin-1 that byte is a C1 control; as Windows-1252 it is `‚`, a low quotation mark. So `â‚¬` was read as Windows-1252 and `â` followed by an invisible control and `¬` was read as Latin-1 — and this is the practical reason both `é` and `€` are in the cast. One of them is the damage everybody sees; the other is the damage that identifies the reader.

## What the web decided, and what it does not license

The [WHATWG Encoding Standard ↗](https://encoding.spec.whatwg.org/) lists seventeen labels that resolve to `windows-1252`, and `iso-8859-1`, `latin1`, `ascii` and `us-ascii` are four of them. A browser told a page is Latin-1 decodes it as Windows-1252 deliberately, and has for twenty years, because the web was full of pages that said one and meant the other. The standard's own note is that these labels are synonyms in a web context.

That is a decision about *labels on the web*, made because a browser must render something and cannot ask. It is not a statement that the two tables are the same, and it does not transfer to a file interface, where you can ask — and where the five unassigned bytes decide whether a repair is possible. Treat the browser's leniency as evidence of how common the confusion is, not as permission to inherit it.

## In Python

<!-- output:windows_1252_vs_latin1_py -->
*Verified output of [`windows_1252_vs_latin1_py.py`](examples/windows_1252_vs_latin1_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. WHERE THE TWO TABLES STAND ON EVERY BYTE
------------------------------------------------------------------------
   identical in both tables        224 bytes
   cp1252 maps to a DIFFERENT char  27 bytes
   cp1252 has NO entry at all        5 bytes
                                   256 total

   Every byte in the last two rows lies in 0x80-0x9F, and that
   range is 32 bytes wide -- so the two tables agree everywhere else.

2. SO IS CP1252 A SUPERSET OF LATIN-1?
------------------------------------------------------------------------
   A superset would keep every mapping and add more. Count the bytes
   where cp1252 KEEPS what Latin-1 says, over the disputed 32:
      kept: 0 of 32
   Zero. Every one of the 32 is either given away to another
   character or dropped, so cp1252 REPLACES that block rather than
   extending it. There is no byte on which cp1252 says everything
   Latin-1 says and more -- which is what 'superset' would require.

3. THE DISPUTED BLOCK, SIDE BY SIDE
------------------------------------------------------------------------
   byte   ISO-8859-1        Windows-1252
   0x80   U+0080     €
   0x81   U+0081    --   <- no entry in cp1252
   0x82   U+0082     ‚
   0x83   U+0083     ƒ
   0x84   U+0084     „
   0x85   U+0085     …
   0x86   U+0086     †
   0x87   U+0087     ‡
   0x88   U+0088     ˆ
   0x89   U+0089     ‰
   0x8A   U+008A     Š
   0x8B   U+008B     ‹
   0x8C   U+008C     Œ
   0x8D   U+008D    --   <- no entry in cp1252
   0x8E   U+008E     Ž
   0x8F   U+008F    --   <- no entry in cp1252
   0x90   U+0090    --   <- no entry in cp1252
   0x91   U+0091     ‘
   0x92   U+0092     ’
   0x93   U+0093     “
   0x94   U+0094     ”
   0x95   U+0095     •
   0x96   U+0096     –
   0x97   U+0097     —
   0x98   U+0098     ˜
   0x99   U+0099     ™
   0x9A   U+009A     š
   0x9B   U+009B     ›
   0x9C   U+009C     œ
   0x9D   U+009D    --   <- no entry in cp1252
   0x9E   U+009E     ž
   0x9F   U+009F     Ÿ

   The left column is the C1 control range, U+0080 to U+009F.
   ISO-8859-1 assigns no printable character there at all; the control
   functions that use the range are defined by ISO/IEC 6429, and almost
   nothing emits them. That is why the block was available to take.

4. THE FIVE BYTES CP1252 LEAVES EMPTY
------------------------------------------------------------------------
   0x81 0x8D 0x8F 0x90 0x9D

   Latin-1 maps all 256 byte values, so decoding under it CANNOT fail.
   cp1252 maps 251. Those five are the difference between a table that
   always round-trips and one that does not, which is the subject of
   the mojibake round-trip page.
      latin-1  decodes 256 of 256 single bytes
      cp1252   decodes 251 of 256 single bytes

5. THE EURO IS THE SHARPEST SINGLE CASE
------------------------------------------------------------------------
   '€' in cp1252     -> 80
   '€' in Latin-1    -> UnicodeEncodeError: ordinal not in range(256)

   ISO-8859-1 dates from 1987 and the euro sign postdates it by about a
   decade, so the character is simply not in that table. This is why an
   interface declared as Latin-1 can never carry a euro sign, whatever
   the sender does -- ISO-8859-15 was published to add it, at 0xA4.

6. WHICH TABLE WAS WRONGLY APPLIED? NOT EVERY CHARACTER TELLS YOU
------------------------------------------------------------------------
   Take UTF-8 bytes and read them under each of the two tables.

   'é' = c3 a9
      as Latin-1 : '\xc3\xa9'
      as cp1252  : '\xc3\xa9'
      IDENTICAL -- tells you nothing

   '€' = e2 82 ac
      as Latin-1 : '\xe2\x82\xac'
      as cp1252  : '\xe2\u201a\xac'
      DIFFERENT -- names the table

   The reason is in section 1: the two tables differ only on 0x80-0x9F.
   The bytes of 'e-acute' are 0xC3 0xA9, both outside that block, so
   both tables give the same garbage. The euro's UTF-8 bytes include
   0x82, which IS inside it -- so the middle character differs, and
   that one character names the table the reader used.

7. WHAT THE WEB DECIDED
------------------------------------------------------------------------
   The WHATWG Encoding Standard lists 17 labels for windows-1252, and
   'iso-8859-1', 'latin1', 'ascii' and 'us-ascii' are four of them --
   so a browser told a page is Latin-1 reads it as cp1252 on purpose,
   and so does one told the page is ASCII.

   That is a decision about labels on the web. It is NOT a licence to
   treat the two as interchangeable in a file interface, where the
   five unassigned bytes decide whether a repair is possible at all.
   Label list checked against https://encoding.spec.whatwg.org/,
   2026-09-07.
```
<!-- /output -->

## In the terminal

<!-- output:windows_1252_vs_latin1_sh -->
*Verified output of [`windows_1252_vs_latin1_sh.sh`](examples/windows_1252_vs_latin1_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE BYTE, TWO TABLES
------------------------------------------------------------------------
   the file is one byte: 80

   read as ISO-8859-1, written out as UTF-8:
      c280   (U+0080, a C1 control)
   read as CP1252, written out as UTF-8:
      e282ac   (U+20AC, the euro sign)

   Same byte on disk. The table is not in the file, so the reader
   supplies it -- and these two readers disagree about this byte.

2. THE EURO CANNOT BE WRITTEN AS LATIN-1 AT ALL
------------------------------------------------------------------------
   euro as UTF-8: e282ac
   UTF-8 -> CP1252      exit=0   bytes: 80
   UTF-8 -> ISO-8859-1  exit=1   bytes written: 0

   Not a bug and not a setting: the character is absent from the table,
   so there is nothing to write. An interface contract that says
   Latin-1 has ruled out the euro sign, whatever the sender intends.
   (The message text differs between BSD and GNU iconv, so only the
   exit status is shown.)

3. THE FINGERPRINT: WHICH TABLE DID THE READER USE?
------------------------------------------------------------------------
   e-acute as UTF-8 is c3a9, read back as...
      ISO-8859-1   -> c383c2a9
      CP1252       -> c383c2a9
      the two are identical, so this character names no table

   euro as UTF-8 is e282ac, read back as...
      ISO-8859-1   -> c3a2c282c2ac
      CP1252       -> c3a2e2809ac2ac
      these differ, so this character DOES name the table

   The rule behind it: the two tables differ only on 0x80-0x9F. The
   euro's UTF-8 bytes include 0x82; e-acute's (c3 a9) do not.

4. HOW MANY BYTES OF THE DISPUTED BLOCK EACH TABLE ACCEPTS
------------------------------------------------------------------------
   Converting each of the 32 bytes 0x80-0x9F to UTF-8, one at a time,
   and counting how many the table can turn into a character:
      ISO-8859-1   accepts 32 of 32
      CP1252       accepts 27 of 32

   Latin-1 has a character for every byte; CP1252 is missing five.
   Convert to UTF-8 to ask this question, never CP1252 to CP1252 --
   see the note on the page for why the same-to-same form is not
   portable.
```
<!-- /output -->

### One command that is not portable, and the one that is

The obvious way to ask *"is this byte valid in CP1252?"* on a pipe is the same-to-same validator, `iconv -f CP1252 -t CP1252`. It does not work, and it fails in the quiet direction:

```text
                     one byte 0x81, which CP1252 does not assign
  iconv -f CP1252 -t CP1252   BSD: exit 0, byte passed through   GNU: exit 1
  iconv -f CP1252 -t UTF-8    BSD: exit 1                        GNU: exit 1

  measured 2026-09-07 on macOS 26.6.2 (BSD iconv) and
  iconv (Ubuntu GLIBC 2.39-0ubuntu8.8) 2.39 on ubuntu:24.04
```

BSD iconv reports the file clean and hands the byte back unchanged; GNU rejects it. The same split holds for CP1250's and CP1253's unassigned bytes, so it is not something peculiar to this table. **Convert to UTF-8 instead** — that form agrees on both, and it is what section 4 of the shell run uses.

Two limits on that advice, because it is a workaround rather than a fix. It is *not* a general statement that BSD iconv skips validation: `iconv -f UTF-8 -t UTF-8` over invalid UTF-8 correctly exits 1 on both platforms, which is the case [validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) records. And the `-t UTF-8` form is not universal either — on CP874's byte `0xDB` the two builds still disagree, because their CP874 tables differ in content rather than in how the conversion is driven. When the answer has to be right, decode it in Python, where the table is the one documented in the standard library and the same on every machine.

## If you are coming from Python or ABAP

**Python.** The two codecs are `latin-1` (aliases `iso-8859-1`, `8859`, `cp819`, `latin`, `L1`) and `cp1252` (alias `windows-1252`), and Python does **not** follow the WHATWG rule — asking for `latin-1` gets you real ISO-8859-1, holes and all, which is the behaviour you want in a data pipeline and a surprise if your mental model came from a browser. The practical consequence is the asymmetry in error behaviour: `bytes.decode('latin-1')` can never raise, and that makes it the right tool for *carrying bytes through* a string-shaped API and the wrong tool for *detecting* anything, because it accepts every file you give it and calls it text. `bytes.decode('cp1252')` can raise, on exactly five byte values, and that raise is information — it is the codec telling you the file is not what the label says. If you want the browser's behaviour deliberately, the closest built-in is `cp1252` with `errors='replace'`, and you should write down that you chose it.

**ABAP.** SAP numbers these two tables separately — **1100** for ISO-8859-1 and **1160** for Windows-1252 — which is the right design, because they are different tables, and it means a file interface has to name one. That is where the bug lives: `OPEN DATASET … IN LEGACY TEXT MODE CODE PAGE '1100'` against a file a Windows tool actually wrote in 1160 gives you the 224 agreeing bytes correctly and the punctuation wrong, so it reads as a data-quality problem rather than a configuration one. `cl_abap_codepage=>convert_from( )` raises `cx_sy_conversion_codepage` when the bytes do not fit the table it was given, which is the ABAP spelling of Python's `UnicodeDecodeError` and the same piece of evidence — the exception names the byte it stopped on, so read that before deciding whose system is wrong. Verify both numbers against your own system's code-page table rather than trusting them from this page or any other, and see [SAP code pages](../sap_code_pages/README.md) for why. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 07_Real_Data/windows_1252_vs_latin1/examples
python3 windows_1252_vs_latin1_py.py
bash windows_1252_vs_latin1_sh.sh
```

1. Take the worst CSV you have — the export somebody sent from Excel that never quite loads. Run `LC_ALL=C grep -c '[\x80-\x9f]' yourfile.csv` to count the lines holding a byte from the disputed block. If the answer is zero, the two tables cannot be your problem and you can stop looking at them.
2. On the same file, `python3 -c "d=open('yourfile.csv','rb').read(); print(sorted({b for b in d if 0x80<=b<=0x9f}))"`. If any of `129`, `141`, `143`, `144`, `157` appears, that file cannot be Windows-1252 — those are the five holes, and you have just ruled the table out rather than guessed at it.
3. Find a record whose text is right but whose apostrophe or dash is wrong. Dump that field's bytes and look up which of the 32 it is; the answer tells you which of the two tables the *writer* used.
4. Without the machine: an interface has run for a year against a contract that says ISO-8859-1. A user reports that one product description shows a strange character where a price should read `€9.99`. Say what the sender did, what the receiver did, and why nobody noticed for a year.

## See also

- [Code pages](../../02_Characters/code_pages/README.md) — what a code page is, the four you will meet, and the kata that settles the superset question with one byte
- [Mojibake round trip](../mojibake_round_trip/README.md) — the five holes again, this time deciding whether damaged text can be repaired
- [SAP code pages](../sap_code_pages/README.md) — 1100 and 1160, and the three numbering systems that all look like "code page N"
- [Mojibake](../../03_Encodings/mojibake/README.md) — the shapes of the garbage, and what each one names
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — the `iconv -f X -t X` idiom, and the case where it *is* portable
- [`iconv`](../../06_Terminal/iconv/README.md) — the tool doing the converting above
- [CAST.md](../../CAST.md) — why `é` and `€` are both in the cast, which this page is the argument for
