# Anki: hexadecimal

**Level:** 101 → 201 · for anyone who reads bytes

**One line:** One spaced-repetition deck — 22 cards on hex, from *why sixteen* up to the two readings of one hex string — whose every snippet was compiled and run by `verify.py` in four languages before the deck was written, so a card cannot claim output no program produced.

## Import

Anki → **File → Import** → pick `Encodings_Hex.txt` → Import. Nothing to configure: the header lines set the deck, the note type and the tags column.

| file | deck | cards |
|---|---|---|
| `Encodings_Hex.txt` | `Encodings::Hex` | 22 |

Re-importing is safe and idempotent: Anki matches on the first field, so an edited card updates in place and your review history survives.

## Where the deck came from, and the one answer it changes

It started as a seven-question kata Adam had written — the multiple-choice sort — and every question is here. But a multiple-choice question and a flashcard train different acts: recognising the right option among four is not retrieving the answer from nothing, and only the second one is what a card can practise. So each question became a card that asks you to **produce** something, and then the traps behind it became cards too.

| the kata asked | the card asks | id |
|---|---|---|
| What does `0x` represent? | Write 195 in all four bases; what is the rule behind the three prefixes? | `hex_four_bases` |
| What does `\x` represent in a string? | `0x41` and `\x41` both name 65 — what is the difference? | `hex_0x_versus_backslash_x` |
| How many unique characters does hex use? | Where does the 16 come from — and why not ten symbols, or eight? | `hex_why_sixteen` |
| What is the value of `A`? | Say the sixteen symbols in order; what is `A`? `F`? | `hex_af_values` |
| What is `0xFF` in decimal? | `0xFF` in decimal, in bits, and why is it the one everyone remembers? | `hex_ff_and_100` |
| Which escape gives a byte in hex? | (same card as `\x` above, from the other side) | `hex_0x_versus_backslash_x` |
| **What is the purpose of hexadecimal?** | **Where does the 16 come from?** — see below | `hex_why_sixteen` |

**The last one is the answer that changed.** The kata's key says *"to represent large numbers with fewer digits."* That is true and it is not the reason, and the deck says so on the card, because the wrong reason leads you to the wrong instincts about padding, dumps and field widths.

Compactness cannot be what picks hex, for a one-line reason: **decimal is also far shorter than binary, and decimal is useless here.** `65`, `200` and `255` look nothing like their bits; a byte in decimal is one, two or three characters wide, so a row of them has no rhythm; and no dump tool has ever printed one. If shortness were the criterion, base 36 would beat hex and nobody uses it.

What picks hex is that **16 = 2⁴, so one digit is exactly four bits and a byte is *always* two digits**. That single property is why a hex dump is a grid, why the seam between two bytes never falls inside a digit, and why you can read the bits off the digit without arithmetic. It is also why octal lost: three does not divide eight. [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) is the page that argues it in full, and the deck's `hex_why_not_octal` and `hex_octal_still_fits` are the two halves of it — including the half that keeps octal honest, since 9 ÷ 3 = 3 exactly and `0o755` says *rwx r-x r-x* out loud where `0x1ED` says nothing.

Of the kata's other six answers, all six are right as given.

Two of those six — *how many symbols* and *what is `A`* — got their own lesson the same day the deck was built: [Counting in hexadecimal](../../01_Bits_and_Bytes/counting_in_hex/README.md), which makes the point the kata's phrasing hides, that `A` is a **digit worth ten** and not a letter. Those two cards link there rather than here.

## What else is in the deck

The kata's seven questions are the first rung. The rest of the deck is the material a person who can answer all seven still gets wrong, and it is mostly one idea seen from several sides: **the picture is not the thing.**

- **`41` on screen is not `'41'` in the file.** The text is two bytes, `0x34` and `0x31`; the file holds one. `bytes.fromhex` and `.hex()` are the two directions, and the confusion is invisible because both readings look like "hex".
- **`\x` does not have one meaning.** In a Python `str` it names a *code point*, so `"\xc3".encode()` is **two** bytes; in a `bytes` literal it names the byte. Rust refuses the ambiguity outright above `\x7F` and makes you pick. C's `\x` is *greedy* and has no width at all, which is how `"\x7f"` becomes DEL when you meant BEL-then-`f`.
- **The prefix is for humans, and every parser decides separately whether to humour you.** `"0x41"` parses in Python, C and bash; Rust's `from_str_radix` refuses it.
- **`int(s, 16)` succeeding is not a validation.** It returns 65 for `٤١` — two ARABIC-INDIC digits — so a field "checked" that way accepts characters your regex and your database reject.
- **`0041` is two different objects**, and the string does not say which. As a number, leading zeros are noise; as bytes, the leading zero *is* a NUL byte and the width is the field.
- **An odd number of digits: fine, fatal, or silently halved.** `int` says 291, `bytes.fromhex` raises, `xxd -r -p` drops the trailing nibble and exits 0.
- **`{:02x}`, not `{:x}`.** A byte is always two digits; the padding is what keeps the output reversible.

Four of the twenty-two are *predict the compiler* cards rather than *predict the output*, including one that must **not** compile — Rust's `"\xC3"`, whose error message is itself the answer key, since rustc prints both correct alternatives as help lines.

Each back ends with a **Python / Rust / ABAP bridge** where one is honest, and a link to the lesson on the site.

## Regenerating

```bash
python3 verify.py cards_hex
python3 build.py
```

`verify.py` runs each snippet in its own language — `python3 -I`, bare `rustc --edition 2024`, `cc -std=c11 -Wall -Wextra`, `bash` — under the library's own fixed environment (`LC_ALL=C`, `LANG=C`, `PYTHONUTF8=1`), and requires an exact stdout match. A card carrying `fails_msg=` must **not** compile, with that text in stderr. That is the same contract [`tools/run_examples.py`](../../tools/run_examples.py) holds every lesson page to.

`build.py` asks each toolchain for its own version at build time rather than carrying a hand-typed one, because a version string nobody re-checks is exactly the kind of claim this deck exists to refuse.

Edit a card in `cards_hex.py`, run both commands, re-import. **Never hand-edit `Encodings_Hex.txt`** — it is generated.

Two things the gate caught while this deck was written, both of which read as correct prose: a `\x` snippet whose escapes Python had eaten before the file was ever run (the deck's own subject, one level up — which is why every card string containing a backslash is a `r"raw"` literal, and there is a comment at the top of `cards_hex.py` saying so), and a C snippet that demonstrated greedy escapes by going out of range, where the diagnostic rather than the value was the honest lesson.

## See also

- [Counting in hexadecimal](../../01_Bits_and_Bytes/counting_in_hex/README.md) — the page behind `hex_af_values` and `hex_counting_carry`: A–F are digits, and the wheel rolls over after `F`
- [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) — the 101 page the first half of the deck is drawn from
- [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) — the 201 page behind `hex_two_readings`, `hex_odd_length` and `hex_int_is_not_validation`
- [Reading a hex dump](../../01_Bits_and_Bytes/reading_a_hex_dump/README.md) — where you read these two-digit pairs sixteen at a time
- [Writing a code point](../../02_Characters/writing_a_code_point/README.md) — the escape cards' other half: one number, five spellings
- [The Rust library's Anki decks ↗](https://github.com/masiarek/rust-learning-library/tree/master/10_Resources/anki) — five decks built the same way, and where this one's `verify.py` / `build.py` came from
