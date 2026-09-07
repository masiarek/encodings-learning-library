#!/usr/bin/env bash
# The shell has exactly one integer width, and no way to ask for another.
#
# Run:  bash arithmetic_has_its_own_width_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

echo "1. THE SHIFT THAT LEAVES THE BYTE, AND NOTHING NOTICES"
show "echo \$(( 255 << 2 ))          # 1111 1111 shifted twice -- ten bits now"
show "echo \$(( (255 << 2) & 0xFF )) # the byte answer, masked by hand"
echo "   There is no byte in this script. \$(( )) has one integer type, and the only"
echo "   way to say 'eight bits' is to write the mask yourself."

echo
echo "2. WHICH DIVISION THE SHELL CHOSE"
show "echo \$(( -5 / 8 ))            # rounds toward zero"
show "echo \$(( -5 % 8 ))            # so the remainder is negative"
show "echo \$(( -5 >> 3 ))           # rounds down: a shift is not a division here either"
echo "   The shell follows C, not Python. That is not a coincidence: \$(( )) is C"
echo "   arithmetic, evaluated with the host's own integer operators."

echo
echo "3. THE BASE IS NOT A TYPE"
show "x=0xFF; echo \$(( x + 1 ))     # hex in, decimal out, no declaration anywhere"
show "echo \$(( 2#11111111 + 1 ))    # base#digits is the shell's own spelling for binary"
show "z=010; echo \$(( z + 1 ))      # and a LEADING ZERO means octal, so 010 is 8"
echo "   Three literals, three bases, one type. The last one is the trap: a zero-padded"
echo "   number out of a log file or a date becomes octal without being asked, and 08"
echo "   is then an error rather than eight."

echo
echo "4. THE WIDTH APPEARS ONLY WHERE THE NUMBER BECOMES BYTES"
show "echo \$(( 255 << 2 ))                      # the shell's answer, as a number"
show "printf '%d' \$(( 255 << 2 )) | xxd         # written out as text: four bytes"
show "printf '\\374' | xxd                       # written out as the byte 252: one byte"
echo "   Same value, four bytes and one, and only the last two commands ever had"
echo "   to know how wide anything was. That boundary is where Python makes you"
echo "   call to_bytes() and where a C declaration made the choice long before."
