# Mojibake

**Level:** 101 → 201 · for anyone who has seen Ã©

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Mojibake is bytes decoded under the wrong table — `Ã©` is `C3 A9` read as Latin-1 — and once you can recognise the four common patterns you can name the culprit from the garbage alone.

## What the finished page has to answer

- The recognition table: `Ã©` / `Ã‚Â` (UTF-8 read as Latin-1 or 1252), `é` as `?` (encoded to a table that lacks it), `�` (the replacement character, U+FFFD), `□` (a font gap, not an encoding error at all)
- Double encoding: UTF-8 bytes read as Latin-1 and written out as UTF-8 again — `Ã©` becomes `Ã\u0083Â©`, and how to count the layers
- Reversing it: `s.encode('latin-1').decode('utf-8')` and why it works — Latin-1 is the table that round-trips every byte
- The one that cannot be reversed: `?` means the byte was thrown away at write time
- Where it came from: which side of an interface decoded, under what default, and how to prove it with a hex dump rather than argue

## The example it will run

Python: produce each pattern deliberately from `'café'`, then reverse the reversible ones; shell: the same with `iconv`.

## See also

- [Encode and decode are verbs](../encode_and_decode_are_verbs/README.md)
- [Mojibake round trip](../../07_Real_Data/mojibake_round_trip/README.md)
- [Code pages](../../02_Characters/code_pages/README.md)
