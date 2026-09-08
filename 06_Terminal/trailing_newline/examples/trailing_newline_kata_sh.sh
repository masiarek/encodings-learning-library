#!/usr/bin/env bash
# Answer key: one letter, two files, and four tools that disagree about them.
# Everything is xxd and wc, which are the same program on both platforms.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

printf 'a\n' > with.txt
printf 'a'   > without.txt

printf '   %-14s %-12s %-10s %-10s %s\n' file bytes 'wc -l' 'wc -c' 'last byte'
for f in with.txt without.txt; do
  printf '   %-14s %-12s %-10s %-10s %s\n' "$f" "$(xxd -p < $f)" \
    "$(wc -l < $f | tr -d ' ')" "$(wc -c < $f | tr -d ' ')" "$(tail -c1 $f | xxd -p)"
done
echo
echo "   without.txt holds a letter and reports ZERO LINES. wc -l does not"
echo "   count lines; it counts newline BYTES, which is the same number only"
echo "   for a file that ends in one. POSIX defines a line as ending in 0a, so"
echo "   wc is right and the file is, strictly, not text."
echo
echo "READING IT BACK IN A LOOP"
n=0; while read -r line; do n=$((n+1)); done < without.txt
echo "   while read < without.txt   iterations: $n"
n=0; while read -r line; do n=$((n+1)); done < with.txt
echo "   while read < with.txt      iterations: $n"
echo "   read returns false on the last piece when it hits EOF instead of a"
echo "   newline, so the loop body never runs for it. The data is not lost --"
echo "   the variable was set -- but the loop dropped it. This is the single"
echo "   most common way a last record vanishes from a shell pipeline."
echo
echo "CONCATENATION, WHICH IS WHERE IT SPREADS"
cat without.txt with.txt > joined.txt
printf '   cat without.txt with.txt -> %s   (one line: %s)\n' "$(xxd -p < joined.txt)" "$(head -1 joined.txt)"
echo "   Two files, one line. The missing byte did not stay in its own file;"
echo "   it merged two records. A CSV assembled this way has a row that is two"
echo "   rows, and nothing anywhere reports an error."
echo
echo "WHAT DREW THE SYMBOL YOUR SHELL SHOWED"
echo "   Nothing in the file. zsh prints a reverse-video % (bash prints"
echo "   nothing) when the cursor is not in column 1 at the end of output. It"
echo "   is your PROMPT saying the line was unfinished -- a fact about the"
echo "   terminal, not a byte you can grep for."
echo
echo "AND THE FIX, WHICH IS ONE BYTE"
echo "   printf 'a\\n'   writes it;  printf 'a'   does not."
echo "   echo appends one for you, which is why echo is the safer default for"
echo "   writing a line and printf the right tool for writing exact bytes."
