#!/usr/bin/env bash
# The same claim, asked of the tools rather than of a language runtime.
#
# Nothing here prints a reserved code point as itself: every byte string is
# built with printf's \xHH, which names BYTES and asks nothing of the locale
# (finding 13 in CONTRIBUTING.md), and read back through xxd.

set -u
rule() { printf -- '------------------------------------------------------------------------\n'; }
work=$(mktemp -d) && trap 'rm -rf "$work"' EXIT

echo "1. THE BYTES, WRITTEN AND READ BACK"
rule
# label:escape -- three noncharacters, one private-use, and the two the
# encoders actually refuse, for contrast.
for spec in \
  'U+FDD0   noncharacter:\xef\xb7\x90' \
  'U+FFFE   noncharacter:\xef\xbf\xbe' \
  'U+FFFF   noncharacter:\xef\xbf\xbf' \
  'U+E000   private use :\xee\x80\x80' \
  'U+D800   surrogate   :\xed\xa0\x80' \
  'U+110000 past the end:\xf4\x90\x80\x80'
do
  label=${spec%%:*}
  esc=${spec#*:}
  printf "$esc" > "$work/x.bin"
  size=$(wc -c < "$work/x.bin" | tr -d ' ')
  hex=$(xxd -p "$work/x.bin")
  # iconv from UTF-8 to UTF-8 is the shell's yes/no UTF-8 validator.
  if iconv -f UTF-8 -t UTF-8 < "$work/x.bin" > /dev/null 2>&1; then
    verdict='accepted'
  else
    verdict='REFUSED'
  fi
  printf '   %s  %-9s %s bytes   iconv UTF-8 -> UTF-8: %s\n' \
    "$label" "$hex" "$size" "$verdict"
done
echo
echo "   Five of six accepted, and the one refusal is the surrogate -- not"
echo "   a reserved code point. The last row is a different story and the"
echo "   iconv page tells it: both iconvs take f4 90 80 80, which is above"
echo "   U+10FFFF and which Python and Rust each refuse. What matters here"
echo "   is the first four rows, where there is simply nothing to object to."
echo

echo "2. THE TEXT TOOLS HAVE NO OPINION EITHER"
rule
printf 'alpha\xef\xbf\xbebeta\n' > "$work/line.txt"
printf '   the file, as bytes:  %s\n' "$(xxd -p "$work/line.txt")"
printf '   wc -c                %s\n' "$(wc -c < "$work/line.txt" | tr -d ' ')"
printf '   wc -l                %s\n' "$(wc -l < "$work/line.txt" | tr -d ' ')"
printf '   grep -c alpha        %s\n' "$(grep -c alpha "$work/line.txt")"
printf '   grep -c beta         %s\n' "$(grep -c beta "$work/line.txt")"
printf '   cat -v               %s\n' "$(cat -v "$work/line.txt")"
echo
echo "   Nine letters you can read, one code point you cannot see, thirteen"
echo "   bytes on disk, one line, and every tool content. cat -v is the row"
echo "   worth keeping: it is how you SEE a reserved code point at a"
echo "   terminal, because nothing is going to draw it for you."
echo

echo "3. AND THEY SURVIVE A REAL PIPE"
rule
printf 'a\xef\xbf\xbeb\xee\x80\x80c\n' > "$work/mix.txt"
printf '   original          %s\n' "$(xxd -p "$work/mix.txt")"
printf '   through cat       %s\n' "$(cat "$work/mix.txt" | xxd -p)"
printf '   through iconv     %s\n' "$(iconv -f UTF-8 -t UTF-8 < "$work/mix.txt" | xxd -p)"
printf '   through tr -d c   %s\n' "$(tr -d c < "$work/mix.txt" | xxd -p)"
echo
echo "   Byte for byte, unchanged. Which is the practical half of the claim:"
echo "   a pipeline will not clean these up for you, and will not warn you."
