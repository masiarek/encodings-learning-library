# Resources

**Level:** reference · the outside reading

Every link here was fetched and checked on **2026-09-05** (`GET`, following redirects; YouTube links through the oEmbed endpoint, which refuses a wrong video id). A link is listed because it teaches something a page here does not, or teaches it better; each entry says which. Anything advocacy-shaped says so.

## The one answer everybody links

**[What is the difference between UTF-8 and Unicode? ↗](https://stackoverflow.com/questions/643694/what-is-the-difference-between-utf-8-and-unicode)** — Stack Overflow, 2009, 788 votes on the question and 21 answers. Worth reading, and worth reading *three* answers of, because they answer three different questions:

- The **accepted answer** (679 votes) is the history: ASCII's 7 bits, the eighth bit that every language filled differently (the ISO-8859 family), why one byte could never hold more than one language, and then Unicode as *one number per character* with UTF-8, UTF-16 and UTF-32 as three ways of writing that number down. It is [02_Characters](02_Characters/README.md) in six paragraphs.
- The **second answer** (531 votes) is the one to do with a pencil: it takes one Chinese character, `汉` at U+6C49, writes its 16 bits, and pushes them through the UTF-8 template table (`0xxxxxxx` / `110xxxxx 10xxxxxx` / `1110xxxx 10xxxxxx 10xxxxxx` / `11110xxx …`) to get `E6 B1 89`. That is exactly the exercise on [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md), and it is the single most useful thing in the thread.
- **Jon Skeet's answer** (254 votes) is the terminology: *Unicode* is a coded character set (characters ↔ integers), *UTF-8* is an encoding (bytes ↔ characters), and when a platform says "Unicode" as the name of an encoding — .NET's `Encoding.Unicode`, Java, and SAP's internal form — it means UTF-16, surrogate pairs and all. That confusion is the reason [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) exists.

One thing the thread does *not* settle, because nobody asked: that a code point is still not what a person calls a character. [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) picks up there.

## The two articles every programmer is told to read

| | What it gives you | Note |
|---|---|---|
| [The Absolute Minimum Every Software Developer Absolutely, Positively Must Know About Unicode and Character Sets ↗](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/) — Joel Spolsky, 2003 | The essay that named the problem: *there is no such thing as plain text*; a string without an encoding is meaningless. Also the origin of "mojibake" as an English word. | Twenty years old; the mechanics are right, the Windows-centric advice is dated. |
| [What Every Programmer Absolutely, Positively Needs to Know About Encodings and Character Sets to Work with Text ↗](https://kunststube.net/encoding/) — David C. Zentgraf | Joel's article rewritten with the bytes shown, and with PHP as the cautionary example. The clearest single explanation of *decoding under the wrong table*. | Best read after chapter 1 here, so the hex means something. |

## Deeper articles, in a sensible order

| | What it gives you |
|---|---|
| [A Programmer's Introduction to Unicode ↗](https://www.reedbeta.com/blog/programmers-intro-to-unicode/) — Nathan Reed | The best modern survey: planes, encodings, combining marks, grapheme clusters, normalization, with a diagram of which parts of the code space are actually used. Read after chapter 3. |
| [The Absolute Minimum … in 2023 ↗](https://tonsky.me/blog/unicode/) — Nikita Prokopov | Joel's article redone for today: why `len()` is a lie in every language, graphemes, and a table of what each language's string length actually counts. Opinionated and right. |
| [It's Not Wrong that "🤦🏼‍♂️".length == 7 ↗](https://hsivonen.fi/string-length/) — Henri Sivonen | One emoji, and every honest answer to "how long is it": 17 UTF-8 bytes, 7 UTF-16 units, 5 code points, 1 grapheme. The definitive version of the "five answers" table. |
| [Let's Stop Ascribing Meaning to Code Points ↗](https://manishearth.github.io/blog/2017/01/14/stop-ascribing-meaning-to-unicode-code-points/) — Manish Goregaokar | Why Rust gives you `chars()` and refuses to call them characters. From one of Rust's Unicode maintainers. |
| [Unicode is harder than you think ↗](https://mcilloni.ovh/2023/07/23/unicode-is-hard/) — Marco Cilloni | A tour of the traps with C, C++ and Rust code; good on `wchar_t` and why it was a mistake. |
| [Pragmatic Unicode ↗](https://nedbatchelder.com/text/unipain.html) — Ned Batchelder, PyCon 2012 | The Python one: the *unicode sandwich* (decode at the edges, `str` inside), and five facts of life. Talk video linked from the page. |
| [Dive Into Python 3, chapter 4: Strings ↗](https://diveintopython3.net/strings.html) — Mark Pilgrim | Still the best gentle Python chapter on `str` vs `bytes`, with the "everything is bytes" opening this library shares. |
| [UTF-8 history ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/utf-8-history.txt) — Rob Pike | The email from 1992 in which Ken Thompson's UTF-8 design is written up over dinner. Short, and it shows the *lead byte announces the length* idea being invented. |
| [Hello World, or Καλημέρα κόσμε, or こんにちは 世界 ↗](https://doc.cat-v.org/plan_9/4th_edition/papers/utf) — Pike & Thompson | The Plan 9 paper that first shipped UTF-8. Section 2 is the encoding; the rest is what changed in a whole OS when text stopped being bytes. |
| [UTF-8 and Unicode FAQ for Unix/Linux ↗](https://www.cl.cam.ac.uk/~mgk25/unicode.html) — Markus Kuhn | Dated, encyclopaedic, and still the reference for *locale*, `LC_CTYPE`, and how a terminal decides what to draw. Backs [06_Terminal](06_Terminal/README.md). |
| [UTF-8 Everywhere ↗](https://utf8everywhere.org/) | A manifesto: use UTF-8 for storage and interchange, never UTF-16. **Advocacy** — persuasive, and the argument against `wchar_t` is correct, but read it as a position. |

## The standards, when you need the actual rule

| | Use it for |
|---|---|
| [WHATWG Encoding Standard ↗](https://encoding.spec.whatwg.org/) | The set of encodings every browser actually implements — and a **closed** one: "User agents must not support any other encodings". A table of every encoding and every label a document may claim, which is where the web-only facts come from: `latin1`, `iso-8859-1` and even `ascii` are all synonyms for **windows-1252**, so byte `0x80` decodes as `€` under all three. The source for [Code pages](02_Characters/code_pages/README.md), [Windows-1252 vs Latin-1](07_Real_Data/windows_1252_vs_latin1/README.md) and [`file` guesses](06_Terminal/file_guesses/README.md). |
| [RFC 3629: UTF-8 ↗](https://www.rfc-editor.org/rfc/rfc3629) | Six pages. The byte templates, the overlong prohibition, the surrogate prohibition. The only spec in this list short enough to read whole. |
| [The Unicode Standard, chapter 2: General Structure ↗](https://www.unicode.org/versions/latest/core-spec/chapter-2/) | Code points vs code units vs encoding forms, stated by the people who defined them. Section 2.5 is the diagram. |
| [Unicode FAQ: UTF-8, UTF-16, UTF-32 & BOM ↗](https://www.unicode.org/faq/utf_bom.html) | Every BOM question, answered by the consortium. |
| [Unicode code charts ↗](https://www.unicode.org/charts/) | The PDFs: every block, every glyph, every number. |
| [Wikipedia: UTF-8 ↗](https://en.wikipedia.org/wiki/UTF-8) · [Mojibake ↗](https://en.wikipedia.org/wiki/Mojibake) · [Windows-1252 ↗](https://en.wikipedia.org/wiki/Windows-1252) · [Byte order mark ↗](https://en.wikipedia.org/wiki/Byte_order_mark) · [Baudot code ↗](https://en.wikipedia.org/wiki/Baudot_code) · [ISO/IEC 2022 ↗](https://en.wikipedia.org/wiki/ISO/IEC_2022) · [Variable-length quantity ↗](https://en.wikipedia.org/wiki/Variable-length_quantity) · [Base64 ↗](https://en.wikipedia.org/wiki/Base64) | The tables. Wikipedia's UTF-8 page has the template table and the history of how the 6-byte form was cut to 4; the 1252 page has the 32-byte difference; Baudot and 2022 are the ancestors of the Tribit project's CAPS and ESC. |
| [Microsoft: Code pages ↗](https://learn.microsoft.com/en-us/windows/win32/intl/code-pages) | Windows' numbering (1252, 1250, 65001 = UTF-8). SAP's numbering is different and is on [SAP code pages](07_Real_Data/sap_code_pages/README.md). |
| [W3C: Character encodings for beginners ↗](https://www.w3.org/International/questions/qa-what-is-encoding) | The gentlest official page; the "what is an encoding" many tutorials paraphrase. |

## When you want to see one implemented

Not reading for now, and not a tutorial — the answer to *"how hard is all of this, really?"*, for after chapter 3 and for the [Tribit project](08_Build_Your_Own/tribit/README.md).

[encoding_rs: a Web-Compatible Character Encoding Library in Rust ↗](https://hsivonen.fi/encoding_rs/) — Henri Sivonen, 2018-12-03, twenty-one thousand words on implementing the whole Encoding Standard above, in Rust, for Firefox. It has two halves and only the first is for a learner. Everything through *The API Design* is about the decisions the Tribit exercises walk straight into: what a decoder returns when the output buffer fills in the middle of a character, why the *caller* allocates the buffer, why "the input has ended" has to be an explicit flag rather than an empty slice, and what a BOM does to a decoder that has already started. The second half — SIMD, lookup-table compression, benchmarks — is for people optimising one, and can be skipped without loss.

Three things worth taking from it even if you read no further:

- **Age is not safety.** uconv, the library it replaced, was written in 1999 and had a buffer overrun found in it in 2016, in code added in 2001.
- **The bugs were in the boring part.** The memory-safety problems clustered in the *legacy CJK* decoders — the encodings nobody thinks about, not UTF-8.
- **Legacy encodings are not history.** Sivonen's own bank served him ISO-8859-15, and Japanese news sites still published new articles daily in Shift_JIS. That is the same argument as [07_Real_Data](07_Real_Data/README.md), made about the Web instead of about SAP.

Dated in one place, and usefully so: it puts the Web at "over 90%" UTF-8 while questioning W3Techs' method for counting ISO-8859-1 apart from windows-1252 — a distinction the Encoding Standard says does not exist. W3Techs now says 99.0% (September 2026), so the *remaining* 1% is the whole reason that library is as large as it is. The crate is [`encoding_rs` on docs.rs ↗](https://docs.rs/encoding_rs/latest/encoding_rs/); it cannot appear in an example here, since Rust examples in this library are bare `rustc` with no crates.

## Language documentation

| Python | Rust |
|---|---|
| [Unicode HOWTO ↗](https://docs.python.org/3/howto/unicode.html) — the official essay; read the *Reading and Writing Unicode Data* section before [Opening a file](04_Python/opening_a_file/README.md) | [The Book, 8.2: Storing UTF-8 Encoded Text with Strings ↗](https://doc.rust-lang.org/book/ch08-02-strings.html) — why `s[0]` does not compile, in the language's own words |
| [`codecs` — Standard Encodings ↗](https://docs.python.org/3/library/codecs.html) — the table of every codec name and alias (`latin_1`, `cp1252`, `utf_8_sig`, `utf_16_le`) | [`char` ↗](https://doc.rust-lang.org/std/primitive.char.html) — *Unicode scalar value*, four bytes, and the `is_*` / `len_utf8` methods |
| [`unicodedata` ↗](https://docs.python.org/3/library/unicodedata.html) — `name()`, `category()`, `normalize()` | [`str` ↗](https://doc.rust-lang.org/std/primitive.str.html) · [`String` ↗](https://doc.rust-lang.org/std/string/struct.String.html) — `from_utf8`, `from_utf8_lossy`, `as_bytes`, `is_char_boundary` |
| [Fluent Python, 2nd ed. — example code ↗](https://github.com/fluentpython/example-code-2e) — the `04-text-byte` folder is the book's Unicode chapter, runnable | [`unicode-segmentation` ↗](https://docs.rs/unicode-segmentation/latest/unicode_segmentation/) — the grapheme-cluster crate std deliberately lacks |
| | [`core::str::validations` ↗](https://github.com/rust-lang/rust/blob/master/library/core/src/str/validations.rs) — the actual UTF-8 validator behind `from_utf8`, 300 lines, readable |
| [ABAP keyword documentation ↗](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm) — search *code page*, *xstring*, `cl_abap_codepage`; the reference for every ABAP claim on the [07_Real_Data](07_Real_Data/README.md) pages | |

## Books

None of these is required. Listed in the order they would help someone at the start of this library.

- **Charles Petzold, *Code: The Hidden Language of Computer Hardware and Software*, 2nd ed. (2022).** Chapters on Morse, Braille, bits, bytes and ASCII — the [01_Bits_and_Bytes](01_Bits_and_Bytes/README.md) chapter here, told slowly and beautifully. The companion site [codehiddenlanguage.com ↗](https://www.codehiddenlanguage.com/) has the interactive circuits.
- **Luciano Ramalho, *Fluent Python*, 2nd ed. (2022), chapter 4 "Unicode Text Versus Bytes".** The best Python chapter on the subject: `str`/`bytes`, codecs, `errors=`, BOM, normalization, sorting, and dual-mode APIs. The code is linked above.
- **Jim Blandy, Jason Orendorff & Leonora Tindall, *Programming Rust*, 2nd ed. (2021), chapter 17 "Strings and Text".** `char`, `String`, `&str`, formatting, and a proper section on Unicode — the Rust companion to Ramalho's chapter.
- **Jukka Korpela, *Unicode Explained* (2006).** The thorough one: characters vs glyphs, the properties, the encodings, with more history than you will use. Old, but Unicode's foundations have not moved.
- **Richard Gillam, *Unicode Demystified* (2002).** For when you want to know how normalization and bidi actually work. Reference, not reading.

## Videos

| | Minutes | Why |
|---|---|---|
| [Characters, Symbols and the Unicode Miracle ↗](https://www.youtube.com/watch?v=MijmeoH9LT4) — Tom Scott, Computerphile | 10 | UTF-8's design explained on paper in ten minutes, including *why* the continuation bytes start with `10`. Watch before [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md). |
| [Unicode, in friendly terms ↗](https://www.youtube.com/watch?v=ut74oHojxqo) — Studying With Alex | 20 | ASCII → code points → encodings, at exactly the pace of chapters 2 and 3 here. |
| [Plain Text ↗](https://www.youtube.com/watch?v=4mRxIgu9R70) — Dylan Beattie, GOTO 2023 | 60 | The history from telegraphs to emoji as a talk; the best hour on the subject, and funny. Baudot's shift codes — the Tribit project's CAPS — are in the first fifteen minutes. |
| Pragmatic Unicode — Ned Batchelder, PyCon 2012 | 35 | Linked from [his page ↗](https://nedbatchelder.com/text/unipain.html) above; the Python talk. |

## Tools for looking a character up

| | Does |
|---|---|
| [Unicode code converter ↗](https://r12a.github.io/app-conversion/) — Richard Ishida, W3C | Paste anything; see it as code points, UTF-8, UTF-16, escapes in six languages, at once. The tool this library's viewer exercise imitates. |
| [Compart Unicode ↗](https://www.compart.com/en/unicode/) | One page per character with every encoding, block, and property. |
| [FileFormat.info ↗](https://www.fileformat.info/info/unicode/char/e9/index.htm) | The same, older, and the page linked from that Stack Overflow answer. That link is `é`. |
| [Awesome Unicode ↗](https://github.com/jagracey/Awesome-Unicode) | A curated list of the strange corners: zero-width characters, homoglyphs, the emoji that break things. |

On your own machine: `man ascii`, `xxd`, `od`, `iconv -l`, `python3 -c 'import unicodedata; print(unicodedata.name("é"))'`.

## Katas — write the real thing

Once the [Tribit project](08_Build_Your_Own/tribit/README.md) is done, the real encoders are the next step, and they are shorter.

| | The exercise |
|---|---|
| [Rosetta Code: UTF-8 encode and decode ↗](https://rosettacode.org/wiki/UTF-8_encode_and_decode) | Encode a code point to UTF-8 bytes and back, with the four-row test table. Solutions in ~60 languages to compare yours against — Rust and Python included. |
| [Rosetta Code: Base64 encode data ↗](https://rosettacode.org/wiki/Base64_encode_data) | The 3-bytes-to-4-characters packing that Tribit's layer 3 is the mirror image of. |
| [Codewars: Rust katas matching "utf" ↗](https://www.codewars.com/kata/search/rust?q=utf) | Several small UTF-8 and code-point katas with a test harness; free account needed to submit. |
| Exercism, Rust and Python tracks — *Hexadecimal*, *Binary*, *Octal*, *Bob*, *Atbash Cipher* | The base-conversion exercises are chapter 1 as katas. (Exercism's pages refuse automated fetches, so no link here; search the track by name.) |

Katas this library will host itself, with compiled solutions, are on the [ROADMAP](ROADMAP.md).
