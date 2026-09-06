# Roadmap

**Level:** reference

What is written, what is a stub, and what is next — in the order the stubs will be filled, which is the reading order.

## Status

| Page | Status |
|---|---|
| [A byte is eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) | written, 2026-09-05 |
| [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) | written, 2026-09-05 |
| [Reading a hex dump](01_Bits_and_Bytes/reading_a_hex_dump/README.md) | written, 2026-09-05 |
| [A character is a number](02_Characters/a_character_is_a_number/README.md) | written, 2026-09-05 |
| [Control characters](02_Characters/control_characters/README.md) | written, 2026-09-05 — the first page with a *C view* (`examples/*.c`, compiled by the runner since the same day) |
| [Code pages](02_Characters/code_pages/README.md) | written, 2026-09-05 — Python, Rust and shell; the agreement matrix is the original bit |
| [Unicode code points](02_Characters/unicode_code_points/README.md) | written, 2026-09-05 — the neighbourhood map: read `U+XXXX` as a block plus a house number, and measure the whitespace runs instead of memorising them |
| [The table has a version](02_Characters/the_table_has_a_version/README.md) | written, 2026-09-06 — Python and Rust; `python3` and `rustc` on one machine were a Unicode release apart, and the page is about which of the three kinds of fact may go in a key |
| [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) | stub |
| [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) | stub — the checkpoint page |
| [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) | written, 2026-09-05 — all four languages, and the second *C view* |
| [Overlong sequences](03_Encodings/overlong_sequences/README.md) | written, 2026-09-05 — all four languages; the shortest-form rule, Table 3-7, and the three formats that break it on purpose |
| [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) | stub |
| [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) | written, 2026-09-05 — Python, Rust and shell; why `U+FFFE` makes the mirror proof rather than convention |
| [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) | written, 2026-09-05 — Python, Rust and shell |
| [Mojibake](03_Encodings/mojibake/README.md) | written, 2026-09-05 — Python and shell; the Rust point is the previous page's |
| [Normalization](04_Python/normalization/README.md) | written, 2026-09-06 — Python and Rust; chapter 4's first, and the one Unicode table lookup the stability policy lets an answer key hold |
| [04_Python](04_Python/README.md) — the other four pages | stubs |
| [`String` is bytes that promise UTF-8](05_Rust/string_is_bytes_that_promise_utf8/README.md) | written, 2026-09-05 — Rust, Python and shell; the one figure in the repo, and `valid_up_to()` matched against Python's `UnicodeDecodeError.start` |
| [05_Rust](05_Rust/README.md) — the other three pages | stubs |
| [Inspecting a file](06_Terminal/inspecting_a_file/README.md) | written, 2026-09-05 — the named-character row is fiction in two dialects, and the `?` is the terminal's, not od's |
| [The trailing newline](06_Terminal/trailing_newline/README.md) | written, 2026-09-06 — shell, Python and Rust; why a two-byte file reports zero lines, and the marker your shell draws that is not in the file |
| [A character and its bytes on one line](06_Terminal/character_and_its_bytes/README.md) | written, 2026-09-06 — shell and Python; the one-liner, and the three separate newline decisions that let it fit on one row |
| [Locale and `LC_CTYPE`](06_Terminal/locale_and_lc_ctype/README.md) | written, 2026-09-06 — the locale is six independent variables; `wc -c` and `wc -m` collapse to one answer under `C`, `LC_CTYPE` does not touch sort order, and Python has declined to obey any of it since 3.7 |
| [06_Terminal](06_Terminal/README.md) — the other three pages | stubs |
| [A BOM in a CSV](07_Real_Data/bom_in_a_csv/README.md) | written, 2026-09-05 — Python and shell; the decision procedure, and the two platform fingerprints |
| [07_Real_Data](07_Real_Data/README.md) — the other five pages | stubs |
| [From the telegraph to Unicode](09_History/from_telegraph_to_unicode/README.md) | written, 2026-09-05 |
| [Why UTF-8 won](09_History/why_utf8_won/README.md) | written, 2026-09-05 |
| [UTF-8 everywhere](10_Best_Practices/utf8_everywhere/README.md) | written, 2026-09-05 |
| [Rust strings in practice](10_Best_Practices/rust_strings_in_practice/README.md) | written, 2026-09-05 |
| [Python text in practice](10_Best_Practices/python_text_in_practice/README.md) | written, 2026-09-05 |
| [Interfaces and storage](10_Best_Practices/interfaces_and_storage/README.md) | stub |
| [`grep` on text that is not ASCII](11_Tools/grep/README.md) | written, 2026-09-06 — shell and Python; the silent skip, measured, and the binary notice's two streams |
| [`ripgrep` — the Rust grep](11_Tools/ripgrep/README.md) | written, 2026-09-06 — no rg on either runner, so the session is dated and a Python example checks the rules |
| [`find`, and filenames that are bytes](11_Tools/find/README.md) | written, 2026-09-06 — shell and Python; `cat` opens what `find -name` cannot see |
| [`tr` and `sort` work a byte at a time](11_Tools/tr_and_sort/README.md) | written, 2026-09-06 — shell; deleting `é` damages the word next door |
| [`uni` — the character's name](11_Tools/uni/README.md) | written, 2026-09-06 — dated sessions plus a `unicodedata` example printing the same columns |
| [The five worth installing](11_Tools/worth_installing/README.md) | written, 2026-09-06 — each optional tool measured against a machine-checked baseline |
| [Tribit — the specification](08_Build_Your_Own/tribit/README.md) | written, 2026-09-05 — the Rust implementation is Adam's project |
| [RESOURCES.md](RESOURCES.md) | written, 2026-09-05 — re-check the links when a page graduates and cites one |

## Written out of order, on purpose

Chapter 11 was written on 2026-09-06, before chapters 4–7, for the same reason chapters 9 and 10 were: it does not depend on them. It is also the chapter a reader arrives at from outside — somebody whose search did not match, or whose `find` came up empty, has a concrete problem today and no reason to have read chapter 3 first. Each page states what it needs and links back.

Chapters 9 and 10 were written before chapters 3–7 because they are the two that do not depend on them. [09_History](09_History/README.md) explains the *shape* of everything the stubs will say, so it makes the remaining pages read as conclusions rather than commandments; [10_Best_Practices](10_Best_Practices/README.md) is the answer a reader most often arrives wanting, and leaving it until last would have meant a library that could explain every trap and never say what to do. Both link forward into the stubs, so filling those in adds detail under an argument that is already made.

Chapter 3's last two lessons went the same way on 2026-09-05, and for a smaller reason: [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) and [Mojibake](03_Encodings/mojibake/README.md) are the pair that names the whole problem, and the front page had been describing that problem with nowhere finished to send a reader. Neither needs [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) — they are about the table being an argument, not about the bit-packing inside any one table — so the checkpoint page is still next after `code_pages`.

## Deliberately not yet

- **A C track.** Not a fourth language; a short *The C view* aside where it sharpens the point, compiled and checked like the others. The runner takes `examples/*.c` since 2026-09-05; [Control characters](02_Characters/control_characters/README.md) has the first one (NUL and `strlen`) [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) the second (the validator nobody writes for you), and [Overlong sequences](03_Encodings/overlong_sequences/README.md) the third (the three comparisons that are the entire shortest-form rule).
- **Katas.** The sibling libraries keep exercises on the page with a compiled solution. Worth adding once chapter 3 is written, because "encode this code point by hand" is the natural first kata and it needs the UTF-8 page to point at. Until then RESOURCES.md points at the outside katas, and the Tribit project is the big one.
- **Tribit version 2 (self-synchronising) and the Rust crate itself.** Both are Adam's exercises, listed at the bottom of the spec; when the crate exists, link it from the spec page rather than vendoring it here.
- **Polish sections (`## Po polsku`).** The Rust library carries them on its ownership pages. Relevant here — Latin-2, Windows-1250 and the Polish letters' decomposed forms are all lessons — but the terminology table comes first.
- **~~The locale lesson's UTF-8 half.~~ Resolved 2026-09-06.** The worry was that a UTF-8 locale might not exist on both runners. It does — `C.UTF-8` is present on macOS 26.6 and on Ubuntu, and the example picks one by asking each candidate for its `charmap` and keeping the *name* out of the output. Both examples verified byte-identical on macOS and Linux (Python across 3.11–3.14) before recording. The one thing that genuinely could not be recorded is `tr`, now a dated table on the page and a seventh entry in CONTRIBUTING's BSD/GNU list.
- **`file`'s wording.** Differs between versions, so that page will record only `--mime-encoding`.

## Concept backlog — the columns nothing here answers yet

Assembled 2026-09-06 by reading `uni -h` as an inventory rather than a manual. Its `-f` placeholders are one line per question the Unicode Character Database can answer about a character, and six of them have no page in this library. Each entry below is listed with the fact that makes it a *lesson* rather than a topic — all of them measured on this Mac the day the list was written, so a page can start from a hook instead of a definition.

- **The fifth length: how many columns.** `%(cells)` is 1 for `A`, 2 for `日` and `😀`, 0 for a combining mark — and `%(width)` says `é` is **ambiguous**, meaning one column in this terminal and two in a CJK one. [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) already promises terminal columns as its fifth answer and is the page that owes it. The half worth knowing before writing it: `unicodedata.east_asian_width()` is **standard library**, so the width claim can be machine-checked (`Na` `W` `A` `N`) even though nothing in either language's `len` will tell you a column count.
- **Writing a character where only ASCII is allowed.** `%(html)`, `%(xml)` and `%(json)` are three answers to one question this library never asks, and it is the question a SAP interface asks every day: `&eacute;`, `&#xE9;`, `é`, `%C3%A9`, `=?utf-8?b?…?=`, `xn--`. The hook is `json.dumps("😀")` → `"\ud83d\ude00"` — **a UTF-16 surrogate pair inside a format that is UTF-8 by [RFC 8259 ↗](https://www.rfc-editor.org/rfc/rfc8259#section-8.1)**, which is [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) leaking into a place that has no UTF-16 in it. Percent-encoding is the same lesson upside down: `%C5%BC` is `ż`'s UTF-8 bytes written in [hex](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) and nothing else. Feeds [Interfaces and storage](10_Best_Practices/interfaces_and_storage/README.md), whose example already names a URL-encoded query string.
- **How you type it.** `%(keysym)` and `%(digraph)` — `é` is `eacute` / `e'`, `€` is `EuroSign` / `=e`. Nothing in this library tells a reader how to *produce* a character they have just identified, which is the next thing anybody wants. The page is short: compose key, Vim digraphs, `'\N{EURO SIGN}'` in Python, `'\u{20AC}'` in Rust, and `uni print U+20AC | pbcopy`.
- **The name is not always a name.** `unicodedata.name('\x00')` **raises**, and `uni` prints `NULL` — because the UCD gives control characters no Name at all and `NULL` is a *Name Alias*. Python will go the other way (`unicodedata.lookup('NULL')` returns `'\x00'`) but not from the string uni displays (`lookup('LINE FEED (LF)')` is a `KeyError`). And the reason names are frozen is legible in one row: U+FE18 is PRESENTATION FORM FOR VERTICAL RIGHT WHITE LENTICULAR **BRAKCET**, a typo that can never be corrected because Name is a stability guarantee. Belongs beside [The table has a version](02_Characters/the_table_has_a_version/README.md), which already turns on which facts a key may contain.
- **Confusables, invisibles and the security page.** `%(refs)` is the UCD's own cross-reference list (U+2044 FRACTION SLASH points at U+002F and U+2215), and `%(props)` names the three characters that make text lie: U+200D ZERO WIDTH JOINER (Join Control), U+FE0F VARIATION SELECTOR-16, and U+202E RIGHT-TO-LEFT OVERRIDE (**Bidi Control** — the [Trojan Source ↗](https://trojansource.codes/) class of bug). Cyrillic `а` and Latin `a` are the other half. The library has the tools for this page already — [`uni identify`](11_Tools/uni/README.md) is the diagnosis and [normalization](04_Python/normalization/README.md) is the partial cure — and no page that says so.
- **Two databases, not one.** uni's *names* come from the UCD; its emoji *search* matches **CLDR** keywords (`uni emoji firefighter` matches on `firetruck`, a word not in the character's name), and `-tone`/`-gender` assemble sequences: `👩🏻‍🚒` is `U+1F469 U+1F3FB U+200D U+1F692`, four code points and one grapheme. That split — character data versus locale data — is also the missing half of [`tr` and `sort`](11_Tools/tr_and_sort/README.md), since collation order is CLDR's answer and not the UCD's.

One column needs no page of its own and is worth borrowing: `%(unicode)` prints the release a character was **first assigned in** (`😀` = 6.1, `A` = 1.1), which is the concrete version of the argument [The table has a version](02_Characters/the_table_has_a_version/README.md) makes with two tools disagreeing.
