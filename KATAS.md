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
| K8 | [Seven ways to blank a file, and the one that leaves the old bytes behind](11_Tools/creating_and_writing_files/README.md#practice) | [`touch`, `: >` and `install`](11_Tools/creating_and_writing_files/README.md) | 201 |
