#!/usr/bin/env bash
# Which base did you mean, in the terminal: one string of digits, and every
# field that reads it picks its own base.
#
# Run:  bash which_base_did_you_mean_sh.sh
#
# The tools here are bash builtins plus `xxd`, `od`, `head` and `chmod`, all of
# which read a leading zero the same way on macOS and on Ubuntu. `dd` does NOT,
# which is why it is in a dated fence on the page and not in this key. `od`'s
# line padding differs, so its output goes through `tidy` as elsewhere.
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%s%s", (i > 1 ? " " : ""), $i; print "" }' | sed -e '/^$/d'; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"
printf '0123456789abcdefghij' > off.bin

echo "1. THE SHELL CAN BE TOLD, AND IT HAS TWO SPELLINGS FOR SAYING SO"
echo "   base#digits -- you name the base in front of a #, in any base from 2 to 64"
for e in '2#11111111' '8#377' '10#255' '16#FF'; do
  printf '   %-18s = %s\n' "\$(( $e ))" "$((e))"
done
echo "   and the C prefixes it inherits -- both of them, because there is no 0b here"
printf '   %-18s = %s\n' '$(( 0377 ))' "$((0377))" '$(( 0xFF ))' "$((0xFF))" '$(( 255 ))' "$((255))"
if out=$(bash -c 'echo $((0b11111111))' 2>&1); then
  echo "   \$(( 0b11111111 )) = $out"
else
  echo "   \$(( 0b11111111 )) is an error: bash took 0x and the leading zero from C"
  echo "   and stopped there, which is the set C11 itself had. Binary is 2#11111111."
fi
echo "   Seven spellings, one number. The four with a # say the base out loud. The"
echo "   three below them do not: 0377 is octal because of one character you can"
echo "   miss, and 255 is decimal because nothing said otherwise."

echo
echo "2. SO WHAT IS 010? ONE SHELL, TWO BUILTINS, TWO ANSWERS"
if [ 010 -eq 10 ]; then a=true; else a=false; fi
if [ 010 -eq 8 ]; then b=true; else b=false; fi
if [[ 010 -eq 10 ]]; then c=true; else c=false; fi
if [[ 010 -eq 8 ]]; then d=true; else d=false; fi
printf '   %-20s %-7s %-20s %s\n' '[ 010 -eq 10 ]' "$a" '[[ 010 -eq 10 ]]' "$c"
printf '   %-20s %-7s %-20s %s\n' '[ 010 -eq 8 ]' "$b" '[[ 010 -eq 8 ]]' "$d"
echo "   test(1) reads its operands in base 10. [[ ]] puts them through \$(( )),"
echo "   where a leading zero is octal. Both are builtins of the same shell, both"
echo "   are spelled -eq, and they disagree about the characters between them."
show "printf '%d\\n' 010 0x41 255   # printf takes the C prefixes: 8, 65, 255"
show "printf '%s\\n' 010 9 | sort -n | tr '\\n' ' ' | sed 's/ \$//'   # sort -n: base 10, so 9 is first"
echo
if out=$(bash -c 'echo $((09))' 2>&1); then
  echo "   \$(( 09 )) was accepted, as $out"
else
  echo "   And \$(( 09 )) is an ERROR -- \"value too great for base\" -- because the"
  echo "   leading zero already said octal and 9 is not an octal digit. That is the"
  echo "   rule speaking up, which it does only when the digits happen to give it away."
fi

echo
echo "3. THE OFFSET YOU TYPE IS NOT IN THE BASE THE DUMP PRINTS"
show "xxd -g 4 off.bin"
echo "   The offset column is HEX. The second row begins at 00000010, which is 16."
printf '\n   %-12s %-12s %s\n' 'you type' 'xxd -s' 'od -j'
for n in 10 010 0x10; do
  printf '   %-12s %-12s %s\n' "$n" \
    "$(xxd -s "$n" -l 4 -p off.bin)" \
    "$(od -A n -j "$n" -N 4 -t c off.bin | tr -d ' \n')"
done
echo "   Row 1 is the everyday mistake: you read 00000010 off the dump, typed"
echo "   -s 10, and landed six bytes early. Row 2 is the one nobody expects --"
echo "   both tools read a leading zero as octal, so 010 seeks to 8, not to 10."
echo "   Row 3 is the spelling that says what it means, and both tools take it."
echo
echo "   head -c is a LENGTH rather than a seek, and reads the same three again:"
for n in 10 010 0x10; do
  if out=$(head -c "$n" off.bin 2>/dev/null) && [ -n "$out" ]; then
    printf '   head -c %-6s %2d bytes\n' "$n" "${#out}"
  else
    printf '   head -c %-6s refused\n' "$n"
  fi
done
echo "   Ten, ten, and a refusal: this one is base 10 and takes no prefix at all."

echo
echo "4. ONE FIELD WITH NO SPELLING, AND ONE WITH NO CHOICE"
: > f
chmod 755 f;  m1=$(ls -l f | cut -c1-10)
chmod 0755 f; m2=$(ls -l f | cut -c1-10)
printf '   %-14s %s\n' 'chmod 755' "$m1" 'chmod 0755' "$m2"
if chmod 888 f 2>/dev/null; then echo '   chmod 888      accepted'; else echo '   chmod 888      refused'; fi
echo "   chmod's mode is octal always. The leading zero changes nothing, there is"
echo "   no way to hand it a decimal 755, and the refusal of 888 is the tell: an"
echo "   8 cannot be an octal digit, so the field never had another reading."
show "printf 'A' | od | tidy   # and od's own default OUTPUT base is octal, two bytes at a time"
echo "   000101 is one byte: 0101 octal, 0x41, 'A'. The oldest byte tool on the"
echo "   machine answers in base 8 until you ask it for something else."
