#!/usr/bin/env bash
# Valid bytes are not the same claim as safe bytes. This payload is well-formed
# UTF-8, well-formed ASCII, and contains a script tag -- in a third table.
#
# Portable: printf, xxd, grep, iconv, wc. Runs under LC_ALL=C, so grep is a
# byte matcher on both macOS and Linux.

payload='+ADw-script+AD4-'
f="$(mktemp)"
printf '%s\n' "$payload" > "$f"

echo "1. THE PAYLOAD IS ORDINARY ASCII"
printf '   $ printf %%s %s | xxd -p\n' "'$payload'"
printf '     '; printf '%s' "$payload" | xxd -p
printf '   %s bytes, every one of them below 0x80.\n' "$(printf '%s' "$payload" | wc -c | tr -d ' ')"
echo

echo "2. EVERY BYTE FILTER LETS IT THROUGH"
for pat in '<script>' '<' '>' 'javascript'; do
    n=$(grep -c -- "$pat" "$f")
    printf "   grep -c %-14s %s\n" "'$pat'" "$n"
done
printf "   grep -c %-14s %s   <- the only thing a filter can see\n" "'script'" "$(grep -c -- 'script' "$f")"
echo "   No angle bracket exists in the file. There is nothing to escape,"
echo "   nothing to strip, and nothing for a rule to match on."
echo

echo "3. AND IT IS VALID UTF-8, SO VALIDATION SAYS YES TOO"
iconv -f UTF-8 -t UTF-8 < "$f" > /dev/null 2>&1
echo "   iconv -f UTF-8 -t UTF-8   exit $?   (0 = well-formed)"
iconv -f ASCII -t UTF-8 < "$f" > /dev/null 2>&1
echo "   iconv -f ASCII -t UTF-8   exit $?   (0 = well-formed)"
echo "   Both say yes, and both are right. Well-formedness is a question about"
echo "   ONE table. It cannot tell you that the same bytes spell something else"
echo "   in a second table -- here UTF-7, where +ADw- is '<' and +AD4- is '>'."
echo

echo "4. SO THE DEFENCE IS NOT A FILTER, IT IS A DECLARATION"
echo "   wrong:  serve the bytes and let the reader work out the encoding"
echo "   right:  Content-Type: text/html; charset=utf-8"
echo
echo "   A filter guards a spelling. Naming the table removes the second"
echo "   spelling entirely, which is the only move that scales: there is"
echo "   always another table, and you cannot enumerate them."

rm -f "$f"
