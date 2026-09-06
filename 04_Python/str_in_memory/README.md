# A str in memory

**Level:** 201 · working knowledge

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** A CPython `str` is not stored as UTF-8. It is latin-1, UCS-2 or UCS-4, chosen per string by its **widest** character — so adding one emoji to a long ASCII string can quadruple what it costs.

## What the finished page has to answer

- [PEP 393 ↗](https://peps.python.org/pep-0393/), the flexible string representation: three kinds, picked when the string is built, never mixed within one string
- The consequence that surprises people: cost is set by the widest character, not the average. One `😀` in a million ASCII characters pays for a million four-byte slots.
- Why `len()` and indexing are O(1) in Python and cannot be in Rust — the whole trade [`String` is bytes that promise UTF-8](../../05_Rust/string_is_bytes_that_promise_utf8/README.md) describes, seen from the other side
- The UTF-8 cache hanging off a `str`, and why `sys.getsizeof` can go *down* when the character gets wider
- What this does and does not mean for a program: it is a memory question, never a correctness one — `str` behaves identically whichever kind it is
- The bridge to Rust: `String` is always UTF-8, one representation, and pays for it with byte indices

## The example it will run

**Careful here.** `sys.getsizeof` is CPython-specific, changes between versions, and differs by build — so the numbers may **not** go in an answer key, by the rule [the table has a version](../../02_Characters/the_table_has_a_version/README.md) sets out. Record the *shape* instead: that the size is a step function of the widest code point, that appending one astral character to an ASCII string raises the step, and that the step is unchanged by length. Put actual byte counts in a dated fence.

## See also

- [`str` vs `bytes`](../str_vs_bytes/README.md) — the type distinction this page is the inside of
- [`String` is bytes that promise UTF-8](../../05_Rust/string_is_bytes_that_promise_utf8/README.md) — the other answer to the same problem
- [The table has a version](../../02_Characters/the_table_has_a_version/README.md) — which facts on this page may be recorded
