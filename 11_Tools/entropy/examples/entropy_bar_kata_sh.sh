#!/usr/bin/env bash
# The kata's answer key: five chunks, their scores, and the name Ghidra's four
# default ranges would give each. Same histogram and awk as the lesson's shell
# example; the bands are the integer ones the Rust example derives.
#
# Run:  bash entropy_bar_kata_sh.sh
set -eu

hist() { od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d' | sort -n | uniq -c | sed 's/^ *//'; }

# Prints "score  name": the score to two decimals, then the first of Ghidra's
# default slots -- compressed, x86, ascii, utf16 -- whose band holds
# floor(score x 32), or "-" when none does.
score() {
  hist | awk '{ c[NR] = $1; n += $1 }
              END { for (i = 1; i <= NR; i++) { p = c[i] / n; h -= p * log(p) / log(2) }
                    i = int(h * 32); if (i > 255) i = 255
                    name = "-"
                    if      (i >= 239 && i <= 256) name = "compressed"
                    else if (i >= 178 && i <= 203) name = "x86"
                    else if (i >= 134 && i <= 167) name = "ascii"
                    else if (i >=  96 && i <= 109) name = "utf16"
                    printf "%.2f  %s\n", h, name }'
}

echo "1. 1024 bytes of 00"
head -c 1024 /dev/zero | score

echo "2. 'ab', 512 times over"
yes ab | tr -d '\n' | head -c 1024 | score

echo "3. every byte value, four times over"
for pass in 1 2 3 4; do
  for i in $(seq 0 255); do printf "\\$(printf '%03o' "$i")"; done
done | score

echo "4. 'Hello, World!' in UTF-8, then in UTF-16LE"
printf 'Hello, World!' | score
printf 'Hello, World!' | iconv -f UTF-8 -t UTF-16LE | score

echo "5. 'café' in UTF-8, then in Latin-1"
printf 'caf\303\251' | score
printf 'caf\351' | score
