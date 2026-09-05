# 03_Encodings — how a number becomes bytes

**Level:** 101 → 201 · the chapter this library is built around

A code point is a number, and a file is bytes. An **encoding** is the rule for writing one as the other, and there are several rules. This chapter is UTF-8 done by hand, then the other rules you will meet, then what it looks like when a file is read under the wrong one.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [UTF-8 by hand](utf8_by_hand/README.md) | How does `U+00E9` become `C3 A9`, with a pencil? | stub |
| 2 | [UTF-16 and surrogates](utf16_and_surrogates/README.md) | Why do Windows, Java, JavaScript and SAP say an emoji is two characters long? | stub |
| 3 | [Byte order and the BOM](byte_order_and_bom/README.md) | Which byte of a two-byte number comes first, and what are `EF BB BF` doing at the top of my CSV? | stub |
| 4 | [Encode and decode are verbs](encode_and_decode_are_verbs/README.md) | What exactly are the two operations, and where in a program do they belong? | stub |
| 5 | [Mojibake](mojibake/README.md) | Why `Ã©`, and how do I name the culprit from the garbage alone? | stub |

## The through-line

**Every encoding bug is one of two verbs with the wrong table.** Once UTF-8 is something you can do by hand, mojibake stops being mysterious: it is bytes that were *encoded* under one table and *decoded* under another, and you can read which two from the shape of the damage.
