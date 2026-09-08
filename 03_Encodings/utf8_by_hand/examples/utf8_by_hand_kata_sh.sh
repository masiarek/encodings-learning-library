#!/usr/bin/env bash
# The kata's answer: four code points encoded by hand, and one that cannot be.
#
# Shell rather than Python, because the question is about BYTES and this is the
# one language on the page where the answer arrives as bytes on a pipe. Every
# number below is derived by arithmetic in bash -- no encoder is called until
# the last column, where iconv is asked whether the bytes are UTF-8 at all.
set -u

# A number as N binary digits. bash has no %b for binary, so build it.
bin() {
  local n=$1 width=$2 out=""
  while [ "$width" -gt 0 ]; do
    out="$((n & 1))$out"
    n=$((n >> 1))
    width=$((width - 1))
  done
  printf '%s' "$out"
}

# Encode by the templates, in bash arithmetic. Returns "\xNN\xNN..".
encode_escapes() {
  local cp=$1
  if   [ "$cp" -lt 128 ];   then printf '\\x%02x' "$cp"
  elif [ "$cp" -lt 2048 ];  then printf '\\x%02x\\x%02x' \
         "$((192 | (cp >> 6)))" "$((128 | (cp & 63)))"
  elif [ "$cp" -lt 65536 ]; then printf '\\x%02x\\x%02x\\x%02x' \
         "$((224 | (cp >> 12)))" "$((128 | ((cp >> 6) & 63)))" "$((128 | (cp & 63)))"
  else printf '\\x%02x\\x%02x\\x%02x\\x%02x' \
         "$((240 | (cp >> 18)))" "$((128 | ((cp >> 12) & 63)))" \
         "$((128 | ((cp >> 6) & 63)))" "$((128 | (cp & 63)))"
  fi
}

payload_width() {
  if   [ "$1" -lt 128 ];   then echo 7
  elif [ "$1" -lt 2048 ];  then echo 11
  elif [ "$1" -lt 65536 ]; then echo 16
  else                          echo 21
  fi
}

echo "THE FOUR SEQUENCES"
echo
echo "   Pad the number to the payload width, cut at the slot boundaries, put"
echo "   the markers in front. Every line below is bash arithmetic -- the only"
echo "   thing an encoder is asked is the last column, and only for the fifth."
echo
for cp_hex in 00E9 017C 20AC 1F600; do
  cp=$((16#$cp_hex))
  width=$(payload_width "$cp")
  padded=$(bin "$cp" "$width")
  esc=$(encode_escapes "$cp")
  bytes=$(printf "$esc" | xxd -p)
  echo "   U+$cp_hex"
  printf "      %-20s %s\n" "padded to $width slots" "$padded"
  printf "      %-20s %s\n" "the bytes" \
    "$(printf "$esc" | xxd -b | cut -c11-52 | sed 's/ *$//')"
  printf "      %-20s %s   and it shows as  %s\n" "in hex" \
    "$bytes" "$(printf "$esc")"
done
echo
echo "   C3 A9   C5 BC   E2 82 AC   F0 9F 98 80"
echo "   Two, two, three, four -- and the byte count came from where the number"
echo "   sits on the number line, not from the alphabet the letter belongs to."
echo

echo "AND THE FIFTH, WHICH IS THE POINT OF THE KATA"
echo
cp=$((16#D800))
esc=$(encode_escapes "$cp")
echo "   U+D800 goes through the same arithmetic without complaint:"
printf "      %-20s %s\n" "padded to 16 slots" "$(bin "$cp" 16)"
printf "      %-20s %s\n" "the bytes" \
  "$(printf "$esc" | xxd -b | cut -c11-52 | sed 's/ *$//')"
printf "      %-20s %s\n" "in hex" "$(printf "$esc" | xxd -p)"
echo
if printf "$esc" | iconv -f UTF-8 -t UTF-8 > /dev/null 2>&1; then
  printf "      %-20s %s\n" "iconv says" "exit 0   valid UTF-8"
else
  printf "      %-20s %s\n" "iconv says" "exit 1   refused"
fi
echo
echo "   The templates are a recipe and a rule, and here they part company. The"
echo "   recipe produces ED A0 80; the rule -- Table 3-7's ED row, whose second"
echo "   byte stops at 9F instead of BF -- forbids it. U+D800 is a surrogate:"
echo "   one half of the pair UTF-16 uses to reach above U+FFFF, and not a"
echo "   character at all, so no UTF-8 sequence is allowed to mean it."
echo
echo "   That cap is the 2,048-number hole the lesson's exhaustion walks past:"
echo "   0x110000 - 2048 = 1112064, and every one of those has bytes while"
echo "   these 2,048 do not. If your pencil answered ED A0 80, the arithmetic"
echo "   was right and the answer is still no."
