# 01_Bits_and_Bytes — the unit everything is measured in

**Level:** 101 · for anyone starting from zero

Nine lessons, and after them a hex dump is readable — and you know which parts of it are the file, which are the tool, which of two things a run of hex digits is, which end of a wide value comes first, and how to type a number back into a tool that never says which base it reads. Each answers a question the one before it raises.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [A byte is eight bits](a_byte_is_eight_bits/README.md) | What is the thing a file is made of, and why does it hold 0..255 and nothing else? | written |
| 2 | [Counting in hexadecimal](counting_in_hex/README.md) | Those values are written with letters in them — what is `1A`, and why does counting go `19`, `1A` and not `19`, `20`? | written, 2026-09-07 |
| 3 | [Hex is a shorthand](hex_is_a_shorthand/README.md) | Why does every tool show a byte as two characters from `0`–`F`, and why is `41` on screen not `'41'` in the file? | written |
| 4 | [Reading a hex dump](reading_a_hex_dump/README.md) | What are the three columns of `xxd`, and how do I check a claim about text against the bytes? | written |
| 5 | [Grouping is a choice](grouping_is_a_choice/README.md) | The dump put spaces every two bytes — who decided that, and what does a different width claim about the file? | written |
| 6 | [Hex: a number, or a picture of bytes](hex_number_or_bytes/README.md) | `0041` — is that 65, or two bytes? And why do four languages disagree about what a hex digit is? | written, 2026-09-07 |
| 7 | [Arithmetic has its own width](arithmetic_has_its_own_width/README.md) | The byte holds 0..255 — so why is `255 << 2` equal to 1020 in three of these four languages? | written, 2026-09-07 |
| 8 | [The bytes do not say which end](which_end_comes_first/README.md) | A value too big for one byte needs several — so which of them is the big one, and why do six dump commands give three different answers? | written, 2026-09-12 |
| 9 | [Which base did you mean?](which_base_did_you_mean/README.md) | I have the value — how do I tell a tool which base I typed it in, and what does it assume when I do not? | written, 2026-09-12 |

## The through-line

**A byte means nothing on its own.** `0100 0001` is 65, or `A`, or a quarter of a float, and the byte does not know which. Every later chapter is about the *agreements* that give bytes meaning — [ASCII](../02_Characters/a_character_is_a_number/README.md), [the code pages](../02_Characters/code_pages/README.md), [Unicode](../02_Characters/unicode_code_points/README.md), [UTF-8](../03_Encodings/utf8_by_hand/README.md) — and this chapter is about seeing the bytes before any agreement is applied. That is the skill: when text looks wrong, dump the bytes, and only then argue about whose reading was at fault.

## A note on the code

Most lessons here have a Python, a Rust and a shell example of the same idea, and several add a C aside where C is where the behaviour came from. They are illustrations. Python shows the idea in the fewest lines; the shell shows it on the actual bytes of an actual pipe; Rust shows it with the width and the reading written into the type, so the compiler holds the line the other two leave to you; C shows the rule the other three are reacting to. A lesson takes only the ones that show something the others cannot, so two of them are shorter than that: [Reading a hex dump](reading_a_hex_dump/README.md) needs no Rust, and [Which base did you mean?](which_base_did_you_mean/README.md) makes its point in the shell and in one argument to `strtol`.
