#!/usr/bin/env bash
# awk on text that is not ASCII, in the C locale — where all three awks in
# common use agree. They stop agreeing the moment the locale is a UTF-8 one,
# and that table is on the page, because no answer key could hold it.
#
# Run:  bash awk_counts_bytes_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251\n' > cafe.txt                       # café: 4 chars, 5 bytes
printf 'Ada,caf\303\251,3\nBen,na\303\257ve,7\n' > rows.csv
printf '\305\273\303\223\305\201W\n' > shout.txt        # ŻÓŁW

echo "1. WHICH awk IS THIS? THE ANSWER IS NOT THE SAME ON TWO MACHINES"
echo "   macOS ships the one-true-awk (BWK awk); Ubuntu ships mawk; gawk is"
echo "   what many people mean by 'awk' and is on neither by default. This"
echo "   script prints nothing about which one it is, because the identity is"
echo "   exactly what differs — and in THIS locale all three agree anyway."

echo
echo "2. length() COUNTS BYTES HERE"
echo '$ cat cafe.txt'
cat cafe.txt
echo '$ awk "{print length(\$0)}" cafe.txt'
awk '{print length($0)}' cafe.txt
echo "   Four characters on screen, five from length(). In the C locale that"
echo "   is every awk's answer. In a UTF-8 locale it is still mawk's and still"
echo "   BWK awk's, and gawk says 4 — see the page."

echo
echo "3. substr() CUTS WHERE length() COUNTS, SO IT CUTS INSIDE A CHARACTER"
echo '$ awk "{printf \"%s\", substr(\$0,1,4)}" cafe.txt | xxd -p'
awk '{printf "%s", substr($0,1,4)}' cafe.txt | xxd -p
echo "   63 61 66 c3 — 'caf' and the FIRST HALF of é. The output is no longer"
echo "   valid UTF-8, and awk neither warned nor failed. This is the same shape"
echo "   as cut -b and as a fixed-width field: an offset is a byte offset."

echo
echo "4. gsub(/./) AGREES WITH length() — IN THIS LOCALE"
echo '$ awk "{n=gsub(/./,\"X\"); print n, \$0}" cafe.txt'
awk '{n=gsub(/./,"X"); print n, $0}' cafe.txt
echo "   Five. Both the regex engine and length() are counting bytes, so they"
echo "   agree. On one of the three awks, in a UTF-8 locale, they stop agreeing"
echo "   with EACH OTHER inside a single program. That is the page's point."

echo
echo "5. toupper() IS AN ASCII PROMISE HERE"
echo '$ awk "{print toupper(\$0)}" cafe.txt'
awk '{print toupper($0)}' cafe.txt
echo '$ awk "{print tolower(\$0)}" shout.txt'
awk '{print tolower($0)}' shout.txt
echo "   café became CAFé and ŻÓŁW became ŻÓŁw: the ASCII letters changed and"
echo "   nothing else did. Half a word case-mapped is worse than none, because"
echo "   it reads as a typo rather than as an encoding problem."

echo
echo "6. WHAT DOES WORK PERFECTLY: FIELDS WITH AN ASCII SEPARATOR"
echo '$ cat rows.csv'
cat rows.csv
echo '$ awk -F, "{print \$1 \" wants \" \$2}" rows.csv'
awk -F, '{print $1 " wants " $2}' rows.csv
echo "   Splitting on a comma and moving whole fields around never looks inside"
echo "   a character, so it is safe at any width in any locale. Most awk in the"
echo "   world is this, which is why the trap above stays hidden for years."

echo
echo "7. COUNTING CHARACTERS PORTABLY, WITHOUT A LOCALE"
echo '$ awk "{n=\$0; c=gsub(/[\\200-\\277]/,\"\",n); print length(\$0)-c}" cafe.txt'
awk '{n=$0; c=gsub(/[\200-\277]/,"",n); print length($0)-c}' cafe.txt
echo "   Four — the right answer, from an awk that thinks in bytes. UTF-8's"
echo "   design is what makes it possible: continuation bytes are exactly"
echo "   0x80-0xBF and nothing else uses that range, so bytes minus"
echo "   continuation bytes is the character count. It works on all three awks"
echo "   in any locale, which no built-in can claim."
