# The topic map — every keyword this subject has

**Level:** reference

**One line:** An inventory, not a lesson: every term the subject of this library touches, imported from a list Adam pasted on 2026-09-06 and then extended with what that list was missing — so that "is there a page for X?" and "what have we not thought about yet?" have one place to be asked.

## How to read this page

Three things to know before using it.

**This is a backlog, not teaching text.** Every other page here carries a claim that a program checked ([CONTRIBUTING.md](CONTRIBUTING.md)). Nothing on *this* page has been through that. A hook written beside a term is **a claim to verify when the page is written**, not a fact this library has established — several of them will turn out to be wrong, which is the normal outcome and the reason the pages get written at all.

**It is a different job from [GLOSSARY.md](GLOSSARY.md).** The glossary defines the terms a reader meets in the written lessons, and every row links to the page that earns it. This page lists terms whether or not anything here explains them — most of them nothing here explains.

**Characters are named, not shown.** Outside the cast in [CAST.md](CAST.md), a character is written as `U+XXXX` plus its name. That is the house rule ([the cast](CONTRIBUTING.md)), and on a page this long it is also self-defence: a list that mints 300 one-off characters teaches nobody anything and would put a bidi control into a file that is meant to warn about them.

Each section carries a **scope** tag:

| Tag | Meaning |
|---|---|
| **core** | This library's subject. A gap here is a page that should exist. |
| **adjacent** | Real, and it touches text, but the lesson belongs in a sibling library ([Python ↗](https://masiarek.github.io/python-learning-library/), [Rust ↗](https://masiarek.github.io/rust-learning-library/)) or nowhere yet. Listed so the boundary is a decision rather than an oversight. |
| **reference** | Worth being able to name. Not worth a page. |

**Imported** runs list the terms exactly as received, compressed to one line per group so the whole list stays scannable. **Missing — add** is what was not in it.

---

## What the imported list got wrong

Corrections first, because the list is otherwise good enough to be trusted, and a good list is where a wrong fact does the most damage. Measured on this Mac, 2026-09-06, `python3` 3.14.7 carrying UCD 16.0.0 — the same frozen-table trick [The table has a version](02_Characters/the_table_has_a_version/README.md) uses.

| The list says | Measured | So |
|---|---|---|
| *"Unicode stability policy — assigned characters will never be removed **or have their properties changed**"* | **185 code points** changed `General_Category` between UCD 3.2 and 16.0. `U+00AD SOFT HYPHEN` went `Pd` → `Cf`; 85 went `Lo` → `Lu` | Half true, and the false half is the load-bearing one. **Name** and non-reuse are guaranteed; **General_Category is not on the stability list.** This is the distinction [The table has a version](02_Characters/the_table_has_a_version/README.md) is built on |
| *"Windows-1252 — superset of Latin-1"* | Byte `0x80` decodes as `€` in cp1252 and as `U+0080` (a C1 control) in Latin-1 | Not a superset — a **replacement** of Latin-1's C1 block. That difference is the entire subject of the [Windows-1252 vs Latin-1](07_Real_Data/windows_1252_vs_latin1/README.md) stub |
| *"Tertiary Ideographic Plane (TIP) — Plane 3; additional CJK **compatibility** ideographs"* | `U+2F800` is `CJK COMPATIBILITY IDEOGRAPH-2F800` — Plane **2**. Plane 3 begins at `U+30000`, Extension G | Plane 3 holds *unified* ideographs (Ext G/H/I). The compatibility ideographs are in Plane 2 |
| *"As of Unicode 15.1: approximately 149,000+ assigned code points"* | UCD 16.0: **155,063** assigned excluding the 137,468 private-use and 2,048 surrogate slots | Stale by a release, and the number depends on a definition the sentence does not give. Quote it with its definition or not at all |
| §1.4 *"Java stores all String objects as UTF-16 internally"* vs §9.2 *"compact strings — Latin-1 stored as byte arrays"* | — | The list contradicts itself. JDK 9+ is the second one |
| *"Ctrl+D — sending an EOF **signal** on stdin"* | — | Not a signal. It makes the terminal flush the line buffer; a flush of zero bytes is what `read()` reports as EOF. The list half-says this in its own parenthesis |

Two more that are not wrong, only incomplete, and both are traps this library has already been bitten by: **`isascii()`** is not portable C (it left POSIX in 2008), and **`iconv` is not one validator** — it accepts sequences above `U+10FFFF` that Python and Rust reject, which is measured on [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md).

---

## 1. Character sets and encodings

### 1.1 ASCII — **core**

*Covered:* [A character is a number](02_Characters/a_character_is_a_number/README.md) · [Control characters](02_Characters/control_characters/README.md) · [The NUL byte](02_Characters/the_nul_byte/README.md) · [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) · [Rotation is not encryption](02_Characters/rotation_is_not_encryption/README.md)

**Imported:** ASCII · 7-bit ASCII · ASCII table · printable characters (32–126) · non-printable characters · control range 0–31 · digits 48–57 · uppercase 65–90 · lowercase 97–122 · punctuation · SPACE (32) · extended ASCII · code page · high ASCII · ISO 646 · 7-bit clean · ASCII-compatible encoding · ASCII art · ASCII folding · ROT13 · `atoi` / `atof` · `isascii()` · `isprint()`

**Missing — add:**

- **ASA X3.4-1963 → USAS X3.4-1967 → ANSI X3.4-1968** — three ASCII standards, not one. 1963 had no lowercase. Dates matter because "ASCII" in a 1970s manual is not today's table.
- **The `0x20` bit trick** — upper and lower differ by one bit, which is why `c | 0x20` lowercases and why the alphabet starts at 65 and not 1. The single most useful thing about the layout.
- **ISO 646 national variants** — the same byte, a different letter per country: `0x23` is `#` in the US and a pound sign in the UK, `0x5C` is a backslash in the US and a yen sign in JIS X 0201. **This is the ancestor of the Shift-JIS `5C` problem** already on [Why UTF-8 won](09_History/why_utf8_won/README.md).
- **C trigraphs and digraphs** — `??/` for backslash existed *because* of those national variants. Removed in C++17, still in C.
- **Delete is not a control** — `0x7F` is all-bits-set because on paper tape you could only punch more holes. Explains why DEL sits at the end and not at 32.
- **Sixbit / RADIX-50 / Fieldata / Hollerith / BCDIC** — the pre-ASCII encodings, worth naming once so "before ASCII" is not a blank.
- **`strcasecmp` and the ASCII-only shortcut** — every language has one caseless compare that is honest about being ASCII-only (Rust's `eq_ignore_ascii_case` says it in its name) and one that is not.
- **`isprint()` is locale-dependent** — the reason a macOS `od -a` dump disagrees with a Linux one, measured on [Inspecting a file](06_Terminal/inspecting_a_file/README.md).

### 1.2 Unicode — **core**

*Covered:* [Unicode code points](02_Characters/unicode_code_points/README.md) · [The table has a version](02_Characters/the_table_has_a_version/README.md) · [Preparing a string](02_Characters/preparing_a_string/README.md) · [Confusables and scripts](02_Characters/confusables_and_scripts/README.md) · [Unicode in identifiers](02_Characters/unicode_in_identifiers/README.md)

**Imported:** Unicode · Unicode Consortium · the Standard · UCS / ISO-IEC 10646 · plane · BMP · SMP · SIP · TIP · SSP · Private Use Areas · block · category · version · scalar value · UCD · character name · UBA / BiDi · RTL · LTR · emoji · math symbols · currency symbols · diacritics · Han unification · CJK Unified Ideographs · UTF · stability policy · Age property · name alias · deprecated character · noncharacter

**Missing — add:**

- ~~**The Unicode character encoding model (UTR #17)**~~ — **written 2026-09-08** as [An encoding is four layers](03_Encodings/the_encoding_model/README.md). The count in this line was wrong and the page says so: UTR #17 defines **four** levels — abstract character repertoire → coded character set → character *encoding form* (code units) → character *encoding scheme* (bytes, hence byte order) — and puts the transfer encoding syntax deliberately *outside* them, alongside a sixth concept, the character map, which is what an IANA `charset=` name really identifies. Five is Gillam's count, not the standard's. **"UTF-16" names a form *and* a scheme**, which the standard states in as many words; `UTF-16LE` names only the scheme, and half the BOM confusion is that distinction missing.
- **The 16-bit assumption and its collapse** — Unicode 1.0 promised every character fit in 16 bits. Unicode 2.0 (1996) broke that promise, and UTF-16 with its surrogates is the retrofit. Explains why Java, JavaScript, Windows and Qt all have the same scar in the same place.
- **`U+FFFD` substitution is not one algorithm** — how many replacement characters a bad sequence produces differs between the WHATWG "maximal subpart" rule and older implementations. Two decoders, one input, different output lengths: a [parser differential](12_Adversarial/parser_differentials/README.md) hiding inside the error path.
- **Ill-formed vs irregular sequences** — conformance vocabulary; the difference between "must reject" and "should not produce".
- **`Script_Extensions`** — a character can belong to several scripts. The single-`Script` property is a simplification that [Confusables and scripts](02_Characters/confusables_and_scripts/README.md) leans on.
- **Standardized Variation Sequences and the IVD** — `U+FE00`–`U+FE0F` plus the Ideographic Variation Database: how one code point renders as a specific national glyph.
- **Tag characters (`U+E0000` block)** — the deprecated language tags, now reused for subdivision flags — **and today the main carrier of invisible text in prompt injection**. Deserves a page in [12_Adversarial](12_Adversarial/README.md).
- **`Default_Ignorable_Code_Point`** — the property that says "render nothing, do not draw a box". The formal answer to "why is this character invisible".
- **CJK Extensions A–I, Nushu, Tangut, Egyptian hieroglyphs** — what actually fills the supplementary planes.
- **ConScript Unicode Registry (CSUR)** — the PUA's shadow standard (Tengwar, Klingon). The best available answer to "who decides what a private use area means": nobody, by design.
- **The Unicode roadmap and encoding proposals** — how a script gets in, and why the backlog is measured in decades.
- **Unihan** — the largest database in the UCD, with its own UAX (#38) and its own source-reference model (`kIRG*`).
- **"Unicode is not a font" / "Unicode does not encode glyphs"** — the two sentences that resolve most beginner confusion, and neither is in the list.

### 1.3 UTF-8 — **core**

*Covered:* [UTF-8 by hand](03_Encodings/utf8_by_hand/README.md) · [Overlong sequences](03_Encodings/overlong_sequences/README.md) · [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md) · [Why UTF-8 won](09_History/why_utf8_won/README.md) · [UTF-8 everywhere](10_Best_Practices/utf8_everywhere/README.md)

**Imported:** UTF-8 · 1/2/3/4-byte sequences · continuation byte · leading byte · overlong encoding · UTF-8 BOM · validity · MUTF-8 · CESU-8 · WTF-8 · RFC 3629 · UTF-8 Everywhere

**Missing — add:**

- **Self-synchronisation** — you can seek into the middle of a UTF-8 file and find the next character boundary by inspecting one byte. The property Ken Thompson's placemat design was actually for, and the one Tribit v2 asks Adam to reinvent ([Tribit](08_Build_Your_Own/tribit/README.md)).
- **No byte of a multi-byte character can be mistaken for ASCII** — the property that makes every ASCII-assuming tool keep working, and the one Shift-JIS lacks.
- **Byte-order-free by construction** — UTF-8 has no endianness, which is why its "BOM" marks nothing. Already on [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md); belongs in the term list too.
- **`F4 90 80 80` and the RFC 3629 cap** — the 2003 restriction to `U+10FFFF`, and the fact that `iconv` never got the memo. Measured; on [Validation is a boundary](03_Encodings/validation_is_a_boundary/README.md).
- **UTF-8 in DFA form** — Björn Höhrmann's ~40-line table-driven validator, and Bob Steagall's SIMD version. The bridge from "the rule" to "the code everyone actually ships".
- **`simdutf` / `simdutf8`** — validation at memory bandwidth. Rust-goal relevant, and a concrete answer to "does this cost anything".
- **UTF-8B / surrogateescape** — the trick that round-trips undecodable bytes through a `str`, so a filename that is not UTF-8 can still be opened. **PEP 383 in Python; the reason `os.fsdecode` exists.** Written 2026-09-07 as [Bytes that are not text](04_Python/surrogateescape/README.md), in chapter 4 rather than chapter 7 — the mechanism is a Python one, and the real-data chapter can link it.
- **Modified UTF-8's real home** — the JNI and the `.class` constant pool, not "Java strings".
- **The maximum byte length of a character** — 4 under RFC 3629, 6 under the original design. Both numbers are in old code.

### 1.4 UTF-16 — **core**

*Covered:* stub: [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) · [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md)

**Imported:** UTF-16 · code unit · BMP character · surrogate pair · high / low surrogate · UTF-16LE · UTF-16BE · UTF-16 BOM · `wchar_t` · Java internal encoding · Windows `WCHAR`

**Missing — add:**

- **UCS-2 is not UTF-16** — UCS-2 cannot represent anything above the BMP at all. Systems that say UTF-16 and mean UCS-2 are where lone surrogates come from.
- **Lone surrogates survive in real systems** — Windows filenames, JavaScript strings, JSON documents. **`json.dumps` of `😀` emits a surrogate pair in a format that is UTF-8 by RFC 8259**, and `json.loads('"\ud800"')` succeeds: measured 2026-09-06.
- **`isWellFormed()` / `toWellFormed()`** — the 2024 JavaScript answer to lone surrogates; the shortest proof that the problem is still live.
- **WTF-8 is where Rust keeps them** — `OsString` on Windows. The reason `Path` is not `String`.
- **UTF-16 is *still* the wire format of half the world** — Windows APIs, NTFS names, SQL Server `NVARCHAR`, Java/JS/C# in memory. "UTF-8 everywhere" is advice, not a description.
- **Endianness detection without a BOM** — the statistical hack (count null bytes in even vs odd positions) every text editor ships and none documents.

### 1.5 UTF-32 / UCS-4 — **core (small)**

**Imported:** UTF-32 · UTF-32LE / BE · UCS-4 · UTF-32 BOM · direct indexing · memory overhead

**Missing — add:**

- **`FF FE 00 00` begins with the whole of `FF FE`** — so a sniffer that checks two bytes reads every UTF-32LE file as UTF-16 and succeeds. Measured; on [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md).
- **O(1) indexing buys less than it looks** — a code point is still not a character, so random access lands you inside a grapheme cluster. The argument against UTF-32 that is not about memory.
- **`wchar_t` is UTF-32 on Unix and UTF-16 on Windows** — which is why `wchar_t` is not portable and `char32_t` exists.

### 1.6 ISO-8859 family — **core**

*Covered:* [Code pages](02_Characters/code_pages/README.md)

**Imported:** ISO-8859-1 Latin-1 · -2 Latin-2 · -3 Latin-3 · -4 Latin-4 · -5 Cyrillic · -6 Arabic · -7 Greek · -8 Hebrew · -9 Latin-5 · -10 Latin-6 · -11 Thai · -13 Latin-7 · -14 Latin-8 · -15 Latin-9 · -16 Latin-10 · single-byte encoding · 8-bit character set

**Missing — add:**

- **There is no ISO-8859-12** — reserved for Devanagari, abandoned. The gap is a real question a reader will have.
- **Latin-1 is the only encoding that cannot fail to decode** — all 256 bytes are assigned, which makes it the universal "decode anything" fallback *and* the reason mojibake so often reaches you as Latin-1 specifically.
- **ISO-8859-1 vs the `latin1` label in HTTP** — the WHATWG Encoding Standard says a document labelled `iso-8859-1` **must be decoded as windows-1252**. Reality overruled the standard, in a standard.
- **Latin-1 as the first 256 code points of Unicode** — not a coincidence; a deliberate design decision, and the reason `bytes.decode('latin-1')` is the same as "treat each byte as a code point".
- **Latin-9 exists because of one character** — the euro. The story is a whole lesson about what "we'll just add it" costs.

### 1.7 Windows code pages — **core**

*Covered:* [Code pages](02_Characters/code_pages/README.md) · stub: [Windows-1252 vs Latin-1](07_Real_Data/windows_1252_vs_latin1/README.md)

**Imported:** Windows-1252 · -1250 · -1251 · -1253 · -1254 · -1255 · -1256 · -1257 · -1258 · CP437 · CP850 · CP932 · CP936 GBK · CP949 · CP950 · ANSI code page · OEM code page · NLS · active code page · `SetConsoleCP` / `SetConsoleOutputCP` · `chcp` · code page 65001

**Missing — add:**

- **"ANSI" is a misnomer** — ANSI never standardised these. Microsoft's own docs now say so. Naming a thing wrong for 30 years is itself the lesson.
- **Best-fit mapping** — Windows will silently convert `U+2018` to `'` when encoding to a code page that lacks it. **A quote mark appearing out of nowhere is a security bug**, not a convenience; it is how a filter that checked the original string gets bypassed. Named on [The check that ran too early](12_Adversarial/canonicalize_then_check/README.md) as described-not-demonstrated — it deserves its own page.
- **`WC_ERR_INVALID_CHARS`** — without it, `MultiByteToWideChar` silently substitutes. The default is the unsafe one.
- **The UTF-8 process manifest (`activeCodePage`)** — Windows 10 1903+; makes `CP_ACP` mean UTF-8 for one process. The modern answer, and almost nobody knows it exists.
- **`chcp 65001` breaks things** — historically it did, in specific, documented ways (`ReadFile` on the console). Worth stating *what* broke rather than repeating the folklore.
- **CP437's line-drawing characters are the reason a `.txt` from 1990 looks like that** — and the reason `U+2500`–`U+257F` exists in Unicode at all.

### 1.8 EBCDIC — **core, because SAP**

**Imported:** EBCDIC · CP037 · CP500 · CP1047 · IBM mainframe · collation difference · AS/400 (IBM i) · packed decimal · CICS · JCL · EBCDIC-to-ASCII conversion

**Missing — add:**

- **The euro-updated code pages 1140–1149** — every CP037-family page got a twin with the euro at `0x9F`. If a mainframe file's currency symbol is wrong, this pair is why.
- **The letters are not contiguous** — `A`–`I`, `J`–`R`, `S`–`Z` sit in three runs with gaps. `for (c = 'A'; c <= 'Z'; c++)` is a bug on EBCDIC, and it is the sharpest possible demonstration that character order is a table's opinion.
- **CP1047 vs CP037 differ in the square brackets** — which breaks C source on z/OS specifically. The `5C` problem's mainframe cousin.
- **NL (`0x15`) vs LF (`0x25`)** — EBCDIC has both, and the mapping to `U+0085` NEL is where line endings stop being a two-way choice.
- **Packed decimal / zoned decimal / COMP-3** — a "number" that is neither text nor binary integer, with the sign in the last nibble. Every mainframe extract has one, and no `iconv` will help.
- **SAP's non-Unicode era, MDMP, and SPUMG/SUMG** — the conversion projects. Verify against the system before quoting any number ([sap-library ↗](https://masiarek.github.io/sap-library/) provenance rule).

### 1.9 East Asian encodings — **core**

**Imported:** Shift JIS · SJIS double-byte sequence · CP932 · EUC-JP · ISO-2022-JP · Big5 · Big5-HKSCS · GB2312 · GBK · GB18030 · EUC-KR · JOHAB · ISO-2022-KR · ISO-2022-CN · DBCS · MBCS · CJK · Hanzi · Kanji · Hangul

**Missing — add:**

- **JIS X 0201, 0208, 0212, 0213** — the character *sets* that the encodings above encode. Set and encoding are different things, and Japanese is where that distinction is unavoidable.
- **Half-width katakana** — a whole script duplicated at half width for teletype reasons, now `NFKC`'s most common real-world job.
- **The `5C` problem, stated once and properly** — a Shift-JIS trail byte can be `0x5C`, so a byte-wise scan finds a backslash inside a character. Already the argument on [Why UTF-8 won](09_History/why_utf8_won/README.md); it is also **the GBK injection on [Two readers, one byte string](12_Adversarial/parser_differentials/README.md)**, which is the same bug in Chinese.
- **GB18030 is mandatory in China and is Unicode-complete** — a legally-required encoding that can represent everything. The exception to "legacy encodings are subsets".
- **ISO-2022 is stateful** — escape sequences switch the meaning of every later byte. **A stateful encoding cannot be seeked into, cannot be concatenated, and can be truncated into a different document.** The strongest possible argument for stateless UTF-8, and it is missing from the list's framing entirely.
- **Emoji came from Japanese carrier sets** — DoCoMo/KDDI/SoftBank, in Shift-JIS private-use space, unified into Unicode 6.0 in 2010. The reason emoji have "compatibility" mappings at all.
- **Han unification's dissent** — the "Han unification is wrong" argument, Source Han / Noto CJK, and the HTML `lang` attribute as the practical workaround. Name the controversy; don't referee it.

### 1.10 Other legacy and specialty encodings — **reference**

**Imported:** KOI8-R · KOI8-U · TIS-620 · Mac OS Roman · VISCII · Baudot · Murray code · Morse · BCD · Quoted-Printable · uuencoding · yEnc · HTML named entity · numeric character reference · percent-encoding · MIME Content-Transfer-Encoding · Punycode

**Missing — add:**

- **KOI8-R's design is the point** — the Cyrillic letters are ordered so that **stripping the high bit yields readable Latin transliteration**. An encoding designed for a lossy channel. Beautiful, and one line.
- **ATASCII, PETSCII, ZX80, Videotex, Teletext** — home-computer character sets; where the box-drawing and "graphics characters" habit comes from.
- **DEC MCS, HP Roman-8, NeXT, Atari ST, Amiga** — the pre-standard 8-bit tables.
- **MARC-8 and ANSEL** — library-catalogue encodings, still live in ILS systems, with *combining marks that precede* their base character. The one encoding that puts the accent first.
- **ISCII / InScript** — the Indic answer before Unicode.
- **VSCII / VNI / VPS** — three incompatible Vietnamese encodings, which is why Vietnamese text is the classic mojibake sample.
- **KPS 9566** — North Korea's national encoding, with code points reserved for named individuals. A reminder that a character set is a political document.
- **TRON code and Mojikyo** — the "Unicode is not enough for Japanese" alternatives.
- **ASCII Braille and the Braille Patterns block** — 8 dots map to 256 code points in `U+2800`, which makes Braille the tidiest encoding in Unicode.

### 1.11 Base64 and binary-to-text — **core (small)**

*Covered:* [Binary to text](03_Encodings/binary_to_text/README.md) · [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md) · [The alphabet is not the encoding](03_Encodings/base32_alphabets/README.md)

**Imported:** Base64 · alphabet · padding · algorithm · Base64URL · MIME Base64 · Base32 · Base16 · Base85 / ASCII85 · Base58 · Base62 · data URI · RFC 4648 · padding removal

**Missing — add:**

- ~~**Base64 is not encryption and not compression**~~ · ~~**Base64 has no charset**~~ · ~~**Non-canonical Base64**~~ · ~~**JOSE / JWT base64url without padding**~~ · ~~**`base64 -d` tolerance differs by implementation**~~ — all written 2026-09-06 on [Binary to text](03_Encodings/binary_to_text/README.md), which also added the split the imported list did not have: **does the base divide a power of two?** Base16/32/64/Ascii85 have a fixed quantum and stream; Base58/62/36 are big-integer division over the whole message, and the reference tables sort them together on an efficiency percentage as though the difference were bandwidth.
- ~~**Crockford Base32**~~, and with it base32hex and z-base-32 — written 2026-09-07 on [The alphabet is not the encoding](03_Encodings/base32_alphabets/README.md), which found the thing the imported list implies is not true: these are *not* all one encoding with four alphabets. Three are (a 32-character `tr` converts between them), but Crockford's specification is a notation for **numbers**, so it zero-extends the high end where RFC 4648 pads the low end, and the two readings of the same bytes disagree at every length not divisible by five. **Z85, Base45 (EU digital covid certificates), Bech32, Base58Check, multibase** are still open — Bech32's checksum and Base58Check's leading-`1` rule are named on the binary-to-text page; the rest are not, and Crockford's own **check symbol** (modulo 37, five extra symbols) is named but not implemented anywhere here.
- **PEM armor, BinHex, MacBinary** — the historical wrappers.
- **Data URIs** — `data:image/png;base64,…`, where the charset question and the base64 question sit in one string, and the media type is the only thing that answers either.

### 1.12 Hexadecimal and numeric bases — **core**

*Covered:* [Hex is a shorthand](01_Bits_and_Bytes/hex_is_a_shorthand/README.md) · [Hex: a number, or a picture of bytes](01_Bits_and_Bytes/hex_number_or_bytes/README.md) · [Reading a hex dump](01_Bits_and_Bytes/reading_a_hex_dump/README.md) · [A byte is eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) · [Why hex and not octal](01_Bits_and_Bytes/hex_is_a_shorthand/README.md#why-hex-and-not-octal) · [Writing the literal](01_Bits_and_Bytes/hex_is_a_shorthand/README.md#writing-the-literal) · [A byte was not always eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md#a-byte-was-not-always-eight-bits)

**Imported:** hexadecimal · hex digits · `0x` prefix · hex dump · hex editor · `xxd` · `od` · nibble · hex string · case convention · octal · binary · decimal · bit · byte · octet

**Missing — add:**

- ~~**`0b`, `0o`, `_` separators**~~ — both halves are written. The *parsing* side is on [Hex: a number, or a picture of bytes](01_Bits_and_Bytes/hex_number_or_bytes/README.md): `4_1` is 65 to Python, an error to Rust, and **4** to C's `strtol` with the rest left over. The *literal* side — what a compiler accepts in source — is [Writing the literal](01_Bits_and_Bytes/hex_is_a_shorthand/README.md#writing-the-literal), where the sting is the base that has no prefix: `0755` is **493 in C, 755 in Rust, and a syntax error in Python 3**.
- ~~**Endianness is visible in a hex editor and nowhere else**~~ — half-answered on the same page: a number has no byte order and a byte string does, so the question comes into existence at the conversion. The hex-editor half still belongs to §2.5.
- ~~**A "byte" was not always 8 bits**~~ — written as [A byte was not always eight bits](01_Bits_and_Bytes/a_byte_is_eight_bits/README.md#a-byte-was-not-always-eight-bits), and it took more than a sentence because the question is still open in C: `CHAR_BIT` is a number the language declines to fix at 8 (POSIX does), and `sizeof(char) == 1` is true by *definition*, so `sizeof` counts chars and not octets. Which is where the RFC vocabulary comes from.

### 1.13 Registries and living standards — **core, and entirely absent from the imported list**

- **IANA Character Sets registry** — the authority for what a charset *label* means; carries "preferred MIME name" and the reason `UTF8`, `utf-8` and `csUTF8` all work.
- **The WHATWG Encoding Standard** — a *living* standard that defines the exact encodings and label-matching a browser must implement, including that `iso-8859-1` means windows-1252 and that unknown labels map to the **replacement encoding** (which decodes to a single `U+FFFD` on purpose, as an anti-XSS measure). **This is the document the web actually obeys**, and the list does not mention it once.
- **Encoding label vs encoding** — matching is case-insensitive and whitespace-trimmed, and the label set is closed. "Just pass the charset through" is not a strategy.
- **`x-user-defined`** — the escape hatch for reading binary through a text API.
- **`encoding_rs` / `chardetng`** — Firefox's Rust implementations, and the practical answer for Rust to "decode this legacy file".
- **ICU** — the elephant. Collation, break iteration, normalization, transliteration, formatting, and 30 MB of data. The list mentions ICU six times without ever saying what it *is* or that most languages' text handling is ICU wearing a hat.
- **CLDR vs the UCD** — character data versus locale data, and the fact that sort order, plural rules and date formats come from CLDR, not Unicode proper. Already the missing half of [`tr` and `sort`](11_Tools/tr_and_sort/README.md).

### 1.14 Ciphers over an alphabet — **adjacent, with one core page**

*Covered:* [Rotation is not encryption](02_Characters/rotation_is_not_encryption/README.md)

**Imported:** ROT13 (the list files it under §1.1, which is the right place for it)

**The boundary, decided 2026-09-07.** A substitution table whose rule is *published* is a re-labelling of a character set — this library's subject, and the reason ROT13 has a page: its shift is half the size of a contiguous ASCII range, and nothing about it survives a move to EBCDIC. A table whose rule is a *secret* is cryptography, and the questions become keyspace, attack model and frequency analysis, none of which is answered by knowing anything about ASCII.

- **In scope, and written:** ROT13 · ROT5 / ROT18 / ROT47 · the Caesar, Atbash and affine alphabets shown once as the same shape · why every ROT number is half of a range in the table · ROT8000 as the case where a rotation stops being a sum, because the code space has holes in it.
- **Out of scope here, and now written next door (2026-09-07):** frequency analysis · index of coincidence · Vigenère and the polyalphabetic family · Playfair · one-time pads · Enigma · everything modern. This section said *"if an encryption library is ever written, this is where it starts"*, and it did: [cryptography-learning-library ↗](https://masiarek.github.io/cryptography-learning-library/), whose [02_Classical_Ciphers ↗](https://masiarek.github.io/cryptography-learning-library/02_Classical_Ciphers/index.html) picks up exactly where this line stops — its first page breaks a substitution cipher by counting, without trying a single one of the 26! keys.
- **Worth writing down anyway, because it belongs to §13:** *encoding for secrecy* is the same mistake in every decade. Base64 (§1.11), ROT13, hex and URL-escaping all get reached for when somebody wants a value to be unreadable, and every one of them is reversible by anybody who recognises it. The rule is not "which one is stronger" — none of them is on that scale at all.

---

---

## 2. Unicode and character mechanics

### 2.1 Code points — **core**

**Imported:** code point · `U+` notation · scalar value · reserved · unassigned · noncharacter · private use · surrogate · code space · first / last code point · total 1,114,112 · assigned count · property · General_Category · Script · Block · Bidi_Class

**Missing — add:**

- **`0x110000 − 2048 = 1,112,064`** — the number of encodable scalar values, and the one Unicode figure that is arithmetic rather than a table lookup, so it never goes stale. (Rust's `char` is exactly this set.)
- **Why the ceiling is `U+10FFFF`** — because that is what UTF-16 surrogates can address. The whole code space is the shape of a 1996 compromise.
- **`Age`** — the release a character was first assigned in. The concrete version of [The table has a version](02_Characters/the_table_has_a_version/README.md).
- **`Cn` does not mean "not in my edition"** — it means unassigned, with no hedge. A stale table states a false fact rather than reporting a gap. Measured; on [The table has a version](02_Characters/the_table_has_a_version/README.md).

### 2.2 Characters, glyphs and graphemes — **core**

*Covered:* stub: [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md)

**Imported:** abstract character · glyph · character-vs-glyph · encoded character · grapheme · grapheme cluster · extended grapheme cluster · user-perceived character · base character · combining character · combining diacritical mark · ZWJ · ZWNJ · cluster boundary · font · typeface · font fallback · tofu · `.notdef` · variation selector · emoji variation selector · emoji modifier · emoji sequence · regional indicator · keycap

**Missing — add:**

- **The five lengths** — bytes, code units, code points, grapheme clusters, terminal columns. One string, five different correct answers to "how long is it". This library's spine, and the frame the whole section needs.
- **UAX #29 and the GB rules** — grapheme cluster boundaries are a specified state machine, not a heuristic. Legacy vs extended vs *tailored* clusters.
- **`unicode-segmentation` (Rust) / `Intl.Segmenter` (JS) / `StringInfo` (.NET) / Swift's `Character`** — who ships this and who makes you install it. **Swift is the only mainstream language whose `count` is graphemes**, which is why its `"👨‍👩‍👧‍👦".count == 1`.
- **Stream-Safe Text Format** — UAX #15's 30-mark limit, and **Zalgo text** as what happens without it. Also a denial-of-service vector on naive renderers.
- **Canonical combining class and canonical ordering** — why two decomposed strings with the same marks in different orders are still equal.
- **`wcwidth()` and ambiguous width** — `U+00E9` is one column here and two in a CJK terminal, so a table's alignment depends on the reader's locale. Promised as the fifth answer on [A code point is not a character](02_Characters/a_code_point_is_not_a_character/README.md); `unicodedata.east_asian_width` makes it checkable.
- **Emoji width is unresolved** — terminals disagree with each other today, not historically.

### 2.3 Surrogate pairs — **core**

**Imported:** surrogate pair · high / low surrogate · decoding formula · lone surrogate · supplementary character · non-BMP · JavaScript handling · Java handling

**Missing — add:**

- **`0x10000 + ((H − 0xD800) << 10) + (L − 0xDC00)`** — worth doing once by hand for `😀` (`U+1F600` → `D83D DE00`), which is exactly the pencil exercise [UTF-16 and surrogates](03_Encodings/utf16_and_surrogates/README.md) owes.
- **`"😀".length === 2` in JavaScript** — the one-line demonstration that a language's `length` is a promise about code *units*.
- **`for...of` and spread iterate code points; `charAt` and `length` do not** — the split inside one language.
- **Surrogates are why `str` slicing can produce an unpaired half** — the JS/Java equivalent of Rust's byte-index panic.

### 2.4 Byte Order Mark — **core**

*Covered:* [Byte order and the BOM](03_Encodings/byte_order_and_bom/README.md) · [A BOM in a CSV](07_Real_Data/bom_in_a_csv/README.md)

**Imported:** BOM · UTF-8 BOM · UTF-16 LE/BE BOM · UTF-32 LE/BE BOM · BOM-less UTF-8 · detection · stripping · ZWNBSP · BOM in XML · `utf-8-sig`

**Missing — add:**

- **The codec *name* decides whether a mark is written** — `utf-16le` writes none, bare `utf-16` writes one. Already measured on the BOM page; belongs in the term list.
- **`U+FEFF` is legal mid-file and means ZWNBSP** — which is why "strip the BOM" and "strip all `U+FEFF`" are different operations, and why `U+2060 WORD JOINER` exists.
- **Excel requires the UTF-8 BOM to read a CSV as UTF-8** — the single most consequential BOM fact in business data, and the reason the "never write a BOM" advice cannot be followed everywhere.
- **A BOM inside a shebang line, a JSON document, or a PHP file** — three places where the mark is a hard error rather than noise.

### 2.5 Endianness — **core**

**Imported:** endianness · big-endian · little-endian · mixed-endian · bi-endian · network byte order · host byte order · `htons`/`htonl` · `ntohs`/`ntohl` · byte swapping · `bswap` · endian-neutral code · struct packing

**Missing — add:**

- **Plain `hexdump` with no `-C` reads two bytes at a time in the CPU's order** — so a file starting `63 61` prints as `6163`. The byte-order question hiding inside a tool that was only asked to show bytes. Measured; on [Inspecting a file](06_Terminal/inspecting_a_file/README.md).
- **Text has no endianness; *code units* do** — UTF-8 is immune because its unit is one byte. The cleanest way to explain why UTF-16 needs a BOM and UTF-8 does not.
- **`to_le_bytes` / `to_be_bytes` / `from_be_bytes`** — Rust makes you name it, which is the language enforcing the lesson.
- **Gulliver's Travels** — the terms are a joke about which end of a boiled egg to open. Worth one line, because it tells you neither order is better.

### 2.6 Collation — **core**

*Covered:* stub: [Sorting and collation](07_Real_Data/sorting_and_collation/README.md) · [`tr` and `sort`](11_Tools/tr_and_sort/README.md)

**Imported:** collation · sort order · locale-sensitive sorting · UCA · DUCET · collation element · collation key · primary/secondary/tertiary weight · variable weighting · CLDR · case-insensitive · accent-insensitive · natural sort · binary collation · `strcoll` · `strcmp` · ICU Collator · tailoring · MySQL `utf8_unicode_ci` / `utf8_general_ci`

**Missing — add:**

- **Sorting is not a property of the string** — it is a property of the (string, locale) pair. Same data, three locales, three different correct orders. The stub's own hook.
- **German phonebook vs dictionary order (DIN 5007-1 vs -2)** — one language, two official orders, and neither is wrong.
- **Czech `ch` is one letter, and it sorts after `h`** — a two-character grapheme in the collation sense. Kills any per-character sorting model.
- **Polish: `ą` sorts after `a`, not near it** — and `ł` is a letter, not an `l` with a mark.
- **The glibc 2.28 collation change broke PostgreSQL indexes worldwide** — an OS upgrade silently invalidating a `text` index, with no error until a query returns the wrong rows. **The strongest argument in existence for `COLLATE "C"` on identifier columns.** A real-data page in waiting.
- **Collation versioning** — ICU and PostgreSQL both track a collation version for this reason.
- **`LC_COLLATE=C` changes what `[a-z]` matches in a glob and in `tr`** — the shell half, already half-told on [`tr` and `sort`](11_Tools/tr_and_sort/README.md).
- **Sort keys are one-way** — you cannot recover the string, which is why they are stored beside it and not instead.

### 2.7 Normalization — **core**

*Covered:* [Normalization](04_Python/normalization/README.md)

**Imported:** normalization · NFC · NFD · NFKC · NFKD · canonical / compatibility equivalence · canonical / compatibility decomposition · canonical composition · composition exclusion · combining class · canonical ordering · starter · precomposed · decomposed · stream-safe · FCD · macOS NFD · `isNormalized()` · `normalize()`

**Missing — add:**

- **`NFC(NFD(x)) == x` is false for a whole class of characters** — singletons and composition exclusions. Normalization is a projection, not a round trip. Measured; on [Normalization](04_Python/normalization/README.md).
- **NFKC is lossy on purpose and dangerous by consequence** — `U+2100 ACCOUNT OF` expands to `a/c`, one code point becoming a path separator. On [The check that ran too early](12_Adversarial/canonicalize_then_check/README.md).
- **The Normalization Stability Policy** — the one Unicode table lookup an answer key may hold, and *why*.
- **Normalize *where*, not *whether*** — at the boundary, once, in a named direction. The operational rule the term list has no room for.
- **NFKC_Casefold** — the guaranteed-stable caseless form, and not the same as `casefold()`.
- **rsync, Samba, git and macOS** — the same filename in NFC and NFD is two files on Linux and one on macOS. `core.precomposeunicode` exists solely for this.

### 2.8 Transliteration — **adjacent**

**Imported:** transliteration · transcription · romanization · Pinyin · Hepburn · Kunrei-shiki · Wade-Giles · McCune-Reischauer · Revised Romanization · ISO 9 · ALA-LC · diacritic stripping · Unidecode · ICU transliteration · phonetic transliteration

**Missing — add:**

- **"NFD then drop the marks" does not give you ASCII** — `ł` has no decomposed form, because no COMBINING STROKE exists. The folk recipe leaves exactly one Polish letter standing. Measured; on [Normalization](04_Python/normalization/README.md).
- **`anyascii`** — the modern, data-driven alternative to `unidecode` (which has a licence most companies dislike).
- **Slugification is transliteration with a spec** — and every framework's is different, which is why the same article title yields three URLs.
- **Transliteration is not reversible** and romanization systems are political. Two sentences, and they prevent a class of bad decisions.

### 2.9 Encoding conversion — **core**

*Covered:* [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) · [Mojibake](03_Encodings/mojibake/README.md) · stub: [`iconv`](06_Terminal/iconv/README.md)

**Imported:** conversion · transcoding · `iconv` (tool and API) · Python `codecs` · Java `Charset` · .NET `Encoding` · ICU converter · lossy / lossless · `U+FFFD` · best-fit mapping · mojibake · double encoding · detection · `chardet` · `uchardet` · ICU detection

**Missing — add:**

- **There is no "convert" — there is decode then encode** — and naming the middle is the whole skill. Already the argument of [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md).
- **Detection is guessing, and it is *sometimes confidently wrong*** — the "Bush hid the facts" bug: Notepad's detector reads a specific 4-word ASCII file as UTF-16. Still the best one-line demonstration in computing.
- **`ftfy`** — the library for repairing already-mangled text, and the recipe behind it (`text.encode('cp1252').decode('utf-8')`), which is [the mojibake round trip](07_Real_Data/mojibake_round_trip/README.md) stub's whole subject.
- **Double encoding is *sometimes* repairable and sometimes not** — the deciding question is whether the wrong table was total (Latin-1: always reversible) or partial (cp1252: five bytes are unassigned, so information is gone). This is the single most useful thing to know when someone hands you a corrupted export.
- **`iconv //TRANSLIT` and `//IGNORE`** — and that both mean "lose data quietly"; GNU and BSD disagree on how. Measured.

### 2.10 Properties and the UCD files — **core, absent from the imported list**

- **The data files themselves** — `UnicodeData.txt`, `PropList.txt`, `DerivedCoreProperties.txt`, `Scripts.txt`, `Blocks.txt`, `CaseFolding.txt`, `SpecialCasing.txt`, `NormalizationTest.txt`, `confusables.txt`, `emoji-data.txt`, `LineBreak.txt`, `GraphemeBreakProperty.txt`. The library reads these through `unicodedata` and `uni`; naming them makes the database a place rather than a magic.
- **`NormalizationTest.txt`** — the conformance suite. If you implement normalization, this file is the grader.
- **The properties worth knowing by name:** `Alphabetic` · `White_Space` · `Default_Ignorable_Code_Point` · `Deprecated` · `Noncharacter_Code_Point` · `Pattern_Syntax` · `ID_Start` / `ID_Continue` / `XID_Start` / `XID_Continue` · `Case_Ignorable` · `Changes_When_Casefolded` · `Grapheme_Base` / `Grapheme_Extend` · `Word_Break` / `Sentence_Break` / `Line_Break` · `Joining_Type` · `Indic_Syllabic_Category` · `Decomposition_Type` · `Numeric_Type` / `Numeric_Value` · `Bidi_Mirrored` · `Emoji` / `Emoji_Presentation` / `Extended_Pictographic`.
- **`Numeric_Value` is not `int()`** — Unicode knows that `U+2158` is 3/5 and that a Han numeral is 10,000. `unicodedata.numeric` will tell you; `int()` will not.
- **The annexes, as an index:** UAX #9 bidi · #11 east-asian width · #14 line breaking · #15 normalization · #24 script · #29 segmentation · #31 identifiers · #34 named sequences · #38 Unihan · #42 UCD in XML · #44 the character database · #50 vertical text; UTS #10 collation · #18 regular expressions · #35 LDML/CLDR · #37 IVD · #39 security · #46 IDNA compatibility · #51 emoji.

### 2.11 Case mapping — **core, absent from the imported list**

- **Case is not a per-character operation** — `ß` uppercases to `SS`, so a string gets *longer*. Rust's `to_uppercase` returns an iterator for exactly this reason; the cast carries `ß` for it.
- **Simple vs full case mapping** — and `SpecialCasing.txt` as the file that holds the difference.
- **The Turkish dotted and dotless i** — `"I".lower()` is `"i"` in English and `U+0131` in `tr_TR`. **The bug that has broken .NET, Java and Android code repeatedly**, and the reason `StringComparison.Ordinal` and `CultureInfo.InvariantCulture` exist.
- **Greek final sigma** — a case mapping that depends on position in the word. Context-sensitive, so no table alone can do it.
- **`casefold()` is not `lower()`** — and `'İ'.casefold()` is two code points, so casefolding can *create* the thing normalization exists to reconcile. Fold, then normalize. Measured; on [Normalization](04_Python/normalization/README.md).
- **Case-insensitive filesystems** — APFS, NTFS and HFS+ each use a *frozen* case table, so a filename that collides on one macOS version may not on another.
- **Cherokee gained uppercase in Unicode 8** — a script that was caseless became cased, which is a stability guarantee people assumed existed and does not.

### 2.12 Bidirectional text — **core**

*Covered:* stub: [Logical and visual order](02_Characters/logical_and_visual_order/README.md) · [What you see is not what runs](12_Adversarial/trojan_source/README.md)

- **Logical order vs visual order** — a string is stored in the order it is *typed*, displayed in the order it is *read*. **A terminal screenshot is not evidence about a string**, which is the stub's hook.
- **Embedding levels and the resolution algorithm (UAX #9)** — paragraph direction, the implicit level rules, and why a phone number in an Arabic sentence renders left-to-right inside it.
- **Isolates vs embeddings vs overrides** — `U+2066`–`U+2069` (isolates, the modern form) versus `U+202A`–`U+202E` (embeddings and overrides, the legacy form). All nine are written as escapes here, never as characters, per [12_Adversarial](12_Adversarial/README.md)'s house rule.
- **Mirroring (`Bidi_Mirrored`) and BD16 bracket pairing** — a `(` is drawn as `)` in an RTL run. The glyph is not the character.
- **RTL UI mirroring** — layout, icons, progress direction; CSS logical properties (`margin-inline-start`) as the modern answer.
- **The `.exe` filename spoof** — an override in a filename makes `annexRLOfdp.exe` display as an innocent PDF. Decades old, still shipping in malware.

### 2.13 Emoji — **core (small), absent from the imported list as a topic**

- **ZWJ sequences** — a family emoji is up to seven code points and one grapheme. The best possible demonstration of §2.2.
- **Skin-tone modifiers (`U+1F3FB`–`U+1F3FF`) and the base+modifier model.**
- **Flags are two regional indicators; subdivision flags are tag sequences** — so `U+1F3F4` plus five tag characters is a Scottish flag, and the tag block's other use is invisible text.
- **RGI (Recommended for General Interchange)** — the reason some valid sequences render and some do not.
- **Emoji vs text presentation** — `U+FE0F` and `U+FE0E`, and why the same code point is a black glyph in a terminal and a colour picture in a browser.
- **`emoji-test.txt` and CLDR keyword search** — the character's *name* is UCD data; the words you search it by are CLDR data. Two databases, as on [`uni`](11_Tools/uni/README.md).
- **Cross-platform rendering divergence** — the "pistol/water pistol" change, and the fact that emoji meaning is not preserved across vendors. A design constraint, not trivia.

---

## 3. Streams and I/O — **adjacent**

The imported list's largest section, and the one furthest from this library's subject: file descriptors, `epoll` and async I/O are operating-system material that happens to move bytes. **Kept in full for completeness, and marked adjacent so the boundary is deliberate.** Two parts of it are genuinely core and are called out below.

**Imported (3.1–3.9), preserved:** stdin/stdout/stderr · redirection `>` `>>` `<` `2>` `2>&1` · pipe · FIFO · `tee` · process substitution · here-doc · here-string · `isatty` · `/dev/null` · file descriptor · open file table / description · `dup` / `dup2` · `fcntl` · `open` flags · `read` / `write` / `pread` / `pwrite` / `lseek` · `RLIMIT_NOFILE` · `/proc/self/fd` · `FD_CLOEXEC` · byte stream vs character stream · Java `InputStream` / `Reader` / `InputStreamReader` / `BufferedReader` · .NET `TextReader` / `StreamReader` · Python `io.StringIO` / `BytesIO` / `TextIOWrapper` / `sys.stdout.buffer` · text vs binary mode · universal newlines · buffering (unbuffered / line / full) · `fflush` · `setvbuf` · page cache · ring buffer · double buffering · read-ahead · `fsync` / `fdatasync` · `O_SYNC` / `O_DIRECT` · EOF · `feof` · Ctrl+D / Ctrl+Z · premature EOF · blocking vs non-blocking · `O_NONBLOCK` · `EAGAIN` · reactor / proactor · event loop · sync vs async I/O · POSIX AIO · `io_uring` · Windows overlapped I/O · IOCP · coroutines · async/await · future/promise · `select` / `poll` / `epoll` / `kqueue` · edge vs level triggered · libevent · libuv · libev · asyncio · serialization / deserialization · marshaling · JSON · XML (SAX/DOM/StAX) · YAML · TOML · CSV · protobuf · MessagePack · CBOR · Avro · Thrift · Cap'n Proto · FlatBuffers · BSON · ASN.1 / BER / DER · pickle · schema evolution · backward / forward compatibility

**Missing — add (the core half):**

- **A pipe is not a terminal, and that changes the *encoding* behaviour** — `isatty()` decides buffering, colour, *and* in Python which encoding `sys.stdout` gets. The same program prints different bytes into a pipe than onto a screen. **This is core**, and it is why `python x.py | cat` can raise `UnicodeEncodeError` when `python x.py` does not.
- **`PYTHONIOENCODING`, `PYTHONUTF8`, PEP 540 UTF-8 mode, PEP 538 locale coercion, PEP 686** — the five levers that decide what Python's streams do. This library pins `PYTHONUTF8=1` in every run for exactly this reason.
- **`stdbuf`, `unbuffer`, `script`, and a pty** — how to make a program behave as if it were on a terminal, which is the only way to test the above.
- **SIGPIPE / EPIPE** — `head` closing a pipe kills the writer, and the "BrokenPipeError" every Python CLI eventually prints. One line, saves an afternoon.
- **Short reads and short writes** — `write()` returning less than you asked is not an error, and the loop everyone forgets. In text terms: **a multi-byte character can be split across two reads**, which is why incremental decoders exist (`codecs.IncrementalDecoder`, `encoding_rs`'s streaming API). **This is core** and it is the thing a naive `decode()` per chunk gets wrong.
- **Framing** — length-prefixed vs delimiter-terminated vs self-describing. Text protocols pick delimiters, which is why a newline inside a field is a security bug.
- **`EINTR`** — a signal can interrupt a read; `SA_RESTART` and Python's PEP 475.
- **`ARG_MAX`** — why `xargs` exists at all, already on [`xargs`](11_Tools/xargs/README.md).
- **Windows text mode** — `O_TEXT` translates CRLF *and* treats `0x1A` as end-of-file. A binary file opened in text mode is silently truncated at the first Ctrl+Z byte.

---

## 4. Text processing and formatting

### 4.1 Line endings — **core**

*Covered:* [CRLF vs LF](07_Real_Data/crlf_vs_lf/README.md) — written 2026-09-07, and it takes `dos2unix` / `tr` / `sed`, `core.autocrlf`, `.gitattributes`, universal newlines, newline translation and the mandatory-CRLF protocols with it · [The trailing newline](06_Terminal/trailing_newline/README.md)

**Imported:** line terminator · CR · LF · CRLF · NEL · LS `U+2028` · PS `U+2029` · `dos2unix` / `unix2dos` · `core.autocrlf` · `core.eol` · `.gitattributes` · universal newlines · newline translation · SMTP CRLF

**Missing — add:**

- **Python's `splitlines()` splits on eleven sequences** — `\n`, `\r`, `\r\n`, `\v`, `\f`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `U+2028` and `U+2029` — so a string carrying eight of them comes back as **nine** pieces while `split('\n')` returns **one** (measured 2026-09-06). **`split('\n')` and `splitlines()` are not the same function**, and the difference is a parser differential inside one language.
- **`U+2028` in a JavaScript string literal was a syntax error until ES2019** — the JSON-is-not-a-JS-subset bug.
- **A file with no trailing newline is not a text file by POSIX** — `wc -l` says 0 for a two-byte file. Already measured on [The trailing newline](06_Terminal/trailing_newline/README.md).
- **`git diff`'s "\ No newline at end of file"** — the one place the rule becomes visible to everyone.
- ~~**CRLF in HTTP, SMTP, FTP and NNTP is mandatory**~~ — written 2026-09-07 on [CRLF vs LF](07_Real_Data/crlf_vs_lf/README.md), which puts it where it explains something: those protocols were drafted while DOS was current, which is why the ending nobody on a Unix machine wants is the one the wire requires. The injection half — CRLF inside a header field is [response splitting](12_Adversarial/in_band_signals/README.md) — was already there.
- ~~**Mixed line endings in one file**~~ — what every editor does silently, measured 2026-09-07 on [CRLF vs LF](07_Real_Data/crlf_vs_lf/README.md). "No tool agrees" turned out to be one tool short of true: `file` says `with CRLF, LF line terminators` on both platforms and is the only one that mentions the disagreement at all — `grep`, `cut` and `wc` each answer for their own line and never say the file is inconsistent.

### 4.2 Tokenizing, lexing and parsing — **adjacent**

**Imported:** tokenization · token · lexer · lexical analysis · token type/value/stream · lexical grammar · finite automaton · DFA · NFA · flex · re2c · maximal munch · BPE · WordPiece · SentencePiece · OOV · parser · parse tree · AST · CFG · BNF · EBNF · ABNF · PEG · LL · LR · LALR(1) · recursive descent · packrat · Pratt · Earley · GLR · yacc / bison · ANTLR · parser combinator · `nom` · shift-reduce and reduce-reduce conflicts

**Missing — add:**

- **A lexer's first decision is what a *character* is** — bytes, code points or graphemes, and languages disagree. This is the only part of the section that is this library's business, and it is the part the list omits.
- **Unicode in identifiers is a spec, UAX #31** — and NFKC vs NFC on identifiers is a real divergence between Python and Rust. Already written: [Unicode in identifiers](02_Characters/unicode_in_identifiers/README.md).
- **Significant whitespace, the off-side rule, INDENT/DEDENT tokens** — and tabs-versus-spaces as a *lexing* problem, which is what Python 3 made an error.
- **tree-sitter and incremental parsing** — what editors actually run.
- **The lexer hack** — C cannot be lexed without a symbol table.
- **Byte-level BPE and the token-boundary problem** — see §19.

### 4.3 Regular expressions — **adjacent, with a core corner**

**Imported:** regex · pattern · match · capture group · named group · non-capturing group · backreference · lookahead / lookbehind (positive and negative) · alternation · greedy / lazy / possessive quantifiers · character class · negated class · dot · anchors · `\b` · `\d` `\w` `\s` · Unicode property escapes · flags · POSIX BRE / ERE · PCRE · RE2 · Oniguruma · catastrophic backtracking · ReDoS · atomic group · `grep` · `sed` · `awk`

*Covered:* [`grep`](11_Tools/grep/README.md) · [`ripgrep`](11_Tools/ripgrep/README.md) · [`sed`](11_Tools/sed/README.md) · [`awk`](11_Tools/awk/README.md) · [PCRE2](11_Tools/pcre2/README.md)

**Missing — add:**

- **UTS #18, the three levels of Unicode regex support** — and the fact that almost no engine reaches level 2. The specification that says what "Unicode regex" is even supposed to mean.
- **`\X` matches a grapheme cluster** — the one escape that does what a user expects, and most engines lack it.
- **`.` matches a code point, not a character** — so `.` against a flag emoji matches half of it.
- **Case-insensitive matching is a Unicode operation** — `(?i)k` matches `U+212A KELVIN SIGN` in a full-Unicode engine and not in an ASCII one. The most surprising true fact about `(?i)`.
- **`\w` and `\b` depend on the Unicode flag** — same pattern, same input, different answer.
- **DFA vs backtracking as a *safety* property** — RE2 and Rust's `regex` guarantee linear time by giving up backreferences. That is a trade, and knowing which side your engine is on is the whole ReDoS story.
- **Hyperscan, PCRE2 JIT, and `regex-automata`** — where speed comes from.
- **Globs are not regexes** — `fnmatch`, `extglob`, and the fact that a shell glob's `[a-z]` is locale-dependent.

### 4.4 String operations — **core**

**Imported:** interpolation · template literal · f-string · `String.format` · printf-style · string builder · `StringBuilder` · `strings.Builder` · immutability · interning · string pool · rope · lexicographic order · padding · zero-padding · slicing · `split` · `join` · `strip` · `lower`/`upper` · `casefold` · hashing · reversal · printf width and precision

**Missing — add:**

- **`printf("%-20s")` pads by *bytes* in C and by *code points* in Python** — and by neither in a terminal, which measures columns. **A padded table is three different widths depending on who is counting**, which is the pun that makes the five lengths matter and is already used by `utf8_everywhere`'s `pad()`.
- **Reversing a string is almost always wrong** — reverse the bytes and you destroy UTF-8; reverse the code points and you move a combining mark onto the wrong letter; reverse the graphemes and you are finally correct and still wrong for Arabic.
- **Truncating to N characters is the same trap** — and truncating to N *bytes* mid-sequence is how a database column produces invalid UTF-8.
- **`str.translate` and `bytes.maketrans`** — the fast per-character table, and its limits.
- **Small-string optimisation** — why `String` in C++ and Rust behave differently for short strings, and why `&str` has no allocation at all.
- **String interning and identity** — `is` vs `==`, and the reason CPython's behaviour changes with literal length.
- **Concatenation in a loop is quadratic** — in every immutable-string language, and it is the one performance fact worth teaching early.

### 4.5 Encoding and decoding in practice — **core**

*Covered:* [Encode and decode are verbs](03_Encodings/encode_and_decode_are_verbs/README.md) · stub: [Encode, decode and errors](04_Python/encode_decode_and_errors/README.md)

**Imported:** `encode()` · `decode()` · codec · error handlers `strict` / `ignore` / `replace` / `xmlcharrefreplace` / `backslashreplace` · `UnicodeEncodeError` · `UnicodeDecodeError` · `utf-8-sig` · incremental codec · stream codec · PEP 263 · XML declaration · HTML meta charset · HTTP charset

**Missing — add:**

- **`surrogateescape`** — the sixth error handler, the one that makes byte-preserving round trips possible, and the mechanism behind `os.fsdecode`. **The most important missing item in this whole section.**
- **`surrogatepass`** — how to write a lone surrogate out as UTF-8 on purpose (which is WTF-8).
- **`codecs.register_error`** — you can write your own.
- **`UnicodeDecodeError.start` / `.end` / `.object`** — the exception tells you *which byte*, which is Python's `valid_up_to()`. Already paired on [`String` is bytes that promise UTF-8](05_Rust/string_is_bytes_that_promise_utf8/README.md).
- **Every error handler is a policy decision with a blast radius** — `ignore` is silent data loss, `replace` is visible data loss, `strict` is an outage. Choosing is the lesson; the stub's own hook.
- **The declaration is not the encoding** — a meta charset, an XML declaration and a PEP 263 comment are all *claims* that can be false, and the file is bytes either way.

### 4.6 String search — **adjacent, absent from the imported list**

- Naive · Knuth-Morris-Pratt · Boyer-Moore / Boyer-Moore-Horspool · Rabin-Karp · Aho-Corasick (many needles at once) · Two-Way (glibc `memmem`) · Bitap / shift-or · suffix array · suffix automaton · FM-index.
- **`memchr` and SIMD** — why `str::find` is fast in Rust, and why `grep` beats a hand-written loop.
- **Searching is encoding-dependent** — a substring search in UTF-8 is byte-safe (a valid sequence cannot match inside another), which is not true of Shift-JIS. **The self-synchronisation property, cashed in.**
- **Case-insensitive and accent-insensitive search need collation, not `lower()`** — ICU search collators; the "why can't I find `café` by typing `cafe`" question.
- **Trigram indexes (`pg_trgm`) and fuzzy matching in a database.**

### 4.7 Similarity, phonetics and diffs — **adjacent, absent from the imported list**

- Levenshtein · Damerau-Levenshtein · Hamming · Jaro-Winkler · longest common subsequence · cosine / Jaccard on n-grams.
- Soundex · Metaphone / Double Metaphone · NYSIIS · Caverphone — and that **every one of them is English-only**, which is the point worth making.
- Myers diff · patience diff · histogram diff · word-level and character-level diff · `git diff --word-diff`.
- **Diffing text that differs only in normalization or line endings** — the invisible diff, and `git diff --ignore-cr-at-eol`.

### 4.8 Line breaking, wrapping and justification — **adjacent, absent from the imported list**

- **UAX #14** — line breaking is a specified algorithm with break opportunities, not "split on spaces". Thai and Japanese have no spaces at all.
- Knuth-Plass paragraph breaking · greedy wrapping · `textwrap` and why it is wrong for CJK.
- Hyphenation: Liang's algorithm, TeX patterns, `hyphen` dictionaries, the soft hyphen `U+00AD`.
- `overflow-wrap` / `word-break` / `line-break` in CSS — the same algorithm exposed as four properties.

### 4.9 Case styles, slugs and identifiers — **adjacent, absent from the imported list**

- camelCase · PascalCase · snake_case · kebab-case · SCREAMING_SNAKE_CASE · Train-Case · dot.case.
- **Acronym handling is where every converter differs** — `HTTPServer` to snake case has three defensible answers.
- Rust's `heck`, Python's `inflection`, and the fact that "convert case" is not a total function on Unicode.
- Slugs, URL safety, and the collision that happens when two titles slugify to one string.

---

## 5. Control and special characters

### 5.1–5.2 C0, C1 and the specials — **core**

*Covered:* [Control characters](02_Characters/control_characters/README.md) · [The NUL byte](02_Characters/the_nul_byte/README.md)

**Imported:** the full C0 table NUL…US with names and uses · DEL · C1 controls · non-printable character · control pictures · XON/XOFF · soft hyphen · word joiner · function application · invisible times / separator / plus · interlinear annotation · object replacement character · the Specials block

**Missing — add:**

- **C1 controls have a 7-bit escape form** — `ESC` plus a byte, which is why `0x9B` (CSI) and `ESC [` mean the same thing, and why a UTF-8 continuation byte can look like a control introducer to an 8-bit terminal.
- **The four separators FS/GS/RS/US are a complete record format nobody uses** — and `RS` (`0x1E`) is the delimiter in RFC 7464 JSON text sequences, so it did come back.
- **`U+0085 NEL`** — the Unicode line terminator that exists because EBCDIC had one.
- **Overstrike** — `a`, backspace, `_` is how underlining worked, and why `man` output needs `col -b`.
- **BEL inside a terminal title sequence** — the string terminator that is also an alarm.

### 5.3 Escape sequences — **core**

*Covered:* [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md)

**Imported:** escape sequence · backslash escapes `\n \r \t \v \b \f \a \0` · `\xHH` · `\uHHHH` · `\UHHHHHHHH` · `\N{name}` · octal escape · raw string · HTML / JSON / URI / shell escaping · double escaping · escape hell · SQL `LIKE ESCAPE`

**Missing — add:**

- **`\xHH` means a *byte* in Python `bytes` and a *code point* in Python `str`** — the same spelling, two meanings, one language.
- **Rust has no `\xHH` above `\x7F` in a string literal** — the compiler refuses, because a byte is not a character. The type system enforcing chapter 3.
- **The layering rule** — a URL inside JSON inside HTML inside a shell command needs four escapes applied in one order and undone in the reverse. Already the argument of [Escaping into ASCII](03_Encodings/escaping_into_ascii/README.md).
- **Context-aware auto-escaping** — Go's `html/template` and Angular's sanitizer decide the escape from the *position* in the document. The only design that survives layering.
- **`\N{...}` names are UCD names**, so `\N{LINE FEED}` fails while `\N{EURO SIGN}` works — control characters have aliases, not names.

### 5.4 ANSI escape codes — **core (terminal chapter)**

*Covered:* [Terminal hyperlinks](06_Terminal/terminal_hyperlinks/README.md)

**Imported:** ANSI escape code · CSI · SGR · reset · bold / faint / italic / underline / blink / reverse / conceal / strike · 30–37 and 40–47 · 90–97 / 100–107 · 256-colour · truecolor · cursor movement and position · save/restore · erase display / line · OSC · hyperlink escape · VT100 · terminfo / termcap · ncurses · `tput` · colorama · rich · chalk · Windows VT sequences · strip-ANSI

**Missing — add:**

- **Escape-sequence injection** — untrusted text printed to a terminal can move the cursor, rewrite earlier lines, set the window title, and on some terminals **request a response that is then typed as input**. A log viewer is an interpreter. Belongs in [12_Adversarial](12_Adversarial/README.md), beside [in-band signals](12_Adversarial/in_band_signals/README.md).
- **`NO_COLOR`, `CLICOLOR`, `CLICOLOR_FORCE`, `FORCE_COLOR`, `TERM=dumb`** — the actual protocol for "should I emit colour", which most tools get wrong.
- **Alternate screen buffer (1049), bracketed paste (2004), mouse tracking, synchronized output (2026), cursor shape (DECSCUSR)** — the private modes that make a modern TUI.
- **OSC 8 hyperlinks, OSC 52 clipboard, OSC 7 working directory, OSC 133 semantic prompts** — the modern OSC set; OSC 52 in particular lets a remote process write your local clipboard.
- **Sixel, iTerm2 inline images, the Kitty graphics protocol** — pictures in a terminal, three incompatible ways.
- **Stripping ANSI with a regex is not sufficient** — OSC sequences end with `BEL` or `ST`, not `m`, so the common one-liner leaves half of them in.

### 5.5 Whitespace — **core**

*Covered:* [Locale and `LC_CTYPE`](06_Terminal/locale_and_lc_ctype/README.md) touches it; `White_Space` is measured on [Unicode code points](02_Characters/unicode_code_points/README.md)

**Imported:** whitespace character · SPACE · NBSP · en / em / thin / hair space · ZWSP · narrow NBSP · ideographic space · tab stop · tab width · soft and hard tab · `expandtabs` · VT · FF · `isspace` · Unicode Zs / Zl / Zp · normalization · HTML collapsing · trimming

**Missing — add:**

- **25 code points have `White_Space`, in 10 runs** — measured on both CI runners, and stable since Unicode 4.1. One of the few table facts safe to record.
- **NBSP is the most common invisible bug in business data** — it survives copy-paste from Word and Excel, it is not stripped by `strip()` in every language, and it makes a numeric field fail to parse. **A real-data page in waiting.**
- **`str.strip()` strips Unicode whitespace; `bytes.strip()` strips ASCII** — the same method name, two definitions.
- **`Zs` is not `White_Space`** — `U+200B ZERO WIDTH SPACE` is neither, despite the name. The name of a character is not a specification.
- **`U+180E` moved category twice** — `Cf`, then `Zs`, then `Cf` again. The cleanest single example of a property that is not stable.

### 5.6 NUL and string termination — **core**

*Covered:* [The NUL byte](02_Characters/the_nul_byte/README.md)

**Imported:** null terminator · NUL character · C string · `strlen` · off-by-one · buffer overflow · Pascal string · counted string · fat pointer · Rust `&str` · `std::string_view` · null-byte injection · null vs empty string · embedded null

**Missing — add:**

- **Three languages, three answers to "what ends a string"** — C says a byte, Rust and Go say a length, Python says an object header. Everything else follows from that one choice.
- **`CString` refuses an interior NUL at construction time** — Rust turning a class of vulnerability into a compile-time-shaped error.
- **Filenames cannot contain NUL on any POSIX system**, which is why `find -print0` and `xargs -0` are safe. Already on [`xargs`](11_Tools/xargs/README.md).
- **NUL in the middle of a `bytes` is fine everywhere and fatal at every C boundary** — the boundary is the bug, not the byte.

---

## 6. Fonts and text rendering — **adjacent**

**Imported:** font rendering · hinting · anti-aliasing · subpixel rendering · ClearType · FreeType · HarfBuzz · Pango · complex text layout · ligature · kerning · tracking · leading · monospace vs proportional · colour emoji · fallback chain · Noto · OpenType · TrueType · `cmap` · WOFF / WOFF2 · font coverage · tofu

**Missing — add:**

- **The pipeline, in order: bidi → itemisation → shaping → line breaking → justification → rasterisation.** The list names pieces without the order, and the order is what makes rendering comprehensible.
- **Shaping is not one-to-one** — one code point can become several glyphs and several code points one glyph. **A glyph index is not a character index**, which is why text selection and cursor movement are hard.
- **Arabic joining forms** — one letter, four glyphs, chosen by neighbours. The clearest possible proof that a font is a program.
- **CoreText, DirectWrite, Uniscribe, HarfBuzz** — who does the shaping on each platform.
- **Colour emoji have four incompatible formats** — Apple `sbix`, Google `CBDT`, Microsoft `COLR`, and `SVG`-in-OpenType. Which is why an emoji font is not portable.
- **Variable fonts, COLRv1, font subsetting, `unicode-range`** — the modern web delivery model.
- **Nerd Fonts and Powerline glyphs live in the Private Use Area** — the single most common real-world PUA use, and the reason a terminal theme breaks on another machine.
- **Font fingerprinting** — which fonts you have is an identifier.
- **The "last resort" font** — a font whose whole job is to draw a meaningful box per script instead of tofu.

---

## 7. Internationalization and localization — **adjacent, and much bigger than the imported list suggests**

**Imported:** i18n · l10n · g11n · locale · BCP 47 · language / region / script subtags · CLDR · ICU · gettext · `.po` / `.mo` · translation key · plural forms · date/time and number formatting · calendars · RTL support · bidi overrides · Trojan Source · homoglyph · confusables · homoglyph phishing · IDN · pseudo-locale · translation memory · machine translation · time zones · `setlocale` · `LC_*` variables

**Missing — add:**

- **ICU MessageFormat and MessageFormat 2.0** — the actual format for a translatable sentence with a number in it.
- **The six plural categories** — `zero one two few many other`; English uses two, Arabic uses six, and **a translated string is not a string, it is a function of a number**.
- **Ordinal plurals and RBNF** — "1st/2nd/3rd" is its own rule set; spelling numbers out is another.
- **Grouping is not always three digits** — the Indian system groups 2-2-3, so `10,00,000`. Also: which *character* the separator is (NBSP in French, apostrophe in Swiss German).
- **Arabic-Indic digits** — `U+0660`–`U+0669`; a number can be written in digits your parser does not recognise, and `int()` in Python accepts them while `int()` in most languages does not.
- **The tz database, and that it is not a standard but a volunteer project** — plus DST ambiguity (one local time, two instants), the Japanese era transition (Reiwa, 2019), and Windows-to-IANA zone mapping via CLDR.
- **ISO 8601 vs RFC 3339 vs "ISO format"** — they are not the same, and `datetime.fromisoformat` historically parsed neither exactly.
- **Locale negotiation** — `Accept-Language`, RFC 4647 lookup vs filtering, fallback chains, likely subtags, the `und` and `root` locales, and CLDR's inheritance.
- **POSIX locale names are not BCP 47** — `pl_PL.UTF-8` versus `pl-PL`, and nothing converts between them reliably.
- **Resource formats:** `.strings` · `.resx` · `.arb` · XLIFF · Java `.properties` (**ISO-8859-1 with `\uXXXX` escapes until Java 9**) · Android `strings.xml` · gettext plural header.
- **Positional placeholders** — `%1$s`, because translators must reorder arguments; `%s %s` is untranslatable.
- **Text expansion** — German runs ~30% longer than English; pseudolocalization exists to find the layouts that break.
- **Name, address and phone-number i18n** — given/family order, mononyms, `libphonenumber`, E.164. The "falsehoods programmers believe about names" genre.
- **Sorting a list of names is §2.6, not §7** — but users blame the localization.

---

## 8. Text in protocols and file formats — **core, and the chapter this library calls Real Data**

**Imported:** HTTP `Content-Type` / `Accept-Charset` / `Transfer-Encoding` / `Content-Encoding` · MIME · charset parameter · RFC 2047 encoded word · HTML entities · XML character reference · JSON string encoding · percent-encoding · reserved URI characters · `application/x-www-form-urlencoded` · `multipart/form-data` · CSV quoting · TSV · SQL string escaping · SQL injection via encoding · content sniffing · `nosniff` · charset sniffing · robots.txt · RFC 4180 · protobuf string · MessagePack `str` vs `bin` · CBOR text vs byte string

**Missing — add:**

- **HTTP headers are ISO-8859-1 by RFC 7230, and RFC 8187 is the fix** — `filename*=UTF-8''...` in `Content-Disposition` is why a download with a Polish filename works in some browsers and not others. **A daily real-data problem.**
- **WHATWG URL vs RFC 3986** — two specifications, different parses of the same string, which is a [parser differential](12_Adversarial/parser_differentials/README.md) with a CVE list attached. Plus the **percent-encode sets** (C0, fragment, query, path, userinfo, component) — there is no single "URL encoding".
- **IRIs (RFC 3987), IDNA2003 vs IDNA2008, UTS #46** — three answers to "what does this domain name mean", and browsers implement UTS #46.
- **SMTPUTF8 / EAI (RFC 6531/6532)** — internationalized email addresses. The mailbox part, not just the domain.
- **Email header folding and the 998-character line limit** — why encoded-words are chopped into pieces, and why a long Polish subject line arrives in fragments.
- **JSON:** duplicate keys (undefined behaviour, and a differential), lone surrogates (accepted by `json.loads`, measured), `\/` escaping, BOM forbidden by RFC 8259, JSON Lines / NDJSON, JCS canonical JSON (RFC 8785), number precision, JSON5, and the fact that **JSON is defined over Unicode text, so "which encoding" is a question the format answers for you and the transport does not**.
- **XML:** the forbidden control characters (XML 1.0 cannot carry `0x01` at all, even escaped), XML 1.1's different rules, the encoding-detection algorithm in Appendix F, entity expansion (billion laughs), XXE, `xml:lang`, and C14N.
- **YAML: the Norway problem** — YAML 1.1 parses `no`, `off`, `yes` as booleans, so a country code becomes `false`. **`12:30` parses as 750 in base 60.** Directly relevant: the [voting library ↗](https://github.com/masiarek/star-voting-library) has a machine-checked rule for exactly this. Also: YAML 1.1 vs 1.2, anchors and merge keys, multi-line scalar styles, and tag-based deserialization as an RCE vector.
- **CSV, properly:** RFC 4180 is not what Excel does; Excel uses **the locale's list separator** (semicolon across most of Europe), needs a UTF-8 BOM to read UTF-8, and interprets a leading `=`, `+`, `-` or `@` as a formula — **CSV injection**. Plus embedded newlines inside quoted fields, dialect sniffing, and the IANA TSV spec that forbids quoting entirely.
- **Fixed-width and COBOL copybooks** — where a field is N *bytes* and a two-byte character silently steals a column. The [fixed-width byte fields](07_Real_Data/fixed_width_byte_fields/README.md) stub.
- **EDI (X12, EDIFACT)** — character-set levels UNOA/UNOB/UNOC, and segment/element/release characters, which is in-band signalling as a design.
- **SWIFT MT's restricted character set; ISO 20022 XML** — finance's answer to "no, you may not use that character".
- **HL7 v2's encoding characters `|^~\&`** — declared in the message itself. In-band signalling, made configurable, which is worse.
- **Archives:** ZIP filename encoding (CP437 by default, UTF-8 only with the EFS bit set) — the garbled-Japanese-zip classic; tar's pax extended headers; 7z and RAR.
- **Git:** `core.quotepath` (why `git status` prints octal escapes), `core.precomposeunicode`, `.gitattributes working-tree-encoding` (for UTF-16 files), the commit `encoding` header, and `i18n.commitEncoding`.
- **PDF text extraction** — `WinAnsiEncoding`, CID fonts, `ToUnicode` CMaps, and the reason copied text comes out as gibberish. The format where the *bytes are glyph indices*, not characters.
- **QR codes** — the ECI mode that names a charset, the fact that most generators omit it, and the resulting "byte mode is Shift-JIS or Latin-1, guess which".
- **WebSocket** — a text frame **must** be valid UTF-8; an invalid one closes the connection with code 1007. A protocol that validates.
- **MQTT** — UTF-8 strings with explicit prohibitions (no NUL, no unpaired surrogates).
- **vCard / iCalendar** — line folding and the `\,` `\;` escapes; the format where a comma in a name breaks the file.
- **Content sniffing and `X-Content-Type-Options: nosniff`** — already in the list, but the *charset* sniffing half (meta-tag pre-scan, the 1024-byte window) is what makes it a text problem.

---

## 9. Programming-language specifics

*Covered:* [04_Python](04_Python/README.md) · [05_Rust](05_Rust/README.md) · [Python text in practice](10_Best_Practices/python_text_in_practice/README.md) · [Rust strings in practice](10_Best_Practices/rust_strings_in_practice/README.md)

**Imported (9.1–9.7), preserved:** Python `str` / `bytes` / `bytearray` / `memoryview` / `open(encoding=)` / `getdefaultencoding` / `getfilesystemencoding` / `getpreferredencoding` / encode / decode / the two exceptions · Java `String` / `char` / `codePointAt` / `codePoints` / `StandardCharsets` / `getBytes` / `readString` / compact strings · JavaScript string / `charCodeAt` / `codePointAt` / `fromCharCode` / `fromCodePoint` / `TextEncoder` / `TextDecoder` / Node `Buffer` / the `u` flag · C `char` / `wchar_t` / `char16_t` / `char32_t` / `u8""` / `u""` / `U""` / `L""` / `strlen` / `wcslen` / `mbtowc` / `mbstowcs` / `setlocale` · C++ `std::string` / `wstring` / `u8string` / `u16string` / `u32string` / `string_view` / `codecvt` · Rust `String` / `&str` / `char` / `OsString` / `PathBuf` / `chars` / `bytes` / `encode_utf16` / `from_utf8` / `from_utf8_lossy` · Go `string` / `rune` / `byte` / range / `unicode/utf8` / `RuneCountInString` / `ValidString` / `strings.Builder` / `[]byte` conversion · Swift `Character` / `String` / `UnicodeScalar` / `String.Encoding` · Ruby `String` encoding / `Encoding` / magic comment · PHP string / `mb_string` / `mb_strlen` · Perl `use utf8` / `Encode` · C# `string` / `System.Text.Encoding` / `Rune`

**Missing — add, per language:**

- **Python:** `surrogateescape` and PEP 383 · `os.fsencode` / `os.fsdecode` · PEP 393 flexible representation (latin-1 / UCS-2 / UCS-4 internally — **one emoji quadruples a string's memory**, [`str` in memory](04_Python/str_in_memory/README.md)) · `sys.intern` · `-X utf8` and PEP 540 · `locale.getencoding()` vs the removed `getdefaultlocale` · the `regex` module vs `re` · `unicodedata.is_normalized` · `int.from_bytes` / `to_bytes` · `bytes.hex(sep)` · `str.isidentifier` · `ascii()` and `repr` escaping · `codecs.register_error` · **the `open()` default encoding is locale-dependent and PEP 686 is making it UTF-8** — the change that will silently fix and silently break code.
- **Rust:** `OsStr` / `OsString` and **WTF-8 on Windows** · `Path` is not `String` and `to_string_lossy` is a decision · `CStr` / `CString` · `char_indices` · `bstr` for byte strings that are usually text · `unicode-segmentation` · `unicode-width` · `unicode-normalization` · `encoding_rs` and `chardetng` · `simdutf8` · `str::from_utf8` vs `from_utf8_unchecked` (and the deny-by-default `invalid_from_utf8_unchecked` lint, measured on [Overlong sequences](03_Encodings/overlong_sequences/README.md)) · `to_uppercase` returns an iterator · `char::from_u32` returns `Option` · `eq_ignore_ascii_case` is the only built-in caseless compare · byte-index panics on a char boundary — the [slicing by byte](05_Rust/slicing_by_byte/README.md) stub.
- **Java:** JEP 400 (**UTF-8 became the default charset in Java 18** — before that, `file.encoding` came from the platform) · `Charset.defaultCharset()` · `native2ascii` and the `.properties` escape · JNI modified UTF-8 · `Normalizer` · text blocks · `String.length()` vs `codePointCount`.
- **JavaScript:** `Intl.Segmenter` (graphemes, words, sentences — finally) · `Intl.Collator` / `NumberFormat` / `DateTimeFormat` / `PluralRules` / `ListFormat` / `RelativeTimeFormat` · `isWellFormed` / `toWellFormed` · `String.raw` · `Array.from` splits by code point where `split('')` splits by code unit · `TextDecoderStream` · `Buffer` encodings that lie (`'binary'` is latin-1).
- **C / C++:** `char8_t` and C++20 `u8` literals · execution charset vs source charset · MSVC `/utf-8` · `_setmode(_O_U16TEXT)` and `wmain` on Windows · the UTF-8 process manifest · `std::text_encoding` (C++26) · `<charconv>` for locale-free number parsing · why `std::locale` is avoided in practice.
- **C#/.NET:** `Rune` · `StringInfo` for graphemes · **`CodePagesEncodingProvider` — .NET Core dropped every legacy code page and you must register them** · `StringComparison.Ordinal` vs `InvariantCulture` (the Turkish-i bug) · globalization-invariant mode · ICU replaced NLS in .NET 5.
- **Go:** `golang.org/x/text` (everything real lives here, not in std) · `strings.ToValidUTF8` · `norm` · `runewidth` · `[]rune(s)` allocates · source files are UTF-8 by language spec.
- **Swift:** `String` is native UTF-8 since Swift 5 · `count` is O(n) because it counts graphemes · `String.Index` is not an integer, on purpose · the four views (`unicodeScalars`, `utf8`, `utf16`, characters).
- **Ruby:** `force_encoding` vs `encode` (**relabel vs convert** — the clearest name for the distinction in any language) · `Encoding::CompatibilityError` · `String#scrub` · `ASCII-8BIT` is Ruby's name for "bytes".
- **PHP:** strings are bytes; `mb_*` is a separate extension; `mb_str_split`; `htmlspecialchars`'s charset argument default changed in PHP 8.
- **Perl:** the "Unicode bug", `use open`, `binmode`, `utf8::upgrade`, "Wide character in print".
- **ABAP / SAP** — **the missing track, and one of Adam's three goals.** `string` vs `xstring` · `STRLEN` vs `XSTRLEN` · `cl_abap_conv_in_ce` / `cl_abap_conv_out_ce` / `cl_abap_codepage` · `cl_abap_char_utilities` (`newline`, `horizontal_tab`, `cr_lf`) · `CX_SY_CONVERSION_CODEPAGE` · SAP code-page numbers (**verify against the system, never quote from memory**) · `OPEN DATASET ... IN TEXT MODE ENCODING UTF-8` vs `LEGACY TEXT MODE` · RFC and `SAP_CODEPAGE` · SAP GUI's own encoding · non-Unicode → Unicode conversion (SPUMG/SUMG, MDMP).
- **PowerShell** — `$OutputEncoding` vs `[Console]::OutputEncoding` vs `-Encoding`; **Windows PowerShell 5 writes UTF-16LE by default and PowerShell 7 writes BOM-less UTF-8**, so the same script produces two different files on two machines. A real-data page in one sentence.
- **Bash/zsh** — `$'€'` ANSI-C quoting · `printf '%b'` · `IFS` · `read -r` · `LC_ALL=C` changing glob ranges and `tr`. Mostly covered across [11_Tools](11_Tools/README.md).
- **SQL as a language** — identifier quoting, `N'...'` literals, `LENGTH` vs `CHAR_LENGTH` vs `DATALENGTH`, and per-column collation. See §10.
- **Editors** — Vim `fileencoding` / `bomb` / `:e ++enc=`; VS Code `files.encoding` and `files.autoGuessEncoding`; `.editorconfig`'s `charset`, `end_of_line`, `insert_final_newline`, `trim_trailing_whitespace`.

---

## 10. Storage and databases — **core (real data)**

**Imported:** database character set · collation · MySQL `utf8` (3-byte) vs `utf8mb4` · `utf8mb4_unicode_ci` / `_bin` · PostgreSQL server and client encoding · SQLite TEXT · Oracle `NLS_CHARACTERSET` / `AL32UTF8` / `NVARCHAR2` · SQL Server `NVARCHAR` / `VARCHAR` / collation · MongoDB BSON string · Redis · Elasticsearch analyzer · full-text normalization · inverted index · n-gram

**Missing — add:**

- **MySQL's `utf8` was a three-byte lie for 20 years** — it is now `utf8mb3` and deprecated, and inserting an emoji into it raises error 1366 *Incorrect string value*. The single most famous encoding bug in databases.
- **The 767/3072-byte index prefix limit** — why `VARCHAR(255)` became un-indexable when a column moved to `utf8mb4`. A byte limit meeting a character-count column definition.
- **PostgreSQL `SQL_ASCII` is not an encoding** — it means "no validation, no conversion", so the database will happily store two different encodings in one column and hand them back unchanged.
- **The glibc 2.28 collation break** — an OS upgrade changing sort order and silently invalidating every `text` index. `COLLATE "C"`, `citext`, and PG 15's ICU collations are the responses.
- **Oracle `NLS_LANG` on the client** — the classic mojibake source: the client *declares* an encoding and Oracle converts to match, so a wrong declaration corrupts on write, invisibly. Also `AL32UTF8` vs the older `UTF8` (which is CESU-8), byte vs char semantics (`NLS_LENGTH_SEMANTICS`), and `ORA-12899` — value too large *in bytes* for a column sized in characters.
- **SQL Server:** `_SC` collations are required for supplementary characters (without them, `LEN()` counts surrogate halves), `_UTF8` collations arrived in 2019, and `NVARCHAR` is UTF-16 so `N` is code units.
- **SQLite:** `PRAGMA encoding` is set once at creation; `LIKE` is ASCII-only case-insensitive unless you load ICU; there is no charset conversion at all.
- **Backup and restore is where encodings change hands** — `mysqldump --default-character-set`, `pg_dump` client encoding, and the double-encoding that follows.
- **The repair recipe** — `CONVERT(BINARY col USING utf8mb4)` and its Postgres/Oracle equivalents; and the prior question of whether the damage is reversible (§2.9).
- **Elasticsearch analyzers, ICU folding, and `keyword` vs `text`** — where normalization becomes a search-quality decision.
- **Kafka, S3, Parquet** — keys and values are bytes; a schema registry is the only place the encoding is written down.

---

## 11. Operating system and platform — **core**

*Covered:* [Locale and `LC_CTYPE`](06_Terminal/locale_and_lc_ctype/README.md) · [`find`, and filenames that are bytes](11_Tools/find/README.md)

**Imported:** filesystem encoding · NTFS UTF-16 · ext4 bytes · HFS+ / APFS normalization · Linux locale variables · Windows A vs W APIs · UTF-8 manifest · code page 65001 · `GetConsoleCP` · POSIX locale · SSH encoding · terminal emulator encoding · Python stdin encoding · UTF-8 Everywhere

**Missing — add:**

- **A POSIX filename is a byte string with two forbidden bytes** — `/` and NUL. Not text. `find` cannot match what `cat` can open; already measured on [`find`](11_Tools/find/README.md).
- **NTFS permits unpaired surrogates in filenames** — so a Windows filename may be unrepresentable in UTF-8, which is why Rust has WTF-8.
- **Windows reserved names and shapes** — `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, trailing dots and spaces, `\\?\` long paths, 8.3 short names. Half of them are still enforced in 2026.
- **musl has essentially no locale support** — so an Alpine container behaves differently from Debian on the same code. The container-era version of the BSD/GNU split this library already tracks.
- **`C.UTF-8` exists on modern macOS and Ubuntu** — measured 2026-09-05; the portable UTF-8 locale, at last.
- **argv and environment variables are bytes on POSIX and UTF-16 on Windows** — plus `CommandLineToArgvW`'s quoting rules, which are their own escaping language.
- **Clipboard formats** — `CF_UNICODETEXT`, and the fact that copying through the clipboard normalizes on macOS.
- **Filesystem name encoding across the wire** — SMB, NFS, `rsync --iconv`, and the Japanese-filename-over-SMB classic.
- **ISO 9660 / Joliet / Rock Ridge, exFAT and FAT LFN** — UTF-16 in the places nobody expects it.
- **WSL interop** — two filename models sharing one path.

---

## 12. Binary, compression and packed formats — **adjacent**

*Covered:* [Decompress, then decode](11_Tools/decompress_then_decode/README.md)

**Imported:** gzip · zlib · DEFLATE · bzip2 · xz / LZMA · zstd · LZ4 · Brotli · Huffman · RLE · LZW · chunked transfer encoding · Python `struct` · pack/unpack format strings · struct alignment · endian-aware packing · bit field · varint · LEB128 · base-128 · network packet encoding

**Missing — add:**

- **Order matters: compress, then encrypt, then encode** — and compressing attacker-influenced data beside a secret is CRIME/BREACH. **A compression ratio is a side channel.**
- **The gzip header's `FNAME` field is ISO-8859-1 by spec** — an encoding decision hiding in a compression format.
- **Brotli ships a built-in dictionary of English web text** — which is why it beats gzip on small HTML and not on your binary.
- **Zip bombs and decompression limits** — always bound the output, never the input.
- **rANS/tANS, dictionary training (`zstd --train`), delta encoding, VCDIFF/bsdiff** — the modern toolbox.
- **SCSU and BOCU-1** — compression schemes designed *for* Unicode, now historical, and a good closing note for §1.
- **Base64 inflates by 33%, so base64-then-gzip is usually wrong and gzip-then-base64 is usually right** — the practical version of the ordering rule.

---

## 13. Security and encoding — **core**

*Covered:* [12_Adversarial](12_Adversarial/README.md) — all five pages

**Imported:** SQL injection via encoding · XSS via encoding bypass · normalization attack · overlong UTF-8 · null-byte injection · path traversal via encoding · double URL encoding · Trojan Source · bidi overrides · zero-width characters in passwords · WAF bypass · content-sniffing XSS · charset confusion · MIME sniffing · `nosniff` · detection manipulation · mojibake as corruption · best-fit exploits · homoglyph phishing · IDN homograph · `confusables.txt` · UTF-7 injection · BOM stripping attack · timing attack · percent-encoding bypass · second-order injection

**Missing — add:**

- **PRECIS (RFC 8264/8265/8266)** — the *successor* to stringprep, with `UsernameCaseMapped`, `OpaqueString` for passwords, and `Nickname`. This library already teaches [stringprep](02_Characters/preparing_a_string/README.md); PRECIS is the sequel and the current advice.
- **Normalizing a password is a decision** — normalize and `café` typed two ways both log in; do not, and one of them silently fails forever. There is no option without a cost.
- **bcrypt truncates at 72 bytes** — so a long passphrase in a non-Latin script is *shorter than it looks* in entropy terms, and some implementations also truncate at a NUL byte.
- **Invisible tag characters (`U+E0000` block) as a prompt-injection carrier** — text that is invisible to a human reviewer and fully present to a model. The 2024–2026 version of Trojan Source, and the most current thing missing from the list.
- **Zero-width watermarking / Unicode steganography** — the same mechanism used deliberately.
- **RLO in a filename** — `...RLO...fdp.exe` displays as a PDF. Malware's favourite, and a bidi lesson with consequences.
- **Terminal escape injection through logs** — see §5.4.
- **mXSS (mutation XSS)** — the sanitized string is re-parsed by the browser and becomes something else. **A parser differential where both parsers are in the same browser.**
- **Hash flooding** — string keys chosen to collide, turning a hash map into a list; SipHash and randomized seeds are the fix (and why Python's `hash()` differs per process).
- **Length in bytes vs characters as a security boundary** — a truncation that splits a UTF-8 sequence, and a validator that counted the other unit.
- **Unicode in package names** — typosquatting with look-alikes on npm/PyPI/crates.io.
- **`%c0%af` and the IIS directory-traversal worm** — the overlong-encoding attack that actually happened, at scale, and the reason the shortest-form rule is enforced rather than recommended.

---

## 14. Identity, hashing and canonical forms — **core, absent from the imported list**

- **Hash before or after normalization?** — the question decides whether two spellings of one name are one account. On [Two people, one account](12_Adversarial/collisions_by_design/README.md).
- **Canonicalization for signatures** — XML C14N, JSON Canonicalization Scheme (RFC 8785), and why a signature over "the document" needs the document to have exactly one byte form.
- **Content addressing** — git's object ids, IPFS; a file's identity *is* its bytes, so a line-ending conversion changes its name.
- **Checksums vs hashes vs MACs** — CRC32, Adler-32, SHA-2, and what each one is actually promising.
- **Stable hashing across languages** — the same string must hash the same in Python and Rust, which needs a fixed encoding named in the protocol.
- **UUID text forms, ULID (Crockford base32), nanoid alphabets** — identifiers as text, and the alphabets chosen to survive being read aloud.

## 15. Numbers and dates as text — **adjacent, absent from the imported list**

- **Float round-tripping** — shortest representation that reparses exactly; Ryū and Grisu; why `0.1` prints as `0.1` in Python 3 and `0.1000000000000000055` in some others.
- **Locale decimal separators** — `strtod` obeys the locale, so parsing a config file under a Polish locale can fail. `<charconv>` and `Decimal` exist to escape it.
- **Leading zeros and accidental octal** — `int('010')` differs across languages; `parseInt` and radix.
- **Digit shapes that are not ASCII** — Python's `int()` accepts Arabic-Indic digits; almost nothing else does.
- **NaN, Infinity, `-0`** — text forms JSON has no room for.
- **ISO 8601 vs RFC 3339 vs Excel serial dates vs Unix epoch** — four formats, one column, in every export.

## 16. Testing, fuzzing and CI for text — **core, absent from the imported list**

- **The Big List of Naughty Strings** — the standard hostile corpus; every field that accepts text should have met it once.
- **Fuzzing a decoder** — the classic first fuzz target, and how most UTF-8 bugs were found.
- **Property-based testing with Unicode generators** — round-trip properties (`decode(encode(x)) == x`) are exactly the shape hypothesis/proptest want.
- **Golden files with invisible characters** — a recorded key holding a NBSP or a BOM that no reviewer can see. This library's own `check_decomposed_literals.py` exists for one instance of this.
- **A recorded key must not contain a Unicode table lookup** — measured, and written up on [The table has a version](02_Characters/the_table_has_a_version/README.md).
- **Testing across BSD and GNU** — this library's own hardest-won lesson; seven documented tool splits and counting.

## 17. Input: keyboards, IMEs and clipboards — **adjacent, absent from the imported list**

- Compose key · dead keys · `U+0301`-style combining input · macOS Unicode Hex Input · `Ctrl+Shift+U` on Linux · Vim digraphs · `\N{}` in Python · `uni print`.
- **Input methods (IME)** — composition state, and why a keystroke is not a character in Chinese, Japanese or Korean.
- **Smart quotes and autocorrect** — the most common way a `U+2019` gets into a config file or a password, and the reason "it works when I retype it".
- **Clipboard normalization** — copying through macOS can change the bytes.

## 18. Accessibility and text — **adjacent, absent from the imported list**

- **Mathematical alphanumeric symbols destroy screen readers** — "fancy text" is `MATHEMATICAL BOLD SMALL A`, announced as such or skipped. A real harm, and a normalization argument (NFKC folds them back).
- **Emoji announcement** — a screen reader reads the CLDR name aloud, so a decorative emoji run is a sentence.
- **`lang` attributes drive pronunciation and font selection** — the same code point, two languages, two renderings.
- **Text alternatives, `aria-label`, and text in images** — the accessibility version of "a screenshot is not evidence about a string".

## 19. Text for language models — **adjacent, absent from the imported list, and current**

- **Tokenizers:** byte-level BPE (`tiktoken`), WordPiece, SentencePiece, byte fallback — and that a token is neither a character nor a word.
- **Why "strawberry" appears to have two r's** — the model sees tokens, not letters. The clearest possible demonstration that "a string" depends on who is counting, which is this library's thesis arriving somewhere new.
- **Non-Latin scripts cost more tokens** — the same sentence in Polish or Japanese consumes several times as many tokens as in English, which is a cost, a context-window limit and a fairness question at once.
- **Invisible characters in prompts** — see §13.
- **Normalization before embedding** — the same silent decision as before search indexing.

## 20. Famous bugs and case studies — **core, absent from the imported list**

Teaching material, all of it. Each of these is one page's worth of hook.

- **"Bush hid the facts"** — Notepad's charset detector reading a 4-word ASCII file as UTF-16.
- **The IIS overlong-UTF-8 traversal worm** — §13.
- **The Turkish-i bug** — in .NET, in Java, in Android.
- **The glibc 2.28 collation change** — §2.6, §10.
- **MySQL `utf8` being three bytes** — §10.
- **Trojan Source (2021)** — and RFC 3454 having prohibited the same code point by number in 2002.
- **The Telugu character that crashed iOS** ("effective power", chaiOS) — a rendering bug reachable by a text message.
- **The black-flag / ZWJ crashes** — malformed emoji sequences as a denial of service.
- **Spotify's username canonicalization collision** — two users, one account, exactly [collisions by design](12_Adversarial/collisions_by_design/README.md).
- **The `hexdump` swapped-pairs default** — small, local, measured by this library, and the same genre.

## 21. Standards, registries and where to look it up — **reference**

- **Unicode:** the Standard, the UAX/UTS/UTR series, the UCD files, CLDR, ICU, `confusables.txt`, `NormalizationTest.txt`.
- **IETF:** RFC 3629 (UTF-8) · 3986 (URI) · 3987 (IRI) · 3492 (Punycode) · 5890–5895 (IDNA2008) · 4648 (Base64) · 2045–2049 (MIME) · 2047 (encoded words) · 6531/6532 (EAI) · 8259 (JSON) · 8264–8266 (PRECIS) · 8187 (HTTP header charset) · 4180 (CSV) · 7464 (JSON sequences) · 8785 (JCS).
- **ISO:** 10646 · 8859-x · 2022 · 8601 · 646.
- **W3C / WHATWG:** the Encoding Standard, the URL Standard, HTML's charset rules, Internationalization Best Practices.
- **IANA:** the Character Sets registry, the language subtag registry.
- **Where to look a character up:** [`uni`](11_Tools/uni/README.md) · `unicodedata` · unicode.org charts · codepoints.net · the [RESOURCES.md](RESOURCES.md) list, every link of which was checked the day it was added.
