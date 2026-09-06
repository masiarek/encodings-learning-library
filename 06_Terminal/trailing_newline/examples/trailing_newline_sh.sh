#!/usr/bin/env bash
# The last byte of a text file, and the six things that depend on it.
#
# Two files hold the same one character. One ends in a newline and one does
# not, and almost every tool in the terminal treats them as different files.
#
# Run:  bash trailing_newline_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# Work in a scratch directory so every command below can name its files plainly.
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# 'ż' — two bytes, C5 BC. Written twice: once with printf, which writes exactly
# what it is given, and once with echo, which adds a newline.
printf '\305\274'   > no_nl.txt
printf '\305\274\n' > with_nl.txt

echo "1. THE SAME CHARACTER, TWO FILES"
show "xxd no_nl.txt"
show "xxd with_nl.txt"
echo "   Same letter. The second file has a third byte, 0a, and that byte is the"
echo "   whole subject of this page."

echo
echo "2. HOW BIG, AND HOW MANY LINES"
show "wc -c < no_nl.txt   | tr -d ' '"
show "wc -l < no_nl.txt   | tr -d ' '"
show "wc -l < with_nl.txt | tr -d ' '"
echo "   A file with a letter in it has ZERO lines. wc -l counts newline bytes,"
echo "   and POSIX says a line is characters ENDING WITH one — so the letter sits"
echo "   in what POSIX calls an incomplete last line, and nothing counts it."

echo
echo "3. THE CHECK: WHAT IS THE LAST BYTE?"
show "tail -c 1 no_nl.txt   | xxd -p"
show "tail -c 1 with_nl.txt | xxd -p"
echo "   0a means the file ends in a newline. Anything else means it does not."

echo
echo "4. WHY CONCATENATION GLUES"
show "cat no_nl.txt no_nl.txt | xxd"
show "cat with_nl.txt with_nl.txt | xxd"
echo "   Without the terminator, cat runs the two files together into one line."
echo "   That is the same fact as section 2, seen from the other side: the newline"
echo "   is not a decoration at the end, it is what closes the line."

echo
echo "5. COMMAND SUBSTITUTION ERASES THE DIFFERENCE"
a=$(cat no_nl.txt)
b=$(cat with_nl.txt)
printf '\n$ a=$(cat no_nl.txt); b=$(cat with_nl.txt)\n'
echo "  a is $(printf '%s' "$a" | wc -c | tr -d ' ') bytes, b is $(printf '%s' "$b" | wc -c | tr -d ' ') bytes"
if [ "$a" = "$b" ]; then echo "  a = b  -> the same string"; else echo "  a != b"; fi
echo "   \$(...) strips EVERY trailing newline, so the difference the whole page is"
echo "   about cannot survive being put in a variable. Useful when you want the"
echo "   text; a trap when you were trying to measure the file."

echo
echo "6. A READ LOOP SILENTLY DROPS THE LAST LINE"
printf 'one\ntwo\nthree' > three.txt
echo '$ printf "one\ntwo\nthree" > three.txt   # no trailing newline'
echo '$ while read -r line; do echo "  got: $line"; done < three.txt'
while read -r line; do echo "  got: $line"; done < three.txt
echo "   Two of three. read returns false on the incomplete last line, so the loop"
echo "   ends before the body runs — the classic way a data file loses its last row."
echo '$ while read -r line || [ -n "$line" ]; do ...   # the fix'
while read -r line || [ -n "$line" ]; do echo "  got: $line"; done < three.txt

echo
echo "7. ADDING THE BYTE"
printf '\n$ printf %s >> no_nl.txt\n' "'\\n'"
printf '\n' >> no_nl.txt
show "xxd no_nl.txt"
show "wc -l < no_nl.txt | tr -d ' '"
echo "   One byte appended, and the file now has a line in it."
