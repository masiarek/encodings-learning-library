# Katas

**Level:** reference · the practice track

**One line:** The lessons explain; the katas make you predict. Each one lives on the page for the topic it teaches — this is the only place they are put in an order.

## Where a kata lives

**A kata belongs to its topic, not to a folder of its own.** The page that explains the byte is the page that asks you to write one down, under a `## Practice` heading near the end, with the answer folded into a `<details markdown="1">` block.

That is deliberate, and the reason is that folders are URLs. A topic — the byte, the code point, `grep`'s locale — is stable for years; a *sequence* is not. The moment a kata belongs between K1 and K2, a `K01_…/` folder either gets renumbered, breaking every link anyone saved, or starts lying about its own order. So the sequence lives here, in a table that costs nothing to reorder, and the numbers below are labels rather than addresses. Same rule as the sidebar: order is presentation, so it belongs in a page, never in a path.

**Every answer here is printed by a program**, recorded as an answer key and run by CI on Ubuntu and macOS with every other example in the library — so a solution cannot rot into one that no longer says what the page says. [`check_katas.py`](tools/check_katas.py) enforces that, and the rules are written down in [CONTRIBUTING.md](CONTRIBUTING.md).

## The katas

| # | Kata | Lesson | Level |
|---|---|---|---|
| K1 | [One byte, four readings — and the byte decides none of them](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md#practice) | [A byte is eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) | 101 |
| K2 | [Turn the odometer in your head — five hex questions, one carry](01_Bits_and_Bytes/counting_in_hex/README.md#practice) | [Counting in hexadecimal](01_Bits_and_Bytes/counting_in_hex/README.md) | 101 |
| K3 | [Four bits at a time, both ways — then find the byte boundary in octal](01_Bits_and_Bytes/hex_is_a_shorthand/README.md#practice) | [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) | 101 |
| K4 | [Read the three columns off a file whose bytes you chose](01_Bits_and_Bytes/reading_a_hex_dump/README.md#practice) | [Reading a hex dump](01_Bits_and_Bytes/reading_a_hex_dump/README.md) | 101 |
| K5 | [Thirteen bytes at three widths, and where the ragged piece falls](01_Bits_and_Bytes/grouping_is_a_choice/README.md#practice) | [Grouping is a choice](01_Bits_and_Bytes/grouping_is_a_choice/README.md) | 101 → 201 |
| K6 | [The hash field that arrived one character short, read three ways](01_Bits_and_Bytes/hex_number_or_bytes/README.md#practice) | [Hex: a number, or a picture of bytes](01_Bits_and_Bytes/hex_number_or_bytes/README.md) | 201 |
| K7 | [Two columns for four expressions — and where the loss happens in each language](01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md#practice) | [Arithmetic has its own width](01_Bits_and_Bytes/arithmetic_has_its_own_width/README.md) | 101 → 201 |
| K8 | [Three ASCII tricks, and the four characters that break them](02_Characters/a_character_is_a_number/README.md#practice) | [A character is a number](02_Characters/a_character_is_a_number/README.md) | 101 |
| K9 | [Rotate, rotate back, then step outside ASCII and lose both guarantees](02_Characters/rotation_is_not_encryption/README.md#practice) | [Rotation is not encryption](02_Characters/rotation_is_not_encryption/README.md) | 101 → 201 |
| K10 | [How many lines is this string? Three answers, all correct](02_Characters/control_characters/README.md#practice) | [Control characters](02_Characters/control_characters/README.md) | 101 |
| K11 | [Five doors, and the one byte that is valid UTF-8 and welcome nowhere](02_Characters/the_nul_byte/README.md#practice) | [The NUL byte](02_Characters/the_nul_byte/README.md) | 201 |
| K12 | [One byte, four tables — and the byte that settles the superset question](02_Characters/code_pages/README.md#practice) | [Code pages](02_Characters/code_pages/README.md) | 101 → 201 |
| K13 | [Four code points read as addresses, and what each costs to write](02_Characters/unicode_code_points/README.md#practice) | [Unicode code points](02_Characters/unicode_code_points/README.md) | 101 → 201 |
| K14 | [Four spellings of é, then the character `\u` cannot reach](02_Characters/writing_a_code_point/README.md#practice) | [Writing a code point](02_Characters/writing_a_code_point/README.md) | 201 |
| K15 | [Five claims: which go in a bug report without a version stamp?](02_Characters/the_table_has_a_version/README.md#practice) | [The table has a version](02_Characters/the_table_has_a_version/README.md) | 201 |
| K16 | [Six strings, three of them one user — and when folding is the bug](02_Characters/preparing_a_string/README.md#practice) | [Preparing a string](02_Characters/preparing_a_string/README.md) | 301 |
| K17 | [Five checks that all say no, and only one for the right reason](02_Characters/confusables_and_scripts/README.md#practice) | [Confusables and scripts](02_Characters/confusables_and_scripts/README.md) | 301 |
| K18 | [Five ways to type one variable name, and the language that says so](02_Characters/unicode_in_identifiers/README.md#practice) | [Unicode in identifiers](02_Characters/unicode_in_identifiers/README.md) | 301 |
| K19 | [One bad byte, and how much of the check survives the call](03_Encodings/validation_is_a_boundary/README.md#practice) | [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) | 201 → 301 |
| K20 | [Two spellings of a slash, and the filter that only sees one](03_Encodings/overlong_sequences/README.md#practice) | [Overlong sequences](03_Encodings/overlong_sequences/README.md) | 301 |
| K21 | [Build the surrogate pair by hand, then explain U+10FFFF](03_Encodings/utf16_and_surrogates/README.md#practice) | [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) | 201 |
| K22 | [Write the bytes for six encodings, then name the CSV column](03_Encodings/byte_order_and_bom/README.md#practice) | [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) | 201 |
| K23 | [Five lines, two loud failures and two quiet wrong answers](03_Encodings/encode_and_decode_are_verbs/README.md#practice) | [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) | 101 |
| K24 | [Name the culprit from the garbage, and say which garbage is repairable](03_Encodings/mojibake/README.md#practice) | [Mojibake](03_Encodings/mojibake/README.md) | 101 → 201 |
| K25 | [One character through four channels, and what each one wraps](03_Encodings/escaping_into_ascii/README.md#practice) | [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md) | 201 |
| K26 | [Predict four output lengths, then find the 4/3 that is not there](03_Encodings/binary_to_text/README.md#practice) | [Binary to text](03_Encodings/binary_to_text/README.md) | 201 |
| K27 | [Four Base32 menu entries, and the one that is a different encoding](03_Encodings/base32_alphabets/README.md#practice) | [The alphabet is not the encoding](03_Encodings/base32_alphabets/README.md) | 201 |
| K28 | [Nine ways out of one string, and the two bytes it will not carry](04_Python/surrogateescape/README.md#practice) | [Bytes that are not text](04_Python/surrogateescape/README.md) | 201 |
| K29 | [Six round trips, and the three that come back unchanged](10_Best_Practices/what_your_language_gives_you/README.md#practice) | ["Handles Unicode" is four questions](10_Best_Practices/what_your_language_gives_you/README.md) | 301 |
| K30 | [Seven ways to blank a file, and the one that leaves the old bytes behind](11_Tools/creating_and_writing_files/README.md#practice) | [`touch`, `: >` and `install` are not three spellings of one command](11_Tools/creating_and_writing_files/README.md) | 201 |
