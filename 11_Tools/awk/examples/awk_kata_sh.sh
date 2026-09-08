#!/usr/bin/env bash
# Answer key: whose awk is this, and what does length() count?
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251\n' > f          # 4 characters, 5 bytes

echo "THE FILE: 4 characters, 5 bytes"
printf '   %s   %s\n' "$(cat f)" "$(xxd -p < f)"
echo
echo "IN THE C LOCALE"
printf '   awk length($0)          %s\n' "$(awk '{print length($0)}' f)"
printf '   awk gsub(/./,"X")       %s\n' "$(awk '{n=gsub(/./,"X"); print n}' f)"
echo "   Five and five. A character is a byte here, so both halves of awk agree"
echo "   -- and the answer they agree on is the BYTE count, not the four"
echo "   characters a person would count."
echo
echo "THERE ARE THREE awks, AND YOU HAVE ONE OF THEM"
echo "   BWK awk (the one true awk)  the default on macOS and the BSDs"
echo "   mawk                        the default /usr/bin/awk on Debian/Ubuntu"
echo "   gawk                        GNU awk, the default on Fedora, and"
echo "                               installable everywhere"
echo "   They are different programs by different authors with different"
echo "   Unicode support, and none of them is 'awk' in a portable sense. Ask:"
echo "       awk --version    (or awk -W version for older mawk)"
echo
echo "WHAT SEPARATES THEM IS THE UTF-8 LOCALE, NOT THE C ONE"
echo "   Measured 2026-09-07: in the C locale all three count bytes in both"
echo "   length() and the regex engine, so all three agree with each other and"
echo "   with themselves. Put a UTF-8 locale in front of them and the"
echo "   guarantees come apart -- some versions of BWK awk count BYTES in"
echo "   length() while the regex engine matches CHARACTERS, so length($0) and"
echo "   gsub(/./,\"X\") disagree about one string in one run of one program."
echo
echo "THE PRACTICAL RULE"
echo "   If an awk script measures or slices text, pin the locale and say which"
echo "   awk it needs -- or move the job to a tool with one implementation."
echo "   substr() and length() are the two functions to distrust; field"
echo "   splitting on a delimiter is safe, because a delimiter is a byte"
echo "   sequence and every awk finds it the same way."
printf '   awk -F" " "{print \$1}"  -> %s\n' "$(awk -F' ' '{print $1}' f)"
