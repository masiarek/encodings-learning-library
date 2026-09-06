# Sorting and collation

**Level:** 301 · for anyone who has shipped an alphabetical list

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `sorted()` puts `Łódź` after `Zebra`, and no Polish speaker would — because code point order is not alphabetical order in any language, and which order is right is a property of the *locale*, not of the text.

## What the finished page has to answer

- The demonstration, which needs no argument: a list of Polish names in code point order, in `pl_PL` order, and in `en_US` order — **three different answers**, and the two locales disagree with each other as well as with the code points
- Why: a code point is an index into a table that was never sorted alphabetically, and accented letters were appended to it decades after the unaccented ones
- Multi-level comparison — base letter first, then accent, then case — which is why `Óda` and `Osa` can swap places between two locales that both look "right"
- `locale.strxfrm` and `LC_COLLATE`: how to actually do it in the standard library, and the two traps — it is **global process state**, and `LC_COLLATE` is a separate variable from `LC_CTYPE` ([locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) has the six of them)
- Why the `sort` command is not the answer either — [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md)
- Where the real answer lives: CLDR and ICU, the same locale-data-versus-character-data split the tools chapter meets in `uni`
- Database collations, which is where this bites hardest in practice and which [interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) owes a paragraph to

## The example it will run

**The locale is the hazard.** Which locales exist differs between this Mac and both CI runners, so an example that asks for `pl_PL.UTF-8` will pass here and fail there. Do what [locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) did: probe for candidates, keep the locale *name* out of the recorded output, and record the *relationship* — that code point order and collated order differ, and where. The three-way comparison belongs in a dated fence.

## See also

- [Locale and `LC_CTYPE`](../../06_Terminal/locale_and_lc_ctype/README.md) — six independent variables, and this is a different one
- [`tr` and `sort` work a byte at a time](../../11_Tools/tr_and_sort/README.md) — the tool-level version of the same gap
- [Normalization](../../04_Python/normalization/README.md) — equality has the same shape of problem as ordering
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — where a collation is actually chosen, usually by accident
