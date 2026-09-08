#!/usr/bin/env bash
# Answer key: the preset that reorders your file.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'cafe\n' > f

echo "THE FILE, ONE BYTE AT A TIME"
printf '   %s\n' "$(xxd -p < f)"
echo
echo "hexdump WITH NO FLAGS"
hexdump f | sed 's/^/   /'
echo "   Read the first group: 6163. The file starts 63 61. The two bytes came"
echo "   out SWAPPED -- and so did every other pair."
echo
echo "WHY"
echo "   The default is -x, which reads the file two bytes at a time as a"
echo "   16-BIT NUMBER and prints that number. On a little-endian machine the"
echo "   low byte is stored first, so the number made from 63 61 is 0x6163."
echo "   Nothing is wrong: hexdump printed the integer correctly. It is just"
echo "   not showing you the file."
echo
echo "THE FLAGS THAT DO SHOW YOU THE FILE"
echo "   hexdump -C f"
hexdump -C f | sed 's/^/      /'
echo "   hexdump -e is the same idea written out -- the letter flags are canned"
echo "   format strings, and you can type your own:"
hexdump -e '16/1 "%02x " "\n"' f | sed 's/^/      /'
echo
echo "THE POINT, WHICH IS BIGGER THAN ONE TOOL"
echo "   A dump that groups bytes into a WIDTH has made a claim about what the"
echo "   data's unit is -- and if the claim is wrong, the tool will reorder your"
echo "   bytes to keep it true. hexdump's default claims 16-bit integers; xxd's"
echo "   default claims nothing and never reorders."
echo
echo "   That is the whole reason this library reaches for xxd or hexdump -C in"
echo "   a bug report. A bare hexdump is a picture of your CPU's opinion, and"
echo "   on a big-endian machine the same command would print the bytes in file"
echo "   order -- so the output is not even reproducible across hardware."
