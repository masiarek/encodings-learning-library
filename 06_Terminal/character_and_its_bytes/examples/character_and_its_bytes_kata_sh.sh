#!/usr/bin/env bash
# Answer key: the one-liner, and the three newline decisions holding it up.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

printf '\305\274' > f          # ż, two bytes, and NO trailing newline

echo "THE LINE"
echo '   $ printf '"'"'%s = '"'"' "$(cat f)"; xxd -p f'
printf '   '; printf '%s = ' "$(cat f)"; xxd -p f
echo
echo "THREE DECISIONS, AND THE LINE NEEDS ALL THREE"
echo
echo "1. THE FILE HAS NO TRAILING NEWLINE."
printf '   f is %s bytes: %s -- letter only\n' "$(wc -c < f | tr -d ' ')" "$(xxd -p < f)"
echo "   If it had one, \$(cat f) would still be 'ż' -- command substitution"
echo "   strips trailing newlines -- but xxd -p would print c5bc0a and the row"
echo "   would claim the letter is three bytes. The file must be exactly the"
echo "   character for the two halves of the line to be about the same thing."
echo
echo "2. printf DOES NOT ADD ONE, SO THE ROW STAYS A ROW."
printf '   printf %%s = -> no newline, so xxd continues the SAME line\n'
echo "   With echo the '=' would end the line and the hex would land under it."
echo
echo "3. xxd -p DOES ADD ONE, SO THE ROW ENDS."
printf '   xxd -p output ends with %s\n' "$(xxd -p f | xxd -p | tail -c 3)"
echo "   That is the 0a finishing the line -- supplied by the tool, not by the"
echo "   file. Three separate decisions about one byte, and the readable"
echo "   one-liner is what you get when all three line up."
echo
echo "WHAT EACH HALF IS ACTUALLY DOING"
echo "   \$(cat f)   DECODES: the terminal draws these bytes using your locale."
echo "              Get the locale wrong and the left side is mojibake while"
echo "              the right side stays correct."
echo "   xxd -p     does not decode at all. It is the file."
echo "   So the row is a decoded reading beside the bytes it came from -- which"
echo "   is the whole reason it is worth typing: the two halves can disagree,"
echo "   and when they do, the right one is right."
