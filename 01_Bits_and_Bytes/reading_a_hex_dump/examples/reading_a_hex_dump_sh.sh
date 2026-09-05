#!/usr/bin/env bash
# Three hex-dump tools, one input. Learn to read the columns.
#
# Run:  bash reading_a_hex_dump_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od pads every line to a fixed width on macOS (BSD) and not on Linux (GNU), and
# prints an empty trailer line on one of them. `tidy` strips both so the recorded
# output is the same on every machine — the bytes it shows are not affected.
tidy() { sed -e 's/[[:space:]]*$//' -e '/^$/d'; }

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
show "printf 'Hi there\\n' | od -An -tx1 -c | tidy"

echo
echo "5. hexdump -C: the third classic; same three columns, |ascii| framed"
show "printf 'Hi there\\n' | hexdump -C"

echo
echo "6. NON-ASCII BYTES: the right-hand column gives up and prints a dot"
show "printf 'caf\\xc3\\xa9\\n' | xxd"
show "printf 'caf\\xc3\\xa9\\n' | od -An -tx1 -c | tidy"
echo "   Four letters, five bytes plus the newline: c a f, then TWO bytes c3 a9 for the e-acute."
echo "   od -c shows those two as octal (303 251) because it has no character to show."
