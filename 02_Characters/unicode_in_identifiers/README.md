# Unicode in identifiers

**Level:** 301 · deep dive

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Python normalizes your variable names — write `ﬁle = 2` and you have defined `file` — while Rust accepts non-ASCII names and deliberately does *not* fold them, which is [IDNA2003 against IDNA2008](../preparing_a_string/README.md) being argued again in a different room.

## What the finished page has to answer

- [PEP 3131 ↗](https://peps.python.org/pep-3131/): Python 3 identifiers may be non-ASCII, and the compiler **NFKC-normalizes them**, so a ligature and a mathematical italic letter both collapse onto ordinary ASCII names
- Rust's `non_ascii_idents`, stable since 1.53: non-ASCII names compile, normalized to NFC rather than NFKC, and the compiler ships `uncommon_codepoints` / `confusable_idents` / `mixed_script_confusables` lints instead of folding
- [UAX #31 ↗](https://www.unicode.org/reports/tr31/), which is where both languages got their character sets from, and what `XID_Start` / `XID_Continue` mean
- The security story: two identifiers that no reviewer can tell apart in a diff, and which of the two languages' answers catches it
- Why this is the *same* question as the previous chapter's protocol one — which characters may be a name, and who is allowed to decide two names are the same — asked of a compiler instead of a registry
- What it means for a codebase in practice, including the honest answer that most projects should keep identifiers ASCII and put the language in the strings

## The example it will run

Python: `exec` a few assignments whose names are not ASCII and read the resulting namespace keys back — the normalization is visible as a key that was never typed. Rust: a program with non-ASCII bindings that compiles, plus the lint output for a deliberately confusable pair, in a `text` fence if the wording is not stable enough to record.

## See also

- [Preparing a string](../preparing_a_string/README.md) — the same decision, made by a protocol
- [Confusables and scripts](../confusables_and_scripts/README.md) — why the lints exist
- [Normalization](../../04_Python/normalization/README.md) — what NFKC does, and why it is the aggressive one
- [UAX #31, Unicode Identifier and Pattern Syntax ↗](https://www.unicode.org/reports/tr31/)
