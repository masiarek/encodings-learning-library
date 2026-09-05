#!/usr/bin/env bash
# Hex is binary written four bits at a time. The shell speaks all three bases.
#
# Run:  bash hex_is_a_shorthand_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od pads every line to a fixed width on macOS (BSD) and not on Linux (GNU), and
# prints an empty trailer line on one of them. `tidy` strips both so the recorded
# output is the same on every machine — the bytes it shows are not affected.
tidy() { sed -e 's/[[:space:]]*$//' -e '/^$/d'; }

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
