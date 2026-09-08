# A record has to say what it is, how long it is, and whether it arrived

**Level:** 201 → 301 · for anyone who has just finished designing a format

**One line:** An encoding turns your values into bytes and stops there; a **frame** is what you wrap around those bytes so that somebody else's program can read them back — and the three fields a hand-rolled format almost always lacks are a **record type**, a **length** and a **checksum**, each of which costs a few lines to write and is close to impossible to add once the format has shipped.

## Where this page sits, and why it is not part of the tribit spec

[Tribit](../tribit/README.md) is the hand-rolled one. It has four layers — a character set, a variable-length encoding on 3-bit units, a container, a viewer — and its container already does more than most first attempts: a two-byte magic number so `file` and `xxd` can recognise it, and a pad count so the last byte's leftover bits are accounted for. It is a good encoding. It is not yet a format, because nothing in a `.t3` file says what kind of thing the next byte begins, how far that thing runs, or whether it arrived the way it was written.

This is a separate page rather than a new section of that specification, and the choice is deliberate: the three fields below are not facts about 3-bit units. They are what you add to *any* format the moment it has to leave your machine, and folding them into the tribit spec would make them read as a detail of tribit rather than as the general thing they are. Tribit's URL does not move, and section 7 of the Python program here wraps tribit's own `café` bytes in the frame, which is the bridge back.

## Three fields, and what each one buys

A **record type** is a small number at a fixed place saying what shape the rest of this record has. It is what lets one file carry several kinds of line — data here, an address there, an end marker at the bottom — and a reader know which it is looking at *before* it parses the payload. A hand-rolled format usually has exactly one line shape, and therefore no way to add a second later without breaking every reader already in the field.

A **length** says how many bytes of payload follow. Its obvious job is bounds-checking, and its real job is this: with a length, the stream is self-delimiting, so the format stops caring what its payload contains. Without one, the only thing holding the file together is a delimiter — and a delimiter is a byte that can occur in data, which is the whole subject of [in-band signalling](../../12_Adversarial/in_band_signals/README.md). The length is also what turns an unknown record type from a dead end into a skip: a reader that meets something it has never heard of can jump exactly that far and carry on.

A **checksum** is arithmetic over the record, stored in the record, so that a reader can tell damage from data. It is about four lines. What it buys is not correctness — it is the difference between a file that is wrong and a file that is *detectably* wrong, which is the difference between a bug report and a silent bad flash.

Notice that none of the three has anything to do with how your values became bytes in the first place. [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) takes *encoding* apart into a character set, a code point assignment, an encoding form and an encoding scheme; a frame sits outside all four, which is why the same frame carries anything. Intel HEX's payload is base16 over arbitrary bytes, and it would carry UTF-16 code units, tribit's packed 3-bit units or a JPEG without one field changing.

None of the three is clever. All three are the parts a format needs to survive contact with a stranger, and all three are cheapest on the day you have not shipped yet.

## Intel HEX, in one paragraph

[Intel HEX ↗](https://en.wikipedia.org/wiki/Intel_HEX) is a format for shipping a memory image to a PROM programmer or a hardware emulator, written down by Intel in 1988 and still what `objcopy -O ihex` and an AVR Arduino build produce today, and it is a useful worked example precisely because nobody would design it this way today. It is unremarkable as a format and disciplined as a frame. Everything below is checked against Intel's own [*Hexadecimal Object File Format Specification*, Revision A, 6 January 1988 ↗](https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/s2012/ads264_mws228/Final%20Report/Final%20Report/Intel%20HEX%20Standard.pdf) rather than against a summary, because the details that matter here — what the checksum covers, and what it does not — are exactly the ones a summary rounds off.

A record is a colon followed by pairs of hex characters:

```text
:  05      0100         00      636166C3A9   64
│  │       │            │       │            │
│  │       │            │       │            └── CHKSUM   1 byte
│  │       │            │       └─────────────── DATA     n bytes  (here 'café' in UTF-8)
│  │       │            └─────────────────────── RECTYP   1 byte   00 = Data
│  │       └──────────────────────────────────── OFFSET   2 bytes  where the loader puts it
│  └──────────────────────────────────────────── RECLEN   1 byte   how many data bytes follow
└─────────────────────────────────────────────── the record mark, an ASCII colon
```

Every field is a count of *bytes*, and every byte is written as two ASCII characters — so `RECLEN` occupies two characters, `OFFSET` four, and the frame around any payload is a constant eleven characters. The maximum `RECLEN` is `FF`, 255. Six record types are defined: `00` data, `01` end of file, `02` and `04` two flavours of extended address, `03` and `05` two flavours of start address. And the whole thing is ASCII-armoured, so a firmware image survives a paper tape, a line printer, a mail gateway, a YAML block and a copy-and-paste — which is the same reason [binary-to-text encodings](../../03_Encodings/binary_to_text/README.md) exist at all, reached from a different direction and before base64 had a name.

The checksum is the part worth copying. It is the two's complement of the sum of the bytes from `RECLEN` through the last data byte — and note what that excludes: the record mark is not in the sum. The specification then states the property that makes a reader's job one line rather than two: add up everything from `RECLEN` through `CHKSUM` and the result is zero. A reader never computes a complement or compares anything; it adds, and checks for nought.

## What the 1988 specification does not say

It never defines a line terminator. Search the document and there is no carriage return, no line feed, no rule about whitespace between records; the word *line* appears once, in the phrase *line printers*, in a sentence about where you might display the file. Every Intel HEX file you will ever see has one record per line, and that convention is entirely the tooling's — the format does not need it, because the mark says where a record starts and `RECLEN` says where it ends. Section 4 of the Python program below parses a three-record file with nothing at all between the records, to show that this is a real property rather than a reading of the prose.

That is the lesson underneath the three fields. **A frame with a length is a frame that does not depend on its delimiter**, and the formats that get into trouble are the ones that left the length out and then discovered their separator inside somebody's data.

## In Python

The whole format is about twenty lines, so the program builds records, corrupts them, and shows what each field is doing when it fails.

<!-- output:framing_a_format_py -->
*Verified output of [`framing_a_format_py.py`](examples/framing_a_format_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE RECORD, FIELD BY FIELD

   payload   b'caf\xc3\xa9'   5 bytes: 63 61 66 c3 a9
   record    :05010000636166C3A964

   field          chars  value        what it is for
   RECORD MARK       1  :            the ASCII colon, 0x3A -- where a record begins
   RECLEN            2  05           5 data bytes follow the type; the maximum is FF
   LOAD OFFSET       4  0100         0x0100 -- where the loader puts the first byte
   RECTYP            2  00           00 = Data; the field that lets one file hold several shapes
   DATA             10  636166C3A9   the payload, one pair of hex digits per byte
   CHKSUM            2  64           two's complement of RECLEN..DATA

   5 bytes of payload arrive as a 21-character record:
   10 characters of payload in hex, 11 characters of frame.
   The frame is a constant -- 11 characters however long the payload is.

   And every character is printable ASCII. The two bytes of the é,
   c3 a9, are not printable ASCII themselves; they travel as the
   four characters 'C3A9'. That is the armour. The frame is the rest.

2. THE CHECKSUM IS FOUR LINES

   byte  field         running sum
   05    RECLEN          5  0x05
   01    LOAD OFFSET     6  0x06
   00    LOAD OFFSET     6  0x06
   00    RECTYP          6  0x06
   63    DATA          105  0x69
   61    DATA          202  0xCA
   66    DATA           48  0x30
   C3    DATA          243  0xF3
   A9    DATA          156  0x9C

   sum over RECLEN..DATA     668  ->  0x9C in eight bits
   two's complement          100  ->  0x64   <- the CHKSUM field

   And the property that makes a reader's job one line: the specification
   says the sum from RECLEN to and including CHKSUM is zero, so a reader
   never has to compute the complement at all -- it adds everything up
   and compares against nothing.
   sum(RECLEN..CHKSUM) & 0xFF = 0

   Note what is NOT in the sum: the record mark. A colon corrupted into
   a semicolon is not a checksum failure -- it is a record the reader
   never finds. A frame's own delimiter is the part it cannot check.

3. ONE CHARACTER CHANGED

   good    :05010000636166C3A964   checksum ok

   Now change one character. Not a byte of payload -- one ASCII digit,
   which is the damage a text channel actually does.

   change                record                 verdict
   3->1 at 10 in DATA    :05010000616166C3A964  checksum FAILED
   A->9 at 17 in DATA    :05010000636166C39964  checksum FAILED
   4->5 at 20 in CHKSUM  :05010000636166C3A965  checksum FAILED
   5->6 at 2 in RECLEN   :06010000636166C3A964  Malformed: RECLEN claims 6 data bytes, 5 present

   Four characters changed, and the last one fails differently. A wrong
   RECLEN never reaches the checksum: the reader is already looking for
   a byte that is not there. A length field is a check too, and it is
   the one that fires first.

   What a failing checksum tells you: this record is wrong. What it does
   not tell you: which character. One 8-bit sum has 256 values and this
   record has 20 characters after the mark, so there is nothing in it
   to locate anything with. Detection, not correction.

4. NO SEPARATOR REQUIRED

   Three records, concatenated with nothing at all between them --
   no newline, no space, no length prefix on the file:

   :020000040001F9:05010000636166C3A964:00000001FF

   record  type  name                       offset  data
        1    04  Extended Linear Address    0x0000  00 01
        2    00  Data                       0x0100  63 61 66 c3 a9
        3    01  End of File                0x0000  (none)

   It parses, and that is the length field's real job. The mark says
   where a record starts and RECLEN says where it ends, so the stream
   is self-delimiting: a newline between records is a courtesy to `cat`
   and to `grep`, not something the format needs.

   The alternative -- a delimiter and no length -- is the arrangement
   that breaks the moment the delimiter occurs in data, which is the
   whole subject of in-band signalling. A length field is how a format
   stops caring what its payload contains.

5. A TYPE THE READER HAS NEVER SEEN

   A file written by a newer tool: same three fields, and one record
   whose type this reader has never heard of.

   :05010000636166C3A964:04000006DEADBEEFBE:02020000C5BC7B:00000001FF

   type 00  Data                     handled   63 61 66 c3 a9
   type 06  unknown to this reader   SKIPPED   4 bytes, checksum verified anyway
   type 00  Data                     handled   c5 bc
   type 01  End of File              handled   (none)

   recovered payload  63 61 66 c3 a9 c5 bc  = 'caféż'
   skipped            1 record it could not interpret and did not need to

   This is what a record type is FOR, and it only works because of the
   length. A type alone tells a reader that it does not understand
   something; a type plus a length tells it exactly how far to jump to
   reach the next thing it does. One field is a diagnosis, two are a
   recovery -- and an old reader that survives a new record is the whole
   of what anybody means by an extensible format.

6. WHAT THE FRAME DOES NOT CATCH

   two bytes swapped        :0200000041427B -> :0200000042417B
                            checksum still ok -- addition does not care about order

   two errors that cancel   :0200000041427B -> :0200000040437B
                            41 42 became 40 43: one down, one up, sum unchanged
                            checksum still ok

   a whole record deleted
      before  :020000040001F9:05010000636166C3A964:00000001FF
      after   :020000040001F9:00000001FF
      every remaining record's checksum: all ok

   Three failures the frame does not see, and they fall into two
   kinds. The first two are inside a record and slip past because an
   8-bit sum is a coarse check: it fails on any single wrong byte and
   on nothing that leaves the total alone. The third is a different
   thing entirely -- the damage is not inside any record, and a
   per-record checksum has no scope to reach it. Nothing about the
   FILE is checked by anything here, and the 1988 specification's six
   record types include no count, no sequence number and no hash.
   Knowing what a check does not cover is the second half of adding one.

7. TRIBIT, FRAMED

   tribit's own container   54 33 05 e1 d8 37 40
      54 33   magic 'T3'    says what the file is
      05      pad count     says how the last byte ends
      e1..    payload       and that is the whole header

   It has a magic number, which Intel HEX does not, and it is missing
   all three of the fields this page is about. Wrap the same bytes:

   :07000000543305E1D837403D:00000001FF

   parsed back  type 00  7 bytes  checksum ok  54 33 05 e1 d8 37 40
   round trip   identical to the tribit bytes

   cost  7 bytes in, 36 characters out
         14 are the payload in hex
         11 are this record's frame
         11 are the end-of-file record, :00000001FF, which is those
         same characters in every Intel HEX file ever written

   That is the trade, and it is worth writing down before choosing it:
   2x for the armour, a fixed 11 characters per record for the frame.
   In exchange, a file that survives a 7-bit channel, that cuts into
   records without a delimiter, that a reader can skip through when it
   meets something new, and that says NO when it has been damaged
   instead of quietly handing back the wrong bytes.
```
<!-- /output -->

## In the terminal

The same seven payload bytes twice — raw, and framed — and what the 2× actually buys, which is four things and not one.

<!-- output:framing_a_format_sh -->
*Verified output of [`framing_a_format_sh.sh`](examples/framing_a_format_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. TWO FILES, ONE PAYLOAD
------------------------------------------------------------------------

   raw bytes        543305e1d83740
   as Intel HEX
       :07000000543305E1D837403D
       :00000001FF

   file(1) says     application/octet-stream
   and              text/plain

   That verdict is the whole point of the armour: the same payload,
   and only one of the two files is something a text tool will open.

2. ONLY ONE OF THEM SURVIVES A 7-BIT CHANNEL
------------------------------------------------------------------------

   payload.t3     is NOT ASCII   exit 1    a 7-bit channel mangles or drops it
   payload.hex    is US-ASCII    exit 0    goes through a 7-bit channel intact

   In 1988 that channel was paper tape and a CRT terminal. Today it is
   a JSON string, a YAML block, a git diff, an email body and a copy
   and paste. The channel changed; the reason for the armour did not.

3. FIXED-WIDTH ASCII MEANS cut IS A RECORD PARSER
------------------------------------------------------------------------

   record marks   2
   RECLEN  (2-3)  07 00 
   OFFSET  (4-7)  0000 0000 
   RECTYP  (8-9)  00 01 
   CHKSUM  (last) 3D FF 

   No parser, no library, no program -- four column ranges. The fields
   are fixed width because they are counts of hex digits, so `cut`,
   `grep` and `sed` read this format as well as anything written for
   it. That is the second thing the armour buys, and it is the reason
   a format nobody would design today is still easy to debug.

   Find the end-of-file record with no tool that knows the format:
       2::00000001FF

4. THE DATA FIELD IS BASE16, SO xxd PUTS IT BACK
------------------------------------------------------------------------

   data field       543305E1D83740
   xxd -r -p        543305e1d83740
   cmp              identical to the original bytes

   Intel HEX has no encoding of its own. The DATA field is plain
   base16 -- the same rewriting `xxd -p` performs -- and everything
   else in the record is the frame. Separating those two is the
   point: an encoding turns values into bytes, a frame turns bytes
   into something a stranger can read back.

5. WHAT IT COST
------------------------------------------------------------------------

   payload bytes                  7
   characters, newlines stripped  36
   file size with newlines        38
   growth                         514%

   Two costs, and only one of them scales. The base16 is 2x forever.
   The frame is a constant 11 characters a record, plus one 11-byte
   end-of-file record per file -- so it dominates a seven-byte payload
   and disappears into a long one:

     7 data bytes ->   25 characters   frame is 44% of the record
    16 data bytes ->   43 characters   frame is 25% of the record
    32 data bytes ->   75 characters   frame is 14% of the record
   255 data bytes ->  521 characters   frame is  2% of the record

   255 is the largest RECLEN the 1988 specification allows. Real
   toolchains emit 16 or 32, which buys a line that fits in an editor
   at a frame cost of a quarter to a seventh.
```
<!-- /output -->

## In Rust

Four sections, each one something Rust makes you write down that the other two languages leave to a convention. The modulo-256 has to be asked for by name; `wrapping_neg` *is* the two's complement rather than an approximation of it; an `Unknown(u8)` arm is forward compatibility expressed as a type; and a `parse` that returns `Result` means there is no state in the program where an unverified record exists.

<!-- output:framing_a_format_rs -->
*Verified output of [`framing_a_format_rs.rs`](examples/framing_a_format_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE WRAP HAS TO BE ASKED FOR

   record        :05010000636166C3A964
   RECLEN..DATA  05 01 00 00 63 61 66 c3 a9

   fold with wrapping_add   156  0x9C
   .wrapping_neg()          100  0x64   <- the CHKSUM field

   The sum passes 255 at byte 6: 202 + 102 = 304.
   u8::checked_add returns None there, and in a debug build the plain
   `+` would have panicked. Python spells the same step `& 0xFF` and C
   does it silently; Rust makes you write the word `wrapping`, which is
   the only one of the three where the modulo is visible in the source.

   And `wrapping_neg` is not an approximation of the two's complement --
   it IS it, which is why the checksum is one expression:
       body.iter().fold(0u8, |a, b| a.wrapping_add(*b)).wrapping_neg()

2. AN ENUM WITH AN ARM FOR WHAT IT DOES NOT KNOW

   :05010000636166C3A964:04000006DEADBEEFBE:02020000C5BC7B:00000001FF

   Data                     at 0x0100  63 61 66 c3 a9
   unknown to this reader   type 0x06, 4 bytes skipped -- the length said how far
   Data                     at 0x0200  c5 bc
   End of File              stop

   recovered  63 61 66 c3 a9 c5 bc  = "caféż"

   `Unknown(u8)` is the whole extensibility story in one arm. Without
   it the enum would be a closed set and `from_byte` would have to
   return an error for a record that is perfectly well formed and
   simply newer than this program.

3. THE REFUSALS ARE NAMED

   one data character changed       BadChecksum { sum: 254 }
   checksum character changed       BadChecksum { sum: 1 }
   RECLEN claims one byte too many  Truncated { claims: 6, present: 5 }
   a G where a hex digit goes       NotHexDigits { at: 11 }
   no record mark at all            NoRecordMark { at: 0 }

   Five wrong records, four named variants -- which is what lets a test
   assert the reason rather than just the failure. And `BadChecksum`
   carries the sum it got, which is not decoration: a correct record
   sums to 0, so the number it hands back is the damage itself, mod 256.
   Row 1 changed 0x63 to 0x61, two less, and the sum came back 254 = -2.
   Row 2 changed 0x64 to 0x65, one more, and the sum came back 1.

4. AN UNVERIFIED RECORD HAS NOWHERE TO LIVE

   derived Debug   Record { kind: Data, offset: 256, data: [99, 97, 102, 195, 169] }
   the same record  kind Data  offset 0x0100  data 63 61 66 c3 a9
   -- Rust's derived Debug prints a Vec<u8> in decimal, which is the
   least useful base for bytes. Say `{:02x}` yourself for anything
   you intend to compare against a dump.

   `parse_one` is the only thing that constructs a Record, and it
   returns Err before it builds one. So there is no state in this
   program where a Record exists and its checksum has not been
   checked -- the question "did anyone verify this?" is answered by
   the type rather than by reading the call sites. That is the same
   move as `String` promising UTF-8, applied to a frame instead of
   to an encoding.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** The checksum is `(-sum(body)) & 0xFF` and the verification is `sum(record) & 0xFF == 0`; the interesting part is the mask. Python's `int` does not wrap, so the modulo-256 is something you write down, which is a nuisance and also a favour — a missing `& 0xFF` is a visible omission rather than an invisible one. Reach for `int.from_bytes` and `int.to_bytes` for the multi-byte fields rather than shifting by hand; they take the byte order as an argument, which is the question you want to be forced to answer. And `bytes.fromhex` accepts either case and rejects an odd number of digits, so it is already most of a validator for the DATA field.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* This shape is more familiar here than anywhere else in this library, because SAP's own interchange formats are built out of exactly these three fields. An IDoc is a stream of segments in which the segment name is the record type and the segment definition supplies the fixed layout, wrapped in a control record that carries the counts — the reason an IDoc from a newer release can still be read is that the receiver dispatches on the segment name and can skip what it does not know. The frame/encoding split is worth keeping in mind at the same boundary: `xstring` holds bytes and `string` holds characters, so anything that has to travel through a character field needs the base16 step first, and that hex conversion is the *armour*, not the format. Two habits transfer directly from the Rust section: name every refusal rather than raising one generic exception, and do the length check before the checksum, because a wrong length is the error that stops you reading the right bytes in the first place. Verify any code-page number against the system rather than against a page.

## Try it

1. Find a `.hex` file on your own machine — an AVR Arduino sketch's build output, anything a toolchain wrote with `objcopy -O ihex`, or make one from any binary you have with `objcopy -I binary -O ihex`. Run `cut -c8-9` on it, then `sort | uniq -c`, and see which of the six record types your toolchain actually emits.
2. Take that same file and check one record by hand: add its bytes from `RECLEN` to `CHKSUM` and confirm you get zero. Then change one character in a data field with an editor and check again.
3. Take a format *you* own — a log line, a CSV your team invented, an export nobody documented — and ask the three questions of it. Can a reader tell which shape a line is before parsing it? Can a reader skip a line it does not understand? Would anyone notice if a byte changed in transit?
4. Find the answer to question 3 for the format you are most confident about, then look for its delimiter inside a real payload. `grep` for your separator in the data column.
5. If you are writing the tribit implementation: add a record type and a length to its container, and see what breaks. Every existing `.t3` file, is the answer — which is the whole argument for adding them before there are any.

## Practice

**Four records, one lie.** Below are four Intel HEX records, and everything you need to read them is addition.

```text
1  :020000040000FA
2  :03001000E282ACDD
3  :02002000C4BC5D
4  :00000001FF
```

Before running anything: **(1)** name each record's type from its `RECTYP` field; **(2)** say how many data bytes record 2 carries, at what offset, and what character those bytes spell; **(3)** exactly one record has a bad checksum — say which, and say what the number the reader gets back tells you about the damage. Then **(4)**, the question with no arithmetic in it: delete record 3 from the file entirely. Which of the remaining records now fails, and what does your answer say about what a per-record checksum is for?

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:framing_a_format_kata_py -->
*Verified output of [`framing_a_format_kata_py.py`](examples/framing_a_format_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE FOUR RECORDS

   1  :020000040000FA
   2  :03001000E282ACDD
   3  :02002000C4BC5D
   4  :00000001FF

1. WHAT EACH ONE IS -- read RECTYP, characters 8 and 9

   #  record              RECLEN  OFFSET   RECTYP  name
   1  :020000040000FA     02      0x0000   04      Extended Linear Address
   2  :03001000E282ACDD   03      0x0010   00      Data
   3  :02002000C4BC5D     02      0x0020   00      Data
   4  :00000001FF         00      0x0000   01      End of File

   Two Data records between an address record and an end-of-file
   record. RECTYP is the third field and it is always in the same two
   columns, which is why `cut -c8-9` reads it straight out of the file.

2. RECORD 2 -- how many bytes, and where

   RECLEN  03    = 3 data bytes
   OFFSET  0010  = 16 decimal, where the loader puts the first one
   DATA    e2 82 ac  = '€' in UTF-8

   RECLEN counts BYTES, not characters of the record -- three data
   bytes are six hex characters. The frame is eleven characters, the
   record mark included, and it does not change with the payload:
   len(record) = 17 = 11 + 6

3. WHICH ONE IS THE LIE

   Add up every byte from RECLEN to CHKSUM. A good record sums to 0.

   #  record              sum mod 256
   1  :020000040000FA       0   ok
   2  :03001000E282ACDD     0   ok
   3  :02002000C4BC5D     255   FAILS -- got 255 = 0xFF
   4  :00000001FF           0   ok

   Record 3 is the lie. The reader gets 255 back, and in eight bits
   255 is -1: the record's content is 1 less than whatever the
   checksum was computed over. The number it hands you IS the damage.

   stored          c4 bc
   +1 on byte 0    c5 bc   = 'ż'

   The character 5 in the file became a 4 -- one bit of one byte, the
   damage a bad cable or a careless edit actually does -- and ż became
   a byte that starts a UTF-8 sequence nothing finishes.

   But the checksum never said WHICH byte. +1 on the other one satisfies
   it exactly as well:
   c4 bd sums to 0 as well -- and it is not the right answer.
   Eight bits of check over the 14 characters after the mark can
   detect, and have nothing left over to locate with.

4. NOW DELETE RECORD 3 -- the question with no arithmetic in it

   the file that is left:
      :020000040000FA
      :03001000E282ACDD
      :00000001FF

   every remaining checksum verifies: True

   Nothing complains. The corrupt record is gone, and so is the only
   thing in the file that objected to it -- what a reader now has is a
   clean file missing two bytes of somebody's data, and it says so
   nowhere. Deleting the damage repaired the file's self-report.

   And it is not one blind spot, it is the whole class. Take the good
   file -- records 1, 2 and 4 -- and damage it four different ways
   without touching a single record's own bytes:

   the original, undamaged     3 records   every checksum verifies: True
   record 2 deleted            2 records   every checksum verifies: True
   record 2 sent twice         4 records   every checksum verifies: True
   records 1 and 2 swapped     3 records   every checksum verifies: True
   cut off before end-of-file  2 records   every checksum verifies: True

   Four kinds of damage and not one of them is visible, because none
   of them is inside a record. That is the shape of the answer: a
   checksum is scoped to a RECORD, so it can say a record is damaged
   and can never say the FILE is. Catching these wants a different
   field -- a count, a sequence number, or a hash over the whole
   stream -- and which one you want is a decision to make at the
   start, because a field added later is a field every existing
   reader has never heard of.

   Unless, of course, the format left itself somewhere to put one.
   That is the record type, one field along: a reader that can skip a
   record it does not recognise is a reader that survives the version
   of the format nobody has written yet.
```
<!-- /output -->

</details>

## See also

- [Tribit — a silly 3-bit encoding, specified](../tribit/README.md) — the format these three fields are missing from, and where to put them
- [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) — the four layers a frame sits outside of; read it first if *encoding* and *format* still feel like one word
- [Binary to text](../../03_Encodings/binary_to_text/README.md) — base16, base32, base64 and what each costs; Intel HEX's DATA field is the first of those
- [UTF-7, and the seven-bit transport](../../03_Encodings/utf7_and_the_seven_bit_transport/README.md) — the same 7-bit constraint section 2 of the shell example measures, answered by an encoding rather than by a frame, and deprecated for a reason worth knowing before you make anything optional
- [Escaping into ASCII](../../03_Encodings/escaping_into_ascii/README.md) — the other way of surviving a text channel, and how it differs from armouring the whole stream
- [The byte that means something to somebody else](../../12_Adversarial/in_band_signals/README.md) — what happens to a format whose delimiter turns up in its data
- [Hex: a number, or a picture of bytes](../../01_Bits_and_Bytes/hex_number_or_bytes/README.md) — `RECLEN` is a number and `DATA` is a picture, in the same record, in the same notation
- [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) — `xxd -r -p` is the DATA field's decoder, and you already have it
- [Intel HEX ↗](https://en.wikipedia.org/wiki/Intel_HEX) — the article that prompted this page; the specification below is what it was checked against
- [*Hexadecimal Object File Format Specification*, Revision A, 1988 ↗](https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/s2012/ads264_mws228/Final%20Report/Final%20Report/Intel%20HEX%20Standard.pdf) — eleven pages, and the source for every record number and field width on this page
- [Motorola S-record ↗](https://en.wikipedia.org/wiki/SREC_%28file_format%29) — the same three fields, arranged differently: a byte count that includes the checksum, and a *one's* complement where Intel HEX takes a two's. Worth reading beside this one for how much of a frame is the designer's free choice
