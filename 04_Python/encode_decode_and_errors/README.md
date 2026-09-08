# Encode, decode and errors

**Level:** 101 → 201 · for Python programmers

**One line:** `.encode()` and `.decode()` each take a table name and an `errors` policy, and the policy is your decision about what to do with the bytes you cannot explain — `strict` raises, and every other choice throws something away without saying so.

```python
text  = raw.decode("utf-8")                 # bytes -> str, and it can fail
raw   = text.encode("utf-8")                # str -> bytes, and it can fail
text  = raw.decode("utf-8", errors="replace")   # ...unless you say what to do instead
```

This is the page [00_Start_Here](../../00_Start_Here/README.md) points at for the third checkpoint — *explain Python `str` vs `bytes`* — so here is the whole answer in four sentences before anything else. **`str` is a sequence of characters and `bytes` is a sequence of numbers 0–255.** They never mix, and Python will not convert between them behind your back; the only two doors are `.encode()` and `.decode()`. Every door needs a **table** (the codec name), because a character has no bytes until some table says which. And every door can **fail**, because a table is a finite agreement — so the second argument, which almost nobody types, is the one that decides what your program does on the day the data is not what you were promised.

The types themselves are next door in [`str` vs `bytes`](../str_vs_bytes/README.md); the two verbs are in [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md). This page is about the **second argument**.

## The default is a decision

`errors` defaults to `"strict"`, which raises. That is the right default and it is worth being clear that it *is* a default rather than an absence: leaving the argument out is choosing to fail loudly, and every other value is choosing to continue with less than you were given.

The exception it raises is not a complaint, it is a **report** — five attributes, one per clause of the message:

| attribute | on `b"caf\xe9 au lait".decode("utf-8")` |
|---|---|
| `.encoding` | `'utf-8'` — the table that was asked |
| `.object` | the whole input, not a copy of the bad part |
| `.start` / `.end` | `3` / `4` — so `.object[.start:.end]` is `b'\xe9'` |
| `.reason` | `'invalid continuation byte'` — which rule broke |

`UnicodeDecodeError` and `UnicodeEncodeError` are both `ValueError`s, so a bare `except ValueError` already catches them — usually by accident, and usually somewhere that then continues with a variable it never assigned.

## Eight handlers, and the matrix is not symmetrical

Python ships eight named policies. The reflex is to read them as a list of increasing leniency; they are not that. Two of them do not work on `decode` at all, and one of them is not a general escape despite the name:

| handler | decode | encode | what it does |
|---|---|---|---|
| `strict` | ✓ raises | ✓ raises | the default |
| `ignore` | ✓ | ✓ | drops it, silently |
| `replace` | ✓ | ✓ | `U+FFFD` in, **`?`** out — two different markers |
| `backslashreplace` | ✓ | ✓ | `\xe9` / `€` as literal text |
| `xmlcharrefreplace` | **TypeError** | ✓ | `&#8364;` — encode only |
| `namereplace` | **TypeError** | ✓ | `\N{EURO SIGN}` — encode only |
| `surrogateescape` | ✓ | ✓ *its own only* | [the reversible one](../surrogateescape/README.md) |
| `surrogatepass` | surrogates only | surrogates only | for `U+D800–DFFF`, not for bad bytes |

The two `TypeError`s are the sharp edge, because they are the wrong *kind* of exception: a program that carefully catches `UnicodeError` around a `decode` will not catch this one. The reason is honest enough — there is no XML entity, and no Unicode name, for a byte that is not a character — but it means "the eight handlers" is a list of five with three special cases in it.

## Every marker is forgeable

This is the finding the page is built on, and it decides which policy to use.

Each lossy handler looks like it leaves a trace. None of them does — because every marker they insert is a character the input could legitimately have contained:

| handler | `b'caf\xe9'` gives | and so does | which is |
|---|---|---|---|
| `replace` | `'caf�'` | `b'caf\xef\xbf\xbd'` | a real `U+FFFD`, an ordinary character |
| `backslashreplace` | `'caf\\xe9'` | `b'caf\\xe9'` | the four ASCII characters `\ x e 9` |
| `ignore` | `'caf'` | `b'caf'` | a file that just says `caf` |

So none of the three can be undone, and — the part that matters more — none can be **detected**. A `U+FFFD` in your database might be a byte somebody lost in 2019, or it might be what the user typed. The replacement character is not a record of damage; it is a character, and any input can contain it.

`surrogateescape` is the exception, and it is the only one: it round-trips byte-for-byte, because it escapes into a range no valid decode can produce. That is [a page of its own](../surrogateescape/README.md).

## Choosing, which is the actual lesson

<!-- output:encode_decode_and_errors_py -->
*Verified output of [`encode_decode_and_errors_py.py`](examples/encode_decode_and_errors_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. TWO ARGUMENTS, AND THE SECOND ONE HAS A DEFAULT
------------------------------------------------------------------------
     bytes.decode(encoding, errors='strict')
     str.encode(encoding, errors='strict')

   The first names a table. The second names what to do when the table
   has no answer. Leaving it out is not neutrality -- it is a choice,
   and the choice is to raise:

     .decode('utf-8') and .decode('utf-8','strict') raise the
     same exception with the same message:  True

2. THE EXCEPTION IS A REPORT, NOT A COMPLAINT
------------------------------------------------------------------------
     'utf-8' codec can't decode byte 0xe9 in position 3: invalid continuation byte

   Every clause of that sentence is an attribute you can read:

     .encoding  'utf-8'                        the table that was asked
     .object    b'caf\xe9 au lait'             the whole input, not just the bad part
     .start     3                              the offset where it went wrong
     .end       4                              and where the trouble stops
     .reason    'invalid continuation byte'    which rule was broken

     .object[.start:.end]  ->  b'\xe9'

   So a handler for this does not have to guess. And the class is
   a ValueError, which is what a bare `except ValueError` catches:

     UnicodeDecodeError -> UnicodeError -> ValueError -> Exception

   Encoding fails the same way, with a different reason:

     'latin-1' codec can't encode character '\u20ac' in position 3: ordinal not in range(256)
     .reason is 'ordinal not in range(256)' -- Latin-1 has 256 slots and no more,
     and this character's number is 8364.

3. THE HANDLERS, BOTH DIRECTIONS
------------------------------------------------------------------------
   Python registers eight by name. They are not interchangeable and
   they are not symmetrical -- two of them do not work on decode at
   all, and refuse with a TypeError rather than a UnicodeError:

     handler            decode utf-8 of          encode latin-1 of
                        b'caf\xe9 au lait'       '10 \u20ac'
     ------------------------------------------------------------------
     strict             ! UnicodeDecodeError     ! UnicodeEncodeError
     ignore             'caf au lait'            b'10 '
     replace            'caf\ufffd au lait'      b'10 ?'
     backslashreplace   'caf\\xe9 au lait'       b'10 \\u20ac'
     xmlcharrefreplace  ! TypeError              b'10 &#8364;'
     namereplace        ! TypeError              b'10 \\N{EURO SIGN}'
     surrogateescape    'caf\udce9 au lait'      ! UnicodeEncodeError
     surrogatepass      ! UnicodeDecodeError     ! UnicodeEncodeError

   Three things to read off it. `xmlcharrefreplace` and `namereplace`
   are ENCODE-ONLY: there is no sensible XML entity for a byte that is
   not a character. `surrogatepass` fails BOTH columns here, because
   it handles surrogate code points and neither of these inputs has
   one -- it is not a general-purpose escape. And `surrogateescape`
   works on the left and raises on the right, which is correct: it
   only re-encodes the surrogates it made.

4. `replace` MEANS TWO DIFFERENT CHARACTERS
------------------------------------------------------------------------
     decoding    'caf\ufffd au lait'
     encoding    b'10 ?'

   U+FFFD REPLACEMENT CHARACTER on the way in; the ASCII question
   mark, 0x3F, on the way out. One policy name, two markers, and only
   one of them is rare enough in real text to grep for.

5. EVERY MARKER IS FORGEABLE
------------------------------------------------------------------------
   This is the finding that decides which policy to use, and it is
   easy to miss because each handler looks like it leaves a trace.
   For each of the three lossy ones, here is an input containing NO
   bad bytes at all that decodes to the identical string:

     replace
       b'caf\xe9'             -> 'caf\ufffd'     (four bytes, one bad)
       b'caf\xef\xbf\xbd'     -> 'caf\ufffd'     identical: True
       the second input is a real U+FFFD, which is a normal character
     backslashreplace
       b'caf\xe9'             -> 'caf\\xe9'      (four bytes, one bad)
       b'caf\\xe9'            -> 'caf\\xe9'      identical: True
       the second input is the four ASCII characters \ x e 9
     ignore
       b'caf\xe9'             -> 'caf'           (four bytes, one bad)
       b'caf'                 -> 'caf'           identical: True
       the second input is a file that simply says 'caf'

   So none of the three can be undone, and none of them can even be
   DETECTED after the fact: a U+FFFD in your database might be a byte
   somebody lost, or it might be what the user typed. The marker is
   not a record of damage, it is a character.

6. THE ONE THAT IS REVERSIBLE
------------------------------------------------------------------------
     decode surrogateescape   'caf\udce9 au lait'
     encode it back           b'caf\xe9 au lait'
     byte-identical to input  True

   That is a whole page of its own -- how it works, where it leaks,
   and the byte it lets a JSON document write into a filename.

7. HOW MUCH DID EACH ONE COST
------------------------------------------------------------------------
     input: b'caf\xe9 au lait, \xffour euros'  (24 bytes, two bad ones)

     handler            chars  U+FFFD   reversible  can you tell?
     ------------------------------------------------------------
     ignore             22     0        False       no
     replace            24     2        False       only by guessing
     backslashreplace   30     0        False       only by guessing
     surrogateescape    24     0        True        yes

   `ignore` is the row to look at. The string got SHORTER and there
   is nothing in it, or in any return value, that says so. That is
   why it is the one policy this library tells you never to use: it
   is not 'be lenient', it is 'delete evidence and report success'.

8. HOW MANY U+FFFD IS ALSO A DECISION
------------------------------------------------------------------------
   `replace` does not write one marker per bad byte. It writes one
   per maximal subpart -- the longest prefix that could still have
   become a valid sequence:

     bytes                    bytes in   U+FFFD out
     b'\xe9'                  1          1
     b'\xf0\x9f'              2          1
     b'\xf0\x9f\x98'          3          1
     b'\xff\xff\xff'          3          3
     b'\xed\xa0\x80'          3          3

   Two bytes of a truncated emoji are ONE marker: they are still a
   plausible beginning. Three bytes of 0xFF are three, because none
   of them could start anything. And the last row is the subtle one --
   0xED IS a legal lead byte, but only in front of 0x80..0x9F, so
   0xED 0xA0 is rejected at the SECOND byte and the maximal subpart
   is just 0xED. That is the surrogate range being excluded, one
   byte earlier than the arithmetic alone would suggest.

9. A POLICY YOU WRITE YOURSELF
------------------------------------------------------------------------
   The eight names are just registered functions. A handler takes the
   exception and returns (replacement, where to resume) -- so the
   policy nobody ships, 'replace it AND tell me where', is four lines:

     text     'caf\ufffd au lait, \ufffdour euros'
     log      [(3, b'\xe9'), (14, b'\xff')]

   Now the U+FFFD is not the only record, so section 5's ambiguity is
   gone: the offsets and the original bytes are beside it.

10. THE FIRST ARGUMENT IS A NAME, AND NAMES HAVE ALIASES
------------------------------------------------------------------------
   Six spellings of one codec, resolved through the registry:

     latin-1      -> iso8859-1
     latin1       -> iso8859-1
     iso-8859-1   -> iso8859-1
     iso8859_1    -> iso8859-1
     L1           -> iso8859-1
     cp819        -> iso8859-1

   Note the canonical name is not any of the ones people type.
   Whether two spellings are the same codec is a question for
   codecs.lookup(), never for the eye.

   And the pair that looks like an alias and is not:

     bytes where cp1252 and latin-1 disagree:  32 of 256
     the range:  0x80..0x9F
     0x80 is '\u20ac' in cp1252 and '\x80' in latin-1

   Those 32 are the C1 control block, which Windows reused for the
   euro sign and the smart quotes. A file decoded with the wrong one
   of this pair is correct for 224 bytes out of 256.

11. NOT EVERY CODEC IS A TEXT CODEC
------------------------------------------------------------------------
   The registry also holds transforms that are bytes-to-bytes or
   str-to-str. .encode()/.decode() refuse them, by name, with a
   message that tells you the right door:

     b'abc'.decode('base64_codec')
       'base64_codec' is not a text encoding; use
         codecs.decode() to handle arbitrary codecs
     'abc'.encode('rot13')
       'rot13' is not a text encoding; use codecs.encode() to
         handle arbitrary codecs

     codecs.encode('abc','rot13')           'nop'
     codecs.decode(b'YWJj','base64_codec')  b'abc'

12. THREE SPELLINGS, ONE OPERATION
------------------------------------------------------------------------
     good.decode('utf-8')               'caf\xe9'
     str(good, 'utf-8')                 'caf\xe9'
     codecs.decode(good, 'utf-8')       'caf\xe9'

     all three equal:  True

   Prefer the method. `str(b, enc)` exists for symmetry with the other
   constructors and reads as a cast rather than as a decision; and
   `str(b)` with NO encoding does not decode at all -- it gives you
   the repr, "b'caf\\xc3\\xa9'", which is a bug that runs.
```
<!-- /output -->

Read section 7 of that run as a decision table rather than a demonstration:

- **`strict`** — data you own, and anything you will act on. It fails at the boundary, which is far from where the bad byte was written, and that distance is the cost. Pay it: the alternative is failing somewhere further away still, with less information.
- **`surrogateescape`** — data you are carrying, not reading. Filenames, log lines you will hand back, a column you are copying between systems. Nothing is lost and nothing is decided.
- **`replace`** — a message for a human, once, at the end. Never for anything that gets stored.
- **`backslashreplace`** — better than `replace` for a diagnostic, because it names the byte rather than erasing it. Still not reversible; see the table above.
- **`ignore`** — never. Not "rarely": never. It is the one that shortens the string and reports success, so the loss is invisible in the data *and* in the return value. If a lenient read is genuinely wanted, `replace` at least leaves something to count.

## How many `U+FFFD`? is a separate question

`replace` does not write one marker per bad byte. It writes one per **maximal subpart** — the longest prefix that could still have become valid — so two bytes of a truncated emoji are one marker and three `0xFF` bytes are three. The subtle row in the program's section 8 is `ED A0 80`: `0xED` is a perfectly legal lead byte, but only in front of `0x80–0x9F`, so the sequence is rejected at the *second* byte and the surrogate range is excluded one byte earlier than the arithmetic alone would suggest — which is the same exclusion [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) is about, seen from inside the decoder.

Unicode's conformance clause **C10** requires that an ill-formed sequence be treated as an error and offers `U+FFFD` as a marker; it does not fix how many markers. So a count is a fact about the decoder, and "how many `U+FFFD`?" is a question two systems can answer differently — [a ranked page this library has not written yet](../../TODO.md).

## A policy you can write

The eight names are just functions in a registry. [PEP 293 ↗](https://peps.python.org/pep-0293/) made that extensible, and it takes four lines to build the policy nobody ships — *replace it and tell me where*:

```python
log = []
def audit(exc):
    log.append((exc.start, bytes(exc.object[exc.start:exc.end])))
    return ("�", exc.end)
codecs.register_error("audit", audit)
```

A handler returns `(replacement, where to resume)`. With the offsets and the original bytes recorded beside the text, the ambiguity two sections up is gone: the `U+FFFD` is no longer the only evidence.

## The first argument is a name, and names have aliases

`latin-1`, `latin1`, `iso-8859-1`, `iso8859_1`, `L1` and `cp819` are six spellings of one codec, and the canonical name Python resolves them to — `iso8859-1` — is not any of the ones people type. Whether two spellings are the same codec is a question for `codecs.lookup()`, never for the eye. (The trap where a *plausible* spelling raises `LookupError` — `utf16-le` against `utf-16le` — is already worked out in [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md).)

The pair that looks like an alias and is not is `cp1252` against `latin-1`: **32 of the 256 bytes differ**, exactly `0x80–0x9F`, which is the C1 control block that Windows reused for the euro sign and the smart quotes. Measured here, confirming what [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) is written to be about — a file decoded with the wrong one of that pair is *correct for 224 bytes out of 256*, which is why it is a bug that survives a spot check.

And not everything in the registry is a text codec. `b'abc'.decode('base64_codec')` and `'abc'.encode('rot13')` both raise `LookupError` — not because the codec is missing, but because `.encode()`/`.decode()` are typed: `str` → `bytes` and back. A `bytes`→`bytes` or `str`→`str` transform goes through `codecs.encode` / `codecs.decode`, and the exception says so.

## Three spellings, one operation

`b.decode('utf-8')`, `str(b, 'utf-8')` and `codecs.decode(b, 'utf-8')` all do the same thing. Prefer the method: `str(b, enc)` reads as a cast rather than as a decision, and it sits one keystroke away from the real trap — **`str(b)` with no encoding does not decode at all.** It returns the *repr*, `"b'caf\\xc3\\xa9'"`, quotes and backslashes included. That is a bug that runs, passes a truthiness check, and reaches a database.

## If you are coming from Python or ABAP

**Python.** Say both arguments at every boundary, and say them in the same places you would put a type annotation: the read, the write, and the subprocess. `open()` takes the same pair (`encoding=`, `errors=`) and defaults the first one to the *locale* — that is [Opening a file](../opening_a_file/README.md), and it is the same lesson one layer up. `sys.stdout` has the pair too and picks its `errors` from the environment, which is why a `print()` that works on your laptop can raise in a container. `codecs.lookup_error(name)` hands you any registered handler as a callable, which is how you find out what one actually does without reading the C.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* The two arguments exist, split across a different API. The table is the code page you pass to `cl_abap_conv_in_ce=>create( encoding = … )` or `cl_abap_codepage`; the policy is the `replacement` parameter, and it is `errors='replace'` with a character you choose — there is no `ignore`, no `backslashreplace`, and nothing reversible, so the `surrogateescape` row of the matrix above has no ABAP entry at all. Without a `replacement`, conversion raises `CX_SY_CONVERSION_CODEPAGE`, which is `strict`. The practical consequence is the same as the decision table: for data you are only *carrying*, do not convert — read it with `OPEN DATASET … IN BINARY MODE` into an `xstring` and keep it as bytes. And treat any code-page number you find in a document as something to verify against the system that will run the job.

## Try it

- Take the exception you get from `b'caf\xe9'.decode('utf-8')` and print `e.object[e.start:e.end]`. That is the smallest useful bug report you can send about a data file.
- `'10 €'.encode('cp1252')` and `'10 €'.encode('latin-1')`. One works. That is the 32-byte difference, in one line.
- Search your own codebase for `errors=` — then for `.decode(` with no second argument. The ratio is your real policy.
- Register the four-line `audit` handler above and point it at a file you have never checked. The `log` list is the answer to "is this file clean", which no boolean gives you.
- `'abc'.encode('rot13')`, then `codecs.encode('abc', 'rot13')`. The error message is the whole explanation.

## Practice

**Six policies, one bad byte.** For `b"caf\xe9.txt"` decoded as UTF-8, predict what each of `strict`, `replace`, `ignore`, `backslashreplace` and `surrogateescape` produces — and, for each, whether you could recover the original bytes from the result.

Exactly one is reversible. Say which, why it looks so strange, and what Python uses it for. Then encode `"café → ż"` as ASCII under six handlers and say which two exist only for encoding, and which consumer each of those two is safe for.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:encode_decode_and_errors_kata_py -->
*Verified output of [`encode_decode_and_errors_kata_py.py`](examples/encode_decode_and_errors_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
DECODING BYTES THAT ARE NOT UTF-8
   input 63 61 66 e9 2e 74 78 74
   strict             UnicodeDecodeError     nothing produced -- an outage, on purpose
   replace            'caf�.txt'             lossy
   ignore             'caf.txt'              lossy
   backslashreplace   'caf\\xe9.txt'         lossy
   surrogateescape    'caf\udce9.txt'        REVERSIBLE

   Exactly one of the five is reversible, and it is the one that looks
   strangest: surrogateescape maps each bad byte to a lone surrogate in
   a private range, so the original byte can be recovered on the way
   out. That is why it is what Python uses for FILENAMES, which are
   bytes that must survive a round trip even when they are not text.

   ignore is silent data loss. replace is visible data loss -- U+FFFD is
   a record that something was there, not of what. backslashreplace is
   lossless as TEXT but the escape is now literal characters, so a later
   consumer sees six characters where there was one byte.

ENCODING TEXT A TABLE CANNOT HOLD
   text 'café → ż' -> ascii
   strict             UnicodeEncodeError
   replace            b'caf? ? ?'
   ignore             b'caf  '
   backslashreplace   b'caf\\xe9 \\u2192 \\u017c'
   xmlcharrefreplace  b'caf&#233; &#8594; &#380;'
   namereplace        b'caf\\N{LATIN SMALL LETTER E WITH ACUTE} \\N{RIGHTWARDS ARROW} \\N{LATIN SMALL LETTER Z WITH DOT ABOVE}'

   Two of those exist only for encoding, and both are round-trippable by
   a reader that knows the convention: xmlcharrefreplace produces valid
   HTML/XML, namereplace produces Python source. Neither is 'safe' in
   general -- they are safe for one consumer each.

THE DECISION, STATED PLAINLY
   strict           an outage at 3am, and the only one that cannot
                    silently ship wrong data
   replace/ignore   a smaller or wronger value, and a green log
   surrogateescape  a round trip, at the price of a str that is not
                    encodable by anything else
   The handler is not a convenience argument. It is where you write down
   what your program should do when the world hands it something it
   cannot explain -- and the default, strict, is a defensible answer.
```
<!-- /output -->

</details>

## See also

- [`str` vs `bytes`](../str_vs_bytes/README.md) — the two types this page moves between
- [Bytes that are not text](../surrogateescape/README.md) — the one reversible handler, in full
- [Opening a file](../opening_a_file/README.md) — the same two arguments, with the first one defaulted from the locale
- [Encode and decode are verbs](../../03_Encodings/encode_and_decode_are_verbs/README.md) — the concept, before the API
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — *where* the check happens, in four languages
- [Mojibake](../../03_Encodings/mojibake/README.md) — what a wrong first argument looks like on screen
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — codec names that write a mark, and the `LookupError` trap
- [Windows-1252 vs Latin-1](../../07_Real_Data/windows_1252_vs_latin1/README.md) — the 32 bytes, and how to repair a file that met the wrong one
- [Code pages](../../02_Characters/code_pages/README.md) — why there are so many tables to name
- [UTF-8 everywhere](../../10_Best_Practices/utf8_everywhere/README.md) — the same policies as one rule of five
- [`codecs` — error handlers ↗](https://docs.python.org/3/library/codecs.html#error-handlers) — the registry, and the full list
- [`codecs` — standard encodings ↗](https://docs.python.org/3/library/codecs.html#standard-encodings) — every name and alias Python ships
- [PEP 293 — codec error handling callbacks ↗](https://peps.python.org/pep-0293/) — why you can add your own
- [The codecs registry ↗](https://masiarek.github.io/python-learning-library/01_Text_and_Bytes/the_codecs_registry/index.html) — the ninth handler at full length, plus the two rules its signature does not state: one name serves both directions, and it fires once per *run* of bad input rather than once per character
- [Unicode Standard, chapter 3 ↗](https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-3/) — conformance clause C10
