# Why UTF-16 stayed

**Level:** 201 · for anyone starting from zero

**One line:** UTF-16 lost the format war and is still inside Java, JavaScript, Windows and every SAP system, because all four adopted Unicode while it was still a *fixed-width 16-bit* character set — and ABAP had a second reason the others did not, which is that its field offsets are arithmetic.

## The question

[Why UTF-8 won](../why_utf8_won/README.md) is the argument. This page is about what happened to the loser, which is the stranger half of the story: UTF-16 is not a curiosity you read about and move past. It is the string type of the language most enterprise software is written in, of the one every browser runs, of the Windows system-call layer, and of every SAP system on earth. The gap between *"ABAP is weird"* and *"ABAP is a decision from 1993 whose consequences you can predict"* is this page.

## 1991: sixteen bits was not a compromise, it was the pitch

Unicode 1.0 shipped in [October 1991 ↗](https://www.unicode.org/history/publicationdates.html), and the thing being sold was not "a bigger character set." It was **the end of encodings as a topic**: one table, every character in exactly two bytes, fixed width, no code pages, no mode switches, no variable-length anything. Sixteen bits hold 65,536 code points and the repertoire needed a fraction of that, so the encoding question looked answered before it was asked. That design has a name — **UCS-2** — and for five years it was simply what "Unicode" meant.

Which means the systems that got Unicode *right on time* are exactly the ones that got it wrong. Adopting early meant adopting UCS-2, and UCS-2 went into the places that are hardest to change: type widths, ABI-level function signatures, and the semantics of `length`.

| System | Adopted Unicode | What its `length` counts | Got out? |
|---|---|---|---|
| Windows NT | 1993 | `wchar_t` is 16 bits | No — the `…W` entry points *are* the ABI |
| Java | mid-1990s | `String.length()` — 16-bit units | No — JDK 9 compact strings changed the *storage*, not the semantics |
| JavaScript | 1995 | `.length` — 16-bit units | No — frozen by every page on the web |
| Qt, ICU | mid-1990s | `QChar` is 16 bits | No |
| **ABAP** | the 6.x releases, early 2000s | `strlen( )` — 16-bit units | No |
| Python | 2.0, in 2000 | `len()` — **code points** | **Yes**, and it is the only one |

Python is the interesting row because it was in the club and left. Its original `unicode` type was UCS-2 on a "narrow" build, so `len('😀')` really did return `2`, the same answer Java gives today. [PEP 393 ↗](https://peps.python.org/pep-0393/) (Python 3.3, 2012) replaced that with a per-string representation picked by the widest character, and `len()` has counted code points everywhere since — at the cost of a `str` whose memory quadruples when one emoji joins it, which is [`str` in memory](../../04_Python/str_in_memory/README.md). Nobody else could pay that bill, because nobody else's `length` was an implementation detail. In Java and JavaScript it is a specified, published number that programs branch on.

## 1996: the promise stops being true

Unicode 2.0 arrived in [July 1996 ↗](https://www.unicode.org/history/publicationdates.html) and widened the codespace to 1,114,112 code points — seventeen planes instead of one. To let a 16-bit encoding reach the new sixteen, it introduced the **surrogate pair**: two units, from two reserved blocks, standing for one character. UCS-2 became UTF-16 on that day, and "fixed width" quietly became "variable width."

The cost was not paid in 1996, which is the whole problem. It was paid over the following thirty years by everyone whose API had already promised that a character was a unit. The mechanism — the `D800`–`DBFF` / `DC00`–`DFFF` ranges and the arithmetic that turns `U+1F600` into `D83D DE00` — belongs to [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md); what matters here is the *timing*. Five years of shipped code assumed something that stopped being true, and no deprecation cycle can reach into every caller that stored a length in a database column.

## ABAP's second reason: an offset is arithmetic

Every system in the table above is stuck for the shared reason — the semantics escaped into the API. ABAP is stuck for that reason **and** a sharper one that is worth understanding on its own, because it is the one that makes the choice look correct rather than merely early.

**ABAP is a language of fixed-length fields.** `DATA city TYPE c LENGTH 8.` is eight characters, not "a string." Structures have computable layouts, internal tables have fixed row widths, interfaces are columns at known positions, and the language has offset/length access as *syntax*:

```abap
DATA(code) = record+8(3).      " characters 8 through 10
```

Before Unicode, one character was one byte, so "eight characters in" and "eight bytes in" were the same sentence — and that identity was load-bearing across every customer program, every file layout, and every structure definition in the installed base.

Look at what each candidate does to it:

- **UTF-16 keeps the arithmetic and changes the constant.** One character becomes two bytes, uniformly, so `record+8(3)` is still bytes 16 to 21 and a structure's offsets are still constants. `cl_abap_char_utilities=>charsize` returns `2` on a Unicode system where it returned `1` before — a single number, in one place, and the layout rules survive intact.
- **UTF-8 makes the offset a function of the data.** In `'Kraków  PLN'` the code field starts at byte 9; in `'Gdansk  PLN'` it starts at byte 8. Same layout, same field, different number — because `ó` is two bytes and `a` is one. A structure definition cannot hold a number that moves, and no compiler can find the callers that assumed otherwise.

Section 5 of the Python program below runs exactly that comparison. **This is why the migration was possible at all**: UCS-2 was a *widening* of a rule ABAP already had, and UTF-8 would have been a rewrite of every offset in every program that ever touched a record.

And the choice left a visible scar in the language, which is the part worth recognising when you meet it: the Unicode conversion is why ABAP hard-separates `c` from `x` and `string` from `xstring`, why offset access across those types is refused, and why the whole installed base had to be walked with the Unicode checks before it could be switched on. Those rules read like fussiness until you know they are the compiler being asked to find every place that had assumed a byte was a character.

## What the choice cost

Three bills, and the third is the one that still surprises people.

1. **Surrogates, forever.** `strlen( )` on an emoji is `2`. So is Java's `.length()` and JavaScript's `.length`. The fixed width that justified the decision is not actually fixed above `U+FFFF`, so UTF-16 pays the variable-width price *and* gives up ASCII compatibility — which is the case for calling it the worst of both, and it is fair.
2. **Byte order.** A 16-bit unit has two spellings, so UTF-16 files need a [byte-order mark](../../03_Encodings/byte_order_and_bom/README.md) and UTF-8 files do not. This is property 5 in [Why UTF-8 won](../why_utf8_won/README.md).
3. **A sort that is not code-point order.** Lead surrogates live at `D800`, *below* the ordinary code points at `E000`–`FFFF`, so sorting UTF-16 bytes puts every astral character in the wrong place. Section 4 below prints the inversion. It stays invisible while the kernel does your sorting and appears the moment you hash, sign, or byte-compare something you converted yourself.

There is a fourth, smaller one that shows how far the decision travels: `json.dumps("😀")` produces `"\ud83d\ude00"` — a UTF-16 surrogate pair, written into a format that is UTF-8 by specification. JSON's escape syntax was designed in JavaScript, so a 1995 storage decision is now visible in a wire format that has no UTF-16 anywhere in it.

## In Python

<!-- output:why_utf16_stayed_py -->
*Verified output of [`why_utf16_stayed_py.py`](examples/why_utf16_stayed_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE 1991 PROMISE: EVERY CHARACTER IN EXACTLY TWO BYTES
------------------------------------------------------------------------
   Sixteen bits hold 65,536 code points, and Unicode 1.0 needed
   far fewer. So the encoding question had an obvious answer: one
   character, one 16-bit unit, fixed width, forever.

   char   code point   utf-16-be    units
   A      U+0041       00 41        1
   é      U+00E9       00 e9        1
   ż      U+017C       01 7c        1
   €      U+20AC       20 ac        1
   日     U+65E5       65 e5        1
   ಠ      U+0CA0       0c a0        1

   Six characters from four scripts, one unit each. That is UCS-2 — and
   it is what Windows NT (1993), Java and JavaScript (both designed in
   1995) and SAP's Unicode kernel were all built on.

2. WHAT FIXED WIDTH BUYS: AN OFFSET IS JUST ARITHMETIC
------------------------------------------------------------------------
   A fixed-width record — city in 8 characters, then a 3-character code:
     'Kraków  PLN'   11 characters
     utf-16-le : 22 bytes  = 2 x 11
     utf-8     : 12 bytes  = it depends

   'The code field' is characters 8..11. Under UTF-16 you reach it by
   multiplying the offset by two, and nothing else:
     rec[8:11]                       -> 'PLN'
     u16[16:22].decode('utf-16-le')  -> 'PLN'

   The same multiply-by-N trick in UTF-8 cuts a character in half:
     u8[:5]  -> b'Krak\xc3'   the first 5 BYTES
     u8[:5].decode('utf-8') raises: unexpected end of data
     u16[:10].decode('utf-16-le') -> 'Krakó'   the first 5 CHARACTERS

3. THE 1996 BREAK: THE PROMISE STOPS BEING TRUE
------------------------------------------------------------------------
   Unicode 2.0 (July 1996) widened the codespace to 1,114,112 code
   points — 17 planes, not one — and invented the surrogate pair to
   let a 16-bit encoding reach them. UCS-2 became UTF-16 that day, and
   'fixed width' quietly became 'variable width'.

     😀  U+1F600  utf-16-be d8 3d de 00  = 2 units, 4 bytes

   So the identity section 2 was built on holds for some strings and not
   others, and nothing in the type says which:

     string             chars  utf-16 bytes   2 x N ?
     'café'                 4             8   holds
     'Kraków  PLN'         11            22   holds
     '日本語'               3             6   holds
     '😀'                   1             4   BREAKS
     'a😀b'                 3             8   BREAKS

   And this is the length disagreement that outlived the decision:
     len('😀')                          = 1   Python counts code points
     len('😀'.encode('utf-16-le')) // 2 = 2   Java, JavaScript and ABAP
                                              count 16-bit units

4. THE BILL: TWO SPELLINGS, AND A SORT THAT IS NOT CODE-POINT ORDER
------------------------------------------------------------------------
   A 16-bit unit is two bytes, so it has an order, so a file needs a
   mark to say which one it used:
     utf_16_be    00 e9
     utf_16_le    e9 00
     utf_16       ff fe e9 00
   The third one is not a third encoding — it is UTF-16 with a BOM in
   front, which is the platform's order written down.

   And because lead surrogates sit at D800-DBFF, below the last ordinary
   code points at E000-FFFF, sorting UTF-16 bytes is NOT sorting by code
   point. The same five characters, three ways:
     by code point        A é 日 � 😀
     by utf-8 bytes       A é 日 � 😀
     by utf-16-be bytes   A é 日 😀 �   <- inverted

5. AND WHY NOBODY LEFT: THE OFFSETS LIVE IN THE CALLERS
------------------------------------------------------------------------
   The same 8-character city field, in two records that differ only in
   their data:

     record             utf-16-le        utf-8
     'Kraków  PLN'         16..22        9..12
     'Gdansk  PLN'         16..22        8..11

   The UTF-16 offsets are the same in both because they are 2 x 8. The
   UTF-8 offsets move, because 'ó' is two bytes and 'a' is one — so the
   number belongs to the DATA, not to the layout.

   A structure definition cannot hold a number that moves. That is the
   whole reason a language built on fixed-length fields could adopt
   UCS-2 as a widening of an existing rule (1 char = 1 byte became
   1 char = 2 bytes) and could not adopt UTF-8 as anything short of
   rewriting every offset in every program that ever touched the record.
```
<!-- /output -->

## In Rust

Rust is the control group. It was designed long after 1996 with the whole mess visible, and it is the one language here that had the option to store 16-bit units and declined — UTF-16 exists in `std` as a *conversion* and never as a type.

<!-- output:why_utf16_stayed_rs -->
*Verified output of [`why_utf16_stayed_rs.rs`](examples/why_utf16_stayed_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THERE IS NO UTF-16 STRING TYPE, AND THAT IS THE POINT
------------------------------------------------------------------------
   size_of::<char>() = 4   a char is a CODE POINT, not a 16-bit unit
   size_of::<u16>()  = 2   the unit Java, JavaScript and ABAP count

   std has String (UTF-8) and OsString (the platform's bytes). It has
   no Utf16String at all — on Windows, where the OS speaks UTF-16,
   the conversion happens at the system call and not in the type.

2. UTF-16 IS A CONVERSION HERE, NEVER A STORAGE FORMAT
------------------------------------------------------------------------
   label      code point   chars u16 len  u8 len   char
   ascii      U+0041           1       1       1   A
   accent     U+00E9           1       1       2   é
   polish     U+017C           1       1       2   ż
   cjk        U+65E5           1       1       3   日
   astral     U+1F600          1       2       4   😀

   len_utf16() is a question you have to ASK. In a language whose
   strings are UTF-16 it is the answer you get by default, which is
   why their `length` is a unit count and nobody chose that.

3. THE DOOR BACK IS FALLIBLE, BECAUSE UTF-16 CAN HOLD NON-TEXT
------------------------------------------------------------------------
   a valid pair             [D83D DE00]  -> Ok("😀")
   a lone lead surrogate    [D83D]  -> Err(invalid utf-16: lone surrogate found)
   a lone trail surrogate   [DE00]  -> Err(invalid utf-16: lone surrogate found)

   A lone surrogate is a perfectly ordinary u16, so any UTF-16 buffer
   can contain one — a truncated string, a bad concatenation, a file
   cut at the wrong byte. Rust makes you handle it:
   from_utf16_lossy([D83D]) -> "�"

4. AND A char CANNOT BE A SURROGATE AT ALL
------------------------------------------------------------------------
   char::from_u32(0x0041) = Some('A')
   char::from_u32(0xD7FF) = Some('\u{d7ff}')
   char::from_u32(0xD800) = None   <- reserved for UTF-16's sake
   char::from_u32(0xDFFF) = None   <- reserved for UTF-16's sake
   char::from_u32(0xE000) = Some('\u{e000}')
   char::from_u32(0x1F600) = Some('😀')

   Those 2,048 code points are not characters and never will be. They
   exist only so that a 16-bit encoding can reach past 16 bits — a
   permanent hole punched in Unicode itself, in 1996, to rescue the
   encoding this page is about. Rust declines to represent them, which
   is a choice only a language that does not store UTF-16 can make.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** You are on the other side of this history, and `len()` is the proof: it counts code points, so `len('😀')` is `1` where Java, JavaScript and ABAP all say `2`. That was not always true — narrow builds gave you `2` as well — and the escape cost the flexible representation described in [`str` in memory](../../04_Python/str_in_memory/README.md). The place the old world still reaches you is at interfaces: `json.dumps` emits surrogate pairs by default (`ensure_ascii=False` stops it), `'utf-16'` with no suffix writes a BOM where `'utf-16-le'` does not, and a lone surrogate from a UTF-16 source will encode to UTF-8 only under `errors='surrogatepass'`. Everything that hurts here arrives from a system that made the 1991 choice.

**ABAP.** This page is largely about your runtime, so the practical version is short. `strlen( )` counts 16-bit units, so an emoji is `2` and a Polish letter is `1`; `xstrlen( )` on the converted `xstring` is the byte count, and those are the two different questions [`unicode_code_points`](../../02_Characters/unicode_code_points/README.md) is about. `cl_abap_char_utilities=>charsize` is the constant the whole layout argument above rests on. The rule that follows is the one in [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md): let the internal representation stay the kernel's business, and convert to UTF-8 at every boundary — anything hashed, signed, or byte-compared with an outside system — because the byte order and the sort order in bills 2 and 3 above are exactly what a foreign system will disagree with you about. Two things to check against your own system rather than against this page: the SAP code-page numbers for UTF-16BE, UTF-16LE and UTF-8 are three different numbers and none of them should be quoted from memory (the table is in [SAP code pages](../../07_Real_Data/sap_code_pages/README.md)), and on a HANA-based system the database's own character storage is not necessarily the runtime's, so a conversion at the database interface is worth confirming for your release rather than assuming in either direction. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 09_History/why_utf16_stayed/examples
python3 why_utf16_stayed_py.py
rustc --edition 2024 why_utf16_stayed_rs.rs -o /tmp/utf16stayed && /tmp/utf16stayed
```

Without the machine: a record layout says the city field is characters 0–7 and the country code is 8–9. You are told the file is UTF-16 and 40 bytes long. Where does the country code start, and what is the one assumption that answer depends on? Then the same file arrives as UTF-8, still 40 bytes. Where does it start now — and what would you have to read before you could say?

## See also

- [Why UTF-8 won](../why_utf8_won/README.md) — the other half; this page is its loser's history
- [From the telegraph to Unicode](../from_telegraph_to_unicode/README.md) — the eras before 1991
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — the mechanism this page only dates
- [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) — where the offset argument lands in practice
- [`str` in memory](../../04_Python/str_in_memory/README.md) — what Python paid to leave the club
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — the rule that follows from all of it
- [Unicode publication dates ↗](https://www.unicode.org/history/publicationdates.html) — the primary source for every date here
- [UTF-8, UTF-16, UTF-32 & BOM FAQ ↗](https://www.unicode.org/faq/utf_bom.html) — the Consortium's own answers, including why the surrogate blocks are where they are
