# The typical words

**Level:** reference · for anyone reading somebody else's encoding example

**One line:** Tutorials, test suites and bug reports keep reaching for the same few dozen words — `café`, `naïve`, `Straße`, `żółw`, `文字化け`, `💩` — and each one is there for one property, so the word tells you what the example is about to show you before it shows you.

```python
"café".encode()                                     # b'caf\xc3\xa9'  <- 4 characters, 5 bytes
"café".encode().decode("cp1252")                    # 'cafÃ©'          <- the shape to recognise
bytes(b & 0x7F for b in "Привет".encode("koi8_r"))  # b'pRIWET'        <- KOI8-R with every top bit cleared
```

Three words, three properties: an accent costs a second byte; a second byte read through the wrong table becomes two characters; and one Cyrillic table was laid out so that losing the eighth bit still leaves something you can read. Most encoding examples are one of a few dozen properties like these, wearing a word — and the same words come back so often that knowing which property each one carries saves reading the rest of the example.

## Three lists, three jobs

This library already keeps two lists of strings, and this page is a third. They are easy to confuse:

| list | whose words | what it is for |
|---|---|---|
| [The cast](../../CAST.md) | this library's | the fixed vocabulary every page here demonstrates with, so a reader learns `é` once |
| [The hard strings](../hard_strings/README.md) | yours, to test with | one string per behaviour, to point at a form or an API and see what breaks |
| **The typical words** | everybody else's | the words other people's examples are made of, and the property each one is there to show |

The cast's first rule still stands — [reach for a cast member first](../../CAST.md#rules) — and nothing here is a licence to open a lesson with `naïve`. This page is a field guide instead: when a blog post, an answer or a bug report leads with one of these words, the tables below say what it is about to demonstrate and which page of this library shows the same thing, usually with a cast member standing in. A ★ marks a word that *is* in the cast. Every count is printed by the program at the [foot of the page](#in-python).

## Accented Latin: bytes part company with characters

| word | there to show | here |
|---|---|---|
| `café` ★ | one accent is enough: 4 characters and 5 bytes, and `cafÃ©` when two tables are confused | [The cast](../../CAST.md), [Mojibake](../../03_Encodings/mojibake/README.md) |
| `naïve` | English is not ASCII either — and its `ï` is in Latin-1 but missing from ISO-8859-2 | [Code pages](../../02_Characters/code_pages/README.md) |
| `résumé` | two accents, so four spellings that draw identically | [The hard strings](../hard_strings/README.md), whose first section counts them |
| `Iñtërnâtiônàlizætiøn` | every mark at once — a stress test more than a lesson, and one the strip-the-accents recipe fails, leaving `æ` and `ø` behind | [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) |

## Central Europe: which code page?

| word | there to show | here |
|---|---|---|
| `żółw` ★ | Latin-1 cannot hold it; both Polish tables can, and write it byte for byte the same | [Code pages](../../02_Characters/code_pages/README.md) |
| `Łódź` ★ | the word the two Polish tables write *differently* — `ź` is `BC` in ISO-8859-2 and `9F` in Windows-1250 — and a capital, `Ł` = `C5 81`, whose UTF-8 lands on a byte Windows-1252 leaves empty | [Code pages](../../02_Characters/code_pages/README.md), [The mojibake round trip](../../07_Real_Data/mojibake_round_trip/README.md) |
| `zażółć gęślą jaźń` ★ | all nine Polish letters in one line | [The cast](../../CAST.md) |
| `Árvíztűrő tükörfúrógép` | Hungarian's test phrase (*flood-resistant mirror-drilling machine*): all nine of its accented vowels, two of which — `ő` and `ű` — Latin-1 lacks, so ISO-8859-2 bytes read as Latin-1 come out `Árvíztûrõ`, wrong in a way that looks nearly right | [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) |
| `Příliš žluťoučký kůň úpěl ďábelské ódy` | the Czech equivalent: all fifteen of its accented letters | [Whole sentences](#whole-sentences), below |

## Case and normalization: one letter, several answers

| word | there to show | here |
|---|---|---|
| `Straße` | `upper()` gives `STRASSE`, one letter longer | [The cast](../../CAST.md) (`ß`), [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) |
| `İstanbul` | `lower()` gives nine code points for eight letters; and under a Turkish locale an ordinary `i` uppercases to `İ` — the [Turkey test ↗](https://www.moserware.com/2008/02/does-your-code-pass-turkey-test.html) | [The hard strings](../hard_strings/README.md#the-row-that-needs-a-fourth-language-to-show-it) |
| `ΟΔΥΣΣΕΥΣ` | *Odysseus* in capitals: the last `Σ` lowercases to the final form `ς`, the others to `σ` | [Case is not a per-character operation](../../02_Characters/case_is_not_per_character/README.md) |
| `Ångström` | `Å` has three spellings — `U+00C5`, `A` + `U+030A`, and `U+212B ANGSTROM SIGN` — and NFC makes them one | [Normalization](../../04_Python/normalization/README.md) |
| `Nguyễn` | two marks on one letter — spelled out, `ễ` is `e` + `U+0302` + `U+0303` — and a Windows table, 1258, that holds the name in neither normal form | [In Python](#in-python), section 2 |
| `한국어` | syllables that are made of letters: three characters, eight code points once taken apart | [Normalization](../../04_Python/normalization/README.md) |

## Other scripts: more bytes, other tables

| word | there to show | here |
|---|---|---|
| `Привет` | the Cyrillic table zoo — KOI8-R read as Windows-1251 gives `рТЙЧЕФ`, the reverse gives `оПХБЕР` — and KOI8-R's party trick: its letters were [laid out in Latin order ↗](https://en.wikipedia.org/wiki/KOI8-R) so that clearing the top bit of every byte leaves a readable, case-reversed transliteration, `pRIWET` | [Code pages](../../02_Characters/code_pages/README.md) |
| `Ελληνικά` | two bytes a letter, and a table of its own, Windows-1253 — the Japanese and Korean double-byte tables hold the plain capitals of `ΟΔΥΣΣΕΥΣ` but not an accented `ά` | [In Python](#in-python), section 2 |
| `日本語` ★ | three bytes a character, and two columns wide on a terminal | [The cast](../../CAST.md), [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| `文字化け` | the word *mojibake* itself — and its own UTF-8 read as Shift_JIS, `譁�蟄怜喧縺�`, which is the garbling Wikipedia's article shows | [Mojibake](../../03_Encodings/mojibake/README.md) |
| `नमस्ते` | six code points, and a grapheme cluster count of 3 or 4 depending on which Unicode version your tools were built for; and no legacy table at all — of every codec Python names, only the UTFs and GB18030 can write it | [The table has a version](../../02_Characters/the_table_has_a_version/README.md#the-rules-have-a-version-too) |

Right-to-left words are missing from this list on purpose. A Hebrew *shalom* and an Arabic *marhaba* turn up in every bidi tutorial, and bidi is a subject this library does not teach — the cast's note on [what is deliberately left out](../../CAST.md#what-is-deliberately-not-in-the-cast) gives the reason.

## Above U+FFFF, and one emoji made of five code points

| word | there to show | here |
|---|---|---|
| `😀` ★ | one code point: four UTF-8 bytes, two UTF-16 units | [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) |
| `💩` | the same shape, and the running example of Mathias Bynens' [*JavaScript has a Unicode problem* ↗](https://mathiasbynens.be/notes/javascript-unicode) | [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) |
| `𝄞` | a musical G clef, `D834 DD1E` in UTF-16 — the pair [Wikipedia's UTF-16 article ↗](https://en.wikipedia.org/wiki/UTF-16) uses to show both halves written into a string constant | [Writing a code point](../../02_Characters/writing_a_code_point/README.md) |
| the facepalm, `U+1F926 U+1F3FC U+200D U+2642 U+FE0F` | five code points, 17 bytes, 7 UTF-16 units, one emoji — [Henri Sivonen's ↗](https://hsivonen.fi/string-length/) answer to *how long is a string?* | [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) |
| the family ★ | the same lesson, which this library tells with three people and two joiners | [The cast](../../CAST.md) |

## Whole sentences

When a test needs every letter a language adds rather than one of them, it reaches for a pangram, and the collection everyone borrows from is Markus Kuhn's [quickbrown.txt ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/examples/quickbrown.txt). Section 5 of the program checks the ones worth knowing against the letters each language adds to ASCII, and finds one that does not do the job its reputation suggests: the German line, *Zwölf Boxkämpfer jagten Eva quer über den Sylter Deich*, has `ä`, `ö` and `ü` and no `ß`. Kuhn's file has no Czech line; `Příliš žluťoučký kůň úpěl ďábelské ódy`, the usual Czech one, has all fifteen.

## The word for mojibake

Every language that met the problem gave it a name. From [Wikipedia's article ↗](https://en.wikipedia.org/wiki/Mojibake):

| language | word | meaning |
|---|---|---|
| Japanese | 文字化け, *mojibake* | the word English borrowed — [Mojibake](../../03_Encodings/mojibake/README.md) takes it apart |
| Russian | кракозябры, *krakozyabry* | |
| Polish | *krzaczki* | little shrubs |
| Hungarian | *betűszemét* | letter garbage |
| Bulgarian | маймуница, *majmunica* | monkey's [alphabet] |
| Serbian | ђубре, *đubre* | trash |
| Chinese | 乱码, *luànmǎ* | |

## In Python

One program measures every word on the page. Its six sections follow the page's own order: the four rulers that need no table, which legacy tables can hold each word, the mojibake each one is known for, the characters above `U+FFFF`, the pangrams against their alphabets, and what the strip-the-accents recipe leaves behind.

<!-- output:typical_words_py -->
*Verified output of [`typical_words_py.py`](examples/typical_words_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE WORDS, AND FOUR RULERS THAT NEED NO TABLE
------------------------------------------------------------------------
   chars  NFD  UTF-8  UTF-16      word
   -- accented Latin
       4    5      5       4  *   café
       5    6      6       5      naïve
       6    8      8       6      résumé
      20   25     27      20      Iñtërnâtiônàlizætiøn
   -- Central Europe
       4    6      7       4  *   żółw
       4    6      7       4  *   Łódź
      17   25     26      17  *   zażółć gęślą jaźń
      22   31     31      22      Árvíztűrő tükörfúrógép
      38   53     53      38      Příliš žluťoučký kůň úpěl ďábelské ódy
   -- case and normalization
       6    6      7       6      Straße
       8    9      9       8      İstanbul
       8    8     16       8      ΟΔΥΣΣΕΥΣ
       8   10     10       8      Ångström
       6    8      8       6      Nguyễn
       3    8      9       3      한국어
   -- other scripts
       6    6     12       6      Привет
       8    9     16       8      Ελληνικά
       3    3      9       3  *   日本語
       4    4     12       4      文字化け
       6    6     18       6      नमस्ते
   -- above U+FFFF
       1    1      4       2  *   😀
       1    1      4       2      💩
       1    1      4       2      𝄞
       5    5     17       7      🤦🏼‍♂️
       5    5     18       8  *   👨‍👩‍👧

   'chars' counts code points as typed; 'NFD' counts them again with
   every accent taken off as a mark of its own; 'UTF-8' is bytes;
   'UTF-16' is the units Java, JavaScript and ABAP call characters.
   A star marks a member of this library's own cast, in CAST.md.

2. WHICH LEGACY TABLE CAN HOLD EACH WORD
------------------------------------------------------------------------
   8859-1   1252 8859-2   1250   1254   1253 KOI8-R   1251   SJIS EUC-KR   word
      yes    yes    yes    yes    yes      .      .      .      .      .   café
      yes    yes      .      .    yes      .      .      .      .      .   naïve
      yes    yes    yes    yes    yes      .      .      .      .      .   résumé
      yes    yes      .      .    yes      .      .      .      .      .   Iñtërnâtiônàlizætiøn
        .      .    yes    yes      .      .      .      .      .      .   żółw
        .      .    yes    yes      .      .      .      .      .      .   Łódź
        .      .    yes    yes      .      .      .      .      .      .   zażółć gęślą jaźń
        .      .    yes    yes      .      .      .      .      .      .   Árvíztűrő tükörfúrógép
        .      .    yes    yes      .      .      .      .      .      .   Příliš žluťoučký kůň úpěl ďábelské ódy
      yes    yes    yes    yes    yes      .      .      .      .    yes   Straße
        .      .      .      .    yes      .      .      .      .      .   İstanbul
        .      .      .      .      .    yes      .      .    yes    yes   ΟΔΥΣΣΕΥΣ
      yes    yes      .      .    yes      .      .      .      .      .   Ångström
        .      .      .      .      .      .      .      .      .      .   Nguyễn
        .      .      .      .      .      .      .      .      .    yes   한국어
        .      .      .      .      .      .    yes    yes    yes    yes   Привет
        .      .      .      .      .    yes      .      .      .      .   Ελληνικά
        .      .      .      .      .      .      .      .    yes    yes   日本語
        .      .      .      .      .      .      .      .    yes    yes   文字化け
        .      .      .      .      .      .      .      .      .      .   नमस्ते
        .      .      .      .      .      .      .      .      .      .   😀
        .      .      .      .      .      .      .      .      .      .   💩
        .      .      .      .      .      .      .      .      .      .   𝄞
        .      .      .      .      .      .      .      .      .      .   🤦🏼‍♂️
        .      .      .      .      .      .      .      .      .      .   👨‍👩‍👧

   7 of the words fit none of the ten:
      Nguyễn  नमस्ते  😀  💩  𝄞  🤦🏼‍♂️  👨‍👩‍👧

   Nor does a table built for Devanagari turn up anywhere else. Of every
   codec named in Python's alias table, these can write 'नमस्ते' at all:
      gb18030  utf_16  utf_16_be  utf_16_le  utf_32  utf_32_be  utf_32_le  utf_7  utf_8
   The UTFs, and GB18030 -- the Chinese national standard, which maps
   the whole of Unicode rather than one script.

   Vietnamese has a Windows table of its own, 1258, and it does not
   fill the gap so much as move it -- 'Nguyễn' fits in neither
   normal form:
      NFC      004E 0067 0075 0079 1EC5 006E            refuses U+1EC5
      NFD      004E 0067 0075 0079 0065 0302 0303 006E  refuses U+0302
      neither  004E 0067 0075 0079 00EA 0303 006E       4E 67 75 79 EA DE 6E
   1258 carries the five Vietnamese tone marks as combining characters
   and the vowel shapes as precomposed letters, so it wants the
   e-circumflex composed and the tilde written after it -- a spelling
   that no normalization form produces.

3. THE MOJIBAKE EACH ONE IS FAMOUS FOR
------------------------------------------------------------------------
   written as  read as     the word, and what the reader gets
   utf-8       cp1252      'café'         -> 'cafÃ©'
   latin-1     utf-8       'café'         -> 'caf�'
   utf-8       cp1252      'don’t'        -> 'donâ€™t'
   utf-8       cp1250      'żółw'         -> 'ĹĽĂłĹ‚w'
   cp1250      iso8859_2   'Łódź'         -> 'Łód\x9f'
   iso8859_2   cp1250      'Łódź'         -> 'ŁódĽ'
   iso8859_2   latin-1     'Árvíztűrő'    -> 'Árvíztûrõ'
   koi8_r      cp1251      'Привет'       -> 'рТЙЧЕФ'
   cp1251      koi8_r      'Привет'       -> 'оПХБЕР'
   utf-8       shift_jis   '文字化け'         -> '譁�蟄怜喧縺�'
   utf-8       cp1252      'café'         -> 'cafÃƒÂ©'   (misread twice)

   'Привет' in KOI8-R           F0 D2 C9 D7 C5 D4
   every top bit cleared        70 52 49 57 45 54   'pRIWET'
   Clear the eighth bit of every byte and KOI8-R text is still
   readable: Latin letters, with the case turned over.

4. ABOVE U+FFFF: ONE CHARACTER, TWO UTF-16 UNITS
------------------------------------------------------------------------
   U+1F600   UTF-8 F0 9F 98 80   UTF-16 D83D DE00   GRINNING FACE
   U+1F4A9   UTF-8 F0 9F 92 A9   UTF-16 D83D DCA9   PILE OF POO
   U+1D11E   UTF-8 F0 9D 84 9E   UTF-16 D834 DD1E   MUSICAL SYMBOL G CLEF

   the facepalm: 5 code points, 17 UTF-8 bytes, 7 UTF-16 units, one emoji to a reader
      U+1F926  FACE PALM
      U+1F3FC  EMOJI MODIFIER FITZPATRICK TYPE-3
      U+200D   ZERO WIDTH JOINER
      U+2642   MALE SIGN
      U+FE0F   VARIATION SELECTOR-16
   the family: 5 code points, 18 UTF-8 bytes, 8 UTF-16 units, one emoji to a reader
      U+1F468  MAN
      U+200D   ZERO WIDTH JOINER
      U+1F469  WOMAN
      U+200D   ZERO WIDTH JOINER
      U+1F467  GIRL

5. WHOLE SENTENCES: DOES THE PANGRAM COVER THE ALPHABET?
------------------------------------------------------------------------
   of the letters the language adds to ASCII (for Russian, of all 33)
   Polish      9 of 9   missing none   zażółć gęślą jaźń
   Polish      9 of 9   missing none   Pchnąć w tę łódź jeża lub ośm skrzyń fig
   Czech      15 of 15  missing none   Příliš žluťoučký kůň úpěl ďábelské ódy
   Hungarian   9 of 9   missing none   Árvíztűrő tükörfúrógép
   German      3 of 4   missing ß      Zwölf Boxkämpfer jagten Eva quer über den Sylter Deich
   Turkish     6 of 6   missing none   Pijamalı hasta, yağız şoföre çabucak güvendi.
   Russian    33 of 33  missing none   Съешь же ещё этих мягких французских булок да выпей чаю

6. STRIP THE MARKS: THE FOLK WAY TO ASCII
------------------------------------------------------------------------
   ASCII        cafe
   ASCII        naive
   ASCII        Nguyen
   ASCII        Prilis zlutoucky kun upel dabelske ody
   ASCII        Arvizturo tukorfurogep
   keeps ß      Straße
   keeps ł      zołw
   keeps Ł      Łodz
   keeps æ ø    Internationalizætiøn

   Decompose, drop the combining marks, keep the rest. It works on
   every letter whose accent Unicode writes as a separate mark, and
   on nothing else: ß, ł, æ and ø have no decomposition at all, so
   they come through untouched -- and so does every search, sort or
   username check built on this recipe.
```
<!-- /output -->

**Section 2 is why the classic words are the classic words.** `café` fits every Western table, so a tutorial can misread it without any table refusing it; `żółw` breaks Latin-1 and fits both Central European tables; `Łódź` is where those two disagree. And two rows found things the list was not built to find: Windows-1258 holds `Nguyễn` only in a spelling that no normalization form produces, and no table built for Devanagari is anywhere in Python's catalogue.

**Section 6 is the recipe most "remove the accents" functions are.** It works on exactly the letters whose accent Unicode writes as a separate mark, which is why every Czech and Hungarian letter comes out clean and `ß`, `ł`, `æ` and `ø` do not. [Sorting and collation](../../07_Real_Data/sorting_and_collation/README.md) shows what that costs a sort.

Grapheme clusters are the one count the program does not print. `नमस्ते` has three to a segmenter built for Unicode 15.1 or later and four to one built before, and both kinds were on the machine this page was written on — the measurement is in a dated fence on [The table has a version](../../02_Characters/the_table_has_a_version/README.md#the-rules-have-a-version-too), which is where a number that depends on the tool belongs.

## If you are coming from Python or ABAP

**Python.** Every table on this page is one argument to `encode` or `decode` — `latin_1`, `cp1250`, `iso8859_2`, `koi8_r`, `shift_jis` — and `errors="replace"` is what turned `文字化け` into a line with two `U+FFFD` in it. The strip-the-accents recipe is `unicodedata.normalize("NFD", s)` followed by dropping every character for which `unicodedata.combining()` is non-zero; that is all most such helpers are, and section 6 is the list of what they cannot do.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* These are the words that break SAP interfaces, for the same reasons. A `Łódź` in a vendor master is exactly the case where a file written in one Central European code page is read in the other, and `cl_abap_codepage` converts between code pages by SAP code-page number — a number to verify against the system that will run the job, never to copy from a document. ABAP strings count UTF-16 units, so the facepalm emoji is 7 long to `STRLEN( )`, the same answer Java and JavaScript give.

## Try it

1. Search your own test fixtures for `café`, `naïve`, `Straße` and `żółw`. Each hit tests one property; decide which from the tables above, and whether anything tests the properties no hit covers.
2. Take the last mojibake you met and match it against section 3. `Ã©`, `â€™`, `Ĺ‚` and `рТЙЧЕФ` each name the wrong table as well as the damage.
3. Run section 6's recipe over a list of names you own: `python3 -c "import sys, unicodedata as u; [print(l, end='') for l in sys.stdin if not ''.join(c for c in u.normalize('NFD', l) if not u.combining(c)).isascii()]" < names.txt`. Every line it prints is one that "remove the accents" cannot turn into ASCII.
4. Ask two tools on your own machine how many grapheme clusters `नमस्ते` has — the one-liner is on [The table has a version](../../02_Characters/the_table_has_a_version/README.md#try-it) — and see which side of Unicode 15.1 each of them is on.

## See also

- [The cast](../../CAST.md) — this library's own words, and the rule for adding one
- [The hard strings](../hard_strings/README.md) — the corpus to test with, one string per behaviour
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) — the five rulers behind section 1
- [The table has a version](../../02_Characters/the_table_has_a_version/README.md) — why no grapheme count is printed here
- [Code pages](../../02_Characters/code_pages/README.md) — the tables behind section 2
- [Mojibake](../../03_Encodings/mojibake/README.md) and [The mojibake round trip](../../07_Real_Data/mojibake_round_trip/README.md) — what section 3 is, and when it can be undone
- [Normalization](../../04_Python/normalization/README.md) — the forms behind sections 1 and 6
- [quickbrown.txt ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/examples/quickbrown.txt), [UTF-8-demo.txt ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-demo.txt) and [UTF-8-test.txt ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt) — Markus Kuhn's three files: pangrams, a page of many scripts, and malformed input for testing a decoder
- [Big List of Naughty Strings ↗](https://github.com/minimaxir/big-list-of-naughty-strings) — the pile [The hard strings](../hard_strings/README.md) was written as an answer to
- [Mojibake — Wikipedia ↗](https://en.wikipedia.org/wiki/Mojibake) — the examples by language, and the names in the table above
