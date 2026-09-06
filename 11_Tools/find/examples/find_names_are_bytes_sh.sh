#!/usr/bin/env bash
# find compares filenames as BYTES. Everything here is the same on macOS and on
# Ubuntu; the place where the two machines disagree is on the page, in a dated
# fence, because no answer key could hold both.
#
# Run:  bash find_names_are_bytes_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# 'żółw' — Polish for turtle — written two ways. Same word on screen.
nfc=$(printf '\305\274\303\263\305\202w')            # precomposed: ż ó ł w
nfd=$(printf 'z\314\207o\314\201\305\202w')          # decomposed: z+dot, o+acute, ł, w
printf 'turtle\n' > "$nfc"

echo "1. ONE WORD, TWO SPELLINGS, DIFFERENT BYTES"
echo -n "   NFC  ż ó ł w        : "; printf '%s' "$nfc" | xxd -p
echo -n "   NFD  z+ ̇ o+ ́ ł w     : "; printf '%s' "$nfd" | xxd -p
echo -n "   same on screen?     : "; [ "$nfc" = "$nfd" ] && echo "yes and equal" || echo "yes on screen, NOT equal as bytes"
echo "   Seven bytes against nine. A reader sees one word; every tool on this"
echo "   page sees two different names. This is normalization, and it is the"
echo "   reason the next section behaves the way it does."

echo
echo "2. -name IS A BYTE COMPARISON"
echo '$ find . -name <the NFC bytes>'
find . -name "$nfc"
echo '$ find . -name <the NFD bytes>; echo "exit $?"'
out=$(find . -name "$nfd"); st=$?
[ -n "$out" ] && printf '%s\n' "$out" || echo "   (printed nothing)"
echo "   exit $st"
echo "   The file exists. You typed its name. find matched nothing, because it"
echo "   compared your nine bytes against the seven on disk — and it still exits"
echo "   0, because find's status answers 'did the walk succeed', never 'did"
echo "   anything match'. There is no error to notice and no status to test."

echo
echo "3. WHAT find ACTUALLY PRINTED, IN HEX"
echo '$ find . -name "*w" | xxd -p'
find . -name '*w' | xxd -p
echo "   2e2f is './', then the seven bytes of the name, then 0a for the newline"
echo "   find added. There is no encoding in that stream — a filename is a bag"
echo "   of bytes with two forbidden values, 0x00 and 0x2f ('/'), and newline is"
echo "   not one of them."

echo
echo "4. WHICH IS WHY COUNTING LINES IS NOT COUNTING FILES"
mkdir sub && cd sub
touch "$(printf 'two\nlines')"
echo '   one file, whose name contains a newline'
echo -n '$ find . -type f | wc -l                      : '
find . -type f | wc -l | tr -d ' '
echo -n '$ find . -type f -print0 | tr -dc "\0" | wc -c : '
find . -type f -print0 | tr -dc '\0' | wc -c | tr -d ' '
echo "   Two against one. -print0 ends each name with the one byte that cannot"
echo "   occur inside a name, so the count is right and so is everything"
echo "   downstream: find … -print0 | xargs -0, and never find … | xargs."
cd ..

echo
echo "5. THE PATTERN IS BYTES TOO, SO GLOBBING IS BYTE GLOBBING"
echo '$ find . -name "*ó*"     # o + COMBINING ACUTE, two characters'
out=$(find . -name "*$(printf 'o\314\201')*")
[ -n "$out" ] && printf '%s\n' "$out" || echo "   (printed nothing)"
echo '$ find . -name "*ó*"     # U+00F3, one character'
out=$(find . -name "*$(printf '\303\263')*")
[ -n "$out" ] && printf '%s\n' "$out" || echo "   (printed nothing)"
echo "   Both patterns are the letter o with an acute accent. One is two"
echo "   characters, the other is one. Only the spelling on disk matches, and"
echo "   your keyboard decides which one you typed — on a Mac, an option-key"
echo "   accent and a paste from a web page can differ."

echo
echo "6. THE HABIT"
echo "   Search by the part you are sure of. ASCII substrings are safe:"
echo '$ find . -name "*w" -o -name "*.txt"'
find . -name '*w' -o -name '*.txt'
echo "   And when a name must be matched exactly, do not retype it — let the"
echo "   shell hand you the bytes that are already there:"
echo '$ for f in *; do find . -name "$f"; done'
for f in *; do find . -name "$f"; done
