#!/usr/bin/env bash
# xxd is the only dump on your machine that goes backwards — and the half of it
# you are most tempted to edit is the half it throws away on the way back.
#
# Everything here is byte-identical on macOS and Ubuntu. It is the same program
# on both: xxd ships with vim, so there is one implementation, not two.
#
# Run:  bash xxd_goes_both_ways_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251: 1\342\202\254\n' > s.txt   # café: 1€ — 9 characters, 12 bytes
head -c 64 /dev/zero > zeros.bin
python3 -c "import sys; sys.stdout.buffer.write(b'A'*80 + b'END\n')" > runs.bin

echo "1. THE DEFAULT VIEW, AND WHY IT LOOKS LIKE THAT"
show "xxd s.txt"
echo "   Offset in hex, then the bytes in PAIRS, then the same bytes as ASCII."
echo "   The pairing is cosmetic — xxd is not reading two-byte numbers the way"
echo "   a bare hexdump does; 6361 is byte 63 then byte 61, in file order. -g"
echo "   changes the grouping and -c the line width:"
show "xxd -g 1 -c 8 s.txt"

echo
echo "2. IT IS THE ONLY ONE HERE THAT PRINTS BITS"
show "xxd -b -c 4 s.txt"
echo "   Eight ones and zeros per byte. od and hexdump have octal and decimal"
echo "   views; neither has this one."

echo
echo "3. THE ONE THAT GOES BACK"
show "xxd s.txt > dump.txt; xxd -r dump.txt > back.txt; cmp s.txt back.txt && echo 'identical'"
echo "   A dump is not just a picture here: it is a representation you can put"
echo "   back. That round trip is the reason xxd ships with vim — :%!xxd, edit,"
echo "   :%!xxd -r, and you have edited a binary in a text editor."

echo
echo "4. AND THE HALF IT THROWS AWAY"
echo "   The text column is NOT the file. Overwrite it and reverse the dump:"
show "sed 's/caf\\.\\.: 1/OVERWRITTEN/' dump.txt"
show "sed 's/caf\\.\\.: 1/OVERWRITTEN/' dump.txt | xxd -r"
echo "   Nothing changed. xxd -r reads the hex and ignores everything after it,"
echo "   which is the strongest demonstration in this library that the right-hand"
echo "   column is the tool talking, not the file. Change a byte in the HEX and"
echo "   it lands — 63 is 'c', 43 is 'C':"
show "sed 's/: 6361/: 4361/' dump.txt | xxd -r"

echo
echo "5. THE OFFSET IS AN INSTRUCTION, NOT A LABEL"
echo "   xxd -r SEEKS to the offset each line names. So deleting a line does not"
echo "   shorten the file — it leaves a hole, and a hole is NUL bytes:"
show "xxd runs.bin | sed -n '1,3p'"
show "xxd runs.bin | sed '2d' | xxd -r | xxd | sed -n '1,3p'"
echo "   Same length, different contents, no complaint. Line 2 came back as"
echo "   zeros, because xxd -r never saw an instruction to write anything at"
echo "   offset 10 and the file system gives you zeros for a gap. Editing a dump"
echo "   by hand is safe as long as you change characters in place and never add"
echo "   or remove a line."

echo
echo "6. -p: THE INTERCHANGE FORM, AND ITS INVERSE"
show "xxd -p s.txt"
show "xxd -p s.txt | xxd -r -p | cat"
echo "   No offsets, no text column, no line structure — just the bytes as hex,"
echo "   which is the form every other tool will take from you. The reverse is"
echo "   whitespace-tolerant, so hex you pasted out of a bug report works:"
show "printf '63 61 66\n65\n' | xxd -r -p"

echo
echo "7. AUTOSKIP COLLAPSES NUL RUNS — AND ONLY NUL RUNS"
show "xxd -a zeros.bin"
show "xxd -a runs.bin | sed -n '1,3p'"
echo "   64 zero bytes collapse to a *. Eighty identical 'A' bytes do not."
echo "   That is the difference from hexdump and od, whose * collapses ANY"
echo "   repeated line: xxd's -a is documented as replacing nul-lines, and it"
echo "   means it. It is also why -a survives a round trip — the lines it drops"
echo "   are zeros, and the hole xxd -r leaves is filled with zeros:"
show "xxd -a zeros.bin | xxd -r | cmp - zeros.bin && echo 'identical'"

echo
echo "8. THE TEXT COLUMN HAS A SWITCH, AND NOTHING ELSE HERE DOES"
show "xxd s.txt"
show "xxd -E s.txt"
echo "   The same twelve bytes, twice. The hex column is identical — it is the"
echo "   file. The right-hand column changed completely, because -E reads the"
echo "   bytes as EBCDIC instead of ASCII, and in EBCDIC 61 is '/', c3 is 'C'"
echo "   and e2 is 'S'. Neither column is more true than the other. A text"
echo "   column is an AGREEMENT being applied, and this flag is the only place"
echo "   in any of these tools where you get to say which agreement."

echo
echo "9. -i: THE FILE AS SOURCE CODE"
show "xxd -i s.txt"
echo "   The variable name comes from the filename. -i is how a font, an icon or"
echo "   a test fixture gets compiled into a C program with no file to ship."

echo
echo "10. WHAT IS NOT HERE"
echo "   -e prints little-endian GROUPS — 63 61 66 c3 as c3666163, which is what"
echo "   a bare hexdump does to every pair without being asked. It is not in this"
echo "   run because the two xxd versions pad its short last group by different"
echo "   amounts; the page shows both, dated. Reach for it when you are reading"
echo "   32-bit values, not when you want to see the file."
