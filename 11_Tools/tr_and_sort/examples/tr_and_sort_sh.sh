#!/usr/bin/env bash
# tr, sort, uniq and cut on text that is not ASCII. Everything here runs in the
# C locale — the library runner pins LC_ALL=C — where all four work a byte at a
# time. What changes when the locale changes is on the page, dated, because the
# two machines do not agree about it.
#
# Run:  bash tr_and_sort_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251 na\303\257ve\n' > two_words.txt          # café naïve
printf 'zebra\n\305\274aba\naaa\n\303\251clair\nEcho\n' > words.txt
printf '\305\273\303\223\305\201W\n' > shout.txt             # ŻÓŁW

echo "1. tr -d DELETES BYTES, AND THE BYTES ARE SHARED"
echo '$ cat two_words.txt'
cat two_words.txt
echo '$ xxd -p two_words.txt'
xxd -p two_words.txt
echo '$ tr -d "é" < two_words.txt'
tr -d 'é' < two_words.txt
echo '$ tr -d "é" < two_words.txt | xxd -p'
tr -d 'é' < two_words.txt | xxd -p
echo "   You asked it to delete é from café. It also damaged naïve, which"
echo "   contains no é at all. The hex says why: é is c3 a9 and ï is c3 af, and"
echo "   tr does not take a character — it takes a SET OF BYTES, here {c3, a9}."
echo "   In café both bytes were in the set, so the letter went. In naïve only"
echo "   the c3 was, so half of ï went and the orphaned af stayed. One word is"
echo "   short a letter; the other is no longer valid UTF-8 at all."

echo
echo "2. WHICH IS NOT A BUG, IT IS THE DOCUMENTED CONTRACT"
echo '$ printf "abc" | tr "abc" "xyz"'
printf 'abc' | tr 'abc' 'xyz'; echo
echo "   tr maps a set of single-byte values to another set of single-byte"
echo "   values. There is no multi-byte character in that description anywhere."
echo "   For anything above U+007F the tool you want is sed, which matches a"
echo "   whole pattern, not a byte set:"
echo '$ sed "s/é//" < two_words.txt | xxd -p'
sed 's/é//' < two_words.txt | xxd -p
echo "   café lost its é; naïve is untouched, and both are still valid UTF-8."

echo
echo "3. sort IN THE C LOCALE IS BYTE ORDER, NOT ALPHABETICAL ORDER"
echo '$ cat words.txt'
cat words.txt
echo '$ sort words.txt'
sort words.txt
echo "   Echo before aaa, because 'E' is 0x45 and 'a' is 0x61 — every capital"
echo "   sorts before every lowercase. And éclair and żaba are at the bottom,"
echo "   after every ASCII word, because their first byte is above 0x7f. This"
echo "   is a correct byte ordering and nobody's idea of alphabetical."

echo
echo "4. uniq COMPARES BYTES, SO TWO SPELLINGS ARE TWO VALUES"
printf '\305\274\303\263\305\202w\nz\314\207o\314\201\305\202w\n' > turtles.txt
echo '$ cat turtles.txt      # the same word twice, NFC then NFD'
cat turtles.txt
echo '$ sort turtles.txt | uniq -c | sed "s/^ *//"'
sort turtles.txt | uniq -c | sed 's/^ *//'
echo "   (the leading spaces are stripped — BSD and GNU uniq pad the count to"
echo "    different widths, which is the kind of thing this library records)"
echo "   Two groups of one. On the screen they are the same word; uniq is"
echo "   comparing seven bytes against nine. Normalize before you deduplicate,"
echo "   or the count is fiction."

echo
echo "5. cut -c AND cut -b, AND WHY THE HONEST ONE IS -b"
echo '$ cut -c1-4 < two_words.txt | xxd -p'
cut -c1-4 < two_words.txt | xxd -p
echo '$ cut -b1-4 < two_words.txt | xxd -p'
cut -b1-4 < two_words.txt | xxd -p
echo "   Identical here, because in the C locale a character IS a byte, and both"
echo "   cut through the middle of é: 63 61 66 c3 is three letters and half of a"
echo "   fourth. -b promises bytes and keeps the promise everywhere; -c promises"
echo "   characters and delivers bytes whenever the locale is not a UTF-8 one."
echo "   For fixed-width records, -b is the one that means what you meant."

echo
echo "6. tr AND CASE: [:upper:] IS AN ASCII PROMISE HERE"
echo '$ cat shout.txt'
cat shout.txt
echo '$ tr "[:upper:]" "[:lower:]" < shout.txt'
tr '[:upper:]' '[:lower:]' < shout.txt
echo "   ŻÓŁw. Exactly one letter changed — the ASCII W — because in the C"
echo "   locale [:upper:] is A-Z and none of Ż, Ó, Ł is in it. That is the worst"
echo "   possible outcome: not a refusal, not a conversion, a word that is now"
echo "   half lowercased and looks like a typo rather than an encoding bug."
echo "   In a UTF-8 locale the two machines this library runs on give two"
echo "   different answers to this same command — the page has both."
