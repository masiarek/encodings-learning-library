#!/usr/bin/env bash
# UTF-8 by hand, where the bytes are real: on a pipe, in a file, cut in half.
#
# Python and Rust can tell you a character is two bytes. Only a terminal can
# show you the two bytes going past with the template markers visible in
# binary, and only a pipe can be cut in the middle of a character so you can
# watch a reader find its footing again. That is this script's whole job, and
# section 4 is the part no other example on this page can do at all.
#
# Every byte here is written \xHH, which names a BYTE and asks nothing of the
# locale or of the bash version -- unlike printf '\u20ac', which gives three
# different answers on three configurations (see: Writing a code point).
set -u

# `wc -c` pads its count to different widths on BSD and GNU, so strip it.
bytes() { wc -c < "$1" | sed 's/^ *//'; }

# The length a lead byte announces, by counting its leading 1 bits.
announced_width() {
  local b=$1
  if   [ "$b" -lt 128 ]; then echo 1
  elif [ "$b" -lt 224 ]; then echo 2
  elif [ "$b" -lt 240 ]; then echo 3
  else                        echo 4
  fi
}

byte_class() {
  local b=$1
  if   [ "$b" -lt 128 ]; then echo "ASCII"
  elif [ "$b" -lt 192 ]; then echo "continuation"
  else echo "lead of $(announced_width "$b")"
  fi
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "1. THE TEMPLATES, ON A REAL PIPE"
echo "   printf writes the bytes; xxd -b prints them back as bits. The markers"
echo "   are in plain view: a lone 0, or 110/1110/11110 and then 10 each time."
echo
for spec in "A:\x41" "e-acute:\xc3\xa9" "z-dot:\xc5\xbc" \
            "euro:\xe2\x82\xac" "grinning face:\xf0\x9f\x98\x80"; do
  printf "   %-14s %s\n" "${spec%%:*}" \
    "$(printf "${spec#*:}" | xxd -b | cut -c11-52 | sed 's/ *$//')"
done
echo
echo "   Count the leading 1s of the first group and you have the length,"
echo "   before reading any further byte. That is the whole decoder."
echo

echo "2. FROM A HEX DUMP BACK TO A CHARACTER"
echo "   The pencil loop closed: type the bytes you worked out, and the"
echo "   terminal shows you what they say. No library, no table lookup."
echo
for esc in "\x41" "\xc3\xa9" "\xc5\xbc" "\xe2\x82\xac" "\xf0\x9f\x98\x80"; do
  printf "   printf '%-18s writes %-10s and the terminal shows  %s\n" \
    "$esc'" "$(printf "$esc" | xxd -p)" "$(printf "$esc")"
done
echo
echo "   That is also how you make a test file for a character you cannot"
echo "   type -- and how you make one your editor would quietly repair."
echo

echo "3. ONE FILE, AND WHY THE TWO RULERS DISAGREE"
printf 'zolw\n'                      > "$tmp/ascii.txt"
printf '\xc5\xbc\xc3\xb3\xc5\x82w\n' > "$tmp/polish.txt"
echo "   Four letters either way, and one file is bigger. Every non-ASCII"
echo "   letter is paying for its second byte."
echo
printf "   %2s bytes on disk   %-18s the word: %s\n" \
  "$(bytes "$tmp/ascii.txt")"  "$(xxd -p "$tmp/ascii.txt")"  "$(cat "$tmp/ascii.txt")"
printf "   %2s bytes on disk   %-18s the word: %s\n" \
  "$(bytes "$tmp/polish.txt")" "$(xxd -p "$tmp/polish.txt")" "$(cat "$tmp/polish.txt")"
echo
echo "   0a is the newline, one byte in both. Strip it and the Polish word is"
echo "   7 bytes for 4 letters: three letters at two bytes, one at one. The"
echo "   file records none of that -- a reader has to be told the encoding,"
echo "   which is this chapter's whole argument."
echo

echo "4. CUT THE PIPE IN THE MIDDLE OF A CHARACTER"
stream="$tmp/stream.bin"
printf 'a\xc5\xbc\xf0\x9f\x98\x80b' > "$stream"
echo "   The stream is 'a', z-dot, a grinning face, 'b' -- $(bytes "$stream") bytes:"
echo
echo "      $(xxd -p "$stream")"
echo
echo "   Start reading at each byte in turn, as a program joining a stream"
echo "   late would. A first byte in 80-BF says you have landed inside a"
echo "   character: skip while that is true, and the next one starts there."
echo
echo "   start  byte  class         skip  starts at  width  the character"
for ((start = 1; start <= 8; start++)); do
  first=$(tail -c +"$start" "$stream" | head -c 1 | xxd -p)
  probe=$start
  while [ "$probe" -le 8 ]; do
    b=$(tail -c +"$probe" "$stream" | head -c 1 | xxd -p)
    [ "$((16#$b))" -ge 128 ] && [ "$((16#$b))" -le 191 ] || break
    probe=$((probe + 1))
  done
  if [ "$probe" -le 8 ]; then
    lead=$(tail -c +"$probe" "$stream" | head -c 1 | xxd -p)
    width=$(announced_width "$((16#$lead))")
    char=$(tail -c +"$probe" "$stream" | head -c "$width")
  else
    width="-"; char="(end of stream)"
  fi
  printf "   %5s  %4s  %-12s  %4s  %9s  %5s  %s\n" \
    "$start" "$first" "$(byte_class "$((16#$first))")" \
    "$((probe - start))" "$probe" "$width" "$char"
done
echo
echo "   Never more than three bytes skipped, because no template is longer."
echo "   So a truncated or corrupted file costs you one character and not the"
echo "   rest of the stream. Note what the resync did NOT need: no state from"
echo "   earlier in the file, no byte count from the top, and no lookahead."
echo "   That is what self-synchronising means, and it is a consequence of one"
echo "   decision -- continuation bytes start 10, and nothing else does."
echo

echo "5. HALF A CHARACTER IS NOT TEXT"
echo "   The templates are a rule as well as a recipe, so a piece of a"
echo "   character is refused rather than decoded into something."
echo
for esc in "\xc5\xbc" "\xc5" "\xbc" "\xf0\x9f\x98\x80" "\xf0\x9f" "\x80\x80"; do
  if printf "$esc" | iconv -f UTF-8 -t UTF-8 > /dev/null 2>&1; then
    verdict="exit 0   valid UTF-8"
  else
    verdict="exit 1   refused"
  fi
  printf "   printf '%-20s %s\n" "$esc'" "$verdict"
done
echo
echo "   A lead byte with its continuations missing is refused, and so is a"
echo "   continuation byte with no lead byte in front of it. Both are the"
echo "   templates being read as a specification. Who runs that check, and"
echo "   what is left of it downstream, is the next lesson."
