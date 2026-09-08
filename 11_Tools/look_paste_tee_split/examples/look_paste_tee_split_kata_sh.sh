#!/usr/bin/env bash
# Answer key: three tools that take a number or a string as BYTES, and the control.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251\n' > f      # 6 bytes

echo "1. split -b CUTS A CHARACTER IN HALF"
split -b 4 f piece_
for p in piece_*; do printf '   %-10s %s\n' "$p" "$(xxd -p < "$p")"; done
# iconv from UTF-8 to UTF-8 is a pure validity check, and it is on both
# platforms -- no interpreter needed to answer "is this still text".
valid() { iconv -f UTF-8 -t UTF-8 < "$1" >/dev/null 2>&1 && echo yes || echo NO; }
printf '   piece_aa is valid UTF-8? %s      piece_ab? %s\n' "$(valid piece_aa)" "$(valid piece_ab)"
echo "   -b is a byte budget, and 4 lands inside é. Neither piece is text, and"
echo "   split neither knows nor says. -l splits on lines and cannot do this."
echo
echo "2. paste -d TAKES A LIST OF BYTES, NOT A DELIMITER"
printf 'a\nb\n' > c1; printf '1\n2\n' > c2; printf 'x\ny\n' > c3
printf '   paste -d X      %s\n' "$(paste -d 'X' c1 c2 c3 | tr '\n' ' ' | sed 's/ $//')"
printf '   paste -d é      %s\n' "$(paste -d 'é' c1 c2 c3 | tr '\n' ' ' | sed 's/ $//')"
echo "   One 'delimiter' produced TWO different separators: -d is a LIST read"
echo "   one byte at a time, and é is two bytes, so c3 joins the first pair and"
echo "   a9 the second. The output is not valid UTF-8 either."
echo
echo "3. look NEEDS A SORTED FILE, AND SAYS NOTHING WHEN IT IS NOT"
printf 'zebra\napple\nmango\n' > words
st=0; look apple words >/dev/null 2>&1 || st=$?
printf '   look apple <unsorted>   exit=%d\n' "$st"
LC_ALL=C sort words > sorted
st=0; look apple sorted >/dev/null 2>&1 || st=$?
printf '   look apple <sorted>     exit=%d\n' "$st"
echo "   The word is in the file both times. look does a BINARY SEARCH, which"
echo "   assumes an order -- and which order is a locale question, so even a"
echo "   sorted file can be the wrong sorted file."
echo
echo "4. tee IS THE CONTROL"
printf 'caf\303\251\000\377\n' | tee copy.bin | xxd -p | sed 's/^/   through tee: /'
printf '   the file tee wrote:  %s\n' "$(xxd -p < copy.bin)"
echo "   NUL, ff, an incomplete sequence -- tee passes all of it through"
echo "   unchanged, because it has no text model to get wrong. That is exactly"
echo "   why it is the tool to insert in a pipeline you have stopped trusting:"
echo "       ... | tee /tmp/raw | rest-of-pipeline    then xxd /tmp/raw"
echo
echo "THE PATTERN IN THE OTHER THREE"
echo "   Each takes something you meant as TEXT -- a length, a delimiter, an"
echo "   order -- and applies it as BYTES. None warns. Two of them exit 0."
