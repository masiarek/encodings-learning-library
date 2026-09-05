#!/usr/bin/env bash
# Three hex-dump tools, one input. Learn to read the columns.
#
# Run:  bash reading_a_hex_dump_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od lays its columns out differently on macOS (BSD) and Linux (GNU): BSD keeps a
# blank address column under -An, pads every line, and left-aligns the -c row
# where GNU right-aligns it. `tidy` re-prints every field four wide, so the same
# bytes give the same picture on both. One limit: a SPACE byte prints as blanks
# under -c and would vanish, so these examples feed od inputs with no spaces.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

echo "1. xxd: offset | sixteen bytes in hex, paired | the same bytes as ASCII"
show "printf 'Hi there\\n' | xxd"

echo
echo "2. A LONGER INPUT: the offset column counts bytes, in hex, sixteen per line"
show "printf 'The quick brown fox jumps over it\\n' | xxd"

echo
echo "3. xxd -g1 ungroups the pairs; -c 8 changes the line width"
show "printf 'Hi there\\n' | xxd -g1 -c 8"

echo
echo "4. od: the POSIX tool. -An drops the offset, -tx1 = hex bytes, -c = as characters"
echo "   (a tab instead of the space, so -c has something to show for every byte)"
show "printf 'Hi\\tthere\\n' | od -An -tx1 -c | tidy"

echo
echo "5. hexdump -C: the third classic; same three columns, |ascii| framed"
show "printf 'Hi there\\n' | hexdump -C"

echo
echo "6. NON-ASCII BYTES: the right-hand column gives up and prints a dot"
show "printf 'caf\\xc3\\xa9\\n' | xxd"
show "printf 'caf\\xc3\\xa9\\n' | od -An -tx1 -c | tidy"
echo "   Four letters, five bytes plus the newline: c a f, then TWO bytes c3 a9 for the e-acute."
echo "   od -c shows those two as octal (303 251) because it has no character to show."
