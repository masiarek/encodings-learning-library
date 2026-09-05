#!/usr/bin/env bash
# A byte is eight switches. The terminal can show you all eight.
#
# Run:  bash a_byte_is_eight_bits_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od pads every line to a fixed width on macOS (BSD) and not on Linux (GNU), and
# prints an empty trailer line on one of them. `tidy` strips both so the recorded
# output is the same on every machine — the bytes it shows are not affected.
tidy() { sed -e 's/[[:space:]]*$//' -e '/^$/d'; }

echo "1. THE LETTER A, AS THE EIGHT BITS IT IS STORED AS"
show "printf 'A' | xxd -b"

echo
echo "2. THE SAME BYTE AS A DECIMAL, A HEX PAIR, AND A CHARACTER"
show "printf 'A' | od -An -tu1 -tx1 -c | tidy"

echo
echo "3. GOING THE OTHER WAY: WRITE THE BYTE 65 AND LET THE TERMINAL READ IT AS TEXT"
show "printf '\\101'; echo        # octal escape: 101 base 8 = 65"
show "printf '\\x41'; echo        # hex escape:    41 base 16 = 65"

echo
echo "4. BASH ARITHMETIC UNDERSTANDS BASES"
show "echo \$(( 2#01000001 ))"
show "echo \$(( 2#11111111 ))"
show "echo \$(( 2#11111111 + 1 ))    # bash integers are 64-bit: no wrap here"
