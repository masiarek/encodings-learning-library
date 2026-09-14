#!/usr/bin/env bash
# Entropy is a histogram, and od | sort | uniq -c IS the histogram. The score
# Ghidra paints down the side of the Listing is one awk loop over that count,
# computed here on bytes printf writes, so the key is the same on both platforms.
#
# Run:  bash entropy_bar_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# The byte-value histogram of stdin: "count value", one line per value, values
# ascending. tr and the two seds absorb od's padding and uniq's, both of which
# differ between BSD and GNU.
hist() { od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d' | sort -n | uniq -c | sed 's/^ *//'; }

# The score: -sum p log2(p) over the histogram, summed in value order so the
# last digit does not depend on which awk this is. 0.00 for one value, 8.00 for
# all 256 equally often.
score() {
  hist | awk '{ c[NR] = $1; n += $1 }
              END { for (i = 1; i <= NR; i++) { p = c[i] / n; h -= p * log(p) / log(2) }
                    printf "%.2f\n", h }'
}

echo "1. THE HISTOGRAM IS THE WHOLE INPUT"
show "printf 'Hello, World!' | hist"
echo "   Thirteen bytes, ten values: l three times, o twice, eight once each."
echo "   Nothing about their order survives into this table, and the score is"
echo "   computed from the table alone:"
show "printf 'Hello, World!' | score"

echo
echo "2. THE SAME TEXT IN UTF-16LE"
show "printf 'Hello, World!' | iconv -f UTF-8 -t UTF-16LE | hist | head -1"
show "printf 'Hello, World!' | iconv -f UTF-8 -t UTF-16LE | score"
echo "   Twenty-six bytes now, and the first row of the histogram is the whole"
echo "   story: half of them are 00. Half the mass on one value pulls the"
echo "   score down, which is why UTF-16 text has a band of its own in"
echo "   Ghidra's palette, below ASCII's."

echo
echo "3. THE ENDS OF THE SCALE"
show "head -c 1024 /dev/zero | score"
show "for i in \$(seq 0 255); do printf \"\\\\\$(printf '%03o' \"\$i\")\"; done | score"
echo "   One value is 0.00. Every value, equally often, is 8.00 -- and this"
echo "   input is a counter, not noise. The scale measures spread, not"
echo "   randomness."

echo
echo "4. ORDER DOES NOT MATTER; THE ENCODING DOES"
show "printf 'abcabcabc' | score"
show "printf 'aaabbbccc' | score"
show "printf 'cbacbacba' | score"
show "printf 'Hello, World!' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | score"
echo "   Three arrangements of the same nine bytes, and ROT13 of section 1's"
echo "   string, all keep their score: a rearrangement or a one-to-one"
echo "   substitution leaves the histogram's heights alone. What changes the"
echo "   score is a different set of bytes for the same text:"
show "printf 'caf\\303\\251' | score"
show "printf 'caf\\351' | score"
echo "   café is five distinct bytes in UTF-8 and four in Latin-1, so the"
echo "   UTF-8 spelling scores log2(5) and the Latin-1 spelling log2(4). Short"
echo "   strings sit low on the scale whatever they hold; the named bands on"
echo "   the page are for chunks of a thousand bytes."
