# `rune` is an `int32`

**Level:** 201 · for anyone who meets the word in Go, .NET or a man page

**One line:** Go's name for one code point is `rune`, and a `rune` is an `int32` "in all ways" — so it holds `-1`, a surrogate or a number past `U+10FFFF` without complaint, the check Rust builds into `char` becomes a function you have to remember to call, and a Go loop over broken UTF-8 writes one `U+FFFD` per bad **byte** where Python and Rust write one per **mistake**.

The word turns up in three places sooner or later — every Go loop over a string, .NET's `System.Text.Rune`, and a BSD man page, [`mbrune(3)`](../../13_Documentation/the_encoding_man_pages/README.md) — and it always means *one code point*. What it does not mean is one guarantee. Go's `rune` holds any 32-bit integer and checks none of them; .NET's `Rune` holds only the 1,112,064 scalar values, and its constructor throws on anything else. Same word, opposite promises — and Microsoft's documentation for its type says in so many words that it is not Go's.

## One word, two promises

| | declared as | what it will hold | where the check lives |
|---|---|---|---|
| **Go** `rune` | `type rune = int32` | every `int32` — 4,294,967,296 values | not in the type: `utf8.ValidRune(r)`, if you call it |
| **.NET** `Rune` | `readonly struct Rune` | the 1,112,064 scalar values | the constructor: `new Rune(0xD800)` throws |
| **BSD** `rune_t` | `wchar_t` under another name | every `wchar_t` | nowhere |
| **Plan 9** `Rune` | `typedef unsigned long Rune;` | 21-bit values, in the Plan 9 paper's fourth-edition text | nowhere |

And the same job under other names:

| | the type | what it will hold | where the check lives |
|---|---|---|---|
| **Rust** | `char` | the scalar values | the constructor: `char::from_u32(0xD800)` is `None` |
| **Swift** | `Unicode.Scalar` | the scalar values | the initializer: `Unicode.Scalar(0xD800)` is `nil` |
| **Python** | none — `ord()` gives an `int`, `chr()` a one-character `str` | every code point, surrogates included | the range at `chr()`, the surrogates at `.encode()` |
| **Java** | none — a code point is an `int` | anything; `Character.isValidCodePoint(0xD800)` is `true` | the range, if you ask |
| **C** | `char32_t` (C11) or `wchar_t` | any value of the type | nowhere — and on macOS 26, `#include <uchar.h>` does not even find the header that declares `char32_t` |

Read the last column down both tables and the languages fall into two camps. In one, a value that is not a character **cannot be built**: Rust, Swift, .NET's `Rune`. In the other it can be built, stored and passed along, and whatever reads it later decides what it meant: Go, Python, Java, C. Go is the purest member of the second camp, because its rune is not even a type of its own.

## "Equivalent to `int32` in all ways"

That is how Go's own source documents the type ([`builtin` ↗](https://pkg.go.dev/builtin#rune)), and it means exactly what it says. `rune` is an **alias** — a second name for `int32`, not a second type — so the difference between a character and a count lives in the programmer's head and nowhere else; the same comment says the name is used *by convention*. Every line of it runs in [the Go program below](#in-go), which CI builds and checks on Ubuntu and macOS on every push:

```go
var r rune = 0xD800            // compiles: 0xD800 is an int32, so it is a rune
fmt.Printf("%T\n", r)          // int32
fmt.Println(utf8.ValidRune(r)) // false
fmt.Println([]byte(string(r))) // [239 191 189]

var n int32 = 'A'
r = n                          // no conversion: one type, two names
fmt.Println(r)                 // 65

var neg rune = -1
fmt.Println(neg, utf8.ValidRune(neg)) // -1 false
```

Three consequences, one for each group of lines.

**`%T` cannot see the name.** By the time anything can ask, the alias is gone, and Go reports `int32`. The Rust program below declares the same alias and gets the same answer out of `TypeId`.

**The check is a function.** `utf8.ValidRune` exists because the type cannot carry the rule — [its documentation ↗](https://pkg.go.dev/unicode/utf8#ValidRune) calls out-of-range values and surrogate halves illegal — and like any function it runs only where somebody wrote the call.

**A conversion that cannot fail has to do something else.** `string(r)` on a rune that is not a scalar value does not panic and returns no error: [the spec ↗](https://go.dev/ref/spec#Conversions_to_and_from_a_string_type) converts it to `U+FFFD`, which is the `[239 191 189]` above — `ef bf bd`. That is a third answer to *where does the check go?* Rust refuses to build the value and Python refuses to encode it ([`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md) shows both), while Go writes something else and says nothing. It is the only silent one of the three.

And one conversion is a famous mistake precisely because a rune is an integer: `string(rune(65))` is `"A"`, not `"65"`. Written with a plain `int`, `string(i)` still compiles — `go build` exits 0 — and `go vet` flags it with exit status 1 (measured by hand on go1.25.5: the runner builds and runs a program, and does not vet it).

## One `U+FFFD` per byte

The loop every Go program writes hands you a byte offset and a rune:

```go
for i, r := range "aé€😀" {
    fmt.Print(i, ":", r, " ") // 0:97 1:233 3:8364 6:128512
}
```

The offsets are `0 1 3 6` — bytes, which is what Rust's `char_indices()` gives you, for the same reason ([`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md), section 3). The difference is what happens when the bytes are not UTF-8. A Go `string` is bytes with a UTF-8 *convention* rather than a guarantee ([measured](../../10_Best_Practices/what_your_language_gives_you/README.md)), so the loop has to cope, and [the spec ↗](https://go.dev/ref/spec#For_range) says how: at an invalid sequence the rune is `0xFFFD` and the loop moves on by a single byte. `utf8.RuneCountInString` counts the same way — [its documentation ↗](https://pkg.go.dev/unicode/utf8#RuneCount) makes every erroneous or short encoding a rune one byte wide.

Python and Rust do not. They write one `U+FFFD` per **maximal subpart** — the longest run of bytes that could still have become a character, as [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md#how-many-ufffd-is-a-separate-question) sets out — so a Go service and a Python service reading the same broken field can count it differently:

- `e2 82`, a euro sign cut after two of its three bytes: Python writes **1**, Go writes **2**.
- `f0 9f 98`, `😀` cut after three of its four: Python **1**, Go **3**.
- `ed a0 80`, the surrogate `U+D800` written in UTF-8's shape: **3** and **3**, because the decoder turns it down at the second byte and each byte is a mistake of its own.

**The rule is exact, and it was checked by exhaustion rather than by example.** Over every input of one, two and three bytes — 16,843,008 of them — Go's count (go1.25.5, a `DecodeRuneInString` loop) equals the total **length** of the mistakes Python 3.14.7's decoder reports, input for input, with no exception. The two counts part on 562,368 of those inputs, and every one of them contains a mistake longer than a byte; none of the 16,280,640 on which they agree does. A mistake is longer than a byte in exactly one situation — a character that began correctly and was cut short with two or more of its bytes still there — so that is the whole of the difference. **Go and Python count broken UTF-8 the same way except where a character was cut off after two or more of its bytes.**

That is not an exotic input. It is what a [fixed-width byte field](../../07_Real_Data/fixed_width_byte_fields/README.md) that truncates rather than refuses does to every value that does not fit, and it is the case the kata below is built on.

**Is Go wrong?** No. Unicode's conformance clause C10 requires a decoder to treat an ill-formed sequence as an error and leaves the number of markers to the decoder — the same section of *Encode, decode and errors* has it. The web is stricter: the [Encoding Standard's UTF-8 decoder ↗](https://encoding.spec.whatwg.org/#utf-8-decoder) matches Unicode's best practice for `U+FFFD` and permits no other behaviour, so a browser may not count the way Go does, and Go is under no obligation to count the way a browser must.

## Five answers to one question

Go is not the only decoder with a count of its own. The same five byte strings through eleven decoders on one machine. Python's, Rust's and both of Go's counts are re-run on every push by the programs below; the rest were measured by hand on 2026-09-10 and are dated for that reason (the versions are [below](#what-was-measured-and-where)):

| bytes | what they are | Python, Rust, JS, Swift, .NET, Ruby | Go `range` | Go `ToValidUTF8` | Java | Perl `Encode` |
|---|---|---|---|---|---|---|
| `c3` | `é` cut after 1 of its 2 bytes | 1 | 1 | 1 | 1 | 1 |
| `e2 82` | `€` cut after 2 of 3 | 1 | **2** | 1 | 1 | 1 |
| `f0 9f 98` | `😀` cut after 3 of 4 | 1 | **3** | 1 | 1 | 1 |
| `ed a0 80` | `U+D800` in UTF-8's shape | 3 | 3 | **1** | **1** | **1** |
| `f4 90 80 80` | one past `U+10FFFF` | 4 | 4 | **1** | 4 | **1** |

The first count column is six implementations that agree on every row — the maximal-subpart rule, which the web requires. Go's loop counts bytes. Go's `strings.ToValidUTF8` counts **runs**: [its documentation ↗](https://pkg.go.dev/strings#ToValidUTF8) replaces each run of invalid bytes with one replacement, so mistakes that touch merge into one. Java — through `new String(bytes, UTF_8)` and through a `CharsetDecoder` set to `REPLACE` alike — writes one marker for an encoded surrogate where the majority writes three, and agrees with the majority on every other row here. Perl's `Encode` writes one on every row: anything with the *shape* of a UTF-8 sequence becomes a single mistake, the surrogate and the out-of-range value alike. Five answers, and none of them breaks the one rule Unicode makes — flag the mistake, never read it as a character. What an attacker does with two components that count one input differently is [a ranked page of its own](../../TODO.md); [Two readers, one byte string](../../12_Adversarial/parser_differentials/README.md) is the general form.

## In Go

The runner builds Go since 2026-09-11 — `examples/*.go`, one file at a time, standard library only — so every Go claim on this page is re-run on Ubuntu and macOS on every push rather than measured once by hand.

<!-- output:rune_is_an_int32_go -->
*Verified output of [`rune_is_an_int32_go.go`](examples/rune_is_an_int32_go.go) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A RUNE IS AN int32, AND THE TYPE CANNOT TELL THE DIFFERENCE
   var r rune = 0xD800        compiles, and %T says int32
   var n int32 = 'A'; r = n   compiles with no conversion; r is 65
   string(rune(65))           "A", not "65": a rune converts as a code point

        value   utf8.ValidRune  []byte(string(r))
           -1   false           ef bf bd
         0x41   true            41
         0xE9   true            c3 a9
       0xD800   false           ef bf bd
     0x10FFFF   true            f4 8f bf bf
     0x110000   false           ef bf bd
   All six compile, because each one is an int32. utf8.ValidRune is the
   check, and it runs only where somebody writes the call. string(r) never
   fails: for the three values it cannot encode it writes ef bf bd, which
   is U+FFFD, and reports nothing.

2. THE LOOP HANDS YOU BYTE OFFSETS
   s = "aé€😀"
   for i, r := range s        0:U+0061  1:U+00E9  3:U+20AC  6:U+1F600
   len(s)                     10   <- bytes
   utf8.RuneCountInString(s)  4    <- runes
   The index is the offset of each rune's first BYTE -- 0, 1, 3, 6 -- and
   len() counts bytes. A Go string is a run of bytes that is usually UTF-8,
   and nothing in the type promises that it is.

3. ONE U+FFFD PER BYTE -- OR PER RUN
   bytes         range  RuneCount  ToValidUTF8   what they are
   c3                1          1            1   é cut after 1 of its 2 bytes
   e2 82             2          2            1   € cut after 2 of its 3 bytes
   f0 9f 98          3          3            1   😀 cut after 3 of its 4 bytes
   ed a0 80          3          3            1   U+D800 in the shape of UTF-8
   f4 90 80 80       4          4            1   one past U+10FFFF, same shape
   range writes U+FFFD and moves on ONE byte, so a euro sign cut after two
   of its bytes is two broken runes -- and utf8.RuneCountInString counts
   them the same way. strings.ToValidUTF8 replaces each RUN of bad bytes
   with one replacement, so the touching mistakes of rows 4 and 5 become
   one. The Python and Rust programs on this page write one per maximal
   subpart instead -- 1, 1, 1, 3, 4 -- and the page has the rule that
   turns one count into the other.

4. A REAL U+FFFD AND A BROKEN BYTE, TOLD APART ONLY BY THE WIDTH
   DecodeRuneInString(ef bf bd)   r == RuneError: true    size 3   a genuine U+FFFD, correctly encoded
   DecodeRuneInString(f0 9f 98)   r == RuneError: true    size 1   the cut-short 😀 from section 3
   Both come back as RuneError, because a decoder that replaces has to hand
   you SOME rune. Only the size separates them: (RuneError, 1) is the one
   result that correct UTF-8 can never produce. A range loop hands you the
   index and the rune but not the size, so `r == utf8.RuneError` alone
   cannot tell a broken byte from a U+FFFD the text really contained.
```
<!-- /output -->

Section 1 is the alias doing exactly what its documentation says: `%T` reports `int32`, an `int32` goes into a `rune` with no conversion, and `utf8.ValidRune` is the only thing in the program that knows which of the six values are characters. Section 3 is the census's two Go columns, counted by Go itself. Section 4 is why `r == utf8.RuneError` is not a validity test: a genuine `U+FFFD` and a broken byte both come back as `RuneError`, and only the width — which `range` does not hand you — tells them apart.

## In Python

Python has no rune, and needs none for this page's question. Its decoder reports every mistake with a start and an end, and those two numbers are enough to compute all three of Go's and Python's policies — section 2 does it for the five inputs, and section 3 tests the rule against every input of one or two bytes.

<!-- output:rune_is_an_int32_py -->
*Verified output of [`rune_is_an_int32_py.py`](examples/rune_is_an_int32_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. HOW MANY VALUES EACH LANGUAGE WILL CALL ONE CHARACTER
   Go       a rune is an int32          4,294,967,296   every one of them
   Python   chr() takes a code point        1,114,112   surrogates included
   Rust     a char is a scalar value        1,112,064   surrogates refused

   chr(-1)         ValueError
   chr(0x41)       'A'        .encode('utf-8') -> 41
   chr(0xD800)     '\ud800'   .encode('utf-8') -> UnicodeEncodeError
   chr(0x110000)   ValueError
   Python checks the RANGE at chr() and leaves the surrogates to .encode().
   Rust checks both, at char::from_u32. A Go rune checks neither: it is an
   int32, and 4,293,855,232 int32 values are not a scalar value --
   the only kind of number UTF-8 can write. -1, 0xD800 and 0x110000 are three
   of them, and nothing in the type records which.

2. ONE U+FFFD PER MISTAKE, PER BYTE, OR PER RUN
   bytes        mistakes at      per mistake  per byte  per run   what they are
   c3           0-1                        1         1        1   é cut after 1 of its 2 bytes
   e2 82        0-2                        1         2        1   € cut after 2 of its 3 bytes
   f0 9f 98     0-3                        1         3        1   😀 cut after 3 of its 4 bytes
   ed a0 80     0-1 1-2 2-3                3         3        1   U+D800 in the shape of UTF-8
   f4 90 80 80  0-1 1-2 2-3 3-4            4         4        1   one past U+10FFFF, same shape

   'mistakes at' is what Python's decoder reports: byte offsets, end excluded.
   per mistake  is what Python writes -- counted, not computed.
   per byte     is what Go's `for range` loop writes, and what
                utf8.RuneCountInString counts as that many runes.
   per run      is what Go's strings.ToValidUTF8 writes.
   The last two are computed here from Python's own report; the page puts
   them beside Go itself.

   One decoder, one report, three policies. Per mistake and per byte agree
   whenever every mistake is one byte long, and part only when one is
   longer -- which happens when a character starts correctly and is cut
   short. The first three rows are that one accident at three lengths.
   Per run parts from both whenever mistakes touch, and rows 4 and 5 are
   nothing but touching one-byte mistakes.

3. EVERY INPUT OF ONE OR TWO BYTES
   inputs                                          65,792
   per mistake and per byte agree                  64,576
   they differ                                      1,216
   ...differing, with a mistake over one byte       1,216   every one
   ...agreeing, with a mistake over one byte            0   none

   Which ones? The program was never given the UTF-8 table. It read these
   ranges off the inputs where the two counts parted:
       lead E0     then A0-BF     32
       lead E1-EC  then 80-BF    768
       lead ED     then 80-9F     32
       lead EE-EF  then 80-BF    128
       lead F0     then 90-BF     48
       lead F1-F3  then 80-BF    192
       lead F4     then 80-8F     16
   Every row is the first two bytes of a three- or four-byte character with
   nothing after them. Note where ED and F4 stop: 9F and 8F. ED A0 would
   begin a surrogate and F4 90 a number past U+10FFFF, so the decoder turns
   the pair down at its second byte and reports the lead byte alone -- a
   one-byte mistake, which is why the two counts agree there.
```
<!-- /output -->

Section 2's three count columns come from one report. `per mistake` is simply what Python writes — counted from the decoded string, not computed — and the program asserts that it equals the number of mistakes the handler saw. The other two are arithmetic over the same `(start, end)` pairs, and they match what Go's two functions print in section 3 of the Go program, row for row.

Section 3 is the one to read slowly. The program is never given the UTF-8 table, and it prints a piece of it anyway: the seven rows are exactly the valid first two bytes of every three- and four-byte character in Table 3-7 ([UTF-8 by hand](../../03_Encodings/utf8_by_hand/README.md) walks the whole table), recovered from nothing but the inputs where the two counts disagree. `ED` stopping at `9F` and `F4` at `8F` is the table's own surrogate and ceiling rules showing through.

## In Rust

Rust can declare Go's type in one line, which is the shortest proof that the name was never the guarantee.

<!-- output:rune_is_an_int32_rs -->
*Verified output of [`rune_is_an_int32_rs.rs`](examples/rune_is_an_int32_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A RUNE IN RUST IS ONE LINE, AND IT CHECKS NOTHING
   type Rune = i32;
   TypeId::of::<Rune>() == TypeId::of::<i32>()   true
   TypeId::of::<char>() == TypeId::of::<u32>()   false
   The alias is gone before anything can ask about it: a Rune IS an i32,
   the way Go's rune is an int32. A char is not a name for u32. It is a
   type of its own, and the only way in is a constructor that can say no.

        value    as a Rune   as a char
           -1           -1   refused before char is asked: no u32 is negative
         0x41           65   Some(U+0041)
         0xE9          233   Some(U+00E9)
       0xD800        55296   None
     0x10FFFF      1114111   Some(U+10FFFF)
     0x110000      1114112   None
   All six are Runes, because every i32 is. Three of them are not a char,
   and nothing in a Rune says which three.

   size_of::<Option<Rune>>()   8   <- no value is off limits, so None needs a tag
   size_of::<Option<char>>()   4   <- None is kept in a value no char may hold

2. THE SAME FIVE MISTAKES, HANDED BACK AS SLICES
   bytes        invalid chunks        lossy  per byte   what they are
   c3           [c3]                      1         1   é cut after 1 of its 2 bytes
   e2 82        [e2 82]                   1         2   € cut after 2 of its 3 bytes
   f0 9f 98     [f0 9f 98]                1         3   😀 cut after 3 of its 4 bytes
   ed a0 80     [ed] [a0] [80]            3         3   U+D800 in the shape of UTF-8
   f4 90 80 80  [f4] [90] [80] [80]       4         4   one past U+10FFFF, same shape
   utf8_chunks() walks the original bytes and hands each mistake back as a
   slice of them. from_utf8_lossy writes one U+FFFD per slice, because each
   slice is one maximal subpart -- the same count the Python example gets
   from its own decoder. Add up the slice LENGTHS instead and you have what
   Go's `for range` loop writes. A decoder has to know how long a mistake is
   to carry on after it, so the per-byte count is never lost -- only rounded
   down to one.
```
<!-- /output -->

The two `TypeId` lines are the whole difference between `rune` and `char`. `type Rune = i32` is the same type as `i32`, so there is nothing for a check to attach to; `char` is a different type from `u32`, and the only way in is `char::from_u32`, which can say no. The two sizes are the same fact seen by the compiler: every `i32` is a valid `Rune`, so `Option<Rune>` needs a tag of its own and is 8 bytes, while `Option<char>` keeps its `None` in a value no `char` may hold and stays at 4 — the niche [`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md) explains. Rust is the one checked type measured here that spends the gap that way: Swift's `Unicode.Scalar?` is 5 bytes and .NET's `Rune?` is 8.

Section 2 is a second witness for the rule. [`utf8_chunks()` ↗](https://doc.rust-lang.org/std/primitive.slice.html#method.utf8_chunks), stable since Rust 1.79, walks the original bytes and returns each mistake as a slice of them; `from_utf8_lossy` writes one `U+FFFD` per slice, and adding up the slices' lengths gives Go's count. Two decoders written independently report the same mistakes at the same lengths, so Go's per-byte count is not a different reading of the bytes — only a different way of rounding the same reading.

## What was measured, and where

The three programs above, and the kata's two, are answer keys: CI runs them on Ubuntu and macOS on every push. Before they were recorded, the Python ones were diffed byte for byte on CPython 3.11, 3.12, 3.13 and 3.14, the Rust one on rustc 1.90, 1.94, 1.95, 1.96 and 1.98, and the Go ones on Go 1.18, 1.21, 1.23 and 1.25, and every run was identical. **Everything else on this page was measured by hand, on one machine, and is dated:**

| | version | measured on 2026-09-10 |
|---|---|---|
| machine | macOS 26.6.2, x86-64 | |
| Go | go1.25.5 | `go vet` flags `string(i)` on a plain `int` (exit 1) where `go build` accepts it; and all 16,843,008 inputs of one to three bytes against Python's spans, 0 mismatches. Everything else Go says on this page is in its answer key |
| .NET | 5.0.5 | `Rune.IsValid(0xD800)` is `False`; `new Rune(0xD800)` throws `ArgumentOutOfRangeException`; a `Rune` is 4 bytes and a `Rune?` 8; `Encoding.UTF8.GetString` counts with the majority |
| Swift | 6.3.3 | `Unicode.Scalar(0xD800)` and `Unicode.Scalar(0x110000)` are `nil`; `Unicode.Scalar?` is 5 bytes; `String(decoding:as:)` counts with the majority |
| Java | OpenJDK 25.0.4.1 | `Character.isValidCodePoint(0xD800)` is `true`; `ed a0 80` gives one `U+FFFD`, through `new String` and through a `CharsetDecoder` |
| Perl | v5.42.0 | `Encode::decode('UTF-8', …)` gives one `U+FFFD` on every row |
| Node | v20.20.2 | `TextDecoder` and `Buffer.toString` both count with the majority |
| Ruby | 2.6.10 | `String#scrub` counts with the majority |
| C | Apple clang 21, MacOSX26 SDK | `#include <uchar.h>` fails with *file not found*; `rune_t` is declared as `wchar_t` in `arm/_types.h` and `i386/_types.h` |
| Python | 3.14.7 | the answer keys, and the other side of the 16,843,008-input run |
| rustc | 1.98.0 | the answer key |

## Where the word comes from

**Plan 9.** Rob Pike and Ken Thompson's paper on moving Plan 9 to Unicode — *Hello World or Καλημέρα κόσμε or こんにちは 世界*, USENIX Winter 1993, listed in [Resources](../../RESOURCES.md) — introduces the type and its library. In the text Plan 9's fourth edition publishes, `Rune` is `typedef unsigned long Rune;`, wide enough for 21-bit values, with `runetochar`, `chartorune`, `fullrune`, `utflen` and `utfrune` around it. Unsigned, note: the original held no negative numbers, and Go's does. The word is also older than UTF-8. A note by Russ Cox in the same file as [Pike's history of UTF-8 ↗](https://www.cl.cam.ac.uk/~mgk25/ucs/utf-8-history.txt) records Plan 9's `libc/port/rune.c` being switched from the older UTF to Thompson's new one on 4 September 1992 — so the file, and the word, were there first.

**4.4BSD** borrowed it for its locale machinery. [`mbrune(3)`](../../13_Documentation/the_encoding_man_pages/README.md) on macOS says three of its functions first appeared in Plan 9, as `utfrune`, `utfrrune` and `utfutf`, and that the whole API is deprecated in favour of C99's wide characters. On macOS `rune_t` is declared *as* `wchar_t`: a second name for it, not an ancestor.

**Go** made it the everyday word. Robert Griesemer, Rob Pike and Ken Thompson started the language in September 2007, by [its own FAQ ↗](https://go.dev/doc/faq), and Pike's account of the term is [*Strings, bytes, runes and characters in Go* ↗](https://go.dev/blog/strings) (2013): the name exists so that a program can say when an integer holds a code point, and it means the same thing as *code point*.

**.NET** came last, with `System.Text.Rune` in .NET Core 3.0 — [its documentation ↗](https://learn.microsoft.com/en-us/dotnet/api/system.text.rune) lists no earlier version — and chose the opposite promise: a `Rune` is a validated scalar value. The same page notes that the Unicode Standard does not define the word at all, and that .NET's type is not Go's.

## If you are coming from Python or ABAP

**Python.** There is no rune to port, and the loop maps almost directly: Go's `for _, r := range s` is Python's `for ch in s`, `rune(c)` is `ord(c)` and `string(r)` is `chr(r)`. Two differences are worth more than the similarity. The failures run opposite ways: `chr(0x110000)` raises `ValueError`, while `string(rune(0x110000))` quietly hands back `U+FFFD`. And the lengths: Go's `len(s)` is Python's `len(s.encode())`, and Python's `len(s)` is Go's `utf8.RuneCountInString(s)` — **for valid text only**. On bytes that were cut short they part, by exactly the rule above, and the kata is five fields where they do. `string(65)` being `"A"` where `str(65)` is `"65"` is the mistake `go vet` is there to catch.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* ABAP has no rune either, and no type that holds a code point at all: a position in a `c` field or a `string` is a UTF-16 code unit, so `😀` occupies two of them and there is no ABAP value that is that character as one number ([`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md) has the detail). What transfers is this page's question about camps, and ABAP sits with Go and Python: a string will hold an unpaired surrogate unit as readily as a Go `rune` holds `0xD800`, and whatever checking happens is done by whoever converts it to bytes — `cl_abap_conv_out_ce` or `cl_abap_codepage=>convert_to( )`. So the defensive habit is Python's: validate at that boundary, and find out what the converter does there before relying on it.

## Try it

1. With Go installed, walk a file you suspect was truncated using `utf8.DecodeRuneInString` rather than `range`, and print the offset of every `(RuneError, 1)`. The width is the part `range` hides, and width 1 is the only way to tell a broken byte from a genuine `U+FFFD`, which decodes as `(65533, 3)` — section 4 of the Go program prints both pairs.
2. Search a Go codebase you own for `== utf8.RuneError` with no width check beside it. Each one treats a real `U+FFFD` in the input as a decoding failure — [the in-band problem](../../12_Adversarial/in_band_signals/README.md), one character wide.
3. Find a length limit in your own systems that one language enforces and another stores — a form field, an API gateway, a database column. Write down what each side counts and what each does with a broken byte. If either answer is "I don't know", run the kata's five fields through both.
4. Point the Python example's error handler at a real bad file and compare the number of mistakes with the sum of `end - start`. The first is what Python writes, the second is what a Go service reading the same bytes would count, and the gap tells you how many of that file's mistakes are truncations.

## Practice

**Five fields, cut to fit.** A form keeps names in a fixed-width byte field and cuts whatever does not fit. Five values come back: `63 61 66 c3`, `35 20 e2 82`, `68 69 20 f0 9f 98`, `c5 bc c3 b3 c5` and `e6 97 a5 e6 9c` — which were `café`, `5 €`, `hi 😀`, `żółw` and `日本` before the cut. For each, write down how many `U+FFFD` Python's `decode('utf-8', 'replace')` produces, the `len()` of the result, and what Go's `utf8.RuneCountInString` returns — before running anything.

Then the question those numbers are for. A Go front end refuses anything over four runes, and a Python back end stores whatever it is given. Which field does the front end refuse that the back end would have called four characters or fewer? And what can you read off the bytes alone that tells you whether the two will agree?

```bash
python3 02_Characters/rune_is_an_int32/examples/rune_is_an_int32_kata_py.py
go run 02_Characters/rune_is_an_int32/examples/rune_is_an_int32_kata_go.go
```

<details markdown="1">
<summary><strong>Answers</strong></summary>

Every row of these two keys is the same on every machine: the first was diffed byte for byte on CPython 3.11 through 3.14 and the second on Go 1.18 through 1.25 before they were recorded. The first computes Go's column from the rule above, the second asks Go itself, and the two agree row for row.

<!-- output:rune_is_an_int32_kata_py -->
*Verified output of [`rune_is_an_int32_kata_py.py`](examples/rune_is_an_int32_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
PART ONE -- FIVE FIELDS
------------------------------------------------------------------------

   the bytes that came back   U+FFFD  len()  Go runes   what it was
   63 61 66 c3                     1      4         4   café, cut inside the é
   35 20 e2 82                     1      3         4   5 €, cut inside the €
   68 69 20 f0 9f 98               1      4         6   hi 😀, cut inside the 😀
   c5 bc c3 b3 c5                  1      3         3   żółw, cut inside the ł
   e6 97 a5 e6 9c                  1      2         3   日本, cut inside the 本

   Every field holds exactly ONE mistake, so Python writes one U+FFFD each
   time and len() counts it as one character. Go counts the same mistake as
   one rune per byte it spans:

      the mistake is 1 byte  long   Go's count is +0   café, cut inside the é
      the mistake is 2 bytes long   Go's count is +1   5 €, cut inside the €
      the mistake is 3 bytes long   Go's count is +2   hi 😀, cut inside the 😀
      the mistake is 1 byte  long   Go's count is +0   żółw, cut inside the ł
      the mistake is 2 bytes long   Go's count is +1   日本, cut inside the 本

   So the two lengths agree on exactly the fields cut ONE byte into a
   character -- café and żółw -- and everywhere else Go's is longer by the
   bytes that were kept, minus one.

PART TWO -- THE FRONT END AND THE BACK END
------------------------------------------------------------------------

   A Go front end refuses anything over 4 runes. A Python back end
   stores whatever it is given, and would call it len() characters long.

   refused by Go, yet 4 characters or fewer to Python:
      6 runes to Go, 4 characters to Python   hi 😀, cut inside the 😀

   1 of the 5 fields. Not an exotic input: many fixed-width fields cut
   a value to their byte width rather than refuse it, and here that leaves
   the two services disagreeing about whether the value is too long.
   Neither has misread a byte -- they found the same mistake and counted it
   by different rules. A limit that crosses a language has to say what it
   counts, and whether it counts before or after the bytes are decoded.

PART THREE -- THE RULE, FROM THE BYTES ALONE
------------------------------------------------------------------------

   Find where the field was cut. If the last character kept only its first
   byte, the mistake is one byte long, and one byte is one marker under any
   policy. If it kept two or more of its bytes, Go counts every one of them
   and Python counts the mistake once: the difference is the bytes kept,
   minus one. The bytes after the cut do not matter -- they are gone.
```
<!-- /output -->

And Go's own count of the same five fields:

<!-- output:rune_is_an_int32_kata_go -->
*Verified output of [`rune_is_an_int32_kata_go.go`](examples/rune_is_an_int32_kata_go.go) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
GO, COUNTING THE SAME FIVE FIELDS ITSELF
------------------------------------------------------------------------

   the bytes that came back    RuneCount  len()   what it was
   63 61 66 c3                         4      4   café, cut inside the é
   35 20 e2 82                         4      4   5 €, cut inside the €
   68 69 20 f0 9f 98                   6      6   hi 😀, cut inside the 😀
   c5 bc c3 b3 c5                      3      5   żółw, cut inside the ł
   e6 97 a5 e6 9c                      3      5   日本, cut inside the 本

   RuneCount is the column the Python key above computed for Go, and it
   matches it row for row. The third count is Go's len(), which is BYTES:
   three different lengths for one field, and not one of them wrong.

   over the 4-rune limit:
      6 runes   hi 😀, cut inside the 😀
```
<!-- /output -->

</details>

## See also

- [`char` is four bytes](../../05_Rust/char_is_four_bytes/README.md) — the checked version of the same idea, and the niche that makes `Option<char>` free
- [Unicode code points](../unicode_code_points/README.md) — what the number is before any type holds it
- [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md) — the maximal-subpart rule, and the eight things Python can do at a bad byte
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — where the UTF-8 check runs, and the C, Python and Rust that agree with each other
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — the 2,048 values a `Rune` refuses and a `rune` does not
- ["Handles Unicode" is four questions](../../10_Best_Practices/what_your_language_gives_you/README.md) — question 4, *can the type system stop you?*, asked of whole languages
- [The encoding man pages nobody opens](../../13_Documentation/the_encoding_man_pages/README.md) — `mbrune(3)`, the BSD branch of the word
- [Meet the `char` ↗](https://masiarek.github.io/rust-learning-library/14_Strings/meet_the_char/index.html) — the sibling library's tour of Rust's checked type
