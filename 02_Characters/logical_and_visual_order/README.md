# Logical and visual order

**Level:** 301 · deep dive

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Text is stored in the order it is *read* and drawn in the order it is *seen*, and for Hebrew and Arabic those are not the same order — so the screen is a rendering of your string, never evidence about it.

## What the finished page has to answer

- Logical order vs visual order, and the rule that all Unicode text is stored logically — the bytes are in reading order even when the screen is not
- The [Unicode Bidirectional Algorithm ↗](https://www.unicode.org/reports/tr9/) in outline: every character has a direction class, and the display order is computed from the sequence, not stored in it
- Why `len()`, slicing and `==` are completely unaffected — they read the stored order, which is why a bidi bug never shows up in a test that compares strings
- The explicit overrides (`U+202D` LRO, `U+202E` RLO, `U+2069` PDI and friends) and what they let someone do to a line of source code — the [Trojan Source ↗](https://trojansource.codes/) class of bug
- Why [preparing a string](../preparing_a_string/README.md)'s bidi step is the protocol-level answer to the same problem: it refuses the shapes whose display is ambiguous instead of trying to render them
- The practical rule for this library and for bug reports: **a screenshot of a terminal is not evidence about a string.** Print the code points.

## The example it will run

Python: a short mixed-direction string printed three ways — its code points in stored order, each character's `unicodedata.bidirectional()` class, and the same string with an RLO in it — so a reader can see that the sequence never changed while the line did. **The rendered line itself cannot be an answer key**: what a terminal draws is the terminal's, the same trap [inspecting a file](../../06_Terminal/inspecting_a_file/README.md) records for `od -a`. Record the classes and the code points; put any rendered line in a dated fence, or leave it out.

## See also

- [Preparing a string](../preparing_a_string/README.md) — RFC 3454 §6, the shape rule that refuses ambiguous strings
- [Confusables and scripts](../confusables_and_scripts/README.md) — the other way text lies about itself
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — you are always reading the last program in the pipe
- [UAX #9, the Unicode Bidirectional Algorithm ↗](https://www.unicode.org/reports/tr9/)
