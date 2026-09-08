#!/usr/bin/env bash
# Answer key: what `.` means, and who decided.
#
# This key runs everything in ONE locale, C, and states it. Two reasons, and
# the second is the interesting one. A UTF-8 locale is not portably named --
# C.UTF-8 on Ubuntu, en_US.UTF-8 on a Mac -- so a recorded key that used one
# would be a fact about the runner. And BSD grep's binary-file heuristic fires
# on an undecodable byte in BOTH locales, so the silent-skip demonstration the
# page documents cannot be reproduced from the locale alone. The page has that
# in a dated fence; this key sticks to what is the same everywhere.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251\n' > f      # café, 5 bytes + newline

echo "THE FILE"
printf '   %s   %s   (%s bytes, 4 characters)\n' "$(cat f)" "$(xxd -p < f)" \
  "$(wc -c < f | tr -d ' ')"
echo
echo "1. HOW MANY CHARACTERS DOES caf. MATCH?"
printf '   grep -c "^caf.$"      %s\n' "$(LC_ALL=C grep -c '^caf.$' f || true)"
printf '   grep -c "^caf..$"     %s\n' "$(LC_ALL=C grep -c '^caf..$' f || true)"
echo "   In the C locale a character IS a byte, so the four-character word"
echo "   needs FIVE dots' worth of pattern -- and caf. does not reach the end"
echo "   of the line. In a UTF-8 locale the first pattern matches and the"
echo "   second does not. Same file, same grep, opposite answers, and the"
echo "   only thing that changed was an environment variable."
echo
echo "2. WHICH IS RIGHT?"
echo "   Both. The question 'does caf. match café' has no answer until"
echo "   somebody says what a character is, and grep asks the locale rather"
echo "   than the file. The file has no opinion: it is five bytes either way."
echo
echo "3. THE OTHER TOOLS ANSWER THE SAME QUESTION DIFFERENTLY"
echo "   grep   asks LC_CTYPE"
echo "   rg     never asks the locale; it reads the file's first bytes for a"
echo "          BOM and otherwise works in bytes"
echo "   find   asks nobody and compares bytes"
echo "   python asks nothing since 3.7 -- str is code points, always"
echo "   So four tools in one pipeline can hold four different definitions of"
echo "   'a character' at the same moment, and none of them is misconfigured."
echo
echo "4. THE ESCAPE, AND ITS PRICE"
printf '   LC_ALL=C grep -c caf   %s   -- a literal string is unaffected\n' \
  "$(LC_ALL=C grep -c caf f)"
echo "   For a FIXED string the locale changes nothing, which is why LC_ALL=C"
echo "   is a safe default for searching: no interpretation, no undecodable"
echo "   input, the same answer on every machine. It only bites when the"
echo "   pattern contains ., [[:alpha:]], a range, or a case-insensitive flag"
echo "   -- everything that needs to know how wide a character is."
echo
echo "5. AND THE FAILURE SHAPE WORTH REMEMBERING"
echo "   Of the tools in this chapter, grep is the one that can find FEWER"
echo "   lines than are there and still exit 0 -- a short answer with a"
echo "   success status. sed reports an illegal byte sequence, awk names the"
echo "   record, cut refuses. Only grep can say nothing at all."
