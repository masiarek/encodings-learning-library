# UTF-8 everywhere

**Level:** 201 · for anyone starting from zero

**One line:** Five rules that hold in every language: bytes at the edges and text in the middle; the encoding comes from the protocol, never from the bytes; `errors=` is a decision; normalize before comparing; and "length" has three answers, so say which one you meant.

## The sandwich

Every encoding bug is the same bug. Bytes arrive, and somewhere in the middle of the program something treats them as text — or the reverse. The fix has a name, from Ned Batchelder's talk: the **Unicode sandwich**.

```text
        bytes in   ->  DECODE  ->  text  ->  ENCODE  ->  bytes out
        (network,      (once,      (all       (once,      (file,
         file, DB)      here)      your        here)       socket,
                                   logic)                  DB)
```

The filling is `str` (Python), `String`/`&str` (Rust), `string` (ABAP, Java, C#). It never contains bytes, never contains an encoding name, and never contains a decision about either. The two slices of bread are the only places where the word "utf-8" appears in your code, and they are the only two places anything can go wrong.

That is not a style preference. It is what makes the bug *findable*: if there are exactly two conversion points, a wrong character has exactly two suspects.

## The encoding comes from the protocol

Bytes do not carry their encoding. There is no header, no marker, no reliable signature — [that is the whole of chapter 9](../../09_History/from_telegraph_to_unicode/README.md). So "what encoding is this file?" is never answered by looking at the file. It is answered by:

- the **HTTP** `Content-Type: text/html; charset=utf-8` header,
- the **database** connection's client encoding,
- the **interface specification** you were handed with the file,
- the **XML declaration** or the `<meta charset>`,
- and failing all of those, by **asking the person who sent it**.

Detection libraries (`chardet`, `charset-normalizer`, `file --mime-encoding`) are statistics. They are right most of the time, which is worse than being wrong all of the time, because the failures are rare enough to reach production. Use one to *investigate* a mystery file, never as the encoding in a pipeline.

The corollary is about your own defaults: `open(path)` with no `encoding=` uses whatever the machine's locale says, so the same script reads correctly on your Mac and silently wrongly on a Windows box. Name the encoding even when it is already the default — see [Python text in practice](../python_text_in_practice/README.md).

## `errors=` is a policy, not an escape hatch

Every decoder takes an error policy, and reaching for one is a decision about *evidence*:

| Policy | What it does | When |
|---|---|---|
| `strict` | raise | data you own. The default, and usually right |
| `surrogateescape` | park bad bytes in surrogates, **reversibly** | carrying somebody else's bytes through untouched |
| `replace` | bad bytes become `U+FFFD` | a log line a human will read, and nothing else |
| `backslashreplace` | bad bytes become `\xNN` text | a diagnostic you want to paste into a bug report |
| `ignore` | bad bytes vanish | never. It destroys the evidence *and* the data |

Only `surrogateescape` round-trips. That is the one that lets you read a directory listing containing a filename nobody can decode, sort it, and rename it — without ever having to understand it.

## Normalize, then compare

`é` has two spellings: one code point, or `e` plus a combining accent. They look identical, they *are* the same character, and they are not equal. A macOS filename, a Linux one, a form field, a database row — the same word can arrive both ways in one afternoon.

**Normalize to NFC as text comes in**, then compare, hash, index and store the normalized form. Do not normalize at comparison time in one place and forget in another; that produces a system where `a == b` depends on which function asked.

For caseless comparison the operation is **casefold**, not lowercase. `'Straße'.casefold()` is `'strasse'` — one letter became two, which is why case conversion is not a per-character operation and why `.lower()` on both sides is not enough.

And [NFKC](../python_text_in_practice/README.md) is the *aggressive* normalization: it folds `ﬁ` to `fi` and fullwidth `１２３` to `123`. Right for a search index or a username uniqueness check; wrong for text you will store and hand back.

## "Length" has three answers

```text
   "café" (decomposed)      6 bytes    5 code points    4 things a person sees
```

- **Bytes** — what a `VARCHAR(50)`, a fixed-width field, a wire limit and `wc -c` count.
- **Code points** — what `len()` gives you in Python, `.chars().count()` in Rust.
- **Grapheme clusters** — what a person means by "characters", what a cursor moves over, and what needs a library in every language including Python and Rust.

A truncation bug is almost always someone answering with the wrong one of the three. Say which you meant, in the variable name if nowhere else.

## In Python

Python is the shortest place to show all five, because it draws the text/bytes line as a type you can print. The rules are not Python's.

<!-- output:utf8_everywhere_py -->
*Verified output of [`utf8_everywhere_py.py`](examples/utf8_everywhere_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SANDWICH: DECODE AT THE EDGE, WORK IN TEXT, ENCODE AT THE EDGE
------------------------------------------------------------------------
   in   (bytes) b'name,city\r\n\xc5\x81\xc3\xb3d\xc5\xba,PL\r\n'
   work (str)   [['name', 'city'], ['Łódź', 'PL']]
   out  (bytes) b'name;city\n\xc5\x81\xc3\xb3d\xc5\xba;PL'
   Bytes at the two ends, text in the middle, and NOTHING in the middle
   that has to know what an encoding is. Every encoding bug you will
   ever have is a program that let bytes leak into the filling.

2. THE ENCODING IS NOT A GUESS — IT COMES FROM THE PROTOCOL
------------------------------------------------------------------------
   sys.flags.utf8_mode        = 1
   locale.getencoding() is UTF-8? False
   (The NAME is not printed on purpose: this run is pinned to LC_ALL=C,
   where macOS calls it 'US-ASCII' and Linux calls it 'ANSI_X3.4-1968'.
   Even the name of the fallback encoding is machine-dependent.)

   That fallback is what open() uses when you do not pass encoding=.
   On a Windows box it is 'cp1252' — which is how the same script reads
   a file correctly here and silently wrongly there.

   So: open(path, encoding='utf-8'), always, even when it is the default.
   Python 3.15 makes UTF-8 the default (PEP 686) and the argument STILL
   belongs in the call, because it documents which side of the boundary
   the file is on. The encoding comes from the HTTP header, the database
   connection, the interface spec — never from the bytes themselves.

3. errors= IS A POLICY DECISION. MAKE IT ON PURPOSE.
------------------------------------------------------------------------
   the bytes: b'Sales: caf\xe9'
     errors=strict            -> UnicodeDecodeError at byte 10
     errors=replace           -> 'Sales: caf�'
     errors=ignore            -> 'Sales: caf'
     errors=backslashreplace  -> 'Sales: caf\\xe9'
     errors=surrogateescape   -> 'Sales: caf\udce9'

   Only ONE of them can be undone: surrogateescape round-trips.
     decode then encode == the original bytes: True
   Use strict for data you own, surrogateescape when you must carry
   somebody else's bytes through unharmed, replace only for a log line
   a human will read. Never ignore: it deletes evidence silently.

4. COMPARE AFTER NORMALIZING, NOT BEFORE
------------------------------------------------------------------------
   composed   'łódź'  4 code points  c5 82 c3 b3 64 c5 ba
   decomposed 'łódź'  6 code points  c5 82 6f cc 81 64 7a cc 81
   composed == decomposed                : False
   NFC(composed) == NFC(decomposed)      : True
   Same word, same screen, different bytes — a macOS filename and a
   Linux one, or a form field and a database row. Normalize to NFC on
   the way IN and compare after that; do not normalize at compare time
   in one place and forget in the other.

   Caseless comparison is casefold(), not lower():
     'Straße'     lower 'straße'      casefold 'strasse'     upper 'STRASSE'
     'İstanbul'   lower 'i̇stanbul'   casefold 'i̇stanbul'   upper 'İSTANBUL'
   Note the lengths change. 'ß'.upper() is two letters, so a case
   conversion is not a per-character operation and never was.

5. 'LENGTH' HAS THREE ANSWERS. SAY WHICH ONE YOU MEANT.
------------------------------------------------------------------------
   text            bytes  code points  graphemes
   Łódź                7            4          4
   café                5            4          4
   café (NFD)          6            5          4
   👨‍👩‍👧           18            5          1
   (the last column is counted BY EYE — Python's standard library has no
    grapheme segmenter, which is the point of the paragraph below)
   The bytes column is what a VARCHAR(n) and a fixed-width field count.
   The code-point column is what len() gives you. The last column needs
   grapheme-cluster segmentation, which is a library in every language
   including this one. Three different questions — pick one deliberately.

6. TWO DEFAULTS WORTH CHANGING ON THE WAY OUT
------------------------------------------------------------------------
   json.dumps(...)                     -> {"city": "\u0141\u00f3d\u017a"}
   json.dumps(..., ensure_ascii=False) -> {"city": "Łódź"}
   Both are valid JSON and both survive the trip. The first is ASCII-safe
   escaping from an era when the channel might not be 8-bit clean; today
   it mostly makes payloads bigger and logs unreadable. JSON is UTF-8 by
   RFC 8259, so ensure_ascii=False is the honest default now.

   And the BOM: read Excel's CSVs with encoding='utf-8-sig', which eats a
   leading BOM if there is one; write with 'utf-8' so you never add one.
     first bytes from Excel : ef bb bf 69 64 2c
     read as utf-8          : '\ufeffid'  <- BOM stuck to the header
     read as utf-8-sig      : 'id'
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** The sandwich is enforced by the type system already: `str` and `bytes` do not concatenate, do not compare equal, and do not silently coerce. That refusal *is* the rule — Python 2 guessed here, with ASCII, and the resulting `UnicodeDecodeError`-at-3am is why Python 3's split exists. The two places to be deliberate are `open(..., encoding=...)` and any `.encode()` / `.decode()` you write by hand; if one appears in the middle of your business logic, that is the sandwich leaking.

**ABAP.** The sandwich is the same shape, with different bread: `xstring` outside, `string` inside, and `cl_abap_codepage=>convert_from( source = raw codepage = 'UTF-8' )` as the decode. The two rules that need most attention in SAP work are the third and the fifth. `errors=` has no direct equivalent — the conversion classes raise, and a `TRY … CATCH cx_sy_conversion_codepage` around the boundary is the honest version of `strict`. And "length" is where fixed-width interface files get you: `strlen` counts characters, `xstrlen` counts bytes, and a legacy partner's "50-character field" is nearly always 50 *bytes*. On a Unicode system those differ for every Polish, Greek or Chinese name in the file. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 10_Best_Practices/utf8_everywhere/examples
python3 utf8_everywhere_py.py
```

Without the machine: a partner sends a fixed-width file where a name field is "30 characters". Which of the three lengths did they mean, what happens to `Łódź` under each reading, and what is the one question you send back? Then: you have a user database where `José` was entered from a Mac and searched for from a browser and the search misses. Which rule on this page was broken, and at which end?

## See also

- [Rust strings in practice](../rust_strings_in_practice/README.md) — the same rules with the compiler enforcing them
- [Python text in practice](../python_text_in_practice/README.md) — `open()`, the interpreter switches, and filenames
- [Why UTF-8 won](../../09_History/why_utf8_won/README.md) — where rule 1 and rule 4 come from
- [Mojibake](../../03_Encodings/mojibake/README.md) — what rule 2 prevents, in detail
- [Normalization](../../04_Python/normalization/README.md) — NFC, NFD, NFKC up close
- [Pragmatic Unicode ↗](https://nedbatchelder.com/text/unipain.html) — Ned Batchelder; the talk the sandwich comes from
