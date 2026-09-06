#!/usr/bin/env bash
# cut on text that is not ASCII, in the C locale — where -c and -b are the same
# thing and both platforms agree. In a UTF-8 locale they stop being the same
# thing on ONE of the two platforms, which is on the page in a dated fence.
#
# Run:  bash cut_by_byte_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251 bar\n' > cafe.txt                       # café bar
printf 'Ada,caf\303\251,3\nBen,na\303\257ve,7\n' > rows.csv
printf 'ADA  caf\303\251      003\n' > fixed.txt            # a fixed-width record
printf 'a\342\200\242b\n' > bullet.txt                      # a•b, • is 3 bytes

echo "1. -c AND -b, ON THE SAME FILE, IN THIS LOCALE"
echo '$ cat cafe.txt'
cat cafe.txt
echo '$ xxd -p cafe.txt'
xxd -p cafe.txt
echo '$ cut -c1-4 cafe.txt | xxd -p'
cut -c1-4 cafe.txt | xxd -p
echo '$ cut -b1-4 cafe.txt | xxd -p'
cut -b1-4 cafe.txt | xxd -p
echo "   Identical, and both wrong in the same way: 63 61 66 c3 is 'caf' plus"
echo "   the first byte of é. The output is not valid UTF-8 and cut said"
echo "   nothing. In the C locale a character IS a byte, so -c and -b are the"
echo "   same flag — which is exactly why the difference between them is so"
echo "   easy to never notice."

echo
echo "2. THE PROMISE IN THE MANUAL"
echo "   -b selects BYTES. -c selects CHARACTERS. Those are different words for"
echo "   a reason, and only one of the two cuts on your PATH keeps the second"
echo "   promise, and only in a UTF-8 locale. The page has the measurement."
echo "   The rule that survives it: if you mean bytes, write -b; if you mean"
echo "   characters, do not use cut."

echo
echo "3. FIELDS ARE SAFE — THE DELIMITER IS WHAT MATTERS, NOT THE CONTENT"
echo '$ cat rows.csv'
cat rows.csv
echo '$ cut -d, -f2 rows.csv'
cut -d, -f2 rows.csv
echo "   Whole fields, comma-delimited, and the accented text inside them comes"
echo "   through untouched. cut never looks inside a field, so -d/-f is safe at"
echo "   any width. Nearly all real cut usage is this."

echo
echo "4. BUT THE DELIMITER ITSELF MUST BE ONE BYTE"
echo '$ cat bullet.txt        # a bullet, three bytes: e2 80 a2'
cat bullet.txt
echo '$ cut -d"•" -f2 bullet.txt'
if cut -d'•' -f2 bullet.txt 2>/dev/null; then
  echo "   (it ran)"
else
  echo "   (refused — exit $?)"
fi
echo "   Both cuts refuse here, wording it differently, so only the status is"
echo "   shown. A multi-byte delimiter is not a thing cut can take in this"
echo "   locale — and when a field separator is a real character rather than a"
echo "   comma, awk -F is the tool that will take it."

echo
echo "5. THE FIXED-WIDTH RECORD, WHICH IS WHERE THIS BITES FOR REAL"
echo '$ cat fixed.txt'
cat fixed.txt
echo '$ xxd -p fixed.txt'
xxd -p fixed.txt
echo "   The layout was designed in CHARACTERS, the way a person counts:"
echo "     name 1-5, description 6-15, code 16-18   (18 characters of record)"
echo '$ cut -b1-5 fixed.txt   | xxd -p      # name: correct'
cut -b1-5 fixed.txt | xxd -p
echo '$ cut -b16-18 fixed.txt                # code: should be 003'
cut -b16-18 fixed.txt
echo "   It printed ' 00'. The code field is one byte late, and every field"
echo "   after the é is, because é costs two bytes and the layout budgeted one"
echo "   character. The record is 18 characters and 19 bytes, so the byte"
echo "   columns for the code are 17-19, not 16-18:"
echo '$ cut -b17-19 fixed.txt'
cut -b17-19 fixed.txt
echo "   Both cuts do this identically, and neither reports anything: you get a"
echo "   field, it is the wrong field, and it is only obviously wrong because"
echo "   this record ends in digits. Had the code been letters you would have"
echo "   shipped it. The offset is correct until the first non-ASCII character"
echo "   in the record and wrong for everything after it, which is why these"
echo "   bugs surface months later, on one customer's data."
echo
echo "6. COUNTING CHARACTERS WITHOUT cut"
echo -n '   wc -c (bytes)      : '; wc -c < cafe.txt | tr -d ' '
echo -n '   wc -m (this locale): '; wc -m < cafe.txt | tr -d ' '
echo "   Both say the same number here, because in the C locale wc -m is also"
echo "   counting bytes. Two flags, one answer, and no warning that the"
echo "   question you asked was not the question that got answered."
