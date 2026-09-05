# Normalization

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Two strings that print identically can be different code points, and `unicodedata.normalize('NFC', s)` is the step that belongs before any comparison, dictionary lookup or filename check.

## What the finished page has to answer

- `'é' == 'é'` can be `False`: `U+00E9` versus `U+0065 U+0301`, and where each comes from (a keyboard vs a Mac filesystem)
- NFC / NFD / NFKC / NFKD: composed, decomposed, and the *compatibility* forms that turn `ﬁ` into `fi` and `²` into `2`
- Why macOS filenames are NFD and Windows filenames are whatever you typed — and what `os.listdir` hands you on each
- `casefold()` vs `lower()`: `'ß'.casefold()` is `'ss'`, and why that is the comparison you want
- Polish: which letters have a decomposed form (all of them), and what a sort key looks like after NFD

## The example it will run

Python: the same word four ways, `==` on every pair, then `normalize` and `==` again; `casefold` on the German and Turkish cases.

## See also

- [A code point is not a character](../../02_Characters/a_code_point_is_not_a_character/README.md)
- [Unicode code points](../../02_Characters/unicode_code_points/README.md)
