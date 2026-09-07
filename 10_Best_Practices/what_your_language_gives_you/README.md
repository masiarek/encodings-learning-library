# "Handles Unicode" is four questions

**Level:** 301 · for anyone choosing a tool for a text job

**One line:** Whether a language is good at text splits into four capabilities that turn out to be independent — converting between encodings, deciding what to do with a byte it cannot explain, agreeing with a person about what one character is, and refusing to hold bytes that are not text — and no language has all four, which is why "does it support Unicode" has never been a yes-or-no question.

## The question, and the answer that looks obvious

*Which language has the most sophisticated, mature encodings and string processing? JavaScript, maybe?*

JavaScript is a reasonable guess. It is Unicode-aware in every modern way: `String.prototype.normalize`, Unicode property escapes in regular expressions (`\p{Script=Greek}` under the `u` flag, set operations under `v`), `Intl.Segmenter` for grapheme clusters, and `Intl.Collator` for locale-correct sorting — all of it backed by a full [ICU ↗](https://icu.unicode.org/) build.

And it is, measurably, one of the *worst* mainstream languages at encodings. Both things are true at once, and that is the whole subject of this page.

## The measurement

The [WHATWG Encoding Standard ↗](https://encoding.spec.whatwg.org/) is the list of encodings every browser implements. Its machine-readable form, [`encodings.json` ↗](https://encoding.spec.whatwg.org/encodings.json), names **40** encodings under **228** labels. Asking Node how many of the 40 it will decode, and how many it will encode:

```text
table encodings      : 40
TextDecoder accepts  : 37   refuses: ["ISO-8859-16","replacement","x-user-defined"]
TextEncoder produces : 1    distinct encodings it can emit: ["utf-8"]
```

Thirty-seven in. One out. It is not a gap in the implementation — the standard says so in one sentence: *"A `TextEncoder` object offers no label argument as it only supports UTF-8."* The preface gives the reason, which is a policy and not a limitation: new formats **must use the UTF-8 encoding exclusively**, and the legacy tables are there so that a browser can *read* the old web, not so anyone can write more of it.

So the platform is deliberately one-directional. You can read a Shift_JIS page in a browser. You cannot produce one.

That is a design decision worth admiring and worth knowing about, and it means a sentence like "JavaScript handles encodings well" is neither true nor false until you say which direction you meant.

## The four questions

| | The question | What it is really asking |
|---|---|---|
| **1** | **Can it convert?** | How many byte-to-character tables does it know, and does it know them in *both* directions? |
| **2** | **What does it do at a byte it cannot explain?** | Raise, replace, drop, or carry the byte through unharmed — and is the choice yours? |
| **3** | **What does it call one character?** | Bytes, code units, code points or grapheme clusters — [four honest answers](../../02_Characters/a_code_point_is_not_a_character/README.md), and the default decides what `length` means |
| **4** | **Can the type system stop you?** | Is "bytes that are not text" a state the language will let you construct at all? |

They look like one question and are not. JavaScript is excellent at 3 (`Intl.Segmenter`) and cannot do half of 1. Rust answers 4 the most strictly of any of them and answers 1 with *nothing at all*. Python is the best of them at 1 and 2 and gives you no help whatsoever on 3. A language's reputation usually comes from whichever of the four its community argues about most.

## Question 1 — can it convert, and both ways?

| | Encodings it can **read** | Encodings it can **write** | Where they live |
|---|---|---|---|
| **Python** | 117 codecs | the same 117 | `codecs`, in the standard library |
| **Perl** | 124 | the same 124 | `Encode`, in core |
| **Java** | the JDK's charset set | the same set | `java.nio.charset`, with the finest-grained error control of any of these |
| **JavaScript** | **37** | **1** | `TextDecoder` / `TextEncoder`, and the asymmetry is normative |
| **Rust** | **2** (UTF-8, UTF-16) | 2 | `std` ships no legacy table at all; [`encoding_rs` ↗](https://docs.rs/encoding_rs/) is the crate |
| **Swift** | Unicode, plus a short Foundation list | the same | `String.Encoding` |

Two rows deserve their explanation, because they look like failures and are not.

**Rust's `2` is a deliberate exclusion, not an omission.** A legacy encoding is a 256-entry table somebody wrote down; there is nothing to compute. Shipping the forty of them means shipping data, and Rust's standard library does not ship data it can avoid. The Rust program below makes that concrete: `b as char` — the only integer-to-char cast the language permits — is a complete and correct **Latin-1 decoder**, because Latin-1's characters *are* code points 0–255 by construction. Try the same trick on windows-1250 and it gets 177 of 256 bytes right, which is worse than useless. And Latin-1 is not the easy member of an easy family: of the 28 single-byte tables in the WHATWG standard, **not one** is the identity map, and Latin-1 itself is not among them — the standard hands its label to windows-1252 instead ([why that matters](../../07_Real_Data/windows_1252_vs_latin1/README.md)).

**JavaScript's `1` is a policy.** See above. It is the only row in the table where the two columns differ.

## Question 2 — what happens at a byte it cannot explain?

This is the axis with the clearest winner, and the winning feature is one most people have never used.

Python's `errors=` argument takes eight named policies, and seven of them are decisions to lose information. The eighth is [PEP 383 ↗](https://peps.python.org/pep-0383/)'s `surrogateescape`, which maps an undecodable byte to a **lone surrogate** — a code point that can never occur in real text — and maps it back on the way out, so the byte survives a decode/encode round trip intact. That is how a filename which is not valid UTF-8 can still be opened. Neither Java's `CharsetDecoder` nor JavaScript's `TextDecoder` offers anything like it — their choices are report, replace or ignore, and all three lose the byte. Go does not need one: a Go string is a byte slice with a UTF-8 *convention* rather than a guarantee, so the bytes were never in danger.

The nice part is that the web standard invented the same trick independently. `x-user-defined` — one of the three names Python's registry does not know — maps bytes `0x80–0xFF` to `0xF780 + byte − 0x80`, a slice of the **private use area**. Different reserved range, identical idea: to carry a byte you cannot interpret through a string type, send it somewhere that means nothing else. Section 4 of the Python program below puts the two side by side.

## Question 3 — what does it call one character?

One string — the four characters `c a f e` followed by U+0301 COMBINING ACUTE ACCENT, which renders as `café` and is the spelling you cannot type ([why](../../04_Python/normalization/README.md)):

| | `length` returns | counting | grapheme count available? |
|---|---|---|---|
| **Swift** | **4** | extended grapheme clusters | it is the default |
| **Python** | 5 | code points | no — nothing in the standard library |
| **Rust** | 5 (`.chars().count()`) | code points | no — `unicode-segmentation` is a crate |
| **Perl** | 5 | code points | yes — `/\X/` in the regex engine |
| **JavaScript** | 5 | UTF-16 code units | yes — `Intl.Segmenter` |
| **ABAP** | 5 | [UCS-2 code units](../../09_History/why_utf16_stayed/README.md) | no |

Swift is alone here, and it is a genuine design choice rather than a library: `Character` *is* an extended grapheme cluster, `==` compares under canonical equivalence, and the other views (`unicodeScalars`, `utf8`, `utf16`) are opt-in. `"caf" + "e\u{301}"` has a `count` of 4 and compares equal to `"café"` precomposed.

The bottom two rows agree with the middle ones **on this string and not in general**, which is the trap in reading a table like this. JavaScript's `.length` and ABAP's `strlen( )` count [UTF-16 code units](../../03_Encodings/utf16_and_surrogates/README.md), and a code unit is a code point only inside the BMP — every character in `café` qualifies. Add one that does not and they part: `"a😀".length` is **3** where `[..."a😀"].length` is **2**. That is the legacy JavaScript shares with Java and ABAP, each for [its own reason](../../09_History/why_utf16_stayed/README.md), and it means a length test that passes on European text can still be wrong.

## Question 4 — can the type system stop you?

Rust wins this one by refusing: `String` and `&str` are *guaranteed* valid UTF-8, `str::from_utf8` returns a `Result`, and in safe code there is no way to construct a string holding bytes that are not text. Python answers the opposite way on purpose — `str` under `surrogateescape` will hold them, so the filename survives — and both answers are right, because they are answers to different questions.

Everyone else is somewhere between: Java, JavaScript and ABAP all have string types that will happily hold an unpaired surrogate, which is a sequence no encoder can write.

## Nobody wins all four

Unlike everything above it, this table is a **judgement** rather than a measurement — the stars are mine, and the row you disagree with is probably the one you know best:

| | 1 · convert | 2 · error policy | 3 · one character | 4 · type system |
|---|---|---|---|---|
| **Python** | ★★★ | ★★★ | ✗ (code points) | ★★ (`str`/`bytes`) |
| **Perl** | ★★★ | ★★ | ★★ (`\X`) | ✗ |
| **Java** | ★★★ | ★★★ | ★ (ICU on the side) | ✗ (UTF-16) |
| **JavaScript** | ✗ (read-only) | ★ | ★★ (`Intl.Segmenter`) | ✗ (UTF-16) |
| **Rust** | ✗ (crate) | ★★ | ✗ (crate) | ★★★ |
| **Swift** | ★ | ★ | ★★★ | ★★ |

And the honest bottom line under the whole table: **the most sophisticated text engine in existence is not a language at all.** It is [ICU ↗](https://icu.unicode.org/) — collation, break iteration, normalization, transliteration, formatting, spoof checking — and Java's `java.text`, Node's `Intl`, .NET 5 and later, and Swift's Foundation are all ICU wearing a hat. So the real question is never "which language is best at Unicode" but "which parts has my language chosen to own, and which has it left to a library" — and Rust's `std` is the one that says so out loud, which is why the crates are so good.

If you have to pick one for a job that is *mostly encodings*: **Python**, and it is not close on ergonomics. `data.decode('cp1250', 'surrogateescape')` is the whole program.

## In Python

<!-- output:what_your_language_gives_you_py -->
*Verified output of [`what_your_language_gives_you_py.py`](examples/what_your_language_gives_you_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. QUESTION ONE: CAN IT CONVERT? AND CAN IT CONVERT BOTH WAYS?
------------------------------------------------------------------------
   encodings the standard names                     40
   of the ones this registry resolves, how many it
       will only READ, never write                  0
       will only WRITE, never read                  0

   Zero and zero, and that is the answer to question one. Python's
   codecs come in pairs; there is no table it will take in and not
   give back. A standard library that reads a table it cannot write
   is a real design and not an oversight -- see the page.

   How many of the forty it resolves at all is a different question,
   and not one an answer key may hold: it is a property of the alias
   table, which has a version. Spot checks, on names that resolve
   the same way on CPython 3.11 through 3.14:
       UTF-8          -> Python calls it utf-8        both ways: True
       windows-1250   -> Python calls it cp1250       both ways: True
       ISO-8859-2     -> Python calls it iso8859-2    both ways: True
       KOI8-R         -> Python calls it koi8-r       both ways: True
       Shift_JIS      -> Python calls it shift_jis    both ways: True
       Big5           -> Python calls it big5         both ways: True
       EUC-KR         -> Python calls it euc_kr       both ways: True

2. THE STAKE, IN ONE CHARACTER
------------------------------------------------------------------------
   ż  U+017C  LATIN SMALL LETTER Z WITH DOT ABOVE

   encode to utf-8        c5 bc     and back: 'ż'
   encode to cp1250       bf        and back: 'ż'
   encode to iso8859-2    bf        and back: 'ż'
   encode to latin-1      UnicodeEncodeError  -- no byte here means it

   One byte in windows-1250, one in ISO-8859-2, two in UTF-8, and no
   byte at all in Latin-1. A language that can only WRITE UTF-8 can
   still read all four -- and cannot send a file to a system that
   expects the first.

3. QUESTION TWO: WHAT HAPPENS AT A BYTE IT CANNOT EXPLAIN?
------------------------------------------------------------------------
   the bytes 63 61 66 e9 2e 74 78 74, decoded as UTF-8 under each policy:

   replace            'caf�.txt'             round-trips: False
   ignore             'caf.txt'              round-trips: False
   backslashreplace   'caf\\xe9.txt'         round-trips: False
   surrogateescape    'caf\udce9.txt'        round-trips: True
   strict             UnicodeDecodeError     round-trips: n/a

   registered under these names:
      strict              replace             ignore
      backslashreplace    xmlcharrefreplace   namereplace
      surrogateescape     surrogatepass

   Only `surrogateescape` gives the byte back, and it is worth seeing
   how: 0xE9 becomes U+DCE9, a lone surrogate -- a code point that can
   never occur in real text, holding a byte until something encodes it
   again. PEP 383 is the reason a filename that is not valid UTF-8 can
   still be opened.

4. THE SAME TRICK, TWICE, INVENTED SEPARATELY
------------------------------------------------------------------------
   a byte that is not valid UTF-8   0xE9

   Python, surrogateescape    0xDC00 + byte          U+DCE9  lone surrogate
   the web, x-user-defined    0xF780 + byte - 0x80   U+F7E9  private use

   Two standards, no shared authors, one idea: to carry a byte you
   cannot interpret through a string type, map it into a range of
   code points that means nothing else, and map it back on the way
   out. Python reserved lone surrogates for it; the browsers reserved
   a slice of the private use area. So `x-user-defined` is not really
   a character table at all: it is this escape hatch, wearing an
   encoding's name so that it can be asked for like one.

5. QUESTION THREE: WHAT DOES IT CALL ONE CHARACTER?
------------------------------------------------------------------------
   the string renders as café, and is U+0063 U+0061 U+0066 U+0065 U+0301

   UTF-8 bytes                              6
   len(), which counts code points          5
   what a reader counts                     4

   Python answers one of those three, and it is not the one a person
   means. Nothing in the standard library returns the third; neither
   does Rust's. Swift's `count` does, because Swift chose a different
   default unit -- which is the whole of question three, and the page
   has the table.
```
<!-- /output -->

## In Rust

<!-- output:what_your_language_gives_you_rs -->
*Verified output of [`what_your_language_gives_you_rs.rs`](examples/what_your_language_gives_you_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. QUESTION ONE: WHAT ENCODINGS DOES `std` KNOW?
------------------------------------------------------------------------
   the encodings `std` can decode, in full:
       UTF-8    str::from_utf8 / _mut, String::from_utf8, _lossy
       UTF-16   String::from_utf16, _lossy, and since rustc 1.98
                the explicit-endian from_utf16le / from_utf16be

   Two encodings, and both of them are Unicode. There is no third,
   and no registry to ask for one: no `from_latin1`, no lookup by
   name, no `windows-1250` anywhere in the standard library. Where
   Python answered question one with thirty-odd tables in both
   directions, Rust answers it with none, and points at a crate.

2. LATIN-1 LOOKS LIKE AN EXCEPTION, AND IS ARITHMETIC
------------------------------------------------------------------------
   `b as char` is the only integer-to-char cast Rust permits,
   and for all 256 byte values it agrees with Latin-1: true
       0x41 -> 'A'      0xE9 -> 'é'

   That one-liner is a complete, correct Latin-1 decoder, and it is
   not a feature anybody implemented. Latin-1's 256 characters ARE
   code points 0 to 255, by construction, so the decode is the
   identity function and a cast is enough.

3. windows-1250 IS NOT ARITHMETIC, AND THAT IS THE GENERAL CASE
------------------------------------------------------------------------
   of the 256 byte values, how many `b as char` gets right
   for windows-1250:                     177
   bytes the table maps somewhere else:  74
   bytes the table leaves undefined:     5

       byte 0xBF   `as char` says '¿'   U+00BF
       byte 0xBF   the table says 'ż'   U+017C

   The lower half is ASCII and free. The upper half is a decision
   somebody wrote down decades ago, and there is nothing in it to
   compute -- which is what a legacy encoding mostly IS.

   Latin-1 is not the easy case in a family of easy cases. It is the
   only case. Of the twenty-eight single-byte tables in the browser
   standard, NONE is the identity map, and Latin-1 itself is not
   among them -- the standard gives its name to windows-1252 instead.
   The closest is ISO-8859-15, which agrees on 120 of the 128 high
   bytes and puts a euro sign in one of the other eight. Shipping
   these is shipping data, which is why they live in a crate.

4. QUESTION FOUR: CAN THE TYPE SYSTEM STOP YOU?
------------------------------------------------------------------------
   str::from_utf8 on the same caf-0xE9-.txt bytes: Err, valid up to byte 3
   String::from_utf8_lossy:                        "caf�.txt"
   the 0xE9 is gone, replaced:                     true
   the only signal that anything changed:          Cow::Owned

   Rust's answer here is different in kind, and it is a refusal: in
   safe Rust there is no way to put those bytes in a `String` at all.
   Python's `str` will hold them under `surrogateescape`, which is a
   different and equally deliberate answer -- one language made the
   invalid state unrepresentable, the other made it representable on
   purpose so that a filename survives.

   Both are right. They are answers to different questions, which is
   the whole point of asking four.
```
<!-- /output -->

## What was measured, and where

Only the Python and Rust programs above are answer keys — CI runs them on Ubuntu and macOS on every push, so their numbers cannot rot silently. **Everything in the comparison tables was measured by hand on one machine**, and is dated for that reason:

| | version | measured |
|---|---|---|
| machine | macOS 26.6.2, x86-64 | 2026-09-07 |
| Node | v20.20.2, ICU 78.3, Unicode 17.0 | 37 decodable / 1 encodable, of the standard's 40; `("caf"+"e\u{301}").length` → 5 and `Intl.Segmenter` → 4; `"a😀".length` → 3 against 2 code points |
| Perl | v5.42.0 | `Encode->encodings(":all")` → 124; `\X` → 4; `Unicode::Collate` sorts `Łódź` before `Zebra` where `sort` gets it backwards |
| Go | go1.25.5 | `string([]byte{...0xE9...})` keeps the byte: `len` 8, `utf8.ValidString` false, `s[3] == 0xE9` true |
| Swift | 6.3.3 | `("caf" + "e\u{301}").count` → 4, `unicodeScalars` → 5, `utf8` → 6 |
| Python | 3.14.7 | see the recorded key above; 122 codec modules resolving to 117 distinct codecs, under 341 aliases |
| rustc | 1.98.0 | see the recorded key above |

**Java is the one row in the tables with no measurement behind it at all** — there is no JDK on this machine, and the ABAP row carries the library's usual caveat that CI cannot run it — so its column is read from the documentation and should be treated as the weakest claim on the page. What is worth checking if you have one to hand: `CharsetDecoder` lets you set `onMalformedInput` and `onUnmappableCharacter` *independently* to REPORT, REPLACE or IGNORE, which is finer control than Python's single `errors=` string, and is the reason Java is in the top row of question 2.

One thing the Python program deliberately does **not** print is *how many* of the standard's 40 names its registry resolves, and the reason is a small find: it is **37 on CPython 3.14 and 35 on 3.11 through 3.13**, because 3.14 added six aliases (`874`, `cseuckr`, `iso_8859_8_e`, `iso_8859_8_i`, `ms874`, `windows_874`) and removed none. Not one codec changed — only the spellings the registry answers to. So [the table has a version](../../02_Characters/the_table_has_a_version/README.md) is true of the *encoding registry* as well as of the Unicode data, and a count like that cannot be an answer key. What the program prints instead is the invariant: of the names it does resolve, the number it will read but not write is zero, and so is the number it will write but not read.

## If you are coming from Python or ABAP

**Python.** You are already on the best row of question 1 and question 2, and the two things to take from this page are the ones Python does *not* do. It has no grapheme segmentation and no locale collation in the standard library — `sorted()` is code point order, which puts `Łódź` after `Zebra` and is wrong in every language that uses those letters ([sorting and collation](../../07_Real_Data/sorting_and_collation/README.md)) — so if you need either, you are installing `regex` or `PyICU`, and that is normal rather than a failure. The other is `errors=`: eight policies is a lot of rope, and the only one that loses nothing is `surrogateescape` ([encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md)).

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* ABAP answers question 1 well and question 3 badly, which is the exact opposite shape to JavaScript. Conversion goes both ways through `cl_abap_conv_*` and `cl_abap_codepage=>convert_to` / `convert_from`, addressed by SAP code page number rather than IANA name — and any code page number you find written down is something to verify against the system that will run the job, never to quote from a document ([SAP code pages](../../07_Real_Data/sap_code_pages/README.md)). Question 4 will feel familiar: `string` and `xstring` are the same boundary Python draws between `str` and `bytes`, and the same discipline applies — convert at the interface, keep text in the middle. Question 3 is where ABAP is furthest from a modern answer, and for a reason worth knowing rather than complaining about: the language is [UCS-2](../../09_History/why_utf16_stayed/README.md), so `strlen( )` over an emoji returns `2` because the surrogate pair was never assembled into one character, and `charlen( )` is the function that sees it.

## Try it

```bash
cd 10_Best_Practices/what_your_language_gives_you/examples
python3 what_your_language_gives_you_py.py
rustc --edition 2024 what_your_language_gives_you_rs.rs -o /tmp/wylgy && /tmp/wylgy
```

And the measurement that started the page, if you have Node:

```bash
curl -s https://encoding.spec.whatwg.org/encodings.json -o /tmp/encodings.json
node -e 'const t=require("/tmp/encodings.json").flatMap(g=>g.encodings.map(e=>e.name));
let d=0; for(const n of t){try{new TextDecoder(n);d++}catch(e){}}
console.log("of",t.length,"-> decode",d,"| encode",new Set(t.map(n=>new TextEncoder(n).encoding)).size)'
```

Without the machine: a partner sends a nightly file that must be windows-1250, and the service that will produce it is written in TypeScript running on Node. Say what has to change, and which of the four questions on this page you would have asked *before* the language was chosen rather than after.

## See also

- [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md) — the two operations this page counts, and why a platform can implement one of them
- [UTF-8 everywhere](../utf8_everywhere/README.md) — the nine rules that are true whichever of these languages you are in
- [Python text in practice](../python_text_in_practice/README.md) and [Rust strings in practice](../rust_strings_in_practice/README.md) — the same two languages, one at a time and in more depth
- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md) — question 3 on its own page, where the four lengths get counted properly
- [`from_utf8` and lossy](../../05_Rust/from_utf8_and_lossy/README.md) — question 4 in full, including what `_lossy` throws away silently
- [The table has a version](../../02_Characters/the_table_has_a_version/README.md) — why the count of resolvable codec names could not go in the answer key
- [Why UTF-16 stayed](../../09_History/why_utf16_stayed/README.md) — the shared reason JavaScript, Java and ABAP all give a surprising answer to question 3
- [The encoding man pages nobody opens](../../13_Documentation/the_encoding_man_pages/README.md) — asking a registry for names, which is the same move section 1 of the Python program makes
