# Python text in practice

**Level:** 201 · for anyone starting from zero

**One line:** Pass `encoding='utf-8'` to every `open()` even when it is already the default, run your tests under `-X warn_default_encoding` once to find the ones you missed, treat filenames as bytes wearing a costume, and remember that `bytes` methods that look like text methods are ASCII-only on purpose.

## The one-line version

Python 3 already made the big decision for you: `str` and `bytes` do not mix, and the interpreter refuses rather than guessing. Everything below is about the *defaults around the edges*, which are older than that decision and still carry the locale with them.

## `open()` — four arguments that should be reflex

```python
open(path, encoding="utf-8")            # always. even when it is the default
open(path, encoding="utf-8", newline="")  # for csv. always. see below
open(path, encoding="utf-8-sig")        # when Excel is upstream: eats a BOM
open(path, "rb")                        # when it is not text at all
```

**`encoding=`** because the fallback is the machine's locale — `cp1252` on a Windows box, UTF-8 on your Mac — so the same script reads correctly here and silently wrongly there. Naming it also documents which side of the [sandwich](../utf8_everywhere/README.md) the file is on, which is why it still belongs in the call after Python 3.15 changes the default.

**`newline=""`** for anything going through the `csv` module, always. `csv` does its own line-ending handling; leaving the default on top of it doubles up and produces blank rows between records on Windows.

**`utf-8-sig` to read, `utf-8` to write.** The `-sig` codec strips a leading BOM if there is one and does nothing if there is not, so it is the safe reader for files that may have come from Excel. Never write with it: you would be adding a BOM to somebody else's problem.

## Two interpreter switches worth knowing

**`-X utf8` / `PYTHONUTF8=1`** ([PEP 540 ↗](https://peps.python.org/pep-0540/)) tells Python to ignore the locale and use UTF-8 for everything. [PEP 686 ↗](https://peps.python.org/pep-0686/) is Final and makes that the **default in Python 3.15** — the single biggest change to this subject in fifteen years, and the end of the "works on my machine" encoding bug.

**`-X warn_default_encoding`** ([PEP 597 ↗](https://peps.python.org/pep-0597/), since 3.10) turns every `open()` that did not name an encoding into an `EncodingWarning` with the line number. Run your test suite under it once and you have audited a whole codebase in one pass. This is the highest-value five minutes on this page.

```bash
python3 -X warn_default_encoding -W error::EncodingWarning -m pytest
```

## Filenames are not text

A Unix filename is any bytes except NUL and `/`. It need not be UTF-8, and on a disk that has been around a while, some of it will not be. Python's answer is `surrogateescape`: `os.listdir()` hands you `str` with the undecodable bytes parked in surrogate code points, and `os.fsencode()` puts them back exactly. That is why you can rename a file you cannot print.

The rule that follows: **never `.encode('utf-8')` a path by hand.** Use `os.fsencode` / `os.fsdecode`, or stay in `pathlib` and let it deal. The hand-rolled version works on every machine you own and raises on somebody else's.

## `bytes` looks like text and is not

`bytes` has `.upper()`, `.split()`, `.strip()`, `.isalpha()`. They are all **ASCII-only**, deliberately: a `bytes` object does not know which table produced it, so ASCII is the only assumption available. `b'stra\xc3\x9fe'.upper()` leaves the `ß` bytes untouched. The same split runs through `re`: `\w` means "Unicode word character" against `str` and "ASCII word character" against `bytes`, so the same pattern gives two different answers.

This is a feature. It means byte-level parsing of a protocol cannot accidentally apply Turkish casing rules to a header name.

## The toolkit you already have

`unicodedata` is a copy of the Unicode character database in your standard library:

```python
unicodedata.name("ź")            # 'LATIN SMALL LETTER Z WITH ACUTE'
unicodedata.category("́")         # 'Mn' — a nonspacing mark
unicodedata.normalize("NFC", s)  # the one you want on the way in
unicodedata.normalize("NFKC", s) # the aggressive one: ﬁ -> fi, １２３ -> 123
```

`name()` is the fastest way to find out what a character actually is when the terminal will not show you. `NFC` is the storage default; `NFKC` is right for a search index or a username uniqueness check and wrong for text you will hand back to the person who typed it.

And on the way out: `json.dumps(data, ensure_ascii=False)`. The default escapes every non-ASCII character to `\uXXXX` — valid JSON, from an era when the channel might not have been 8-bit clean, and today it mostly triples your payload and makes your logs unreadable. JSON is UTF-8 by [RFC 8259 ↗](https://www.rfc-editor.org/rfc/rfc8259#section-8.1).

## In Python

<!-- output:python_text_in_practice_py -->
*Verified output of [`python_text_in_practice_py.py`](examples/python_text_in_practice_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. str AND bytes DO NOT MIX, AND THAT IS THE FEATURE
------------------------------------------------------------------------
   str    'Łódź'       len 4   type str
   bytes  b'\xc5\x81\xc3\xb3d\xc5\xba' len 7   type bytes
   "a" + b"b"             -> TypeError: can only concatenate str (not "bytes") to str
   "Ł" in b"\xc5\x81"     -> TypeError: a bytes-like object is required, not 'str'
   b"x".decode()          -> 'x'
   Python 2 would have guessed here, and guessed with ASCII. Python 3
   refuses, which turns a wrong answer in production into a TypeError
   on your machine. Every '.encode()' you add is you saying where the
   boundary of your program is.

2. open(): FOUR ARGUMENTS THAT SHOULD BE HABIT
------------------------------------------------------------------------
   on disk               b'id,city\r\n1,\xc5\x81\xc3\xb3d\xc5\xba\r\n'
   encoding='utf-8'      'id,city\r\n1,Łódź\r\n'
   newline= left default 'id,city\n1,Łódź\n'   <- \r\n became \n
     open(p, encoding='utf-8')   name the encoding even when it is the
                                 default; it says which side of the
                                 boundary the file is on
     newline=''                  for csv, ALWAYS — the csv module does
                                 its own line handling and doubles up
                                 otherwise
     errors='strict'             the default; change it deliberately
     'rb' / 'wb'                 when it is not text: images, zips, and
                                 anything you will hash or checksum

3. TWO SWITCHES THAT TURN THE WHOLE CLASS OF BUG INTO A WARNING
------------------------------------------------------------------------
   sys.flags.utf8_mode        = 1   (PYTHONUTF8=1 / -X utf8)
   sys.flags.warn_default_encoding = 0   (-X warn_default_encoding)
   UTF-8 mode (PEP 540) makes Python ignore the machine's locale and use
   UTF-8 everywhere; PEP 686 makes that the DEFAULT in Python 3.15, which
   is the single biggest change to this subject in fifteen years.

   The second flag is the one to run your test suite under today:
   -X warn_default_encoding turns every open() that did not name an
   encoding into an EncodingWarning, pointing at the line. That is a
   whole codebase audited in one run, and it is PEP 597, since 3.10.

4. FILENAMES ARE NOT TEXT, AND PYTHON HANDS YOU THE ESCAPE HATCH
------------------------------------------------------------------------
   bytes on disk       b'report-caf\xe9.csv'
   os.fsdecode(...)    'report-caf\udce9.csv'
   os.fsencode(back)   b'report-caf\xe9.csv'
   round-trips exactly True
   A Unix filename is any bytes but NUL and '/', so it need not be UTF-8
   at all. os.listdir() gives you str with the undecodable bytes parked
   in surrogates, and os.fsencode puts them back — which is why you can
   rename a file you cannot print. Never .encode('utf-8') a filename by
   hand; that is the call that raises on somebody else's disk.

5. bytes HAS TEXT-LOOKING METHODS. THEY ARE ASCII-ONLY, ON PURPOSE.
------------------------------------------------------------------------
   'straße'.upper()          -> 'STRASSE'   <- one letter became two
   'straße'.encode().upper() -> b'STRA\xc3\x9fE'
                                  ^ the ß bytes came through untouched:
                                    bytes.upper() only knows a-z.

   re.findall(r'\w+', 'Łódź ok')          -> ['Łódź', 'ok']
   re.findall(rb'\w+', b'...') on bytes   -> [b'd', b'ok']
   Same pattern, two answers: \w means 'Unicode word character' against
   str and 'ASCII word character' against bytes. A bytes object has no
   idea which table made it, so ASCII is the only thing it can assume —
   and that is the right call, not a limitation.

6. THE unicodedata TOOLKIT, WHICH IS ALREADY INSTALLED
------------------------------------------------------------------------
   'ź'        category Ll   combining   0  LATIN SMALL LETTER Z WITH ACUTE
   '́'        category Mn   combining 230  COMBINING ACUTE ACCENT
   '😀'        category So   combining   0  GRINNING FACE
   lookup('YEN SIGN')          -> '¥'
   normalize('NFKC', 'ﬁ')      -> 'fi'   <- the ligature becomes two letters
   normalize('NFKC', '１２３')  -> '123'   <- fullwidth digits become ASCII
   NFKC is the aggressive one: it folds compatibility forms together, so
   it is right for a search index or a username check and wrong for text
   you will store and hand back. NFC is the safe default for storage.

   And the export side, one flag: json.dumps(ensure_ascii=False) -> {"c": "Łódź"}
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** You are here — but two things carry over from the *other* direction. If you have written Python 2, the instinct to reach for `str(x)` on something that might be bytes is the exact reflex to unlearn: in Python 3 that gives you `"b'caf\\xc3\\xa9'"`, a string containing the letter `b` and a quote mark, which then travels a long way before anyone notices. And `sys.stdout` is a text wrapper with its own encoding: `sys.stdout.buffer.write(b"...")` is the way to put raw bytes on the pipe, and `sys.stdout.reconfigure(encoding="utf-8")` is the way to fix a wrapper you inherited.

**ABAP.** The nearest thing to `encoding=` is the `ENCODING` addition on `OPEN DATASET` — `IN TEXT MODE ENCODING UTF-8` versus `DEFAULT`, where `DEFAULT` means the system code page and is exactly the trap that `open()` without `encoding=` is. Name it. `SET LOCALE` and the system code page are the ABAP versions of the locale-dependent default, and the ABAP version of `-X warn_default_encoding` does not exist — so the audit is a grep for `OPEN DATASET` without `ENCODING`, done by hand. The `xstring` ↔ `string` conversions are `cl_abap_codepage=>convert_to` / `convert_from`, and the byte-order mark handling is yours to do: nothing eats a BOM for you. *(Not machine-checked — CI cannot run ABAP. Verify code-page numbers against your own system.)*

## Try it

```bash
cd 10_Best_Practices/python_text_in_practice/examples
python3 python_text_in_practice_py.py
```

Then, on your own code:

```bash
python3 -X warn_default_encoding -W error::EncodingWarning -c "open('README.md').read()"
```

Without the machine: a script writes a CSV that opens correctly in Excel on your machine and shows `Å??dÅº` on a colleague's. Name two arguments that were missing from the `open()` call, and say which one of them Excel specifically needs.

## See also

- [UTF-8 everywhere](../utf8_everywhere/README.md) — the language-independent rules these implement
- [04_Python](../../04_Python/README.md) — the mechanics: `str` vs `bytes`, `errors=`, normalization
- [Rust strings in practice](../rust_strings_in_practice/README.md) — the same checklist with a compiler
- [PEP 686 ↗](https://peps.python.org/pep-0686/) — UTF-8 mode becomes the default in 3.15
- [PEP 597 ↗](https://peps.python.org/pep-0597/) — `EncodingWarning`, the audit switch
