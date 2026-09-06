# Confusables and scripts

**Level:** 301 · for anyone who accepts a name from a stranger

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Two strings can be different code points, different bytes and the same picture — and no normalization form will merge them, because Cyrillic `а` and Latin `a` are not two spellings of one letter, they are two letters that were drawn by the same hand.

## What the finished page has to answer

- The pair itself: `U+0061 LATIN SMALL LETTER A` and `U+0430 CYRILLIC SMALL LETTER A`, one glyph, two numbers, two different UTF-8 byte strings
- **Why normalization is not the fix** — NFC, NFD, NFKC, NFKD and `casefold()` all leave the Cyrillic letter exactly where it was, and they are right to. This is the misconception the page exists to kill; [normalization](../../04_Python/normalization/README.md) reconciles spellings of the *same* character and these are not that.
- Why [preparing a string](../preparing_a_string/README.md) does not fix it either, and says so: RFC 3454 §9.1 declines to map look-alikes together, because the answer depends on the font
- What `apple.com` with one Cyrillic letter encodes to, and why a browser shows the `xn--` form back to you rather than the pretty one
- **The standard library has no `script()`** — `unicodedata` exposes category, bidirectional, combining, east-asian width and no script property at all. So how do you detect a mixed-script string? The first word of `unicodedata.name()` is the poor man's answer, and it is *safe to record* for the reason [the table has a version](../the_table_has_a_version/README.md) gives: a name never changes.
- What the real answer is — [UTS #39 ↗](https://www.unicode.org/reports/tr39/), confusable-detection and mixed-script restriction — and who actually applies it (registries and browsers, not your code)
- The invisibles are the other half of the same problem, and [preparing a string](../preparing_a_string/README.md) already deletes them; this page is about characters that are *visible* and still lie

## The example it will run

Python: a handful of same-picture pairs with their code points and bytes; the four normalization forms and casefold applied to each, all leaving them distinct; and a mixed-script detector built from `name()` prefixes, run over a short list of domains. Every value in it is a name or a code point, so all of it may be recorded.

## See also

- [Preparing a string](../preparing_a_string/README.md) — the step that handles the invisible half, and declines this half in writing
- [Normalization](../../04_Python/normalization/README.md) — what it does reconcile, and why that is a different question
- [`uni` — the character's name](../../11_Tools/uni/README.md) — `uni identify` is the fastest end to a "why doesn't this match" argument
- [Unicode Security Mechanisms (UTS #39) ↗](https://www.unicode.org/reports/tr39/)
