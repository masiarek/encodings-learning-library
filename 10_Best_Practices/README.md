# 10_Best_Practices — what to actually do

**Level:** 201 → 301 · for anyone starting from zero

Everything else in this library is *how it works*. This chapter is **what to do on Monday**, and it is short on purpose, because the modern answer really is small.

| # | Lesson | The question it answers | Status |
|---|---|---|---|
| 1 | [UTF-8 everywhere](utf8_everywhere/README.md) | The five rules that are true in every language — the sandwich, the protocol, `errors=`, normalizing, and the three meanings of "length" | written |
| 2 | [Rust strings in practice](rust_strings_in_practice/README.md) | Which type to take, which length to ask for, when to say `&[u8]`, and the three std methods that are ASCII-only on purpose | written |
| 3 | [Python text in practice](python_text_in_practice/README.md) | `encoding=` on every `open()`, the two interpreter switches, filenames that are not text, and what changes in Python 3.15 | written |
| 4 | [Interfaces and storage](interfaces_and_storage/README.md) | HTTP, JSON, CSV, databases and SAP — where the encoding is declared, per protocol | stub |

## The whole chapter in nine lines

1. **UTF-8 for everything you write.** Files, wire formats, source code, database columns, filenames. There is no longer a second candidate.
2. **No BOM.** Write plain UTF-8; read with something that tolerates a BOM if Excel is upstream.
3. **Decode at the edge, encode at the edge, keep text in the middle.** The [Unicode sandwich](utf8_everywhere/README.md). Every encoding bug is bytes leaking into the filling.
4. **The encoding comes from the protocol, never from the bytes.** The HTTP header, the interface spec, the connection setting. Detection libraries are a last resort, and they guess.
5. **Say `errors=` on purpose.** `strict` for data you own, `surrogateescape` to carry somebody else's bytes through unharmed, `replace` only for a log line. Never `ignore`.
6. **Normalize to NFC on the way in**, then compare. Casefold, don't lowercase, for caseless matching.
7. **Say which length you mean.** Bytes for storage and wire limits, code points for `len()`, grapheme clusters for anything a person counts — three different questions.
8. **Validate, don't assume.** UTF-8's structure lets a decoder reject a wrong-table file; that is a feature to use, not an inconvenience to route around with `errors='ignore'`.
9. **Filenames and command-line arguments are not text.** They are bytes on Unix and possibly-invalid UTF-16 on Windows. Use the platform's escape hatch rather than `.encode('utf-8')`.

The three written pages are those nine lines with the failures shown. [Chapter 9](../09_History/README.md) is why they are the rules rather than one option among several.

## Where this is going to change

**Python 3.15 makes UTF-8 mode the default** ([PEP 686 ↗](https://peps.python.org/pep-0686/), Final). That removes the single most common Python encoding bug — the script that reads correctly on the developer's Mac and wrongly on a colleague's Windows box — and it is the biggest change to this subject in fifteen years. Until then, and after it, `encoding='utf-8'` still belongs in the call.

Nothing else on this page is expected to move. UTF-8 passed 99% of the web in 2026 and the remaining work is legacy interfaces, not new formats.
