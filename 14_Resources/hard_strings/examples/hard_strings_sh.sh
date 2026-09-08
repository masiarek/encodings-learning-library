#!/usr/bin/env bash
# The corpus on a pipe, where every tool is a byte matcher.
#
# The Python and Rust examples ask what a language can do about these strings.
# This one asks the question a data pipeline actually faces: they arrive as
# bytes in a file, and the tools that will touch them next -- sort, uniq, grep,
# iconv -- have no normalization, no case folding, and no opinion. So the
# answer is short, and worth seeing rather than being told.
#
# Every string below is written with \xHH byte escapes, which name bytes and
# ask nothing of the locale, so this script contains no non-ASCII character
# at all and still writes the whole corpus.
#
# Run: bash hard_strings_sh.sh

bar="------------------------------------------------------------------------"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp" || exit 1

echo
echo "1. FOUR SPELLINGS ARRIVE AS FOUR LINES"
echo "$bar"
{
  printf 'r\xc3\xa9sum\xc3\xa9\n'       # A  both accents precomposed
  printf 'r\xc3\xa9sume\xcc\x81\n'      # B  second one decomposed
  printf 're\xcc\x81sum\xc3\xa9\n'      # C  first one decomposed
  printf 're\xcc\x81sume\xcc\x81\n'     # D  both decomposed
} > names.txt
xxd names.txt
echo
# awk's length() counts bytes under LC_ALL=C, which is what every example here
# runs under -- so this is the byte count and not a character count.
printf '   %-34s %s\n' 'bytes per line, newline included' \
  "$(awk '{ printf "%s ", length($0) + 1 }' names.txt | sed 's/ $//')"
echo
echo "   Four byte counts for one word. Nothing in that file is malformed"
echo "   and nothing in it is unusual; it is one name, typed on four"
echo "   machines."
echo

echo "2. sort -u IS THE DEDUPE EVERY PIPELINE USES"
echo "$bar"
printf '   %-34s %s\n' 'lines in the file' "$(grep -c '' names.txt)"
printf '   %-34s %s\n' 'after sort -u' "$(sort -u names.txt | grep -c '')"
echo
composed=$(printf 'r\xc3\xa9sum\xc3\xa9')
prefix=$(printf 'r\xc3\xa9sum')
printf '   %-34s %s\n' 'grep -c for the whole word' "$(grep -c "$composed" names.txt)"
printf '   %-34s %s\n' 'grep -c for its first five' "$(grep -c "$prefix" names.txt)"
echo
echo "   One of four, then two of four. The prefix search finds the spellings"
echo "   whose FIRST accent is precomposed and misses the two whose is not --"
echo "   and the letter it disagrees about is not the letter you searched for."
echo "   A report built this way is not wrong in a way anybody will notice."
echo

echo "3. VALID IS NOT THE SAME AS SAME"
echo "$bar"
iconv -f UTF-8 -t UTF-8 names.txt > /dev/null 2>&1
printf '   %-34s %s\n' 'iconv -f UTF-8 -t UTF-8, exit' "$?"
echo
echo "   Zero: all four lines are well-formed UTF-8, because they are. A"
echo "   validator answers a question about bytes and this is a question"
echo "   about meaning, so no amount of validation upstream will help."
echo

echo "4. THE ONE THE EYE CANNOT AUDIT"
echo "$bar"
{
  printf 'admin\n'
  printf 'ad\xe2\x80\x8bmin\n'          # a ZERO WIDTH SPACE in the middle
} > users.txt
xxd users.txt
echo
printf '   %-34s %s\n' 'grep -c for the exact line' "$(grep -c '^admin$' users.txt)"
printf '   %-34s %s\n' 'after sort -u' "$(sort -u users.txt | grep -c '')"
echo
echo "   Two accounts. Printed to a terminal, pasted into a ticket, or read"
echo "   off a screenshot they are the same five letters -- the three bytes"
echo "   E2 80 8B draw nothing at all. The only place the difference exists"
echo "   is the hex dump above."
echo

echo "5. WHAT THE SHELL CAN AND CANNOT DO HERE"
echo "$bar"
echo "   Everything in this script ran under LC_ALL=C, where sort and grep"
echo "   are pure byte matchers -- which is the right setting for auditing"
echo "   unknown data, and is what makes the output above the same on every"
echo "   machine. Turning the locale up does not fix any of it: a UTF-8"
echo "   locale teaches these tools about character boundaries and collation"
echo "   order, and none of the five sections above is a boundary question."
echo
echo "   So the shell's honest job with this corpus is to SHOW it -- xxd, and"
echo "   the byte counts -- and to hand the merging decision to a program"
echo "   that has a Unicode table. Reach for sort -u to find duplicates and"
echo "   you will get an answer; it just will not be about names."
