#!/usr/bin/env bash
# EBCDIC on a real pipe.
#
# Only CP037 and CP500 are used here, because they are the two EBCDIC pages
# both BSD and GNU iconv ship. The euro-updated pages (CP1140-CP1149) exist
# on GNU and on NEITHER of macOS's -- see the note on the page -- so the
# euro twin is demonstrated in Python instead.
set -u

work=$(mkdir -p "${TMPDIR:-/tmp}/sapcp.$$" && cd "${TMPDIR:-/tmp}/sapcp.$$" && pwd)
trap 'rm -rf "$work"' EXIT
cd "$work"

echo "1. THE SAME LETTERS, A DIFFERENT TABLE"
echo "------------------------------------------------------------------------"
printf 'ABC abc 123' > plain.txt
echo "   text        ABC abc 123"
echo "   as ASCII    $(xxd -p < plain.txt)"
echo "   as CP037    $(iconv -f ASCII -t CP037 plain.txt | xxd -p)"
echo
echo "   Not a rearrangement you can do in your head: 'A' is 0x41 in ASCII"
echo "   and 0xC1 in EBCDIC, and the space is 0x20 against 0x40."
echo

echo "2. THE ALPHABET IS IN THREE PIECES"
echo "------------------------------------------------------------------------"
printf 'abcdefghijklmnopqrstuvwxyz' > alpha.txt
iconv -f ASCII -t CP037 alpha.txt > alpha037.bin
echo "   a-z in ASCII:  $(xxd -p < alpha.txt)"
echo "   a-z in CP037:  $(xxd -p < alpha037.bin)"
echo
echo "   Read the second row along: 81..89, then a jump to 91..99, then a"
echo "   jump to a2..a9. Three runs of 9, 9 and 8. The ASCII row has"
echo "   no jumps at all, which is the whole reason 'is it between a and z'"
echo "   became an idiom."
echo
first=$(printf 'a' | iconv -f ASCII -t CP037 | xxd -p)
last=$(printf 'z' | iconv -f ASCII -t CP037 | xxd -p)
echo "   a is 0x$first and z is 0x$last, so that test spans 41 byte values"
echo "   to cover 26 letters."
echo

echo "3. TWO EBCDIC PAGES THAT AGREE ON EVERY LETTER"
echo "------------------------------------------------------------------------"
printf 'Kowalski' > name.txt
echo "   a name is identical in both:"
echo "      CP037   $(iconv -f ASCII -t CP037 name.txt | xxd -p)"
echo "      CP500   $(iconv -f ASCII -t CP500 name.txt | xxd -p)"
echo
printf '[a]' > brackets.txt
echo "   a bracketed field is not:"
echo "      CP037   $(iconv -f ASCII -t CP037 brackets.txt | xxd -p)"
echo "      CP500   $(iconv -f ASCII -t CP500 brackets.txt | xxd -p)"
echo
echo "   Seven bytes differ between the two pages and every one of them is"
echo "   punctuation: [ ] ! | ^ and the cent and not signs. So master data"
echo "   crosses a wrongly configured interface unharmed and anything with"
echo "   SYNTAX in it -- a JSON payload, a delimited file, a script -- does"
echo "   not. Choosing the wrong one of these two is invisible until the"
echo "   day the payload has a bracket in it."
echo

echo "4. THE LINE SEPARATOR MOVES TOO, AND EVERY LINE TOOL GOES BLIND"
echo "------------------------------------------------------------------------"
printf 'alpha\nbeta\n' > lines.txt
iconv -f ASCII -t CP037 lines.txt > lines037.bin
echo "   ASCII file    $(xxd -p < lines.txt)"
echo "   CP037 file    $(xxd -p < lines037.bin)"
echo "   LF (0x0a) became $(printf '\n' | iconv -f ASCII -t CP037 | xxd -p) -- EBCDIC's NL"
echo
printf '   wc -c says %s bytes and wc -l says %s lines\n' \
    "$(wc -c < lines037.bin | tr -d ' ')" "$(wc -l < lines037.bin | tr -d ' ')"
echo
echo "   Two lines went in and the file is not empty, but nothing on a Unix"
echo "   box will find a line in it: wc, grep, sed, sort, head and read all"
echo "   look for 0x0a and there is not one in the file. This is why an"
echo "   EBCDIC extract is moved in BINARY mode and converted at one end,"
echo "   rather than streamed through a pipeline of text tools."
echo

echo "5. SORT ORDER IS NOT A REARRANGEMENT EITHER"
echo "------------------------------------------------------------------------"
for word in Zebra apple 9lives Apple; do
    printf '%s %s\n' "$(printf '%s' "$word" | iconv -f ASCII -t CP037 | xxd -p)" "$word"
done | LC_ALL=C sort | while read -r hex word; do
    printf '   %-24s %s\n' "$hex" "$word"
done
echo
echo "   Sorted by their EBCDIC bytes, small letters come first, then"
echo "   capitals, then digits -- the opposite grouping to ASCII, where"
echo "   digits sort before capitals before small letters. A report ordered"
echo "   on the mainframe and the same report ordered after transfer"
echo "   disagree, and neither of them is broken."
