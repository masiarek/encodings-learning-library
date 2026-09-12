# A code point is not a character

**Level:** 201 · working knowledge

**One line:** Five rulers can be laid along one string — bytes, code units, code points, grapheme clusters, terminal columns — and they give five different numbers, every one of them correct; `len` is one of them in each language, and it is never the one a person means.

Ask how long `👨‍👩‍👧` is and there is no answer, only a question back: *in what unit?* It is 18 bytes in a file, 8 units to Java, 5 code points to Python, one thing a cursor moves over, and — depending on which program is drawing it — 2, 6 or 8 columns of your terminal. Nobody in that list is confused. They are answering five different questions, and the only mistake available is thinking there was one question.

This is the library's thesis in its sharpest form. [A character is a number](../a_character_is_a_number/README.md) put a number under every character; [Unicode code points](../unicode_code_points/README.md) made those numbers universal. This page is where the tidy correspondence breaks: **a code point was never promised to be a character**. This is not a recent complication either — the UCD dates `U+0301 COMBINING ACUTE ACCENT` to Unicode 1.1, so a character built from two code points has been possible for as long as there has been a Unicode — and every standard library on this page still counts code points as though the two were the same thing.

## The five rulers

| ruler | counts | who returns it |
|---|---|---|
| **bytes** | what the string costs in a file or a socket | Rust `s.len()`, Python `len(s.encode())`, `wc -c` |
| **code units** | 16-bit pieces, so a non-BMP character costs two | Java/JavaScript `.length`, ABAP, `s.encode_utf16().count()` |
| **code points** | entries in the Unicode table | Python `len(s)`, Rust `s.chars().count()` |
| **grapheme clusters** | what a cursor moves over — what a person calls a character | **nothing in either standard library** |
| **terminal columns** | how much screen it occupies | nothing, and see below |

Each row of the example's ladder splits exactly one more ruler off the others. `A` is the degenerate case where all five agree, which is the reason the other four are surprising. `cafe` + `U+0301` separates bytes from code points *and* code points from graphemes — five code points that print as four letters. `日本語` is the first string where the terminal disagrees with everybody: three code points, nine bytes, six columns. `😀` is one code point and two UTF-16 units, which is the whole [surrogate](../../03_Encodings/utf16_and_surrogates/README.md) story and the reason a Java `length()` says 2. And the family emoji separates all five at once.

**The fourth ruler is the one people mean and the one nobody ships.** A grapheme cluster is defined by Unicode's segmentation annex, UAX #29, as a list of numbered boundary rules — and neither Python's nor Rust's standard library implements them. Python's answer is the third-party `regex` module, whose `\X` matches one cluster; Rust's is the `unicode-segmentation` crate. The example here hand-rolls **two** of the rules, over code point ranges written into the file, and prints the list of what that leaves out. That is not a good segmenter. It is a readable one, which is the point: you can see every rule it knows, and therefore exactly how much a real implementation is doing for you.

## The decision this page had to make first

The fifth ruler is the interesting one, and it forced a choice about what may be written down.

This library's hard rule is that **nothing read out of the Unicode table may become an answer key**. `rustc` is not pinned here, and `python3` is pinned only to a minor version whose table changes the day the pin moves — on the machine this page was written, the two answered from Unicode versions a full release apart, which [the table has a version](../the_table_has_a_version/README.md) is entirely about. A character's *name* is safe, because Unicode promises never to change one. A width class is not on that list.

So the example programs read the Unicode table exactly **once**, for `unicodedata.name()` in section 3, and get their other four numbers from arithmetic: UTF-8 spends one, two, three or four bytes on ranges the standard froze; UTF-16 spends one unit inside the BMP and a pair above it; a code point's number never moves; and the grapheme count comes from rules written out in the source. Those four are facts about the string, so they are recorded as an answer key and CI checks them on both platforms.

The column count is not a fact about the string, and the programs say so in the only way that stays honest: **the width table is written into the source rather than looked up**, and every number in the `cols` column is that table's arithmetic. That is not a dodge around the rule. It is the more accurate model, because `unicodedata.east_asian_width()` would have been the wrong program to ask in the first place — **the terminal drawing your text has its own width table, compiled into the terminal, at its own Unicode version.** A width from Python is already a guess about a different program on the same machine.

What the interpreter *does* say is worth seeing, so it goes here, dated, rather than into a key:

```text title="Measured on one Mac, macOS 26.6.2, 2026-09-07 — not machine-checked, because this is exactly the kind of claim that moves"
$ python3 --version
Python 3.14.7
$ python3 -c 'import unicodedata; print(unicodedata.unidata_version)'
16.0.0
$ rustc --version
rustc 1.98.0 (88d9e12ae 2026-08-18)      # and char::UNICODE_VERSION is (17, 0, 0)

east_asian_width, per code point:
  A               Na
  cafe + U+0301   Na Na Na Na A
  nihongo         W W W
  grinning face   W
  family          W N W N W

  Na narrow   W wide   N neutral   A ambiguous
```

Read the `A` on the second row. The table's answer for a combining acute is **ambiguous** — one column in a Western terminal, two in a legacy East Asian one. That is not the table declining to answer; ambiguous *is* the answer, and it means the width depends on a context no string carries. Rust is blunter still: its standard library has no width property at all, so the fifth ruler is not merely unreliable there, it is absent.

And the family emoji has **three** defensible column counts — 8 if you count every code point, 6 if the joiners get no width, 2 if the terminal understands ZWJ and draws one glyph. All three follow a rule you could defend; none of them is a property of the string. Your own terminal has already picked one to draw the table below, and comparing the columns is how you find out which.

## In Python

<!-- output:a_code_point_is_not_a_character_py -->
*Verified output of [`a_code_point_is_not_a_character_py.py`](examples/a_code_point_is_not_a_character_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FIVE RULERS, ONE STRING AT A TIME
   bytes  u16 chars graph cols   what it is
       1    1     1     1    1   A -- all five rulers agree
       6    5     5     4    4   cafe + U+0301 -- a mark is its own code point
       9    3     3     3    6   nihongo -- a wide character costs two columns
       4    2     1     1    2   grinning face -- above U+FFFF: two UTF-16 units
      18    8     5     1    6   family -- one picture, five code points

   bytes  what a file costs, and what Rust's .len() returns
   u16    16-bit units: Java, JavaScript and ABAP call these characters
   chars  code points: what Python's len() returns
   graph  grapheme clusters: what a cursor moves over, and what a
          person means by 'character'
   cols   how wide a terminal draws it -- see section 5

2. EACH ROW SPLITS ONE MORE COLUMN OFF THE OTHERS
   A               1 1 1 1 1   the case that teaches nothing, and the
                               reason every other row is surprising
   cafe + U+0301   bytes and code points part company, and so do code
                   points and graphemes: 5 code points, 4 graphemes,
                   and it prints as four letters
   nihongo         3 code points, 9 bytes, 6 columns -- the first row
                   where the terminal disagrees with everybody
   grinning face   1 code point and 2 UTF-16 units: the BMP boundary,
                   which is why a Java length() says 2
   family          every ruler gives a different answer

3. THE FAMILY, CODE POINT BY CODE POINT
   U+1F468  4 bytes  2 u16   MAN
   U+200D   3 bytes  1 u16   ZERO WIDTH JOINER
   U+1F469  4 bytes  2 u16   WOMAN
   U+200D   3 bytes  1 u16   ZERO WIDTH JOINER
   U+1F467  4 bytes  2 u16   GIRL
   5 code points, 18 bytes, 8 UTF-16 units, and 1 cluster.
   A name is the one question this program asks the Unicode table,
   and it is one of the few questions whose answer Unicode promises
   never to change. That is why this section quotes names, and why
   section 5 refuses to quote a width.

4. WHAT THIS SEGMENTER DOES NOT IMPLEMENT
   A               -> 1 cluster(s): A
   cafe + U+0301   -> 4 cluster(s): c | a | f | é
   nihongo         -> 3 cluster(s): 日 | 本 | 語
   grinning face   -> 1 cluster(s): 😀
   family          -> 1 cluster(s): 👨‍👩‍👧

   Two rules, GB9 and GB11, over ranges written into this file. A
   real UAX #29 implementation reads the Grapheme_Cluster_Break
   property for every code point instead, and it also handles:
     - CR LF as one cluster, and controls as their own
     - spacing marks, which this misses outside U+0300..U+036F
     - regional indicator pairs, so a flag is one cluster
     - emoji modifiers, so a skin tone joins the emoji before it
     - Indic conjunct clusters, the newest rule in the list
   Python has no grapheme segmenter in the standard library; the
   third-party 'regex' module spells one \X. Rust's std has none
   either, and the unicode-segmentation crate is the usual answer.

5. THE FIFTH RULER IS NOT A FACT ABOUT THE STRING
   The 'cols' column above came from this table, written into this
   program on purpose:
     U+0300..U+036F     -> 0   combining marks take no column of their own
     U+200D             -> 0   ZWJ is a joiner, not a glyph
     U+4E00..U+9FFF     -> 2   CJK ideographs are drawn double-width
     U+1F300..U+1FAFF   -> 2   emoji are drawn double-width
     everything else    -> 1

   unicodedata.east_asian_width() would answer this too, and this
   program does not call it. A width class is read out of the
   Unicode table, so recording the answer would make this file a
   fact about whichever Python ran it -- and unlike a name, a width
   class is not one of the properties Unicode promises to freeze.
   The page prints what this machine's table says, in a fence with
   a date on it, which is where a measurement like that belongs.

   It would be the wrong program to ask in any case. The terminal
   drawing this text has its own width table, compiled into the
   terminal, at its own Unicode version -- so a width from Python
   is a guess about a different program on the same machine.

   The family emoji has THREE defensible column counts, and that is
   the strongest evidence here that the fifth ruler measures the
   terminal rather than the string:
      8  every code point counted, joiners included
      6  the same sum, with the joiners given no width
      2  what a terminal that understands ZWJ draws: one glyph,
         the same width as any other emoji
   All three follow a defensible rule, and none of them is a
   property of the string. Your own terminal has already picked one
   of them to draw the table in section 1 -- look at whether the
   columns there line up, and you will know which.

6. SO WHAT DOES len() ANSWER?
   Python   len(s)                 ->  5   code points
   Python   len(s.encode())        -> 18   UTF-8 bytes
   Rust     s.len()                -> 18   UTF-8 bytes
   Rust     s.chars().count()      ->  5   code points
   Java/JS  s.length               ->  8   UTF-16 units
   a person 'how many characters'  ->  1   grapheme cluster

   Four of the six rows are the same question asked of different
   units, and the last one is the question everybody actually asked.
   No standard library on this page answers it.
```
<!-- /output -->

## In Rust

The same five strings, and a language that names the rulers differently enough to catch people out: `len()` is **bytes** here and **code points** in Python.

<!-- output:a_code_point_is_not_a_character_rs -->
*Verified output of [`a_code_point_is_not_a_character_rs.rs`](examples/a_code_point_is_not_a_character_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. FIVE RULERS, AND THE THREE RUST HANDS YOU
   bytes  u16 chars graph cols   what it is
       1    1     1     1    1   A
       6    5     5     4    4   cafe + U+0301
       9    3     3     3    6   nihongo
       4    2     1     1    2   grinning face
      18    8     5     1    6   family

2. THE NAMES ARE THE TRAP
   Rust    s.len()             UTF-8 BYTES      -- an O(1) field read
   Python  len(s)              CODE POINTS      -- a different question
   Rust    s.chars().count()   code points      -- O(n), and it says so
   Java    s.length()          UTF-16 units     -- a third answer

   One spelling, len(), means two different rulers in the two
   languages on this page. Rust makes the count you did not ask
   for expensive to write by accident: .chars().count() is a
   visible walk, where len() is a field on the string.

3. WHAT THE TYPES ACTUALLY GUARANTEE
   a &str is guaranteed valid UTF-8, so these two never disagree:
     family.len()                 = 18
     family.as_bytes().len()      = 18
   a char is a single code point, always 4 bytes as a value:
     size_of::<char>()            = 4
     family.chars().count()       = 5
   and nothing in the standard library counts the fourth ruler:
     family.graphemes()           does not exist
     graphemes(family)            = 1   <- the two rules in this file

   Slicing is where this stops being trivia. &s[0..1] on the
   family panics: byte 1 is inside a four-byte character, and Rust
   refuses rather than hand back half a code point. Python's
   s[0:1] returns the whole emoji, because its index is a code
   point index. Neither one can slice off a whole grapheme.

4. THE FIFTH RULER IS NOT IN THE STANDARD LIBRARY AT ALL
   Python at least has unicodedata.east_asian_width() to argue
   about. Rust's std has no width property at all, and no
   grapheme segmenter. It does carry Unicode tables -- enough for
   is_alphabetic(), for a to_uppercase() that turns one letter
   into two, and for char::UNICODE_VERSION to have a value -- so
   the missing two were left out, not merely never added.
   So the 'cols' column above came from the table in this file:
     U+0300..U+036F   -> 0   combining marks
     U+200D           -> 0   ZWJ
     U+4E00..U+9FFF   -> 2   CJK ideographs
     U+1F300..U+1FAFF -> 2   emoji
     everything else  -> 1

   Both of the missing rulers need a table that changes every
   September, and both have an answer outside std: the
   unicode-segmentation crate for rule 4, unicode-width for rule
   5. Those are versioned separately from the compiler, which is
   the same table skew this library keeps meeting -- moved into a
   Cargo.toml, where at least it has a version number you can read.
```
<!-- /output -->

## Who ships the fourth ruler

"Nothing in either standard library" is true of the two languages this library teaches, and it is not a fact about programming languages. It is a choice each one made, and four of them chose differently. This section exists because of the question that prompted the page: *do we have a page on grapheme clusters — the equivalent term in .NET is text element?*, asked while reading [Microsoft's character encoding introduction ↗](https://learn.microsoft.com/en-us/dotnet/standard/base-types/character-encoding-introduction).

| | what its `length` counts | how you get the fourth ruler | where the segmentation lives |
|---|---|---|---|
| **.NET** | UTF-16 code units | `StringInfo` — **in the box** | the base class library |
| **Swift** | grapheme clusters — that *is* `String.count` | you already have it | the standard library |
| **Rust** | bytes (`len()`) or code points (`chars()`) | the `unicode-segmentation` crate | deliberately outside `std` |
| **Python** | code points | `regex`'s `\X`, or `grapheme`, from PyPI | nowhere |

**.NET is the one worth knowing about, because it is the exception.** It calls the unit a **text element** rather than a grapheme cluster, and `System.Globalization.StringInfo` ships an enumerator for it — one of very few standard libraries that hand you the fourth ruler with no dependency. Both numbers at once, measured below: `"👩🏻‍🚒".Length` is `7` and `StringInfo` walks the same string in **one** step.

**Swift made the opposite trade from Rust, on the same evidence.** `Character` *is* an extended grapheme cluster, so `count` is 1 for both spellings of an e-acute and iterating a string gives you what a reader sees, with `unicodeScalars`, `utf8` and `utf16` as views you ask for by name. The cost is that the default operation is O(n) and its answer moves when the tables underneath are updated. Rust chose the number that cannot change and makes you ask for the other; Swift chose the number people mean and pays for it. Neither is wrong, and the fence below is the bill Swift is paying.

**Python is the outlier, and the absence is the lesson.** It ships the whole character database in `unicodedata` — categories, combining classes, widths — and no segmentation on top of it. So the honest answer to "how do I iterate graphemes in Python" is a dependency or an approximation, which is why the example above hand-rolls two rules and prints what it leaves out rather than pretending. The Python sibling library's [Counting characters ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/counting_characters/index.html) makes the same choice from the other side and marks it as crude on the page; point its rule at the woman firefighter and it answers **2**, because it knows about combining marks and joiners and not about emoji modifiers.

### And the rules themselves have a version

Four real segmenters, on one machine, on one afternoon. The first column is the two-rule subset the example above prints, and it is here to be distrusted.

```text title="Measured on one Mac, macOS 26.6.2, 2026-09-08 — not machine-checked: four of these five are tools this library does not run in CI, and each ships its own copy of the rules"
                                     code    this   PCRE2   Perl    .NET   Swift
   string                          points    page   10.45   5.42   5.0.5   6.3.3
   -----------------------------------------------------------------------------
   WOMAN, MODIFIER, ZWJ, FIRE ENGINE    4       1       1      1       1       1
   two flags -- four regional inds      4       2       1      2       2       2
   HANGUL, as three jamo                3       3       1      1       1       1
   U+0600, then an Arabic 7             2       2       1      1       1       1
   THAI KO KAI, then SARA AM            2       2       1      1       1       1
   a  ZWJ  b                            3       1       2      2       2       2
   DEVANAGARI ka, virama, ssa           3       2       2      1       2       1

   rg 15.1.0 (PCRE2 10.45)   rg -P -o '\X' f | wc -l
   perl v5.42.0              $n++ while $s =~ /\X/g
   .NET 5.0.5                StringInfo.GetTextElementEnumerator
   Swift 6.3.3               String.count
```

**Read the middle rows first**, where four real implementations agree against the subset: three jamo spelling one Hangul syllable (`GB6`–`GB8`), an Arabic number sign that belongs to the digit behind it (`GB9b`, Prepend), a Thai vowel that Unicode classifies as a **letter** and segments as a mark (`GB9a`), and a joiner between two Latin letters, which `GB11` breaks because a ZWJ only welds *pictographs*. That is what a two-rule approximation costs, stated by the implementations rather than by this page.

**Then read the last two rows, where the real ones disagree with each other.**

`क` `्` `ष` — consonant, virama, consonant — is one conjunct to Perl 5.42 and Swift 6.3, and two to PCRE2 10.45 and .NET 5.0.5. Nothing is broken. `GB9c`, the rule that holds an Indic conjunct together, was added to [UAX #29 ↗](https://www.unicode.org/reports/tr29/) for Unicode 15.1, so an implementation built against an earlier revision breaks where a newer one does not. **"How many grapheme clusters" is therefore not a property of the string.** It is a property of the string *and* the UAX #29 revision your library implements — which is [the table has a version](../the_table_has_a_version/README.md) one layer up, with the segmentation *rules* carrying the version instead of the character data. It is also the bill named above: Swift's `count` is the number people mean, and this row is what "the answer moves when the tables update" looks like when it happens to you.

**And one row is a plain defect worth carrying away.** PCRE2 10.45 matches an entire run of regional indicators as a single `\X`: four of them — two flags side by side — come back as one cluster, and so do three. `GB12`/`GB13` pair them up, which Perl, .NET and Swift all do. So `rg -P -o '\X' | wc -l`, which [PCRE2 — the other regex engine](../../11_Tools/pcre2/README.md) recommends and which is still the shortest way to get this number at a prompt, is right on every string on this page except a run of flags.

## If you are coming from Python or ABAP

**Python.** `len(s)` counts code points, and it is the second ruler down from what you probably wanted. The practical rule: `len(s.encode())` for anything with a size limit measured in bytes — a database column, a network frame, a filename — and `len(s)` for nothing in particular, because a code point count is rarely the number any requirement was written in. Slicing has the same problem one level up: `s[0]` on a name stored as `e` + `U+0301` returns the bare `e` and leaves the accent behind as `s[1]`, so a "first initial" taken this way is wrong for exactly the users whose names carry marks. There is no standard library answer for the fourth ruler; `pip install regex` and `regex.findall(r'\X', s)` is the usual one, and `unicodedata.east_asian_width()` is as close as the standard library gets to the fifth — see the fence above for why that number deserves less trust than it looks like it deserves.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* ABAP's `STRING` and `C` fields are **UTF-16 code units**, which is the second ruler, not the third — so `STRLEN( )` on a string containing an emoji returns 2 for one character, for the same reason Java's `length()` does. The history is [UCS-2](../../09_History/why_utf16_stayed/README.md): the type was defined when 16 bits was believed to be enough for every character, and a surrogate pair is read as two characters rather than one. The consequences are the ones this page keeps naming: an `OFFSET`/`LENGTH` substring can cut a surrogate pair in half and produce a field that is not valid text; a `CHAR20` column sized by counting letters on a screen holds fewer than twenty for anyone outside the BMP; and `cl_abap_conv_out_ce` is where you go when the number you actually need is bytes. Grapheme clusters have no representation in ABAP at all, so "first letter of the surname" is a code unit slice and will separate a mark from its letter given the chance.

## Try it

1. Run `python3 -c "s=input(); print(len(s), len(s.encode()))"` and paste in a name from your own user table that has an accent in it. If the two numbers differ by more than you expected, the name is stored decomposed.
2. Take the longest string in a database column you own and ask what unit its limit is in. `VARCHAR(20)` means twenty of *something*, and which one depends on the database, not on the column.
3. Put an emoji in a filename, then run `wc -c`, `wc -m`, and `ls | cat -vet` on it, and account for all three numbers.
4. Compare the `cols` column of the Python output against your own terminal: select the family emoji with the mouse and see how many columns the highlight covers. That tells you which of the three answers *your* terminal picked.
5. `python3 -c "import unicodedata as u; print(u.east_asian_width('é'), u.unidata_version)"` — then run the same line on a different machine, or a different Python, and see whether the version moved.

## Practice

**Five numbers for one Polish word, spelled two ways.**

The word is `żółw` — turtle. Write down all five rulers for it as you would type it, then write them again for the same word **decomposed**, before running anything:

```text
              bytes   u16   code points   graphemes   columns
as typed        ?      ?         ?            ?          ?
decomposed      ?      ?         ?            ?          ?
```

Three of the four letters carry something above or through them. Two questions to answer before you look: how many code points does the decomposed spelling have, and does the grapheme count move? Then the third question, on a different string — how many correct answers are there for the family emoji's column count?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:a_code_point_is_not_a_character_kata_py -->
*Verified output of [`a_code_point_is_not_a_character_kata_py.py`](examples/a_code_point_is_not_a_character_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE FIVE NUMBERS, BOTH SPELLINGS
   bytes  u16 chars graph cols   spelling
       7    4     4     4    4   as you would type it
       9    6     6     4    4   decomposed

   Both spellings print the same four letters, and a reader cannot
   tell them apart on screen. Two of the five rulers noticed.

2. THE TRAP IS IN THE SECOND ROW: 6 CODE POINTS, NOT 8
   composed decomposed   cps   why
   U+017C   z + U+0307     2   ż  the dot above comes off
   U+00F3   o + U+0301     2   ó  the acute comes off
   U+0142   U+0142         1   ł  the STROKE does not -- it is drawn through
   U+0077   U+0077         1   w  nothing to take off
                           6   total

   Four letters, three of them decorated, and only two come apart.
   A stroke through a letter is part of the letter; a mark above it
   is a code point of its own. Nothing about looking at 'ł' tells
   you which kind it is -- you have to ask.

   The graph column did not move, and that is the whole lesson:
   'żółw' is four graphemes in both spellings, because a grapheme
   cluster is what a person calls a letter. Only the code point
   count changed, and code points are the ruler len() reaches for.

3. THE COLUMN COUNT HAS MORE THAN ONE RIGHT ANSWER
   the family emoji: 18 bytes, 8 u16, 5 code points, 1 grapheme
   and for columns, three defensible answers:
      8  every code point counted, joiners included
      6  the same sum, with the joiners given no width
      2  what a terminal that understands ZWJ draws
   If you wrote one number here and did not hedge, that is the
   answer this kata was looking for. The other four rulers are
   properties of the string; the fifth is a property of whatever
   is drawing it.
```
<!-- /output -->

The decomposition is safe to write down, incidentally, for the same reason the names in section 3 of [the Python example](#in-python) are: Unicode promises never to change either. Its normalization stability policy freezes the canonical decomposition of a character that already exists, which is what makes NFC and NFD mean the same thing in five years' time. Width classes carry no such promise.

</details>

## See also

- [Unicode code points](../unicode_code_points/README.md) — the number under the character, before this page complicated it
- [The table has a version](../the_table_has_a_version/README.md) — why the fifth ruler could not be recorded, in full
- [Preparing a string](../preparing_a_string/README.md) — what to do about the two spellings of `é` before you compare them
- [Normalization](../../04_Python/normalization/README.md) — NFC, NFD, and which one to store
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — where the second ruler comes from
- [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) — the same splitting move applied to the word *encoding*, and where a code unit sits in it
- [`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md) — the type that holds one code point and refuses to hold half of one
- [Slicing by byte](../../05_Rust/slicing_by_byte/README.md) — what Rust does when an index lands mid-character
- [PCRE2 — the other regex engine](../../11_Tools/pcre2/README.md) — the one tool already on your machine that can count the fourth ruler, with `rg -P -o '\X'`
- [The cast](../../CAST.md) — where all five demonstration strings come from
- [UAX #29: Unicode Text Segmentation ↗](https://www.unicode.org/reports/tr29/) — the boundary rules themselves, `GB1` to `GB999`
- [Character encoding in .NET ↗](https://learn.microsoft.com/en-us/dotnet/standard/base-types/character-encoding-introduction) — the introduction that prompted the crosswalk above, and where *text element* comes from
- [Counting characters ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/counting_characters/index.html) — the same rulers from Python's side, with a grapheme rule the page marks as crude and this one measures
- [Four lengths ↗](https://masiarek.github.io/rust-learning-library/14_Strings/four_lengths/index.html) — the same rulers from Rust's side
- [It's Not Wrong that "🤦🏼‍♂️".length == 7 ↗](https://hsivonen.fi/string-length/) — one emoji and every honest answer to how long it is
