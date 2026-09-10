#!/usr/bin/env bash
# Kata solution: four files, three readers that look at the bytes, and a
# rename that none of them can see.
#
# Every column is an exit status, a count, or file --mime-encoding, and all
# of them were identical on macOS 26.6.2 and ubuntu:24.04 on 2026-09-10. The
# "NUL in first 8000" column is git's rule, applied here by hand rather than by
# running git: buffer_is_binary() in git's xdiff-interface.c looks for a zero
# byte in the first 8000 and nothing else.
#
# Run:  bash binary_or_text_kata_sh.sh
set -u
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

hx() { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }

printf '\300\377\356'   > coffee.txt
printf 'caf\303\251\n'  > notes.bin
printf 'caf\351\n'      > legacy.txt
printf 'a\000b\n'       > data.txt

table() {
  printf '   %-11s %-19s %-12s %-18s %s\n' "file" "bytes" "valid UTF-8" "NUL in first 8000" "file(1)"
  for f in "$@"; do
    if iconv -f UTF-8 -t UTF-8 < "$f" > /dev/null 2>&1; then u=yes; else u=no; fi
    n=$(head -c 8000 "$f" | tr -dc '\000' | wc -c | tr -d ' ')
    if [ "$n" -gt 0 ]; then z=yes; else z=no; fi
    printf '   %-11s %-19s %-12s %-18s %s\n' "$f" "$(hx < "$f")" "$u" "$z" "$(file -b --mime-encoding "$f")"
  done
}

echo "1. FOUR FILES, TWELVE ANSWERS"
table coffee.txt notes.bin legacy.txt data.txt

echo
echo "2. RENAME ALL FOUR TO .dat, AND ASK AGAIN"
for f in coffee.txt notes.bin legacy.txt data.txt; do mv "$f" "${f%.*}.dat"; done
table coffee.dat notes.dat legacy.dat data.dat
echo "   Not one of the twelve answers moved. Each reader opened the file and"
echo "   looked at bytes, and none of them was ever told the file's name."

echo
echo "3. THE TWO THAT SURPRISE"
echo "   data is VALID UTF-8 - a NUL is the character U+0000 - and it is the"
echo "   only one of the four that git's rule and file(1) call binary."
echo "   legacy is NOT valid UTF-8, and both of them call it text."
echo "   'Binary' and 'not UTF-8' are two different questions. A decoder asks"
echo "   the second. git's rule asks the first, and for git the first is a"
echo "   question about a single byte value, 00 - on all four files file(1)"
echo "   gave the same verdict."
