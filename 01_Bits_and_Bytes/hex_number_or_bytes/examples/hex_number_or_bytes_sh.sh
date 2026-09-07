#!/usr/bin/env bash
# The two doors in the shell, and the one that loses data without saying so.
#
# For a NUMBER: printf '%d' and $(( )). For BYTES: xxd -p and xxd -r -p.
# Everything here is byte-identical on macOS and Ubuntu -- including, sadly,
# section 3.
#
# Run:  bash hex_number_or_bytes_sh.sh

set -u

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. THE NUMBER DOOR, AND THE BASE IT ASSUMES"
printf '   %-28s %s\n' "printf '%d' 0x41"  "$(printf '%d' 0x41)"
printf '   %-28s %s\n' "printf '%d' 41"    "$(printf '%d' 41)"
printf '   %-28s %s\n' '$(( 16#41 ))'      "$(( 16#41 ))"
printf '   %-28s %s\n' '$(( 0x41 ))'       "$(( 0x41 ))"
printf '\n   Rows one and two are the same command on the same-looking input\n'
printf '   and they differ by a factor of about one and a half. Without the\n'
printf '   0x, 41 is forty-one -- correct, silent, and wrong if the field was\n'
printf '   hex. $(( 16#41 )) is the spelling that cannot be misread, because\n'
printf '   the base is written where the value is, not inferred from a prefix.\n'

say "2. THE BYTE DOOR"
printf '   %-28s ' "printf 'A' | xxd -p";      printf 'A' | xxd -p
printf '   %-28s ' "printf '\\x41' | xxd -p";   printf '\x41' | xxd -p
printf '   %-28s ' "printf '0041' | xxd -r -p"; printf '0041' | xxd -r -p | xxd -p
printf '   %-28s %s\n' "how many bytes is that" "$(printf '0041' | xxd -r -p | wc -c | tr -d ' ')"
printf '\n   xxd -r -p is the shell'"'"'s bytes.fromhex: hex text in, bytes out,\n'
printf '   two digits per byte, leading zeros kept because they are bytes.\n'
printf '   Compare $(( 16#0041 )), which is %s -- the same digits, one byte\n' "$(( 16#0041 ))"
printf '   shorter, because a number has no width to keep.\n'

say "3. AND IT DROPS WHAT IT CANNOT USE, WITHOUT SAYING SO"
for input in '123' 'c3zzA9' 'c3 a9'; do
  out=$(printf '%s' "$input" | xxd -r -p | xxd -p)
  status=$?
  printf '   %-12s -> %-10s exit %s\n' "'$input'" "${out:-(nothing)}" "$status"
done
printf '\n   Three malformed or unusual inputs, three quiet answers and three\n'
printf '   zero exits. The first is an odd number of digits and the trailing\n'
printf '   nibble is simply gone. The second stops at the first character\n'
printf '   that is not a hex digit and keeps whatever it had. The third is\n'
printf '   the benign one -- whitespace between bytes really is allowed, and\n'
printf '   is what xxd -p emits with a width flag.\n'
printf '\n   So xxd -r -p is a fine encoder of hex you produced and a poor\n'
printf '   validator of hex somebody sent you. Nothing in this pipeline can\n'
printf '   tell a short field from a complete one; check the length yourself,\n'
printf '   before decoding, where the answer is still knowable.\n'

say "4. THE ROUND TRIP THAT IS SAFE"
printf '   %-28s ' 'the word';             printf 'café'; printf '\n'
printf '   %-28s ' 'xxd -p';               printf 'café' | xxd -p
printf '   %-28s ' 'xxd -p | xxd -r -p';   printf 'café' | xxd -p | xxd -r -p; printf '\n'
printf '   %-28s %s\n' 'bytes in / bytes out' "$(printf 'café' | wc -c | tr -d ' ') / $(printf 'café' | xxd -p | xxd -r -p | wc -c | tr -d ' ')"
printf '\n   xxd -p and xxd -r -p are inverses on anything xxd -p produced,\n'
printf '   which is the only guarantee either of them offers. Everything in\n'
printf '   section 3 was hex that xxd -p had never written.\n'
