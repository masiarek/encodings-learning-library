#!/usr/bin/env bash
# od's interface is a C TYPE, not a layout. -t x1 is "hexadecimal, one byte at
# a time"; change either half and you get a different reading of the same file.
# That is why its default prints 16-bit octal words, and why it can print one
# input several ways in a single pass.
#
# Every od block here goes through `tidy`, and section 9 says why: od is the one
# tool in this chapter whose two implementations lay their columns out
# differently, so an untidied answer key could not match both machines.
#
# Run:  bash od_reads_types_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# Re-print every field separated by exactly one space, and drop blank lines.
# BSD od indents, pads a short line out to full width and adds a trailing blank
# line; GNU od does none of it. The fields are untouched — only the space
# between them is. (A fixed column width cannot be used here the way the other
# shell examples do: od's fields run from 2 characters under -t x1 to 11 under
# -t dI, and a width that suits one runs the other together.)
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%s%s", (i > 1 ? " " : ""), $i; print "" }' | sed -e '/^$/d'; }
# The same, but four wide, for the one section where two rows have to line up
# under each other. It needs -A n: with an offset column the second row is one
# field short and the columns slide.
cols() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251: 1\342\202\254\n' > s.txt      # café: 1€ — 9 characters, 12 bytes
printf 'caf\303\251=1\342\202\254\n' > nospace.txt # the same, with = for ': ' — see section 6
head -c 64 /dev/zero > zeros.bin

echo "1. TWO NUMBER BASES NOBODY ASKED FOR"
show "od s.txt | tidy"
echo "   Twelve bytes, and not one of them is on screen. The default type is"
echo "   -t o2: SIX 16-bit words, printed in octal. And the offsets are octal"
echo "   too, so the last line says 0000014 for a 12-byte file — 14 octal is 12."
echo "   Two number bases, neither of them stated, in the output of the only"
echo "   dump tool a stripped-down machine is guaranteed to have."

echo
echo "2. THE INCANTATION"
show "od -An -tx1 s.txt | tidy"
echo "   -A n drops the offset column, -t x1 says hexadecimal one byte at a"
echo "   time. Those twelve numbers ARE the file. If you remember one od"
echo "   command, remember this one."

echo
echo "3. -A PICKS THE RADIX OF THE OFFSET COLUMN"
show "od -Ad -tx1 s.txt | tidy"
show "od -Ao -tx1 s.txt | tidy"
echo "   d for decimal, o for octal (the default), n for none. There is an x"
echo "   for hex too, and it is the one thing on this page that is not the same"
echo "   width on both machines — the page has that measurement."

echo
echo "4. -t IS A TYPE: A LETTER AND A SIZE"
echo "   The letter is how to print it, the number is how many bytes that is."
show "od -An -tx1 s.txt | tidy"
show "od -An -tu1 s.txt | tidy"
show "od -An -tx2 s.txt | tidy"
show "od -An -tx4 s.txt | tidy"
echo "   Same twelve bytes, four readings. x1 and u1 are the same bytes in two"
echo "   bases. x2 and x4 group them into 16- and 32-bit numbers and print each"
echo "   number in THIS CPU's byte order, which is why 63 61 becomes 6163 and"
echo "   63 61 66 c3 becomes c3666163. Grouping is a claim about the file."

echo
echo "5. AND IT WILL READ YOUR TEXT AS ANYTHING YOU NAME"
show "od -An -td2 s.txt | tidy"
echo "   The same bytes as SIGNED 16-bit integers. c366 is 50022 unsigned and"
echo "   -15514 signed, and od printed the second one because you asked for d."
show "od -An -tdI s.txt | tidy"
echo "   Sizes have letters as well as numbers: C is a char, S a short, I an"
echo "   int, L a long. -t dI is three signed ints, because twelve bytes is"
echo "   three of them. There is -t f4 and -t f8 for floating point as well,"
echo "   and od will happily tell you what your CSV is as a run of doubles."
echo "   Nothing here is a bug: od is doing exactly what a C cast does, which"
echo "   is what the tool was built for."

echo
echo "6. SEVERAL READINGS IN ONE PASS — THE THING ONLY od DOES"
show "od -An -tx1 -tc nospace.txt | cols"
echo "   Two -t flags, two rows for every line of input, each byte's hex sitting"
echo "   directly above what it is as a character. hexdump needs three -e"
echo "   strings to line those up and xxd cannot do it at all. Add a third -t"
echo "   and you get a third row:"
show "od -An -tx1 -tu1 -tc nospace.txt | cols"
echo "   (These two use '=' where the demo file has ': ' — under -t c a space"
echo "   byte prints as blanks, which the column helper cannot tell apart from"
echo "   padding. That is a limit of the helper, not of od.)"

echo
echo "7. A WINDOW INTO A BIG FILE"
show "od -Ad -j 2 -N 4 -tx1 s.txt | tidy"
echo "   -j skips, -N stops. The offsets keep counting from the front of the"
echo "   file, so what you read is the address in the file and not in the"
echo "   window — which is what you want when you are quoting it to someone."

echo
echo "8. THE STAR, WHICH od SHARES WITH hexdump"
show "od -Ad -tx1 zeros.bin | tidy"
echo "   64 bytes in, one line out. A * means the line above repeats. -v turns"
echo "   it off, and anything parsing od's output needs -v:"
show "od -Ad -v -tx1 zeros.bin | tidy | wc -l | tr -d ' '"
echo "   ^ five: four lines of sixteen bytes, plus the final offset line."

echo
echo "9. WHY EVERY BLOCK ABOVE ENDS IN | tidy"
echo "   Because the raw output cannot be recorded. BSD od indents, pads a short"
echo "   line out to the width a full 16-byte line would take, and adds a"
echo "   trailing blank line; GNU od does none of that, and its own indent is"
echo "   not constant between formats either. The NUMBERS agree on both"
echo "   machines. Nothing else does — so od output is the one thing in this"
echo "   chapter you cannot quote without saying which machine it came from,"
echo "   and the page shows both raw versions side by side rather than this"
echo "   script pretending there is one answer."
