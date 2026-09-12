# The bytes do not say which end

**Level:** 101 → 201 · for anyone who has read one hex dump

**One line:** A file records bytes and never records which of them is the big one, so *"what number is this?"* has two correct answers — and every tool that shows you one of them is applying a setting, whether or not it tells you which.

## The question begins at two bytes

[Grouping is a choice](../grouping_is_a_choice/README.md) leaves a dump grouped into pairs and does not say which half of a pair is worth more. [Hex: a number, or a picture of bytes](../hex_number_or_bytes/README.md) names the gap and steps over it: a number has no byte order, a byte string does, and the question comes into existence at the moment you cross from one reading to the other. This page is that crossing.

A single byte has no order, because there is nothing to put first. Two bytes have two arrangements, and here is the whole problem on three of them:

```text
the file            2f 75 05

read big-endian     0x2f7505  =  3110149      most significant byte first
read little-endian  0x05752f  =   357679      least significant byte first
```

Both readings are correct. Nothing was corrupted, nothing was misparsed, and the two numbers differ by a factor of nine. The file contains three bytes and an opinion about them is not one of the things it contains — so a reader has to bring the opinion, and the only question is whether it brought the right one.

This is why *"the field is four bytes"* is not a specification and *"the field is four bytes, big-endian, unsigned"* is. It is also why the failure has no exception in it: **every byte string is a valid number in both orders**, so a mismatch cannot raise. It can only be wrong.

## Where the names come from

Danny Cohen took them from *Gulliver's Travels*, in [*On Holy Wars and a Plea for Peace* ↗](https://history.rfc-editor.org/ien/ien137.txt) — IEN 137, dated 1 April 1980, a joke date on a serious paper. Swift's Lilliput is at war with Blefuscu over which end of a boiled egg to open, and Cohen's point in borrowing it was that **neither order is better**. There is no technical argument that settles it; there is only the cost of not having agreed. The paper argues for picking one for the *network* precisely because the argument is unwinnable, which is where **network byte order** — big-endian — comes from, and why C's conversion functions are named `htons` and `ntohl` for *host to network* and back.

In practice the two camps are named after processors. **Little-endian** is what x86 and ARM do, so it is what the machine you are reading this on almost certainly does; the older literature calls it *Intel order*. **Big-endian** is what the 68000 and SPARC did and what the internet protocols write, so it turns up as *Motorola order* or *network order*. Neither name tells you anything about a file, which is the point of the next section.

## The setting belongs to the reader, not to the file

Open three bytes in a hex editor and you can watch this directly, because the editor makes the reading a control you can click.

**010 Editor** gives *every file* its own endian setting and prints it in the status bar as `LIT` or `BIG`; the `View > Endian` menu or a click on that word changes it, and — the sentence worth reading twice — *"most tools and the Inspector use this endian setting"*. The Inspector is the pane that reads the bytes under the cursor as an int16, an int32, a float, and it re-reads all of them through whichever way the switch is thrown. It can also be configured to set the endian from the file **extension**, so a format that is big-endian by specification opens that way without being asked. Throw the switch and the hex column does not move: the *file* is untouched and every number beside it changes. *(From [010 Editor's *Introduction to Byte Ordering* ↗](https://www.sweetscape.com/010editor/manual/ByteOrdering.htm) — the vendor's documentation, not machine-checked, unlike everything below.)*

**Hex Fiend** does the same job in its data inspector, whose type row reads `le` or `be` beside the value. [The screenshot on *Binary or text*](../../06_Terminal/binary_or_text/README.md#looking-at-the-bytes) is of exactly that row, sitting at `le, dec`, on a file whose bytes are `C0FFEE`.

That control is not a hex-editor luxury. **It exists on the command line too — as a flag, and on one tool as a default you never chose:**

| command | prints | what it did |
|---|---|---|
| `xxd` | `2f75 0500` | the file |
| `od -An -tx1` | `2f 75 05 00` | the file |
| `hexdump -C` | `2f 75 05 00` | the file |
| `xxd -e -g 4` | `0005752f` | **one 32-bit little-endian number** |
| `od -An -x` | `752f 0005` | **two 16-bit numbers, this CPU's order** |
| `hexdump` | `752f 0005` | the same — **and it is the default** |

Three of the six printed the file; three printed numbers. And the number `xxd -e` prints is `0x05752f` with its leading zero byte still attached — the little-endian reading from the top of this page, arrived at by a flag rather than by a status bar. [Plain `hexdump`'s swap](../../11_Tools/hexdump/README.md) has its own account on the `hexdump` page, and [Grouping is a choice](../grouping_is_a_choice/README.md#the-tool-will-change-your-representation-to-keep-the-claim-true) sets out the shape it belongs to: a tool asked a question it cannot answer in the terms it was given, answering a neighbouring question instead, in silence.

The habit that falls out of this is small and worth keeping: **in a bug report, dump with a tool that never groups into a number** — `xxd`, `od -tx1`, `hexdump -C`. Those three print the same thing on every machine ever built. The other three print a picture of your CPU's opinion, and are not even reproducible across hardware.

## Text has no byte order; code units do

This is the cleanest way to say why [UTF-16 needs a mark and UTF-8 does not](../../03_Encodings/byte_order_and_bom/README.md). Endianness is not a property of *text*. It is a property of a multi-byte **code unit**, and the encodings differ in what their unit is:

- **UTF-8**'s unit is one byte. A three-byte character has exactly one spelling, there is no end to put first, and there is nothing for a byte order mark to resolve — which is why the three bytes `EF BB BF` at the front of a UTF-8 file are doing a *different* job, as a signature.
- **UTF-16**'s unit is two bytes, **UTF-32**'s is four. Both are therefore ambiguous in a file, and undetectably so, since both layouts are well-formed. `U+FEFF` first in the stream resolves it by being a two-byte value written in the file's own order.

So the BOM is not a text problem that happens to involve bytes. It is this page's problem, met at the point where the thing being ordered is a character.

## In Python

<!-- output:which_end_comes_first_py -->
*Verified output of [`which_end_comes_first_py.py`](examples/which_end_comes_first_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE FILE, TWO NUMBERS
   the bytes                      2f 75 05
   int.from_bytes(b, 'big')         3110149   0x2f7505
   int.from_bytes(b, 'little')       357679   0x05752f
   Neither call is a misreading. The bytes are the same object both times;
   the number is a thing the reader made, and the file never voted.

2. THIS MACHINE
   sys.byteorder                  'little'
   That is what the CPU does in memory. It is NOT what the bytes in a file
   do, and -- the next section -- it is not what Python does when you
   decline to choose.

3. THE DEFAULT IS 'big', AND IT IS NOT YOUR MACHINE'S ORDER
   int.from_bytes(b)              3110149
   (65).to_bytes(2).hex()         00 41
   Since Python 3.11 both arguments have defaults: to_bytes(length=1,
   byteorder='big'). So the reflex call is not 'whatever this machine
   does' -- it is big-endian on every machine, while sys.byteorder is
   'little' here. The two disagree, silently, and the result is a
   perfectly ordinary int either way.
   Before 3.11 the argument was required, which is the version most advice
   about this was written against.

4. struct: FIVE PREFIXES, AND ONLY TWO OF THEM NAME AN ORDER
   <I  05 75 2f 00  little-endian, no padding
   >I  00 2f 75 05  big-endian, no padding
   !I  00 2f 75 05  network order -- a synonym for >
   =I  05 75 2f 00  this machine's order, no padding
   @I  05 75 2f 00  this machine's order AND its alignment (the default)
   '!' and '>' produce the same bytes because network byte order IS
   big-endian; the name is the only difference. '=' and '@' differ from
   each other in padding, not in order, which is why a struct that looks
   portable because it says '=' is still this machine's opinion.
   struct.calcsize('@ci') = 8, struct.calcsize('=ci') = 5   <- the padding, not the order

5. THE FAILURE HAS NO EXCEPTION IN IT
   wrote 3110149 little-endian   -> 05 75 2f 00
   read it back big-endian       -> 91565824
   3110149 became 91565824. No error, no warning, no clue:
   every byte string is a valid number in both orders, so a mismatch
   cannot raise. It can only be wrong. That is the whole reason a format
   specification has to say which end, and why 'the field is four bytes'
   is not a specification.
```
<!-- /output -->

Section 3 is the one to carry away, because it is the half of this that changed recently and quietly. **Since Python 3.11, `int.from_bytes` and `int.to_bytes` have defaults** — `length=1`, `byteorder='big'` — where before 3.11 the byte order was a required argument. Most advice written about this says the argument is mandatory, and on a modern interpreter it is not.

The default is the interesting part. It is `'big'`, which is **not** what `sys.byteorder` reports on any machine you are likely to own. So a bare `int.from_bytes(b)` is not *"read it the way this computer does"* — it is *"read it as network order"*, on every platform, and it returns an ordinary `int` whichever you meant. That is a defensible choice (a default that is the same everywhere is a default you can reason about), and it is not the one most people assume when they leave the argument out.

`struct` is worth the second look too: of its five prefixes only `<`, `>` and `!` name an order — `!` is a synonym for `>` because network order *is* big-endian — while `=` and `@` both mean *this machine's*, and differ from each other in **padding**, not in order. A struct format that says `=` because it looked like the portable one is still your machine's opinion, with the alignment taken out.

## In the terminal

<!-- output:which_end_comes_first_sh -->
*Verified output of [`which_end_comes_first_sh.sh`](examples/which_end_comes_first_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE FILE: three bytes, and nothing on this page will change them

$ xxd three.bin
00000000: 2f75 05                                  /u.
   2f 75 05. That is the whole file. Ask what NUMBER it is and there are two
   answers, because a file records bytes and never records which end is the
   big one:
      0x2f7505 = 3110149   most significant byte first  (big-endian)
      0x05752f =  357679   least significant byte first (little-endian)
   Neither is a misreading. The question did not exist until you asked for a
   number, and the file does not answer it.

2. FOUR BYTES THROUGH SIX TOOLS -- same file every time
   (a fourth byte 00, so a 32-bit reading is a whole group; every dump here
   goes through squeeze, so the six are comparable and so the two xxd builds
   agree -- they pad a short line's trailing space differently)

$ xxd four.bin | squeeze
00000000: 2f75 0500 /u..

$ xxd -e -g 4 four.bin | squeeze
00000000: 0005752f /u..

$ od -An -tx1 four.bin | squeeze
2f 75 05 00

$ od -An -x four.bin | squeeze
752f 0005

$ hexdump four.bin | squeeze
0000000 752f 0005
0000004

$ hexdump -C four.bin | squeeze
00000000 2f 75 05 00 |/u..|
00000004

3. READ THAT COLUMN AGAIN
      xxd            2f75 0500     the file
      xxd -e -g 4    0005752f      ONE 32-bit little-endian number
      od -An -tx1    2f 75 05 00   the file
      od -An -x      752f 0005     TWO 16-bit numbers, this CPU's order
      hexdump        752f 0005     the same, and it is the DEFAULT
      hexdump -C     2f 75 05 00   the file

   Three of the six printed the file. Three printed numbers -- and 0005752f
   is 0x05752f, the little-endian reading from section 1, with the leading
   zero byte still on it. The setting a hex editor puts in its status bar is
   the same setting; on the command line it is a flag you may not know you
   set, and on a bare hexdump it is one you never chose at all.

4. SO WHICH DUMP IS THE FILE?
   The ones that never group into a number: xxd, od -tx1, hexdump -C.
   Those three print the same bytes on every machine ever built. The other
   three print a picture of this CPU's opinion, and on a big-endian machine
   the same three commands would print something else.
```
<!-- /output -->

## In Rust

<!-- output:which_end_comes_first_rs -->
*Verified output of [`which_end_comes_first_rs.rs`](examples/which_end_comes_first_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THREE METHODS, NO FLAG
   n = 0x002f7505  (3110149)
   n.to_be_bytes()   [00, 2f, 75, 05]
   n.to_le_bytes()   [05, 75, 2f, 00]
   n.to_ne_bytes()   [05, 75, 2f, 00]
   There is no n.to_bytes(). You cannot decline to choose, because
   the choice is spelled into the name you call -- which also means
   `grep to_ne_bytes` finds every place a program committed to the
   machine it was built on. The Python version of that mistake is a
   call with the argument LEFT OUT, and no grep finds a missing word.

2. WHAT THIS BUILD TARGETS
   cfg!(target_endian = "little")   true
   cfg!(target_endian = "big")      false
   `ne` is whichever of those is true, decided at COMPILE time, so a
   cross-compiled binary and the machine that built it can disagree.

3. THE WIDTH IS IN THE TYPE
   bytes                          [00, 2f, 75, 05]
   u32::from_be_bytes(bytes)      3110149
   u32::from_le_bytes(bytes)      91565824
   from_be_bytes takes [u8; 4], not &[u8]: a slice of the wrong
   length is a compile error, not a runtime surprise. Python's
   int.from_bytes accepts any length and quietly means it.

4. THE SAME MISMATCH AS EVERY OTHER LANGUAGE
   wrote 3110149 little-endian   -> [05, 75, 2f, 00]
   read it back big-endian       -> 91565824
   Rust makes you NAME the order; it cannot make you name the same
   one twice. Nothing here is unsafe, nothing panics, and the number
   is simply wrong -- the compiler was never told the two calls were
   supposed to agree.
```
<!-- /output -->

Rust is the language that will not let you skip the question: there is no `to_bytes()`, only `to_be_bytes`, `to_le_bytes` and `to_ne_bytes`, so the order is spelled into the name you call. The practical payoff is a grep. `to_ne_bytes` is native order, fixed at **compile** time by the target rather than at run time by the host, and it is the one method on that list that is not portable — so `grep to_ne_bytes` enumerates every place a program committed to the machine it was built for. Python's version of the same mistake is a call with the argument *left out*, and no grep finds a missing word.

The width comes along for free: `u32::from_be_bytes` takes a `[u8; 4]`, so a slice of the wrong length is a compile error rather than a runtime surprise, where `int.from_bytes` accepts any length and quietly means it.

## If you are coming from Python or ABAP

**Python.** Everything above, plus one habit: pass `byteorder` explicitly even where the default is what you wanted, because the next reader cannot tell *"I chose big-endian"* from *"I didn't think about it"*, and the two need different fixes. For anything with a fixed layout reach for `struct` with `<` or `>` rather than assembling `int.from_bytes` calls — the format string documents the record in one place, and `struct.error` catches a length mismatch that `int.from_bytes` would silently accept.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* The question is usually one layer away from you, because an `xstring` arrives from an interface already laid out by whoever wrote it. Where it does surface, it surfaces as a conversion class rather than as a flag: `cl_abap_conv_*` handle the code-page side, and a numeric field's layout belongs to the interface agreement — an RFC or a file spec — not to the program. The trap is the same as everywhere else: an application server's own byte order is not a fact about the file it just read, and a field that "works in the test system" has only proved that two machines agree, not that the specification was read. Write the expected order into the interface document, and test with bytes you constructed rather than bytes the same platform produced.

## Try it

1. Take a binary file you own — a `.png`, a `.zip`, a compiled `.o` — and dump its first sixteen bytes with `xxd` and then with a bare `hexdump`. Which pairs moved? PNG's and ZIP's headers are documented; check whether the tool or the format matches your expectation.
2. Find a struct or a `from_bytes` call in your own code where the byte order is defaulted or implied rather than written down. Decide what it *should* be, then write it down even if nothing changes.
3. `python3 -c "import sys; print(sys.byteorder)"` and then `python3 -c "print(int.from_bytes(b'\x01\x00'))"`. Explain the second result to yourself using the first, and notice that you cannot.
4. Open any file in a hex editor, select four bytes, and find the inspector's endian control. Switch it and watch which parts of the window change and which do not.

## Practice

**Four bytes: `01 00 00 00`.** Write all five answers down before running anything.

1. The value as an unsigned 32-bit **big-endian** integer.
2. The value as an unsigned 32-bit **little-endian** integer.
3. What a bare `hexdump` prints.
4. What `xxd` prints.
5. Which of those four answers would be different on a big-endian machine.

The fifth is the one worth the pause: some of the first four are facts about the file and some are facts about the machine you ran them on, and nothing in any of the printouts says which is which.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:which_end_comes_first_kata_sh -->
*Verified output of [`which_end_comes_first_kata_sh.sh`](examples/which_end_comes_first_kata_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE FILE: four bytes, 01 00 00 00

$ wc -c < one.bin | squeeze
4

1 and 2. THE TWO INTEGER READINGS

$ python3 -c "b=open('one.bin','rb').read(); print('big   ', int.from_bytes(b,'big')); print('little', int.from_bytes(b,'little'))"
big    16777216
little 1
   big-endian     16777216   = 0x01000000
   little-endian         1   = 0x00000001
   The same four bytes are sixteen million or one -- a factor of 2^24, which
   is the largest ratio two readings of four bytes can have (all the weight
   in the first byte and none anywhere else, which is this file). That is
   why 01 00 00 00 is the pattern to keep in your head: when a length field
   reads 16777216 and the file is 200 bytes long, you have not found a
   corrupt file, you have found the other end.

3. WHAT A BARE hexdump PRINTS

$ hexdump one.bin | squeeze
0000000 0001 0000
0000004
   0001 0000 -- two 16-bit numbers in this CPU's order, not the file. The
   first group is 0x0001, made from the bytes 01 00.

4. WHAT xxd PRINTS

$ xxd one.bin | squeeze
00000000: 0100 0000 ....
   0100 0000 -- the file, in file order, grouped into pairs and reordered
   by nothing. Compare it with answer 3 character by character: same four
   bytes, same tool family, and the groups are not the same number.

5. WHICH OF THE FOUR WOULD CHANGE ON A BIG-ENDIAN MACHINE
   Only answer 3.

      1 and 2   facts about the FILE. int.from_bytes names its order, so
                both numbers are the same on every machine ever built.
      4         a fact about the FILE. xxd never reorders.
      3         a fact about the MACHINE. A bare hexdump reads two bytes
                at a time as a number and prints it in the host's order,
                so on a big-endian host the same command prints 0100 0000.

   Two of the four are the file and two are not, and nothing in the
   printout says which is which. That is the whole lesson: the dump you
   paste into a bug report should be one of the ones that cannot lie.
```
<!-- /output -->

</details>

## See also

- [Hex: a number, or a picture of bytes](../hex_number_or_bytes/README.md) — the page that raises this question and deliberately does not answer it
- [Grouping is a choice](../grouping_is_a_choice/README.md) — the width a dump groups by is a claim about the data's unit; this page is what the tool does with the claim
- [Reading a hex dump](../reading_a_hex_dump/README.md) — the three columns, and which of them are the file
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — the same question where the multi-byte unit is a character, and the mark invented to answer it
- [`hexdump`](../../11_Tools/hexdump/README.md) — the swap in full, and the format engine behind it
- [`xxd`](../../11_Tools/xxd/README.md) — the dump that never reorders, and what `-e` does when you ask it to
- [Packing a record](../../07_Real_Data/packing_a_record/README.md) — width, byte order and alignment as the three decisions a binary record has to make
- [*On Holy Wars and a Plea for Peace* ↗](https://history.rfc-editor.org/ien/ien137.txt) — Cohen, IEN 137, 1980; eight pages, and the source of both words
