#!/usr/bin/env bash
# A log file is a text format with exactly one delimiter, and anybody who can
# put that delimiter in a field can write a line the program never wrote.
#
# Portable: printf, cat -vet, xxd, wc, grep. Nothing here ever cats an escape
# sequence to the screen -- which is the point of section 3.

log="$(mktemp)"

# The application's one and only log statement.
applog() { printf 'login failed user=%s\n' "$1" >> "$log"; }

echo "1. ONE LOG CALL, TWO LOG LINES"
applog 'alice'
applog 'bob
login ok user=root'
printf '   log calls made      2\n'
printf '   lines in the file   %s\n' "$(wc -l < "$log" | tr -d ' ')"
printf "   grep -c 'login ok'  %s   <- a line no log statement produced\n" "$(grep -c 'login ok' "$log")"
echo "   The second username contained a newline. The log format's only"
echo "   structure IS the newline, so the field became a record."
echo

echo "2. WHAT IS ACTUALLY IN THE FILE"
cat -vet "$log" | sed 's/^/     /'
echo "   cat -vet marks the ends of lines with \$ and shows control bytes as ^X."
echo "   The forged record is a real line by every measure a reader has."
echo

echo "3. THE PART YOU CANNOT SEE AT ALL"
: > "$log"
applog "$(printf 'mallory\033[2K\rlogin ok user=root')"
echo "   the file, as bytes:"
xxd "$log" | sed 's/^/     /'
echo "   the file, with control bytes shown:"
cat -vet "$log" | sed 's/^/     /'
echo "   ^[ is ESC. On a terminal, ESC [ 2K erases the line and CR returns to"
echo "   its start, so anyone who runs 'cat' or 'tail -f' on this file is shown"
echo "   'login ok user=root' and never sees the word mallory at all."
echo "   The bytes are in the file. The screen is a renderer, and it was"
echo "   following instructions the file gave it."
echo

echo "4. HOW TO READ SOMETHING YOU DID NOT WRITE"
echo "   cat -vet file      control bytes as ^X, line ends as \$"
echo "   xxd file           no interpretation at all"
echo "   less -R OFF        (plain 'less' already escapes control bytes)"
echo "   and on the writing side: escape or reject CR, LF and ESC in any field"
echo "   that goes into a line-delimited format. A log line is a record, and a"
echo "   record separator inside a value is the same bug as a quote inside SQL."

rm -f "$log"
