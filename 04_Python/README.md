# 04_Python — `str`, `bytes`, and the boundary between them

**Level:** 101 → 201 · for Python programmers

Python draws the text/bytes line as a type boundary and refuses to cross it silently. These lessons are what you already know about `str` and `bytes`, reorganised around chapters 2 and 3, plus the four places the boundary is easy to get wrong: `open()`, the `errors` policy, normalization, and binary formats.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [`str` vs `bytes`](str_vs_bytes/README.md) | Which is which, and why will Python not concatenate them? | stub |
| 2 | [Encode, decode and errors](encode_decode_and_errors/README.md) | What do the five `errors=` policies each throw away? | stub |
| 3 | [Opening a file](opening_a_file/README.md) | Why is `open(path)` a bet, and what is the portable call? | stub |
| 4 | [Normalization](normalization/README.md) | Why can `'é' == 'é'` be `False`, and what do I run before comparing? | written, 2026-09-06 |
| 5 | [Bytes, hex and int](bytes_hex_and_int/README.md) | How do I read a binary format by hand with four conversions? | stub |
| 6 | [A str in memory](str_in_memory/README.md) | Why can one emoji quadruple what a string costs, and why is `len()` still O(1)? | stub |
