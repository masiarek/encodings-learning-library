#!/usr/bin/env bash
# Kata answers: 01 00 00 00, four ways, and which two answers are about the file.
#
# Run:  bash which_end_comes_first_kata_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
squeeze() { sed -e 's/  */ /g' -e 's/^ //' -e 's/ *$//' -e '/^$/d'; }

d=$(mktemp -d)
cd "$d"
trap 'rm -rf "$d"' EXIT
printf '\x01\x00\x00\x00' > one.bin

echo "THE FILE: four bytes, 01 00 00 00"
show "wc -c < one.bin | squeeze"

echo
echo "1 and 2. THE TWO INTEGER READINGS"
show "python3 -c \"b=open('one.bin','rb').read(); print('big   ', int.from_bytes(b,'big')); print('little', int.from_bytes(b,'little'))\""
echo "   big-endian     16777216   = 0x01000000"
echo "   little-endian         1   = 0x00000001"
echo "   The same four bytes are sixteen million or one -- a factor of 2^24, which"
echo "   is the largest ratio two readings of four bytes can have (all the weight"
echo "   in the first byte and none anywhere else, which is this file). That is"
echo "   why 01 00 00 00 is the pattern to keep in your head: when a length field"
echo "   reads 16777216 and the file is 200 bytes long, you have not found a"
echo "   corrupt file, you have found the other end."

echo
echo "3. WHAT A BARE hexdump PRINTS"
show "hexdump one.bin | squeeze"
echo "   0001 0000 -- two 16-bit numbers in this CPU's order, not the file. The"
echo "   first group is 0x0001, made from the bytes 01 00."

echo
echo "4. WHAT xxd PRINTS"
show "xxd one.bin | squeeze"
echo "   0100 0000 -- the file, in file order, grouped into pairs and reordered"
echo "   by nothing. Compare it with answer 3 character by character: same four"
echo "   bytes, same tool family, and the groups are not the same number."

echo
echo "5. WHICH OF THE FOUR WOULD CHANGE ON A BIG-ENDIAN MACHINE"
echo "   Only answer 3."
echo
echo "      1 and 2   facts about the FILE. int.from_bytes names its order, so"
echo "                both numbers are the same on every machine ever built."
echo "      4         a fact about the FILE. xxd never reorders."
echo "      3         a fact about the MACHINE. A bare hexdump reads two bytes"
echo "                at a time as a number and prints it in the host's order,"
echo "                so on a big-endian host the same command prints 0100 0000."
echo
echo "   Two of the four are the file and two are not, and nothing in the"
echo "   printout says which is which. That is the whole lesson: the dump you"
echo "   paste into a bug report should be one of the ones that cannot lie."
