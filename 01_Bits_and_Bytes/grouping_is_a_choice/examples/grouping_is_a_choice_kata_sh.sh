#!/usr/bin/env bash
# Answer key: thirteen bytes at three widths, and where the ragged tail falls.
#
# xxd is the same on both platforms -- it is one program, shipped with vim,
# rather than a BSD/GNU pair -- so this key records its real columns. The file
# is built with printf so its thirteen bytes are stated, not found.
#
# Run:  bash grouping_is_a_choice_kata_sh.sh
set -eu

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'thirteen byte' > f          # 13 bytes, chosen because 13 divides by nothing

echo "THE FILE: 13 bytes, and 13 is prime to 2 and 4"
echo "\$ wc -c < f"
printf '   %s\n' "$(wc -c < f | tr -d ' ')"

for g in 1 2 4; do
  echo
  echo "\$ xxd -g$g f"
  xxd -g"$g" f | sed 's/^/   /'
  groups=$(xxd -g"$g" f | head -1 | sed 's/^[0-9a-f]*: //; s/  .*$//' | wc -w | tr -d ' ')
  printf '   -> %s group(s) on the line, of %s byte(s) each\n' "$groups" "$g"
done

echo
echo "WHAT CHANGED IN THE FILE: nothing. Thirteen bytes, three renderings."
echo
echo "WHERE THE TAIL FALLS. 13 = 16-3, so the line is short whatever the width,"
echo "and the last group is the one that cannot be full:"
echo "  -g1  the tail is 13 whole groups; a group is a byte, so nothing is ragged."
echo "  -g2  six pairs and then a single byte. 13 is odd, so the last group is"
echo "       half a group, and xxd prints it as one byte rather than padding it."
echo "  -g4  three quads and then ONE byte -- 12 + 1. The ragged piece is three"
echo "       bytes short of the width you asked for."
echo
echo "Nothing is padded, and that is the honest choice: a 00 added to square the"
echo "line would be a byte the file does not contain, printed in the column"
echo "whose whole job is to say what the file contains."
echo
echo "And the width is a CLAIM. -g2 says 'read this as 16-bit units'; -g4 says"
echo "32-bit. For a text file all three claims are wrong and it does not matter,"
echo "because the bytes are drawn in file order either way. It starts mattering"
echo "the moment a tool reorders within a group to keep the claim true -- which"
echo "is what hexdump's -x does and xxd never does."
