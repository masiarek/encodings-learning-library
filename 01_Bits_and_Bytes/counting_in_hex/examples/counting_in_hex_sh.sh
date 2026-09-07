#!/usr/bin/env bash
# Counting in hex, in the terminal: the shell will turn the wheel for you.
#
# Run:  bash counting_in_hex_sh.sh
#
# Every tool used here is a bash builtin, so there is no BSD/GNU split to tidy
# around -- `bin` is written out with shifts rather than calling bc, which is
# not installed on a bare ubuntu image.
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
bin() {  # n [width] -> the bits, grouped in nibbles the way the rest of the library writes them
  local n=$1 w=${2:-8} i out=""
  for ((i = w - 1; i >= 0; i--)); do
    out+=$(((n >> i) & 1))
    if ((i % 4 == 0 && i != 0)); then out+=" "; fi
  done
  printf '%s' "$out"
}

echo "1. printf IS THE ODOMETER. seq TURNS IT"
show "seq 13 18 | while read -r n; do printf '%3d = %2X\\n' \"\$n\" \"\$n\"; done"
echo "   D, E, F, then 10 -- and the decimal column is there to say that 10 is sixteen."

echo
echo "2. THE THREE PLACES A BYTE CARRIES, AND WHAT EACH ONE MEANS"
for n in 15 127 255; do
  after=$((n + 1))
  if ((after > 255)); then w=9; note="   <- a NINTH bit, and a byte has eight"; else w=8; note=""; fi
  printf '   %02X + 1 = %-3X  (%3d -> %3d)   %9s -> %s%s\n' "$n" "$after" "$n" "$after" "$(bin "$n")" "$(bin "$after" "$w")" "$note"
done
echo "   0F -> 10   the low nibble is full, so the high one goes up: the second hex digit changes"
echo "   7F -> 80   the top bit turns on -- that is where ASCII stops and chapter 2 starts"
echo "   FF -> 100  every wheel in the byte is full, and the carry needs a column the byte does not have"

echo
echo "3. THE SHELL DOES NOT STOP AT FF -- BUT IT DOES STOP"
show "printf '%X\\n' \$(( 0xFF + 1 ))                 # not a byte, so nothing wrapped"
show "printf '%d\\n' \$(( 0x7FFFFFFFFFFFFFFF + 1 ))   # 63 bits and a sign bit: bash uses a signed 64-bit integer"
echo "   So the shell has a width too; it is just wide enough that you rarely meet it, and signed,"
echo "   so the wheel past the end lands on the most negative number rather than on zero."

echo
echo "4. ARITHMETIC IS DECIMAL. THE BASE IS A DISPLAY CHOICE, MADE TWICE"
show "echo \$(( 0x19 + 1 ))            # hex in, decimal out -- and 19 + 1 is not 20"
show "printf '%X\\n' \$(( 0x19 + 1 ))   # ask for the answer back in hex, and there it is"
show "echo \$(( 16#FF ))  \$(( 2#11111111 ))  \$(( 8#377 ))  255"
echo "   Four spellings, one number. \$(( )) always answers in decimal; printf picks the spelling."
