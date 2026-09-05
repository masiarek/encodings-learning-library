# Why UTF-8 won

**Level:** 201 · for anyone starting from zero

**One line:** UTF-8 did not win a vote — it won because an ASCII file already *is* a UTF-8 file, no fragment of a character can ever look like ASCII, a reader can start anywhere, a wrong guess fails loudly, there is no byte order to get wrong, and sorting the bytes sorts the characters. It pays for all six in CJK storage, and that bill lost.

## The design, and where it came from

Unicode says which *number* a character has. It does not say how to write that number into a file, and in 1992 there were two obvious answers and one strange one. The obvious ones: give every character a fixed two bytes (UCS-2, what Windows NT and Java did) or a fixed four (UCS-4). The strange one was **variable width** — one byte for ASCII, two, three or four for everything else — and it was strange because variable width is exactly what had just made Shift-JIS so painful.

Ken Thompson and Rob Pike designed it in September 1992, in Pike's telling ["on a placemat in a New Jersey diner" ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/utf-8-history.txt); the proposal was mailed to X/Open on 8 September, Thompson wrote the packing and unpacking code that night, and Plan 9 was running nothing else by that Friday. It replaced an existing X/Open proposal, FSS-UTF, and the reason they replaced it rather than adopting it is the property in section 3 below: **you can pick up a byte stream in the middle** and find the next character boundary within three bytes. They presented it as [*Hello World* ↗](https://www.usenix.org/conference/usenix-winter-1993-conference/hello-world) at the USENIX Winter 1993 conference.

It then took fifteen years. Google's measurements put Unicode past both ASCII and Western European encodings on the web [in December 2007 ↗](https://googleblog.blogspot.com/2008/05/moving-to-unicode-51.html); [W3Techs ↗](https://w3techs.com/technologies/details/en-utf8) has it at **99.0% of all websites** as of September 2026. There is no other format-war in computing with that ending.

## The bit layout, in one table

| Code points | Bytes | Pattern |
|---|---|---|
| `U+0000`–`U+007F` | 1 | `0xxxxxxx` |
| `U+0080`–`U+07FF` | 2 | `110xxxxx 10xxxxxx` |
| `U+0800`–`U+FFFF` | 3 | `1110xxxx 10xxxxxx 10xxxxxx` |
| `U+10000`–`U+10FFFF` | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` |

Every property below is a consequence of that table, and mostly of one decision inside it: **continuation bytes start `10`, and nothing else does.** Doing the encoding by hand — which is where a code point stops being abstract — is [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md). This page is about why the table is shaped that way.

## The six properties

**1 · An ASCII file is already a UTF-8 file.** Not "compatible with", not "convertible to" — the same bytes. Every tool, every protocol, every file on every disk in 1992 was already valid UTF-8, and nothing had to be converted on any particular day. UCS-2 could not say that, and that is most of the answer on its own.

**2 · No fragment of a character can look like ASCII.** Every byte of a multi-byte character has its top bit set, so a byte below `0x80` is *always* a whole ASCII character. Splitting on `,`, scanning for `/`, looking for a newline — none of them can land inside a character. Shift-JIS could not promise this: its second byte ranges over `0x40`–`0xFC`, which includes `0x5C`, the backslash. `ソ` is `83 5C`. A path splitter looking for a backslash found one *inside a character*, and that is the "5C problem" that made Japanese Windows filenames a decade-long joke.

**3 · You can start reading anywhere.** A continuation byte is `10xxxxxx` and a leading byte never is, so a reader dropped into the middle of a stream skips at most three bytes and is synchronised. That is what makes `tail -c`, a seek into a log file, a corrupted packet, and a parallel chunked parser all recoverable. It is also the property Thompson added to FSS-UTF, and the reason UTF-8 exists as a separate thing at all.

**4 · A wrong guess fails loudly.** Most byte sequences are *not* valid UTF-8, so decoding a Latin-1 file as UTF-8 usually raises on the first accented character. The reverse is the important half: Latin-1 maps all 256 bytes, so it can never report a problem — it accepts every file and returns the wrong text in silence. That asymmetry is why mojibake was undiagnosable for twenty years and why it is a stack trace today.

**5 · There is no byte order.** UTF-16 and UTF-32 each have a little-endian and a big-endian spelling, so a file needs a [BOM](../../03_Encodings/byte_order_and_bom/README.md) to say which — a magic prefix that then turns up in CSV headers, JSON parsers and shell scripts forever. UTF-8 has one spelling, and needs no mark. (Windows tools write one anyway. That is a separate scar.)

**6 · Byte order equals code-point order.** Sorting UTF-8 bytes gives the same order as sorting code points, so a byte-wise sort, a `memcmp`, a binary search or a plain B-tree index is *already correct* without knowing any Unicode. UTF-16 gets this wrong: surrogates start at `D800`, so every character above `U+FFFF` sorts before the ones from `E000` to `FFFF`.

**And the bill.** A CJK character is three bytes in UTF-8 and two in UTF-16 or Shift-JIS — a 50% surcharge on exactly the text that needed the most room. That was argued loudly and at length, mostly from Japan, and it was a real cost fairly stated. It lost to the six properties above, and the last section of the Python program prints the numbers rather than waving at them.

## In Python

<!-- output:why_utf8_won_py -->
*Verified output of [`why_utf8_won_py.py`](examples/why_utf8_won_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. AN ASCII FILE IS ALREADY A UTF-8 FILE
------------------------------------------------------------------------
   'id,name,city'
     as ascii : 69 64 2c 6e 61 6d 65 2c 63 69 74 79
     as utf-8 : 69 64 2c 6e 61 6d 65 2c 63 69 74 79
     identical: True
     as utf-16: 00 69 00 64 00 2c 00 6e 00 61 00 6d 00 65 00 2c 00 63 00 69 00 74 00 79
   Every file, tool and protocol that already spoke ASCII kept working
   on the day UTF-8 arrived. Nothing else on this page could say that,
   and that alone is most of the reason it won.

2. NO FRAGMENT OF A CHARACTER CAN EVER LOOK LIKE ASCII
------------------------------------------------------------------------
   'id,Łódź,日本語,😀,ok'
     utf-8 : 28 bytes, 9 of them below 0x80
     those bytes, as characters : 'id,d,,,ok'
     the ASCII characters of the text : 'id,d,,,ok'
     the same, in the same order: True
   In UTF-8 a byte below 0x80 is ALWAYS a whole ASCII character, never
   half of something else. So splitting on ',' or '/' cannot go wrong.

   The rival could not promise that. In Shift-JIS the second byte of a
   two-byte character may be any of 0x40..0xFC — which includes ASCII:
     83 5c is 'ソ', and its second byte is '\\'
     93 5c is '貼', and its second byte is '\\'
   A path splitter looking for a backslash found one INSIDE a character.
   That is the '5C problem', and it broke Japanese Windows for years.

3. SELF-SYNCHRONISING: YOU CAN START READING ANYWHERE
------------------------------------------------------------------------
   Every byte says what it is, from its top bits alone:
     0xxxxxxx  a whole ASCII character
     110xxxxx  start of a 2-byte character   1110xxxx  start of 3
     11110xxx  start of a 4-byte character   10xxxxxx  a CONTINUATION

   'Łódź' -> c5 81 c3 b3 64 c5 ba
     byte 0  0xC5  11000101  start of a 2-byte character
     byte 1  0x81  10000001  continuation
     byte 2  0xC3  11000011  start of a 2-byte character
     byte 3  0xB3  10110011  continuation
     byte 4  0x64  01100100  ascii
     byte 5  0xC5  11000101  start of a 2-byte character
     byte 6  0xBA  10111010  continuation

   So a reader dropped into the middle can find the next character by
   skipping continuation bytes — at most 3 of them:
     start at byte 0: skip 0, then read 'Łódź'
     start at byte 1: skip 1, then read 'ódź'
     start at byte 2: skip 0, then read 'ódź'
     start at byte 3: skip 1, then read 'dź'
     start at byte 4: skip 0, then read 'dź'
     start at byte 5: skip 0, then read 'ź'
     start at byte 6: skip 1, then read ''
   Shift-JIS and EUC-JP cannot be entered in the middle at all: you
   must read from the start of the file to know which byte is which.
   (UTF-16 can, but only once you know where the 2-byte boundaries are,
   and a byte stream does not tell you that either.)

4. SELF-VALIDATING: A WRONG-TABLE FILE CAN BE DETECTED
------------------------------------------------------------------------
   A Latin-1 file : 63 61 66 e9 20 61 75 20 6c 61 69 74
     read as utf-8   -> UnicodeDecodeError: invalid continuation byte at byte 3
     read as latin-1 -> 'café au lait'

   Now the other direction, which is the important one:
   A UTF-8 file   : 63 61 66 c3 a9 20 61 75 20 6c 61 69 74
     read as latin-1 -> 'cafÃ© au lait'  (no error!)
   Latin-1 maps all 256 bytes, so it can NEVER report a problem. It
   accepts every file and quietly returns the wrong text — which is
   exactly why mojibake was silent for twenty years. UTF-8's structure
   makes most wrong guesses fail loudly, on the first bad byte.

5. NO BYTE ORDER, SO NO BOM AND NO VARIANTS
------------------------------------------------------------------------
   'Hi' in utf_8      -> 48 69
   'Hi' in utf_16_le  -> 48 00 69 00
   'Hi' in utf_16_be  -> 00 48 00 69
   'Hi' in utf_16     -> ff fe 48 00 69 00
   'Hi' in utf_32_le  -> 48 00 00 00 69 00 00 00
   'Hi' in utf_32     -> ff fe 00 00 48 00 00 00 69 00 00 00
   UTF-8 has one spelling. UTF-16 and UTF-32 have two each, so they
   need a Byte Order Mark to say which — a magic prefix that then
   leaks into CSV headers, JSON parsers and shell scripts forever.

6. SORTING BY BYTES == SORTING BY CODE POINT
------------------------------------------------------------------------
   by code point : U+0041 U+007A U+00E9 U+FF01 U+10000 U+1F600
   by utf-8 bytes: U+0041 U+007A U+00E9 U+FF01 U+10000 U+1F600
   by utf-16 byte: U+0041 U+007A U+00E9 U+10000 U+1F600 U+FF01
   UTF-8's byte order and Unicode's numbering agree, so a sort, a
   binary search or a B-tree index over raw bytes is already correct.
   UTF-16 gets it wrong: surrogates start at D800, so every character
   above U+FFFF sorts BEFORE the ones from E000 to FFFF.

7. WHAT IT COSTS, STATED HONESTLY
------------------------------------------------------------------------
   ASCII     'hello world'  utf-8  11   utf-16  22   utf-8 wins
   Polish    'Łódź'         utf-8   7   utf-16   8   utf-8 wins
   Japanese  '日本語です'   utf-8  15   utf-16  10   utf-16 wins
   UTF-8 charges 3 bytes for a CJK character where UTF-16 and the old
   Japanese tables charged 2 — a 50% bill on exactly the text that
   needed the most storage. That is a real cost, it was argued about
   loudly, and it lost to the six properties above.
```
<!-- /output -->

## In Rust

Python can *ask* whether bytes are valid UTF-8. Rust makes it the difference between two types: `&[u8]` is bytes, `&str` is bytes that have already been checked, and `from_utf8` is the only safe door between them. Two of the refusals below are security rather than pedantry.

<!-- output:why_utf8_won_rs -->
*Verified output of [`why_utf8_won_rs.rs`](examples/why_utf8_won_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A &str IS BYTES PLUS A PROMISE
------------------------------------------------------------------------
   "Łódź"
   s.len()          = 7   <- BYTES, not characters
   s.chars().count()= 4   <- characters
   s.as_bytes()     = [c5, 81, c3, b3, 64, c5, ba]
   The promise is the whole difference between &str and &[u8]:
   every &str in a running program is already valid UTF-8, because
   there is no way to make one that is not without saying `unsafe`.

2. THE DOOR: from_utf8 CHECKS, AND SAYS WHERE IT FAILED
------------------------------------------------------------------------
   b"caf\xc3\xa9" (real UTF-8)        -> Ok("café")
   b"caf\xe9 au lait" (Latin-1)       -> Err: valid up to byte 3, 1 byte(s) rejected there
   b"caf\xc3" (truncated)             -> Err: valid up to byte 3, ended mid-character
   `valid_up_to` is the byte offset where the file stops making
   sense — which is how a tool can report the LINE of the problem
   instead of 'this file is not UTF-8, good luck'.

3. TWO REJECTIONS THAT ARE SECURITY, NOT PEDANTRY
------------------------------------------------------------------------
   c0 80  (overlong NUL)              -> Err: valid up to byte 0, 1 byte(s) rejected there
   2f              (a real slash)     -> Ok("/")
   c0 af  (overlong slash)            -> Err: valid up to byte 0, 1 byte(s) rejected there
   Every code point has exactly ONE valid UTF-8 spelling. A decoder
   that accepts the padded spellings lets `c0 af` slip a '/' past a
   filter that was looking for 2f — which is how directory-traversal
   attacks worked in 2001. Rust's `from_utf8` refuses them.

   ed a0 80  (a lone surrogate)       -> Err: valid up to byte 0, 1 byte(s) rejected there
   Surrogates are UTF-16's plumbing, not characters. UTF-8 has no
   room for them, so text that came from a careless UTF-16 system
   is caught here rather than three systems later.

4. WHEN YOU CANNOT REFUSE: from_utf8_lossy
------------------------------------------------------------------------
   bytes  [53, 61, 6c, 65, 73, 20, 72, 65, 70, 6f, 72, 74, 3a, 20, 63, 61, 66, e9, 20, ff, 20, 74, 6f, 74]
   lossy  "Sales report: caf� � totals"
   Each bad byte becomes U+FFFD, the replacement character. Use it
   for a log line a human will read; never for data you will write
   back out, because the original bytes are gone for good.

5. SELF-SYNCHRONISING, IN THE TYPE SYSTEM
------------------------------------------------------------------------
   char_indices(): 0:Ł 2:ó 4:d 5:ź
   is_char_boundary: 0:Y 1:n 2:Y 3:n 4:Y 5:Y 6:n 7:Y
   Slicing at a boundary works; slicing inside a character does not.
   `get` asks instead of panicking, which is how to do it in a tool:
     s.get(0..2) = Some("Ł")
     s.get(0..1) = None
     s.get(2..4) = Some("ó")

6. AND ASCII STILL COSTS ONE BYTE
------------------------------------------------------------------------
   bytes  5   chars  5   ascii-only true    "hello"
   bytes  7   chars  4   ascii-only false   "Łódź"
   bytes  9   chars  3   ascii-only false   "日本語"
   `is_ascii()` is a fast path a great deal of real code takes: if a
   string is ASCII, byte indexing and character indexing are the same
   thing, and UTF-8 is what makes that shortcut safe to check for.
```
<!-- /output -->

## In the terminal

The practical half: the tools you already have, under `LC_ALL=C`, with no Unicode awareness at all, getting the right answer anyway.

<!-- output:why_utf8_won_sh -->
*Verified output of [`why_utf8_won_sh.sh`](examples/why_utf8_won_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ASCII-ONLY TOOLS, ON TEXT THEY HAVE NEVER HEARD OF
   The row: id,Łódź,日本語,ok

$ printf '%s\n' "$ROW" | cut -d, -f2
Łódź

$ printf '%s\n' "$ROW" | cut -d, -f3
日本語

$ printf '%s\n' "$ROW" | awk -F, '{print NF " fields"}'
4 fields

$ printf '%s\n' "$ROW" | grep -c 'id'
1
   cut, awk and grep split on the byte 0x2c. In UTF-8 that byte can only
   ever be a real comma, so none of them can cut a character in half.

2. THE SAME ROW AS UTF-16, HANDED TO THE SAME TOOLS

$ printf '%s' "$ROW" | iconv -f UTF-8 -t UTF-16LE | xxd -p | head -2
690064002c004101f30064007a012c00e5652c679e8a2c006f006b00
   cut -d, -f2 on that gives : 004101f30064007a010a
   Bytes, not text — and every other byte is 00, which is what ends a
   string in C. Adopting UTF-16 in 1993 would have meant rewriting every
   tool on the machine on the same day. Adopting UTF-8 meant rewriting
   none of them.

3. SORTING BY RAW BYTES IS ALREADY THE RIGHT ORDER
   Five characters, deliberately out of order, sorted by BYTE value
   with no locale at all:

$ printf 'z\né\nA\n日\n0\n' | LC_ALL=C sort
0
A
z
é
日
   That is exactly their Unicode order: 0 (U+0030), A (U+0041),
   z (U+007A), é (U+00E9), 日 (U+65E5). A byte sort, a byte-wise binary
   search and a plain B-tree index are all correct on UTF-8 without
   knowing a thing about Unicode.

4. AND THE COUNTING TRAP THAT NEVER WENT AWAY

$ printf '%s' 'Łódź' | wc -c | tr -d ' '
7
   Seven bytes, four letters. wc -c counts bytes and always did; it is
   the database column, the fixed-width field and the substring that
   still need to be told which of the two they meant.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** The properties show up as things you never had to think about. `line.split(',')` on a `bytes` object is safe because of property 2. `sorted(names)` matches `sorted(names, key=lambda s: s.encode('utf-8'))` because of property 6 — which means a database's byte-ordered index and Python's `sorted()` agree, as long as nobody asked for locale collation. And `UnicodeDecodeError` is property 4 doing its job: it is not Python being awkward, it is the *only* encoding on the list that could have told you.

**ABAP.** A Unicode SAP system holds text as UTF-16 internally, so properties 5 and 6 are exactly the ones you do not get: the internal form has a byte order, and a byte-wise sort of it is not code-point order above `U+FFFF`. This does not usually surface, because you sort with `SORT` on character fields and the kernel handles it — but it does surface the moment you hash, checksum, or compare an `xstring` that came from `cl_abap_codepage=>convert_to`. Convert to UTF-8 at the boundary for anything that will be hashed, signed, or compared byte-wise with an outside system, and let the internal representation stay the kernel's business. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 09_History/why_utf8_won/examples
python3 why_utf8_won_py.py
bash why_utf8_won_sh.sh
rustc --edition 2024 why_utf8_won_rs.rs -o /tmp/utf8won && /tmp/utf8won
```

Without the machine: you are handed the bytes `C3 A9 64` and told to find the start of the second character. Which byte, and how did you know without looking at anything before it? Then: `E9 64` arrives instead. Why can you be sure that is *not* UTF-8, and what does that certainty buy you that Latin-1 never could?

## See also

- [From the telegraph to Unicode](../from_telegraph_to_unicode/README.md) — the six eras this ended
- [UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) — doing the bit-packing yourself, which is the checkpoint
- [What to do today](../../10_Best_Practices/README.md) — the rules that follow from these properties
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — the encoding that lost, in detail
- [UTF-8 history, Rob Pike ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/utf-8-history.txt) — the primary source, two pages long
- [UTF-8 Everywhere ↗](https://utf8everywhere.org/) — the manifesto, aimed mostly at Windows codebases
