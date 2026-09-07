#!/usr/bin/env bash
# Answer key: read the three columns off a file whose bytes are known.
#
# The kata gives you a dump and asks four questions about it. The file is
# written here with printf, so every byte in the answer is one somebody put
# there on purpose -- including the two that the right-hand column refuses to
# draw.
#
# Run:  bash reading_a_hex_dump_kata_sh.sh
set -eu

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'Hi\tthere\n\303\251\007ok\n' > f

echo "\$ xxd f"
xxd f | sed 's/^/   /'
echo
echo "1. WHERE ARE THE NEWLINES?"
echo "   Offsets 09 and 0f, both 0a. The right-hand column draws each as a dot,"
echo "   which is the column telling you it has nothing to draw rather than the"
echo "   file containing a dot."
echo
echo "2. THE FIRST BYTE SHOWN AS A DOT"
first=$(xxd -p f | fold -w2 | grep -n -m1 -v -E '^(2[0-9a-e]|[3-6][0-9a-f]|7[0-9a-e])$' | cut -d: -f2)
printf '   %s -- at offset 02, the tab.\n' "0x$first"
echo "   It is a real byte, 09, and it is the reason the words on that line are"
echo "   spaced the way they are. The dot is the dump's placeholder for every"
echo "   byte outside 20..7e, so a dot never means 'a dot'."
echo
echo "3. HOW MANY BYTES DOES THE LETTER MAKE?"
echo "   Two: c3 a9 at offsets 0a and 0b, one letter e-acute. The text column"
echo "   draws two dots for them, side by side, because it decodes nothing --"
echo "   it tests each byte against ASCII on its own. A dump cannot show you a"
echo "   character; it can only show you the bytes one is spelled with."
echo
echo "4. THE BYTE THAT IS NOT A LETTER AND NOT A NEWLINE"
echo "   07 at offset 0c, BEL. Printed to a terminal it would make a sound and"
echo "   move the cursor nowhere -- which is exactly why cat is not a way to"
echo "   look at a file and xxd is."
echo
echo "THE THREE COLUMNS, RESTATED"
printf '   %-10s %s\n' "left" "the offset, in hex, of the first byte on the line"
printf '   %-10s %s\n' "middle" "the bytes, and this is the file"
printf '   %-10s %s\n' "right" "a guess: ASCII where it can, a dot where it cannot"
echo "   Only the middle column is the file. The left one is counting and the"
echo "   right one is a courtesy that has already thrown information away."
