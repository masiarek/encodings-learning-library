# Encode and decode are verbs

**Level:** 101 · for anyone starting from zero

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** *Encoding* turns code points into bytes and *decoding* turns bytes back into code points, each under a named table — and nearly every bug in this field is one of those two verbs applied with the wrong table, or applied twice.

## What the finished page has to answer

- The vocabulary, fixed once: text / code points / `str` on one side; bytes / `bytes` / `xstring` on the other; an *encoding* is the table that maps between them
- The unicode sandwich: decode at the edge on the way in, work in text, encode at the edge on the way out — and where the edges are (file, socket, database, terminal, RFC)
- What it looks like when a program does neither: bytes stored in a text field, text stored in a byte field, and why both work until the first `é`
- The two error messages, in Python and Rust, read line by line: which byte, which position, which table
- Why `latin-1` decoding never raises and is therefore the wrong tool for detecting anything

## The example it will run

Python: one string, encode under three tables, decode each result under each table — a 3×3 grid of outcomes.

## See also

- [UTF-8 by hand](../utf8_by_hand/README.md)
- [Mojibake](../mojibake/README.md)
- [`str` vs `bytes`](../../04_Python/str_vs_bytes/README.md)
