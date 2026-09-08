# 02_Characters — a character is a number by agreement

**Level:** 101 → 201 · for anyone starting from zero

A [byte](../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) is a number. Text is characters. The only bridge between them is a **table**, and this chapter is the history of that table getting bigger: 128 entries, then 256 with everybody's own second half, then a million with one numbering for all of them.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [A character is a number](a_character_is_a_number/README.md) | Who decided 65 means `A`, and why are the digits and the two alphabets placed where they are? | written |
| 2 | [Rotation is not encryption](rotation_is_not_encryption/README.md) | Why is ROT13 thirteen, why is it not encryption, and what breaks when you rotate past ASCII? | written, 2026-09-07 |
| 3 | [Control characters](control_characters/README.md) | What are the first 32, which three still matter every day, and where does a C string end? | written |
| 4 | [The NUL byte](the_nul_byte/README.md) | Why does one zero byte end a C string, hide a grep match, and make the only separator a filename cannot forge? | written, 2026-09-06 |
| 5 | [Code pages](code_pages/README.md) | What did everybody do with the unclaimed 128, and why do the tables agree just enough to hide the bug? | written, 2026-09-05 |
| 6 | [Unicode code points](unicode_code_points/README.md) | What is `U+00E9`, and why is it a number rather than a byte? | written, 2026-09-05 |
| 7 | [Writing a code point](writing_a_code_point/README.md) | You have the number — how do you write it down, and why does every language spell it differently? | written, 2026-09-06 |
| 8 | [The table has a version](the_table_has_a_version/README.md) | Whose copy of Unicode is your program actually reading, and what may you write down? | written, 2026-09-06 |
| 9 | [Noncharacters and the private use areas](noncharacters_and_private_use/README.md) | Which code points are reserved forever, and why "reserved" is not "invalid"? | written, 2026-09-08 |
| 10 | [Preparing a string](preparing_a_string/README.md) | Are these two strings the same name, and who decides which differences count? | written, 2026-09-06 |
| 11 | [A code point is not a character](a_code_point_is_not_a_character/README.md) | Why does `len()` still not count what a person calls a character? | written, 2026-09-07 |
| 12 | [Confusables and scripts](confusables_and_scripts/README.md) | Two strings, one picture, different code points — why does no normalization form merge them? | written, 2026-09-06 |
| 13 | [Logical and visual order](logical_and_visual_order/README.md) | Why is the order you store not the order you see, and why is a screenshot not evidence? | stub |
| 14 | [Unicode in identifiers](unicode_in_identifiers/README.md) | Why does `ﬁle = 2` define `file`, and why does Rust refuse to do that? | written, 2026-09-06 |

## The through-line

**The number is settled before the bytes are.** By the end of this chapter every character you can name has one agreed number, its code point, and nothing has been said yet about how that number is written into a file. Keeping *code point* and *byte* apart is most of the subject, and [chapter 3](../03_Encodings/README.md) is where they finally meet.
