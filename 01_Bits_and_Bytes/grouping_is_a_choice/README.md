# Grouping is a choice

**Level:** 101 → 201 · for anyone who has read one hex dump

**One line:** The spaces in a dump are not in the file — the width you group by is a claim about what the data's unit is, and every tool has its own silent way of coping when the bytes refuse to divide by it.

## The spaces are not in the file

[Reading a hex dump](../reading_a_hex_dump/README.md) treats `xxd`'s layout as given. It is not. `xxd` pairs the bytes, `hexdump -C` spaces them singly, `od` puts characters on a second row — and `café` is the same five bytes under all three. Nothing in the file separates one byte from the next; a file is a run of bits, and a byte boundary is already an agreement laid over it.

So when a tool offers to group by something *other* than a byte, it is not offering a cosmetic setting. It is asking what you think the data is made of.

## The width is a claim about the unit

The widths a dump tool offers are not arbitrary. Each one is the code unit of something this library has a chapter about:

| Width | One group is | Where you meet it |
|---|---|---|
| 4 bits | a nibble — exactly one hex digit | [Hex is a shorthand](../hex_is_a_shorthand/README.md) |
| 5 bits | one Base32 character | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| 6 bits | one Base64 character | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| 8 bits | a byte | [A byte is eight bits](../a_byte_is_eight_bits/README.md) |
| 16 bits | a UTF-16 code unit | [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) |
| 24 bits | Base64's quantum; also an RGB pixel | [Binary to text](../../03_Encodings/binary_to_text/README.md) |
| 32 bits | a UTF-32 code unit | [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) |

Read the menu that way and it stops being a display preference. Picking 6 says *this is Base64*; picking 16 says *this is UTF-16*. The dump does not check, and it will draw whichever picture you ask for over whatever bytes are actually there.

The groups are cut from the **bit** stream, not from the bytes. A 5-bit group has to be — five does not divide eight — so the second group of any 5-bit view is part of one byte followed by part of the next, belonging to two bytes and to no character at all. That is not a quirk of the view; it is what Base32 does to your data, seen early.

## The tool will change your representation to keep the claim true

Here is where it bites. A 5- or 6-bit group has no whole number of hex digits, so a tool asked to group that way and to print hex has been asked for something that does not exist. [cryptii ↗](https://cryptii.com/pipes/hex-decoder/)'s hex-decoder pipe resolves it by quietly changing the *other* setting:

```text title="cryptii.com/pipes/hex-decoder, observed 2026-09-06 — a third-party web tool, not run by CI"
Format: Hexadecimal, input "The quick brown 🦊 jumps over 13 lazy 🐶." (45 bytes)

Group by     Format after        Output begins
--------     ------------        -------------
None         Hexadecimal         546865207175…
4 Bits       Hexadecimal         5 4 6 8 6 5 2 0 7 1 …
5 Bits       BINARY  ← switched  01010 10001 10100 …
6 Bits       BINARY  ← switched  010101 000110 100001 …
Byte         Hexadecimal         54 68 65 20 71 75 …
2 Bytes      Hexadecimal         5468 6520 7175 6963 …
3 Bytes      Hexadecimal         546865 207175 69636b …
4 Bytes      Hexadecimal         54686520 71756963 …

It does not switch back. Returning to "Byte" leaves you in binary,
looking at a view you did not choose and were not told about.
```

The switch is forced — hex genuinely cannot render five bits — and the tool is not wrong to make it. What it does not do is *say* so, and that is the shape worth recognising, because it is the same shape as [`od -a` inventing a letter](../../06_Terminal/inspecting_a_file/README.md) and [plain `hexdump` swapping every pair](../../11_Tools/hexdump/README.md): a tool asked a question it cannot answer in the terms it was given, answering a neighbouring question instead, in silence. When a dump surprises you, check what the tool decided before you conclude anything about the file.

## Nothing is padded, so the tail is ragged

Five bytes grouped four at a time is one group and a leftover. Display grouping does not pad, does not mark the short group, and does not warn you: `xxd -g4` on `café` prints `636166c3 a9`, and only counting tells you the `a9` is a tail rather than a group of its own kind.

That is exactly the line between a *view* and an *encoding*. [Base64](../../03_Encodings/binary_to_text/README.md) cuts the same bit stream into sixes, and because its groups have to survive a round trip it must pad the last quantum to 24 bits and then write `=` to declare how much it added. A dump has nothing to declare, because nobody is going to reassemble the file from the picture. Ragged is correct here and would be a bug one layer down.

## Alignment is not understanding

`😀` is four bytes of UTF-8. Group a file by four bytes and the emoji will sometimes land inside a single group, looking for all the world as though the tool understood the encoding. It did not. It divided by four, and the character's *offset* happened to divide too:

```text
offset 0  (0 % 4 = 0)   f09f9880                     one group
offset 1  (1 % 4 = 1)   7ef09f98 80                  split
offset 4  (4 % 4 = 0)   7e7e7e7e f09f9880            one group
offset 5  (5 % 4 = 1)   7e7e7e7e 7ef09f98 80         split
```

One character added earlier in the file and the picture changes. This is worth having been stung by once, because the accidental version is convincing: on the cryptii screen above, grouping by 4 bytes puts **both** emoji in a group of their own — 🦊 starts at byte 16 and 🐶 at byte 40, and both of those divide by four. Two coincidences in one sentence look exactly like a feature.

## In Python

<!-- source:grouping_is_a_choice_py -->
*[`grouping_is_a_choice_py.py`](examples/grouping_is_a_choice_py.py) in full — pasted here by `tools/run_examples.py` from the file CI runs.*

```python
#!/usr/bin/env python3
"""Where the spaces go in a dump, and what choosing a width claims.

Run:  python3 grouping_is_a_choice_py.py
"""


def bits(data: bytes) -> str:
    """The whole input as one run of binary digits, no separators anywhere."""
    return "".join(f"{b:08b}" for b in data)


def group(data: bytes, width: int, base: int = 2) -> str:
    """Cut the BIT stream into width-bit pieces. The last piece may be short."""
    stream = bits(data)
    pieces = [stream[i : i + width] for i in range(0, len(stream), width)]
    if base == 2:
        return " ".join(pieces)
    return " ".join(f"{int(p, 2):0{-(-len(p) // 4)}x}" for p in pieces)


WIDTHS = [
    (4, "a hex digit (a nibble)"),
    (5, "a Base32 character"),
    (6, "a Base64 character"),
    (8, "a byte"),
    (16, "a UTF-16 code unit"),
    (24, "Base64's quantum, or an RGB pixel"),
    (32, "a UTF-32 code unit"),
]


def main() -> None:
    word = "café".encode("utf-8")

    print("1. THE SPACES ARE NOT IN THE FILE")
    print(f"   {word!r} is {len(word)} bytes = {len(word) * 8} bits, and that never changes.")
    print(f"   ungrouped   {bits(word)}")
    print(f"   as hex      {group(word, 8, base=16)}")
    print("   Same file. The separators below are all this program's opinion.")
    print()

    print("2. THE WIDTH YOU PICK IS A CLAIM ABOUT THE UNIT")
    for width, what in WIDTHS:
        shown = group(word, width, base=16 if width % 4 == 0 else 2)
        print(f"   {width:>2} bits = {what:<33} {shown}")
    print("   A width that is not a multiple of 4 has no whole number of hex digits,")
    print("   so those two rows had to be shown in binary. That is not a preference.")
    print()

    print("3. THE GROUPS ARE CUT FROM BITS, NOT FROM BYTES")
    stream = bits(word)
    print(f"   bytes    {' '.join(f'{b:08b}' for b in word)}")
    print(f"   5 bits   {group(word, 5)}")
    print(f"   The second 5-bit group is {stream[5:10]}: the last {len(stream[5:8])} bits of "
          f"{word[0]:#04x} ({stream[5:8]})")
    print(f"   followed by the first {len(stream[8:10])} bits of {word[1]:#04x} ({stream[8:10]}).")
    print("   It belongs to two bytes and to no character at all.")
    print()

    print("4. NOTHING IS PADDED: A SHORT LAST GROUP IS JUST SHORT")
    for width in (16, 24, 32):
        pieces = [len(p) for p in group(word, width).split(" ")]
        print(f"   {width:>2} bits: {len(pieces)} groups, sizes {pieces} -> last one holds "
              f"{pieces[-1]} bits")
    print("   Base64 does the opposite: it pads the last quantum to 24 bits and writes")
    print("   '=' to say how much it added, because there the groups are the encoding.")
    print("   Here they are only the view, so the tail is left ragged.")
    print()

    print("5. ALIGNMENT IS NOT UNDERSTANDING")
    print("   Grouping by 4 bytes will sometimes put a 4-byte character in one group.")
    print("   That is arithmetic about its offset, not knowledge of UTF-8.")
    emoji = "😀".encode("utf-8")
    for pad in range(8):
        data = b"~" * pad + emoji
        start = pad
        contained = start % 4 == 0
        print(f"   offset {start} ({start} % 4 = {start % 4}): {group(data, 32, base=16):<28} "
              f"{'the whole character in one group' if contained else 'split across two groups'}")
    print("   One character earlier in the file and the picture changes. The tool never knew.")
    print()

    print("6. IN PYTHON THE SIGN IS THE DIRECTION")
    print(f"   word.hex(' ', -2)  {word.hex(' ', -2):<20} pairs from the LEFT, short group last")
    print(f"   word.hex(' ',  2)  {word.hex(' ', 2):<20} pairs from the RIGHT, short group first")
    print("   Positive counts back from the end, which is right for a number and wrong")
    print("   for a stream. A hex dump reads left to right, so it wants the negative.")


if __name__ == "__main__":
    main()
```
<!-- /source -->

<!-- output:grouping_is_a_choice_py -->
*Verified output of [`grouping_is_a_choice_py.py`](examples/grouping_is_a_choice_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE SPACES ARE NOT IN THE FILE
   b'caf\xc3\xa9' is 5 bytes = 40 bits, and that never changes.
   ungrouped   0110001101100001011001101100001110101001
   as hex      63 61 66 c3 a9
   Same file. The separators below are all this program's opinion.

2. THE WIDTH YOU PICK IS A CLAIM ABOUT THE UNIT
    4 bits = a hex digit (a nibble)            6 3 6 1 6 6 c 3 a 9
    5 bits = a Base32 character                01100 01101 10000 10110 01101 10000 11101 01001
    6 bits = a Base64 character                011000 110110 000101 100110 110000 111010 1001
    8 bits = a byte                            63 61 66 c3 a9
   16 bits = a UTF-16 code unit                6361 66c3 a9
   24 bits = Base64's quantum, or an RGB pixel 636166 c3a9
   32 bits = a UTF-32 code unit                636166c3 a9
   A width that is not a multiple of 4 has no whole number of hex digits,
   so those two rows had to be shown in binary. That is not a preference.

3. THE GROUPS ARE CUT FROM BITS, NOT FROM BYTES
   bytes    01100011 01100001 01100110 11000011 10101001
   5 bits   01100 01101 10000 10110 01101 10000 11101 01001
   The second 5-bit group is 01101: the last 3 bits of 0x63 (011)
   followed by the first 2 bits of 0x61 (01).
   It belongs to two bytes and to no character at all.

4. NOTHING IS PADDED: A SHORT LAST GROUP IS JUST SHORT
   16 bits: 3 groups, sizes [16, 16, 8] -> last one holds 8 bits
   24 bits: 2 groups, sizes [24, 16] -> last one holds 16 bits
   32 bits: 2 groups, sizes [32, 8] -> last one holds 8 bits
   Base64 does the opposite: it pads the last quantum to 24 bits and writes
   '=' to say how much it added, because there the groups are the encoding.
   Here they are only the view, so the tail is left ragged.

5. ALIGNMENT IS NOT UNDERSTANDING
   Grouping by 4 bytes will sometimes put a 4-byte character in one group.
   That is arithmetic about its offset, not knowledge of UTF-8.
   offset 0 (0 % 4 = 0): f09f9880                     the whole character in one group
   offset 1 (1 % 4 = 1): 7ef09f98 80                  split across two groups
   offset 2 (2 % 4 = 2): 7e7ef09f 9880                split across two groups
   offset 3 (3 % 4 = 3): 7e7e7ef0 9f9880              split across two groups
   offset 4 (4 % 4 = 0): 7e7e7e7e f09f9880            the whole character in one group
   offset 5 (5 % 4 = 1): 7e7e7e7e 7ef09f98 80         split across two groups
   offset 6 (6 % 4 = 2): 7e7e7e7e 7e7ef09f 9880       split across two groups
   offset 7 (7 % 4 = 3): 7e7e7e7e 7e7e7ef0 9f9880     split across two groups
   One character earlier in the file and the picture changes. The tool never knew.

6. IN PYTHON THE SIGN IS THE DIRECTION
   word.hex(' ', -2)  6361 66c3 a9         pairs from the LEFT, short group last
   word.hex(' ',  2)  63 6166 c3a9         pairs from the RIGHT, short group first
   Positive counts back from the end, which is right for a number and wrong
   for a stream. A hex dump reads left to right, so it wants the negative.
```
<!-- /output -->

Section 6 is a real trap and not only a demonstration. `bytes.hex(sep, bytes_per_sep)` takes the group width as a *signed* number, and the sign is the direction: negative groups from the left, positive from the right. Positive is the sensible default for a number — you want the low-order digits grouped consistently, the way a thousands separator works — and it is the wrong one for a stream, where the short group lands at the front:

```python
"café".encode().hex(" ", -2)   # '6361 66c3 a9'  — left, short group last
"café".encode().hex(" ", 2)    # '63 6166 c3a9'  — right, short group first
```

Both are five bytes and both are correct. Only one of them is a hex dump.

## In Rust

<!-- output:grouping_is_a_choice_rs -->
*Verified output of [`grouping_is_a_choice_rs.rs`](examples/grouping_is_a_choice_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
input: "café", 5 bytes

1. chunks(4) HANDS YOU A SHORT ONE AND SAYS NOTHING
   chunk 0: 636166c3 4 bytes
   chunk 1: a9       1 bytes
   Every chunk has type &[u8]. The last one is a different size and the
   type cannot say so, which is exactly how a tail gets processed twice
   or read past the end.

2. chunks_exact(4) REFUSES TO GIVE YOU A SHORT ONE
   chunk 0: 636166c3 4 bytes
   remainder: a9       1 bytes
   The leftover did not vanish; it moved to a method you have to call.
   Forgetting it is now visible in the code rather than in the output.

3. THE FORGETTING, SIDE BY SIDE
   bytes seen via chunks(4)        5  (all of them)
   bytes seen via chunks_exact(4)  4  (one short of the file)
   Same loop, same width, one byte of café silently missing.

4. THERE IS NO BIT-LEVEL CHUNKER, AND THAT IS HONEST
   std groups &[u8]: the smallest thing it can hand you is one byte.
   A 5-bit group (Base32) or a 6-bit group (Base64) is not a subslice of
   anything, so you shift it out yourself:
   six-bit groups: [24, 54, 5, 38, 48, 58, 36]
   Note the last one had to be filled out to six bits to exist at all.
   That fill is what Base64's '=' is there to declare.
```
<!-- /output -->

`chunks` and `chunks_exact` are the same grouping with the ragged tail moved from the output to the type. `chunks(4)` hands you a short final `&[u8]` that looks like every other chunk; `chunks_exact(4)` never does, and the leftover is a `remainder()` you have to go and ask for. Section 3 shows the cost of forgetting: the same loop, the same width, and one byte of `café` silently absent from the count.

Section 4 is the honest limit. `std` groups `&[u8]`, so the narrowest thing it can hand you is one byte — a 5- or 6-bit group is not a subslice of anything and has to be shifted out by hand. Worth checking the numbers it prints against the [Base64 worked example](../../03_Encodings/binary_to_text/README.md): the first four six-bit groups of `café` come out `24 54 5 38`, which is `Y2Fm`, the same four characters that page derives with a pencil.

## In the terminal

<!-- output:grouping_is_a_choice_sh -->
*Verified output of [`grouping_is_a_choice_sh.sh`](examples/grouping_is_a_choice_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE DEFAULT IS TWO BYTES PER GROUP, AND IT IS A DEFAULT, NOT THE FILE

$ printf "caf\\xc3\\xa9" | xxd
00000000: 6361 66c3 a9                             caf..

2. -g SETS THE GROUP WIDTH IN BYTES. Same five bytes every time.

$ printf "caf\\xc3\\xa9" | xxd -g1
00000000: 63 61 66 c3 a9                                   caf..

$ printf "caf\\xc3\\xa9" | xxd -g4
00000000: 636166c3 a9                          caf..

$ printf "caf\\xc3\\xa9" | xxd -g8
00000000: 636166c3a9                         caf..

3. -g0 ASKS FOR NO GROUPING AT ALL

$ printf "caf\\xc3\\xa9" | xxd -g0
00000000: 636166c3a9                        caf..

4. -c IS A DIFFERENT KNOB: bytes per LINE, not per group

$ printf "caf\\xc3\\xa9" | xxd -g1 -c 3
00000000: 63 61 66  caf
00000003: c3 a9     ..
   Two lines now, and the offset column counts in bytes as always.

5. THE LAST GROUP IS SHORT. Nothing is padded and nothing says so.

$ printf "caf\\xc3\\xa9" | xxd -g4
00000000: 636166c3 a9                          caf..
   Groups of four over five bytes: 636166c3 then a9 alone. The a9 is not a
   short group of its own kind -- it is the tail, and only counting tells you.

6. hexdump -e IS THE GENERAL FORM: you write the grouping out

$ printf "caf\\xc3\\xa9" | hexdump -e '4/1 "%02x" " "' -e '"\n"'
636166c3 
a9       
   4/1 means four iterations of one byte. Change the 4 and you have changed
   the claim about what this file is made of.
```
<!-- /output -->

`xxd -g` is the group width in bytes and `-c` is the line width — two knobs that are easy to confuse because both change where the spaces are. `-g0` asks for no grouping at all. `hexdump -e '4/1 "%02x" " "'` is the general form: *four iterations of one byte*, written out, which is what every other tool's grouping flag is a preset for. Every command on this page is byte-identical on macOS and `ubuntu:24.04`, which is not true of much else in `hexdump` — see [the six presets](../../11_Tools/hexdump/README.md) for the ones that differ, and [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) for what else that tool does with the columns once you stop trusting them.

## If you are coming from Python or ABAP

**Python.** The whole of this page is one habit: when you print bytes for a human, `bytes.hex(' ', -2)` and be explicit, rather than accepting whatever a tool's default grouping implies. The negative sign is the tell that you thought about it. And if you are writing the dump yourself — as [Reading a hex dump](../reading_a_hex_dump/README.md) does in ten lines — the group width is a parameter you are choosing on the reader's behalf; name it in the output if it is not one byte.

**ABAP.** The debugger's `xstring` view is ungrouped: a run of hex digits with no spaces at all, which is the one presentation that makes no claim. That is a feature when you are trying to see what is really there, and a nuisance the moment you are counting — so the habit that transfers is to count in *pairs* deliberately rather than trusting the eye, and to convert with `cl_abap_codepage=>convert_to( )` before arguing about whose bytes are wrong. ABAP's own width claims live in the type: `x` is one byte, `xstring` is a run of them, and there is nothing in the language that will group them four at a time for you. *(Not machine-checked — CI cannot run ABAP.)*

## Try it

```bash
cd 01_Bits_and_Bytes/grouping_is_a_choice/examples
python3 grouping_is_a_choice_py.py
bash grouping_is_a_choice_sh.sh
rustc --edition 2024 grouping_is_a_choice_rs.rs && ./grouping_is_a_choice_rs
```

Then take a file of your own and dump it at three widths: `xxd -g1 f | head`, `xxd -g2 f | head`, `xxd -g4 f | head`. Nothing about the file changed. Decide which of the three you would paste into a bug report, and why.

## Practice

**Thirteen bytes, three widths.** `printf 'thirteen byte' > f` makes a 13-byte file. Before running anything, say how many groups `xxd -g1`, `xxd -g2` and `xxd -g4` will each put on the line, and — for the two that cannot divide 13 evenly — where the ragged piece falls and what `xxd` does about it. Then say which byte of the file changed between the three dumps.

<details markdown="1">
<summary><strong>Answers</strong></summary>

<!-- output:grouping_is_a_choice_kata_sh -->
*Verified output of [`grouping_is_a_choice_kata_sh.sh`](examples/grouping_is_a_choice_kata_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
THE FILE: 13 bytes, and 13 is prime to 2 and 4
$ wc -c < f
   13

$ xxd -g1 f
   00000000: 74 68 69 72 74 65 65 6e 20 62 79 74 65           thirteen byte
   -> 13 group(s) on the line, of 1 byte(s) each

$ xxd -g2 f
   00000000: 7468 6972 7465 656e 2062 7974 65         thirteen byte
   -> 7 group(s) on the line, of 2 byte(s) each

$ xxd -g4 f
   00000000: 74686972 7465656e 20627974 65        thirteen byte
   -> 4 group(s) on the line, of 4 byte(s) each

WHAT CHANGED IN THE FILE: nothing. Thirteen bytes, three renderings.

WHERE THE TAIL FALLS. 13 = 16-3, so the line is short whatever the width,
and the last group is the one that cannot be full:
  -g1  the tail is 13 whole groups; a group is a byte, so nothing is ragged.
  -g2  six pairs and then a single byte. 13 is odd, so the last group is
       half a group, and xxd prints it as one byte rather than padding it.
  -g4  three quads and then ONE byte -- 12 + 1. The ragged piece is three
       bytes short of the width you asked for.

Nothing is padded, and that is the honest choice: a 00 added to square the
line would be a byte the file does not contain, printed in the column
whose whole job is to say what the file contains.

And the width is a CLAIM. -g2 says 'read this as 16-bit units'; -g4 says
32-bit. For a text file all three claims are wrong and it does not matter,
because the bytes are drawn in file order either way. It starts mattering
the moment a tool reorders within a group to keep the claim true -- which
is what hexdump's -x does and xxd never does.
```
<!-- /output -->

</details>

## See also

- [Reading a hex dump](../reading_a_hex_dump/README.md) — the three columns this page takes apart
- [Hex is a shorthand](../hex_is_a_shorthand/README.md) — why four bits is one digit, which is why 5 and 6 have nowhere to go
- [Binary to text](../../03_Encodings/binary_to_text/README.md) — the same re-cutting, done for real, where the padding has to be declared
- [`hexdump` is a format engine wearing six presets](../../11_Tools/hexdump/README.md) — grouping as a format string, and the presets that hide it
- [`xxd` is the dump you can put back](../../11_Tools/xxd/README.md) — the tool this page leans on, and the only dump that reverses
- [Inspecting a file](../../06_Terminal/inspecting_a_file/README.md) — the other tools that answer a neighbouring question in silence
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — the rest of Python's byte-reading toolkit
