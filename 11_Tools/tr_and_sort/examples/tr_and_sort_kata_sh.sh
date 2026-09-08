#!/usr/bin/env bash
# Answer key: delete one letter, damage two words.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251 na\303\257ve\n' > f     # café naïve

echo "THE FILE"
printf '   text  %s\n' "$(cat f)"
printf '   bytes %s\n' "$(xxd -p < f)"
printf '   é is %s and ï is %s\n' "$(printf '\303\251' | xxd -p)" "$(printf '\303\257' | xxd -p)"
echo
echo "1. tr -d 'é'"
out=$(tr -d 'é' < f)
printf '   result %-14s bytes %s\n' "$out" "$(printf '%s' "$out" | xxd -p)"
echo "   naïve lost a byte too. tr was never handed a character: it was handed"
echo "   the byte SET {c3, a9}, and it deletes every occurrence of either. ï is"
echo "   c3 af, so its c3 matched and vanished -- leaving af, which is not a"
echo "   valid UTF-8 sequence on its own. The output is no longer text."
echo
echo "2. sed 's/é//' ON THE SAME FILE"
out=$(sed 's/é//' < f)
printf '   result %-14s bytes %s\n' "$out" "$(printf '%s' "$out" | xxd -p)"
echo "   Correct, and it is not because sed knows about characters. sed was"
echo "   given a two-byte SEQUENCE to match -- c3 then a9, in that order -- and"
echo "   c3 af does not match it. A sequence has an order; a set does not."
echo "   That difference survives the C locale, where neither tool knows what a"
echo "   character is."
echo
echo "3. THE SAME SHAPE IN sort AND uniq"
printf 'b\na\n\303\251\nB\n' > g
printf '   sort:  %s\n' "$(LC_ALL=C sort g | tr '\n' ' ')"
echo "   In the C locale sort compares BYTES, so uppercase sorts before"
echo "   lowercase and é lands after everything -- e9 and c3 are just numbers."
echo "   Change the locale and the order changes, because collation is the one"
echo "   thing sort does ask the environment about."
echo
echo "4. AND cut -c, WHICH HAS NO ESCAPE AT ALL"
printf '   cut -b1-4: %s\n' "$(cut -b1-4 < f | xxd -p)"
echo "   Four bytes: 63 61 66 c3. The last one is half a character, so the"
echo "   output is not text -- and -b is the HONEST flag here, because it says"
echo "   bytes. -c claims characters and the two cuts disagree about whether it"
echo "   delivers them."
echo
echo "THE RULE"
echo "   Ask whether a tool takes a SET of bytes or a SEQUENCE. tr, cut -b and"
echo "   sort take sets or offsets and cannot see a multi-byte character. sed,"
echo "   grep and awk take patterns, which have order, and get this right even"
echo "   when they have no idea what a character is."
