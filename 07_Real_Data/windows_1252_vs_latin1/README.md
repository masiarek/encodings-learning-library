# Windows-1252 vs Latin-1

**Level:** 201 · for anyone repairing data

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Windows-1252 and Latin-1 agree on 224 of 256 bytes and disagree on the 32 in `0x80–0x9F`, which is exactly where the euro sign and the smart quotes live — so text that is *almost* fine, with a few odd characters, is usually this pair confused.

## What the finished page has to answer

- The 32-byte table, side by side: Latin-1 has C1 control characters there, 1252 has `€ ‚ ƒ „ … † ‡ ˆ ‰ Š ‹ Œ Ž ‘ ’ “ ” • – — ˜ ™ š › œ ž Ÿ`
- The five holes: `0x81 0x8D 0x8F 0x90 0x9D` are undefined in 1252, and Python's `cp1252` codec raises on them
- The HTML5 rule that says *treat Latin-1 as 1252*, and why browsers have quietly done so for twenty years
- SAP: 1100 vs 1160, and the interface that declared 1100 and sent a `€`
- The recognition trick: a `€` shown as `\x80` or as `Â\x80` tells you which side used which table

## The example it will run

Python: `bytes(range(0x80, 0xA0))` decoded under both tables, `errors='replace'`, side by side; the euro round trip.

## See also

- [Code pages](../../02_Characters/code_pages/README.md)
- [Mojibake round trip](../mojibake_round_trip/README.md)
