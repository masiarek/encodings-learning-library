# The mojibake round trip

**Level:** 201 · for anyone repairing data

**One line:** Damaged text is repairable exactly when the wrong step *misread* bytes rather than *discarded* them — Latin-1 discards nothing so it always reverses, Windows-1252 has five unassigned bytes so it sometimes cannot, and a `?` or a `�` means the byte was thrown away and nothing will bring it back.

## Ask the question before you reach for the incantation

The repair is one line, and everybody knows it: `text.encode('latin-1').decode('utf-8')`. That is not the skill. The skill is knowing, *before* you run anything, whether a repair can work at all — because the alternative is a script that runs over a column, reports success, and leaves you no better informed about the rows it could not fix and no wiser about the rows it silently changed.

The question is decidable, and it has one form:

> **Did the broken step misread the bytes, or discard them?**

Mojibake is a function applied uniformly to your bytes, and [nothing was damaged](../../03_Encodings/mojibake/README.md) — a function that threw nothing away can be un-applied. But some failure modes are not functions at all: they replaced a character with a fixed stand-in and dropped what was there. Those are not repairable by anybody, and no cleverness changes that. Everything below is how to tell the two apart from the evidence in front of you.

## Latin-1 always reverses, and the reason is arithmetic

Latin-1 maps byte *N* to code point *N* for all 256 values. The decode is total — it cannot fail on any input — and one-to-one, so the encode is exactly its inverse. That is why a file read under Latin-1 still contains every original byte: they are sitting inside the wrong-looking string as code points `U+0000`–`U+00FF`, and `.encode('latin-1')` hands the file back byte for byte. Section 2 of the run below checks all 256 rather than asserting it.

This is the same property from two directions, and it is worth holding both: Latin-1 is the **right** tool for undoing mojibake precisely because it is the **wrong** tool for detecting anything. A decoder that never refuses tells you nothing about the file it just accepted.

## Windows-1252 does not, and the five bytes are ordinary letters

[Windows-1252 leaves five byte values unassigned](../windows_1252_vs_latin1/README.md) — `0x81`, `0x8D`, `0x8F`, `0x90` and `0x9D` — so it maps 251 of 256 and the round trip is not guaranteed. That sounds like a rounding error until you notice *where* those bytes turn up. All five are legal UTF-8 continuation bytes, so they appear inside perfectly ordinary characters: `Á` is `C3 81`, `Í` is `C3 8D`, `Ð` is `C3 90`, `Ý` is `C3 9D`, and `Ł` is `C5 81`. A Spanish capital, an Icelandic one, a Polish L.

So the round trip fails on exactly the rows a European master-data table is full of. There are two ways it shows up, and they feel completely different:

- **A strict reader refuses.** Python's `cp1252` codec raises `UnicodeDecodeError` on the hole, naming the byte and the offset. This is the *good* outcome — the reader is telling you the label is wrong before anything is written down.
- **A lenient reader does not.** Most readers outside Python map the five holes to the C1 controls rather than refusing, so the byte survives into the string and the text looks repairable. It is not: Python's `cp1252` *encoder* has no entry to write those characters back to, so the re-encode fails and the guard hands you your input back unchanged.

This page uses `Ł` because it is the sharpest available case, and it is the reason `Łódź` is in the [cast](../../CAST.md): **`Ł` is the one letter there whose UTF-8 lands on a hole.** The cast's `é` (`C3 A9`), `ż` (`C5 BC`), `ß` (`C3 9F`) and `€` (`E2 82 AC`) all avoid the five, so none of them can show a round trip that fails. Two *invisible* characters in the cast do land on one — `U+0301` is `CC 81`, and the family's zero-width joiner is `E2 80 8D` — so a `café` spelled with a separate `U+0301` cannot make the trip either, and nothing on the screen says why.

## The two losses that look alike and blame different people

A `?` and a `�` both mean a byte is gone, and they are gone at opposite ends of the wire:

| What you find | Who lost it | When |
|---|---|---|
| `?` — ASCII `0x3F` | the **sending** system | at write time: its table had no room for the character, and `errors='replace'` on an *encode* writes a question mark |
| `�` — `U+FFFD` | the **reading** system | at read time: it met a byte its table could not use, and `errors='replace'` on a *decode* writes the replacement character |
| nothing at all — the text is just short | either | `errors='ignore'`, which is the same loss with no evidence left behind |

Neither is repairable. But the distinction is worth making the moment you find one, because it says whose logs to read and whose configuration to change — and because the third row is the one to fear. `ignore` leaves no marker, so a field that is merely *shorter* than it should be is the same failure with the evidence removed.

The one lossy policy that is reversible is `xmlcharrefreplace`, which writes `&#321;` instead of throwing the character away: it wrote the code point down in ASCII rather than discarding it, so the information is still on disk in a different notation.

## The guard, and the two things it cannot do

A repair function should return its input unchanged whenever the round trip does not work. That single property is what lets you run it over a whole column without first sorting the good rows from the bad — every row that is fine, or damaged in a way this repair does not address, comes out untouched.

There are two limits, and the second is the one people get wrong.

**A successful round trip is not proof the repair was right.** The guard proves the re-encoded bytes are valid UTF-8; it cannot prove they were *meant* to be. `Ã©` is a legitimate two-character string, and it round-trips into `é` silently. How likely is that? Count every string of a given length drawn from Latin-1's printable top half and ask how many are accidentally valid UTF-8: **0% at length 1** — one high byte is never valid UTF-8 alone — **10.4% at length 2**, and **1.7% at length 3**, falling away fast as every extra character has to keep fitting the UTF-8 grammar. The practical reading is a rule about *scope*: the guard is safe on a sentence and genuinely risky on a two-character field. On short fields, decide for the column rather than for the value.

**And "repair until it errors" is a Python trick.** The Python loop stops on its own because its last step is a UTF-8 *decode*, which correctly-repaired text fails. A shell pipeline has no such stop — `iconv -f UTF-8 -t ISO-8859-1` will cheerfully take a correct UTF-8 file one hop further and report success, which the [mojibake](../../03_Encodings/mojibake/README.md) page demonstrates. The fix is not to avoid the shell but to compose the missing half, which is what the terminal section below does.

## In Python

<!-- output:mojibake_round_trip_py -->
*Verified output of [`mojibake_round_trip_py.py`](examples/mojibake_round_trip_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE DECIDING QUESTION
------------------------------------------------------------------------
   Mojibake is a function that was applied to your bytes. A function
   can be undone when it threw nothing away. So the question is not
   'how do I repair this' but:

      Did the wrong step DISCARD any byte, or merely MISREAD it?

   Misread bytes are all still there and the damage is reversible.
   Discarded bytes are gone, and no amount of cleverness returns
   them. Sections 2 to 4 work out which case you are in.

2. WHY LATIN-1 ALWAYS REVERSES -- BY EXHAUSTION, NOT BY REPUTATION
------------------------------------------------------------------------
   bytes that survive .decode('latin-1').encode('latin-1'): 256 of 256

   Latin-1 maps byte N to code point N for all 256 values, so the
   decode is a total, one-to-one function and the encode is exactly
   its inverse. A reader using Latin-1 cannot fail and cannot drop
   anything -- so every byte of the original file is still sitting
   inside the wrong-looking string, and .encode('latin-1') hands the
   file back byte for byte.

   That is why Latin-1 is the right tool for UNDOING mojibake and the
   wrong tool for DETECTING anything: it accepts every file on earth.

3. WHY CP1252 DOES NOT ALWAYS REVERSE
------------------------------------------------------------------------
   cp1252 leaves five byte values unassigned:
      0x81 0x8D 0x8F 0x90 0x9D

   Those five are all legal UTF-8 CONTINUATION bytes, so they appear
   inside ordinary characters. Any character whose UTF-8 encoding
   contains one cannot survive a cp1252 round trip. Below U+0800
   that is 150 characters, and these are the everyday ones:

      U+00C1  Á   c3 81
      U+00CD  Í   c3 8d
      U+00CF  Ï   c3 8f
      U+00D0  Ð   c3 90
      U+00DD  Ý   c3 9d
      U+0101  ā   c4 81
      U+010D  č   c4 8d
      U+010F  ď   c4 8f
      U+0110  Đ   c4 90
      U+011D  ĝ   c4 9d
      U+0141  Ł   c5 81
      U+014D  ō   c5 8d
      U+014F  ŏ   c5 8f
      U+0150  Ő   c5 90
      U+015D  ŝ   c5 9d

   So the repair that fails is not an exotic corner: it is a Spanish
   or Icelandic capital, or a Polish L-with-stroke.

4. ONE STRING, FOUR WAYS OF GOING WRONG
------------------------------------------------------------------------
   original           'Łódź'
   correct UTF-8      c5 81 c3 b3 64 c5 ba

   (a) READ AS LATIN-1 -- every byte misread, none discarded
       looks like     '\xc5\x81\xc3\xb3d\xc5\xba'
       repair         repaired: 'Łódź'
       identical to the original? True

   (b) READ AS CP1252 -- the decode cannot even complete
       UnicodeDecodeError: byte 0x81 at offset 1
       A strict cp1252 reader REFUSES this file. That is the good
       outcome -- it is the reader telling you the label is wrong
       before anything is written down.

   (c) READ AS CP1252 BY A LENIENT READER -- the byte survives, the
       repair does not
       looks like     '\xc5\x81\xc3\xb3d\xc5\xba'
       repair         cannot re-encode under cp1252: character maps to <undefined>
       unchanged?     True
       Many readers outside Python map the five holes to the C1
       controls rather than refusing. The text then looks repairable
       and is not, because Python's cp1252 ENCODER has no entry to
       write those characters back to. The guard returns the input.

   (d) WRITTEN WITH A REPLACEMENT -- the byte is genuinely gone
       errors=replace            -> '?ód?'
       errors=ignore             -> 'ód'
       errors=xmlcharrefreplace  -> '&#321;ód&#378;'
       These happened at WRITE time, in the sending system, and no
       byte of the original reached the file. 'replace' wrote 0x3F,
       the ASCII question mark; 'ignore' wrote nothing at all. Only
       xmlcharrefreplace is reversible, because it wrote the code
       point down in ASCII instead of throwing it away.

5. THE GUARD, AND WHY IT IS THE WHOLE POINT
------------------------------------------------------------------------
   try_repair() returns the INPUT unchanged whenever the round trip
   fails, so running it on text that was never damaged is a no-op:

      'already fine'       -> round trip is a no-op -- nothing to repair unchanged
      'Łódź'               -> cannot re-encode under latin-1: ordinal not in range(256) unchanged
      'café'               -> re-encoded, but the bytes are not UTF-8 unchanged

   That property is what lets you run a repair over a whole column
   without first sorting the good rows from the bad ones.

6. THE GUARD'S LIMIT: A SUCCESSFUL ROUND TRIP IS NOT A PROOF
------------------------------------------------------------------------
   'Ã©' is a legitimate two-character string.
   try_repair says: repaired -> 'é'
   Correct text, silently changed. The guard proves the bytes form
   valid UTF-8; it cannot prove they were MEANT to.

   How often can that happen? Count every string of length N drawn
   from Latin-1's printable top half, and ask how many are valid
   UTF-8 by accident:

      length 1:      0 of     96 =  0.000%
      length 2:    960 of   9216 = 10.417%
      length 3:  15360 of 884736 =  1.736%

   Length 1 is impossible -- one high byte is never valid UTF-8 on
   its own. Then the rate falls away as every extra character has to
   keep fitting the UTF-8 grammar. The practical reading: the guard
   is safe on a sentence and genuinely risky on a two-character
   field, which is exactly the sort of column an interface has.
   On a short field, check the whole column instead of each value.

7. COUNTING THE LAYERS BEFORE REPAIRING THEM
------------------------------------------------------------------------
   after 0 bad hop(s): '\xe9'                     1 chars
   after 1 bad hop(s): '\xc3\xa9'                 2 chars
   after 2 bad hop(s): '\xc3\x83\xc2\xa9'         4 chars
   after 3 bad hop(s): '\xc3\x83\xc2\x83\xc3\x82\xc2\xa9' 8 chars

   Each hop turns one high byte into two, so the string grows and a
   column that keeps overflowing is often this. Repair by looping
   try_repair until the verdict stops being 'repaired':

   stopped after 3 repair(s): 'é'
   the ladder above took 3 hops, and the loop undid 3 -- they agree
   The loop terminates because the last step is a UTF-8 DECODE, and
   repaired text fails it. A shell pipeline has no such stop -- see
   the mojibake page for iconv cheerfully taking one hop too many.
```
<!-- /output -->

## In the terminal

<!-- output:mojibake_round_trip_sh -->
*Verified output of [`mojibake_round_trip_sh.sh`](examples/mojibake_round_trip_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE GUARD IS TWO CALLS, NOT ONE
------------------------------------------------------------------------
   correct file:        636166c3a90a
   after 1 bad hop:     636166c383c2a90a
   after 2 bad hops:    636166c383c283c382c2a90a

   Now repair, checking the result each time instead of trusting the
   exit status of the conversion:

      repair 1: accepted   636166c383c2a90a
      repair 2: accepted   636166c3a90a
      repair 3: REFUSED    (the guard rejected the candidate)

   current bytes: 636166c3a90a
   identical to the original file: yes

   Repair 3 is where a bare iconv pipeline keeps going: the conversion
   itself succeeds, because Latin-1 can hold 'cafe-acute' perfectly
   well. What stops the loop is the second call -- the four bytes
   63 61 66 e9 are not UTF-8, so the candidate is thrown away and the
   file is left where it was.

2. WHY THE SECOND CALL IS THE ONE THAT KNOWS
------------------------------------------------------------------------
   converting the CORRECT file one hop too far: iconv exit=0
   asking whether that hop's output is UTF-8:    exit=1

   Two different questions. iconv answers 'could I convert this',
   which is yes. Only the validator answers 'is the result still the
   kind of thing I wanted', which is no. Neither call alone is a
   repair decision; the pair is.

3. SURVEY THE COLUMN BEFORE YOU CHANGE IT
------------------------------------------------------------------------
   five rows, one per damage mode:

      row  bytes                      verdict
      1    4e6f77616b0a               valid UTF-8, no repair applies
      2    636166c3a90a               valid UTF-8, no repair applies
      3    636166c383c2a90a           repairable -> 636166c3a90a
      4    6361663f0a                 holds '?' -- byte discarded when WRITTEN
      5    636166efbfbd0a             holds U+FFFD -- byte discarded when READ

   Rows 4 and 5 are the ones to notice. Both are perfectly valid
   UTF-8, so nothing downstream will complain, and both have lost a
   byte for good -- row 4 in the sending system and row 5 in the
   reading one. That is the difference worth knowing before you go
   looking for whose fault it was.

   Row 3 is the only one a repair helps. Running the repair over the
   whole file would have left rows 1, 2, 4 and 5 untouched, because
   the guard refuses each of them -- which is what makes a
   column-wide repair safe to run at all.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** Three things to hold. First, `errors=` is a *policy* and it belongs at the boundary — `replace` and `ignore` are one-way doors, and the reversible one for data you are only carrying is [`surrogateescape`](../../04_Python/surrogateescape/README.md), which smuggles the undecodable bytes through a `str` and hands them back byte for byte on the way out. Second, the round-trip idiom is `str → bytes → str` and the two codecs are different on purpose: you encode under the table that was *wrongly applied* and decode as *UTF-8*, so writing the same codec twice is the commonest way to get a confusing no-op. Third, `bytes.decode('latin-1')` is your escape hatch for holding arbitrary bytes in a string-shaped API and it should never appear in a code path that is supposed to *validate* anything — it accepts every file there is.

**ABAP.** The repair has the same two halves and they are two different calls: `cl_abap_codepage=>convert_to( )` turns your `string` back into an `xstring` under the table that was wrongly applied, and `convert_from( )` reads that `xstring` as UTF-8. Do it in that order and nothing else, because there is no in-place fix — a `REPLACE ALL OCCURRENCES` over the mojibake characters is the thing to avoid, since it treats a systematic, reversible transformation as a list of typos and will be wrong on the first character nobody put in the list. The guard transfers directly: `convert_from( )` raises `cx_sy_conversion_codepage` when the bytes are not valid in the table it was given, so wrap the pair in a `TRY` and return the original `string` in the `CATCH` — that is the ABAP spelling of *never make it worse*. Where ABAP is genuinely better placed than Python is upstream of all this: `OPEN DATASET … IN BINARY MODE` gives you an `xstring` nobody has decoded, and a field you never converted is a field you never have to repair. And note the `?` you will see in SE16 is not always this bug — SAP draws any character the display cannot render as `#`, so check the bytes before concluding a byte was lost. Verify code-page numbers against your own system, per [SAP code pages](../sap_code_pages/README.md). *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 07_Real_Data/mojibake_round_trip/examples
python3 mojibake_round_trip_py.py
bash mojibake_round_trip_sh.sh
```

1. Run the survey in section 3 of the shell script against the worst CSV you have, one line at a time. Count the rows in each of the four verdicts before you change a single byte — that count is the answer to "can this file be fixed", and you now have it without touching the file.
2. Search the same file for the two markers: `grep -c '?'` and `LC_ALL=C grep -c $'\xef\xbf\xbd'`. Any hit in the first is your sender's problem and any hit in the second is your reader's, so you now know which team to talk to.
3. Take one damaged field and repair it through `latin-1` and through `cp1252` separately. If they give different answers, or one refuses, you have just learned which system read the file.
4. Find a field whose length looks wrong but which contains no `?` and no `�`. That is the `ignore` case, and there is nothing in the data that will confirm it — say what you would look at instead.
5. Without the machine: a repair script has run over a million-row table and reports "1,000,000 rows processed, 0 errors". Say why that sentence is compatible with the table being completely unrepaired, and name the number you should have asked for instead.

## Practice

**Five damaged fields, and the question that sorts them.** Here are five fields as the reader sees them, written in Python's `ascii()` notation so nothing is hidden:

```text
   A   'caf\xc3\xa9'
   B   'caf?'
   C   'caf�'
   D   '\xc5\x81\xc3\xb3d\xc5\xba'
   E   'caf\xc3ƒ\xc2\xa9'
```

For each one, decide **before running anything**: is the original text recoverable? If so, through which table — `latin-1`, `cp1252`, or either — and how many hops? If not, say which end of the wire lost the byte.

Then say what evidence you used. Two of the five are decided without attempting a repair at all.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:mojibake_round_trip_kata_py -->
*Verified output of [`mojibake_round_trip_kata_py.py`](examples/mojibake_round_trip_kata_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE FIVE FIELDS, AS THE READER SEES THEM
------------------------------------------------------------------------
   A   'caf\xc3\xa9'
   B   'caf?'
   C   'caf\ufffd'
   D   '\xc5\x81\xc3\xb3d\xc5\xba'
   E   'caf\xc3\u0192\xc2\xa9'

THE EVIDENCE, BEFORE ANY REPAIR
------------------------------------------------------------------------
   Three questions decide it, and none of them changes the data:
     1. Is there a '?' or a U+FFFD? Then a byte was DISCARDED, and
        by whom depends on which of the two it is.
     2. Does the text re-encode under the table that was misapplied?
     3. Do those bytes then decode as UTF-8?

   A   re-encodes under latin-1; re-encodes under cp1252
   B   holds '?' (discarded on WRITE); re-encodes under latin-1; re-encodes under cp1252
   C   holds U+FFFD (discarded on READ); will NOT re-encode under latin-1; will NOT re-encode under cp1252
   D   re-encodes under latin-1; will NOT re-encode under cp1252
   E   will NOT re-encode under latin-1; re-encodes under cp1252

THE VERDICTS
------------------------------------------------------------------------
       through latin-1              through cp1252
   A   'caf\xe9' (1 hop)            'caf\xe9' (1 hop)
   B   no repair possible           no repair possible
   C   no repair possible           no repair possible
   D   '\u0141\xf3d\u017a' (1 hop)  no repair possible
   E   no repair possible           'caf\xe9' (2 hop)

READING THE TABLE
------------------------------------------------------------------------
   A  repairs, one hop. Ordinary mojibake: UTF-8 read as a one-byte
      table. Both columns agree, because the bytes involved (c3, a9)
      sit outside 0x80-0x9F, where the two tables are identical.

   B  never repairs. The '?' is byte 0x3F, written by the SENDING
      system when its table had no room for the character. Nothing
      about the original survived the write, so no reader can undo it.

   C  never repairs. U+FFFD was written by the READING system when it
      met a byte its table could not use. Same loss, opposite end of
      the wire -- and that is the whole diagnostic value of telling
      the two apart: B is the sender's logs, C is the receiver's.

   D  repairs through latin-1 and NOT through cp1252. This is the
      case the page is about. The text contains U+0081, one of the
      five code points cp1252 cannot write, so the re-encode fails
      before a decode is ever attempted. Latin-1 has all 256 and
      hands the bytes straight back.

   E  repairs through cp1252 in TWO hops, and not through latin-1 --
      the exact mirror of D. The field went through the same broken
      interface twice, and the reader on the far side was a Windows
      one, so the second hop put an f-with-hook in the string. That
      character lives at 0x83 in cp1252 and does not exist in
      latin-1 at all, so the latin-1 re-encode fails.

      D and E together are the point: the table that repairs is the
      table that BROKE it, and guessing wrong does not silently
      half-work -- it refuses.

   For the record, D was 'Łódź' (1 hop through latin-1)
   and E was 'café' (2 hops through cp1252).

THE ONE THAT IS NOT ON THE LIST
------------------------------------------------------------------------
   Every verdict above assumed the fields are damaged. Field A was
   read as 'caf' + A-tilde + copyright, and repaired to 'cafe-acute'
   -- but that same string is one a person could legitimately have
   typed, and the method cannot tell:
      'Ã©' -> repaired=True -> 'é'

   Same two characters, same successful round trip, and no way to
   know which was meant. The guard proves the bytes ARE valid UTF-8;
   it cannot prove they were meant to be. So decide for the COLUMN
   -- if most of it is damaged the odd innocent row is a price you
   chose, and if only one row looks damaged, look at it by hand.
```
<!-- /output -->

</details>

## See also

- [Mojibake](../../03_Encodings/mojibake/README.md) — what the garbage looks like and what each shape names; this page is what to do next
- [Windows-1252 vs Latin-1](../windows_1252_vs_latin1/README.md) — where the five holes come from, and why the table that repairs is the table that broke it
- [Encode, decode and errors](../../04_Python/encode_decode_and_errors/README.md) — the eight error handlers, and which of them throw a byte away
- [`surrogateescape`](../../04_Python/surrogateescape/README.md) — the one lossy-looking policy that is reversible
- [Validation is a boundary](../../03_Encodings/validation_is_a_boundary/README.md) — the `iconv -f UTF-8 -t UTF-8` test the shell guard is built on
- [SAP code pages](../sap_code_pages/README.md) — reproducing an interface's damage outside the system that caused it
- [Code pages](../../02_Characters/code_pages/README.md) — the tables themselves
