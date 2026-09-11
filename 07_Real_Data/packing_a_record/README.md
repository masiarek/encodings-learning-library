# Packing a record

**Level:** 201 → 301 · for anyone reading or writing a binary interface

**One line:** A binary record carries no description of itself, so the layout — each field's width, the byte order, and where the padding went — has to be written down somewhere, and the four languages here keep it in four different places: a format string, a method name, a struct declaration, or nowhere at all.

## Fourteen bytes that do not say what they are

An order line: `id` 4711, `qty` −3, `price` 19.50. Written as text that is `4711,-3,19.50` and every consumer on earth can read it, because the commas are in the file and the digits describe themselves. Written as a binary record it is fourteen bytes:

```text
00 00 12 67 ff fd 40 33 80 00 00 00 00 00
```

Nothing in those bytes says there are three fields. Nothing says the first is four bytes wide, or unsigned, or that the last eight are an IEEE 754 double rather than eight characters. Nothing says which end of each number comes first. A reader that guesses any of it differently gets numbers — not an error, not a crash, just different numbers, which is the failure this page is about.

So the layout is an agreement, and it lives outside the data. Three decisions have to be in it:

- **Width.** How many bytes is `qty`? Two, here — but `int` in C is a different width on different targets, and "integer" in a specification is not a width.
- **Byte order.** Does the most significant byte of `id` come first (**big-endian**, and what every network protocol means by *network order*) or last (**little-endian**, and what x86 and ARM do in memory)? [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) is where that question comes into existence, and [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) is what text does about it. A single byte has no order; the moment a field is two bytes wide, somebody has decided.
- **Padding.** Does `price` start at byte 6, right after `qty` — or at byte 8, because this machine wants a `double` to begin at an address divisible by eight? **Alignment** is the requirement; **padding** is the dead bytes inserted to satisfy it. In a struct that is the compiler's business. In a file it is yours, and if the two disagree the file is the wrong length.

This page was prompted by [`perlpacktut` ↗](https://perldoc.perl.org/perlpacktut), Perl's tutorial for `pack` and `unpack`. Perl's answer is a template string — `pack "N n d>", $id, $qty, $price` — and Python's `struct` is close enough to it to be a deliberate family resemblance; the two write the same file, which is worth checking rather than assuming:

```text title="Measured 2026-09-08 — perl 5.42.0 and CPython 3.14.7 on macOS 26.6. Not machine-checked: Perl is not in this library's CI, and one page is not a reason to add it."
perl    pack "N n d>",   4711, -3, 19.5        00001267fffd4033800000000000
python  struct.pack('>Ihd',   4711, -3, 19.5)  00001267fffd4033800000000000

perl    pack "N n a10",  4711, -3, $name       00001267fffd5a61c5bcc3b3c582c487
python  struct.pack('>Ih10s', 4711, -3, raw)   00001267fffd5a61c5bcc3b3c582c487

and the modifier that is not decoration:
perl    pack "N n d",    4711, -3, 19.5        00001267fffd0000000000803340
                                                           ^^^^^^^^^^^^^^^^  this machine's order, in a record whose first six bytes are not
```

Two Perl details that do not survive a skim, and both are the same trap this page is about. The `>` on that `d` is **load-bearing**: `N` and `n` name a byte order, but `d` on its own is native, so `pack "N n d"` writes a record whose first six bytes are big-endian and whose last eight are the machine's — and it round-trips perfectly against itself. And Perl's `a` is the NUL-padded string, matching Python's `s` — `pack "a10", "Zaz"` is `5a 61 7a 00 00 …`, while `A10` pads with spaces, `5a 61 7a 20 20 …`. One letter, a different file, and both look identical in a terminal.

The interesting part is not the resemblance. It is that the same problem has four genuinely different answers, and each language forces the decision at a different moment.

## Where each language keeps the layout

| | The layout lives in | You are forced to name the byte order | A wrong width is caught |
|---|---|---|---|
| **Perl** | a template string — `pack "N n d>"` | in the letter, but only for 16- and 32-bit integers (`n`/`N` big, `v`/`V` little); `s`, `l`, `q` and `d` are **native** unless you add a `<` or `>` modifier | not at all |
| **Python** | a format string — `struct.pack('>Ihd', …)` | in the prefix character, **which is optional** | at unpack time, on the total length |
| **Rust** | the method name — `id.to_be_bytes()` | yes; there is no unsuffixed spelling | **at compile time** |
| **C** | the struct declaration, which is about memory | no; the CPU decides unless you write shifts | not at all |
| **ABAP** | the `TYPE` of the field, which fixes the width | no; the application server decides, unless the file is opened `IN LEGACY BINARY MODE` with `BIG ENDIAN` or `LITTLE ENDIAN` | at `TRANSFER` / `MOVE`, by truncation |

The row that costs the most money is Python's, because the trap is a **default**. `'>Ihd'` and `'<Ihd'` are portable and mean what they say. `'Ihd'` — the same string with the prefix left off — is not a shorter spelling of either. It is a fourth format meaning *native order, native sizes, native alignment*: whatever the C compiler that built this Python decided, including padding bytes you did not ask for. It runs, it round-trips on your machine, and it writes a different file on somebody else's.

## In Python

The whole layout is one string, which is what makes `struct` the shortest statement of this idea in any language here — and what makes the missing character so easy to miss.

<!-- output:packing_a_record_py -->
*Verified output of [`packing_a_record_py.py`](examples/packing_a_record_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. A RECORD IS SOME VALUES AND A LAYOUT NOBODY SENT WITH THEM
------------------------------------------------------------------------

   id    = 4711     unsigned, 4 bytes   'I'
   qty   = -3       signed,   2 bytes   'h'
   price = 19.5     float,    8 bytes   'd'

   struct.pack('>Ihd', ...)     00 00 12 67 ff fd 40 33 80 00 00 00 00 00       14 bytes

   Field by field, at the offsets the format string fixes:
     0..4    00 00 12 67              id
     4..6    ff fd                    qty, two's complement
     6..14   40 33 80 00 00 00 00 00  price, IEEE 754 binary64

   Nothing in those fourteen bytes says any of that. No header, no
   field name, no length, no separator. The layout is an agreement
   held somewhere else -- in a specification, in a comment, or, most
   often, in the format string of whichever program wrote the file.

2. THE BYTE ORDER IS THE FIRST CHARACTER OF THE STRING
------------------------------------------------------------------------

   struct.pack('<Ihd', ...)     67 12 00 00 fd ff 00 00 00 00 00 80 33 40       little-endian
   struct.pack('>Ihd', ...)     00 00 12 67 ff fd 40 33 80 00 00 00 00 00       big-endian
   struct.pack('!Ihd', ...)     00 00 12 67 ff fd 40 33 80 00 00 00 00 00       network order -- the same bytes as '>'

   '!Ihd' and '>Ihd' agree, byte for byte: True

   Same three values, same three widths, two different files. Which
   one is correct is not a property of the data and cannot be worked
   out from it. It is a property of whoever you are sending it to.

3. AND THE PREFIX YOU DID NOT WRITE IS NOT 'NO PREFIX'
------------------------------------------------------------------------

   struct.calcsize('<Ihd')     14    4 + 2 + 8, and 14 on every machine
   struct.calcsize('>Ihd')     14    the order changes no width
   struct.calcsize('!Ihd')     14
   struct.calcsize('=Ihd')     14    native ORDER, standard sizes
   struct.calcsize('Ihd')      -- deliberately not printed: with no
                                  prefix the sizes and the padding are
                                  your C compiler's, so the number is a
                                  fact about this machine, not 'Ihd'

   Is the unprefixed format the same length as '<Ihd'?   False

   That False is the whole section. 'Ihd' is not a shorter spelling of
   '<Ihd' or of '>Ihd' -- it is a fourth format, and the bytes it adds
   are ALIGNMENT PADDING: dead bytes the compiler inserts so each
   field begins at an address its type is willing to start at.

   Padding is not the enemy. Invisible padding is. In standard mode you
   can write it down, and then it sits in the string somebody reviews:

   struct.pack('<Ihd', ...)     67 12 00 00 fd ff 00 00 00 00 00 80 33 40       14 bytes, no padding
   struct.pack('<Ihxxd', ...)   67 12 00 00 fd ff 00 00 00 00 00 00 00 80 33 40 16 bytes, two 'x' pads

   'x' is a pad byte you asked for: it writes a zero, unpacks to
   nothing, and is visible in the format. The padding inside 'Ihd'
   does the same job and is visible nowhere.

4. THE WRONG ORDER IS SILENT; ONLY THE WRONG LENGTH IS LOUD
------------------------------------------------------------------------

   written big-endian, read big-endian      (4711, -3, 19.5)
   written big-endian, read little-endian   (1729232896, -513, 4.151005e-317)

   No exception, no warning, nothing in the data to check against.
   4711 read backwards is a perfectly good unsigned integer and 19.5
   read backwards is a perfectly good float, so every field survives
   and every field is wrong. That is the failure this page exists for.

   The one mistake that does raise is a length mismatch, because a
   format string knows exactly how many bytes it wants:
     unpack('<Ihxxd', <14 bytes>)   struct.error   -- a 16-byte format cannot read 14 bytes

   Worth reading twice: the check that fires is on the TOTAL LENGTH,
   never on the meaning. A record of the right length in the wrong
   order passes every check `struct` has.

5. THE NAME FIELD, WHERE THIS BECOMES A QUESTION ABOUT TEXT
------------------------------------------------------------------------

   name               'Zażółć'
     len(name)         6   characters
     len(encoded)      10  bytes in UTF-8   5a 61 c5 bc c3 b3 c5 82 c4 87

   struct.pack('<10s', name)       struct.error

   Two things in that one line. 's' does not pack a string -- it packs
   BYTES, and it will not encode for you, which is the right refusal:
   it does not know which encoding the other end agreed to. And the
   class is struct.error rather than TypeError, so a program guarding
   its packs with `except TypeError` catches none of this.

   The encode step is yours:

   struct.pack('<10s', raw)     5a 61 c5 bc c3 b3 c5 82 c4 87                   10 bytes, exactly full

   Six characters into a ten-byte field, filled to the byte. That is a
   coincidence of this word rather than a rule: 'Zażółć' is two ASCII
   letters and four Polish ones, and each of the four costs two bytes.
   The same field holds ten letters of an English name and five of a
   Polish one. A field width is a BYTE budget.

6. A BYTE BUDGET THAT 's' WILL QUIETLY SPEND FOR YOU
------------------------------------------------------------------------

   struct.pack('<9s', raw)      5a 61 c5 bc c3 b3 c5 82 c4                      9 bytes -- one short

   No exception. 's' truncates on the right and says nothing, because
   as far as `struct` is concerned it was handed bytes and asked for
   nine of them. Ask what those nine bytes are:

     nine.decode('utf-8')            builtins.UnicodeDecodeError
     nine.decode('utf-8', 'replace')  'Zażół�'

   The cut landed between the two bytes that spell 'ć', so the field
   is not text any more. It is nine bytes of which the last is a lead
   byte with nothing behind it -- valid UTF-8 up to position 8 and
   then a promise the file does not keep.

   In a BINARY record the answer is not to truncate more carefully.
   It is to refuse, before the pack, where you still know whose name
   it was:

     Adam     4 chars   4 bytes   fits a 10-byte field: True
     Zażółć   6 chars  10 bytes   fits a 10-byte field: True
     Zażółći  7 chars  11 bytes   fits a 10-byte field: False

   Check the encoded length before you pack and raise at the boundary
   the data entered, rather than shipping a field that is half a
   character. Backing up to a character boundary is the right answer
   for a fixed-width TEXT record, and that is a different lesson.

7. THE ROUND TRIP, ONCE ALL FOUR DECISIONS ARE WRITTEN DOWN
------------------------------------------------------------------------

   struct.pack('>Ih10s', ...)   00 00 12 67 ff fd 5a 61 c5 bc c3 b3 c5 82 c4 87 16 bytes
   unpacked           id=4711  qty=-3  name=b'Za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87'
     name.decode()    'Zażółć'

   round trips: True

   Four decisions, all of them in that one string and the call around it:
     >      byte order, named rather than inherited from the hardware
     I h    widths, fixed by the standard rather than by the compiler
     10s    a byte budget, checked by you before the pack
     utf-8  an encoding, applied by you because 's' will not guess

   A record whose writer and reader agree on all four is portable.
   A record missing any one of them works on the machine that wrote it.
```
<!-- /output -->

## In Rust

No format string, no prefix, no default: the byte order is part of the method name and there is exactly one call per field. The trade is more typing for one fewer thing to leave off — and the second half of the contrast is what Rust refuses to let you do at all, which is treat a struct's memory layout as a file format.

<!-- output:packing_a_record_rs -->
*Verified output of [`packing_a_record_rs.rs`](examples/packing_a_record_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE METHOD CALL PER FIELD, AND THE ORDER IS IN THE NAME
------------------------------------------------------------------------
   order.id.to_be_bytes()      00 00 12 67                u32 -> 4 bytes
   order.qty.to_be_bytes()     ff fd                      i16 -> 2 bytes
   order.price.to_be_bytes()   40 33 80 00 00 00 00 00    f64 -> 8 bytes

   the three concatenated         00 00 12 67 ff fd 40 33 80 00 00 00 00 00          14 bytes

   Those are the same fourteen bytes Python's struct.pack('>Ihd')
   produces, which is the point: two languages, no shared code,
   one agreed layout written down in two different places.

   There is no `to_bytes` without a suffix. `to_ne_bytes` exists
   and is spelled out loud -- NATIVE endian -- so a program that
   reaches for it has said so. The mistake Python's unprefixed
   'Ihd' makes available by DEFAULT is, in Rust, six characters
   you have to type on purpose.

2. THE STRUCT IN MEMORY IS NOT THE RECORD ON THE WIRE
------------------------------------------------------------------------
   size_of::<Order>()   -- not printed: the default layout is
   size_of::<OrderC>()     UNSPECIFIED and repr(C)'s padding is
                           the ABI's, so both are facts about
                           this machine rather than about the
                           record. What is a fact about the
                           record is the line below.

   wire.len() == 4 + 2 + 8              true
   wire.len() == size_of::<Order>()     false
   wire.len() == size_of::<OrderC>()    false

   The two size_of lines are false, and for two different
   reasons. repr(C) is larger than the sum of its fields because
   the ABI pads an f64 up to its alignment -- eight bytes on
   every 64-bit target in common use, and a number that belongs
   to the target rather than to the language. The default
   layout is whatever the compiler liked -- it may reorder the
   fields, and the language promises nothing about the result
   between two builds.

   So the C habit the C section of this page is about -- point
   at the struct, write sizeof bytes, hope -- has no Rust
   spelling. You cannot get the bytes of a struct without unsafe
   code and an attribute, which is the language declining to let
   a memory layout become a file format by accident.

3. READING BACK: THE WIDTH IS CHECKED, THE MEANING IS NOT
------------------------------------------------------------------------
   read with from_be_bytes    id=4711  qty=-3  price=19.5
   read with from_le_bytes    id=1729232896

   Same four bytes, two methods, two integers, no error. Rust
   makes the byte order impossible to LEAVE OUT and no harder to
   get wrong; nothing in those four bytes says which end goes
   first, in any language.

   What the type system does catch is the width. `from_be_bytes`
   takes [u8; 4] and not a slice, so a four-byte field read with
   two bytes is a compile error -- see the page. From a slice the
   same check happens at run time, and it is an error you can
   handle rather than a truncation you cannot see:

     <[u8; 4]>::try_from(&wire[0..2])   is_err: true
     <[u8; 4]>::try_from(&wire[0..4])   is_err: false

4. AND THE NAME FIELD, WHICH RUST HAS ALREADY DECIDED FOR YOU
------------------------------------------------------------------------
   let name = "Zażółć";
     name.chars().count()   6   characters
     name.len()             10  bytes -- len() on a str is BYTES
     name.as_bytes()        5a 61 c5 bc c3 b3 c5 82 c4 87

   `as_bytes` costs nothing and takes no encoding argument,
   because a Rust `str` is UTF-8 by definition -- the decision
   Python's struct.pack('10s', ...) refuses to make for you was
   made when the string was constructed. That removes one of the
   four decisions and none of the other three.

   The byte budget is still yours, and the cut is still a cut:

     Adam     4 chars   4 bytes   fits a 10-byte field: true
     Zażółć   6 chars  10 bytes   fits a 10-byte field: true
     Zażółći  7 chars  11 bytes   fits a 10-byte field: false

   And where Python hands you nine bytes and finds out later,
   Rust will not build a `str` out of a cut sequence at all:

     &name.as_bytes()[..9]           5a 61 c5 bc c3 b3 c5 82 c4
     str::from_utf8(that)  is_err:   true
     name.is_char_boundary(9)        false
     name.is_char_boundary(8)        true

   `is_char_boundary` is the question a byte budget actually
   asks, and it is on `str` in std rather than in a crate. Byte 9
   is inside the two bytes that spell the last letter; byte 8 is
   between characters. Slicing a `str` at 9 panics rather than
   returning half a character -- loud where Python's '9s' is
   silent.

5. THE WHOLE RECORD, WITH THE NAME IN IT
------------------------------------------------------------------------
   id + qty + 10-byte name        00 00 12 67 ff fd 5a 61 c5 bc c3 b3 c5 82 c4 87    16 bytes

   read back      id=4711  qty=-3  name="Zażółć"
   round trips:   true

   The `assert!` above is the whole difference from section 6 of
   the Python run. Nothing in the language forces it -- a fixed
   array and a `copy_from_slice` panic on an over-long name
   rather than truncating, which is better than silence and
   worse than a checked error at the edge of the system. The
   width of a field is the one part of a binary layout that no
   type can hold.
```
<!-- /output -->

**The compile error the program above only describes.** `from_be_bytes` takes `[u8; 4]` rather than a slice, so reading a four-byte field with two bytes does not run and fail — it does not build:

```text title="Measured 2026-09-08 — rustc 1.98.0, identical on macOS and Ubuntu. Not machine-checked: an example that ran this could not compile."
error[E0308]: mismatched types
 --> bad.rs:3:33
  |
3 |     let id = u32::from_be_bytes([wire[0], wire[1]]);
  |              ------------------ ^^^^^^^^^^^^^^^^^^ expected an array with a size of 4, found one with a size of 2
```

That is the strongest guarantee on the page, and it is worth being precise about how narrow it is: it catches the **width**, never the **meaning**. `from_le_bytes` where the format says big-endian compiles perfectly and returns a number.

## In C

C is where the other three get their vocabulary — Python's `I`, `h` and `d` are C's types, and the padding Python's native mode inserts is C's padding. It is also the only one of the four with no serialiser at all, which is why the shortcut is so tempting and so wrong.

<!-- output:packing_a_record_c -->
*Verified output of [`packing_a_record_c.c`](examples/packing_a_record_c.c) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE STRUCT IS A MEMORY LAYOUT, AND IT HAS HOLES IN IT
------------------------------------------------------------------------

   struct order { uint32_t id; int16_t qty; double price; };

   sizeof(struct order)            -- not printed: it is this
   offsetof(struct order, price)      compiler and this ABI, not
                                      the record. The comparisons
                                      below are the portable part.

   4 + 2 + 8, the fields alone              14
   sizeof(struct order) == that sum         false
   sizeof(struct order) >  that sum         true
   offsetof(price) == 6, where a file wants it   false

   The struct is bigger than its fields and the third field does
   not start where the wire wants it. The difference is ALIGNMENT
   PADDING: a double has to begin at an address divisible by its
   ALIGNMENT, so the compiler inserts unnamed bytes after `qty`
   until it does. You cannot see them, you did not ask for them,
   and their contents are indeterminate.

   That alignment is the ABI's number rather than the standard's,
   and _Alignof is how you ask this machine instead of guessing.
   It is not printed here for the usual reason -- but the page
   carries it measured on four targets, including one where a
   double aligns to four rather than eight.

   This is exactly what Python's unprefixed 'Ihd' inherits -- the
   `struct` module's native mode asks the C compiler these same
   two questions and answers with the same padding.

2. SO THE ONE-LINE WRITE IS THE BUG
------------------------------------------------------------------------

   fwrite(&r, sizeof r, 1, fp);

   That compiles, runs, and writes a file that reads back
   perfectly -- with the same program, on the same machine, built
   by the same compiler. It writes:

     * this CPU's byte order, chosen for you by the hardware
     * this ABI's padding, in bytes whose values C does not define
     * this compiler's field order and widths

   None of the three is in the file, so a reader cannot check any
   of them. Padding is the one worth pausing on: those bytes are
   INDETERMINATE, so two records with identical fields can differ
   byte for byte, which breaks memcmp, hashing and any signature
   taken over the struct -- and it is why they are not printed
   here. There is nothing stable to print.

3. THE PORTABLE ANSWER IS TO WRITE THE BYTES YOURSELF
------------------------------------------------------------------------

   shift and mask, field by field  00 00 12 67 ff fd 40 33 80 00 00 00 00 00          14 bytes

     0..4   id     >> 24, >> 16, >> 8, & 0xff
     4..6   qty    cast to uint16_t first, then shift
     6..14  price  memcpy, then reversed if this CPU is little

   Fourteen bytes, no padding, byte order stated in the code. The
   same fourteen bytes Python's struct.pack('>Ihd') and Rust's
   three to_be_bytes calls produce, which is what "agreeing on a
   format" looks like when nobody shares a library.

   Two details the shifts are carrying quietly. `qty` is cast to
   uint16_t before shifting, because shifting a negative signed
   value right is implementation-defined and the cast is the only
   way to say "the two's complement bits, please". And `price`
   needs a memcpy because C has no shift operator for a double --
   which means the float field is the one place where you have to
   ask what this machine does before you can write a portable file.

4. READING IT BACK, AND WHERE C WILL NOT HELP YOU
------------------------------------------------------------------------

   get_u32_be(wire)            id = 4711
   round trips                 true

   And the mistake with no diagnostic anywhere in this file:

     the same four bytes read the other way round   1729232896

   Both are valid uint32_t values, so there is no error to report
   and nothing to test against. C has no type that means "a
   big-endian 32-bit field" -- Rust's from_be_bytes and Python's
   '>' both name the order in the call, and C names it only in
   whichever helper you remembered to write.

   The name field is worse again, and this page's other half:
   `char buf[10]` is ten bytes and C has no opinion at all about
   what encoding they hold, so nothing here can tell you that a
   strncpy landed in the middle of a UTF-8 sequence. There is no
   equivalent of Rust's str::from_utf8 refusing, or of Python's
   decode raising. The bytes just go out.
```
<!-- /output -->

## The measurements that are not in any answer key

Every number above that belongs to a machine rather than to a format is printed as a comparison, because a recorded key must not depend on who ran it — the same rule that keeps `to_ne_bytes` off the [byte order](../../03_Encodings/byte_order_and_bom/README.md) page. Here are the actual values, which are a fact about the ABI and not about your code:

```text title="Measured 2026-09-08 — macOS 26.6 x86_64 (clang, CPython 3.14.7), Linux x86_64 and Linux aarch64 (gcc 14, CPython 3.13.15), and 32-bit x86 Debian 12 (gcc). Not machine-checked."
                                  64-bit    x86 32-bit
struct.calcsize('<Ihd')             14         14       fixed by the documentation
struct.calcsize('Ihd')              16          -       4 + 2 + [2 pad] + 8
sizeof(struct order)                16         16       {u32, i16, f64}
offsetof(struct order, price)        8          8       the wire wants it at 6
_Alignof(double)                     8          4       <- the rule differs
sizeof(struct two)                  16         12       {u32, f64}
```

The last two rows are the ones worth the trip, and they are why this is a fence rather than an answer key. `_Alignof(double)` is **not** 8 everywhere: 32-bit x86 Linux aligns a `double` to 4, so the rule that produces the padding genuinely differs between targets. And then the trap inside the trap — **this page's own struct is 16 bytes on both of them anyway.** `qty` ends at byte 6, and 8 is the next multiple of 4 as well as of 8, so two different rules happen to insert the same two bytes. Reach for a simpler struct and they part company: `{uint32_t, double}` is 16 bytes on a 64-bit target and **12** on 32-bit x86.

That is the finding, and it was one `docker run` away from being an assumption: a struct agreeing across two ABIs is not evidence that the ABIs agree. It is also why [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) can record `struct.calcsize('HI')` as `8` in an answer key and be right to — the number is stable across every machine this library runs on. Stable is not the same as promised, and the distinction is exactly the one `'<HI'` writes down and `'HI'` does not. The number `16` is not *wrong* anywhere here — it is *local* everywhere, and it coincides often enough to be believed. Change the field order to `id`, `price`, `qty` and the padding moves to the end; change `double` to `float` and it disappears. None of that is visible in `'Ihd'`, and all of it is visible in `'<Ihxxd'`.

## Where the character encoding comes in

Everything above is about numbers, and a record with only numbers in it is a data-structures problem. The moment one field holds a name it becomes an encodings problem, and `struct` marks the transition precisely: the `s` format packs **bytes**. It will not encode a `str`, and it is right not to — it does not know which encoding the other end agreed to. So a fourth decision joins the three above, and it is the one no format string can hold.

`Zażółć` is six characters and ten bytes, which fills a ten-byte field exactly. That is arithmetic about this word, not a rule: two ASCII letters at one byte each and four Polish ones at two. The same field holds ten letters of an English name and five of a Polish one, because **a field width is a byte budget**. Cut it at nine and the cut lands inside the two bytes that spell `ć`, and what comes out is not text any more — nine bytes that are valid UTF-8 up to position 8 and then a lead byte with nothing behind it.

Three languages, three moments of finding out:

- **Python** finds out last. `struct.pack('<9s', raw)` truncates in silence and the `UnicodeDecodeError` arrives in whatever reads the file, possibly on another system, possibly next quarter.
- **Rust** will not build a `str` out of the cut bytes at all — `str::from_utf8` refuses, and `is_char_boundary` is the question in std rather than in a crate. Slicing at byte 9 panics rather than returning half a character.
- **C** never finds out. `char buf[10]` is ten bytes with no opinion about what they hold, and `strncpy` will cut a sequence in half without a diagnostic anywhere.

In a *binary* record the answer is not to truncate more carefully — it is to check the encoded length before the pack and refuse at the edge of the system, where you still know whose name it was.

**And this page stops there, deliberately.** Truncating a text field *correctly* — backing up to a character boundary, and what to pad the remainder with, which in a two-byte encoding is its own trap — is [Fixed-width byte fields](../fixed_width_byte_fields/README.md). The two pages share one sentence, *a field is N bytes and `ż` is two of them*, and split on what to do about it, because the file is different. There, the field is a **column** in a text record that somebody else's program reads at a fixed offset, so refusing is not on the table and the whole subject is what to do with the half character. Here, the record was never text, and the honest answer is to refuse before writing anything.

## If you are coming from Python or ABAP

**Python.** The habit that transfers is `int.to_bytes` / `int.from_bytes`, where the byte order argument has no default and you have already been made to name it; `struct` is that decision moved into a string, and the string is where it can be left out. Read the prefix first, every time, in your code and in anyone else's: no prefix means native sizes *and* native alignment, `=` means native order with standard sizes, and only `<`, `>` and `!` are portable. `!` and `>` are the same thing spelled two ways, and `!` is worth preferring in network code because it says *why*. Three more that bite: `s` takes `bytes` and raises `struct.error` rather than `TypeError`, so `except TypeError` around a pack catches nothing; `p` is a Pascal string — `pack('<10p', b'Zaz')` is `03 5a 61 7a 00 …`, the length in the first byte — and one keystroke from `s`, which is `5a 61 7a 00 …`; and `struct.unpack` requires the buffer to be exactly the format's length, which makes it a poor reader for a stream — use `struct.unpack_from` with an offset, or `calcsize` to slice, rather than growing a buffer until it happens to fit. For a format built once and used in a loop, `struct.Struct('>Ih10s')` compiles it once.

**ABAP.** The width lives in the `TYPE`, not in a call, which is the biggest single difference from everything above: `TYPES: BEGIN OF ty_order, id TYPE int4, qty TYPE int2, name TYPE c LENGTH 10, END OF ty_order` is a layout statement, and there is no format string anywhere. What that buys you is that a width cannot be left out. What it costs is that the *byte order* has nowhere to be written in the declaration, because it is not a property of an ABAP type at all — it is settled at the file boundary and on the conversion objects (`cl_abap_conv_out_ce=>create( )` and the newer `cl_abap_conv_codepage`). `OPEN DATASET … IN BINARY MODE` [passes the bytes through unchanged ↗](https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abapopen_dataset_mode.htm), so the file gets the application server's own order, and the statement takes a byte order only in its legacy form: `IN LEGACY BINARY MODE` with [`BIG ENDIAN` or `LITTLE ENDIAN` ↗](https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abapopen_dataset_endian.htm) converts the numeric fields on the way through. Reading a field back, the language picks for you: an assignment from an `x` slice to an `int4` is always big-endian, whatever the server, so on a little-endian one a record written in binary mode and parsed back through an `xstring` gets its integers back byte-reversed — [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md#if-you-are-coming-from-python-or-abap) has the rule. Verify the parameter names and any code-page numbers against your own system; what transfers is the shape, and it is the same finding as the C section above — **a structure declaration is not a wire format**, no matter how carefully it is written. Two more things worth holding on to. First, `c LENGTH 10` is ten *characters* and therefore always exactly twenty bytes internally, because [the language is UCS-2](../../09_History/why_utf16_stayed/README.md) — so the conversion to a byte-counted file format is where the width changes, and `cl_abap_codepage=>convert_to( )` returning an `xstring` is where you can measure it. Second, an ABAP structure is not a wire record either: a `DATA` structure of `c` and `n` fields concatenates without padding, but one mixing `int4` and `c` is subject to the same alignment rules as C, and a `TRANSFER` of the whole structure in binary mode writes the internal image — the ABAP spelling of `fwrite(&r, sizeof r, 1, fp)`, with the same three unwritten assumptions in it. Check the type widths against your own system rather than against a document. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 07_Real_Data/packing_a_record/examples
python3 packing_a_record_py.py
rustc --edition 2024 packing_a_record_rs.rs -o /tmp/pack && /tmp/pack
cc -std=c11 -Wall -Wextra packing_a_record_c.c -o /tmp/pack_c && /tmp/pack_c
```

1. Run `python3 -c "import struct; print(struct.calcsize('Ihd'), struct.calcsize('<Ihd'))"` on your machine and on any other one you can reach — a server, a container, a Raspberry Pi. Then find the format string in your own code that has no prefix.
2. Take a binary file you actually have — a `.png`, a `.class`, a `.zip`, a `.wav` — and read its first sixteen bytes with `xxd`. Find the specification for its header and unpack the first two fields with `struct`. Note which byte order it chose and whether the spec said so in words or only in an example.
3. `grep -rn "struct.pack\|struct.unpack"` over a repository you work on. For each hit, answer one question: portable, native, or nobody knows.
4. Without the machine: an interface has run nightly for three years. It is moved to a new server and every quantity on the report is now a number in the billions. Name the character that is missing from one line of code, and say why nothing raised.
5. Write the same record in Perl (`pack "N n d>"`), Python and Rust, and `cmp` the three files. Then drop the `>` from the Perl template and `cmp` again — the first six bytes still match and the last eight do not, which is the whole page in one command.

## Practice

**Six questions about fourteen bytes, and one of them has no answer.** Write all six down before you run anything.

1. What are `struct.calcsize('>Ih10s')`, `struct.calcsize('<Ihd')` and `struct.calcsize('<Ihxxd')`?
2. What is `struct.pack('>I', 4711).hex()`, and what is `struct.pack('<I', 4711).hex()`?
3. What does `struct.unpack('<I', struct.pack('>I', 4711))[0]` return — and does it raise?
4. Which of `struct.pack('<10s', 'Zażółć')` and `struct.pack('<10s', 'Zażółć'.encode())` fails, and with which exception class?
5. `'Zażółć'` into a nine-byte field: how many bytes come out, and what happens when you decode them?
6. What does `struct.calcsize('Ihd')` return?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:packing_a_record_kata_py -->
*Verified output of [`packing_a_record_kata_py.py`](examples/packing_a_record_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. HOW LONG IS THE RECORD?
------------------------------------------------------------------------

   struct.calcsize('>Ih10s')    16
   struct.calcsize('<Ihd')      14
   struct.calcsize('<Ihxxd')    16

   4 + 2 + 10, 4 + 2 + 8, and the same again with two 'x' pads you
   asked for by name. In standard mode a format string's length is
   arithmetic you can do on paper -- which is the property the
   unprefixed spelling gives away.

2. THE SAME NUMBER, THE TWO ORDERS
------------------------------------------------------------------------

   struct.pack('>I', 4711).hex()   00001267
   struct.pack('<I', 4711).hex()   67120000

   Big-endian puts the most significant byte first, so 4711 -- which
   is 0x1267 -- reads straight off as 00 00 12 67. Little-endian is
   the same four bytes backwards. Two leading zeros either way,
   because the field is four bytes wide and the number is not.

3. AND WHAT THE WRONG READER MAKES OF IT
------------------------------------------------------------------------

   struct.unpack('>I', be)[0]           4711
   struct.unpack('<I', be)[0]     1729232896

   Both are valid unsigned 32-bit integers, so the wrong one raises
   nothing, logs nothing, and looks like an ordinary large id. If you
   predicted 'an error' here, that is the habit this page is aimed at.

4. WHICH OF THE TWO PACKS RAISES, AND WITH WHAT CLASS
------------------------------------------------------------------------

   struct.pack('<10s', 'Zażółć')            struct.error
   struct.pack('<10s', 'Zażółć'.encode())   5a 61 c5 bc c3 b3 c5 82 c4 87

   's' packs bytes and will not encode a str for you. The class is
   struct.error and NOT TypeError, so `except TypeError` around a pack
   catches nothing -- which is the half of this answer most people
   miss even after predicting the raise correctly.

5. TEN BYTES OF NAME INTO A NINE-BYTE FIELD
------------------------------------------------------------------------

   len('Zażółć')             6 characters
   len(encoded)             10 bytes
   struct.pack('<9s', ...)  5a 61 c5 bc c3 b3 c5 82 c4

   nine.decode('utf-8')     UnicodeDecodeError
   with errors='replace'    'Zażół�'

   No exception from the pack: 's' truncates on the right in silence.
   The exception arrives later and somewhere else, in whatever tries
   to read the file -- which is why the check belongs before the pack,
   not after it.

6. AND THE ONE YOU COULD NOT HAVE ANSWERED
------------------------------------------------------------------------

   struct.calcsize('Ihd')  =  ?

   There is no right answer to write down. With no prefix the format
   is NATIVE: the widths and the alignment padding come from the C
   compiler that built this Python, so the number is a property of the
   machine you ran it on and not of the string 'Ihd'.

   What can be checked is the shape, and it is the finding:
     struct.calcsize('Ihd') == struct.calcsize('<Ihd')   False

   If you answered 14 -- the sum of the field widths -- you made
   exactly the assumption the unprefixed format invites, and the
   record you write will be a different length on somebody else's
   machine. Naming the order (`<`, `>` or `!`) fixes the widths and
   removes the padding in the same character.
```
<!-- /output -->

</details>

## See also

- [Fixed-width byte fields](../fixed_width_byte_fields/README.md) — the sibling: the same byte budget in a **text** record, where the field is a column and truncating is the job rather than the bug
- [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) — where the byte-order question comes from, and why a hex field is not a specification
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — what text does about the same problem, and the mark invented to solve it in band
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — the four Python conversions underneath `struct`, and `struct` itself applied to *one number* and a PNG header. Read that page first if you want the Python; this one is what changes when there is more than one field and more than one language
- [A BOM in a CSV](../bom_in_a_csv/README.md) · [CRLF vs LF](../crlf_vs_lf/README.md) — the same interface, damaged in the two ways that do not need a binary format at all
- [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) — the layer outside this one: once the fields are bytes, the **frame** is the record type, the length and the checksum you wrap around them. This page gets the bytes right; that one gets them delivered
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — reading a record you have no specification for
- [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) — for editing one of these records by hand and writing it back
- [Meet the byte ↗](https://masiarek.github.io/rust-learning-library/19_Numbers/meet_the_byte/index.html) — the sibling Rust library on `u8`, `size_of` and the `to_be_bytes` family
- [Calling C ↗](https://masiarek.github.io/rust-learning-library/09_Advanced/calling_c/index.html) — `#[repr(C)]`, and what asking for C's layout rules actually buys
- [`perlpacktut` ↗](https://perldoc.perl.org/perlpacktut) — the Perl tutorial that prompted this page
