#!/usr/bin/env bash
# One file, six groupings. The bytes never move; only the spaces do.
#
# Run:  bash grouping_is_a_choice_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# Five bytes, so no grouping wider than one byte divides evenly.
CAFE='printf "caf\\xc3\\xa9"'

echo "1. THE DEFAULT IS TWO BYTES PER GROUP, AND IT IS A DEFAULT, NOT THE FILE"
show "$CAFE | xxd"

echo
echo "2. -g SETS THE GROUP WIDTH IN BYTES. Same five bytes every time."
show "$CAFE | xxd -g1"
show "$CAFE | xxd -g4"
show "$CAFE | xxd -g8"

echo
echo "3. -g0 ASKS FOR NO GROUPING AT ALL"
show "$CAFE | xxd -g0"

echo
echo "4. -c IS A DIFFERENT KNOB: bytes per LINE, not per group"
show "$CAFE | xxd -g1 -c 3"
echo "   Two lines now, and the offset column counts in bytes as always."

echo
echo "5. THE LAST GROUP IS SHORT. Nothing is padded and nothing says so."
show "$CAFE | xxd -g4"
echo "   Groups of four over five bytes: 636166c3 then a9 alone. The a9 is not a"
echo "   short group of its own kind -- it is the tail, and only counting tells you."

echo
echo "6. hexdump -e IS THE GENERAL FORM: you write the grouping out"
show "$CAFE | hexdump -e '4/1 \"%02x\" \" \"' -e '\"\\n\"'"
echo "   4/1 means four iterations of one byte. Change the 4 and you have changed"
echo "   the claim about what this file is made of."
