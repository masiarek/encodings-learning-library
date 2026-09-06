#!/usr/bin/env bash
# Put the character and its bytes on the same line — the shortest useful thing
# a terminal can tell you about a piece of text.
#
# Run:  bash character_and_its_bytes_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf '\305\274' > one.txt          # 'ż', two bytes, no trailing newline

echo "1. THE ONE-LINER"
echo '$ printf "%s = " "$(cat one.txt)"; xxd -p one.txt'
printf '%s = ' "$(cat one.txt)"; xxd -p one.txt
echo "   Three parts, and each one is doing a job:"
echo "     printf '%s = '   writes the character and NO newline, so the line stays open"
echo "     \$(cat one.txt)   substitution — hands over the text, trailing newlines stripped"
echo "     xxd -p           bare hex, no offset column, no ascii column — and it ends the line"

echo
echo "2. WITHOUT A FILE: THE SAME THING ON A PIPE"
echo '$ printf "ż" | xxd -p'
printf '\305\274' | xxd -p

echo
echo "3. WHY -p, AND NOT PLAIN xxd"
echo '$ xxd one.txt'
xxd one.txt
echo '$ xxd -p one.txt'
xxd -p one.txt
echo "   Plain xxd is for READING: an offset, byte pairs, and a text column."
echo "   -p ('postscript') is for USING: just the hex, which is what you paste into"
echo "   a bug report, an email, or the next command."

echo
echo "4. THE REVERSE GEAR"
echo '$ echo c5bc | xxd -r -p'
echo c5bc | xxd -r -p
echo
echo "   xxd -r -p turns the hex back into bytes — the only one of xxd/od/hexdump"
echo "   that goes both ways, which makes the pair a round trip you can test."
echo "   The letter above sits on its own line only because this script printed a"
echo "   newline after it — xxd -r -p wrote the two bytes and stopped, which is the"
echo "   previous lesson happening inside this one."

echo
echo "5. A TABLE, WHICH IS THE ONE-LINER IN A LOOP"
printf '   %-8s %-7s %s\n' char bytes hex
for ch in A ż € 😀; do
  hex=$(printf '%s' "$ch" | xxd -p)
  n=$(printf '%s' "$ch" | wc -c | tr -d ' ')
  printf '   %-8s %-7s %s\n' "$ch" "$n" "$hex"
done
echo "   One character each, one to four bytes each. That column is UTF-8's whole"
echo "   design, and this loop is how you check it on any character you meet."
echo "   (The char column looks ragged because printf pads by BYTES, not by how"
echo "    wide the glyph is — a two-byte letter eats two of its eight columns.)"

echo
echo "6. THE TRAP IN THE SUBSTITUTION"
printf 'abc\n\n\n' > blanks.txt
echo '$ printf "abc\n\n\n" > blanks.txt   # six bytes: a b c and three newlines'
echo "   file on disk : $(xxd -p blanks.txt)"
captured=$(cat blanks.txt)
echo "   \$(cat file)  : $(printf '%s' "$captured" | xxd -p)"
echo "   The substitution ate all three newlines, not just one. That is exactly what"
echo "   you want when you are printing a character beside its bytes — and exactly"
echo "   wrong if you were trying to measure the file. Measure files with wc -c."
