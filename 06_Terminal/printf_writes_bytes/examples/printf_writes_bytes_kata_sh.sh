#!/usr/bin/env bash
# Kata solution: four writes that look the same, and the one change that makes
# a fifth machine-dependent.
#
# The four recorded rows are byte-identical on macOS (bash 3.2.57) and Ubuntu
# (bash 5.2.21). The fifth is deliberately NOT recorded as bytes — only its
# length — because that is the whole point of the second half.
#
# Run:  bash printf_writes_bytes_kata_sh.sh
set -u
hx() { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }
n()  { wc -c | tr -d ' '; }

row() { printf '   %-26s %-28s %s bytes\n' "$1" "$2" "$3"; }

echo "THE FOUR WRITES"
row "printf '\\x41\\x42'"      "$(printf '\x41\x42'      | hx)" "$(printf '\x41\x42'      | n)"
row "printf '%s' '\\x41\\x42'" "$(printf '%s' '\x41\x42' | hx)" "$(printf '%s' '\x41\x42' | n)"
row "printf '%b' '\\x41\\x42'" "$(printf '%b' '\x41\x42' | hx)" "$(printf '%b' '\x41\x42' | n)"
row "echo    '\\x41\\x42'"     "$(echo '\x41\x42'        | hx)" "$(echo '\x41\x42'        | n)"
echo
echo "WHY THEY DIFFER"
echo "   Rows 1 and 3 wrote AB. The escapes were read, because the FORMAT is"
echo "   always scanned and %b asks for an ARGUMENT to be scanned too."
echo "   Row 2 wrote eight bytes: 5c is a backslash, and 78 34 31 is the ASCII"
echo "   for x41. Under %s an argument is data, and a backslash is a character"
echo "   like any other. Nothing was interpreted, which is usually what you"
echo "   want when the string came from outside your script."
echo "   Row 4 wrote the same eight bytes plus 0a. bash's echo does not read"
echo "   escapes without -e — but /bin/sh's echo on many systems does, and"
echo "   there is your portability bug: one script, two byte counts, no error."
echo
echo "THE ONE-CHARACTER CHANGE"
echo "   Replace the x in row 1 with a u, and 41 becomes a CODE POINT rather"
echo "   than a byte:  printf '\u0041'"
printf '   %-42s %s\n' "printf '\\x41'   here, and everywhere" "$(printf '\x41' | n) byte"
echo "   printf '\u0041' here                       NOT RECORDED — see below"
echo "   \x41 is one byte on every machine ever built, which is why its length"
echo "   is printed above and \u0041's is not. \u0041 writes ONE byte on a bash"
echo "   that implements \u — 4.2 and later, in any locale, since A exists in"
echo "   all of them — and SIX on macOS's bash 3.2, which predates the escape"
echo "   and hands it back as text. Two answers, so no answer key."
echo
echo "   Outside ASCII the fork has three tines rather than two:"
echo "     printf '\u20ac'  bash 5.2 + a UTF-8 locale   e2 82 ac   a euro sign"
echo "                     bash 5.2 + LC_ALL=C          \u20AC     hex uppercased"
echo "                     bash 3.2 (macOS), any        \u20ac     untouched"
echo "   Same command, three answers, one euro sign. Name bytes rather than"
echo "   code points and the question never arises."
