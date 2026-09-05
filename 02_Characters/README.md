# 02_Characters — a character is a number by agreement

**Level:** 101 → 201 · for anyone starting from zero

A byte is a number. Text is characters. The only bridge between them is a **table**, and this chapter is the history of that table getting bigger: 128 entries, then 256 with everybody's own second half, then a million with one numbering for all of them.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [A character is a number](a_character_is_a_number/README.md) | Who decided 65 means `A`, and why are the digits and the two alphabets placed where they are? | written |
| 2 | [Control characters](control_characters/README.md) | What are the first 32, and which three still matter every day? | stub |
| 3 | [Code pages](code_pages/README.md) | What did everybody do with the unclaimed 128, and why does `0xE9` have six meanings? | stub |
| 4 | [Unicode code points](unicode_code_points/README.md) | What is `U+00E9`, and why is it a number rather than a byte? | stub |
| 5 | [A code point is not a character](a_code_point_is_not_a_character/README.md) | Why does `len()` still not count what a person calls a character? | stub |

## The through-line

**The number is settled before the bytes are.** By the end of this chapter every character you can name has one agreed number, its code point, and nothing has been said yet about how that number is written into a file. Keeping *code point* and *byte* apart is most of the subject, and chapter 3 is where they finally meet.
