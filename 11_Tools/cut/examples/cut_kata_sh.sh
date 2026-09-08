#!/usr/bin/env bash
# Answer key: -b, -c, and the promise only one cut keeps.
# Runs in C so the key is portable; the UTF-8-locale split is stated as a dated
# measurement, because that is the half that is a fact about the machine.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251 na\303\257ve\n' > f

echo "THE FILE: 12 bytes of text, 10 characters"
printf '   %s\n   %s\n' "$(cat f)" "$(xxd -p < f)"
echo
echo "IN THE C LOCALE, WHERE A CHARACTER IS A BYTE"
printf '   cut -b1-4  %s   %s\n' "$(cut -b1-4 < f | xxd -p)" "$(cut -b1-4 < f | tr -d '\n')"
printf '   cut -c1-4  %s   %s\n' "$(cut -c1-4 < f | xxd -p)" "$(cut -c1-4 < f | tr -d '\n')"
echo "   Identical, and both end in c3 -- the first half of é. The output is"
echo "   four bytes and is not valid UTF-8. In the C locale there is no"
echo "   difference between the two flags because there is no difference"
echo "   between a byte and a character."
echo
echo "IN A UTF-8 LOCALE THE TWO cuts SEPARATE. Measured 2026-09-07:"
echo "   BSD cut (macOS)     cut -c1-4 -> 63 61 66 c3 a9   FIVE bytes, four"
echo "                       characters: it keeps the promise -c makes."
echo "   GNU cut (Ubuntu)    cut -c1-4 -> 63 61 66 c3      FOUR bytes, the"
echo "                       same as -b: GNU treats -c as a synonym for -b."
echo "   So the same command on the same file gives four bytes on one machine"
echo "   and five on the other, and neither prints a warning."
echo
echo "WHY THE FLAG EXISTS AT ALL"
echo "   POSIX defines -b as bytes and -c as characters precisely because they"
echo "   are different questions. GNU's manual is honest about not"
echo "   distinguishing them; the trap is that the FLAG still reads as a"
echo "   promise, so a script written on a Mac and deployed on Linux changes"
echo "   behaviour without changing a character of source."
echo
echo "WHAT TO USE INSTEAD"
printf '   cut -d" " -f1   %s   -- fields, not offsets\n' "$(cut -d' ' -f1 < f)"
echo "   A field boundary is in the data; a byte offset is a guess about the"
echo "   data's width. Where the data really is fixed-width, it is fixed-width"
echo "   in BYTES, and -b is then the correct and honest flag."
