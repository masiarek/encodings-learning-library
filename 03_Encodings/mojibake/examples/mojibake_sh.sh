#!/usr/bin/env bash
# The hex dump that ends the argument.
#
# Mojibake arguments go in circles because both sides are describing what they
# SEE. The bytes settle it, and a shell is the shortest way to look at them.
# This script makes the damage on a pipe, shows the file growing with each
# layer, repairs it, and ends with the two byte patterns that tell you which
# side of an interface to go and talk to.
#
# Run:  bash mojibake_sh.sh
#
# Deliberately NOT shown: `iconv -c` (drop the bad bytes). On invalid input
# macOS iconv stops at the first bad byte and GNU iconv skips it and keeps
# going, so the same "repair" writes two different files and there is no single
# answer key. Every conversion below targets a table that can hold its input.

set -u

CAFE='caf\xc3\xa9'   # "café" written correctly as UTF-8

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }
bug()    { iconv -f ISO-8859-1 -t UTF-8; }   # read UTF-8 bytes as Latin-1, write UTF-8
unbug()  { iconv -f UTF-8 -t ISO-8859-1; }   # the exact inverse

say "1. WHAT IS ON DISK, AND WHAT THE READER MADE OF IT"
printf '   on disk, written by a program that got it right:\n'
printf "$CAFE" | xxd | sed 's/^/     /'
printf '\n   what a reader using the wrong table then produced:\n'
printf "$CAFE" | bug | xxd | sed 's/^/     /'
printf '\n   Both are real files. The first is café. The second is what you get\n'
printf '   when the first is read as Latin-1 and written back out as UTF-8 --\n'
printf '   and it is the second one that arrives in the bug report.\n'

say "2. EACH LAYER MAKES THE FILE LONGER"
data=$(printf "$CAFE" | xxd -p)
for layer in 0 1 2 3; do
    n=$(printf '%s' "$data" | xxd -r -p | wc -c | tr -d ' ')
    printf '   %d layer(s): %-40s %s bytes\n' "$layer" "$data" "$n"
    data=$(printf '%s' "$data" | xxd -r -p | bug | xxd -p)
done
printf '\n   Five bytes, seven, eleven, nineteen. A field that keeps overflowing\n'
printf '   its column every time the file is copied is this, on every hop.\n'

say "3. THE REPAIR IS THE INVERSE -- AND ONE STEP TOO FAR"
broken=$(printf "$CAFE" | bug | bug | xxd -p)
printf '   found:      %s   (2 layers)\n' "$broken"
for repair in 1 2 3; do
    next=$(printf '%s' "$broken" | xxd -r -p | unbug 2>/dev/null | xxd -p)
    printf '%s' "$broken" | xxd -r -p | unbug >/dev/null 2>&1
    printf '   repair %d:   %-24s iconv exit %d\n' "$repair" "$next" "$?"
    broken="$next"
done
printf '%s' "$broken" | xxd -r -p | unbug >/dev/null 2>&1
printf '   repair 4:   %-24s iconv exit %d\n' "(refused)" "$?"
printf '\n   Read that carefully: repair 2 got the original five bytes back, and\n'
printf '   repair 3 SUCCEEDED anyway -- turning a correct UTF-8 file into a\n'
printf '   correct Latin-1 one. iconv does not stop where you want it to,\n'
printf '   because -t ISO-8859-1 works on any text Latin-1 can hold.\n'
printf '   The Python loop on this page does stop, and only because its repair\n'
printf '   ENDS in a UTF-8 decode, which the four bytes 63 61 66 e9 fail.\n'
printf '   So: count the layers first. "Repair until it errors" is a Python\n'
printf '   trick and it does not transfer to the command line.\n'

say "4. THE TWO BYTE PATTERNS, AND WHO TO GO AND TALK TO"
printf '   c3 a9  in the file  ->  the file IS UTF-8. The bytes are right and the\n'
printf '                           READER was told the wrong table. Fix the reader.\n'
printf "$CAFE" | xxd | sed 's/^/     /'
printf '\n   e9     in the file  ->  the file is Latin-1 (or 1252, or 1250...). The\n'
printf '                           WRITER used a different table. Fix the writer,\n'
printf '                           or tell the reader the truth.\n'
printf "$CAFE" | unbug | xxd | sed 's/^/     /'
printf '\n   That is the whole diagnosis, and it takes one xxd. Neither dump is\n'
printf '   damaged -- and neither one knows which of them was intended.\n'
