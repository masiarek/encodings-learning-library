# Noncharacters and the private use areas

**Level:** 201 · for anyone who has ever wanted a value nobody else can send them

**One line:** A noncharacter is not an invalid character. All 66 of them encode as UTF-8, decode back unchanged, and a conformant decoder may not reject them — what they are is permanently *uninterchangeable*, and that is precisely what makes them usable as your own internal sentinels.

## Reserved is not invalid, and the difference is the page

Two regions of the code space are set aside forever, for opposite reasons, and both are routinely called *invalid* by people who have never encoded one.

**Noncharacters** are 66 code points the standard promises will never be assigned to anything: `U+FDD0`–`U+FDEF`, a block of 32 sitting in the middle of the Arabic Presentation Forms; and `U+FFFE` and `U+FFFF`, the last two code points of every one of the 17 planes. They are not for you to define and not for anyone else either. They are reserved so that a program has values it can use internally in the certain knowledge that no input will contain one.

**Private use** is the other 137,468: `U+E000`–`U+F8FF` in the BMP, plus planes 15 and 16 in their entirety bar the last two code points of each, which the paragraph above has already spent. These have no meaning from the standard *by design* — they mean whatever the sender and the receiver agreed, which is how the Apple logo, a Powerline arrow and every icon font on your machine are addressed.

The word that does *not* apply to either is **invalid**. Both are legal code points. UTF-8 encodes all of them; UTF-16 and UTF-32 encode all of them; `str::from_utf8` accepts their bytes; `iconv` passes them through without a murmur. The Unicode FAQ asks *"Are noncharacters invalid in Unicode strings and UTFs?"* and answers, in two words, [absolutely not ↗](https://www.unicode.org/faq/private_use.html#noncharacters) — an implementation is required to *preserve* these values, not to sanitise them away.

What they are is **not interchangeable**. A noncharacter must not appear in text you send to somebody else, and that prohibition is worth exactly one thing: it is the reason nothing you *receive* will contain one.

The class that genuinely is invalid sits next door and is easy to confuse with these two. A **surrogate** — `U+D800`–`U+DFFF` — is not a [Unicode scalar value](../../03_Encodings/validation_is_a_boundary/README.md) at all, so no UTF has a spelling for it and every encoder here refuses it. That refusal is what a reader is thinking of when they call a noncharacter invalid, and it belongs to a different set of code points entirely.

## The BOM already depends on all this

The clearest use of a noncharacter in the wild is one this library has already taken apart from the other side. `U+FEFF` written little-endian is the two bytes `FF FE`; read back big-endian, those bytes are `U+FFFE`. A decoder that finds `U+FFFE` has not found a rare character it should pass along — it has found a value guaranteed never to mean anything, so it knows *for certain* that it has the byte order backwards.

[Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) makes that argument in full and does not repeat it here. What that page assumes, and this one supplies, is the half underneath: the mirror is proof rather than convention **because** `U+FFFE` is permanently reserved. Take away the reservation and the whole scheme degrades into a guess about whether a file happens to start with an unusual character.

## The number is checkable, which is why it is generated

66 and 137,468 are the kind of numbers that get copied wrong, and this library has [a rule about numbers read out of the Unicode table](../the_table_has_a_version/README.md): most of them are facts about whichever release your interpreter shipped with, and belong in a sentence with a date on it rather than in an answer key.

**The version stamp, since this page turns on one.** The claims below were checked against the Unicode FAQ and the stability policy on **2026-09-08**, with the standard at **Unicode 17.0** (September 2025), and run on `python3` 3.14.7 carrying UCD **16.0.0** and `rustc` 1.98.0 carrying UCD **17.0.0** — a release apart, which is the ordinary state of affairs and [a page of its own](../the_table_has_a_version/README.md). It does not matter here, and that is the finding rather than an aside: both toolchains produce the same 66 and the same 137,468, because neither number is a lookup.

These two are the exception, and it is worth knowing why. The set of noncharacters is *formally immutable* — a [stability policy ↗](https://www.unicode.org/policies/stability_policy.html), not a property of the current release — so counting them is arithmetic over a rule that cannot change. The programs below therefore never quote the count: they generate the set from the two rules that define it and count what comes out. The private-use total is then checked a second way, against the `Co` category in the running interpreter's own table, and the two agree exactly. If a future release ever moved a boundary, that line would flip to `False` and CI would say so, rather than the page quietly becoming wrong.

## In Python

<!-- output:noncharacters_and_private_use_py -->
*Verified output of [`noncharacters_and_private_use_py.py`](examples/noncharacters_and_private_use_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SET, GENERATED RATHER THAN QUOTED
------------------------------------------------------------------------
   U+FDD0..U+FDEF, one block in the middle of the BMP      32
   the last two code points of each of 17 planes           34
                                                         ----
   noncharacters, total                                    66

   first four   U+FDD0  U+FDD1  U+FDD2  U+FDD3
   last four    U+FFFFE  U+FFFFF  U+10FFFE  U+10FFFF

   That 66 may go in an answer key, which almost nothing read out of
   the Unicode table may. The set of noncharacters is formally
   IMMUTABLE -- a stability policy, not a fact about this release --
   so the number is arithmetic over a rule that cannot change, rather
   than a lookup a September might move.

2. RESERVED IS NOT INVALID: EVERY UTF ENCODES ALL 66
------------------------------------------------------------------------
   utf-8       encodes and decodes back all 66:  True
   utf-16-le   encodes and decodes back all 66:  True
   utf-16-be   encodes and decodes back all 66:  True
   utf-32-le   encodes and decodes back all 66:  True
   utf-32-be   encodes and decodes back all 66:  True
   utf-7       encodes and decodes back all 66:  True

   Not one refusal, and not one loss. To an encoder a noncharacter is
   an ordinary code point -- three UTF-8 bytes for the BMP ones, four
   for the rest:
      U+FDD0     ef b7 90     3 bytes
      U+FFFE     ef bf be     3 bytes
      U+FFFF     ef bf bf     3 bytes
      U+1FFFE    f0 9f bf be  4 bytes
      U+10FFFF   f4 8f bf bf  4 bytes

   The contrast is the whole point. THESE two are refused, and neither
   refusal has anything to do with being reserved:
      U+D800     UnicodeEncodeError   a surrogate: not a scalar value, so no UTF carries it
      U+110000   ValueError           not a code point at all -- past U+10FFFF

   So of everything a reader files under 'not really a character',
   the encoder objects to exactly one class, and the noncharacters
   are not it. A conformant decoder may not reject them either: the
   standard requires the value to be preserved, not sanitised.

3. WHICH IS WHY THE BOM CAN PROVE ANYTHING
------------------------------------------------------------------------
   U+FEFF written little-endian      ff fe
   those same bytes read big-endian  U+FFFE
   ...and U+FFFE is a noncharacter:  True

   A reader that decodes U+FFFE has not found a rare character. It has
   found a value guaranteed never to mean anything, so it knows for
   certain the byte order is backwards. The reservation is what turns
   a convention into a proof.

4. THE OTHER RESERVATION: PRIVATE USE
------------------------------------------------------------------------
   U+E000  ..U+F8FF       6400   Private Use Area (BMP)
   U+F0000 ..U+FFFFD     65534   Supplementary Private Use Area-A (plane 15)
   U+100000..U+10FFFD    65534   Supplementary Private Use Area-B (plane 16)
                        137468   total

   code points this interpreter's table calls Co (Private_Use):  137468
   the same set as the three ranges above:                       True

   Two independent sources, one answer: the ranges above are written
   from the standard, the Co set is read out of unicodedata. They
   agree exactly, so neither is a typo -- and were a release ever to
   move a boundary, that line would flip to False rather than go
   unnoticed.

   Note where the supplementary areas STOP. Plane 15 ends at U+FFFFD,
   not U+FFFFF, because the last two of every plane are already spoken
   for. The two reservations do not overlap by a single code point.

5. WHAT NEITHER OF THEM HAS -- AND THE ONE DIFFERENCE THE TABLE SEES
------------------------------------------------------------------------
   code point  cat  name()                  alpha  print  what it is
   U+0041      Lu   LATIN CAPITAL LETTER A  True   True   an ordinary letter
   U+E000      Co   ValueError              False  False  private use -- yours by agreement
   U+F8FF      Co   ValueError              False  False  private use -- Apple's logo, on Apple's machines
   U+100000    Co   ValueError              False  False  private use, plane 16
   U+FDD0      Cn   ValueError              False  False  noncharacter -- nobody's, ever
   U+FFFE      Cn   ValueError              False  False  noncharacter -- the BOM's mirror
   U+0378      Cn   ValueError              False  False  unassigned -- may become a letter one day

   Read the category column. Private use is Co and says so. A
   noncharacter is Cn -- and so is U+0378, which is merely unassigned
   and could be a letter in some future release. The table cannot tell
   those two apart, because Cn means UNASSIGNED and a noncharacter is,
   permanently, unassigned.

   And there is no API for it. unicodedata exports 16 public names and
   not one of them answers 'is this a noncharacter'. The property is in
   the UCD -- Noncharacter_Code_Point -- and the standard library does
   not expose it. Which is why section 1 generates the set from the two
   rules: not for elegance, but because nothing here will tell you.

6. WHAT HAPPENS WHEN ONE REACHES SOMETHING REAL
------------------------------------------------------------------------
   JSON
      json.dumps(U+FFFE)                    "\ufffe"
      json.dumps(U+E000)                    "\ue000"
      round trips through loads:            True
      ensure_ascii=False writes the bytes:  22 ef bf be 22
      No objection anywhere. \uFFFE is a well-formed escape and the
      three raw bytes are well-formed UTF-8, so both spellings survive.

   XML -- where the write and the read disagree, inside one module
      ET.tostring on U+FFFE                 <a>\ufffe</a>
      ET.fromstring of what it just wrote   ParseError: not well-formed (invalid token)

      of the 66 noncharacters, XML 1.0 accepts       64
                                     and refuses      2
      the two it refuses                             U+FFFE U+FFFF
      of four private-use code points sampled, XML accepts 4

      So 'noncharacter' and 'what XML forbids' are two different sets
      that overlap in exactly two places. XML 1.0's Char production
      excludes U+FFFE and U+FFFF and says nothing about the other 64.
      A numeric character reference does not help either: &#xFFFE; is
      refused as well -- the same shape as XML refusing to carry
      U+0001 even when escaped.

   SQLite -- a database in the standard library
      stored and read back unchanged:       True
      SQL length() of each:                 [1, 1]
      No complaint. TEXT is UTF-8, these are UTF-8, and the engine has
      no opinion about what the code points were supposed to mean.

   Sorting and word breaking -- the quiet one
      of 6 strings sorted, the two reserved ones land at [4, 5]
      'a\ue000b'.split()          ->  1 piece(s)
      'a\ue000b'.isidentifier()   ->  False
      'a\ue000b'.isprintable()    ->  False
      Default sort is code point order, so a private-use string lands
      after every Latin letter and ahead of the emoji -- an order
      nobody chose. There is no collation weight to consult and no
      word-break class to honour, because the standard declines to
      have an opinion about what you decided these mean.

7. THE TWO RESERVATIONS, SIDE BY SIDE
------------------------------------------------------------------------
                              noncharacter             private use
   how many                   66                       137468
   General_Category           Cn (unassigned)          Co (private use)
   has a name                 no                       no
   well-formed in every UTF   yes                      yes
   will ever be assigned      no, and guaranteed so    no, that is the point
   meaning                    none, permanently        whatever you agreed
   safe to interchange        no -- that is the deal   only inside the agreement
   what it is for             your program's internals your font, your protocol

   One sentence apart: private use is YOURS TO DEFINE, a noncharacter
   is NOBODY'S, EVER. Both are useless for interchange, and useful for
   exactly that reason -- a value you can be certain did not arrive
   from outside is the only kind of sentinel that cannot be forged.
```
<!-- /output -->

The two findings worth carrying out of that run are both in section 5 and section 6.

**The table cannot tell you what you are holding.** `unicodedata.category` returns `Co` for a private-use code point and says so plainly, but a noncharacter comes back `Cn` — *unassigned* — which is the identical answer it gives for `U+0378`, a gap that may well be a letter in some future September. The claim is true, and it is not the claim you asked. Nor is there an API to ask better: the UCD has a `Noncharacter_Code_Point` property and Python's `unicodedata` does not expose it, so the range test at the top of the program is the only definition on the machine.

**XML is where the abstraction leaks, and it leaks inside one module.** `ElementTree.tostring` will happily write `U+FFFE` into a document, and `ElementTree.fromstring` refuses to read that document back — the same library failing its own round trip. Then the sharper half: of the 66 noncharacters, XML 1.0 accepts **64** and refuses **2**. Its `Char` production excludes `U+FFFE` and `U+FFFF` and has nothing to say about the other 64, so *"noncharacter"* and *"the thing XML forbids"* are two different sets that happen to overlap twice. A numeric character reference does not rescue you either — `&#xFFFE;` is refused as well, which is the same shape as XML's refusal to carry `U+0001` even when escaped.

## In Rust

<!-- output:noncharacters_and_private_use_rs -->
*Verified output of [`noncharacters_and_private_use_rs.rs`](examples/noncharacters_and_private_use_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SAME TWO SETS, COUNTED BY A DIFFERENT LANGUAGE
------------------------------------------------------------------------
   noncharacters   66
   private use     137468
   the two sets are disjoint:  true

   Two programs, two languages, one sweep of the number line each,
   and the same 66 and 137,468. Neither number was typed in.

2. char::from_u32 SAYS YES TO EVERY ONE OF THEM
------------------------------------------------------------------------
   noncharacters that char::from_u32 accepts:   66 of 66
   private-use code points it accepts:          137468 of 137468

   Which is worth pausing on, because `char` is the type that
   REFUSES things. It is the strictest character type in this
   library -- and it refuses exactly one class:
      char::from_u32(0xD7FF)     Some   an ordinary scalar value
      char::from_u32(0xD800)     None   a surrogate -- not a scalar value
      char::from_u32(0xDFFF)     None   a surrogate -- not a scalar value
      char::from_u32(0xE000)     Some   private use -- an ordinary scalar value
      char::from_u32(0xFDD0)     Some   a NONCHARACTER, and still a scalar value
      char::from_u32(0xFFFE)     Some   a NONCHARACTER, and still a scalar value
      char::from_u32(0x10FFFF)   Some   a NONCHARACTER, and still a scalar value
      char::from_u32(0x110000)   None   past U+10FFFF -- not a code point

   Scalar value is the whole rule. `char` holds every code point
   that is not a surrogate, and reservation is not part of the
   contract -- so a noncharacter is as welcome in a String as an
   'a' is. It also compiles as a LITERAL: '\u{FFFE}' is accepted
   by rustc with no lint and no warning.

3. AND SO DOES UTF-8, IN BOTH DIRECTIONS
------------------------------------------------------------------------
   encoded to UTF-8 and validated back:  66 of 66

   str::from_utf8 is THE validator in this language -- the
   boundary every &str is built behind -- and it has no objection:
      ef bf be     Ok                U+FFFE, a noncharacter
      ef b7 90     Ok                U+FDD0, a noncharacter
      ee 80 80     Ok                U+E000, private use
      ed a0 80     Err at byte 0     U+D800 spelled in UTF-8, a surrogate

   One of those four is rejected and it is not one of the reserved
   ones. That is the page in a line.

4. NO PROPERTY, IN EITHER SET
------------------------------------------------------------------------
   code point  alpha  ctrl   ws     upper  len_utf8  what it is
   U+0041      true   false  false  true   1         an ordinary letter
   U+E000      false  false  false  false  3         private use -- yours by agreement
   U+F8FF      false  false  false  false  3         private use -- Apple's logo, on Apple's machines
   U+FDD0      false  false  false  false  3         noncharacter -- nobody's, ever
   U+FFFE      false  false  false  false  3         noncharacter -- the BOM's mirror
   U+0378      false  false  false  false  2         unassigned -- may become a letter one day

   Every column false on all four reserved rows -- and the same
   five falses for the merely-unassigned U+0378. Rust cannot tell
   you which is which either -- there is no is_noncharacter and no
   is_private_use in std, which is why this file opens with two
   range tests written by hand.

5. THE ONE PLACE RUST IS MORE HELPFUL THAN PYTHON
------------------------------------------------------------------------
   Debug on a string holding one of each:
      "a\u{fffe}b"
      "a\u{e000}b"
      escape_unicode:  \u{fffe}

   Debug escapes a non-printable scalar rather than emitting it, so
   dbg! and a {:?} in a log show you the number. Display does not:
   println!("{}", c) writes the three raw bytes and your terminal
   draws a box, or nothing, or whatever a font privately decided.
   When you are hunting one of these, {:?} is the tool.

6. WHAT THEY ARE ACTUALLY FOR
------------------------------------------------------------------------
   A sentinel has to be a value your input cannot contain. That is
   the entire requirement, and it is why a noncharacter beats every
   ASCII character somebody once picked for the job:
      joined on U+FFFF, then split:  ["field one", "field two", "field three"]
      pieces: 3

   Nothing arriving from outside can contain U+FFFF, because no
   conformant producer may emit it as text -- so unlike a comma, a
   tab, a NUL or a pipe, this separator cannot be forged by the
   data. Inside one process that is a real guarantee. The moment
   the string leaves -- to a file, a socket, an XML document, a
   filename -- the guarantee is gone and you have shipped a value
   the standard says you must not interchange.
```
<!-- /output -->

Rust makes the point more sharply than Python does, because `char` is the type in this library that *refuses* things. It rejects a surrogate at construction and there is no way past it in safe code ([`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md)) — so a reader who has met that refusal expects another one here, and instead gets `Some` sixty-six times out of sixty-six. `'\u{FFFE}'` compiles as a literal with no lint and no warning. The contract is *scalar value*, and reservation was never part of it.

One practical detail from section 5 is worth stealing whatever language you work in: Rust's `Debug` formatter escapes these rather than emitting them, so `{:?}` and `dbg!` print `"a\u{fffe}b"` where `Display` writes three raw bytes and your terminal draws a box. When you are hunting one of these, the escaping formatter is the tool. Python's `repr()` does the same job for the same reason — `isprintable()` is `False` for both `Cn` and `Co`.

## In the terminal

<!-- output:noncharacters_and_private_use_sh -->
*Verified output of [`noncharacters_and_private_use_sh.sh`](examples/noncharacters_and_private_use_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE BYTES, WRITTEN AND READ BACK
------------------------------------------------------------------------
   U+FDD0   noncharacter  efb790    3 bytes   iconv UTF-8 -> UTF-8: accepted
   U+FFFE   noncharacter  efbfbe    3 bytes   iconv UTF-8 -> UTF-8: accepted
   U+FFFF   noncharacter  efbfbf    3 bytes   iconv UTF-8 -> UTF-8: accepted
   U+E000   private use   ee8080    3 bytes   iconv UTF-8 -> UTF-8: accepted
   U+D800   surrogate     eda080    3 bytes   iconv UTF-8 -> UTF-8: REFUSED
   U+110000 past the end  f4908080  4 bytes   iconv UTF-8 -> UTF-8: accepted

   Five of six accepted, and the one refusal is the surrogate -- not
   a reserved code point. The last row is a different story and the
   iconv page tells it: both iconvs take f4 90 80 80, which is above
   U+10FFFF and which Python and Rust each refuse. What matters here
   is the first four rows, where there is simply nothing to object to.

2. THE TEXT TOOLS HAVE NO OPINION EITHER
------------------------------------------------------------------------
   the file, as bytes:  616c706861efbfbe626574610a
   wc -c                13
   wc -l                1
   grep -c alpha        1
   grep -c beta         1
   cat -v               alphaM-oM-?M->beta

   Nine letters you can read, one code point you cannot see, thirteen
   bytes on disk, one line, and every tool content. cat -v is the row
   worth keeping: it is how you SEE a reserved code point at a
   terminal, because nothing is going to draw it for you.

3. AND THEY SURVIVE A REAL PIPE
------------------------------------------------------------------------
   original          61efbfbe62ee8080630a
   through cat       61efbfbe62ee8080630a
   through iconv     61efbfbe62ee8080630a
   through tr -d c   61efbfbe62ee80800a

   Byte for byte, unchanged. Which is the practical half of the claim:
   a pipeline will not clean these up for you, and will not warn you.
```
<!-- /output -->

Byte-identical on both CI runners, which is the point of running it: `iconv` used as a yes/no UTF-8 validator accepts every reserved code point on both platforms and refuses only the surrogate. The last row of section 1 is a different story and [`iconv`](../../06_Terminal/iconv/README.md) tells it — both iconvs accept `f4 90 80 80`, which is above `U+10FFFF` and which Python and Rust each refuse.

## The one door that slams, and only on one platform

Everything above says *yes*. Here is the exception, and it is not in a program because it cannot be: the answer depends on the filesystem.

```text title="Measured 2026-09-08 — macOS 26.6.2 on APFS, and ubuntu:24.04 under Docker. Not machine-checked: the two disagree, so no answer key can hold both."
  filename                macOS / APFS                 Linux / ubuntu:24.04
  f<U+FFFE>.txt           OSError, errno 92 EILSEQ     created, name comes back identical
  f<U+FDD0>.txt           OSError, errno 92 EILSEQ     created, name comes back identical
  f<U+1FFFE>.txt          OSError, errno 92 EILSEQ     created, name comes back identical
  f<U+E000>.txt           created, name comes back     created, name comes back identical
  f<U+D800>.txt           UnicodeEncodeError, raised in Python before the syscall — both

  and at the shell, with the bytes written by printf rather than typed:

  $ touch "$(printf 'a\xef\xbf\xbeb.txt')"
  macOS:  touch: a<U+FFFE>b.txt: Illegal byte sequence
  Linux:  silence, and a file
```

`EILSEQ` is the errno APFS already gives a filename that is not valid UTF-8, which this library records as [finding 11](../../CONTRIBUTING.md) and measures on [`find`, and filenames that are bytes](../../11_Tools/find/README.md). The refinement is the interesting part: `EF BF BE` **is** valid UTF-8 — Python encodes it, Rust validates it, `iconv` passes it — and APFS refuses it anyway, with the identical error it gives a genuinely malformed byte. So the rule APFS enforces on a filename is stricter than UTF-8 well-formedness, and there is nothing in the error to tell the two cases apart. Private use passes on both platforms; a lone surrogate fails on both, but one layer earlier, in the encoder rather than in the kernel.

That is the practical shape of the whole subject. *Legal but nobody expects it* is exactly the kind of input that finds the layer where an assumption was never written down — which is what [12_Adversarial](../../12_Adversarial/README.md) is about, and why [two readers of one byte string](../../12_Adversarial/parser_differentials/README.md) is the neighbouring page rather than a repetition of this one.

## If you are coming from Python or ABAP

**Python.** `chr()` builds a noncharacter and a private-use character without complaint, `str` holds them, every UTF codec round-trips them, and `unicodedata.category` is the only thing in the standard library that distinguishes either from an ordinary unassigned code point — and it only manages it for private use (`Co`). There is no `is_noncharacter`; write the two range tests. The place this actually bites in Python code is `json.dumps` (which emits them, escaped, quite happily) and any XML library (which will write what it refuses to read). If you are using a private-use code point as an in-band marker, the thing to grep for is where the string crosses a process boundary, not where it is created.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* The `string` type is [the UCS-2 subset of UTF-16](../../09_History/why_utf16_stayed/README.md), so the BMP private use area (`U+E000`–`U+F8FF`) and the BMP noncharacters (`U+FDD0`–`U+FDEF`, `U+FFFE`, `U+FFFF`) each occupy one character position and behave like any other — while the supplementary private use planes need a surrogate pair and will be counted as two by `strlen`, the same trap `😀` sets. `cl_abap_conv_*` converting to a non-Unicode code page will fail on all of them, because no legacy code page has a mapping for a private-use code point. The practical warning is the SAP-flavoured version of this page's closing rule: a private-use code point that means something in one system means nothing in the next one, and a system copy carries the data without carrying the agreement.

## Try it

1. Take the worst text field you have — a name, a description, an address — and count how many of its code points are in the private use area: `sum(1 for c in s if 0xE000 <= ord(c) <= 0xF8FF)`. A non-zero answer on data that came from a desktop application usually means a font's icon travelled with the text.
2. Write one of your own files with a noncharacter in it, then run every tool you would normally trust on it — `wc`, `grep`, `file`, your editor, your diff. Note which ones say nothing.
3. Try `touch` with a noncharacter in the filename on whatever machine you are reading this on, and see which of the two columns above you are in.
4. Find the place in your own code where you join fields with a separator, and ask what happens when the data contains that separator. Then ask whether the answer would change if the separator were `U+FFFF`.
5. If you maintain an XML or database export, feed it a private-use code point and a noncharacter and see which of the two it survives. They are not the same test.

## Practice

**Which of these five code points will a conformant UTF-8 encoder refuse?**

```text
U+FFFE
U+FDD0
U+E000
U+D800
U+0378
```

Write down your count before you read on. Then the harder second question, which is the one the page is really about: for each of the five, would you put it in a file you are sending to somebody else — and is that the same question?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:noncharacters_and_private_use_kata_py -->
*Verified output of [`noncharacters_and_private_use_kata_py.py`](examples/noncharacters_and_private_use_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE QUESTION: WHICH DOES A UTF-8 ENCODER REFUSE?
------------------------------------------------------------------------
   code point   UTF-8              verdict   what it is
   U+FFFE       ef bf be           encoded   noncharacter -- the last but one code point of the BMP
   U+FDD0       ef b7 90           encoded   noncharacter -- first of the block of 32
   U+E000       ee 80 80           encoded   private use -- first of the BMP area
   U+D800       --                 refused   surrogate -- a high surrogate, on its own
   U+0378       cd b8              encoded   unassigned -- a gap that may be filled one day

   refused: 1 of 5

   ONE. Not four, and not three. The one refusal is U+D800, and it is
   refused for a reason no reader guesses from the list: a surrogate is
   not a Unicode SCALAR VALUE, so no UTF has a spelling for it. It is
   plumbing that UTF-16 reserved for itself in 1996.

   Everything else on the list encodes. The two noncharacters encode,
   the private-use character encodes, and so does the unassigned code
   point that is not anything yet. Reserved is not invalid, and a
   conformant DECODER must hand all four of them back to you unchanged
   rather than filtering them out.

THE SECOND HALF: EVERY LAYER DRAWS ITS OWN LINE
------------------------------------------------------------------------
   code point   encoder  name()      XML 1.0  General_Category
   U+FFFE       encodes  ValueError  refuses  Cn
   U+FDD0       encodes  ValueError  carries  Cn
   U+E000       encodes  ValueError  carries  Co
   U+D800       refuses  ValueError  refuses  Cs
   U+0378       encodes  ValueError  carries  Cn

   Four columns, four different answers about the same five values.
   The encoder refuses one. XML refuses TWO, and the second one is the
   interesting half: U+FFFE falls outside XML 1.0's Char production
   while U+FDD0, equally and identically a noncharacter, does not.
   unicodedata names none of the five. And the category column puts
   the two noncharacters in the same box as the merely unassigned
   U+0378, because Cn means unassigned and that is what they are.

   The lesson is not that one of these is right. It is that 'invalid'
   is never a property of a code point on its own -- it is a property
   of a code point AND the door it is standing at.

AND THE PART THE QUESTION DOES NOT ASK
------------------------------------------------------------------------
   Encoding is not the same question as interchange. All four of the
   encodable rows above go into a file happily. Only the first two
   below are things you may legitimately SEND someone, and even the
   first carries a warning:

      U+0378   unassigned   nothing forbids it, and it may become a
                            real letter, at which point your data is
                            retroactively about something
      U+E000   private use  fine inside the agreement that defines it,
                            and meaningless one hop outside
      U+FDD0   noncharacter never. Reserved for internal use, and the
      U+FFFE   noncharacter guarantee that they are never in the input
                            is exactly what they are worth

   Which is why the answer to 'is this legal?' is one, and the answer
   to 'may I put it in the export?' is a different number entirely.
```
<!-- /output -->

</details>

## See also

- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — where `U+FFFE`'s reservation does real work, and the half of this page that was already written
- [The table has a version](../the_table_has_a_version/README.md) — why 66 may go in an answer key when almost no other number from the table may
- [Unicode code points](../unicode_code_points/README.md) — the number line these two regions are carved out of
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — the *scalar value* rule, which is the one an encoder actually enforces
- [`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md) — the surrogate hole, and why `char` refuses exactly one of the classes on this page
- [Preparing a string](../preparing_a_string/README.md) — [RFC 3454 ↗](https://www.rfc-editor.org/rfc/rfc3454) prohibits both of these by number, twenty years before this page
- [Unicode in identifiers](../unicode_in_identifiers/README.md) — where a name refuses all three of *private use*, *noncharacter* and *unassigned* with one error, and the character that does get through is an ordinary letter
- [Bytes that are not text](../../04_Python/surrogateescape/README.md) — the same idea from the other end: to carry a byte you cannot read, spend a code point nobody can legitimately mean
- [Two readers, one byte string](../../12_Adversarial/parser_differentials/README.md) — where *legal but unexpected* stops being a curiosity
- [`find`, and filenames that are bytes](../../11_Tools/find/README.md) — the APFS `EILSEQ` this page sharpens
- [Unicode FAQ: Private-Use Characters, Noncharacters and Sentinels ↗](https://www.unicode.org/faq/private_use.html) — the source, and the answer to *"are noncharacters invalid?"* in two words
- [Unicode Character Encoding Stability Policies ↗](https://www.unicode.org/policies/stability_policy.html) — where the immutability of the set is written down
