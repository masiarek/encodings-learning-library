#!/usr/bin/env bash
# Binary or text: three bytes, four names, and who decides.
#
# Every line recorded here was byte-identical on macOS 26.6.2 (file-5.41, BSD
# grep 2.6.0, Apple iconv) and ubuntu:24.04 (file-5.45, GNU grep 3.11, glibc
# iconv) on 2026-09-10: --mime-type and --mime-encoding, iconv's exit status,
# iconv out of three 8-bit tables, and grep -I's exit status in the C locale.
# What does differ between the two - grep under a UTF-8 locale - is on the
# page, in a dated fence, and nowhere in this script.
#
# Run:  bash binary_or_text_sh.sh
set -u
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

hx() { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }

echo "1. THE NAME IS NOT IN THE BYTES"
printf '\300\377\356' > output.bin
cp output.bin output.txt
cp output.bin output.dat
cp output.bin output
for f in output.bin output.txt output.dat output; do
  printf '   %-11s %s   %s bytes\n' "$f" "$(hx < "$f")" "$(wc -c < "$f" | tr -d ' ')"
done
if cmp -s output.bin output.txt && cmp -s output.bin output.dat && cmp -s output.bin output; then
  echo "   cmp finds no difference between any of them."
fi
echo "   Four names, one set of bytes. A filename is kept in the directory,"
echo "   not in the file, so nothing that reads the file can see it."

echo
echo "2. file(1) READS THE BYTES - AND CALLS THEM TEXT"
for f in output.bin output.txt output.dat output; do
  printf '   %-11s %-11s %s\n' "$f" "$(file -b --mime-type "$f")" "$(file -b --mime-encoding "$f")"
done
echo "   The same answer four times, because the name is not an input to"
echo "   file(1). And the answer is text: iso-8859-1 means 'high bytes, not"
echo "   UTF-8, so some 8-bit table' - and in Latin-1, c0, ff and ee are"
echo "   three ordinary letters."

echo
echo "3. A READER THAT INSISTS ON UTF-8 SAYS NO"
iconv -f UTF-8 -t UTF-8 < output.bin > /dev/null 2>&1
echo "   iconv -f UTF-8 -t UTF-8 < output.bin      exit $?"
echo "   Non-zero: these bytes are not UTF-8. Of the readers in this script it"
echo "   is the only one that objects, and its objection is about one"
echo "   encoding, not about the file."

echo
echo "4. THREE 8-BIT TABLES, THREE READINGS, NO REFUSALS"
for t in ISO-8859-1 CP1252 MACINTOSH; do
  s=$(iconv -f "$t" -t UTF-8 < output.bin)
  printf '   read as %-11s %s   written back out as UTF-8: %s\n' "$t" "$s" "$(printf '%s' "$s" | hx)"
done
echo "   Latin-1 and Windows-1252 agree on all three bytes, and Mac OS Roman"
echo "   disagrees with them on every one. None of the three refused: each"
echo "   found a character for every byte, so none of them can call a file"
echo "   binary."

echo
echo "5. THE BYTE THAT DOES MAKE A FILE BINARY, TO grep AND file(1)"
printf 'a\000b\n' > nul.txt
for f in output.bin nul.txt; do
  if grep -I -q '' "$f"; then g=text; else g=binary; fi
  if iconv -f UTF-8 -t UTF-8 < "$f" > /dev/null 2>&1; then u=yes; else u=no; fi
  printf '   %-11s %-12s grep -I: %-7s valid UTF-8: %-4s file(1): %s\n' \
         "$f" "$(hx < "$f")" "$g" "$u" "$(file -b --mime-encoding "$f")"
done
echo "   nul.txt is valid UTF-8 - a NUL is the character U+0000 - and it is"
echo "   the one grep and file(1) call binary. output.bin is not UTF-8 at all,"
echo "   and both of them call it text. 'Binary' and 'not UTF-8' are two"
echo "   different questions: a decoder asks the second, and grep asks the"
echo "   first - which, in the C locale this script runs in, is a question"
echo "   about one byte value, 00."
