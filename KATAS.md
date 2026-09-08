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
| K17 | [Five numbers for one Polish word, and the letter that does not come apart](02_Characters/a_code_point_is_not_a_character/README.md#practice) | [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) | 201 |
| K18 | [Five checks that all say no, and only one for the right reason](02_Characters/confusables_and_scripts/README.md#practice) | [Confusables and scripts](02_Characters/confusables_and_scripts/README.md) | 301 |
| K19 | [Five ways to type one variable name, and the language that says so](02_Characters/unicode_in_identifiers/README.md#practice) | [Unicode in identifiers](02_Characters/unicode_in_identifiers/README.md) | 301 |
| K20 | [One bad byte, and how much of the check survives the call](03_Encodings/validation_is_a_boundary/README.md#practice) | [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) | 201 → 301 |
| K21 | [Two spellings of a slash, and the filter that only sees one](03_Encodings/overlong_sequences/README.md#practice) | [Overlong sequences](03_Encodings/overlong_sequences/README.md) | 301 |
| K22 | [Build the surrogate pair by hand, then explain U+10FFFF](03_Encodings/utf16_and_surrogates/README.md#practice) | [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) | 201 |
| K23 | [Write the bytes for six encodings, then name the CSV column](03_Encodings/byte_order_and_bom/README.md#practice) | [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) | 201 |
| K24 | [Five lines, two loud failures and two quiet wrong answers](03_Encodings/encode_and_decode_are_verbs/README.md#practice) | [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) | 101 |
| K25 | [Name the culprit from the garbage, and say which garbage is repairable](03_Encodings/mojibake/README.md#practice) | [Mojibake](03_Encodings/mojibake/README.md) | 101 → 201 |
| K26 | [One character through four channels, and what each one wraps](03_Encodings/escaping_into_ascii/README.md#practice) | [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md) | 201 |
| K27 | [Predict four output lengths, then find the 4/3 that is not there](03_Encodings/binary_to_text/README.md#practice) | [Binary to text](03_Encodings/binary_to_text/README.md) | 201 |
| K28 | [Four Base32 menu entries, and the one that is a different encoding](03_Encodings/base32_alphabets/README.md#practice) | [The alphabet is not the encoding](03_Encodings/base32_alphabets/README.md) | 201 |
| K29 | [Seven numbers for one two-character string](03_Encodings/the_encoding_model/README.md#practice) | [An encoding is four layers](03_Encodings/the_encoding_model/README.md) | 201 |
| K30 | [Six error policies, and the only one you can reverse](04_Python/encode_decode_and_errors/README.md#practice) | [Encode, decode and errors](04_Python/encode_decode_and_errors/README.md) | 101 → 201 |
| K31 | [Nine ways out of one string, and the two bytes it will not carry](04_Python/surrogateescape/README.md#practice) | [Bytes that are not text](04_Python/surrogateescape/README.md) | 201 |
| K32 | [Two spellings, four forms, and the lookup that raises nothing](04_Python/normalization/README.md#practice) | [Normalization](04_Python/normalization/README.md) | 201 |
| K33 | [Five refusals, one invariant](05_Rust/string_is_bytes_that_promise_utf8/README.md#practice) | [`String` is bytes that promise UTF-8](05_Rust/string_is_bytes_that_promise_utf8/README.md) | 101 → 201 |
| K34 | [A file with a letter in it and zero lines, and the loop that drops it](06_Terminal/trailing_newline/README.md#practice) | [The trailing newline](06_Terminal/trailing_newline/README.md) | 101 → 201 |
| K35 | [Three decisions about one newline byte, and the row that needs all three](06_Terminal/character_and_its_bytes/README.md#practice) | [A character and its bytes on one line](06_Terminal/character_and_its_bytes/README.md) | 101 |
| K36 | [Five readings of six bytes -- which column is the file?](06_Terminal/inspecting_a_file/README.md#practice) | [Inspecting a file](06_Terminal/inspecting_a_file/README.md) | 101 → 201 |
| K37 | [Six variables, and whether any of them changes a Python len()](06_Terminal/locale_and_lc_ctype/README.md#practice) | [Locale and `LC_CTYPE`](06_Terminal/locale_and_lc_ctype/README.md) | 201 |
| K38 | [One file, four answers, and which one the kernel consults](06_Terminal/file_type_is_four_questions/README.md#practice) | [File type is four questions](06_Terminal/file_type_is_four_questions/README.md) | 201 |
| K39 | [Three scripts, six answers, and the two that surprise you](06_Terminal/the_first_two_bytes/README.md#practice) | [The first two bytes](06_Terminal/the_first_two_bytes/README.md) | 101 → 201 |
| K40 | [Assemble the escape sequence, then find the byte nobody escapes](06_Terminal/terminal_hyperlinks/README.md#practice) | [Terminal hyperlinks, and the URI that is not one](06_Terminal/terminal_hyperlinks/README.md) | 201 |
| K41 | [Three bytes that are the fix and the bug at once](07_Real_Data/bom_in_a_csv/README.md#practice) | [A BOM in a CSV](07_Real_Data/bom_in_a_csv/README.md) | 101 → 201 |
| K42 | [Totals right to the cent, keys that match nothing](07_Real_Data/crlf_vs_lf/README.md#practice) | [CRLF vs LF](07_Real_Data/crlf_vs_lf/README.md) | 101 → 201 |
| K43 | [Five scars, and the constraint that made each one right](09_History/from_telegraph_to_unicode/README.md#practice) | [From the telegraph to Unicode](09_History/from_telegraph_to_unicode/README.md) | 201 |
| K44 | [Six properties in six lines, and the bill it pays](09_History/why_utf8_won/README.md#practice) | [Why UTF-8 won](09_History/why_utf8_won/README.md) | 201 |
| K45 | [What those four systems actually adopted, and why they cannot leave](09_History/why_utf16_stayed/README.md#practice) | [Why UTF-16 stayed](09_History/why_utf16_stayed/README.md) | 201 |
| K46 | [Five rules, and the line of code each one forbids](10_Best_Practices/utf8_everywhere/README.md#practice) | [UTF-8 everywhere](10_Best_Practices/utf8_everywhere/README.md) | 201 |
| K47 | [Five signatures, and the one the compiler refuses](10_Best_Practices/rust_strings_in_practice/README.md#practice) | [Rust strings in practice](10_Best_Practices/rust_strings_in_practice/README.md) | 201 → 301 |
| K48 | [Four habits, and the bytes method that is right and still a bug](10_Best_Practices/python_text_in_practice/README.md#practice) | [Python text in practice](10_Best_Practices/python_text_in_practice/README.md) | 201 |
| K49 | [Six round trips, and the three that come back unchanged](10_Best_Practices/what_your_language_gives_you/README.md#practice) | ["Handles Unicode" is four questions](10_Best_Practices/what_your_language_gives_you/README.md) | 301 |
| K50 | [What does a dot match? Four answers, and who decided](11_Tools/grep/README.md#practice) | [`grep` on text that is not ASCII](11_Tools/grep/README.md) | 201 |
| K51 | [Three marks, one missing encoding, and three defaults that hide a file](11_Tools/ripgrep/README.md#practice) | [`ripgrep` — the Rust grep](11_Tools/ripgrep/README.md) | 201 |
| K52 | [The only engine that can match one grapheme, and what it stops telling you](11_Tools/pcre2/README.md#practice) | [PCRE2 — the other regex engine](11_Tools/pcre2/README.md) | 201 |
| K53 | [Two stages, and why removing a container fixes no encoding](11_Tools/decompress_then_decode/README.md#practice) | [`--pre` and `-z` — decompress, then decode](11_Tools/decompress_then_decode/README.md) | 201 |
| K54 | [A file cat can open and find -name cannot see](11_Tools/find/README.md#practice) | [`find`, and filenames that are bytes](11_Tools/find/README.md) | 201 |
| K55 | [Four filenames, and how many survive the naive pipeline](11_Tools/xargs/README.md#practice) | [`xargs` splits on the wrong things](11_Tools/xargs/README.md) | 201 |
| K56 | [The edit that works, the locale that breaks it, and the -i with no portable spelling](11_Tools/sed/README.md#practice) | [`sed` matches patterns, not bytes](11_Tools/sed/README.md) | 201 |
| K57 | [Whose awk is this, and what does length() count?](11_Tools/awk/README.md#practice) | [`awk` is three programs](11_Tools/awk/README.md) | 201 |
| K58 | [-b or -c, and the machine that changes the answer](11_Tools/cut/README.md#practice) | [`cut` counts what it is told to count](11_Tools/cut/README.md) | 201 |
| K59 | [Delete one letter, damage two words -- sets against sequences](11_Tools/tr_and_sort/README.md#practice) | [`tr` and `sort` work a byte at a time](11_Tools/tr_and_sort/README.md) | 201 |
| K60 | [Four ways to ask if two files match, none of them the question you meant](11_Tools/diff_and_cmp/README.md#practice) | [`diff` compares lines, `cmp` compares bytes, neither compares text](11_Tools/diff_and_cmp/README.md) | 201 |
| K61 | [Three tools that take text as bytes, and the one with no opinion](11_Tools/look_paste_tee_split/README.md#practice) | [`split` cuts characters, `paste` cuts delimiters, `look` needs a sorted file, `tee` does nothing](11_Tools/look_paste_tee_split/README.md) | 201 |
| K62 | [Seven ways to blank a file, and the one that leaves the old bytes behind](11_Tools/creating_and_writing_files/README.md#practice) | [`touch`, `: >` and `install` are not three spellings of one command](11_Tools/creating_and_writing_files/README.md) | 201 |
| K63 | [Why the pairs came out swapped, and what a grouping width claims](11_Tools/hexdump/README.md#practice) | [`hexdump` is a format engine wearing six presets](11_Tools/hexdump/README.md) | 201 |
| K64 | [Edit the dump and put it back -- and find the column that was ignored](11_Tools/xxd/README.md#practice) | [`xxd` is the dump you can put back](11_Tools/xxd/README.md) | 201 |
| K65 | [Read the interface as a C type, and say why -a cannot be quoted](11_Tools/od/README.md#practice) | [`od` reads types, not bytes](11_Tools/od/README.md) | 201 |
| K66 | [Six columns, and the one no dump tool has](11_Tools/uni/README.md#practice) | [`uni` — the character's name](11_Tools/uni/README.md) | 101 → 201 |
| K67 | [Four ways to type it, and the two that identify the character](11_Tools/typing_a_character/README.md#practice) | [Typing a character you cannot type](11_Tools/typing_a_character/README.md) | 101 → 201 |
| K68 | [One byte string, two readers, and a duplicate JSON key](12_Adversarial/parser_differentials/README.md#practice) | [Two readers, one byte string](12_Adversarial/parser_differentials/README.md) | 301 |
| K69 | [Five paths, two orders, and why checking harder is not the fix](12_Adversarial/canonicalize_then_check/README.md#practice) | [The check that ran too early](12_Adversarial/canonicalize_then_check/README.md) | 301 |
| K70 | [Six signups, three classes, and who owns each one](12_Adversarial/collisions_by_design/README.md#practice) | [Two people, one account](12_Adversarial/collisions_by_design/README.md) | 301 |
| K71 | [Five bytes that end a field for somebody else](12_Adversarial/in_band_signals/README.md#practice) | [The byte that means something to somebody else](12_Adversarial/in_band_signals/README.md) | 301 |
| K72 | [Two readers of one file, and the one with no access to the bytes](12_Adversarial/trojan_source/README.md#practice) | [What you see is not what runs](12_Adversarial/trojan_source/README.md) | 301 |
| K73 | [Forty pages nobody opens, and how to find them without the names](13_Documentation/the_encoding_man_pages/README.md#practice) | [The encoding man pages nobody opens](13_Documentation/the_encoding_man_pages/README.md) | 201 |
| K74 | [Out of date, or wrong? -- and the three dates a page carries](13_Documentation/a_page_has_a_date/README.md#practice) | [A page has a date](13_Documentation/a_page_has_a_date/README.md) | 201 |
| K75 | [The flag no page mentions, and the two platforms that disagree about it](13_Documentation/what_the_page_does_not_say/README.md#practice) | [What the page does not say](13_Documentation/what_the_page_does_not_say/README.md) | 201 |
