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
| [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) | stub |
| [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) | stub — the checkpoint page |
| [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) | written, 2026-09-05 — all four languages, and the second *C view* |
| [Overlong sequences](03_Encodings/overlong_sequences/README.md) | written, 2026-09-05 — all four languages; the shortest-form rule, Table 3-7, and the three formats that break it on purpose |
| [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) | stub |
| [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) | written, 2026-09-05 — Python, Rust and shell; why `U+FFFE` makes the mirror proof rather than convention |
| [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) | written, 2026-09-05 — Python, Rust and shell |
| [Mojibake](03_Encodings/mojibake/README.md) | written, 2026-09-05 — Python and shell; the Rust point is the previous page's |
| [04_Python](04_Python/README.md) — five pages | stubs |
| [`String` is bytes that promise UTF-8](05_Rust/string_is_bytes_that_promise_utf8/README.md) | written, 2026-09-05 — Rust, Python and shell; the one figure in the repo, and `valid_up_to()` matched against Python's `UnicodeDecodeError.start` |
| [05_Rust](05_Rust/README.md) — the other three pages | stubs |
| [06_Terminal](06_Terminal/README.md) — four pages | stubs |
| [A BOM in a CSV](07_Real_Data/bom_in_a_csv/README.md) | written, 2026-09-05 — Python and shell; the decision procedure, and the two platform fingerprints |
| [07_Real_Data](07_Real_Data/README.md) — the other five pages | stubs |
| [From the telegraph to Unicode](09_History/from_telegraph_to_unicode/README.md) | written, 2026-09-05 |
| [Why UTF-8 won](09_History/why_utf8_won/README.md) | written, 2026-09-05 |
| [UTF-8 everywhere](10_Best_Practices/utf8_everywhere/README.md) | written, 2026-09-05 |
| [Rust strings in practice](10_Best_Practices/rust_strings_in_practice/README.md) | written, 2026-09-05 |
| [Python text in practice](10_Best_Practices/python_text_in_practice/README.md) | written, 2026-09-05 |
| [Interfaces and storage](10_Best_Practices/interfaces_and_storage/README.md) | stub |
| [Tribit — the specification](08_Build_Your_Own/tribit/README.md) | written, 2026-09-05 — the Rust implementation is Adam's project |
| [RESOURCES.md](RESOURCES.md) | written, 2026-09-05 — re-check the links when a page graduates and cites one |

## Written out of order, on purpose

Chapters 9 and 10 were written before chapters 3–7 because they are the two that do not depend on them. [09_History](09_History/README.md) explains the *shape* of everything the stubs will say, so it makes the remaining pages read as conclusions rather than commandments; [10_Best_Practices](10_Best_Practices/README.md) is the answer a reader most often arrives wanting, and leaving it until last would have meant a library that could explain every trap and never say what to do. Both link forward into the stubs, so filling those in adds detail under an argument that is already made.

Chapter 3's last two lessons went the same way on 2026-09-05, and for a smaller reason: [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) and [Mojibake](03_Encodings/mojibake/README.md) are the pair that names the whole problem, and the front page had been describing that problem with nowhere finished to send a reader. Neither needs [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) — they are about the table being an argument, not about the bit-packing inside any one table — so the checkpoint page is still next after `code_pages`.

## Deliberately not yet

- **A C track.** Not a fourth language; a short *The C view* aside where it sharpens the point, compiled and checked like the others. The runner takes `examples/*.c` since 2026-09-05; [Control characters](02_Characters/control_characters/README.md) has the first one (NUL and `strlen`) [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) the second (the validator nobody writes for you), and [Overlong sequences](03_Encodings/overlong_sequences/README.md) the third (the three comparisons that are the entire shortest-form rule).
- **Katas.** The sibling libraries keep exercises on the page with a compiled solution. Worth adding once chapter 3 is written, because "encode this code point by hand" is the natural first kata and it needs the UTF-8 page to point at. Until then RESOURCES.md points at the outside katas, and the Tribit project is the big one.
- **Tribit version 2 (self-synchronising) and the Rust crate itself.** Both are Adam's exercises, listed at the bottom of the spec; when the crate exists, link it from the spec page rather than vendoring it here.
- **Polish sections (`## Po polsku`).** The Rust library carries them on its ownership pages. Relevant here — Latin-2, Windows-1250 and the Polish letters' decomposed forms are all lessons — but the terminology table comes first.
- **The locale lesson's UTF-8 half.** Only recordable if both CI runners have a UTF-8 locale installed; check `locale -a` on each before promising it.
- **`file`'s wording.** Differs between versions, so that page will record only `--mime-encoding`.
