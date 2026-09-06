# Glossary

**Level:** reference

Short entries, each with the page that explains it in full. Alphabetical.

| Term | In one line | Read more |
|---|---|---|
| **ASCII** | The 1963 agreement assigning 128 numbers (0–127, seven bits) to characters; the first 128 rows of every table that came after | [A character is a number](02_Characters/a_character_is_a_number/README.md) |
| **bit** | One switch, `0` or `1` | [A byte is eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| **BOM** | Byte order mark, the code point `U+FEFF` written first in a file so a reader can tell the byte order; `EF BB BF` in UTF-8, where it marks nothing and still gets written | [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) |
| **byte** | Eight bits; 256 patterns; the numbers 0..255; the unit a file is measured in. Has no meaning until a table is applied | [A byte is eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| **code page** | A 256-entry table agreeing with ASCII on the first 128 and with nobody on the second 128 — Latin-1, Windows-1252, Latin-2, CP437 | [Code pages](02_Characters/code_pages/README.md) |
| **code point** | A character's number in Unicode, written `U+00E9`. A number, not a byte | [Unicode code points](02_Characters/unicode_code_points/README.md) |
| **code unit** | The fixed-width piece an encoding is written in: 8 bits for UTF-8, 16 for UTF-16, 32 for UTF-32. A code point takes one or more of them | [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) |
| **control character** | ASCII 0–31 and 127: commands to a teletype, not glyphs. TAB (9), LF (10) and CR (13) are the ones still in daily use | [Control characters](02_Characters/control_characters/README.md) |
| **CRLF** | The two-byte Windows line ending, `0D 0A`; Unix uses LF alone, `0A` | [CRLF vs LF](07_Real_Data/crlf_vs_lf/README.md) |
| **decode** | Bytes → code points, under a named table. The inverse of encode | [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) |
| **encode** | Code points → bytes, under a named table | [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) |
| **encoded-word** | The MIME form `=?charset?B?payload?=` that carries non-ASCII text in an email header — and the only escape in common use that names the charset it wrapped | [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md) |
| **encoding** | The rule for writing code points as bytes: UTF-8, UTF-16, Latin-1 … Also, loosely, any code page | [03_Encodings](03_Encodings/README.md) |
| **endianness** | Which byte of a multi-byte number is written first: big-endian (most significant first) or little-endian | [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) |
| **grapheme cluster** | What a person calls one character: possibly several code points (`e` + combining acute; a flag; a family emoji) | [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) |
| **hex dump** | A file shown as offset · hex bytes · ASCII guess, sixteen bytes per line; `xxd`, `od`, `hexdump -C` | [Reading a hex dump](01_Bits_and_Bytes/reading_a_hex_dump/README.md) |
| **hexadecimal** | Base 16; binary written four bits per digit, so a byte is always two digits | [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| **Latin-1** | ISO-8859-1. The code page where byte value = code point for 0..255, so decoding under it never fails — which makes it the wrong tool for detecting anything and the right one for undoing mojibake | [Code pages](02_Characters/code_pages/README.md) |
| **Modified UTF-8** | Java's near-UTF-8: `U+0000` written as the overlong `C0 80`, and characters above `U+FFFF` written as two three-byte surrogates (that half is **CESU-8**). Used in `.class` files, `DataInput`/`DataOutput` and JNI. Fails a UTF-8 validator, correctly | [Overlong sequences](03_Encodings/overlong_sequences/README.md) |
| **mojibake** | Bytes decoded under the wrong table: `Ã©` is `C3 A9` (UTF-8 for `é`) read as Latin-1 | [Mojibake](03_Encodings/mojibake/README.md) |
| **nibble** | Four bits; one hex digit; half a byte | [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| **normalization** | Rewriting a string to one canonical code-point sequence (NFC, NFD …) so that two spellings of `é` compare equal | [Normalization](04_Python/normalization/README.md) |
| **overlong form** | A code point written in more bytes than it needs — `C0 AF` for `/`, `C1 BD` for `}` — which the templates decode fine and every validator rejects, because one character must have exactly one encoding. Why `C0` and `C1` never appear in real UTF-8 | [Overlong sequences](03_Encodings/overlong_sequences/README.md) |
| **percent-encoding** | `%XX` per byte, the escape a URL uses — the hex dump with a sign in front. Nothing in the URL records which encoding produced those bytes | [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md) |
| **punycode** | The ASCII re-spelling of a domain label (`żółw` → `w-uga1v8h`, written `xn--w-uga1v8h`). Defined over code points, not bytes, so there is no encoding to guess | [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md) |
| **replacement character** | `U+FFFD` `�`, what a decoder writes in place of bytes it cannot read, if told to replace rather than raise | [Encode, decode and errors](04_Python/encode_decode_and_errors/README.md) |
| **scalar value** | A code point that is *not* a surrogate: `U+0000`–`U+D7FF` and `U+E000`–`U+10FFFF`. What UTF-8 can encode, and exactly what Rust's `char` can hold | [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) |
| **surrogate pair** | Two 16-bit UTF-16 units (`D800–DBFF` then `DC00–DFFF`) standing for one code point above `U+FFFF` | [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) |
| **tofu** | The empty box `□` shown for a character the FONT has no glyph for. Not an encoding error at all — the bytes decoded correctly, and changing the encoding to chase it is how a working file gets damaged | [Mojibake](03_Encodings/mojibake/README.md) |
| **Unicode** | The one numbering for every character in every script: 1,114,112 code points, 17 planes | [Unicode code points](02_Characters/unicode_code_points/README.md) |
| **UTF-8** | The encoding that writes a code point as 1–4 bytes, leaves ASCII unchanged, and is what nearly every file today is | [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) |
| **UTF-16** | The encoding that writes a code point as one or two 16-bit units; Windows, Java, JavaScript and SAP's internal form | [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) |
| **validation** | Checking that a run of bytes really follows an encoding's rules. Cheap, done once, at the edge of a program — and what a language remembers about it afterwards is the whole difference between them | [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) |
| **Windows-1252** | Latin-1 with the 32 bytes `0x80–0x9F` reassigned to `€`, smart quotes and friends; SAP code page 1160 | [Windows-1252 vs Latin-1](07_Real_Data/windows_1252_vs_latin1/README.md) |
| **xstring** | ABAP's byte-sequence type, displayed in hex; the counterpart of Python's `bytes`. `string` and `c` are characters | [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
