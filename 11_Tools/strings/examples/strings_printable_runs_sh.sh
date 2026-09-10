#!/usr/bin/env bash
# strings does not look for text. It prints every run of four or more bytes
# from a set it calls printable, and on every build measured here that set is
# ASCII — so an accent ends a word and UTF-16 disappears.
#
# Everything below is byte-identical on macOS (Apple's strings) and Ubuntu
# (GNU binutils), because it stays inside the part the two agree on: input on
# STDIN, the C locale, and no tab. The page has the table of where they part.
#
# Run:  bash strings_printable_runs_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# Print a line of decimal byte values as hex ranges: "32 33 34 36" -> "20-22 24".
ranges() {
  awk 'function fmt(a, b) { return a == b ? sprintf("%02x", a) : sprintf("%02x-%02x", a, b) }
       { for (i = 1; i <= NF; i++) {
           v = $i + 0
           if (have && v == last + 1) { last = v; continue }
           if (have) out = out (out == "" ? "" : " ") fmt(first, last)
           first = v; last = v; have = 1
       } }
       END { if (have) out = out (out == "" ? "" : " ") fmt(first, last); print out }'
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'hello\000\001\002world\n' > zoo.bin                     # two runs and three bytes between them
printf 'Hello, World!\n' | iconv -f UTF-8 -t UTF-16LE > u16.txt   # readable text, 28 bytes

echo "1. FOUR PRINTABLE BYTES IN A ROW, OR NOTHING"
show "strings < zoo.bin"
echo "   Two runs, two lines. The three bytes between them — 00 01 02 — are"
echo "   not printed, not replaced and not mentioned: a byte outside the set"
echo "   simply ends the run it interrupted. That is the whole algorithm."
show "printf 'ab\\000cde\\000fghi\\n' | strings"
echo "   Runs of two and three bytes vanish without a word, because the"
echo "   default minimum is four. -n moves the minimum and changes nothing else:"
show "printf 'ab\\000cde\\000fghi\\n' | strings -n 2"

echo
echo "2. WHICH BYTES KEEP A RUN GOING"
echo "   Each byte value in turn, between 'abcd' and 'efgh': one line back means"
echo "   strings counted the byte as printable, two lines means it ended the run."
keep=""; split=""
for i in $(seq 0 255); do
  case $i in 9|10) continue ;; esac   # tab and newline: see below
  o=$(printf '%03o' "$i")
  n=$(printf "abcd\\${o}efgh\\n" | strings | wc -l | tr -d ' ')
  if [ "$n" = 1 ]; then keep="$keep $i"; else split="$split $i"; fi
done
set -- $keep;  nk=$#
set -- $split; ns=$#
printf '   %-20s %-18s %3d byte values\n' "keeps the run going" "$(echo $keep | ranges)" "$nk"
printf '   %-20s %-18s %3d byte values\n' "ends the run" "$(echo $split | ranges)" "$ns"
echo "   Ninety-five bytes, and they are exactly printable ASCII: space through"
echo "   tilde. Every byte from 80 to ff ends a run — and those are the only"
echo "   bytes UTF-8 uses for anything that is not ASCII. Two values were left"
echo "   out on purpose: newline, which ends a line everywhere, and tab, the one"
echo "   byte these two builds disagree about. The page has that table."

echo
echo "3. AN ACCENT ENDS A WORD"
show "printf 'caf\\303\\251 bar\\n' | strings | cat -vet"
echo "   café is c a f, then c3 a9. The run 'caf' is three bytes and is dropped;"
echo "   c3 and a9 are outside the set; ' bar' is four bytes, so it survives —"
echo "   with its leading space, which cat -vet makes visible. The word you were"
echo "   looking for is exactly the part that is missing."
show "printf 'caf\\351 bar\\n' | strings | cat -vet"
echo "   The same words in Latin-1 are one byte shorter and get the same answer:"
echo "   strings is not refusing UTF-8, it is refusing everything above 7e."
show "printf '\\305\\274\\303\\263\\305\\202w\\n' | strings | wc -c | tr -d ' '"
echo "   żółw: four letters in seven bytes, and nothing comes back. Three of the"
echo "   letters take two bytes each, all six of those bytes are above 7e, and"
echo "   the w left over is a run of one."

echo
echo "4. UTF-16 IS INVISIBLE TO IT"
show "xxd u16.txt"
echo "   Every ASCII letter in UTF-16LE is followed by a 00 byte, so no two"
echo "   printable bytes are ever next to each other:"
show "strings < u16.txt | wc -c | tr -d ' '"
echo "   Twenty-eight bytes of readable text, and nothing. Decode first, and"
echo "   strings has runs to find:"
show "iconv -f UTF-16LE -t UTF-8 u16.txt | strings"

echo
echo "5. WHAT IT THREW AWAY, AND HOW TO GET IT BACK"
show "strings -t d < zoo.bin | sed 's/^ *//'"
echo "   -t d puts each run's byte offset in front of it. (The sed removes a"
echo "   padding difference: one build right-aligns the number and the other"
echo "   does not.) The number is the part of each line that strings made up,"
echo "   and it is the part xxd needs to show you what surrounded the run:"
show "xxd -s 5 -l 3 zoo.bin"
echo "   The three bytes between the runs, which strings never mentioned."
