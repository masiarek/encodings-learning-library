# "Supports Unicode" is a level, not a yes

**Level:** 301 · for anyone who has written `\w+` over a language that is not English

**One line:** [UTS #18 ↗](https://www.unicode.org/reports/tr18/) replaces "does your regex engine support Unicode" with a number — Level 1 is properties, code-point semantics and the character classes; Level 2 is graphemes, canonical equivalence and default word boundaries — and the same `\w+` over one Hindi word finds one word in ripgrep's engine, two or three in PCRE2 depending on its version, and three in Python's `re`, which has no `\p{...}` at all.

## The question, and why it has no yes-or-no answer

*What is different about Unicode regex?*

Nothing, and everything. The syntax is the syntax you already know: `.`, `*`, `[a-z]`, `\d`, `\b`. What changes is that every one of those has to be told what a *character* is, and [there are five honest answers to that](../a_code_point_is_not_a_character/README.md) — four of which a pattern could plausibly be written in: bytes, code units, code points, grapheme clusters. (The fifth, terminal columns, is not something a regex could match even in principle.) So an engine that says "yes, Unicode" has quietly picked one of the four and quietly declined the rest.

This library already makes that move once, for languages: ["Handles Unicode" is four questions](../../10_Best_Practices/what_your_language_gives_you/README.md) splits one reputation into four independent capabilities and shows that no language has all four. This page is that argument's regex-shaped sibling, and it has an advantage over it: for regular expressions, somebody already wrote the questions down and numbered them.

## The levels

[Unicode Technical Standard #18 ↗](https://www.unicode.org/reports/tr18/) — *Unicode Regular Expressions*, Revision 25, dated 2025-01-16 — defines two conformance levels and lists the requirements in each. Its conformance clause C1 names eight requirements for **Level 1**, C2 names seven more for **Level 2** and requires C1 as well, so the levels stack. C3 used to name Level 3, *Tailored Support*, and has been withdrawn — the section is retracted, and the report says it last appeared in version 19. There is no Level 3 to reach any more.

**Level 1 — basic Unicode support.** The engine works in code points, addresses Unicode's own properties, and gets the shorthand classes right.

| | Requirement | What it actually asks for |
|---|---|---|
| **RL1.1** | Hex Notation | a way to write any code point with *its own hex digits* in the syntax — `\U0001F600` qualifies, a surrogate pair or a run of UTF-8 bytes does not |
| **RL1.2** | Properties | `\p{...}` over a named minimum: General_Category, Script and Script_Extensions, Alphabetic, Uppercase, Lowercase, White_Space, Noncharacter_Code_Point, Default_Ignorable_Code_Point, and ANY / ASCII / ASSIGNED |
| **RL1.2a** | Compatibility Properties | `\w`, `\d`, `\s` and friends defined by Annex C's property expressions rather than by an ASCII table |
| **RL1.3** | Subtraction and Intersection | union, intersection and difference *inside* a character class |
| **RL1.4** | Simple Word Boundaries | `\b` over that same word-character class — and a nonspacing mark is never divided from its base |
| **RL1.5** | Simple Loose Matches | at least simple, default Unicode case-insensitive matching, and say which properties are closed |
| **RL1.6** | Line Boundaries | LF, VT, FF, CR, CRLF, NEL, LS and PS all end a line |
| **RL1.7** | Supplementary Code Points | a character above U+FFFF is one unit, surrogate pair or not |

**Level 2 — what a reader means.** Seven more: RL2.1 Canonical Equivalents, RL2.2 Extended Grapheme Clusters and Character Classes with Strings, RL2.3 Default Word Boundaries, RL2.4 Default Case Conversion, RL2.5 Name Properties, RL2.6 Wildcards in Property Values, RL2.7 Full Properties. This is where `\X`, `\b{g}`, and matching `café` against its decomposed spelling live.

**The useful part is C4.** The report expects partial conformance and tells you how to state it: name the levels you complete, then name the extras. So the sentence an engine's documentation should be able to produce is *"Level 1 except RL1.2 and RL1.3, plus `\X` from Level 2"* — which is checkable — instead of *"full Unicode support"*, which is not.

## Two engines, one API, and the switch is a type

Before any of the levels, Python has a split the other engines spell as a flag. `re` on a `str` is Unicode-aware; `re` on a `bytes` is ASCII-only; `re.ASCII` turns the first into the second, and nothing turns the second into the first — `re.UNICODE` on a bytes pattern is a `ValueError`, not a no-op.

That is not carelessness. A byte string carries no encoding, so there is no table an engine could consult, and refusing is the honest answer. What it costs is that the *same pattern text* narrows to ASCII the moment a value moves from a decoded string to a raw pipe, with nothing on the pattern to say so. It is [`str` vs `bytes`](../../04_Python/str_vs_bytes/README.md) again, wearing a regex.

## The finding worth the page

Python's `re` has **no `\p{...}` syntax at all**. Not an old list of properties, not a partial one — the escape does not exist, and `re.compile(r'\p{L}')` raises. RL1.2 is the first substantive requirement of Level 1 and RL1.2a is written in terms of it, so on the standard's own terms the module every Python program imports is below Level 1. The properties are still in the standard library, just not in the engine: `unicodedata.category`, `.name` and `.numeric` reach them one character at a time. The third-party [`regex` module ↗](https://pypi.org/project/regex/) is where `\p{...}` lives in Python, and it is not what `import re` gives you.

The module knows. Its own documentation names UTS #18 exactly once (checked 2026-09-08 against the 3.x [`re` page ↗](https://docs.python.org/3/library/re.html)), and it is about RL1.3: nested sets and set operations *as in Unicode Technical Standard #18* might be added later, and in the meantime a `FutureWarning` is raised in ambiguous cases. So the interpreter can already tell that `[\w&&\d]` was meant as an intersection, warns you, and matches every word character anyway — measured on CPython 3.12, 3.13 and 3.14.

## In Python

The program below takes the Level 1 requirements one at a time and prints what `re` does about each, then crosses into Level 2 for canonical equivalence and the dot. Where a fact about the Unicode table would have been the answer — how many decimal digits exist, how many marks — it prints the *disagreement count* instead, which is zero or is not, whatever table your Python was built from ([why that distinction matters](../the_table_has_a_version/README.md)).

<!-- output:what_a_regex_matches_py -->
*Verified output of [`what_a_regex_matches_py.py`](examples/what_a_regex_matches_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE API, TWO ENGINES, AND THE SWITCH IS THE TYPE
------------------------------------------------------------------------
   the digits १२३   U+0967 U+0968 U+0969

   r'\d+'  against the str                 True
   rb'\d+' against the same bytes          False
   r'\d+'  against the str, with re.ASCII  False
   int() on that str                       123
   rb'\d+' with re.UNICODE                 ValueError -- there is no such mode

   Same three characters, same pattern text, two answers. A `str`
   pattern is Unicode-aware and a `bytes` pattern is ASCII-only, and
   `re.ASCII` turns the first into the second. There is no flag that
   turns the second into the first: the type IS the mode, and asking
   for re.UNICODE on bytes is refused rather than ignored.

   Nothing here is careless. A byte string has no encoding attached, so
   there is no table an engine could consult -- the refusal is the
   honest answer. What it means in practice is that the same regex
   moved from a decoded string to a raw pipe silently narrows to ASCII.

2. RL1.2 PROPERTIES -- THE ONE PYTHON DOES NOT HAVE AT ALL
------------------------------------------------------------------------
   re.compile(r'\p{L}')               raises re.error
   re.compile(r'\pL')                 raises re.error
   re.compile(r'\p{Script=Greek}')    raises re.error
   re.compile(r'\p{Alphabetic}')      raises re.error

   RL1.2 asks for a minimal list of properties addressable from the
   pattern: General_Category, Script and Script_Extensions, Alphabetic,
   Uppercase, Lowercase, White_Space, Noncharacter_Code_Point,
   Default_Ignorable_Code_Point, and ANY / ASCII / ASSIGNED.

   Python's `re` has no syntax for any of them. Not a partial list, not
   an older list -- no \p{...} at all, so RL1.2 is not partly met, and
   nor is RL1.2a, which is written in terms of it. That is the single
   largest thing on this page: the module every Python program reaches
   for is below Level 1 by the standard's own first substantive test.

   The properties are still in the standard library, just not in the
   regex engine -- `unicodedata.category`, `.name`, `.numeric` and the
   `str.is*` methods reach some of them, one character at a time. The
   third-party `regex` module is where \p{...} lives in Python, and it
   is not what `import re` gives you.

3. RL1.2a COMPATIBILITY PROPERTIES -- WHAT \w AND \d ARE SUPPOSED TO BE
------------------------------------------------------------------------
   Annex C of the report defines the two classes every engine ships:

       \d   \p{gc=Decimal_Number}
       \w   \p{alpha} + \p{gc=Mark} + \p{digit}
            + \p{gc=Connector_Punctuation} + \p{Join_Control}

   Three of those five terms are a general category -- Mark, Connector
   Punctuation, and \p{digit}, which Annex C says is gc=Decimal_Number --
   so a sweep over every code point can check them with no table this
   program does not already have. Counts of characters move with the
   Unicode version and are not printed; disagreements are the claim.

   code points where \d disagrees with gc=Nd        0
   marks (gc=M*) that \w matches                    0
   connector punctuation (gc=Pc) that \w matches    1

   So \d is exactly right, and \w holds not one Mark of the thousands
   there are, and exactly one connector. That one is the underscore,
   written into the engine as a literal rather than looked up:
       U+005F LOW LINE    gc=Pc   \w matches it: True
       U+203F UNDERTIE    gc=Pc   \w matches it: False

   And here is what the missing Mark costs, in a word chosen because
   it is the name of a language, written in that language:

       हिन्दी   U+0939 U+093F U+0928 U+094D U+0926 U+0940
       U+0939  gc=Lo   in \w: yes
       U+093F  gc=Mc   in \w: NO
       U+0928  gc=Lo   in \w: yes
       U+094D  gc=Mn   in \w: NO
       U+0926  gc=Lo   in \w: yes
       U+0940  gc=Mc   in \w: NO

       re.findall(r'\w+', ...) finds 3 words: ह न द
       re.fullmatch(r'\w+', ...)     False

   Three of the six characters are marks -- two vowel signs and a
   virama -- and \w rejects all three, so one word comes apart into
   three consonants. The pattern did not fail. It reported success,
   three times, with a wrong answer each time, which is the shape this
   whole library keeps meeting.

4. RL1.3 SUBTRACTION AND INTERSECTION -- COMPILES, MEANS SOMETHING ELSE
------------------------------------------------------------------------
   re.compile(r'[\w&&\d]')     compiles
   ...and it matches '&'       True
   ...and it matches 'a'       True

   RL1.3 wants union, intersection and set difference inside a
   character class, so that [\w&&\d] means the characters that are both.
   Python has no such operator, so the two ampersands are just two more
   members of the class: the expression means \w, or '&', or \d. It
   does not raise, it does not warn on the page, and it matches every
   word character -- the opposite of an intersection.

   This is the failure mode worth remembering from the whole page. A
   missing \p{...} announces itself; a missing set operator quietly
   turns a narrowing expression into a widening one.

5. RL1.4 SIMPLE WORD BOUNDARIES -- THE MARK IS NOT ITS OWN WORD
------------------------------------------------------------------------
   The requirement is two sentences: the word character class covers
   Alphabetic plus the decimals plus ZWNJ and ZWJ, and -- separately --
   nonspacing marks are never divided from their base characters.

   re.findall(r'\b\w+\b', hindi)             ['ह', 'न', 'द']
   re.findall(r'\b\w+\b', 'cafe'+U+0301)     ['cafe']

   The second line is the sharper one, because the string is four
   letters of ASCII and one accent. \b puts the boundary after the `e`
   and leaves the acute outside the word, so a pattern anchored on \b
   matches `cafe` and reports it as a whole word -- in a string whose
   whole word is `café`. Nothing about that is visible in the output.

6. RL1.5 SIMPLE LOOSE MATCHES -- THE CLOSURE IS NOT UNICODE'S
------------------------------------------------------------------------
   Which characters does re.IGNORECASE consider equal to each letter,
   and does str.casefold() -- Python's own full case folding -- agree?

   re.I class of 'i': U+0049 U+0069 U+0130 U+0131
      casefold puts those in 3 classes: U+0069 / U+0069 U+0307 / U+0131
   re.I class of 'k': U+004B U+006B U+212A
      casefold puts those in 1 class: U+006B
   re.I class of 's': U+0053 U+0073 U+017F
      casefold puts those in 1 class: U+0073

   re.fullmatch('ss', sharp-s, re.I)   False
   sharp-s.casefold()                  'ss'

   Two different disagreements, in two directions.

   The sharp-s one is allowed and is the point of the word `simple` in
   the requirement's title: Level 1 asks only for simple case folding,
   where a match may not change length, so 'ss' is not required to
   match it. casefold() does full folding and gives 'ss'. Both correct.

   The `i` one is not the same shape. Unicode's default simple folding
   leaves U+0130 and U+0131 -- the Turkish dotted capital and dotless
   small i -- in classes of their own, and only the Turkic tailoring
   merges them with the ASCII pair. Python's re merges them always, in
   every locale, because its case-insensitive matching closes over the
   simple case MAPPINGS rather than over case FOLDING. Its own
   casefold() splits the same four characters into three classes and
   is the half that agrees with Unicode.

7. RL1.6 LINE BOUNDARIES -- ONE STANDARD LIBRARY, TWO ANSWERS
------------------------------------------------------------------------
   The report names seven newline characters plus the CR LF pair.
   Python's own str.splitlines() knows them; Python's own re does not.

   character              . matches it   $ before it (re.M)   splitlines
   U+000A LINE FEED       False          True                 2
   U+000B LINE TAB        True           False                2
   U+000C FORM FEED       True           False                2
   U+000D CARRIAGE RET    True           False                2
   U+0085 NEXT LINE       True           False                2
   U+2028 LINE SEP        True           False                2
   U+2029 PARA SEP        True           False                2

   Read the last two columns together. `re` breaks a line at exactly
   one of the seven; splitlines() breaks at all seven. So a file read
   with .splitlines() and searched with a MULTILINE `$` is being cut
   twice, by two functions from the same standard library that do not
   agree about where a line ends -- and `.`, which is documented as
   'any character except a newline', matches six of the seven.

8. RL1.1 AND RL1.7 -- THE TWO PYTHON PASSES OUTRIGHT
------------------------------------------------------------------------
   r'\U0001F600' matches the emoji           True
   r'[\U0001F600-\U0001F64F]' is ONE unit    True
   r'\N{LATIN SMALL LETTER E WITH ACUTE}'    True
   len(one astral character)                1

   RL1.1 wants the code point's own hex digits to appear in the syntax,
   which rules out spelling an astral character as a surrogate pair or
   as its UTF-8 bytes. `\U0001F600` contains 1F600, so it qualifies;
   `\N{...}` is a bonus the requirement does not ask for.

   RL1.7 wants a supplementary code point handled as one unit. Since
   PEP 393 a Python str is a sequence of code points with no surrogate
   pairs in it, so this one is free -- and it is not free in every
   language: the same requirement is the whole of why a Java or
   JavaScript engine has to say something about UTF-16.

9. THE SCORECARD FOR LEVEL 1
------------------------------------------------------------------------
   RL1.1  Hex Notation                    yes   \U0001F600 and \N{NAME}
   RL1.2  Properties                      NO    no \p{...} syntax exists
   RL1.2a Compatibility Properties        NO    \w holds no Mark at all
   RL1.3  Subtraction and Intersection    NO    && is two literal ampersands
   RL1.4  Simple Word Boundaries          NO    \b divides a mark from its base
   RL1.5  Simple Loose Matches            ~     closes over mappings, not folding
   RL1.6  Line Boundaries                 NO    one separator of seven
   RL1.7  Supplementary Code Points       yes   a str is code points

   Two clear passes, five clear failures, one that depends on how you
   read `at least`. The report allows exactly this -- an implementation
   may claim Level 1 except for named requirements -- so the useful
   sentence is not 'Python's re does not support Unicode'. It is:
   Level 1 except RL1.2, RL1.2a, RL1.3, RL1.4 and RL1.6.

   That sentence is checkable, and 'supports Unicode' is not.

10. LEVEL 2, RL2.1 -- CANONICAL EQUIVALENCE, AND WHAT THE FIX IS
------------------------------------------------------------------------
   composed    café   U+0063 U+0061 U+0066 U+00E9
   decomposed  café   U+0063 U+0061 U+0066 U+0065 U+0301
   the two strings are equal                    False
   NFC(decomposed) == composed                  True

   re.search(composed, decomposed_text)         False
   re.fullmatch(r'caf.', decomposed_text)       False
   re.match(r'caf.', decomposed_text) grabs     'cafe'
   re.fullmatch(r'caf..', decomposed_text)      True
   after ud.normalize('NFC', text)              True

   The third line is the one to keep. `caf.` was written by somebody
   who meant 'caf and one more character', and on the decomposed
   spelling the dot takes the bare `e` and stops -- the accent is left
   behind, outside the match, and the captured group is a word that is
   not in the file. Nothing raised.

   RL2.1 is Level 2 because doing it inside the engine is genuinely
   hard: canonical equivalence can reorder and merge characters, so a
   pattern would have to match parts of characters. The report's own
   advice is the last line above -- put the text in a known
   normalization form, write the pattern for that form, and match code
   point by code point as usual. Normalization is the fix. A cleverer
   pattern is not, and the conformance clause says a system meets RL2.1
   this way as long as it says so out loud.

11. LEVEL 2, RL2.2 -- '.' IS A CODE POINT, AND THAT IS BY DESIGN
------------------------------------------------------------------------
   the family emoji           👨‍👩‍👧‍👦
   UTF-8 bytes                25
   code points                7
   what a person counts       1
   re.findall(r'.', ...)      7 matches
   the first one is           👨   U+1F468

   re has \X                   no -- re.error

   `.` matched one seventh of a family and handed back a man. That is
   not a bug in `re`: the report says in as many words that an engine
   may treat `.` as one code point and spell the grapheme cluster \X,
   and RL2.2 is the requirement to provide the second one. Python's re
   provides neither \X nor any other way to ask the question.

   The 25 bytes above become 26 in a file, once the newline is on the
   end -- which is the number the PCRE2 page measured with wc -c.
```
<!-- /output -->

## The same questions, put to two other engines

Neither macOS nor Ubuntu ships `rg`, so CI does not have it and **no answer key on this page comes from a tool**. What follows was run twice, on the two machines in the caption, and diffed — they are identical apart from the version line and one row, and that row is the interesting one.

```text title="Measured 2026-09-08 — macOS 26.6.2 (rg 15.1.0 brew, PCRE2 10.45, python 3.14.7) and ubuntu:24.04 (rg 14.1.0 apt, PCRE2 10.42, python 3.12.3). Diffed: identical apart from the version line and the `rg -P \w+` row. Not machine-checked: CI has no rg."
-- RL1.2 properties
  rg     \p{Script=Greek}+               αβγ
  rg -P  \p{Greek}+                      αβγ
  rg     \p{Alphabetic}+                 αβγ abc

-- RL1.3 set operations
  rg     [\p{L}&&\p{Greek}]              α β γ
  rg     [\p{L}--\p{Greek}]              a b c
  rg -P  [\w&&\d]                        α β γ a b c

-- RL1.2a  \w+ over the Hindi word हिन्दी
  rg     \w+                             हिन्दी
  rg -P  \w+                             ह न्द          # PCRE2 10.45
  rg -P  \w+                             ह न द          # PCRE2 10.42
  python \w+                             ह न द

-- RL2.2 grapheme clusters
  rg     \X                              PARSE ERROR
  rg -P  \X                              👨‍👩‍👧‍👦
  rg     \b{g}                           PARSE ERROR
  rg     . (count over the family)       7
  rg -P  \X (count over the family)      1

-- RL2.1 canonical equivalence: composed pattern, decomposed file
  rg     composed pattern                (no match)
  rg -P  composed pattern                (no match)
  python re.search                       False
```

**One word, three answers, and none of them is a bug.** `हिन्दी` is six code points: three consonants, two vowel signs and a virama, so half of it is marks. Annex C says `\w` includes `\p{gc=Mark}`, so the whole word is one match — which is what ripgrep's default engine gives. PCRE2 10.45 takes the nonspacing marks and not the spacing ones, so it gives two; PCRE2 10.42, three releases earlier, takes none and gives three. Python takes none either, so it also gives three. A `\w+` that counts words in that file returns 1, 2 or 3 depending on which of three engines you reached for, and every one of them exits 0.

**And ripgrep's `\w` is not merely closer, it is exact.** Sweeping every code point that is not a control or a surrogate — 1,111,999 of them, a figure no Unicode version can move — and comparing each engine's `\w` against Annex C's expression written out longhand as `[\p{Alphabetic}\p{M}\p{Nd}\p{Pc}\p{Join_Control}]`, in ripgrep's own property syntax because it is the only one of the three that can express it:

```text title="Measured 2026-09-08 on the same two machines. The three engines carry three different Unicode tables, so the SIZES below move and only the Rust engine's zeros are a like-for-like comparison — both halves of that row came out of one build. macOS first, ubuntu:24.04 second where they differ."
  the reference set, [\p{Alphabetic}\p{M}\p{Nd}\p{Pc}\p{Join_Control}]   144667 / 139612

                       in \w but not in the spec    in the spec but not in \w
  rg (Rust regex)                             0                            0
  rg -P (PCRE2)                     5611 / 895               613 / 6959
  python re                            915 / 915             2642 / 2591
```

**Zero and zero, on both machines.** That row is the like-for-like one: both sides of it were computed by the same build from the same tables, so it is a statement about the definition and not about anybody's Unicode version. It is the cleanest Level 1 result in this library. The crate says as much itself — its documentation claims it "almost fully implements 'Basic Unicode Support' (Level 1)" and virtually none of Level 2, which is exactly the sentence this page is asking every engine to be able to write.

**The other two rows have numbers in both columns, and that is the shape to notice.** Python and PCRE2 are each *narrower* than the specification in one direction and *wider* in the other: they miss the marks, and they both match `½` and `²`, which are `gc=No` and appear nowhere in Annex C's `\w`. So "Python's `\w` is basically ASCII" is the wrong summary — it is a different set, not a smaller one, and the two engines' figures move with their tables in a way the Rust engine's zeros cannot.

**The PCRE2 row is a version split, not a platform one.** PCRE2 10.45 puts nonspacing marks in `\w` and 10.42 does not, which moves the Hindi word between two and three. Same shape as the `xxd -e` note in [CONTRIBUTING](../../CONTRIBUTING.md): nothing about the platform predicts it, the *version* does. The [PCRE2 page](../../11_Tools/pcre2/README.md) already says PCRE2 carries its own copy of the Unicode tables on its own release schedule; this is that sentence with a number attached.

## Level 2, and the two consequences you will actually meet

**`.` matches a code point.** The report says this in as many words — an engine may treat `.` as one code point and spell the grapheme cluster `\X`, and RL2.2 is the requirement to provide the second one. So `re.findall(r'.', family_emoji)` returns **seven** matches for one picture, and the first of them is a man. On the decomposed spelling of `café` — `c`, `a`, `f`, `e`, `U+0301` — the pattern `caf.` matches `cafe` and leaves the accent outside the match, so what the engine hands back is a word that is not in the file. That is [a code point is not a character](../a_code_point_is_not_a_character/README.md), arriving through a quantifier.

**Canonical equivalence is not a pattern problem.** A regex written for `café` does not match `café` — same picture, different code points, no match, no error. There is no cleverer pattern: RL2.1 is Level 2 precisely because matching under canonical equivalence can require reordering and merging characters, so the engine would have to match *parts* of characters. The report's own advice is the fix everyone actually uses — put the text in a known normalization form, write the pattern for that form, match code point by code point — and the conformance clause says a system that does this outside the engine still meets RL2.1, as long as it documents that it does. So [normalization](../../04_Python/normalization/README.md) is not a workaround here. It is the sanctioned implementation.

The limit is worth knowing before you reach for it: normalization fixes RL2.1 and nothing else. It does not put the marks back into `\w`, because Devanagari vowel signs have no precomposed form to compose *into* — the kata below measures exactly that.

## Choosing an engine, and saying why

| You want | Reach for |
|---|---|
| `\p{Script=...}`, `\p{Alphabetic}`, set operations | `rg`'s default engine, or the [`regex` module ↗](https://pypi.org/project/regex/) in Python — `re` has none of it |
| `\w` that agrees with the specification | `rg`'s default engine; it is the one measured at zero disagreements |
| one grapheme cluster, `\X` | `rg -P` — [the only engine already on your machine that can](../../11_Tools/pcre2/README.md) |
| a match under canonical equivalence | no engine here. Normalize first; that is the standard's answer, not a compromise |
| byte semantics on purpose | `re` on `bytes`, or `rg --no-unicode` — [same decision, two spellings](../../11_Tools/ripgrep/README.md) |
| stdlib only, and you accept the level | `re`, having written down which requirements you are missing |

## If you are coming from Python or ABAP

**Python.** The four things to take away are all about `re` rather than about Unicode. Its `\d` is exactly right and its `\w` is not, so `\w+` is safe over digits and unsafe over any script that writes vowels as marks — Devanagari, Bengali, Tamil, Thai, Arabic with vowel points. Its `\b` inherits that, so `\b\w+\b` reports `cafe` as a whole word inside `café`. It has no `\p{...}`, so a script or a property test has to be done character by character through `unicodedata`, or by installing [`regex` ↗](https://pypi.org/project/regex/), which is a drop-in that adds `\p{...}`, `\X`, set operations and full case folding — the shortest route to Level 1 in Python is `pip install regex`, and that is a normal answer rather than a defeat. And `re.IGNORECASE` closes over Unicode's simple case *mappings* rather than over case *folding*, which is why `i`, `I`, `İ` and `ı` are all one class to it while its own `str.casefold()` splits them into three; when the comparison matters, fold with `casefold()` and compare, do not ask the pattern ([preparing a string](../preparing_a_string/README.md)).

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* Which engine `FIND ... REGEX` and `cl_abap_regex` sit on has changed across releases, so *which row of the table above describes your system* is a per-release question and not one to take from this page — the [PCRE2 page](../../11_Tools/pcre2/README.md) says the same thing and for the same reason. The good news is that the question is now cheap to ask: run `\w+` over one marked-up word on the system that will run the job and count the matches, exactly as you would verify a code page number rather than quote one. Two things transfer whatever the release. The `string` / `xstring` boundary is the same one Python draws between `str` and `bytes`, and it decides the same thing: a regex over an `xstring` has no characters to work with. And ABAP is [UCS-2](../../09_History/why_utf16_stayed/README.md), so RL1.7 is the requirement to ask about first — a pattern that quantifies over a character above U+FFFF is quantifying over half of one.

## Try it

1. Run `\w+` over a word in a script you use that writes vowels as marks, in whatever language you work in. Count the matches, then count the words. If the two agree, find out whether your engine is `\p{gc=Mark}`-aware or whether your word simply had no marks in it.
2. Take a regex from your own codebase that uses `\b` or `\w`, and run it against the same input twice — once as `str`, once as `bytes` from `open(path, 'rb')`. Any difference is the second engine you did not know you had.
3. Find your engine's Unicode level in its own documentation, and notice what it chooses to say. Rust's `regex` crate names its level in the first screen; Python's `re` page mentions UTS #18 once, about the one feature it does not have. An engine that will not name a level is telling you something too.
4. Grep your codebase for `\d` in patterns applied to user input, then decide, per site, whether Devanagari digits passing that check is a feature or a hole. `int('१२३')` is `123`, so the two halves of your validator may already disagree.

## Practice

**Six expressions, and the requirement each one is about.** Every line is stdlib `re` with no flags beyond the ones written down. Write all six answers before running any of them. Four names, and the first two are the same word twice: `composed` is the four code points `c` `a` `f` `e-acute`, `decomposed` is the five `c` `a` `f` `e` `U+0301`, `hindi` is `हिन्दी`, and `deva` is `१२३`.

```python
len(re.findall(r'\w+', hindi))
bool(re.fullmatch(rb'\d+', deva.encode()))
bool(re.search(composed, decomposed))
re.match(r'caf.', decomposed).group()
bool(re.fullmatch(r'[\w&&\d]', '&'))
len(re.findall(r'.', 'a\u2028b'))
```

Then, without a machine: name the UTS #18 requirement each line is about — one of them has no number, and finding out why is the point of that line. Finally the half that decides whether you have read the page: **which of the six does `unicodedata.normalize('NFC', ...)` fix?** Two of them, and two more that look identical in kind are untouched by any normalization form there is.

```bash
python3 02_Characters/what_a_regex_matches/examples/what_a_regex_matches_kata_py.py
```

<details markdown="1">
<summary><strong>Answers</strong></summary>

Every row of this key is the same on every machine. It was diffed byte for byte across CPython 3.12, 3.13 and 3.14 — three different Unicode tables — before it was recorded, so a row that does not match on your machine is a finding rather than a difference of setup.

<!-- output:what_a_regex_matches_kata_py -->
*Verified output of [`what_a_regex_matches_kata_py.py`](examples/what_a_regex_matches_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
PART ONE -- SIX EXPRESSIONS
------------------------------------------------------------------------

   #  expression                                    answer    requirement
   1  len(re.findall(r'\w+', hindi))                3         RL1.2a
   2  bool(re.fullmatch(rb'\d+', deva.encode()))    False     --
   3  bool(re.search(composed, decomposed))         False     RL2.1
   4  re.match(r'caf.', decomposed).group()         cafe      RL2.1
   5  bool(re.fullmatch(r'[\w&&\d]', '&'))          True      RL1.3
   6  len(re.findall(r'.', 'a' + U+2028 + 'b'))     3         RL1.6

   1. one word, three matches: \w has no Mark in it
   2. a bytes pattern is ASCII-only; the str one answers True
   3. same picture, different code points, no match
   4. the dot took the bare e and left the accent behind
   5. no set operators, so && is two more class members
   6. '.' means 'not U+000A', not 'not a line separator'

   Line 2 is the one with no RL number, and it is the one most likely
   to be in your code: it is not a shortfall in the engine, it is the
   OTHER engine. `re` on bytes is a deliberate ASCII matcher, because
   a byte string carries no encoding for it to consult. The switch is
   the argument's type, so it flips when a value moves from a decoded
   string to a raw pipe, and no flag on the pattern will tell you.

   the same three characters through splitlines() 2 lines
   Line 6 next to that one is the whole of RL1.6: the same standard
   library reads the same three characters as one line and as two.


PART TWO -- WHICH OF THE SIX DOES NORMALIZATION FIX?
------------------------------------------------------------------------

   #  expression                            as it stands   over NFC text  moved?
   1  len(findall(r'\w+', hindi))           3              3              no
   3  bool(search(composed, text))          False          True           YES
   4  match(r'caf.', text).group()          cafe           café           YES
   6  len(findall(r'.', a + U+2028 + b))    3              3              no

   Two of the four move and two do not, and the split is the lesson.

   3 and 4 are fixed outright, because RL2.1 is the requirement that
   normalization IS the implementation of. The report says so: put the
   text in a known form, write the pattern for that form, match code
   point by code point. A system that does this conforms, provided it
   documents that it does.

   1 and 6 do not move an inch, and no normalization form will move
   them. NFC composes a base and a mark where a single character for
   the pair exists; Devanagari vowel signs have no precomposed forms,
   so the marks are still there and \w still refuses them. U+2028 is
   not a decomposition of anything. Normalization is a fix for one
   named requirement, not a general repair for Unicode text.

   5 is not in the table because there is nothing to normalize: the
   pattern is wrong about the ENGINE, not about the string. It is the
   only one of the six that silently widens rather than narrows, and
   the only one that would still be wrong on an empty file.
```
<!-- /output -->

</details>

## See also

- ["Handles Unicode" is four questions](../../10_Best_Practices/what_your_language_gives_you/README.md) — the same move for languages rather than regex engines, and the page this one is a sibling of
- [A code point is not a character](../a_code_point_is_not_a_character/README.md) — the five rulers this page's engines are choosing between; `.` is the third of them, and RL2.2 is the requirement to give you a syntax for the fourth
- [Normalization](../../04_Python/normalization/README.md) — the fix RL2.1 blesses, and the two spellings of `café` it moves between
- [PCRE2 — the other regex engine](../../11_Tools/pcre2/README.md) — `\X`, measured, and the one engine here that can count graphemes
- [`ripgrep` — the Rust grep](../../11_Tools/ripgrep/README.md) — the engine that scored zero disagreements, and its `--no-unicode` switch
- [`grep` on text that is not ASCII](../../11_Tools/grep/README.md) — the engine whose answer depends on the locale instead of on a level
- [The table has a version](../the_table_has_a_version/README.md) — why the counts in this page's sweeps could not become answer keys
- [Preparing a string](../preparing_a_string/README.md) — case folding done properly, which is what `re.IGNORECASE` is not
- [Case is not a per-character operation](../case_is_not_per_character/README.md) — the *transformation* half of the case question this page measures the matching half of, including why `re.fullmatch('ß', 'SS', re.IGNORECASE)` is `False`
