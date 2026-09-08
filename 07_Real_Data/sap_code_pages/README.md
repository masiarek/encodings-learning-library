# SAP code pages

**Level:** 201 · for SAP work

**One line:** SAP names encodings by number, and so do IBM and Microsoft, in three unrelated schemes that all look alike — so a code-page number is a name in somebody's catalogue rather than a fact about bytes, and **every number on this page is one to verify against the system that will run your job.**

## Three catalogues, and only one of them is yours

A number like `1100` or `1140` or `1252` looks like it identifies an encoding. It identifies an *entry in a catalogue*, and there are at least three catalogues in play the moment SAP is involved: SAP's own numbering (1100, 1160, 4110), IBM's CCSIDs (037, 500, 1140), and Microsoft's Windows code pages (1250, 1252). They overlap in *shape* and share almost nothing else.

Python's codec names follow IBM and Microsoft, which has a consequence you can check in one line: `codecs.lookup('cp1252')` resolves and `codecs.lookup('cp1100')` raises `LookupError`. **SAP's numbers are not typeable into Python at all.** You need a mapping, and the mapping has to come from the system rather than from a page — including this one.

Here is a starting point. Treat every row's left-hand column as a hypothesis:

| SAP | Python codec | what it is |
|---|---|---|
| 1100 | `latin-1` | ISO-8859-1, western European |
| 1160 | `cp1252` | Windows-1252 |
| 1401 | `iso8859-2` | ISO-8859-2, central European |
| 4110 | `utf-8` | UTF-8 |
| 4102 | `utf-16-be` | UTF-16, big-endian |
| 4103 | `utf-16-le` | UTF-16, little-endian |

The middle column is machine-checked by the example below — every one of those codecs resolves. The left column is not, and cannot be: nothing on the machine running this library knows what SAP calls its tables. **Look the numbers up on your own system before you rely on any of them**, because a wrong number here is not a wrong page, it is a wrong interface.

That is the house rule, and it is not politeness. A code-page number is configuration owned by somebody else, it differs between a system and its own copies, and it is the kind of fact that is *quoted* far more often than it is *checked* — which is exactly the failure mode this library exists to argue against.

## What the two numbers 1100 and 1160 actually cost you

The pair is worth naming because the difference is small and the symptom is a data-quality ticket. [1100 is ISO-8859-1 and 1160 is Windows-1252](../windows_1252_vs_latin1/README.md), the two tables agree on 224 of 256 byte values, and an interface declared as one against a file written in the other is correct in every position except the punctuation. Nobody notices a right-looking name; somebody eventually notices a price.

## EBCDIC, because that is where the numbering came from

The numbers-for-tables habit is IBM's, and so is the encoding underneath a great deal of what still arrives in an SAP shop from a mainframe. EBCDIC is worth an afternoon precisely because it breaks the assumption every other encoding on this site quietly satisfies: **its alphabet is not contiguous.**

`a` is `0x81` and `z` is `0xA9`, which spans 41 byte values to hold 26 letters. The letters run in three pieces — `a`–`i` at `0x81`–`0x89`, `j`–`r` at `0x91`–`0x99`, `s`–`z` at `0xA2`–`0xA9`, so 9, 9 and 8 — and the runs line up with the three zone punches of the 80-column card the encoding inherited from. The gaps are where the card had nothing to encode. Two things break, and both are things nobody thinks of as encoding-dependent:

- **The range test.** `c >= 'a' && c <= 'z'` is a letter test in every language that grew up on ASCII, and under EBCDIC it admits fifteen non-letters. It does not fail loudly; it accepts punctuation as a letter.
- **Sort order.** ASCII sorts digits, then capitals, then small letters. EBCDIC sorts small letters, then capitals, then **digits last** — not a rearrangement but the opposite grouping. A report ordered on the mainframe and the same report ordered after transfer disagree, and neither one is broken.

And a third that catches people before either of those: **the line separator moves too.** LF is `0x0A` in ASCII and `0x25` in EBCDIC, so converting a text file to EBCDIC leaves a file in which `wc`, `grep`, `sed`, `sort`, `head` and the shell's own `read` cannot find a single line. Section 4 of the terminal run shows `wc -l` reporting 0 lines in an 11-byte file that plainly has two. This is why a mainframe extract is moved in *binary* mode and converted once at one end, rather than streamed through a pipeline of text tools.

## The euro twins: two numbers, one byte apart

When the euro arrived, IBM did not extend the existing EBCDIC tables — it published a **second CCSID for each one**, differing in a single position. `037` became `1140`, `273` became `1141`, and so on up to `871` → `1149`: ten pairs, and in every pair the new number is the old table with the euro sign where the international currency sign `¤` used to be.

For `cp037` against `cp1140` that is measured below: exactly **one byte differs, `0x9F`**. Everything else is identical, so a file converted under the wrong one of a pair is correct in every position except the currency symbol — the same shape of bug as Windows-1252 against Latin-1, on a different continent of computing.

**Nine of the ten pairs are not checkable here**, because Python's standard library ships `cp1140` and none of `cp1141`–`cp1149`. They are real and documented by IBM; this page simply has not measured them, and that distinction — between a number this page measured and a number this page repeated — is the same distinction the SAP column above is about.

## Two EBCDIC pages that agree on every letter and digit

`cp037` (US/Canada) and `cp500` (International) differ on exactly **seven** byte values, and all seven are punctuation: `[`, `]`, `!`, `|`, `^`, `¢` and `¬`. Every letter and every digit encodes identically in both.

So the wrong choice between them moves master data unharmed — names, cities, amounts all arrive correct — and destroys anything whose content is *syntax*. A JSON payload, a delimited file, a generated script: those are made of exactly the characters that moved. It is the 1252-against-Latin-1 lesson again in a different alphabet: **the tables agree about the text and disagree about the punctuation**, so the failure waits for the first record with a bracket in it.

## In Python

<!-- output:sap_code_pages_py -->
*Verified output of [`sap_code_pages_py.py`](examples/sap_code_pages_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THREE NUMBERING SYSTEMS, ALL SPELLED 'CODE PAGE N'
------------------------------------------------------------------------
   SAP numbers its tables, IBM numbers its CCSIDs, and Microsoft
   numbers its Windows code pages. The three schemes are unrelated,
   and Python's codec names follow IBM and Microsoft:

      codecs.lookup('cp1100')     LookupError -- no such codec
      codecs.lookup('cp1160')     LookupError -- no such codec
      codecs.lookup('cp4110')     LookupError -- no such codec
      codecs.lookup('cp037')      resolves
      codecs.lookup('cp1140')     resolves
      codecs.lookup('cp1252')     resolves

   So SAP's numbers are not typeable into Python at all: cp1100 is
   not a codec, while cp1252 and cp1140 are -- and cp1140 is IBM's
   EBCDIC, nothing to do with any SAP number that looks like it.
   You need a mapping, and it has to come from the system.

   A starting point, TO BE VERIFIED against your own system's
   code-page table before you rely on any row:

      SAP    Python codec   what it is
      1100   latin-1        ISO-8859-1, western European
      1160   cp1252         Windows-1252
      1401   iso8859-2      ISO-8859-2, central European
      4110   utf-8          UTF-8
      4102   utf-16-be      UTF-16, big-endian
      4103   utf-16-le      UTF-16, little-endian

   The middle column IS checked: all 6 of the 6 codecs named
   above resolve in this Python. The left column is not, and cannot
   be -- nothing on this machine knows what SAP calls its tables, so
   those numbers are the one thing on this page you have to go and
   look up yourself.

2. EBCDIC: THE ALPHABET IS IN THREE PIECES
------------------------------------------------------------------------
   ASCII puts A-Z in one unbroken run, which is why 'c >= "a" and
   c <= "z"' is a letter test in every language that grew up on it.
   EBCDIC does not:

      lowercase:
         a-i   0x81-0x89   9 letters
         j-r   0x91-0x99   9 letters
         s-z   0xA2-0xA9   8 letters
      uppercase:
         A-I   0xC1-0xC9   9 letters
         J-R   0xD1-0xD9   9 letters
         S-Z   0xE2-0xE9   8 letters

      a is 0x81 and z is 0xA9, so the range spans 41 byte
      values to hold 26 letters. 15 of them are not letters.

   The three runs are 9, 9 and 8 long, and they line up with the
   three zone punches of the 80-column card EBCDIC inherited from.
   The gaps are where the card had nothing to encode.

3. WHAT THE GAPS ACTUALLY BREAK
------------------------------------------------------------------------
   (a) the range test, which quietly admits punctuation:
       characters that pass 'between a and z' but are not letters:
          « » ð ý þ ± ° ª º æ ¸ Æ ¤ µ ~

   (b) sort order, which is not a rearrangement of the ASCII one:
       by ascii  bytes: ['9lives', 'Apple', 'Zebra', 'apple']
       by cp037  bytes: ['apple', 'Apple', 'Zebra', '9lives']

       ASCII sorts digits, then capitals, then small letters.
       EBCDIC sorts small letters, then capitals, then digits --
       the reverse grouping, so a report sorted on the mainframe and
       the same report sorted after transfer do not agree, and
       neither is broken.

4. THE EURO TWINS: ONE BYTE APART
------------------------------------------------------------------------
   When the euro arrived, IBM did not extend the EBCDIC tables --
   it published a second number for each one, differing in a single
   position. Python ships exactly one of those pairs:

      cp037   / cp1140  1 byte differs: 0x9F '¤' -> '€'
      cp273   / cp1141  not comparable: cp1141 not in this Python
      cp277   / cp1142  not comparable: cp277, cp1142 not in this Python
      cp278   / cp1143  not comparable: cp278, cp1143 not in this Python
      cp280   / cp1144  not comparable: cp280, cp1144 not in this Python
      cp284   / cp1145  not comparable: cp284, cp1145 not in this Python
      cp285   / cp1146  not comparable: cp285, cp1146 not in this Python
      cp297   / cp1147  not comparable: cp297, cp1147 not in this Python
      cp500   / cp1148  not comparable: cp1148 not in this Python
      cp871   / cp1149  not comparable: cp871, cp1149 not in this Python

   One byte. 0x9F was the international currency sign in cp037 and
   is the euro sign in cp1140, and everything else is identical --
   so a file converted under the wrong one of the pair is correct in
   every position except the currency symbol, which is the same
   shape of bug as Windows-1252 against Latin-1, on a different
   continent of computing.

   Note what this program could NOT check: 9 of the 10 pairs.
   Those CCSIDs are real and documented by IBM; they are simply not
   in Python's standard library, so nothing here can confirm what
   they contain. That is the difference between a number this page
   measured and a number this page repeated -- the same difference as
   the SAP column in section 1.

5. TWO EBCDIC VARIANTS THAT AGREE ON EVERY LETTER AND DIGIT
------------------------------------------------------------------------
   cp037 (US/Canada) against cp500 (International): 7 bytes differ

      byte   cp037    cp500
      0x4A   '¢'      '['
      0x4F   '|'      '!'
      0x5A   '!'      ']'
      0x5F   '¬'      '^'
      0xB0   '^'      '¢'
      0xBA   '['      '¬'
      0xBB   ']'      '|'

   every letter and digit encodes identically in both: True

   The seven that move are brackets, the exclamation mark, the pipe,
   the caret, the cent sign and the not sign -- which is to say, the
   characters that are SYNTAX. Names and amounts survive the wrong
   choice; a JSON payload, a shell script or an ABAP field symbol
   does not. Same lesson as 1252 against Latin-1: the tables agree
   about the text and disagree about the punctuation.

6. REPRODUCING AN INTERFACE'S MOJIBAKE, OUTSIDE THE SYSTEM
------------------------------------------------------------------------
   The point of the mapping in section 1: once you know which table
   each end used, the damage is reproducible in four lines here, and
   you can show it to somebody without a logon.

   the field                 'Zażółć'
   written as UTF-8          5a 61 c5 bc c3 b3 c5 82 c4 87
   read back as Latin-1      'Za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87'

   That is one line of Python standing in for a file written under
   one code page and read under another. Reproduce it before you
   argue about it: the reproduction is the evidence, and it is the
   same evidence whichever system turns out to be misconfigured.

   And check every number in it against the system. Nothing in this
   file knows your landscape -- a table name printed here is a
   hypothesis about a configuration somebody else controls.
```
<!-- /output -->

## In the terminal

<!-- output:sap_code_pages_sh -->
*Verified output of [`sap_code_pages_sh.sh`](examples/sap_code_pages_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SAME LETTERS, A DIFFERENT TABLE
------------------------------------------------------------------------
   text        ABC abc 123
   as ASCII    4142432061626320313233
   as CP037    c1c2c34081828340f1f2f3

   Not a rearrangement you can do in your head: 'A' is 0x41 in ASCII
   and 0xC1 in EBCDIC, and the space is 0x20 against 0x40.

2. THE ALPHABET IS IN THREE PIECES
------------------------------------------------------------------------
   a-z in ASCII:  6162636465666768696a6b6c6d6e6f707172737475767778797a
   a-z in CP037:  818283848586878889919293949596979899a2a3a4a5a6a7a8a9

   Read the second row along: 81..89, then a jump to 91..99, then a
   jump to a2..a9. Three runs of 9, 9 and 8. The ASCII row has
   no jumps at all, which is the whole reason 'is it between a and z'
   became an idiom.

   a is 0x81 and z is 0xa9, so that test spans 41 byte values
   to cover 26 letters.

3. TWO EBCDIC PAGES THAT AGREE ON EVERY LETTER
------------------------------------------------------------------------
   a name is identical in both:
      CP037   d296a68193a29289
      CP500   d296a68193a29289

   a bracketed field is not:
      CP037   ba81bb
      CP500   4a815a

   Seven bytes differ between the two pages and every one of them is
   punctuation: [ ] ! | ^ and the cent and not signs. So master data
   crosses a wrongly configured interface unharmed and anything with
   SYNTAX in it -- a JSON payload, a delimited file, a script -- does
   not. Choosing the wrong one of these two is invisible until the
   day the payload has a bracket in it.

4. THE LINE SEPARATOR MOVES TOO, AND EVERY LINE TOOL GOES BLIND
------------------------------------------------------------------------
   ASCII file    616c7068610a626574610a
   CP037 file    8193978881258285a38125
   LF (0x0a) became 25 -- EBCDIC's NL

   wc -c says 11 bytes and wc -l says 0 lines

   Two lines went in and the file is not empty, but nothing on a Unix
   box will find a line in it: wc, grep, sed, sort, head and read all
   look for 0x0a and there is not one in the file. This is why an
   EBCDIC extract is moved in BINARY mode and converted at one end,
   rather than streamed through a pipeline of text tools.

5. SORT ORDER IS NOT A REARRANGEMENT EITHER
------------------------------------------------------------------------
   8197979385               apple
   c197979385               Apple
   e985829981               Zebra
   f99389a585a2             9lives

   Sorted by their EBCDIC bytes, small letters come first, then
   capitals, then digits -- the opposite grouping to ASCII, where
   digits sort before capitals before small letters. A report ordered
   on the mainframe and the same report ordered after transfer
   disagree, and neither of them is broken.
```
<!-- /output -->

### Three tools, three different subsets of one catalogue

The shell section above uses only `CP037` and `CP500`, and the reason is the page's own thesis arriving in the tooling. The same ten-pair EBCDIC family is present in three different partial forms depending on what you are holding:

```text
  Python 3.14 stdlib   cp037 cp273 cp500 cp1140          (+ cp424 cp875 cp1026)
  BSD iconv            all ten pre-euro pages,
                       and NONE of CP1140-CP1149
  GNU iconv            all ten euro pages,
                       and all pre-euro except CP277

  measured 2026-09-07 on macOS 26.6.2 (BSD iconv) and
  iconv (Ubuntu GLIBC 2.39-0ubuntu8.8) 2.39 on ubuntu:24.04
```

macOS cannot convert to CCSID 1140 at all, which is why the euro twin is demonstrated in Python and not on a pipe. Read that as the general case rather than a macOS complaint: **a code-page number is only as real as the catalogue of whatever is about to read it**, and three tools on two machines gave three different answers about the same ten numbers. It is the same reason the SAP column has to be checked on the SAP system.

## If you are coming from Python or ABAP

**Python.** The whole model is two types and a table named at the boundary, which is exactly ABAP's — `bytes` and `str`, `.decode(table)` and `.encode(table)`. What Python gives you that a system does not is a *second opinion you can run anywhere*: once you know which table each end used, an interface's damage is reproducible in one line on a laptop, with no logon and no transport. That reproduction is the useful artifact in an argument about whose system is misconfigured, because it is the same evidence whichever answer turns out to be right. Two practical notes: `codecs.lookup(name)` is the cheap way to find out whether a name means anything before you build a script around it, and the `cp*` names you can type are IBM's and Microsoft's, so a mapping table from SAP's numbers is something you write down once, from the system, and keep.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* The type split carries the whole idea: `string` is characters and `xstring` is bytes, there is no operator that quietly mixes them, and the conversion between them is the boundary where a code page gets named. `cl_abap_codepage=>convert_to( )` is encode and `convert_from( )` is decode; on older releases you will find the `cl_abap_conv_*` family (`cl_abap_conv_in_ce`, `cl_abap_conv_out_ce`) and newer code routes through `cl_abap_conv_codepage` — check which your release offers rather than trusting a name from any document, including this one. A conversion the table cannot represent raises `cx_sy_conversion_codepage`, which is `strict` and is the same piece of evidence as Python's `UnicodeDecodeError`: it names the byte it stopped on, so read the exception before deciding whose system is wrong.

For files, the addition is the contract: `OPEN DATASET … IN TEXT MODE ENCODING UTF-8` is text with a named encoding, `ENCODING NON-UNICODE` bets on the system's own setting, `IN LEGACY TEXT MODE CODE PAGE …` names a table explicitly, and `IN BINARY MODE` reads bytes into an `xstring` and converts nothing — which is Python's `'rb'`, and the right choice for data you are only *carrying*. A field you never converted is a field you never have to repair. Also worth holding: a Unicode ABAP system stores `string` internally as [the UCS-2 subset of UTF-16](../../09_History/why_utf16_stayed/README.md), so `strlen( )` counts code *units* and is not a byte count — `xstrlen( )` over an `xstring` is the byte question. And the `#` you meet in SE16 or the debugger is SAP drawing a character it cannot render, not necessarily a byte that was lost; look at the `xstring` before concluding anything. Every code-page number in this paragraph and the table above is to be verified on the system that will run the job.

## Try it

```bash
cd 07_Real_Data/sap_code_pages/examples
python3 sap_code_pages_py.py
bash sap_code_pages_sh.sh
```

1. Look up the code page your own system actually uses, on the system, and write the number down next to the Python codec name you believe it maps to. That written pair is the only version of the table above you should trust — and if you cannot find it, that is the finding.
2. Take the worst file an interface has ever handed you and run `python3 -c "print(open('f','rb').read()[:64].hex(' '))"`. If the letters are in the `0x81`–`0xA9` and `0xC1`–`0xE9` ranges rather than `0x41`–`0x7A`, it is EBCDIC and nothing that reads text will make sense of it until it is converted.
3. Convert a two-line file to CP037 and run `wc -l` on the result. Then explain to somebody why a non-empty file has no lines, using the byte value.
4. Take a delimited payload with a `[` or a `|` in it, encode it under CP037 and under CP500, and diff the two. Say which fields survived and which did not, and why that makes this the hardest kind of misconfiguration to notice.
5. Without the machine: an interface has moved names and amounts correctly for two years. A new field is added that carries a JSON fragment, and it arrives corrupted while every other field stays perfect. Name the two candidate code pages and say what you would ask for to tell them apart.

## See also

- [Windows-1252 vs Latin-1](../windows_1252_vs_latin1/README.md) — SAP's 1100 and 1160, and why they are different tables rather than one table twice
- [The mojibake round trip](../mojibake_round_trip/README.md) — reproducing an interface's damage, and deciding whether it can be undone
- [Code pages](../../02_Characters/code_pages/README.md) — what a code page is, before any of it has a number
- [Mojibake](../../03_Encodings/mojibake/README.md) — reading the garbage and naming the culprit
- [Sorting and collation](../sorting_and_collation/README.md) — the other reason two systems disagree about order
- [`iconv`](../../06_Terminal/iconv/README.md) — the converter, and what its catalogue does and does not hold
- [Why UTF-16 stayed](../../09_History/why_utf16_stayed/README.md) — why an ABAP `string` is UCS-2 inside
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — decode at the boundary, and write the encoding into the contract
