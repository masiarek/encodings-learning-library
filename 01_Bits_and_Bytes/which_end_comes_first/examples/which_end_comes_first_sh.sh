#!/usr/bin/env bash
# One file, six dumps, two different numbers. Which of them is the file?
#
# Run:  bash which_end_comes_first_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od and hexdump pad their lines differently on macOS (BSD) and Linux (GNU), and
# the padding is not the lesson. `squeeze` collapses every run of spaces to one
# and trims the ends, so the same bytes give the same picture on both. The groups
# survive, which is the whole point here -- unlike the width-padding helper the
# other shell examples use, this one must not join two groups into one word.
squeeze() { sed -e 's/  */ /g' -e 's/^ //' -e 's/ *$//' -e '/^$/d'; }

d=$(mktemp -d)
cd "$d"
trap 'rm -rf "$d"' EXIT
printf '\x2f\x75\x05' > three.bin
printf '\x2f\x75\x05\x00' > four.bin

echo "1. THE FILE: three bytes, and nothing on this page will change them"
show "xxd three.bin"
echo "   2f 75 05. That is the whole file. Ask what NUMBER it is and there are two"
echo "   answers, because a file records bytes and never records which end is the"
echo "   big one:"
echo "      0x2f7505 = 3110149   most significant byte first  (big-endian)"
echo "      0x05752f =  357679   least significant byte first (little-endian)"
echo "   Neither is a misreading. The question did not exist until you asked for a"
echo "   number, and the file does not answer it."

echo
echo "2. FOUR BYTES THROUGH SIX TOOLS -- same file every time"
echo "   (a fourth byte 00, so a 32-bit reading is a whole group; every dump here"
echo "   goes through squeeze, so the six are comparable and so the two xxd builds"
echo "   agree -- they pad a short line's trailing space differently)"
show "xxd four.bin | squeeze"
show "xxd -e -g 4 four.bin | squeeze"
show "od -An -tx1 four.bin | squeeze"
show "od -An -x four.bin | squeeze"
show "hexdump four.bin | squeeze"
show "hexdump -C four.bin | squeeze"

echo
echo "3. READ THAT COLUMN AGAIN"
echo "      xxd            2f75 0500     the file"
echo "      xxd -e -g 4    0005752f      ONE 32-bit little-endian number"
echo "      od -An -tx1    2f 75 05 00   the file"
echo "      od -An -x      752f 0005     TWO 16-bit numbers, this CPU's order"
echo "      hexdump        752f 0005     the same, and it is the DEFAULT"
echo "      hexdump -C     2f 75 05 00   the file"
echo
echo "   Three of the six printed the file. Three printed numbers -- and 0005752f"
echo "   is 0x05752f, the little-endian reading from section 1, with the leading"
echo "   zero byte still on it. The setting a hex editor puts in its status bar is"
echo "   the same setting; on the command line it is a flag you may not know you"
echo "   set, and on a bare hexdump it is one you never chose at all."

echo
echo "4. SO WHICH DUMP IS THE FILE?"
echo "   The ones that never group into a number: xxd, od -tx1, hexdump -C."
echo "   Those three print the same bytes on every machine ever built. The other"
echo "   three print a picture of this CPU's opinion, and on a big-endian machine"
echo "   the same three commands would print something else."
