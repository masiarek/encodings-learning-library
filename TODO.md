# What to write next — the prioritized backlog

**Level:** reference

**One line:** Fifty pages in the order they are worth writing, ranked against the four checkpoints this library was built around — because the topic map in [TOPICS.md](TOPICS.md) lists over 1,500 terms and a list that long is a way of not choosing.

## The finding that decides the order

[00_Start_Here](00_Start_Here/README.md) names **four checkpoints** — the four things Adam said on day one he could not yet do. On 2026-09-06, counting the pages on disk:

| Checkpoint | The page that settles it | Status |
|---|---|---|
| `0x41` ↔ 65 ↔ `0b01000001` by hand | chapter 1, three lessons | **written** |
| Code point vs UTF-8 bytes | [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) | **stub** |
| Python `str` vs `bytes` | [Encode, decode and errors](04_Python/encode_decode_and_errors/README.md) | **written**, 2026-09-07 |
| Rust `String` vs `&str` vs `char` | [`char` is four bytes](05_Rust/char_is_four_bytes/README.md) | **stub** |

**Two of the four checkpoint pages are still stubs** (2026-09-07; it was three until the Python one landed), while 50-odd lessons are written around them — including a whole security chapter and a whole tools chapter. The library grew outward from its middle, which was the right call each time it was made ([ROADMAP.md](ROADMAP.md) explains each one) and is the wrong shape to leave.

So the ranking is: **finish the promise, then the goal that has no chapter yet (real SAP data), then the remaining stubs, then the pages the topic map exposed.** 22 of the 50 name a page that already exists, and **19 of those are still stubs** (re-counted 2026-09-07) with their questions written down and their URLs minted; graduating one of those beats minting a new page almost every time.

**Every hook below is a claim to verify, not a fact this library has checked.** That is the whole difference between this page and every other page here ([CONTRIBUTING.md](CONTRIBUTING.md)). Expect roughly one in three to come out differently once a program is pointed at it — which is the reason to point a program at it.

---

## Tier 1 — the checkpoints (1–7)

Nothing else in this library is worth more than these seven. Five are stubs; all five have their questions already written on the page.

| # | Page | Lands in | The hook to verify |
|---|---|---|---|
| 1 | [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) | 03 | The checkpoint page. Encode `é`, `ż`, `€`, `😀` with a pencil; the four row shapes; and Table 3-7 **verified by exhaustion in about a second** — 1,112,064 sequences, every one decoding inside the range its row claims — rather than quoted |
| 2 | ~~[Encode, decode and errors](04_Python/encode_decode_and_errors/README.md)~~ | 04 | **Written 2026-09-07.** Eight handlers, not six, and the blast radius came out sharper than the row predicted: `replace` is not *visible* data loss either, because a real `U+FFFD` in the input produces the same string |
| 3 | [`char` is four bytes](05_Rust/char_is_four_bytes/README.md) | 05 | The checkpoint page. `char` is a scalar value, always 4 bytes in memory, 1–4 bytes in a `String` — so `size_of::<char>()` and `'é'.len_utf8()` disagree on purpose |
| 4 | [A `str` vs `bytes`](04_Python/str_vs_bytes/README.md) | 04 | The page checkpoint 3 rests on. `len()` answers two different questions and neither is "characters" |
| 5 | ~~[UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md)~~ | 03 | **Written 2026-09-07.** `U+1F600` → `D83D DE00` by hand, and the sting landed as written: `json.dumps` emits that surrogate pair into a format that is UTF-8 by [RFC 8259 ↗](https://www.rfc-editor.org/rfc/rfc8259), and `json.loads('"\ud800"')` succeeds |
| 6 | [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md) | 02 | **The five lengths** — bytes, code units, code points, graphemes, terminal columns. One string, five correct answers. `unicodedata.east_asian_width` makes the fifth machine-checkable even though no `len` in either language will tell you |
| 7 | [`from_utf8` and lossy](05_Rust/from_utf8_and_lossy/README.md) | 05 | Three functions, three contracts: validate, replace, or promise. `valid_up_to()` against Python's `UnicodeDecodeError.start` — the same byte offset from two languages |

## Tier 2 — real data, the goal with the emptiest chapter (8–14)

Goal three was *real SAP data*, and [07_Real_Data](07_Real_Data/README.md) is 2 written pages against 5 stubs. Every one of these is a bug Adam will actually meet.

| # | Page | Lands in | The hook to verify |
|---|---|---|---|
| 8 | [Windows-1252 vs Latin-1](07_Real_Data/windows_1252_vs_latin1/README.md) | 07 | Measured 2026-09-06: byte `0x80` is `€` in cp1252 and a C1 control in Latin-1, so **cp1252 is a replacement of Latin-1's top block, not a superset** — which is exactly what the imported glossary got wrong |
| 9 | [The mojibake round trip](07_Real_Data/mojibake_round_trip/README.md) | 07 | `text.encode('cp1252').decode('utf-8')` repairs it — **when it can**. Latin-1 is total so it always reverses; cp1252 has five unassigned bytes, so information is genuinely gone. The deciding question, asked before the repair |
| 10 | [SAP code pages](07_Real_Data/sap_code_pages/README.md) | 07 | The one page that must say *verify against the system* on every number. EBCDIC's three letter runs, 1140–1149's euro twins, and `cl_abap_conv` as the boundary |
| 11 | [Fixed-width byte fields](07_Real_Data/fixed_width_byte_fields/README.md) | 07 | A field is N **bytes**; `ż` is two of them. Truncating at N bytes splits a UTF-8 sequence and produces a file that is not text any more |
| 12 | ~~[CRLF vs LF](07_Real_Data/crlf_vs_lf/README.md)~~ | 07 | **Written 2026-09-07.** Python and shell; `splitlines()` splitting on eleven sequences where `split('\n')` sees one, the byte that cannot appear in its own output, and git reporting a tree clean when every line on disk differs from the blob |
| 13 | [Sorting and collation](07_Real_Data/sorting_and_collation/README.md) | 07 | Three locales, three different correct orders for one list. Then the consequence: **the glibc 2.28 collation change silently invalidated PostgreSQL indexes worldwide** |
| 14 | [Interfaces and storage](10_Best_Practices/interfaces_and_storage/README.md) | 10 | The closing rule: decode at the boundary, hold text in the middle, encode at the boundary, and write the encoding down in the contract |

## Tier 3 — the remaining stubs (15–22)

Cheap: the questions are already written, and each is one program away.

| # | Page | Lands in | The hook to verify |
|---|---|---|---|
| 15 | [Slicing by byte](05_Rust/slicing_by_byte/README.md) | 05 | `&s[0..1]` panics on `é` — at runtime, with a message naming the char boundary. Rust's one place where the encoding is enforced by a panic rather than a type |
| 16 | [A `str` in memory](04_Python/str_in_memory/README.md) | 04 | [PEP 393 ↗](https://peps.python.org/pep-0393/): one emoji in a 1,000-character string quadruples its memory, because the whole string upgrades to UCS-4 |
| 17 | [Opening a file](04_Python/opening_a_file/README.md) | 04 | `open()`'s default encoding is the **locale's**, so the same script reads a different file on two machines. [PEP 686 ↗](https://peps.python.org/pep-0686/) is changing it to UTF-8, which will silently fix and silently break code |
| 18 | [`bytes`, hex and int](04_Python/bytes_hex_and_int/README.md) | 04 | `int.from_bytes` makes the endianness argument mandatory. The bridge from chapter 1 into Python |
| 19 | [`iconv`](06_Terminal/iconv/README.md) | 06 | Three measured splits already in hand: `-c` repairs differently on BSD and GNU, `-t UTF-16` picks its own byte order, and iconv accepts sequences above `U+10FFFF` that Python and Rust reject |
| 20 | [`printf` writes bytes](06_Terminal/printf_writes_bytes/README.md) | 06 | `printf '\xc3\xa9'` is how you make a file by hand; `%b` versus `%s`; and `printf '\x..'` is bash, not POSIX |
| 21 | [`file` guesses](06_Terminal/file_guesses/README.md) | 06 | Four answer shapes and only two are evidence: a BOM is a fact, "UTF-8" is an inference, "ISO-8859 text" is a proof of a negative, and `data` for BOM-less UTF-16LE is a surrender |
| 22 | [Logical and visual order](02_Characters/logical_and_visual_order/README.md) | 02 | **A terminal screenshot is not evidence about a string.** [UAX #9 ↗](https://www.unicode.org/reports/tr9/), embedding levels, and the nine controls written only as escapes |

## Tier 4 — the pages the topic map exposed (23–50)

New pages. Ordered by how often the problem shows up in Adam's three goals, not by how interesting the idea is.

| # | Page | Lands in | The hook to verify |
|---|---|---|---|
| 23 | ~~Bytes that are not text — `surrogateescape`~~ | 04 | **Written 2026-09-07** — [Bytes that are not text](04_Python/surrogateescape/README.md). It took the three things this row still listed as owed (`os.fsdecode`, `sys.getfilesystemencoding`, the Windows half via `surrogatepass` and [PEP 529 ↗](https://peps.python.org/pep-0529/)) and left the `x-user-defined` comparison where it already is, on ["Handles Unicode" is four questions](10_Best_Practices/what_your_language_gives_you/README.md) |
| 24 | Best-fit mapping — the quote that appeared from nowhere | 12 | Windows converts `U+2018` to `'` when encoding to a code page that lacks it. **A filter that checked the original string has been bypassed by a conversion.** Currently described-not-demonstrated on [canonicalize then check](12_Adversarial/canonicalize_then_check/README.md) |
| 25 | The space that is not a space | 07 | NBSP survives copy-paste from Excel and Word, is not stripped by every language's `strip()`, and makes a numeric field fail to parse. The most common invisible bug in business data |
| 26 | The Norway problem — when a type is guessed | 07 | YAML 1.1 reads `no` as `false` and `12:30` as 750 in base 60. A country code becomes a boolean. Cross-links the [voting library ↗](https://github.com/masiarek/star-voting-library), which machine-checks for exactly this |
| 27 | Excel and the CSV | 07 | Three separate facts: Excel needs a **UTF-8 BOM** to read UTF-8, uses the **locale's list separator** (semicolon across Europe), and executes a leading `=` — CSV injection |
| 28 | Git and your filenames | 07 | `core.quotepath` (the octal escapes in `git status`), `core.precomposeunicode` (macOS hands git a decomposed name), and `working-tree-encoding` for UTF-16 files |
| 29 | The filename inside the zip | 07 | CP437 unless the EFS bit is set. The garbled-Japanese-zip classic, and a flag most tools never write |
| 30 | Case is not a per-character operation | 02 | `ß` uppercases to `SS`, so the string gets longer — which is why Rust's `to_uppercase` returns an iterator. Then Turkish `I`, and Greek final sigma, where case depends on locale and on position |
| 31 | Where a line may break | 02 | [UAX #14 ↗](https://www.unicode.org/reports/tr14/). Thai and Japanese have no spaces, so "split on whitespace" is not wrapping. `textwrap` is wrong for half the world |
| 32 | What a charset label means | 03 | The WHATWG Encoding Standard: `iso-8859-1` **must** be decoded as windows-1252, label matching is case- and whitespace-insensitive, and unknown labels map to the replacement encoding on purpose. The document the web actually obeys |
| 33 | How many `U+FFFD`? | 12 | Two decoders, one invalid input, different numbers of replacement characters (the maximal-subpart rule). **A parser differential hiding in the error path** |
| 34 | ICU — the library underneath | 03 | Collation, break iteration, normalization, transliteration, formatting. Most languages' text handling is ICU wearing a hat; Rust's std deliberately is not, which is why the crates exist. The claim is now **asserted but not demonstrated** at the foot of ["Handles Unicode" is four questions](10_Best_Practices/what_your_language_gives_you/README.md), which is exactly the gap this page closes |
| 35 | PRECIS — stringprep, after stringprep | 02 | [RFC 8264 ↗](https://www.rfc-editor.org/rfc/rfc8264)/8265/8266, the successor to the [RFC 3454 ↗](https://www.rfc-editor.org/rfc/rfc3454) already taught on [Preparing a string](02_Characters/preparing_a_string/README.md). `UsernameCaseMapped` vs `OpaqueString`, and why passwords get a different profile |
| 36 | Passwords are not text | 12 | **bcrypt truncates at 72 bytes**, so a passphrase in a non-Latin script carries less than it looks; and normalizing a password is a decision with no free option — normalize and two spellings both log in, don't and one silently never works |
| 37 | Text you cannot see | 12 | The `U+E0000` tag block: invisible to a human reviewer, fully present to a parser or a model. Trojan Source's 2026 descendant, and the same house rule applies — escapes only, never a raw control |
| 38 | The filename that reads backwards | 12 | An override in a filename displays `...exe` as `...pdf`. Decades old, still shipping. The bidi lesson with a consequence attached |
| 39 | A log viewer is an interpreter | 12 | Untrusted text printed to a terminal can move the cursor, rewrite earlier lines, set the title, and on some terminals request a reply that is then typed as input. Stripping ANSI with the usual regex misses OSC |
| 40 | A pipe is not a terminal | 06 | `isatty()` decides buffering, colour **and** the encoding Python gives `sys.stdout` — so piping the same program into `cat` can raise `UnicodeEncodeError` where `python x.py` does not. `PYTHONIOENCODING`, `PYTHONUTF8`, [PEP 540 ↗](https://peps.python.org/pep-0540/) |
| 41 | A character split across two reads | 03 | A chunked read can cut a UTF-8 sequence in half, so `chunk.decode()` per chunk is wrong. Incremental decoders exist for this, in every language |
| 42 | The filename in the HTTP header | 08 | Headers are ISO-8859-1 by [RFC 7230 ↗](https://www.rfc-editor.org/rfc/rfc7230) — but 7230 is obsoleted by [RFC 9110 ↗](https://www.rfc-editor.org/rfc/rfc9110), which calls that reading *historical* and constrains field values to US-ASCII; [RFC 8187 ↗](https://www.rfc-editor.org/rfc/rfc8187)'s `filename*=UTF-8''` is the fix. Why a download with a Polish name works in one browser and not another |
| 43 | JSON is Unicode, and still has surrogates | 08 | Measured: `json.dumps("😀")` emits `😀`, `json.loads('"\ud800"')` returns a lone surrogate that cannot be encoded to UTF-8. Plus duplicate keys and the forbidden BOM |
| 44 | The characters XML cannot carry | 08 | XML 1.0 cannot represent `0x01` **even escaped**. A format that forbids data, which is why database exports fail on control characters |
| 45 | The column that counts bytes | 10 | `ORA-12899` (value too large, in bytes, for a column sized in characters), MySQL's 767/3072-byte index prefix, and `utf8mb3` raising error 1366 on an emoji |
| 46 | The client that lies about its encoding | 10 | Oracle `NLS_LANG`: the client *declares* an encoding and the server converts to match, so a wrong declaration corrupts on write, invisibly, forever. The classic enterprise mojibake source |
| 47 | Two PowerShells, two files | 11 | Windows PowerShell 5 writes UTF-16LE by default; PowerShell 7 writes BOM-less UTF-8. The same script, two machines, two different files |
| 48 | The container has no locales | 06 | musl ships essentially no locale data, so Alpine behaves differently from Debian on the same code. The container-era version of the BSD/GNU split this library already tracks |
| 49 | `OsStr`, `Path`, and WTF-8 | 05 | A Windows filename may contain an unpaired surrogate, so it is not representable in UTF-8 — which is why `Path` is not `String` and `to_string_lossy` is a decision, not a convenience. **Narrowed 2026-09-07:** [Bytes that are not text](04_Python/surrogateescape/README.md) already uses `OsStr` as the *contrast* with `surrogateescape`; what is left here is the type as an API — `Cow`, `PathBuf`, and the Windows side |
| 50 | Why the model cannot count the letters | 09 | A tokenizer sees byte-level BPE tokens, not characters — and the same sentence costs several times more tokens in Polish than in English. This library's thesis ("it depends who is counting") arriving somewhere new |

---

## Not on this list, on purpose

[TOPICS.md](TOPICS.md) marks three sections **adjacent**: streams and file descriptors (§3), parsers and grammars (§4.2), fonts and rendering (§6). They are real, they touch text, and the lesson belongs in a sibling library or nowhere yet. Two corners of them *are* core and have been pulled onto this list — items 40 and 41 — which is the point of marking the boundary rather than leaving it to drift.

Also deliberately absent: a second pass over anything already written. When a page here is wrong, that is a correction, not a backlog item; it goes in as a fix the day it is found.

## How to work through it

One page per sitting, the same as reading them ([CONTRIBUTING.md](CONTRIBUTING.md)):

```bash
python3 tools/run_examples.py --update --only <stem>_py   # then READ the key
python3 tools/check_all.py                                # all four gates, CI's order
```

Then update the row in the chapter README and in [ROADMAP.md](ROADMAP.md), and strike the line here. A stub graduates by gaining an `examples/` program and losing its notice — the URL never moves.
