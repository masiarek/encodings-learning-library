#!/usr/bin/env bash
# The same few letters, stored the way each era would have stored them —
# with no language in between, just bytes on a pipe.
#
# Every conversion here is one the target table CAN represent. iconv's
# behaviour on a character its target has no room for differs between GNU and
# BSD (Linux refuses, macOS transliterates), so that half of the story is told
# by the Python example, where the failure is the same everywhere.
#
# Run:  bash from_telegraph_to_unicode_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

echo "1. 'café' AS EACH ERA WOULD HAVE WRITTEN IT TO DISK"
echo "   iconv converts; xxd -p prints the bytes that actually landed."
for enc in CP037 LATIN1 CP1252 CP437 UTF-8 UTF-16BE; do
  printf '   %-9s ' "$enc"
  printf 'caf\xc3\xa9' | iconv -f UTF-8 -t "$enc" | xxd -p
done
echo
echo "   CP037 is EBCDIC, and it does not agree even about the 'c'."
echo "   Three of the 8-bit tables give five bytes and disagree on the last."
echo "   UTF-8 is six bytes; UTF-16BE is eight, half of them 00."

echo
echo "2. A POLISH FILE FROM 2005, READ ON FOUR MACHINES"
echo "   'Łódź' written under Windows-1250, which is where it lived then:"
show "printf '\\xc5\\x81\\xc3\\xb3d\\xc5\\xba' | iconv -f UTF-8 -t CP1250 | xxd -p"
echo
echo "   Those same four bytes, decoded by someone whose machine assumed"
echo "   a different table — every one of these 'succeeds':"
for enc in CP1250 LATIN1 ISO-8859-2 CP1252 KOI8-R; do
  printf '   read as %-11s -> ' "$enc"
  printf '\xc5\x81\xc3\xb3d\xc5\xba' | iconv -f UTF-8 -t CP1250 | iconv -f "$enc" -t UTF-8
  echo
done
echo
echo "   Two of those readings look three letters long. They are not — the"
echo "   fourth byte decoded to an INVISIBLE control character. Only the bytes"
echo "   show it:"
show "printf '\\xc5\\x81\\xc3\\xb3d\\xc5\\xba' | iconv -f UTF-8 -t CP1250 | iconv -f LATIN1 -t UTF-8 | xxd -p"
echo "   c2 9f is U+009F, a C1 control, sitting where the 'ź' was."
echo
echo "   Four bytes, five readings, no error anywhere. The file does not carry"
echo "   its table, so 'which encoding is this?' has no answer from the bytes."

echo
echo "3. WHY UTF-8 COULD BE ADOPTED WITHOUT REWRITING ANYTHING"
show "printf 'Hello' | iconv -f UTF-8 -t ASCII | xxd -p"
show "printf 'Hello' | iconv -f UTF-8 -t UTF-8 | xxd -p"
echo "   Identical. An ASCII file already IS a UTF-8 file, byte for byte, so"
echo "   every tool that only knew ASCII kept working the day UTF-8 arrived."
echo "   The 1991 answer, UTF-16, could not say that:"
show "printf 'Hello' | iconv -f UTF-8 -t UTF-16BE | xxd -p"
echo "   Different bytes, and full of 00 — which is what ends a string in C."
echo "   Every existing tool would have had to be rewritten on the same day."
