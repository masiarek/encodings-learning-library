#!/usr/bin/env bash
# Hex is binary written four bits at a time. The shell speaks all three bases.
#
# Run:  bash hex_is_a_shorthand_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od lays its columns out differently on macOS (BSD) and Linux (GNU): BSD keeps a
# blank address column under -An, pads every line, and left-aligns the -c row
# where GNU right-aligns it. `tidy` re-prints every field four wide, so the same
# bytes give the same picture on both. One limit: a SPACE byte prints as blanks
# under -c and would vanish, so these examples feed od inputs with no spaces.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

echo "1. printf CONVERTS BETWEEN BASES"
show "printf '%x\\n' 65          # decimal in, hex out"
show "printf '%02X\\n' 5         # two digits, uppercase"
show "printf '%d\\n' 0x41        # hex in, decimal out"

echo
echo "2. BASH ARITHMETIC DOES KNOW EVERY BASE: base#digits"
show "echo \$(( 16#41 ))  \$(( 2#01000001 ))  \$(( 8#101 ))"

echo
echo "3. THE PICTURE VERSUS THE THING"
show "printf '41' | xxd            # the TEXT 41: two bytes, 0x34 and 0x31"
show "printf '\\x41' | xxd          # the BYTE 0x41: one byte, shown as 41, read as A"
