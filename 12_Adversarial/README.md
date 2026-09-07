# 12_Adversarial — when text is the attack surface

**Level:** 301 · deep dive

Every other chapter in this library asks what text *is*. This one asks what happens when somebody chooses the bytes on purpose.

The reason it is a chapter rather than a warning box is that the bugs are not a miscellany. They are five shapes, they repeat, and once you can name them you find them by reading a design instead of by waiting for an advisory. Nothing here is an attack tool: every page is a failure shape, a program that demonstrates it in a dozen lines, and the one-line rule that closes it.

## The mental model

**A hacker looks at text and does not see text. They see a pipeline of transformations, and they attack the seams between them.**

A string is never *the* string. It is bytes that get decoded, normalised, case-folded, escaped, truncated, re-encoded and finally rendered — by six pieces of code written by different people in different decades. The bug is almost never *inside* one of those steps. It is in the **disagreement between two of them**, and the attacker's whole job is to find an input the two steps read differently.

That is why the questions on this chapter's pages are never "is this input safe". They are:

1. **Who decodes, with which table?**
2. **In what order does that run, relative to the check?**
3. **Is the transformation many-to-one — and if so, who owns the collision?**
4. **Does the value land somewhere a parser is going to look?**
5. **Does the reader see what the machine will do?**

Five questions, five pages.

## The pages

| # | Page | The question it answers | Status |
|---|---|---|---|
| 1 | [Two readers, one byte string](parser_differentials/README.md) | Why does the filter see nothing and the database see a quote? | written, 2026-09-06 |
| 2 | [The check that ran too early](canonicalize_then_check/README.md) | How does a string get *past* a filter and *become* the thing it blocked? | written, 2026-09-06 |
| 3 | [Two people, one account](collisions_by_design/README.md) | Which fold decides that `mıke` and `mike` are the same person? | written, 2026-09-06 |
| 4 | [The byte that means something to somebody else](in_band_signals/README.md) | Why is one NUL worth a valid certificate for a domain you do not own? | written, 2026-09-06 |
| 5 | [What you see is not what runs](trojan_source/README.md) | How does source code review differently from how it compiles? | written, 2026-09-06 |

## Three of these you have already met

The library did not avoid this material; it just told it one incident at a time. Read these first if you have not:

| Already written | The move it is an instance of |
|---|---|
| [Overlong sequences](../03_Encodings/overlong_sequences/README.md) | a parser differential — the same character with two byte strings, and the 2001 worm that used it |
| [Validation is a boundary](../03_Encodings/validation_is_a_boundary/README.md) | *where* the decode happens, which is question 2 asked about one verb |
| [Confusables and scripts](../02_Characters/confusables_and_scripts/README.md) | what you see is not what runs, at the level of a single letter |
| [Unicode in identifiers](../02_Characters/unicode_in_identifiers/README.md) | the same, for the names a compiler binds |
| [Preparing a string](../02_Characters/preparing_a_string/README.md) | the standardised answer to question 3, from 2002, and why it was replaced |

## The through-line

**Decode once, canonicalise once, check the canonical form, store the canonical form, and render it as escapes.** Five verbs in one order. Every page in this chapter is one way of getting that order wrong, and the last page is the one where the second reader is a person rather than a program.

The order matters more than the strictness. A pipeline that decodes strictly in three places and disagrees is worse than one that decodes leniently in one place, because the second one cannot be made to contradict itself — and *contradiction*, not leniency, is what an attacker is shopping for.

## What this chapter is not

It is not a list of payloads, and none of these pages will help you attack anything you do not own. Each one is a defect *class* with a fix attached, aimed at the person who has to review a design or a diff. The programs are small on purpose: the failure is always small, which is exactly why it survives review.

Two things are missing on purpose. **Memory safety** — the buffer overflows that start with a string — is a language topic rather than an encoding topic; the string half of it (whose unit is the length?) is on [the byte that means something to somebody else](in_band_signals/README.md), and the rest belongs in a C book. And **best-fit mapping**, the Windows conversion table that turns `＆` into `&` underneath your check, is described on [the check that ran too early](canonicalize_then_check/README.md) but cannot be demonstrated by a program here: it is a Win32 behaviour, and this library's examples run on macOS and Ubuntu.

## See also

- [10_Best_Practices](../10_Best_Practices/README.md) — the same rules, stated positively, for a Monday
- [03_Encodings](../03_Encodings/README.md) — the mechanics every page here depends on
- [11_Tools](../11_Tools/README.md) — the tools that make an encoding decision for you, which is the same problem one layer down
- [Trojan Source ↗](https://trojansource.codes/) — Boucher and Anderson's paper, and the coordinated disclosure that gave a dozen compilers the same lint on the same day
