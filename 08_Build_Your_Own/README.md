# 08_Build_Your_Own — invent an encoding, then implement it

**Level:** 201 → 301 · a project, not a lesson

The fastest way to stop confusing *code point* with *byte* is to have designed both yourself. This chapter is one project: a deliberately silly text format with its own character set, its own variable-length encoding on 3-bit units, and its own container — specified precisely enough that you can implement it in Rust and know when you are done, because a Python reference implementation prints every expected result.

| # | Page | What it is | Status |
|---|---|---|---|
| 1 | [Tribit — the specification](tribit/README.md) | The four layers, the rules, the test vectors, and a Rust API sketch | written |

It is also the answer to a question worth asking first: *is re-inventing this the wrong approach?* It is the classic right one — every serious treatment of UTF-8 ends with "now write an encoder" — provided two things stay separate that beginners merge: **your** code points and Unicode's, and the *unit encoding* and the *container*. The spec keeps all four apart on purpose.
