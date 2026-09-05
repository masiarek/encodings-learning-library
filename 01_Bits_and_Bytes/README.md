# 01_Bits_and_Bytes — the unit everything is measured in

**Level:** 101 · for anyone starting from zero

Three lessons, and after them a hex dump is readable. Each answers a question the one before it raises.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [A byte is eight bits](a_byte_is_eight_bits/README.md) | What is the thing a file is made of, and why does it hold 0..255 and nothing else? | written |
| 2 | [Hex is a shorthand](hex_is_a_shorthand/README.md) | Why does every tool show a byte as two characters from `0`–`F`, and why is `41` on screen not `'41'` in the file? | written |
| 3 | [Reading a hex dump](reading_a_hex_dump/README.md) | What are the three columns of `xxd`, and how do I check a claim about text against the bytes? | written |

## The through-line

**A byte means nothing on its own.** `0100 0001` is 65, or `A`, or a quarter of a float, and the byte does not know which. Every later chapter is about the *agreements* that give bytes meaning — ASCII, the code pages, Unicode, UTF-8 — and this chapter is about seeing the bytes before any agreement is applied. That is the skill: when text looks wrong, dump the bytes, and only then argue about whose reading was at fault.

## A note on the code

Every lesson here has a Python, a Rust, and a shell example of the same idea. They are illustrations. Python shows the idea in the fewest lines; the shell shows it on the actual bytes of an actual pipe; Rust shows it with the width and the reading written into the type, so the compiler holds the line the other two leave to you.
