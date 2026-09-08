#!/usr/bin/env bash
# Answer key: two files that print the same, and four ways to ask if they match.
# Only exit STATUS is recorded for cmp: its diagnostics go to stderr and the two
# implementations word them differently.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251\n'  > nfc.txt
printf 'cafe\314\201\n' > nfd.txt

st() { local s=0; "$@" >/dev/null 2>&1 || s=$?; echo "$s"; }

echo "TWO FILES THAT DRAW IDENTICALLY"
printf '   nfc.txt  %-16s %s\n' "$(xxd -p < nfc.txt)" "$(cat nfc.txt)"
printf '   nfd.txt  %-16s %s\n' "$(xxd -p < nfd.txt)" "$(cat nfd.txt)"
printf '   lengths: %s and %s bytes\n' "$(wc -c < nfc.txt|tr -d ' ')" "$(wc -c < nfd.txt|tr -d ' ')"
echo
echo "FOUR QUESTIONS"
printf '   cmp -s              exit %s   same BYTES?           no\n' "$(st cmp -s nfc.txt nfd.txt)"
printf '   diff                exit %s   same LINES as bytes?  no\n' "$(st diff nfc.txt nfd.txt)"
printf '   diff -i             exit %s   ASCII case folded -- irrelevant here\n' "$(st diff -i nfc.txt nfd.txt)"
printf '   diff -w             exit %s   whitespace ignored -- also irrelevant\n' "$(st diff -w nfc.txt nfd.txt)"
echo
echo "   Every flag says different, and none of them is asking the question you"
echo "   meant. diff splits at 0a and compares the byte strings between; those"
echo "   two byte strings are not equal; there is no flag for 'same text,"
echo "   however spelled', because that needs a normalization POLICY that diff"
echo "   has no business choosing."
echo
echo "WHAT diff PRINTS, WHICH IS THE CONFUSING PART"
diff nfc.txt nfd.txt | sed 's/^/   /'
echo "   Both sides look identical on your screen, because your terminal draws"
echo "   both spellings the same way. diff is not malfunctioning; it is"
echo "   reporting a difference the screen cannot show."
echo
echo "THE THREE EXIT STATUSES, AND THE BUG THEY CAUSE"
printf '   same file       exit %s\n' "$(st diff nfc.txt nfc.txt)"
printf '   files differ    exit %s\n' "$(st diff nfc.txt nfd.txt)"
printf '   missing file    exit %s\n' "$(st diff nfc.txt no_such_file)"
echo "   0, 1, 2. So 'if diff a b; then ...' takes the SAME branch for 'they"
echo "   differ' and 'one of them does not exist', unless you test for 2."
echo
echo "THE FIX IS A DECODE, NOT A FLAG"
echo "   Normalize both sides first -- unicodedata.normalize in Python, uconv"
echo "   -x nfc from icu4c -- and then compare. Normalizing to COMPARE is fine;"
echo "   normalizing in place is an edit to somebody's data."
