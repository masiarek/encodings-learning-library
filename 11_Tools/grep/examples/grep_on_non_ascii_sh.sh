#!/usr/bin/env bash
# What grep does with text that is not ASCII — the parts that are the same on
# every machine. The parts that are NOT the same are on the page, in a fence
# labelled with the two machines they were measured on.
#
# Everything here runs in the C locale, which is what the library's runner pins
# (LC_ALL=C). That is not a limitation of the demo: in the C locale grep works a
# byte at a time, and a byte at a time is the honest starting point.
#
# Run:  bash grep_on_non_ascii_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251\n' > cafe.txt                                  # café
printf 'plain ascii\ncaf\303\251 here\nmore ascii\n' > mixed.txt
printf 'hello\000world\nhello again\n' > withnul.txt               # one NUL byte
printf 'caf\303\251\n' | iconv -f UTF-8 -t UTF-16LE > body.bin
printf '\377\376' | cat - body.bin > u16.txt                       # UTF-16LE + BOM

echo "1. IN THE C LOCALE, A 'CHARACTER' IS A BYTE"
echo '$ cat cafe.txt'
cat cafe.txt
echo '$ xxd -p cafe.txt'
xxd -p cafe.txt
echo '$ grep -o . cafe.txt | wc -l'
grep -o . cafe.txt | wc -l | tr -d ' '
echo "   Four characters on the screen. Five answers from grep, because in this"
echo "   locale '.' means one byte and 'é' is two of them. Nothing warned you."

echo
echo "2. THE PORTABLE WAY TO FIND NON-ASCII LINES"
echo '$ grep -n "[^ -~]" mixed.txt'
grep -n '[^ -~]' mixed.txt
echo "   The class is 'any byte outside space through tilde' — the printable"
echo "   half of ASCII. It needs no -P, so it works on BSD grep too, where -P"
echo "   does not exist at all. It also flags tabs, which are outside that range"
echo "   and are usually worth seeing anyway."

echo
echo "3. -c COUNTS LINES, NOT MATCHES"
echo '$ grep -c a mixed.txt'
grep -c a mixed.txt
echo '$ grep -o a mixed.txt | wc -l'
grep -o a mixed.txt | wc -l | tr -d ' '
echo "   Three lines contain an 'a'; there are four of them. -c answers the"
echo "   first question. If you wanted the second, -o and wc are the pair."

echo
echo "4. ONE NUL BYTE, AND THE FILE STOPS BEING TEXT"
echo '$ xxd withnul.txt'
xxd withnul.txt
echo '$ grep -c hello withnul.txt'
grep -c hello withnul.txt
echo '$ grep -a hello withnul.txt | cat -v'
grep -a hello withnul.txt | cat -v
echo "   grep found both lines — -c proves it — and without -a it will not show"
echo "   you either one. What it prints instead is a notice, and the wording and"
echo "   even the STREAM of that notice differ between the two greps; the page"
echo "   has both. -a (--binary-files=text) is the flag that says 'show me anyway'."
echo "   One NUL is enough. High bytes alone are not: a UTF-8 file of accented"
echo "   letters is still text to grep."

echo
echo "5. UTF-16: THE WORD IS RIGHT THERE AND GREP CANNOT SEE IT"
echo '$ xxd u16.txt'
xxd u16.txt
echo '$ grep -a caf u16.txt   # -a, so this is not the binary rule'
grep -a caf u16.txt && echo "   (found)" || echo "   (no match — exit $?)"
echo "   'caf' is in that dump: 63 00 61 00 66 00. It is not in the FILE as the"
echo "   three bytes 63 61 66, and grep searches bytes, so there is no match and"
echo "   no error. A clean exit 1 that means 'not present' when the truth is"
echo "   'present, spelled differently'."

echo
echo "6. THE FIX IS TO DECODE FIRST, NOT TO SEARCH HARDER"
echo '$ iconv -f UTF-16LE -t UTF-8 u16.txt | grep -a caf'
iconv -f UTF-16LE -t UTF-8 u16.txt | grep -a caf
echo '$ iconv -f UTF-16LE -t UTF-8 u16.txt | grep -a caf | xxd -p'
iconv -f UTF-16LE -t UTF-8 u16.txt | grep -a caf | xxd -p
echo "   It matches. Name the encoding, convert, then search — grep is a byte"
echo "   tool, so hand it bytes it can answer about."
echo "   The hex shows what the text line hides: the first three bytes are"
echo "   ef bb bf, the byte-order mark, converted along with everything else and"
echo "   now sitting invisibly at the front of your search result. Naming"
echo "   UTF-16LE told iconv the order, so it treated the mark as content."
