#!/usr/bin/env bash
# Answer key: edit a dump, put it back, and find the column that was ignored.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

printf 'cafe\n' > f
echo "THE ROUND TRIP"
printf '   original      %s\n' "$(xxd -p < f)"
xxd f > dump.txt
sed 's/^/   /' dump.txt
xxd -r dump.txt > back.bin
printf '   xxd -r back   %s   identical: %s\n' "$(xxd -p < back.bin)" \
  "$(cmp -s f back.bin && echo yes || echo NO)"
echo
echo "NOW EDIT THE TEXT COLUMN AND PUT IT BACK"
sed 's/cafe/XXXX/' dump.txt > edited.txt
sed 's/^/   /' edited.txt
xxd -r edited.txt > out1.bin
printf '   result        %s   -> %s\n' "$(xxd -p < out1.bin)" "$(cat out1.bin)"
echo "   Nothing changed. xxd -r reads the OFFSET and the HEX and stops; the"
echo "   text column is output only, and editing it edits nothing. That is the"
echo "   sharpest demonstration in this library that the right-hand column is"
echo "   the tool talking, not the file."
echo
echo "NOW EDIT THE HEX COLUMN"
sed 's/6361 6665/6361 7065/' dump.txt > edited2.txt
xxd -r edited2.txt > out2.bin
printf '   6665 -> 7065   %s   -> %s\n' "$(xxd -p < out2.bin)" "$(cat out2.bin)"
echo "   That is the column that is the file."
echo
echo "THE OFFSET IS AN INSTRUCTION, NOT A LABEL"
printf '00000004: 21\n' > sparse.txt
xxd -r sparse.txt > out3.bin
printf '   a dump with ONE line at offset 4 -> %s bytes: %s\n' \
  "$(wc -c < out3.bin | tr -d ' ')" "$(xxd -p < out3.bin)"
echo "   xxd -r SEEKS to the offset, so the four bytes before it are whatever"
echo "   the file already had -- here nothing, so they are NUL. Delete a line"
echo "   from a dump and you do not shorten the file; you punch a hole in it."
echo
echo "AND THE ONE FLAG THAT CHANGES THE CONTRACT"
xxd -p f > plain.txt
xxd -r -p plain.txt > out4.bin
printf '   xxd -p | xxd -r -p  %s   identical: %s\n' "$(xxd -p < out4.bin)" \
  "$(cmp -s f out4.bin && echo yes || echo NO)"
echo "   -p has no offsets and no text column, so it is pure hex both ways --"
echo "   which makes it the form to paste into a bug report and the form to"
echo "   pipe. The full dump is for reading; -p is for round-tripping."
