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
| [Control characters](02_Characters/control_characters/README.md) | stub — **next** |
| [Code pages](02_Characters/code_pages/README.md) | stub |
| [Unicode code points](02_Characters/unicode_code_points/README.md) | stub |
| [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) | stub |
| [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) | stub — the checkpoint page |
| [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) | stub |
| [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) | stub |
| [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) | stub |
| [Mojibake](03_Encodings/mojibake/README.md) | stub |
| [04_Python](04_Python/README.md) — five pages | stubs |
| [05_Rust](05_Rust/README.md) — four pages | stubs |
| [06_Terminal](06_Terminal/README.md) — four pages | stubs |
| [07_Real_Data](07_Real_Data/README.md) — six pages | stubs |

## Deliberately not yet

- **A C track.** Not a fourth language; a short *The C view* aside on three pages (ASCII, NUL, UTF-8 by hand), compiled and checked like the others. The runner would need a `.c` case; cheap, but not before those pages exist.
- **Katas.** The sibling libraries keep exercises on the page with a compiled solution. Worth adding once chapter 3 is written, because "encode this code point by hand" is the natural first kata and it needs the UTF-8 page to point at.
- **Polish sections (`## Po polsku`).** The Rust library carries them on its ownership pages. Relevant here — Latin-2, Windows-1250 and the Polish letters' decomposed forms are all lessons — but the terminology table comes first.
- **The locale lesson's UTF-8 half.** Only recordable if both CI runners have a UTF-8 locale installed; check `locale -a` on each before promising it.
- **`file`'s wording.** Differs between versions, so that page will record only `--mime-encoding`.
